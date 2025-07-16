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
    """
    Calcola per ogni utente presente nel db il profilo di gusto per ciascuna tipologia di pasto,
    sulla base dei pasti consumati nell'ultimo mese.
    """
    #get all the users
    users = userPersistence.get_all_users()
    for user in users:
        #convert the user from dictionary to object
        userJson = jsonpickle.encode(user)
        userData = userDto.User(None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None)
        userData.from_json(userJson)
        compute_user_taste(userData)

def compute_user_taste(user):
    """
    Calcola il profilo di gusto dell'utente dato input per ciascuna tipologia di pasto,
    come la somma degli embeddings degli ingredienti delle ricette che l'utente ha consumato nell'ultimo mese, 
    e lo aggiorna nel db.

    Args : 
    - user : utente di cui calcolare il profilo di gusto.
    """
 
    #get the user history of the month
    userHistory = foodHistory.get_user_history_of_month(user.id)
    breackfastTaste = compute_taste(userHistory, 'Breakfast')
    lunchTaste = compute_taste(userHistory, 'Lunch')
    dinnerTaste = compute_taste(userHistory, 'Dinner')
    breakTaste = compute_taste(userHistory, 'Break')
    tastes = {'breakfast': pd.Series(breackfastTaste).to_list(), 'lunch': pd.Series(lunchTaste).to_list(), 'dinner': pd.Series(dinnerTaste).to_list(), 'break': pd.Series(breakTaste).to_list()}
    userPersistence.update_user_tastes(user.id, tastes)
    
def compute_taste(userHistory, mealType):
    """
    Calcola il profilo di gusto data la cronologia alimentare userHistory della specifica tipologia di pasto data mealType.
    
    Args : 
    - userHistory : cronologia delle ricette consumante dell'utente.
    - mealType : tipologia di pasto.
    
    Returns :
    - tasteEmbedding : embedding del profilo di gusto della data cronologia alimentare rispetto alla data tipologia di pasto.
    """

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

def get_recipe_emebedding(recipe):
    """
    Calcola l'embedding di una ricetta, fornita come lista di ingredienti, come la somma degli embedding
    degli ingredienti che la compongono. Gli ingredienti nella ricetta vengono usati per recuperare dal db
    l'ingrediente corrispondente, in modo da ottenere il suo embedding. Se un ingrendiente non è presente nel db
    viene recuperato l'ingrediente con valore più alto di similarità del coseno all'ingrediente dato.

    Args : 
    - recipe : ricetta, sotto forma di lista di ingredienti, di cui restituire l'embedding

    Returns : 
    - recipeNameEmbedding : embeddings della ricetta fornita.
    """
    recipeNameEmbedding = np.zeros(1024)
    for ingredient in recipe:
        ingFromDb = ingredientPersistence.get_ingredient_by_name(ingredient['name'])
        if ingFromDb is None:
            ingFromDb = ingredientPersistence.get_most_similar_ingredient(ingredient['name'])
        embedding = ingFromDb['ingredient_embedding']
        recipeNameEmbedding += embedding
    return recipeNameEmbedding

def return_empty_tastes():
    """
    Restituisce un dizionario contenente embedding vuoti per l'embedding del gusto di ciascuna tipologia di pasto.

    Returns:
    - dict: dizionario con chiavi 'breakfast', 'lunch', 'dinner', 'break' e valori None.
    """
    breackfastTaste = compute_taste(None, 'Breakfast')
    lunchTaste = compute_taste(None, 'Lunch')
    dinnerTaste = compute_taste(None, 'Dinner')
    snackTaste = compute_taste(None, 'Break')
    return {'breakfast': pd.Series(breackfastTaste).to_list(), 'lunch': pd.Series(lunchTaste).to_list(), 'dinner': pd.Series(dinnerTaste).to_list(), 'break': pd.Series(snackTaste).to_list()}