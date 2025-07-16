import jsonpickle

class Ingredient:
    
    """Rappresenta un ingrediente alimentare utilizzato all'interno delle ricette."""

    def __init__(self, name, cfp, wfp):
        """
        Inizializza un oggetto istanza della classe Ingredient.

        Args:
        - name : Nome dell'ingrediente.
        - cfp : Carbon Footprint dell'ingrediente.
        - wfp : Water Footprint dell'ingrediente.
        """
        self.name = name
        self.cfp = cfp
        self.wfp = wfp

    def from_json(self, jsonString):
        """
        Decodifica una stringa JSON e popola l'istanza corrente di Ingredient.

        Args:
        - jsonString (str): Una stringa JSON che rappresenta un oggetto Ingredient.

        Returns:
        - Ingredient: L'istanza stessa, con i campi popolati.
        """
        json_obj = jsonpickle.decode(jsonString)
        self.name = json_obj.name
        self.cfp = json_obj.cfp
        self.wfp = json_obj.wfp
        return self
    
    def to_json(self):
        """
        Codifica l'oggetto Ingredient in una stringa JSON.

        Returns:
        - str: La rappresentazione JSON dell'oggetto.
        """
        return jsonpickle.encode(self)