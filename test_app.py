import json
import math
from unittest.mock import MagicMock, patch
import pytest
from pymongo.errors import PyMongoError

from models import (
    GeneratedRecipe,
    Instruction,
    RecipeRequest,
)
from managers.ai.ai_client import AIClient
from managers.ai.gemini_ai_manager import GeminiAIManager
from managers.ai.recipe_validator import RecipeValidator
from managers.logic.logic_manager import LogicManager
from managers.logic.logic_settings import LogicSettings
from managers.logic.outcome import Outcome
from managers.logic.routing_decision import RoutingDecision
from managers.data.csv_ingredient import CsvIngredientRepository
from managers.data.csv_recipe import CsvRecipeRepository
from managers.data.mongo_ingredient import MongoIngredientRepository
from managers.data.mongo_recipe import MongoRecipeRepository
from managers.io.cli_display import CLIDisplay
from managers.io.main_menu import MainMenu
from managers.io.menu_validator import MenuValidator
from managers.io.recipe_request_validator import RecipeRequestValidator
from services.recipe_service import RecipeService

# =====================================================================
# Offline Test Doubles & Sample AI Payloads
# =====================================================================


class SampleAIClient(AIClient):
    """Offline stub implementing AIClient with deterministic sample responses."""

    def __init__(self, responses: list[str | Exception]) -> None:
        self._responses = list(responses)
        self.prompts: list[str] = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        if not self._responses:
            raise RuntimeError("No sample AI responses left in queue.")
        next_item = self._responses.pop(0)
        if isinstance(next_item, Exception):
            raise next_item
        return next_item


SAMPLE_VALID_RECIPE_DICT = {
    "recipe": "Garlic Butter Chicken",
    "ingredients": {"chicken": "200g", "garlic": "10g", "butter": "20g"},
    "instructions": {
        "1": {"step": "Season and sear the chicken.", "time_taken": "10 mins"},
        "2": {
            "step": "Add garlic and butter, baste until cooked.",
            "time_taken": "5 mins",
        },
    },
    "confidence": 0.92,
    "dietary_preferences": ["halal"],
    "hazardous_ingredients": {},
    "equipment": ["pan"],
    "insufficient_ingredients": False,
}

INGREDIENT_FIELDS = ["session_id", "timestamp", "ingredient", "quantity"]
RECIPE_FIELDS = [
    "session_id",
    "timestamp",
    "recipe",
    "ingredients",
    "instructions",
    "confidence",
    "score",
    "outcome",
    "reason",
]


@pytest.fixture
def sample_request() -> RecipeRequest:
    return RecipeRequest(
        ingredients={"chicken": "200g", "garlic": "10g"},
        available_ingredients={"chicken": "500g", "garlic": "50g", "butter": "100g"},
        allergies=["peanuts"],
        dietary_preferences=["halal"],
        pax=2,
    )


class FakeMongoCollection:
    """In-memory MongoDB collection stub supporting standard PyMongo CRUD calls."""

    def __init__(self) -> None:
        self.docs: list[dict] = []
        self.raise_on_read: Exception | None = None

    def _matches(self, doc: dict, query: dict | None) -> bool:
        if not query:
            return True
        return all(doc.get(k) == v for k, v in query.items())

    def find(self, query: dict | None = None) -> list[dict]:
        if self.raise_on_read:
            raise self.raise_on_read
        return [dict(d) for d in self.docs if self._matches(d, query)]

    def find_one(self, query: dict | None = None) -> dict | None:
        if self.raise_on_read:
            raise self.raise_on_read
        for d in self.docs:
            if self._matches(d, query):
                return dict(d)
        return None

    def insert_one(self, doc: dict) -> MagicMock:
        self.docs.append(dict(doc))
        return MagicMock(inserted_id="mock_id")

    def insert_many(self, docs: list[dict]) -> MagicMock:
        self.docs.extend(dict(d) for d in docs)
        return MagicMock(inserted_ids=["mock_id"] * len(docs))

    def update_one(self, query: dict, update: dict, upsert: bool = False) -> MagicMock:
        fields = update.get("$set", update)
        for d in self.docs:
            if self._matches(d, query):
                d.update(fields)
                return MagicMock(modified_count=1)
        if upsert:
            new_doc = {**query, **fields}
            self.docs.append(new_doc)
        return MagicMock(modified_count=0)

    def replace_one(
        self, query: dict, replacement: dict, upsert: bool = False
    ) -> MagicMock:
        for i, d in enumerate(self.docs):
            if self._matches(d, query):
                self.docs[i] = dict(replacement)
                return MagicMock(modified_count=1)
        if upsert:
            self.docs.append(dict(replacement))
        return MagicMock(modified_count=0)

    def delete_one(self, query: dict) -> MagicMock:
        for i, d in enumerate(self.docs):
            if self._matches(d, query):
                self.docs.pop(i)
                return MagicMock(deleted_count=1)
        return MagicMock(deleted_count=0)

    def delete_many(self, query: dict | None = None) -> MagicMock:
        before = len(self.docs)
        self.docs = [d for d in self.docs if not self._matches(d, query)]
        return MagicMock(deleted_count=before - len(self.docs))


