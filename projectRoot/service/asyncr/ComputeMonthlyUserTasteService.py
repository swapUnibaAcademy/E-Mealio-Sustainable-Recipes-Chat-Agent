import jsonpickle
import persistence.UserPersistence as userPersistence
import persistence.IngredientPersistence as ingredientPersistence
import service.domain.FoodHistoryService as foodHistory
import Utils
import random
import numpy as np
import pandas as pd
import dto.User as userDto

def compute_monthly_user_taste():
    #get all the users
    users = userPersistence.get_all_users()
    for user in users:
        #convert the user from dictionary to object
        userJson = jsonpickle.encode(user)
        userData = userDto.User(None,None,None,None,None,None,None,None,None,None,None)
        userData.from_json(userJson)
        compute_user_taste(userData)


## at the end of the month, for each user, compute the user's taste for each meal type
## the user's taste is the sum of the embeddings of the ingredients of the recipes the user has cooked in the month
def compute_user_taste(user):
    #get the user history of the month
    userHistory = foodHistory.get_user_history_of_month(user.id)
    breackfastTaste = compute_taste(userHistory, 'Breakfast')
    lunchTaste = compute_taste(userHistory, 'Lunch')
    dinnerTaste = compute_taste(userHistory, 'Dinner')
    breakTaste = compute_taste(userHistory, 'Break')
    tastes = {'breakfast': pd.Series(breackfastTaste).to_list(), 'lunch': pd.Series(lunchTaste).to_list(), 'dinner': pd.Series(dinnerTaste).to_list(), 'break': pd.Series(breakTaste).to_list()}
    userPersistence.update_user_tastes(user.id, tastes)
    

def compute_taste(userHistory, mealType):
    if userHistory is None or len(userHistory) == 0:
        return None

    meals = []
    tasteEmbedding = np.zeros(1024)
    for singleMeal in userHistory:
        if(singleMeal['recipe']['mealType'] == mealType):
            meals.append(singleMeal['recipe']['ingredients'])
    
    #if there are more than 10 elements in the list, shuffle the list and take the first 10
    if(len(meals) > 10):
        meals = random.sample(meals,10)

    if(len(meals) == 0):
        return None

    for meal in meals:
        recipeNameEmbedding = get_recipe_emebedding(meal)
        tasteEmbedding += recipeNameEmbedding
    
    return tasteEmbedding

#recipe give as a list of ingredients
def get_recipe_emebedding(recipe):
    recipeNameEmbedding = np.zeros(1024)
    for ingredient in recipe:

        ingFromDb = ingredientPersistence.get_ingredient_by_name(ingredient['name'])
        if ingFromDb is None:
            ingFromDb = ingredientPersistence.get_most_similar_ingredient(ingredient['name'])
        
        embedding = ingFromDb['ingredient_embedding']
        recipeNameEmbedding += embedding
    return recipeNameEmbedding

def return_empty_tastes():
    breackfastTaste = compute_taste(None, 'Breakfast')
    lunchTaste = compute_taste(None, 'Lunch')
    dinnerTaste = compute_taste(None, 'Dinner')
    snackTaste = compute_taste(None, 'Break')
    return {'breakfast': pd.Series(breackfastTaste).to_list(), 'lunch': pd.Series(lunchTaste).to_list(), 'dinner': pd.Series(dinnerTaste).to_list(), 'break': pd.Series(snackTaste).to_list()}