from pymongo import MongoClient

client = None
"""Client per la connessione al mongo db."""

connection = None
"""Connessione al mongo db."""

def get_connection():
    """
    Connessione al mongo db, e inizializzazione delle variabili globali client e connesion.

    Returns : 
    - connection : connessione al mongo db.
    """
    global client
    global connection
    if client is None and connection is None:
        client = MongoClient('localhost', 27017)
        connection = client['emealio_food_db']
    return connection