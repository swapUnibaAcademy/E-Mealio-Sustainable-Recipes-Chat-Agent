import jsonpickle

class Recipe:
    def __init__(self, name, id, ingredients, sustainabilityScore, instructions, description, removedConstraints, mealType):
        self.name = name
        self.id = id
        self.ingredients = ingredients
        self.sustainabilityScore = sustainabilityScore
        self.instructions = instructions
        self.description = description
        self.removedConstraints = removedConstraints
        self.mealType = mealType
        
    #populate fields from a json
    def from_json(self, jsonString):
        #convert the string to a json object
        json_obj = jsonpickle.decode(jsonString)
        self.name = json_obj.name
        self.id = json_obj.id
        self.ingredients = json_obj.ingredients
        self.sustainabilityScore = json_obj.sustainabilityScore
        self.instructions = json_obj.instructions
        self.description = json_obj.description
        self.removedConstraints = json_obj.removedConstraints
        self.mealType = json_obj.mealType
        return self
    
    def to_json(self):
        return jsonpickle.encode(self)