import persistence.IngredientPersistence as ip
import dto.Ingredient as ingredientDto

def remove_additional_info(ingredient):
    #given a string like "water _ 2 __ cups"
    #find the  index of the character "_" and remove everything after it
    index = ingredient.find(' _')
    #if the character is not found then return the string as it is
    if index != -1:
        #get the substring from 0 to the index minus 1
        ingredient = ingredient[:index]
    #remove [,],{,} and '
    ingredient = ingredient.replace('[','')
    ingredient = ingredient.replace(']','')
    ingredient = ingredient.replace('{','')
    ingredient = ingredient.replace('}','')
    ingredient = ingredient.replace('"','')
    ingredient = ingredient.replace('\'','')
    #remove trailing and leading spaces
    return ingredient

#uset to extract the ingredients from a string like "['ingredient1 _ quantity __ unit','ingredient2 _ quantity __ unit']" used in recipe
def get_ingredient_list_from_full_ingredient_string(ingredients):
    ingredients = ingredients.split("',")
    ingredients = [ingredient.strip() for ingredient in ingredients]
    ingredients = [remove_additional_info(ingredient) for ingredient in ingredients]
    return get_ingredient_list(ingredients)


def get_ingredient_list_from_generic_list_of_string(ingredientsListOfString):
    ingredients = []
    for ingredient in ingredientsListOfString:
        foodFromDB= ip.get_ingredient_by_name(ingredient)
        if foodFromDB == None or foodFromDB == 'null':
            foodFromDB = ip.get_most_similar_ingredient(ingredient)
        ingredients.append(foodFromDB['ingredient'])
    return get_ingredient_list(ingredients)

def get_ingredient_list(ingredientsList):
    ingredientObjList = []
    for ingredient in ingredientsList:
        #query the database
        ingredientInDB = ip.get_ingredient_by_name(ingredient)

        #if the ingredienntDB has the cfp data then use it else use None
        if 'cfp' in ingredientInDB:
            cfp = ingredientInDB['cfp']
        else:
            cfp = None

        #if the ingredienntDB has the wfp data then use it else use None
        if 'wfp' in ingredientInDB:
            wfp = ingredientInDB['wfp']
        else:
            wfp = None

        ingredientObjList.append(ingredientDto.Ingredient(ingredient,cfp,wfp))
    
    return ingredientObjList