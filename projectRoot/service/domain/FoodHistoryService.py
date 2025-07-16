import persistence.UserHistoryPersistence as userHistoryDB
from datetime import datetime, timedelta
import jsonpickle
import dto.UserHistory as uh
import dto.Recipe as recipe
import dto.CustomRecipe as customRecipe
import service.domain.RecipeService as recipeService
import service.domain.IngredientService as ingService
import persistence.IngredientPersistence as ip
import Utils as utils
import service.bot.LangChainService as lcs

def get_custom_dates(DataJson):
    """
    Estrae da un json la data di inizio e fine.

    Args : 
    - DataJson : stringa JSON 

    Returns : 
    - begin_date, end_date : i campi data di inzio e fine codificati nella stringa JSON in input
    """

    Data = jsonpickle.decode(DataJson)

    begin_date = datetime.strptime(Data["begin_date"]+ " 00:00:00", '%d-%m-%Y %H:%M:%S')
    end_date = datetime.strptime(Data["end_date"]+ " 23:59:59", '%d-%m-%Y %H:%M:%S')
    
    return begin_date, end_date

def get_user_history_of_custom_date(userId, begin_date, end_date, onlyAccepted = True):
    """
    Recupera dalla collection users_food_history del db la cronologia dei suggerimenti alimenatri dell'utente 
    con dato userId del dato intervallo temporale, delimitato dal giormo di inizio e fine.

    Args : 
    - userId : id dell'utente di cui recuperare la cronologia.
    - onlyAccepted : flag booleana che indica se recuperare solo i suggerimenti accettati (di default True)
    - begin_date : giorno di inizio di cui tenere in considerazione la cronologia, nel formato %Y-%m-%d %H:%M:%S.
    - end_date : giorno di fine di cui tenere in considerazione la cronologia, nel formato %Y-%m-%d %H:%M:%S.

    Returns : 
    - userHistory : cronologia dell'ultima settimana dell'utente con dato userId recuperata dal db.
    """
    
    fullUserHistory = userHistoryDB.get_user_history(userId)

    userHistory = []
    for history in fullUserHistory:
        date = datetime.strptime(history['date'], '%Y-%m-%d %H:%M:%S')
        if date >= begin_date and date <= end_date and (not onlyAccepted or history['status'] == 'accepted'or history['status'] == 'asserted'):
            userHistory.append(history)

    if len(userHistory) == 0:
        return None
    
    return userHistory

def get_user_history_of_week(userId, onlyAccepted = True):
    """
    Recupera dalla collection users_food_history del db la cronologia dei suggerimenti alimenatri dell'utente 
    con dato userId dell'ultima settimana.

    Args : 
    - userId : id dell'utente di cui recuperare la cronologia.
    - onlyAccepted : flag booleana che indica se recuperare solo i suggerimenti accettati (di default True)

    Returns : 
    - userHistory : cronologia dell'ultima settimana dell'utente con dato userId recuperata dal db.
    """
    
    fullUserHistory = userHistoryDB.get_user_history(userId)

    #filter the user history of the week
    sysdate = datetime.today()
    previousWeek = sysdate - timedelta(days=7)
    userHistory = []
    for history in fullUserHistory:
        date = datetime.strptime(history['date'], '%Y-%m-%d %H:%M:%S')
        if date >= previousWeek and date <= sysdate and (not onlyAccepted or history['status'] == 'accepted'or history['status'] == 'asserted'):
            userHistory.append(history)

    if len(userHistory) == 0:
        return None
    
    return userHistory

def get_user_history_of_month(userId):
    """
    Recupera dalla collection users_food_history del db la cronologia dei suggerimenti alimenatri dell'utente 
    con dato userId dell'ultimo mese.

    Args : 
    - userId : id dell'utente di cui recuperare la cronologia.

    Returns : 
    - userHistory : cronologia dell'ultima settimana dell'utente con dato userId recuperata dal db.
    """
    
    fullUserHistory = userHistoryDB.get_user_history(userId)

    #filter the user history of the month
    sysdate = datetime.today()
    previousMonth = sysdate - timedelta(days=30)
    userHistory = []
    for history in fullUserHistory:
        date = datetime.strptime(history['date'], '%Y-%m-%d %H:%M:%S')
        if date >= previousMonth and date <= sysdate:
            userHistory.append(history)

    if len(userHistory) == 0:
        return None
    
    return userHistory

