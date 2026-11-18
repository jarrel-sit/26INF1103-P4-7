# --- Imports --- #
from abc import abstractmethod
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from .repository import Repository


# --- Classes --- #
class MongoRepository(Repository):
    """Abstract base class for MongoDB repositories. Provides common functionality
    for saving and loading documents. Subclasses implement _process_document to
    turn a stored document into the record format the program uses."""

    def __init__(
        self, uri: str, db_name: str, collection_name: str, logger: function = None
    ):
        self.__logger = logger
        self._collection = MongoClient(uri, serverSelectionTimeoutMS=3000)[db_name][
            collection_name
        ]

    def _log(self, message: str) -> None:
        """Logs a message if a logger is provided."""
        if self.__logger:
            self.__logger(message)

    def save(self, data: dict) -> bool:
        """Inserts one document. Returns True if the save succeeded."""
        try:
            self._collection.insert_one(data)
        except PyMongoError as error:
            self._log(f"[Data Manager] Database error: {error}")
            return False

        return True

    def load(self) -> list:
        """Loads all documents, converted by _process_document."""
        try:
            documents = list(self._collection.find())
        except PyMongoError as error:
            self._log(f"[Data Manager] Database error: {error}")
            return []

        records = []
        for document in documents:
            try:
                record = self._process_document(document)
                if record is not None:
                    records.append(record)

            except (ValueError, KeyError) as error:
                self._log(
                    f"[Data Manager] Warning: skipping corrupt document ({error})."
                )

        self._log(f"[Data Manager] Loaded {len(records)} record(s) from database.")
        return records

    def query(self, filter_fn: function) -> list:
        """Returns all records for which filter_fn(record) is True."""
        return [record for record in self.load() if filter_fn(record)]

    @abstractmethod
    def _process_document(self, document: dict) -> object:
        """Converts one stored document into a record. Implemented by subclasses."""
        pass
