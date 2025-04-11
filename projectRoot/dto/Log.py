import jsonpickle

class Log:
    def __init__(self, logContent, date, agent, userId):
        #save logContent as a json string
        #if logContent is not a string
        if not isinstance(logContent, str):
            self.logContent = str(jsonpickle.encode(logContent))
        else:
            self.logContent = logContent
        self.date = date
        self.userId = userId
        self.agent = agent
    
    #populate fields from a json
    def from_json(self, jsonString):
        #convert the string to a json object
        json_obj = jsonpickle.decode(jsonString)
        self.logContent = json_obj.logContent
        self.date = json_obj.date
        self.agent = json_obj.agent
        self.userId = json_obj.userId
        return self
    
    def to_json(self):
        return jsonpickle.encode(self)