# =====================================================================
# 1. AI Manager & Schema Validation Tests (Offline Sample Responses)
# =====================================================================


class TestAIManagerAndValidator:
    def test_validator_accepts_valid_schema(self) -> None:
        validator = RecipeValidator()
        raw_res = validator.validate_raw(SAMPLE_VALID_RECIPE_DICT)
        assert raw_res.is_valid

        recipe = GeneratedRecipe.from_dict(SAMPLE_VALID_RECIPE_DICT)
        field_res = validator.validate_fields(recipe)
        assert field_res.is_valid
        assert field_res.errors == []

    @pytest.mark.parametrize(
        "bad_payload",
        [
            "not-a-dict",
            {"recipe": "Soup"},
            {"recipe": "Soup", "instructions": "invalid-string-type"},
            {"recipe": "Soup", "instructions": {}},
        ],
    )
    def test_validator_rejects_malformed_raw_structures(
        self, bad_payload: object
    ) -> None:
        validator = RecipeValidator()
        result = validator.validate_raw(bad_payload)
        assert not result.is_valid
        assert len(result.errors) > 0

    @pytest.mark.parametrize("bad_confidence", [-0.1, 1.5, float("nan"), True, None])
    def test_validator_rejects_invalid_confidence(self, bad_confidence: object) -> None:
        validator = RecipeValidator()
        recipe = GeneratedRecipe(
            recipe="Test Dish",
            ingredients={"chicken": "200g"},
            instructions={"1": Instruction(step="Cook", time_taken="5 mins")},
            confidence=bad_confidence,  # type: ignore[arg-type]
            equipment=["pan"],
            dietary_preferences=[],
            hazardous_ingredients={},
            insufficient_ingredients=False,
        )
        result = validator.validate_fields(recipe)
        assert not result.is_valid

    def test_gemini_ai_manager_parses_sample_json_offline(
        self, sample_request: RecipeRequest
    ) -> None:
        client = SampleAIClient([json.dumps(SAMPLE_VALID_RECIPE_DICT)])
        manager = GeminiAIManager(client=client, validator=RecipeValidator())

        ai_result = manager.process(sample_request)

        assert ai_result.success is True
        assert ai_result.recipe is not None
        assert ai_result.recipe.recipe == "Garlic Butter Chicken"
        assert "chicken" in client.prompts[0].lower()

    def test_gemini_ai_manager_handles_malformed_json_gracefully(
        self, sample_request: RecipeRequest
    ) -> None:
        client = SampleAIClient(["{broken_json:::", "still not json"])
        manager = GeminiAIManager(client=client, validator=RecipeValidator())

        ai_result = manager.process(sample_request)

        assert ai_result.success is False
        assert ai_result.recipe is None
        assert ai_result.error_message

    def test_gemini_ai_manager_handles_api_exception_gracefully(
        self, sample_request: RecipeRequest
    ) -> None:
        client = SampleAIClient([ConnectionError("Simulated API timeout")])
        manager = GeminiAIManager(client=client, validator=RecipeValidator())

        ai_result = manager.process(sample_request)

        assert ai_result.success is False
        assert ai_result.recipe is None
        assert ai_result.error_message


# =====================================================================
# 2. Logic Manager & New Feature (LogicSettings) Tests
# =====================================================================


class TestLogicManagerAndSettings:
    def test_logic_settings_defaults_and_custom_weights(self) -> None:
        settings = LogicSettings()
        assert math.isclose(sum(settings.weights), 1.0)

        settings.set_weights(0.6, 0.3, 0.1)
        assert settings.weights == (0.6, 0.3, 0.1)

    @pytest.mark.parametrize(
        "weights",
        [
            (0.5, 0.5, 0.5),
            (-0.1, 0.6, 0.5),
            (float("nan"), 0.5, 0.5),
        ],
    )
    def test_logic_settings_rejects_invalid_weights(
        self, weights: tuple[float, float, float]
    ) -> None:
        settings = LogicSettings()
        with pytest.raises(ValueError):
            settings.set_weights(*weights)

    def test_logic_manager_routes_valid_and_allergy_recipes(
        self, sample_request: RecipeRequest
    ) -> None:
        logic = LogicManager()
        valid_recipe = GeneratedRecipe.from_dict(SAMPLE_VALID_RECIPE_DICT)

        decision = logic.process(sample_request, valid_recipe)
        assert isinstance(decision, RoutingDecision)
        assert decision.outcome == Outcome.ACCEPT

        allergy_data = dict(SAMPLE_VALID_RECIPE_DICT)
        allergy_data["ingredients"] = {"chicken": "200g", "peanuts": "30g"}
        allergy_recipe = GeneratedRecipe.from_dict(allergy_data)

        rejected = logic.process(sample_request, allergy_recipe)
        assert rejected.outcome == Outcome.REJECT


# =====================================================================
# 3. Data Manager Tests (CSV & MongoDB Repositories)
# =====================================================================


