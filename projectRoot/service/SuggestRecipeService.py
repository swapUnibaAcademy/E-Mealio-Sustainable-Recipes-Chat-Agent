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

db = mongo.get_connection()
    
def get_recipe_suggestion(mealDataJson, userData):

    #restriction and allergy and meal type must always be respected
    #the search will try to respect healthiness and meal duration if possible, but if no recipe is found that respects them, it will return a recipe that does not respect them
    #the system keeps track of the kind of constraints that are not respected in order to give the user a feedback about them
    
    queryTemplate =  """{ "$and": [ 
        { "sustainability_label": { "$in": [0, 1] } }, 
        { "percentage_covered_cfp": { "$gte": 70 } }, 
        { "percentage_covered_wfp": { "$gte": 70 } },
        { "disabled": false },
        {TAGS_SUSTAINABILITY},
        {TAGS_RESTRICTIONS},
        {TAGS_ALLERGENES},
        {TAGS_MEAL_TYPE},
        {TAGS_USER_HISTORY},
        {TAGS_HEALTHINESS},
        {TAGS_MEAL_DURATION}
        ] }"""

    tagsSustainability = ""
    tagsRestrictions = ""   
    allergenes = ""
    tagsMealType = ""
    tagsUserHistory = ""
    tagsHealthiness = ""
    tagsMealDuration = ""
    projection = {"_id": 1, "recipe_id": 1, "title_embedding": 1, "ingredients_embedding": 1, "sustainability_score": 1} 

    #initialize as empty numpy array
    desiredIngredientsEmbedding = np.array([])
    notDesiredIngredientsEmbedding = np.array([])
    recipeNameEmbedding = np.array([])

    mealData = jsonpickle.decode(mealDataJson)

    if(mealData['recipeName'] != None and mealData['recipeName']  != ''):
        recipeNameEmbedding = embedder.embed_sentence(mealData['recipeName'])

    if(mealData['ingredients_desired'] != None and mealData['ingredients_desired']  != ''):
        desiredIngredientsEmbeddingString = ', '.join(mealData['ingredients_desired'])
        desiredIngredientsEmbedding = embedder.embed_list(desiredIngredientsEmbeddingString, False)
    else:
        tastes = userService.get_taste(userData.id, mealData['mealType'].lower())
        if(tastes != None and tastes != []):
            desiredIngredientsEmbedding = np.array(tastes, dtype=np.float32)
    
    if(mealData['ingredients_not_desired'] != None and mealData['ingredients_not_desired']  != ''):
        notDesiredIngredientsEmbeddingString = ', '.join(mealData['ingredients_not_desired'])
        notDesiredIngredientsEmbedding = embedder.embed_list(notDesiredIngredientsEmbeddingString, False)
    
    recipes = db['recipes']

    #filter for the sustainability score
    if(mealData['sustainabilityScore'] != ""):
        tagsSustainability = """ "sustainability_score": { "$lt": SUSTAINABILITY_VALUE } """
        tagsSustainability = tagsSustainability.replace("SUSTAINABILITY_VALUE",str(mealData['sustainabilityScore']))

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

    #obtain the user history
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

    #filter for the meal duration
    cookingTime = mealData['cookingTime']
    if(cookingTime == "short"):
        tagsMealDuration = """ "tags": { "$regex": "15-minutes-or-less" } """
    elif(cookingTime == "medium"):
        tagsMealDuration = """ "tags": { "$regex": "30-minutes-or-less" } """

    #replace the tags in the query template
    mandatoryReplacement = [["TAGS_SUSTAINABILITY",tagsSustainability],["TAGS_RESTRICTIONS",tagsRestrictions],["TAGS_ALLERGENES",allergenes],["TAGS_MEAL_TYPE",tagsMealType]]
    notMadatoryReplacement = [["TAGS_USER_HISTORY",tagsUserHistory],["TAGS_HEALTHINESS",tagsHealthiness],["TAGS_MEAL_DURATION",tagsMealDuration]]

    numberOfFoundRecipes = 0
    numReplacement = len(notMadatoryReplacement)

    removedConstraints = []

    while(numberOfFoundRecipes == 0 and numReplacement > 0):
        queryText = query_template_replacement(mandatoryReplacement, notMadatoryReplacement,numReplacement,queryTemplate)
        #convert query in a dict
        query = jsonpickle.decode(queryText)
        suggestedRecipes = recipes.find(query,projection)
        log.save_log("Executed query" + queryText, datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        
        numberOfFoundRecipes = recipes.count_documents(query)
        numReplacement -= 1

        #remove a constraint if actually was valored
        if(numberOfFoundRecipes == 0 and notMadatoryReplacement[numReplacement][1]!=""):
            removedConstraints.append(notMadatoryReplacement[numReplacement][0])
    
    if(numberOfFoundRecipes == 0):
        #no recipe found
        return None
    
    log.save_log("Retrieved " + str(numberOfFoundRecipes) + " recipes", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        
    suggestedRecipe = get_preferable_recipe_by_taste(suggestedRecipes,desiredIngredientsEmbedding,notDesiredIngredientsEmbedding,recipeNameEmbedding,userData)

    if(suggestedRecipe == None):
        #order the suggested recipes by the sustainability score (the lower the better)
        suggestedRecipes = suggestedRecipes.sort("sustainability_score")
        suggestedRecipe = suggestedRecipes[0]

    #get the full recipe from the database
    suggestedRecipe = recipePersistence.get_recipe_by_id(int(suggestedRecipe["recipe_id"]))

    #convert the recipe to a Recipe object
    suggestedRecipe = recipeService.convert_in_emealio_recipe(suggestedRecipe,removedConstraints,mealType)

    return suggestedRecipe

def query_template_replacement (mandatoryRepalcement, notMandatoryReplacement, numberReplacement, queryTemplate):
    for replacement in mandatoryRepalcement:
        queryTemplate = queryTemplate.replace(replacement[0],replacement[1])

    for replacement in range(0,numberReplacement):
        queryTemplate = queryTemplate.replace(notMandatoryReplacement[replacement][0],str(notMandatoryReplacement[replacement][1]))

    remainingReplacement = len(notMandatoryReplacement) - numberReplacement

    #clean the query from the not mandatory replacement that are not used
    for replacement in range(len(notMandatoryReplacement)-remainingReplacement,len(notMandatoryReplacement)):
        queryTemplate = queryTemplate.replace(notMandatoryReplacement[replacement][0],"")

    return queryTemplate

def get_preferable_recipe_by_taste(recipeSet, desiredIgredientsEmbeddings, notDesiredIgredientsEmbeddings,recipeNameEmbedding, userData):
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