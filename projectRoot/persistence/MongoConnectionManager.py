from pymongo import MongoClient

client = None
connection = None

def get_connection():
    global client
    global connection
    if client is None and connection is None:
        client = MongoClient('localhost', 27017)
        connection = client['emealio_food_db']
    return connection