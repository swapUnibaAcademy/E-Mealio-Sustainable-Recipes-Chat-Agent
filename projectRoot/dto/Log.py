import jsonpickle

class Log:

    """Rappresenta un log."""

    def __init__(self, logContent, date, agent, userId):
        """
        Inizializza un oggetto istanza della classe Log.

        Args:
        - logContent : Il contenuto del log. Se non è una stringa, verrà serializzato in formato JSON.
        - date : Data in cui il log è stato generato.
        - agent : Agente che ha generato il log.
        - userId : Identificativo dell'utente associato al log.

        """
        if not isinstance(logContent, str):
            self.logContent = str(jsonpickle.encode(logContent))
        else:
            self.logContent = logContent
        self.date = date
        self.userId = userId
        self.agent = agent
    
    def from_json(self, jsonString):
        """
        Decodifica una stringa JSON e popola l'istanza corrente di Log.

        Args:
        - jsonString (str): Una stringa JSON che rappresenta un oggetto Log.

        Returns:
        - Log: L'istanza stessa, con i campi popolati.
        """
        json_obj = jsonpickle.decode(jsonString)
        self.logContent = json_obj.logContent
        self.date = json_obj.date
        self.agent = json_obj.agent
        self.userId = json_obj.userId
        return self
    
    def to_json(self):
        """
        Codifica l'oggetto Log in una stringa JSON.

        Returns:
        - str: La rappresentazione JSON dell'oggetto.
        """
        return jsonpickle.encode(self)