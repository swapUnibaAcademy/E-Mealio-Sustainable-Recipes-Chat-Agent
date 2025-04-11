import math
import service.domain.IngredientService as ingredientService
import dto.Recipe as recipe

def compute_recipe_sustainability_score(recipe):
    ingredients = recipe.ingredients
    alpha = 0.8
    beta = 0.2
    max_overall_sustainability = 0.8689
    cfp_score = compute_normalized_cfp_sustainability(ingredients)
    wfp_score = compute_normalized_wfp_sustainability(ingredients)

    overall_sustainability = alpha * cfp_score + beta * wfp_score
    normalized_overall_sustainability = overall_sustainability / max_overall_sustainability
    recipe.sustainabilityScore = normalized_overall_sustainability

def compute_normalized_cfp_sustainability(ingredients):
    normalized_cfps = []
    max_cfp = 78.8
    for ingredient in ingredients:
        if(ingredient.cfp != None):
            normalized_cfps.append(ingredient.cfp/max_cfp)
    #order cfps in descending order
    normalized_cfps.sort(reverse=True)

    cfp_score = 0
    for i in range(len(normalized_cfps)):
        cfp_score += normalized_cfps[i] * math.e ** (-i)
    
    return cfp_score

def compute_normalized_wfp_sustainability(ingredients):
    normalized_wfps = []
    max_wfp = 731000
    for ingredient in ingredients:
        if(ingredient.wfp != None):
            normalized_wfps.append(ingredient.wfp/max_wfp)
    #order wfps in descending order
    normalized_wfps.sort(reverse=True)

    wfp_score = 0
    for i in range(len(normalized_wfps)):
        wfp_score += normalized_wfps[i] * math.e ** (-i)
    
    return wfp_score

def get_recipe_cluster(recipe):
    #if the sustainability score is in [0, 0.04] then the recipe belongs to cluster 0
    if recipe.sustainabilityScore >= 0 and recipe.sustainabilityScore <= 0.04:
        return 0
    
    #if the sustainability score is in ]0.04, 0.15] then the recipe belongs to cluster 1
    if recipe.sustainabilityScore > 0.04 and recipe.sustainabilityScore <= 0.15:
        return 1
    
    #if the sustainability score is in ]0.15, 1] then the recipe belongs to cluster 2
    if recipe.sustainabilityScore > 0.15 and recipe.sustainabilityScore <= 1:
        return 2

def convert_in_emealio_recipe(mongoRecipe,removedConstraints,mealType):
    title = mongoRecipe['title']
    id = mongoRecipe['recipe_id']
    instructions = mongoRecipe['recipe_url']
    sustainabilityScore = mongoRecipe['sustainability_score']
    #check if the description is present
    if 'description' in mongoRecipe:
        description = mongoRecipe['description']
    else:
        description = None
    ingredients = ingredientService.get_ingredient_list_from_full_ingredient_string(mongoRecipe['ingredients'])
    return recipe.Recipe(title,id,ingredients,sustainabilityScore,instructions,description,removedConstraints,mealType)
