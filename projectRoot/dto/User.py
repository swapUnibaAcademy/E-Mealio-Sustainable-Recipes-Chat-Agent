import jsonpickle

class User:
    def __init__(self, username, id, name, surname, dateOfBirth, nation, allergies, restrictions, reminder, lastInteraction, tastes):
        """
        username: the username of the user. Mandatory.
        id: the id of the user. Mandatory.
        name: the name of the user. Mandatory.
        surname: the surname of the user. Mandatory.
        dateOfBirth: the date of birth of the user in the format DD/MM/YYYY. Mandatory.
        nation: the nation of the user. Mandatory.
        allergies: a list of food that the user cannot eat. Optional.
        restrictions: a list of alimentary restrictions derived by ethics choices or religious beliefs. The possible constraints are ["vegan", "vegetarian", "islam", "hinduism", "ebraic"]. Optional.
        reminder: a boolean value that indicates if the user wants to receive reminders. Optional.
        lastInteraction: the last time the user interacted with the chatbot. Mandatory.
        tastes: a dictionary that contains the tastes of the user for each meal type. Mandatory.
        """
        self.username = username
        self.id = str(id)
        self.name = name
        self.surname = surname
        self.dateOfBirth = dateOfBirth
        self.nation = nation
        self.allergies = allergies
        self.restrictions = restrictions
        self.reminder = reminder
        self.lastInteraction = lastInteraction
        self.tastes = tastes

    #populate fields from a json
    def from_json(self, jsonString):
        #convert the string to a json object
        json_obj = jsonpickle.decode(jsonString)
        self.name = json_obj['name']
        self.surname = json_obj['surname']
        self.dateOfBirth = json_obj['dateOfBirth']
        self.nation = json_obj['nation']
        self.allergies = json_obj['allergies']
        self.restrictions = json_obj['restrictions']
        if('reminder' in json_obj):
            self.reminder = json_obj['reminder']
        if('lastInteraction' in json_obj):
            self.lastInteraction = json_obj['lastInteraction']
        if('tastes' in json_obj):
            self.tastes = json_obj['tastes']
        #those fields are loaded only when bulding a user object from the database
        if('username' in json_obj):
            self.username = json_obj['username']
        if('id' in json_obj):
            self.id = json_obj['id']
        
        return self
    
    def update_from_json(self, jsonString):
        #convert the string to a json object
        json_obj = jsonpickle.decode(jsonString)
        if('name' in json_obj):
            self.name = json_obj['name']
        if('surname' in json_obj):
            self.surname = json_obj['surname']
        if('dateOfBirth' in json_obj):
            self.dateOfBirth = json_obj['dateOfBirth']
        if('nation' in json_obj):
            self.nation = json_obj['nation']
        if('allergies' in json_obj):
            self.allergies = json_obj['allergies']
        if('restrictions' in json_obj):
            self.restrictions = json_obj['restrictions']  
        if('reminder' in json_obj):
            self.reminder = json_obj['reminder']
        if('lastInteraction' in json_obj):
            self.lastInteraction = json_obj['lastInteraction']
        if('tastes' in json_obj):
            self.tastes = json_obj['tastes']
        return self
    
    def to_json(self):
        return jsonpickle.encode(self)
    
    def to_plain_json(self):
        return jsonpickle.encode(self, unpicklable=False)