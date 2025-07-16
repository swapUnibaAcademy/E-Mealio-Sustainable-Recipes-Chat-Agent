import jsonpickle

class User:

    """Rappresenta un utente che interagisce con il sistema."""

    def __init__(self, username, id, name, surname, dateOfBirth, nation, language, allergies, restrictions, disliked_ingredients, evolving_diet, reminder, days_reminder, hour_reminder, lastInteraction, tastes):
        """
        Inizializza un oggetto istanza della classe User.

        Args:
        - username: Username dell'utente.
        - id: Identificatore univoco dell'utente.
        - name: Nome dell'utente.
        - surname: Cognome dell'utente.
        - dateOfBirth: Data di nascita dell'utente, nel formato DD/MM/YYYY.
        - nation: Nazione in cui vive l'utente.
         - language : lingua con cui l'utente vuole interagire con il bot.
        - allergies: Lista di allergie dell'utente.
        - restrictions: Lista di restrizioni alimentari derivate da scelte etiche o credenze religigiose. I vincoli possibili sono ["vegan", "vegetarian", "islam", "hinduism", "ebraic"].
        - disliked_ingredients : ingredienti non piacciono all'utente.
        - evolving_diet : eventuale dieta futura dell'utente.
        - reminder: Valore booleano che indica se l'utente vuole ricevere promemoria.
        - day_reminder : numero di giorni di inattività dopo i quali l'utente vuole ricevere il reminder.
        - hour_reminder : ora in cui, passati i giorni di inattività, l'utente vuole ricevere il reminder.
        - lastInteraction: Ultima volta che l'utente ha interagito con il sistema.
        - tastes: Dizione contenente i gusti dell'utente per ogni tipologia di pasto.
        """
        self.username = username
        self.id = str(id)
        self.name = name
        self.surname = surname
        self.dateOfBirth = dateOfBirth
        self.nation = nation
        self.language = language
        self.allergies = allergies
        self.restrictions = restrictions
        self.disliked_ingredients = disliked_ingredients
        self.evolving_diet = evolving_diet
        self.reminder = reminder
        self.days_reminder = days_reminder
        self.hour_reminder = hour_reminder
        self.lastInteraction = lastInteraction
        self.tastes = tastes

    def from_json(self, jsonString):
        """
        Decodifica una stringa JSON e popola l'istanza corrente di User.
        I campi reminder, lastInteraction, tastes potrebbero non essere presenti, in quanto opzionali.
        I campi username e id sono presenti solo quando si sta costruendo l'utente a partire dal db.

        Args:
        - jsonString (str): Una stringa JSON che rappresenta un oggetto User.

        Returns:
        - User: L'istanza stessa, con i campi popolati a partire dall stringa JSON.
        """
        json_obj = jsonpickle.decode(jsonString)
        self.name = json_obj['name']
        self.surname = json_obj['surname']
        self.dateOfBirth = json_obj['dateOfBirth']
        self.nation = json_obj['nation']
        if('language' in json_obj):
            self.language = json_obj['language']
        self.allergies = json_obj['allergies']
        self.restrictions = json_obj['restrictions']
        self.disliked_ingredients = json_obj['disliked_ingredients']
        self.evolving_diet = json_obj['evolving_diet']
        if('reminder' in json_obj):
            self.reminder = json_obj['reminder']
        if('days_reminder' in json_obj):
            self.days_reminder = json_obj['days_reminder']
        if('hour_reminder' in json_obj):
            self.hour_reminder = json_obj['hour_reminder']
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
        """
        Decodifica una stringa JSON e popola l'istanza corrente di User solo con i campi presenti.

        Args:
        - jsonString (str): Una stringa JSON che rappresenta un oggetto User..

        Returns:
        - User: L'istanza stessa, con i campi popolati a partire dall stringa JSON.
        """
        json_obj = jsonpickle.decode(jsonString)
        if('name' in json_obj):
            self.name = json_obj['name']
        if('surname' in json_obj):
            self.surname = json_obj['surname']
        if('dateOfBirth' in json_obj):
            self.dateOfBirth = json_obj['dateOfBirth']
        if('nation' in json_obj):
            self.nation = json_obj['nation']
        if('language' in json_obj):
            self.language = json_obj['language']
        if('allergies' in json_obj):
            self.allergies = json_obj['allergies']
        if('restrictions' in json_obj):
            self.restrictions = json_obj['restrictions']  
        if('disliked_ingredients' in json_obj):
            self.disliked_ingredients = json_obj['disliked_ingredients']
        if('evolving_diet' in json_obj):
            self.evolving_diet = json_obj['evolving_diet']
        if('reminder' in json_obj):
            self.reminder = json_obj['reminder']
        if('days_reminder' in json_obj):
            self.days_reminder = json_obj['days_reminder']
        if('hour_reminder' in json_obj):
            self.hour_reminder= json_obj['hour_reminder']
        if('lastInteraction' in json_obj):
            self.lastInteraction = json_obj['lastInteraction']
        if('tastes' in json_obj):
            self.tastes = json_obj['tastes']
        return self
    
    def to_json(self):
        """
        Codifica l'oggetto User in una stringa JSON.

        Returns:
        - str: La rappresentazione JSON dell'oggetto.
        """
        return jsonpickle.encode(self)
     
    def to_plain_json(self):
        """
        Codifica l'oggetto User in una stringa JSON senza metadati per la ricostruzione dell'oggetto.

        Returns:
        - str: La rappresentazione JSON dell'oggetto non pickable.
        """
        return jsonpickle.encode(self, unpicklable=False)