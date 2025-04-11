import persistence.MongoConnectionManager as mongo
import jsonpickle

db = mongo.get_connection()
collection = db['logs']

def save_log(logJson):
    log = jsonpickle.decode(logJson).__dict__
    collection.insert_one(log)