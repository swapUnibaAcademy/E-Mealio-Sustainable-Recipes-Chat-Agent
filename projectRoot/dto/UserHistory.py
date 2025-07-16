import jsonpickle

class UserHistory:

    """Rappresenta una cronologia alimentare di un utente."""

    def __init__(self, userId, recipeId, recipe, date, status):
        """
        Inizializza un oggetto istanza della classe UserHistory.

        Args:
        - userId: Id dell'utente.
        - recipe: La ricetta di cui l'utentedeve ha accettato il suggerimento.
        - date: La data in cui l'utente deve preparare la ricetta.
        - status: Lo stato della ricetta in relazione all'utente  (accepted, declined, temporary_declined)
        """
        self.userId = userId
        self.recipeId = recipeId
        self.recipe = recipe
        self.date = date
        self.status = status
    
    def from_json(self, jsonString):
        """
        Decodifica una stringa JSON e popola l'istanza corrente di UserHistory.

        Args:
        - jsonString (str): Una stringa JSON che rappresenta un oggetto UserHistory.

        Returns:
        - UserHistory: L'istanza stessa, con i campi popolati a partire dall stringa JSON.
        """
        json_obj = jsonpickle.decode(jsonString)
        self.userId = json_obj.userId
        self.recipeId = json_obj.recipeId
        self.recipe = json_obj.recipe
        self.date = json_obj.date
        self.status = json_obj.status
        return self
    
    def to_json(self):
        """
        Codifica l'oggetto UserHistory in una stringa JSON.

        Returns:
        - str: La rappresentazione JSON dell'oggetto.
        """
        return jsonpickle.encode(self)
    
    def to_plain_json(self):
        """
        Codifica l'oggetto UserHistory in una stringa JSON senza metadati per la ricostruzione dell'oggetto.

        Returns:
        - str: La rappresentazione JSON dell'oggetto non pickable.
        """
        return jsonpickle.encode(self, unpicklable=False)