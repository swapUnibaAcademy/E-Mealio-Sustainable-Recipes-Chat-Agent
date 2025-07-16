import service.ImproveRecipeService as irs
import jsonpickle
import service.domain.RecipeService as rcs


def extractRecipes(recipesData):
    """
    A partire da un dizionario contenente una lista di nomi di ricette e una lista di liste di ingredienti,
    recupera dal db le corrispondenti ricette, e le restituisce come tuple contententi la ricetta recuperata dal db 
    e i corrispondenti valori nutrizionali.

    Args : 
    - recipesData : dizionario contenente una lista di nomi di ricette e una lista di liste di ingredienti.

    Returns : 
    - recipes : tuple di ricette, istanze della classe Recipe, con i corrispondenti valori nutrizionali.
    """

    recipesNames = recipesData['recipeNames']
    recipesIngredients = recipesData['recipeIngredients']    
    recipes = []

    for name in recipesNames:
        mealData = {'name': name, 'ingredients': []}
        baseRecipe = irs.get_base_recipe(jsonpickle.encode(mealData))

        # recuperiamo anche i valori nutrizionali grazie al titolo della ricetta
        nutritional_facts = rcs.get_nutritional_facts_by_title(name)
        recipes.append((baseRecipe,nutritional_facts))

    for ingredients in recipesIngredients:
        mealData = {'name': None,'ingredients': ingredients}
        baseRecipe = irs.get_base_recipe(jsonpickle.encode(mealData))
        recipes.append(baseRecipe)

    return recipes

