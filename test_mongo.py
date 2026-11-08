import data_manager

repo = data_manager.MongoIngredientRepository(logger=print)
print(repo.save_all({"beef": "100g"}))
print(repo.save_all({"beef": "100g", "pork": "50g"}))
print(repo.find_all())     # expect {'beef': '200g', 'pork': '50g'}