import service.ImproveRecipeService as irs
import jsonpickle

def extractRecipes(recipesData):
    recipesNames = recipesData['recipeNames']
    recipesIngredients = recipesData['recipeIngredients']    
    recipes = []

    for name in recipesNames:
        mealData = {'name': name, 'ingredients': []}
        baseRecipe = irs.get_base_recipe(jsonpickle.encode(mealData))
        recipes.append(baseRecipe)

    for ingredients in recipesIngredients:
        mealData = {'name': None,'ingredients': ingredients}
        baseRecipe = irs.get_base_recipe(jsonpickle.encode(mealData))
        recipes.append(baseRecipe)

    return recipes