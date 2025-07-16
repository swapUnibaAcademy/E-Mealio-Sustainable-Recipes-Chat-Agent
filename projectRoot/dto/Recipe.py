import jsonpickle

class Recipe:

    """Rappresenta una ricetta già presente nel db."""

    def __init__(self, name, id, ingredients, sustainabilityScore, who_score, instructions, description, removedConstraints, mealType):
        """
        Inizializza un oggetto istanza della classe Recipe.

        Args:
        - name : Nome della ricetta.
        - id : Identificatore univoco della ricetta.
        - ingredients : Elenco degli ingredienti utilizzati nella ricetta.
        - sustainabilityScore : Punteggio di sostenibilità della ricetta.
        - who_score : Punteggio di salubrità della ricetta.
        - instructions : URL che rimanda alle istruzioni di preparazione della ricetta.
        - description : Descrizione testuale della ricetta.
        - removedConstraints: Elenco di vincoli che sono stati rimossi dalla query per estrarre la ricetta.
        - mealType : Tipo di pasto (ad esempio, ”Cena”, ”Pranzo”).
        """
        self.name = name
        self.id = id
        self.ingredients = ingredients
        self.sustainabilityScore = sustainabilityScore
        self.who_score = who_score
        self.instructions = instructions
        self.description = description
        self.removedConstraints = removedConstraints
        self.mealType = mealType
        
    def from_json(self, jsonString):
        """
        Decodifica una stringa JSON e popola l'istanza corrente di Recipe.

        Args:
        - jsonString (str): Una stringa JSON che rappresenta un oggetto Recipe.

        Returns:
        - Recipe: L'istanza stessa, con i campi popolati a partire dall stringa JSON.
        """
        json_obj = jsonpickle.decode(jsonString)
        self.name = json_obj.name
        self.id = json_obj.id
        self.ingredients = json_obj.ingredients
        self.sustainabilityScore = json_obj.sustainabilityScore
        self.who_score = json_obj.who_score
        self.instructions = json_obj.instructions
        self.description = json_obj.description
        self.removedConstraints = json_obj.removedConstraints
        self.mealType = json_obj.mealType
        return self
    
    def to_json(self):
        """
        Codifica l'oggetto Recipe in una stringa JSON.

        Returns:
        - str: La rappresentazione JSON dell'oggetto.
        """
        return jsonpickle.encode(self)