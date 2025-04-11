import pandas as pd
import numpy as np
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer

def compute_title_embedding():
    client = MongoClient('localhost', 27017)
    db = client['emealio_food_db']
    recipes_db = db['recipes']

    #load the sentence transformer model
    model = SentenceTransformer('Alibaba-NLP/gte-large-en-v1.5', trust_remote_code=True)

    #loop over the recipes
    recipes_cursor = recipes_db.find()

    print("Computing title embeddings...")
    j = 0
    for recipe in recipes_cursor:
        #get the title and the ingredients
        title = recipe['title']

        #The commented instruction allows to compute the embeddings
        #using directly the whole 'simplified_ingredients' field.
        #This approach is deprecated in favour of the one currently used.

        #ingredients = recipe['simplified_ingredients']
        title_embedding = model.encode(title)
        #ingredients_embedding = model.encode(ingredients)
        recipes_db.update_one({"_id": recipe['_id']}, {"$set": {"title_embedding": pd.Series(title_embedding).to_list()}})
        #recipes_db.update_one({"_id": recipe['_id']}, {"$set": {"ingredients_embedding": pd.Series(ingredients_embedding).to_list()}})
        if j % 100 == 0:
            print("Done ", j)
        j += 1
    print("Done")

def compute_ingredients_embedding():
    client = MongoClient('localhost', 27017)
    db = client['emealio_food_db']
    ingredients_db = db['ingredients']

    #load the sentence transformer model
    model = SentenceTransformer('Alibaba-NLP/gte-large-en-v1.5', trust_remote_code=True)

    #loop over the ingredients
    ingredients_cursor = ingredients_db.find()
    print("Computing ingredients embeddings...")
    j = 0
    for ingredient in ingredients_cursor:
        #get the title and the ingredients
        title = ingredient['ingredient']
        title_embedding = model.encode(title)
        ingredients_db.update_one({"_id": ingredient['_id']}, {"$set": {"ingredient_embedding": pd.Series(title_embedding).to_list()}})
        if j % 100 == 0:
            print("Done ", j)
        j += 1
    print("Done")

def compute_recipe_ingredient_embedding():
    client = MongoClient('localhost', 27017)
    db = client['emealio_food_db']
    recipes_db = db['recipes']
    ingredients_db = db['ingredients']

    #loop over the recipes
    recipes_cursor = recipes_db.find()
    j = 0
    print("Computing recipe ingredient embeddings...")
    for recipe in recipes_cursor:
        #get the title and the ingredients
        title = recipe['title']
        ingredients = recipe['simplified_ingredients']
        #remove the brackets
        ingredients = ingredients[1:-1]
        ingredientsArray = ingredients.split(", ")

        #recipe_embeddind as a blank 1024 array
        recipe_embedding = np.zeros(1024)
        for i in range(len(ingredientsArray)):
            ingredient = ingredients_db.find_one({'ingredient': ingredientsArray[i]})
            if ingredient is not None:
                ingredient_embedding = ingredient['ingredient_embedding']
                recipe_embedding += np.array(ingredient_embedding)

        recipes_db.update_one({"_id": recipe['_id']}, {"$set": {"ingredients_embedding": pd.Series(recipe_embedding).to_list()}})
        if j % 100 == 0:
            print("Done ", j)
        j += 1

    print("Done")
    
###### MAIN ######### 
compute_title_embedding()
compute_ingredients_embedding()
compute_recipe_ingredient_embedding()