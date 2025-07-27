from pymongo import MongoClient

import os
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
        mongo_host = os.getenv('MONGO_HOST', 'localhost')  # fallback to localhost
        mongo_port = int(os.getenv('MONGO_PORT', 27017))
        client = MongoClient(mongo_host, mongo_port)
        connection = client['emealio_food_db']
    return connection