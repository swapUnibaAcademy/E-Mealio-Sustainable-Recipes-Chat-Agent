import jsonpickle
import persistence.MongoConnectionManager as mongo

db = mongo.get_connection()
"""Connessione al mongo db."""

collection = db['users_food_history']
"""Collection della cronologia alimentare degli utenti : users_food_history"""


def save_user_history(userHistoryJson):
    """
    Aggiunge la cronologia alimentare dell'utente in input alla collection del db.

    Args : 
    - userHistoruJson : cronologia alimentare da aggiungere alla collection del db.
    """
    userHistory = jsonpickle.decode(userHistoryJson)
    collection.insert_one(userHistory)


def get_user_history(userId):
    """
    Restituisce la cronologia alimentare della settimana dell'utente con dato userId in input.

    Args : 
    - userId : id dell'utente di cui recuperare la cronologia alimentare.

    Returns : 
    - fullUserHistory : restituisce la cronologia alimentare dell'utente.
    """
    #get the user history of the week, given that the status is accepted
    fullUserHistory = collection.find({"userId": userId})
    return fullUserHistory


def clean_temporary_declined_suggestions(userId):
    """
    Pulisce dalla cronologia alimentare dell'utente con dato userId in input dai suggerimenti temporaneamente rifiutati (con staus = "temporary_declined").

    Args : 
    - userId : id dell'utente di cui pulire la cronologia alimentare dai suggerimenti temporaneamente rifiutati.
    """
    #clean the temporary declined suggestions
    collection.delete_many({"userId": userId, "status": "temporary_declined"})


def delete_user_history(userId):
    """
    Elimina la cronologia alimentare dell'utente con dato userId in input.

    Args : 
    - userId : id dell'utente di cui eliminare la cronologia alimentare.
    """
    collection.delete_many({"userId": userId})