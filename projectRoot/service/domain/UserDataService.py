# This file is used to get user data from the database
import dto.User as user
import persistence.UserPersistence as userDB
import jsonpickle


def getUserData(userId):
    """
    Recupera dalla collectione degli utenti del db l'utente con dato userId.

    Args : 
    - userId : id dell'utente da recuperare dal db.

    Returns : 
    - User : se esiste un utente con lo user id dato viene restituito l'utente corrispondente.
    """
    if(userId == None):
        print("User data is empty")
        return None
    else:
        userDbData = userDB.get_user_by_user_id(str(userId))
        if(userDbData == None):
            return None
        userJson = jsonpickle.encode(userDbData)
        userData = user.User(None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None)
        userData.from_json(userJson)
        return userData
    
def save_user(userData):
    """
    Salva l'utente nella collection degli utenti del db.

    Args : 
    - userData : utente da salvare nella collection degli utenti del db.
    """
    userDB.save_user(userData.to_plain_json())

def update_user(userData):
    """
    Aggiorna l'utente nella collection degli utenti del db.

    Args : 
    - userData : utente da aggiornare nella collection degli utenti del db.
    """
    userDB.update_user(userData.to_plain_json())

def update_user_last_interaction(userId, lastInteraction):
    """
    Aggiorna l'ultima interazione dell'utente con dato userId nella collection degli utenti nel db.

    Args : 
    - userId : id dell'utente di cui aggiornare l'ultima interazione.
    - lastInteraction : ultima interazione dell'utente avvenuta con il sistema.
    """
    userData = getUserData(userId)
    if(userData != None):
        userData.lastInteraction = lastInteraction
        update_user(userData)

def get_all_users_with_reminder():
    """
    Restituisce l'insieme degli utenti che hanno il promemoria attivo (reminder=True) dalla collection degli utenti nel db.

    Returns : 
    - users : utenti della collection degli utenti del db che hanno il promemoria attivo.
    """
    return userDB.get_all_users_with_reminder()

def get_language_from_json(DataJson):
    """
    Estrae da una stringa JSON la lingua con cui l'utente con dato userId vuole interagire con il chatbot.

    Args : 
    - DataJson : stringa JSON da cui estarre le informazioni

    Returns :
    - language : lingua con cui l'utente con dato userId vuole interagire con il chatbot estratta dalla data stringa JSON.
    """
    info = jsonpickle.decode(DataJson)
    language = info['language']

    return language

def get_taste(userId, mealType):
    """
    Restituisce il gusto dell'utente con dato userId di una specifica tipologia di pasto mealType.

    Args : 
    - userId : id dell'utente di cui recuperare il gusto.
    - mealType : tipologia di pasto di cui recuperare il gusto dell'utente.

    Returns :
    - taste : gusto dell'utente con dato userId della data specifica tipologia di pasto.
    """
    userDbData = userDB.get_user_by_user_id(str(userId))
    if(userDbData == None):
        return None
    else:
        return userDbData['tastes'][mealType]
    
def get_allergies(userId):
    """
    Restituisce la lista di allergie, sotto forma di stringhe, dell'utente con dato userId.

    Args : 
    - userId : id dell'utente di cui recuperare le allergie.

    Returns :
    - allergies : lista di allergie dell'utente con dato userId.
    """
    userDbData = userDB.get_user_by_user_id(str(userId))
    if(userDbData == None):
        return None
    else:
        return userDbData['allergies']
    
def get_restrictions(userId):
    """
    Restituisce la lista di restrizioni alimentari, sotto forma di stringhe, dell'utente con dato userId.

    Args : 
    - userId : id dell'utente di cui recuperare le restrizioni alimentari.

    Returns :
    - restrictions : lista di restrizioni alimentari dell'utente con dato userId.
    """
    userDbData = userDB.get_user_by_user_id(str(userId))
    if(userDbData == None):
        return None
    else:
        return userDbData['restrictions']
    
def get_disliked_ingredients(userId):
    """
    Restituisce la lista degli ingredienti, sotto forma di stringhe, che non piacciano all'utente con dato userId.

    Args : 
    - userId : id dell'utente di cui recuperare la lista degli ingredienti non piacuti.

    Returns :
    - disliked_ingredients : lista di ingredienti che non piacciono all'utente con dato userId.
    """

    userDbData = userDB.get_user_by_user_id(str(userId))
    if(userDbData == None):
        return None
    else:
        return userDbData['disliked_ingredients']
    
def get_evolving_diet(userId):
    """
    Restituisce la lista di eventuali future restrizioni alimentari, sotto forma di stringhe, dell'utente con dato userId.

    Args : 
    - userId : id dell'utente di cui recuperare le eventuali future restrizioni alimentari.

    Returns :
    - evolving_diet : lista di eventuali future restrizioni alimentari dell'utente con dato userId.
    """
    userDbData = userDB.get_user_by_user_id(str(userId))
    if(userDbData == None):
        return None
    else:
        return userDbData['evolving_diet']

def get_reminder_info(DataJson):
    """
    Estrae da una stringa JSON il numero di giorni e l'ora (da usare per il reminder).

    Args : 
    - DataJson : stringa JSON da cui estrarre le informazioni contenute.

    Returns : 
    - day, hour : informazioni codificate nella stringa JSON.
    """

    info = jsonpickle.decode(DataJson)
    day = info['days_reminder']
    hour = info['hour_reminder']
    
    return day, hour

def get_num_days_reminder(userId):
    """
    Restituisce il numero di giorni dopo i quali l'utente vuole ricevere il reminder dell'utente con dato userId.
    Se l'informazioni non è presente, vengono restituiti di default 2 giorni.

    Args : 
    - userId : id dell'utente di cui recuperare il numero di giorni dopo i quali l'utente vuole ricevere il reminder.

    Returns :
    - days_reminder : numero di giorni dopo i quali l'utente con dato userId vuole ricevere il reminder.
    """
    userDbData = userDB.get_user_by_user_id(str(userId))
    if(userDbData == None):
        return None
    # per gestire il caso in cui c'erano utenti già con il reminder attivato prima della creazione della personalizzazione
    elif 'days_reminder' not in userDbData:
        return userDbData.get('days_reminder', 2)
    else:
        return userDbData['days_reminder']
    
def get_hour_reminder(userId):
    """
    Restituisce l'ora alla quale dopo che sono scaduti il numero di giorni dopo i quali l'utente vuole ricevere il reminder dell'utente con dato userId.
    Se l'informazioni non è presente, viene restituito di default le 12.

    Args : 
    - userId : id dell'utente di cui recuperare l'ora alla quale dopo che sono scaduti il numero di giorni dopo i quali l'utente vuole ricevere il reminder.

    Returns :
    - hour_reminder : ora alla quale dopo che sono scaduti il numero di giorni dopo i quali l'utente con dato userId vuole ricevere il reminder.
    """
    userDbData = userDB.get_user_by_user_id(str(userId))
    if(userDbData == None):
        return None
    # per gestire il caso in cui c'erano utenti già con il reminder attivato prima della creazione della personalizzazione
    elif 'hour_reminder' not in userDbData:
        return userDbData.get('hour_reminder', 12)
    # nel caso l'utente inserisce ad es. 19:00
    elif isinstance(userDbData['hour_reminder'], str):
        return userDbData['hour_reminder'].split(":")[0]  
    else:
        return userDbData['hour_reminder']
    


