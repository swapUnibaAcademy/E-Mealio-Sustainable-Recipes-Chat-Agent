import service.bot.EmbedderService as embedder
import pandas as pd
import numpy as np
import persistence.MongoConnectionManager as mongo
from sklearn.metrics.pairwise import cosine_similarity

db = mongo.get_connection()
collection = db['ingredients']
ingredientsList = None
numpyIngredientEmbeddings = None

def get_ingredients_list():
    global ingredientsList
    if ingredientsList is None:
        ingredientsList = list(collection.find())
    return ingredientsList

def get_numpy_ingredient_embeddings():
    global numpyIngredientEmbeddings
    if numpyIngredientEmbeddings is None:
        ingredients_df = pd.DataFrame(get_ingredients_list())
        numpyIngredientEmbeddings = np.vstack(ingredients_df['ingredient_embedding'], dtype=np.float32)
    return numpyIngredientEmbeddings

def get_ingredient_by_name(ingredientName):
    ingredient = collection.find_one({"ingredient": ingredientName})
    return ingredient

def get_most_similar_ingredient(ingredientName):
    ingredients_df = pd.DataFrame(get_ingredients_list())
    #embed ingredientName
    ingredientNameEmbedding = embedder.embed_sentence(ingredientName)

    similarity = cosine_similarity(
            get_numpy_ingredient_embeddings(),
            ingredientNameEmbedding.reshape(1, -1)
        ).flatten()
    
    ingredients_df['similarity'] = similarity

    #sort the ingredients by similarity
    ingredients_df = ingredients_df.sort_values(by='similarity', ascending=False)
    top_ingredient_name = ingredients_df.head(1)["ingredient"].values[0]

    return get_ingredient_by_name(top_ingredient_name)