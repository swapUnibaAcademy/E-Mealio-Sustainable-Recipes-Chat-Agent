import jsonpickle

class Ingredient:
    def __init__(self, name, cfp, wfp):
        self.name = name
        self.cfp = cfp
        self.wfp = wfp
    
    #populate fields from a json
    def from_json(self, jsonString):
        #convert the string to a json object
        json_obj = jsonpickle.decode(jsonString)
        self.name = json_obj.name
        self.cfp = json_obj.cfp
        self.wfp = json_obj.wfp
        return self
    
    def to_json(self):
        return jsonpickle.encode(self)