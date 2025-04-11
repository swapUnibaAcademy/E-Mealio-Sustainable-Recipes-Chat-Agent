import jsonpickle

class UserHistory:
    def __init__(self, userId, recipeId, recipe, date, status):
        """
        userId: the id of the user. Mandatory.
        recipe: the recipe that the user has to prepare. Mandatory.
        date: the date in which the user has to prepare the recipe. Mandatory.
        status: the status of the recipe in relation to the user (accepted, declined, temporary_declined). Mandatory.
        """
        self.userId = userId
        self.recipeId = recipeId
        self.recipe = recipe
        self.date = date
        self.status = status
    
    #populate fields from a json
    def from_json(self, jsonString):
        #convert the string to a json object
        json_obj = jsonpickle.decode(jsonString)
        self.userId = json_obj.userId
        self.recipeId = json_obj.recipeId
        self.recipe = json_obj.recipe
        self.date = json_obj.date
        self.status = json_obj.status
        return self
    
    def to_json(self):
        return jsonpickle.encode(self)
    
    def to_plain_json(self):
        return jsonpickle.encode(self, unpicklable=False)