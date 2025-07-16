import service.bot.EmbedderService as embedder
import pandas as pd
import jsonpickle
import numpy as np
import persistence.MongoConnectionManager as mongo
from sklearn.metrics.pairwise import cosine_similarity


db = mongo.get_connection()
"""Connessione al mongo db."""

collection = db['recipes']
"""Collection delle ricette nel db : recipes"""

# treat the recipe list as a singleton in order to avoid to load it every time
recipe_list = None
"""Lista delle ricette presenti nel db."""

numpyRecipeEmbeddings = None
"""Embeddings delle ricette presenti nel db."""

sustainable_recipe_list = None
"""Lista delle ricette sostenibili nel db."""



def get_recipe_list():
    """
    Recupera dal db tutte le ricette presenti, considerando solo i campi id, recipe_id e title_embedding.
    
    Returns :
    - recipe_list : lista di tutte le ricette presenti nel db.
    """
    global recipe_list
    if recipe_list is None:
        projection = {"_id": 1, "recipe_id": 1, "title_embedding": 1} 
        recipe_list = list(collection.find({},projection))
    return recipe_list


def get_numpy_recipe_embeddings():
    """
    Recupera dal db gli embeddings di tutte le ricette presenti.
    
    Returns :
    - numpyRecipeEmbeddings : embeddings di tutte le ricette presenti nel db.
    """
    global numpyRecipeEmbeddings
    if numpyRecipeEmbeddings is None:
        recipe_df = pd.DataFrame(get_recipe_list())
        numpyRecipeEmbeddings = np.vstack(recipe_df['title_embedding'], dtype=np.float32)
    return numpyRecipeEmbeddings


def get_recipe_by_id(recipeId):
    """
    Restituisce dalla collezione di ricette presenti nel db la ricetta con l'id specificato in input.

    Args :
    - recipeId : id della ricetta da ricerca nella collezione.

    Returns :
    - recipe : ricetta con id specificato in input.
    """
    recipe = collection.find_one({"recipe_id": recipeId})
    return recipe


def get_recipe_by_title(recipeTitle):
    """
    Restituisce dalla collezione di ricette presenti nel db la ricetta con il titolo specificato in input, in particolare : 
    1. Ricerca la ricetta nel db il cui titolo corrisponde (case-insensitive) a recipeTitle usando una regex. 
    2. Ordina i risultati in ordine crescente della lunghezza dei titoli delle ricette.
    3. Restituisce la prima ricetta dell'ordinamento.

    Args : 
    - recipeTitle : titolo della ricetta da ricercare nella collezione.

    Returns : 
    - first : ricetta con titolo specificato in input.
    
    """
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
    """
    Trova la ricetta nella collezione di ricette del db con valore di similarità del coseno più alto con la ricetta avente titolo specificato in input, in particolare :
    1. Calcola l'embedding del titolo della ricetta dato 
    2. Calcola la similarità del coseno tra l'embedding appena calcolato e tutti gli altri embeddings delle ricette presenti nel db
    3. Restituisce la ricetta con la più alta similarità all'embedding di recipeTitle.
    
    Args : 
    - recipeTitle : Titolo della ricetta di cui vogliamo trovare la ricetta con similarità del coseno più alta. 

    Returns : 
    - recipe : ricetta con valore più alto di similarità del coseno alla ricetta data.
    """
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