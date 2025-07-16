class Response:

    """Rappresenta una risposta dal modello LLM."""

    def __init__(self, answer, action, info, memory, modifiedPrompt):
        """
        Inizializza un oggetto istanza della classe Response.
    
        Args:
        - answer: contiene la stringa effettiva della risposta che l'utente leggerà. Se nulla vuol dire che l'output prodotto sarò ridirezionato verso una diversa fase dell'agente.
        - action: contiene il token che viene usato per gestire il comportamento dell'agente.
        - info: informazioni aggiuntive usate nelle diverse fasi dell'agente.
        - memory: memoria della cronologia della conversazione con l'utente.
        - modifiedPrompt: prompt eventualmente modificato usato per generare la risposta.
        """
        self.answer = answer
        self.action = action
        self.info = info
        self.memory = memory
        self.modifiedPrompt = modifiedPrompt