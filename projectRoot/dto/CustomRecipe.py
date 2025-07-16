import jsonpickle

class CustomRecipe:

    """Rappresenta una ricetta personalizzata costruita dall'utente."""

    def __init__(self, name, ingredients, quantities, mealType, serving, calories, totalFat, saturatedFat, totalCarbohydrate, protein, sugars, dietaryFiber, cholesterol, sodium, sustainabilityScore, who_score):
        """
        Inizializza un oggetto istanza della classe CustomRecipe.

        Args:
        - name : Nome della ricetta.
        - ingredients : Elenco degli ingredienti utilizzati nella ricetta.
        - quantities : Elenco delle corrispondeti quantità degli ingredienti utilizzati nella ricetta.
        - mealType : Tipo di pasto (ad esempio, ”Cena”, ”Pranzo”).
        - serving : quantità totale in grammi della ricetta.
        - calories : calorie, espresse in kcal, della ricetta.
        - totalFat : grammi totali di grassi della ricetta.
        - saturatedFat : grammi di grassi saturi della ricetta.
        - totalCarbohydrate : grammi di carboidrati della ricetta.
        - protein : grammi di proteine della ricetta.
        - sugars : grammi di zucchero della ricetta.
        - dietaryFiber : grammi di fibre della ricetta.
        - cholesterol : milligrammi di colesterolo della ricetta.
        - sodium : milligrammi di sodio della ricetta.
        - sustainabilityScore : Punteggio di sostenibilità della ricetta.
        - who_score : Punteggio di salubrità della ricetta secondo le linee guida WHO
        """
        
        self.name = name
        self.ingredients = ingredients
        self.quantities = quantities
        self.mealType = mealType
        self.serving = serving
        self.calories  = calories
        self.totalFat  = totalFat
        self.saturatedFat  = saturatedFat
        self.totalCarbohydrate  = totalCarbohydrate
        self.protein  = protein
        self.sugars  = sugars
        self.dietaryFiber  = dietaryFiber
        self.cholesterol  = cholesterol
        self.sodium  = sodium
        self.sustainabilityScore = sustainabilityScore
        self.who_score = who_score

    def from_json(self, jsonString):
        """
        Decodifica una stringa JSON e popola l'istanza corrente di CustomRecipe.

        Args:
        - jsonString (str): Una stringa JSON che rappresenta un oggetto CustomRecipe.

        Returns:
        - CustomRecipe: L'istanza stessa, con i campi popolati a partire dall stringa JSON.
        """
        json_obj = jsonpickle.decode(jsonString)
        
        self.name = json_obj.name
        self.ingredients = json_obj.ingredients
        self.quantities = json_obj.quantities
        self.mealType = json_obj.mealType
        if('serving' in json_obj):
            self.serving = json_obj['serving']
        if('calories' in json_obj):
            self.calories = json_obj['calories']
        if('totalFat' in json_obj):
            self.totalFat = json_obj['totalFat']
        if('saturatedFat' in json_obj):
            self.saturatedFat = json_obj['saturatedFat']
        if('totalCarbohydrate' in json_obj):
            self.totalCarbohydrate = json_obj['totalCarbohydrate']
        if('protein' in json_obj):
            self.protein = json_obj['protein']
        if('sugars' in json_obj):
            self.sugars = json_obj['sugars']
        if('dietaryFiber' in json_obj):
            self.dietaryFiber = json_obj['dietaryFiber']
        if('cholesterol' in json_obj):
            self.cholesterol = json_obj['cholesterol']
        if('sodium' in json_obj):
            self.sodium = json_obj['sodium']
        if('sustainabilityScore' in json_obj):
            self.sustainabilityScore = json_obj['sustainabilityScore']
        if('who_score' in json_obj):
            self.who_score = json_obj['who_score']
        return self
    
    def to_json(self):
        """
        Codifica l'oggetto CustomRecipe in una stringa JSON.

        Returns:
        - str: La rappresentazione JSON dell'oggetto.
        """
        return jsonpickle.encode(self)