def clean_temporary_declined_suggestions(userId):
    """
    Rimuove i suggerimenti alimentari temporaneamente rifiutati (con stato "temporary_declined") dalla cronologia dei suggerimenti
    dell'utente con dato userId
    
    Args : 
    - userId : id dell'utente di cui eliminare i suggerimenti temporaneamente rifiutati. 
    """
    userHistoryDB.clean_temporary_declined_suggestions(userId)

def save_user_history(userHistoryJson):
    """
    Salva la data cronologia dei suggerimenti alimentari nel db.
    
    Args:
    - userHistoryJson : suggerimento da salvare nel db.
    """
    userHistoryDB.save_user_history(userHistoryJson)

def build_and_save_user_history(userData, jsonRecipe, status, ingredients_to_remove = None, ingredients_to_add = None):
    """
    Costruisce un oggetto di cronologia suggerimento alimentare istanza della classe UserHistory 
    a partire da una ricetta suggerita, i dati dell'utente, e lo stato di accettazione del suggerimento,
    e lo salva nel db. Se vengono fatte delle modifiche di ingredienti viene ricalcolato lo score di sostenibilità.

    Args:
    - userData : oggetto utente contenente le informazioni dell'utente 
    - jsonRecipe : stringa JSON che rappresenta la ricetta suggerita.
    - status : stato del suggerimento.
    - ingredients_to_remove : evenutali nomi degli ingredienti da rimuovere dalla ricetta prima di salvarla.
    - ingredients_to_add : evenutali nomi degli ingredienti da aggiungere alla ricetta prima di salvarla.
    """

    suggestedRecipe = recipe.Recipe(None,None,None,None,None,None,None,None,None)

    print("---------------------------------------------------------------------\nJSON RECIPE : \n",jsonRecipe)
    suggestedRecipe.from_json(jsonRecipe)

    # rimuoviamo eventuali ingredienti
    if ingredients_to_remove:
        new_ingredients = []
        for ingredient in suggestedRecipe.ingredients:
            if ingredient.name not in ingredients_to_remove:
                new_ingredients.append(ingredient)
        suggestedRecipe.ingredients = new_ingredients


    # aggiungiamo eventuali ingredienti
    if ingredients_to_add:
        # recuperiamo dal db gli ingredienti da aggiungere
        # da stringhe recuperiamo gli oggetti istanza della classe Ingredient
        ingredients_obj_to_add = ingService.get_ingredient_list_from_generic_list_of_string(ingredients_to_add)
        suggestedRecipe.ingredients.extend(ingredients_obj_to_add)
        

    ########################################################################################################
    # se ci sono stati cambiamenti ricalcoliamo lo score di sostenibilità e salubrità
    if ingredients_to_remove or ingredients_to_add:
        
        #print("\n\nRicalcolo.................................")

        #print("\nOLD sustainability_score : ",suggestedRecipe.sustainabilityScore)
        recipeService.compute_recipe_sustainability_score(suggestedRecipe)
        #print("NEW sustainability_score : ",suggestedRecipe.sustainabilityScore)

        # per ricalcolare il who score abbiamo bisogno delle grammature degli ingredienti -> Invochiamo il LLM
        prompt = """
                    Given the following recipe, in json format, return a json string containing the fields 'ingredients' and 'quantities', with the corresponding lists of ingredients and weights.
                    If the ingredients appear in the recipe instructions, extract the corresponding weights, in grams, otherwise assume it based on the portion generally used or recommended of the corresponding ingredient. Report only the number of the weights without grams or g.
                    Print only the JSON string. Do not add any explanation, comment, or text before or after the JSON.
                """
        answer = lcs.ask_model(input=utils.adapt_output_to_bot(suggestedRecipe),prompt=prompt)

        info = jsonpickle.decode(answer)

        ingredients = ingService.get_ingredient_list_from_generic_list_of_string(info['ingredients'])
        quantities = info['quantities']

        # calcoliamo i valori nutrizionali totali della ricetta
        nutritional_facts = recipeService.calculate_nutritional_facts_of_recipe(ingredients, quantities)

        #print("\nOLD who_score : ",suggestedRecipe.who_score)

        # calcoliamo il who score
        who_score = recipeService.compute_who_score_of_custom_recipe(nutritional_facts['protein [g]'],nutritional_facts['totalCarbohydrate [g]'],
                                                nutritional_facts['sugars [g]'],nutritional_facts['totalFat [g]'],
                                                nutritional_facts['saturatedFat [g]'],nutritional_facts['dietaryFiber [g]'],
                                                nutritional_facts['sodium [mg]'],1,"",True)

        suggestedRecipe.who_score = who_score

        #print("NEW who_score : ",suggestedRecipe.who_score)
        
        
    ########################################################################################################

    sysdate = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    userHistory = uh.UserHistory(userData.id, suggestedRecipe.id, suggestedRecipe, sysdate, status)
    
    #save the suggestion in the user history
    save_user_history(userHistory.to_plain_json())

