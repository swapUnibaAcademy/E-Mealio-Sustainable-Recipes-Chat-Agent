import persistence.MongoConnectionManager as mongo
import jsonpickle

db = mongo.get_connection()
"""Connessione al mongo db."""

collection = db['logs']
"""Collection dei log nel db : logs"""

def save_log(logJson):
    """
    Salva il log in input nella collezione logs del mongo db.

    Args : 
    - logJson : log da salvare nel db.
    """
    log = jsonpickle.decode(logJson).__dict__
    collection.insert_one(log)