class TestDataRepositories:
    def test_csv_ingredient_repository_crud_and_missing_file(self, tmp_path) -> None:
        csv_file = tmp_path / "ingredients.csv"
        repo = CsvIngredientRepository(str(csv_file), INGREDIENT_FIELDS)

        assert repo.find_all() == {}
        assert repo.save({"chicken": "500g", "rice": "1kg"}) is True
        assert repo.find_all() == {"chicken": "500g", "rice": "1kg"}

        assert repo.delete("chicken") is True
        assert repo.find_all() == {"rice": "1kg"}
        assert repo.delete("nonexistent") is False

    def test_csv_recipe_repository_handles_corrupt_file(self, tmp_path) -> None:
        csv_file = tmp_path / "recipes.csv"
        csv_file.write_text(
            "corrupt,header\nmalformed_row_without_columns\n", encoding="utf-8"
        )
        repo = CsvRecipeRepository(str(csv_file), RECIPE_FIELDS)

        records = repo.find_all()
        assert isinstance(records, list)

    def test_mongo_ingredient_repository_crud_and_error_handling(self) -> None:
        fake_col = FakeMongoCollection()

        with (
            patch("pymongo.MongoClient") as mock_pymongo_client,
            patch("managers.data.mongo_repository.MongoClient") as mock_repo_client,
        ):
            for client_mock in (mock_pymongo_client, mock_repo_client):
                mock_db = MagicMock()
                mock_db.__getitem__.return_value = fake_col
                mock_db.get_collection.return_value = fake_col
                client_mock.return_value.__getitem__.return_value = mock_db
                client_mock.return_value.get_database.return_value = mock_db

            repo = MongoIngredientRepository("mongodb://localhost:27017", "test_db")
            repo._collection = fake_col
            setattr(repo, "_MongoRepository__collection", fake_col)

            assert repo.save({"chicken": "500g", "garlic": "50g"}) is True
            assert repo.find_all() == {"chicken": "500g", "garlic": "50g"}

            assert repo.delete("chicken") is True
            assert repo.find_all() == {"garlic": "50g"}
            assert repo.delete("nonexistent") is False

            # Simulate DB connection failure -> graceful empty fallback
            fake_col.raise_on_read = PyMongoError("Connection refused")
            assert repo.find_all() == {}

    def test_mongo_recipe_repository_save_and_query(self) -> None:
        mock_collection = MagicMock()
        mock_collection.find.return_value = [
            {
                "recipe": "Garlic Butter Chicken",
                "ingredients": {"chicken": "200g"},
                "instructions": {"1": {"step": "Cook", "time_taken": "10 mins"}},
                "confidence": 0.9,
                "score": 0.88,
                "outcome": "accept",
                "reason": "",
            }
        ]

        with patch("managers.data.mongo_repository.MongoClient"):
            repo = MongoRecipeRepository("mongodb://localhost:27017", "test_db")
            repo._collection = mock_collection

            all_recipes = repo.find_all()
            assert len(all_recipes) == 1

            mock_collection.insert_one.side_effect = PyMongoError("Write failed")
            assert repo.save({"recipe": "Test"}) is False


# =====================================================================
# 4. End-to-End RecipeService Pipeline (Offline)
# =====================================================================


class TestRecipeServicePipeline:
    def test_recipe_service_end_to_end_offline(
        self, tmp_path, sample_request: RecipeRequest
    ) -> None:
        ai_client = SampleAIClient([json.dumps(SAMPLE_VALID_RECIPE_DICT)])
        ai_manager = GeminiAIManager(client=ai_client, validator=RecipeValidator())
        logic_manager = LogicManager()
        recipe_repo = CsvRecipeRepository(str(tmp_path / "recipes.csv"), RECIPE_FIELDS)

        service = RecipeService(ai_manager, logic_manager, recipe_repo)

        outcome = service.generate_recipe(sample_request)
        assert outcome is not None
        assert len(recipe_repo.find_all()) == 1


# =====================================================================
# 5. IO Manager Validators & Menu Input Tests
# =====================================================================


class TestIOManager:
    def test_menu_validator_and_main_menu(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        validator = MenuValidator()
        assert validator.validate("1", 6) is True
        assert not validator.validate("0", 6)
        assert not validator.validate("7", 6)
        assert not validator.validate("abc", 6)

        inputs = iter(["invalid", "9", "2"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        menu = MainMenu(validator=validator, displayer=CLIDisplay())
        assert menu.execute() == "2"

    def test_recipe_request_validator_checks_stock_and_format(self) -> None:
        validator = RecipeRequestValidator(CLIDisplay())
        stock = {"chicken": "500g", "milk": "1000ml"}

        assert validator.validate_ingredients("chicken 200g", stock) is not None
        assert validator.validate_ingredients("chicken 900g", stock) is None
        assert validator.validate_ingredients("beef 200g", stock) is None
        assert validator.validate_ingredients("beef 300g", None) is not None
        assert validator.validate_ingredients("chicken", None) is None
