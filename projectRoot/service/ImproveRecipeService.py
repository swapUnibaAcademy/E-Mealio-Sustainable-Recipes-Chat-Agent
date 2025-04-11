import jsonpickle
import service.domain.IngredientService as ingService
import service.domain.RecipeService as recipeService
import persistence.RecipePersistence as recipePersistence
import dto.Recipe as recipe
import service.SuggestRecipeService as food
import persistence.RecipePersistence as recipePersistence

def get_base_recipe(mealDataJson):
    mealData = jsonpickle.decode(mealDataJson)
    if(mealData['ingredients'] != [] and mealData['ingredients'] != None):
        ingredients = ingService.get_ingredient_list_from_generic_list_of_string(mealData['ingredients'])
    else:
        #this else is for the case when the user does not provide the ingredients but actually it should never happen
        #because the user must always provide the ingredients
        #I decided to keep it here just in case, but previous test showed that searching for a recipe without ingredients provide not reliable results for this context
        #so it is always better to provide the ingredients, like in the food diary task
        dBrecipe = recipePersistence.get_recipe_by_title(mealData['name'])
        if(dBrecipe == None or dBrecipe == 'null'):
            dBrecipe = recipePersistence.get_most_similar_recipe(mealData['name'])
        ingredients = ingService.get_ingredient_list_from_full_ingredient_string(dBrecipe['ingredients'])

    baseRecipe = recipe.Recipe(mealData["name"],None,ingredients,None,None,None,None,None)
    recipeService.compute_recipe_sustainability_score(baseRecipe)
    return baseRecipe

def get_recipe_improved(baseRecipe, userData):
    recipeCluster = recipeService.get_recipe_cluster(baseRecipe)
    ingredients = baseRecipe.ingredients
    ingredientsString = ', '.join([ingredient.name for ingredient in ingredients])

    info = """{ mealType: "", 
                recipeName: RECIPE_NAME,
                sustainabilityScore: SUSTAINABILITY_SCORE,
                ingredients_desired: INGREDIENTS_DESIRED,
                ingredients_not_desired: "",
                cookingTime: "",
                healthiness: ""} """
    
    if(recipeCluster <= 2):
        info = info.replace("SUSTAINABILITY_SCORE", str(baseRecipe.sustainabilityScore))
    else:
        info = info.replace("SUSTAINABILITY_SCORE", "")
    
    info = info.replace("INGREDIENTS_DESIRED", "["+ingredientsString+"]")
    info = info.replace("RECIPE_NAME", baseRecipe.name)
    
    suggestedRecipe = food.get_recipe_suggestion(info,userData)
    return suggestedRecipe