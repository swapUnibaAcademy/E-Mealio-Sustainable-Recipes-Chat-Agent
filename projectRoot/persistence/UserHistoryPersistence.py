import jsonpickle
import persistence.MongoConnectionManager as mongo

db = mongo.get_connection()
collection = db['users_food_history']

def save_user_history(userHistoryJson):
    userHistory = jsonpickle.decode(userHistoryJson)
    collection.insert_one(userHistory)

def get_user_history(userId):
    #get the user history of the week, given that the status is accepted
    fullUserHistory = collection.find({"userId": userId})
    return fullUserHistory

def clean_temporary_declined_suggestions(userId):
    #clean the temporary declined suggestions
    collection.delete_many({"userId": userId, "status": "temporary_declined"})

def delete_user_history(userId):
    collection.delete_many({"userId": userId})