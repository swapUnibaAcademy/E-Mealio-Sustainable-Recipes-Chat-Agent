import service.bot.EmbedderService as embedder
import pandas as pd
import numpy as np
import persistence.MongoConnectionManager as mongo
from sklearn.metrics.pairwise import cosine_similarity


db = mongo.get_connection()
"""Connessione al mongo db."""

collection = db['ingredients']
"""Collection degli ingredienti nel db : ingredients"""

# variabili globali per recuperare i dati una sola volta

ingredientsList = None
"""Collezione degli ingredienti presenti nel db."""

numpyIngredientEmbeddings = None
"""Embeddings degli ingredienti presenti nel db."""

def get_ingredients_list():
    """
    Recupera la lista degli ingredienti dal database MongoDB.

    Returns:
    - list: Lista di documenti contenenti gli ingredienti.
    """
    global ingredientsList
    if ingredientsList is None:
        ingredientsList = list(collection.find())
    return ingredientsList


def get_numpy_ingredient_embeddings():
    """
    Restituisce un array NumPy contenente gli embedding degli ingredienti.

    Gli embedding sono estratti dalla colonna 'ingredient_embedding' dei documenti MongoDB
    e sono convertiti in un array NumPy a 2 dimensioni.

    Returns:
    - numpy.ndarray: Array contenente gli embedding degli ingredienti.
    """
    global numpyIngredientEmbeddings
    if numpyIngredientEmbeddings is None:
        ingredients_df = pd.DataFrame(get_ingredients_list())
        numpyIngredientEmbeddings = np.vstack(ingredients_df['ingredient_embedding'], dtype=np.float32)
    return numpyIngredientEmbeddings

def get_ingredient_by_name(ingredientName):
    """
    Cerca un ingrediente nel database per nome esatto.

    Args:
    - ingredientName : Il nome dell'ingrediente da cercare.

    Returns:
    - dict or None: Il documento dell'ingrediente se trovato, altrimenti None.
    """
    ingredient = collection.find_one({"ingredient": ingredientName})
    return ingredient


def get_most_similar_ingredient(ingredientName):
    """
    Trova l'ingrediente nella collezione di ingredienti del db con valore di similarità del coseno più alto con l'ingrediente avente nome specificato in input, in particolare :
    1. Recupera dal db la lista di tutti gli ingredienti presenti
    2. Calcola l'embedding dell'ingrediente con nome fornito ingredientName
    3. Calcola la similarità del coseno tra l'embedding appena calcolato e tutti gli altri embeddings degli ingredienti presenti (recuperati dal db)
    4. Prdina gli ingrienti in ordine decrescente di similarità con l'ingrediente dato
    5. Restituisce il primo ingrediente nell'ordinamento, ovvero l'ingrediente più simile all'ingrediente dato.

    Args:
    - ingredientName : Il nome dell'ingrediente di cui vogliamo trovare l'ingrediente con similarità del coseno più alta.

    Returns:
    - dict: ingrediente con valore più alto di similarità del coseno all'ingrediente dato.
    """
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