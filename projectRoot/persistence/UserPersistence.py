import jsonpickle
import persistence.MongoConnectionManager as mongo

db = mongo.get_connection()
collection = db['users']

def get_all_users():
    users = collection.find()
    return users

def save_user(userJson):
    user = jsonpickle.decode(userJson)
    collection.insert_one(user)

def update_user(userJson):
    user = jsonpickle.decode(userJson)
    collection.update_one({"id":user['id']}, {"$set": user}, upsert=False)

def get_user_by_user_id(userId):
    user = collection.find_one({"id":userId})
    return user

def update_user_last_interaction(userId, lastInteraction):
    collection.update_one({"id":userId}, {"$set": {"lastInteraction": lastInteraction}}, upsert=False)

def update_user_tastes(userId, tastes):
    collection.update_one({"id":userId}, {"$set": {"tastes": tastes}}, upsert=False)

def delete_user_by_user_id(userId):
    collection.delete_one({"id":userId})

def get_all_users_with_reminder():
    users = collection.find({"reminder": True})
    return users