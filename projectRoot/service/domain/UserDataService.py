# This file is used to get user data from the database
import dto.User as user
import persistence.UserPersistence as userDB
import jsonpickle
def getUserData(userId):
    if(userId == None):
        print("User data is empty")
        return None
    else:
        userDbData = userDB.get_user_by_user_id(str(userId))
        if(userDbData == None):
            return None
        userJson = jsonpickle.encode(userDbData)
        userData = user.User(None,None,None,None,None,None,None,None,None,None,None)
        userData.from_json(userJson)
        return userData
    
def save_user(userData):
    userDB.save_user(userData.to_plain_json())

def update_user(userData):
    userDB.update_user(userData.to_plain_json())

def update_user_last_interaction(userId, lastInteraction):
    userData = getUserData(userId)
    if(userData != None):
        userData.lastInteraction = lastInteraction
        update_user(userData)

def get_all_users_with_reminder():
    return userDB.get_all_users_with_reminder()

def get_taste(userId, mealType):
    userDbData = userDB.get_user_by_user_id(str(userId))
    if(userDbData == None):
        return None
    else:
        return userDbData['tastes'][mealType]