def build_and_save_user_history_from_user_assertion(userData, jsonRecipeAssertion):
    """
    Costruisce un oggetto di cronologia suggerimento alimentare istanza della classe UserHistory
    a partire da una ricetta proposta direttamente dall'utente, calcolandone anche i valori nutrizionali,
    il punteggio di sostenibilità e il who score, e lo salva nel db.

    Args:
    - userData (User): oggetto utente contenente le informazioni dell'utente.
    - jsonRecipeAssertion : stringa JSON che rappresenta la ricetta dichiarata dall'utente, con nome, lista di ingredienti e tipologia di pasto.
    """

    custom_recipe_Assertion = jsonpickle.decode(jsonRecipeAssertion)
    ingredients = ingService.get_ingredient_list_from_generic_list_of_string(custom_recipe_Assertion['ingredients'])
    sustanaibilityScore = None

    # calcoliamo i valori nutrizionali totali della ricetta
    nutritional_facts = recipeService.calculate_nutritional_facts_of_recipe(ingredients, custom_recipe_Assertion['quantities'])

    # calcoliamo il who score
    who_score = recipeService.compute_who_score_of_custom_recipe(nutritional_facts['protein [g]'],nutritional_facts['totalCarbohydrate [g]'],
                                                nutritional_facts['sugars [g]'],nutritional_facts['totalFat [g]'],
                                                nutritional_facts['saturatedFat [g]'],nutritional_facts['dietaryFiber [g]'],
                                                nutritional_facts['sodium [mg]'],1,"",True)

    # costruiamo l'oggeto ricetta personalizzata
    asserted_custom_recipe = customRecipe.CustomRecipe(custom_recipe_Assertion["name"],ingredients, custom_recipe_Assertion["quantities"], custom_recipe_Assertion["mealType"],nutritional_facts['servingSize [g]'],nutritional_facts['calories [cal]'],nutritional_facts['totalFat [g]'],nutritional_facts['saturatedFat [g]'],nutritional_facts['totalCarbohydrate [g]'],nutritional_facts['protein [g]'],nutritional_facts['sugars [g]'],nutritional_facts['dietaryFiber [g]'],nutritional_facts['cholesterol [mg]'],nutritional_facts['sodium [mg]'], sustanaibilityScore, who_score)
    
    # calcoliamo lo score di sostenibilità
    recipeService.compute_recipe_sustainability_score(asserted_custom_recipe)

    # costruiamo l'oggetto di cronologia alimentare
    sysdate = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    userHistory = uh.UserHistory(userData.id, None, asserted_custom_recipe, sysdate, 'asserted')

    # salvataggio su db della cronologia alimentare
    save_user_history(userHistory.to_plain_json())


