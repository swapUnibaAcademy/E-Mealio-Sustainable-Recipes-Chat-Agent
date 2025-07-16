import jsonpickle
import numpy as np
import service.domain.FoodHistoryService as foodHistory
import service.domain.RecipeService as recipeService
import service.domain.UserDataService as userService
import service.bot.EmbedderService as embedder
import persistence.RecipePersistence as recipePersistence
import pandas as pd
import persistence.MongoConnectionManager as mongo
import service.bot.LogService as log
import datetime
from sklearn.metrics.pairwise import cosine_similarity

PRINT_LOG = True
"""Flag che indica se stampare i log (di default True)."""

db = mongo.get_connection()
"""Connessione al mongodb."""
    
def get_recipe_suggestion(mealDataJson, userData):
    """
    A partire dai dati dell'utente e dalle informazioni che l'utente ha fornito riguardo al suggerimento di ricetta
    che vuole ottenere, restituisce dal db la ricetta che sarà fornita come suggerimento all'utente.

    Args : 
    - mealDataJson : informazioni che l'utente ha fornito riguardo al suggerimento di ricetta che vuole ricevere.
    - userData : dati dell'utente che ha chiesto il suggerimento di una ricetta.

    Returns : 
    - Recipe : ricetta che viene fornita come suggerimento all'utente.
    """

    print("\nDebug (get_recipe_suggestion)")
    print("\nmealDataJson : \n", mealDataJson)
    print("\nuserData : \n", userData)

    """
    mealDataJson ha il seguente formato :
     
    {
    "mealType": "",
    "recipeName": "",
    "sustainabilityScore": "",
    "ingredients_desired": [],
    "ingredients_not_desired": [],
    "cookingTime": "",
    "healthiness": ""  
    }
    """

    #restriction and allergy and meal type must always be respected
    #the search will try to respect healthiness and meal duration if possible, but if no recipe is found that respects them, it will return a recipe that does not respect them
    #the system keeps track of the kind of constraints that are not respected in order to give the user a feedback about them
    
    """
    Nella query : 
    - $and specifica che tutte le condizioni devono essere vere contemporaneamente
    - $in specifica che il risultato deve essere in un intervallo [x, y]
    - $gte specifica che il risultato deve essere maggiore o uguale ad un x
    
    Le condizioni fisse sono : 
    - 0 < sustainability_label < 1 
    - percentage_covered_cfp >= 70
    - percentage_covered_wfp >= 70
    - disabled = false per considerare solo le ricette attive

    Mentre le condizioni restanti, TAGS_..., verranno sostituite dinamicamente in base ai valori del particolare utente.
    """

    queryTemplate =  """{ "$and": [ 
        { "sustainability_label": { "$in": [0, 1] } }, 
        { "percentage_covered_cfp": { "$gte": 70 } }, 
        { "percentage_covered_wfp": { "$gte": 70 } },
        { "disabled": false },
        {TAGS_SUSTAINABILITY},
        {TAGS_RESTRICTIONS},
        {TAGS_ALLERGENES},
        {TAGS_DIETARY_PREFERENCES},
        {TAGS_MEAL_TYPE},
        {TAGS_USER_HISTORY},
        {TAGS_HEALTHINESS},
        {TAGS_MEAL_DURATION},
        ] }"""

    tagsSustainability = ""
    tagsRestrictions = ""   
    allergenes = ""
    tagsMealType = ""
    tagsUserHistory = ""
    tagsHealthiness = ""
    tagsMealDuration = ""
    tagsPreference = ""


    # nelle proiezioni usiamo 1 per indicare i campi che vogliamo considerare nel risultato.
    projection = {"_id": 1, "recipe_id": 1, "title_embedding": 1, "ingredients_embedding": 1, "sustainability_score": 1, "who_score":1} 

    #initialize as empty numpy array
    desiredIngredientsEmbedding = np.array([])
    notDesiredIngredientsEmbedding = np.array([])
    recipeNameEmbedding = np.array([])

    mealData = jsonpickle.decode(mealDataJson) 

    # controlliamo se l'utente ha fornito qualche informazione riguardo al suggerimento delle ricetta

    if(mealData['recipeName'] != None and mealData['recipeName']  != ''):
        recipeNameEmbedding = embedder.embed_sentence(mealData['recipeName'])

    if(mealData['ingredients_desired'] != None and mealData['ingredients_desired']  != ''):
        desiredIngredientsEmbeddingString = ', '.join(mealData['ingredients_desired'])
        desiredIngredientsEmbedding = embedder.embed_list(desiredIngredientsEmbeddingString, False)
    else:
        tastes = userService.get_taste(userData.id, mealData['mealType'].lower())
        if(tastes != None and tastes != []):
            desiredIngredientsEmbedding = np.array(tastes, dtype=np.float32)
    

    # oltre agli ingredienti che l'utente ha specificato non volere nel suggerimento aggiungiamo quelli che non li piacciono salvati nel profilo
    disliked_ingredients_in_user_profile = userService.get_disliked_ingredients(userData.id)

    all_disliked_ingredients = []

    if (disliked_ingredients_in_user_profile!= None and disliked_ingredients_in_user_profile  != ''):
        for ingredient in disliked_ingredients_in_user_profile:
            # non consideriamo temporaneamente eventuali ingredienti non desiderati
            # se l'utente ha specificato esplicitamente di volerli nel suggerimento di ricetta
            if ingredient not in mealData['ingredients_desired']:
                all_disliked_ingredients.append(ingredient)


    if (mealData['ingredients_not_desired']!= None and mealData['ingredients_not_desired']  != ''):
        for ingredient in mealData['ingredients_not_desired']:
            if ingredient not in all_disliked_ingredients:
                all_disliked_ingredients.append(ingredient)


    #print("\nmealData['ingredients_desired'] : ", mealData['ingredients_desired'])
    #print("disliked_ingredients_in_user_profile : ",disliked_ingredients_in_user_profile)
    #print("all_disliked_ingredients : ",all_disliked_ingredients)

    if all_disliked_ingredients != None:
        notDesiredIngredientsEmbeddingString = ', '.join(all_disliked_ingredients)
        notDesiredIngredientsEmbedding = embedder.embed_list(notDesiredIngredientsEmbeddingString, False)

    # collection delle ricette nel db
    recipes = db['recipes']

    """
    Se l'utente ha fornito un valore di sostenibilità massimo creiamo un filtro per specificare tale condizione,
    dove $lt specifica minore a uguale ad un x.
    """

    #filter for the sustainability score
    if(mealData['sustainabilityScore'] != ""):
        tagsSustainability = """ "sustainability_score": { "$lt": SUSTAINABILITY_VALUE } """
        tagsSustainability = tagsSustainability.replace("SUSTAINABILITY_VALUE",str(mealData['sustainabilityScore']))


    """
    Dal campo "tags" delle ricette nel db, aggiungiamo delle condizioni per considerare le restrizioni dell'utente,
    le allergie, la tipologia di pasto e il tempo di preparazione.

    Nella query "$regex" specifica che esista un campo con una data stringa in una lista di stringhe.
    """

    #filter for the restrictions
    restrictions = userData.restrictions
    if(restrictions != None and restrictions != '' and restrictions != []):
        tagsRestrictions = """ "$and": [ """
        for restriction in restrictions:
            tagsRestrictions += """ {"tags": { "$regex": "%s" }}, """ % restriction
        tagsRestrictions = tagsRestrictions[:-2]
        tagsRestrictions += """ ] """


    #filter for the allergies 
    allergies = userData.allergies
    if(allergies != None and allergies != '' and allergies != []):
        allergenes = """ "$and": [ """
        for allergen in allergies:
            allergenes += """ {"tags": { "$regex": "%s-free" }}, """ % allergen
        allergenes = allergenes[:-2]
        allergenes += """ ] """


    # eventuali restrizioni future da inserire come vincolo opzionale
    evolving_diet = userService.get_evolving_diet(userData.id) 

    if(evolving_diet != None and evolving_diet != '' and evolving_diet != []):
        tagsPreference = """ "$and": [ """
        for pref in evolving_diet:
            tagsPreference += """ {"tags": { "$regex": "%s" }}, """ % pref
        tagsPreference = tagsPreference[:-2]
        tagsPreference += """ ] """



    #filter for the meal type    
    mealType = mealData['mealType']
    if(mealType == "Dinner"):
        tagsMealType = """ "$and": [{ "tags": { "$regex": "main-dish" } }, { "tags": { "$regex": "dinner" } }] """
    elif(mealType == "Lunch"):
        tagsMealType = """ "$and": [ { "tags": { "$regex": "main-dish" } }, { "tags": { "$regex": "lunch" } } ] """
    elif(mealType == "Breakfast"):
        tagsMealType = """ "tags": { "$regex": "breakfast" } """
    elif(mealType == "Break"):
        tagsMealType = """ "tags": { "$regex": "snack" } """
    #no meal type specified, take all the meal types as filter
    else:
        tagsMealType = """ "$or": [
        "$and": [{ "tags": { "$regex": "main-dish" } }, { "tags": { "$regex": "dinner" } }],
        "$and": [{ "tags": { "$regex": "main-dish" } }, { "tags": { "$regex": "lunch" } }],
        "tags": { "$regex": "breakfast" },
        "tags": { "$regex": "snack" }
        ] """


    #filter for the meal duration
    cookingTime = mealData['cookingTime']
    if(cookingTime == "short"):
        tagsMealDuration = """ "tags": { "$regex": "15-minutes-or-less" } """
    elif(cookingTime == "medium"):
        tagsMealDuration = """ "tags": { "$regex": "30-minutes-or-less" } """


    """
    Aggiungiamo alla query una condizione per evitare di suggerire una ricetta che 
    l'utente ha mangiato nell'ultima settimana.

    Nella query $nin specifica che il valore di un dato campo (recipe_id) non deve essere nell'elenco fornito.
    """

    # recupera le ricette che l'utente ha mangiato nell'ultima settimana
    userHistory = foodHistory.get_user_history_of_week(userData.id, False)

    if userHistory != None and len(userHistory) > 0:
        #filter for not being in the user history
        tagsUserHistory = """"recipe_id": {"$nin": ["""
        for history in userHistory:
            tagsUserHistory +=  str(history['recipeId']) + ","
        tagsUserHistory = tagsUserHistory[:-1]
        tagsUserHistory += "] }"

    #filter for the healthiness
    healthiness = mealData['healthiness']
    if(healthiness == "yes"):
        tagsHealthiness = """ "healthiness_label": 0 """

    
    #replace the tags in the query template

    # filtri obbligatori che devono essere sempre presenti nella query.
    mandatoryReplacement = [["TAGS_SUSTAINABILITY",tagsSustainability],
                            ["TAGS_RESTRICTIONS",tagsRestrictions],
                            ["TAGS_ALLERGENES",allergenes],
                            ["TAGS_MEAL_TYPE",tagsMealType]]
    

    # filtri opzionali che possono essere presenti nella query.
    notMadatoryReplacement = [["TAGS_USER_HISTORY",tagsUserHistory],
                              ["TAGS_HEALTHINESS",tagsHealthiness],
                              ["TAGS_MEAL_DURATION",tagsMealDuration],
                              ["TAGS_DIETARY_PREFERENCES",tagsPreference]]
    
    numberOfFoundRecipes = 0
    numReplacement = len(notMadatoryReplacement)
    removedConstraints = []

    while(numberOfFoundRecipes == 0 and numReplacement > 0):

        """
        Inizialmente costruiamo la query con i filtri obbligatori e tutti quelli opzionali, se non troviamo
        risultati volta per volta eliminiamo qualche vincolo opzionale fino a trovare almeno un risultato.
        """

        # costruiamo la query
        queryText = query_template_replacement(mandatoryReplacement, notMadatoryReplacement,numReplacement,queryTemplate)
        
        # convert query in a dict
        query = jsonpickle.decode(queryText)

        # effettuiamo la query sul db
        suggestedRecipes = recipes.find(query,projection)
        log.save_log("Executed query" + queryText, datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        
        numberOfFoundRecipes = recipes.count_documents(query)

        # decrementiamo di uno il numero di filtri opzionali da applicare
        numReplacement -= 1

        # se il valore del filtro rimosso era una stringa vuota "" non lo aggiungiamo a removedConstraints
        # altrimenti lo salviamo per capire quali filtri abbiamo rimosso per poter trovare dei risultati

        #remove a constraint if actually was valored
        if(numberOfFoundRecipes == 0 and notMadatoryReplacement[numReplacement][1]!=""):
            removedConstraints.append(notMadatoryReplacement[numReplacement][0])
    

    # caso in cui anche elimando tutti i filtri opzionali, con i filtri obbligatori non riusciamo a trovare risultati
    if(numberOfFoundRecipes == 0):
        #no recipe found
        return None
    

    log.save_log("Retrieved " + str(numberOfFoundRecipes) + " recipes", datetime.datetime.now(), "System", userData.id, PRINT_LOG)

    # a partire dalle ricette recuperate dalla query con le condizioni, troviamo la ricetta che è più simile al gusto dell'utente
    suggestedRecipe = get_preferable_recipe_by_taste(suggestedRecipes,desiredIngredientsEmbedding,notDesiredIngredientsEmbedding,recipeNameEmbedding,userData)

    """
    Se l'utente non ha espresso ingredienti desiderati né indesiderati non ha senso calcolare la similarità
    con il suo gusto, ma semplicmente ordiniamo le ricette in base al valore di sostenibilità.
    """
    if(suggestedRecipe == None):
        #order the suggested recipes by the sustainability score (the lower the better)
        suggestedRecipes = suggestedRecipes.sort("sustainability_score")
        suggestedRecipe = suggestedRecipes[0]


    #get the full recipe from the database
    suggestedRecipe = recipePersistence.get_recipe_by_id(int(suggestedRecipe["recipe_id"]))

    #convert the recipe to a Recipe object
    suggestedRecipe = recipeService.convert_in_emealio_recipe(suggestedRecipe,removedConstraints,mealType)

    #print("\nsuggestedRecipe : \n",suggestedRecipe)
    return suggestedRecipe

def query_template_replacement (mandatoryRepalcement, notMandatoryReplacement, numberReplacement, queryTemplate):
    """
    Dato il template della query sostituisce i placeholder con i filtri obbligatori e opzionali, in modo
    da genereare la query finale da effettuare sul db.

    Args : 
    - mandatoryRepalcement : lista di filtri obbligatori nel formato `[placeholder, valore]`
    - notMandatoryReplacement : lista di filtri opzionali nel formato `[placeholder, valore]`
    - numberReplacement : numero di filtri opzionali da applicare nella sostituzione.
    - queryTemplate : stringa rappresentatne il template della query con ancora i placeholder da rimpiazzare.

    Returns : 
    - queryTemplate : stringa rappresentate la query finale che verrà effettivamente usata sul db.
    """

    for replacement in mandatoryRepalcement:
        queryTemplate = queryTemplate.replace(replacement[0],replacement[1])

    for replacement in range(0,numberReplacement):
        queryTemplate = queryTemplate.replace(notMandatoryReplacement[replacement][0],str(notMandatoryReplacement[replacement][1]))

    remainingReplacement = len(notMandatoryReplacement) - numberReplacement

    #clean the query from the not mandatory replacement that are not used
    for replacement in range(len(notMandatoryReplacement)-remainingReplacement,len(notMandatoryReplacement)):
        queryTemplate = queryTemplate.replace(notMandatoryReplacement[replacement][0],"")

    return queryTemplate


def get_preferable_recipe_by_taste(recipeSet, desiredIgredientsEmbeddings, notDesiredIgredientsEmbeddings, recipeNameEmbedding, userData):
    """
    A partire da tutte le ricette recuperate dal db che hanno soddisfatto le condizioni della query,
    calcola per ciascuna un punteggio di similarità (del coseno) del gusto con l'utente corrrente, le ordina 
    in modo decrescente rispetto a tale punteggio, e restituisce la ricetta che è prima nell'ordinamento.

    Args : 
    - recipeSet : insieme delle ricette che sono state restituite come risultato della query sul db.
    - desiredIgredientsEmbeddings : embeddings degli ingredienti che l'utente desidera avere nella ricette che vuole ricevere come sugggerimento.
    - notDesiredIgredientsEmbeddings : embbeddings degli ingredienti che l'utente non desidera avere nella ricette che vuole ricevere come sugggerimento.
    - recipeNameEmbedding : embeddings del nome della ricetta che l'utente desidera avere come sugggerimento.
    - userData : dati dell'utente

    Returns : 
    - highestTasteScoreRecipe : ricetta che è più simile ai gusti dell'utente.
    """
    
    log.save_log("Start similarity searching ", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
    
    #if both desiredIgredientsEmbeddings and notDesiredIgredientsEmbeddings are None then return the first recipe
    if(len(desiredIgredientsEmbeddings) == 0 and len(notDesiredIgredientsEmbeddings) == 0):
        return None
    
    # Convert recipeSet to DataFrame
    recipes_df = pd.DataFrame(list(recipeSet))

    # Initialize taste_score
    recipes_df['taste_score'] = 0.0

    # Compute cosine similarity for desired ingredients
    if len(desiredIgredientsEmbeddings) > 0:
        recipes_df['cosine_similarity_desired'] = cosine_similarity(
            np.vstack(recipes_df['ingredients_embedding']),
            desiredIgredientsEmbeddings.reshape(1, -1)
        ).flatten()
        recipes_df['taste_score'] += recipes_df['cosine_similarity_desired']
    
    # Compute cosine similarity for not desired ingredients
    if len(notDesiredIgredientsEmbeddings) > 0:
        recipes_df['cosine_similarity_not_desired'] = cosine_similarity(
            np.vstack(recipes_df['ingredients_embedding'], dtype=np.float32),
            notDesiredIgredientsEmbeddings.reshape(1, -1)
        ).flatten()
        recipes_df['taste_score'] -= recipes_df['cosine_similarity_not_desired']
    
    # Compute cosine similarity for recipe names
    if len(recipeNameEmbedding) > 0:
        recipes_df['cosine_similarity_recipe_name'] = cosine_similarity(
            np.vstack(recipes_df['title_embedding']),
            recipeNameEmbedding.reshape(1, -1)
        ).flatten()
        recipes_df['taste_score'] += recipes_df['cosine_similarity_recipe_name']  # Adjust weighting as needed
    
    # Sort recipes by taste_score in descending order
    preferred_recipes = recipes_df.sort_values(by='taste_score', ascending=False)
    highestTasteScoreRecipe = preferred_recipes.iloc[0].to_dict()
    log.save_log("End similarity searching ", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
    
    return highestTasteScoreRecipe