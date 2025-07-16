import jsonpickle
import persistence.MongoConnectionManager as mongo


db = mongo.get_connection()
"""Connessione al mongo db."""

collection = db['users']
"""Collection degli utenti : users"""


def get_all_users():
    """
    Restituisce la collection di tutti gli utenti presenti nel db.
    
    Returns :
    - users : collection di tutti gli utenti presenti nel db.
    """
    users = collection.find()
    return users


def save_user(userJson):
    """
    Aggiunge l'utente dato in input nella collection degli utenti nel db.
    
    Args :
    - userJson : stringa JSON che rappresenta l'utente da aggiungere alla collection degli utenti nel db.
    """
    user = jsonpickle.decode(userJson)
    collection.insert_one(user)


def update_user(userJson):
    """
    Aggiorna l'utente dato in input come stringa JSON nella collection degli utenti nel db.

    Se l'utente con dato id non è già presente nella collection, non viene aggiunto come nuova entrata (upsert=False).

    Args : 
    - userJson : stringa Json che rappresenta l'utente da aggiornare nella collection degli utenti nel db.
    """
    user = jsonpickle.decode(userJson)
    collection.update_one({"id":user['id']}, {"$set": user}, upsert=False)


def get_user_by_user_id(userId):
    """
    Restituisce l'utente con dato userId in input dalla collection degli utenti del db.

    Args :
    - userId : id dell'utente da recuperare dalla collection degli utenti.

    Returns : 
    - user : utente con dato userId dato in input recuperato dalla collection degli utenti.
    """
    user = collection.find_one({"id":userId})
    return user


def update_user_last_interaction(userId, lastInteraction):
    """
    Aggiorna l'ultima interazione dell'utente con dato userId nella collection degli utenti nel db.

    Se l'utente con dato id non è già presente nella collection, non viene aggiunto come nuova entrata (upsert=False).

    Args : 
    - userId : id dell'utente di cui aggiornare l'ultima interazione.
    - lastInteraction : ultima interazione dell'utente avvenuta con il sistema.
    """
    collection.update_one({"id":userId}, {"$set": {"lastInteraction": lastInteraction}}, upsert=False)


def update_user_tastes(userId, tastes):
    """
    Aggiorna i gusti dell'utente con dato userId nella collection degli utenti nel db.

    Se l'utente con dato id non è già presente nella collection, non viene aggiunto come nuova entrata (upsert=False).

    Args : 
    - userId : id dell'utente di cui aggiornare l'ultima interazione.
    - tastes : gusti dell'utente.
    """
    collection.update_one({"id":userId}, {"$set": {"tastes": tastes}}, upsert=False)


def delete_user_by_user_id(userId):
    """
    Elimina l'utente con dato userId dalla collection degli utenti del db.

    Args : 
    - userId : id dell'utente da eliminare dalla collection degli utenti.
    """
    collection.delete_one({"id":userId})


def get_all_users_with_reminder():
    """
    Restituisce l'insieme degli utenti che hanno il promemoria attivo (reminder=True) dalla collection degli utenti nel db.

    Returns : 
    - users : utenti della collection degli utenti del db che hanno il promemoria attivo.
    """
    users = collection.find({"reminder": True})
    return users