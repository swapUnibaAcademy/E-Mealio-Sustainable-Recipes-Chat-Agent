import service.bot.EmbedderService as embedder
import pandas as pd
import jsonpickle
import numpy as np
import persistence.MongoConnectionManager as mongo
from sklearn.metrics.pairwise import cosine_similarity


db = mongo.get_connection()
collection = db['recipes']
recipe_list = None
sustainable_recipe_list = None
numpyRecipeEmbeddings = None

#treat the recipe list as a singleton in order to avoid to load it every time
def get_recipe_list():
    global recipe_list
    if recipe_list is None:
        projection = {"_id": 1, "recipe_id": 1, "title_embedding": 1} 
        recipe_list = list(collection.find({},projection))
    return recipe_list

def get_numpy_recipe_embeddings():
    global numpyRecipeEmbeddings
    if numpyRecipeEmbeddings is None:
        recipe_df = pd.DataFrame(get_recipe_list())
        numpyRecipeEmbeddings = np.vstack(recipe_df['title_embedding'], dtype=np.float32)
    return numpyRecipeEmbeddings

def get_recipe_by_id(recipeId):
    recipe = collection.find_one({"recipe_id": recipeId})
    return recipe

def get_recipe_by_title(recipeTitle):
    query = """{"title": { "$regex": "RECIPE_TITLE", "$options": "i" }}"""
    query = query.replace('RECIPE_TITLE',recipeTitle)
    query = jsonpickle.decode(query)
    recipe = collection.find(query)
    found = list(recipe)
    if found is None or len(found) == 0:
        return None
    found.sort(key=lambda x: len(x["title"]))
    first = found[0]
    return first

def get_most_similar_recipe(recipeTitle):
    recipe_df = pd.DataFrame(get_recipe_list())
    #embed recipeTitle
    recipeTitleEmbedding = embedder.embed_sentence(recipeTitle)

    #compute the similarity between the recipeTitle and the recipes in the database
    recipe_df['similarity'] = cosine_similarity(
            get_numpy_recipe_embeddings(),
            recipeTitleEmbedding.reshape(1, -1)
        ).flatten()
    
    #sort the recipes by similarity
    recipe_df = recipe_df.sort_values(by='similarity', ascending=False)
    top_recipe_id= int(recipe_df.head(1)["recipe_id"].values[0])
    return get_recipe_by_id(top_recipe_id)