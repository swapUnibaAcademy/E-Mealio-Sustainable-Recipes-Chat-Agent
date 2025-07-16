from sentence_transformers import SentenceTransformer
import numpy as np

sentence_transformer_model = None
"""Modello di embedding (Alibaba-NLP/gte-large-en-v1.5)"""

def get_sentence_transformer_model():
    """
    Restituisce un'istanza del modello SentenceTransformer di embedding.

    Se il modello non è già stato caricato, viene caricato una sola volta e memorizzato in una variabile globale, ovvero viene gestito come variabile singleton.

    Returns:
    - SentenceTransformer: il modello di embedding.
    """
    global sentence_transformer_model
    if sentence_transformer_model is None:
        sentence_transformer_model = SentenceTransformer('Alibaba-NLP/gte-large-en-v1.5', trust_remote_code=True)
    return sentence_transformer_model

def embed_sentence(sentence):
    """
    Genera l'embedding vettoriale di una singola frase.

    Args:
    - sentence : singola frase da convertire in embedding.

    Returns:
    - numpy.ndarray: array numpy rappresentate l'embedding della frase in input.
    """
    model = get_sentence_transformer_model()
    return model.encode(sentence)

def embed_list(listOfSentences, removeBrackets = True):
    """
    Converte una lista di frasi in un singolo embedding vettoriale sommando gli embeddings di ciascuna frase.

    Args:
    - listOfSentences : stringa contenente una lista di frasi separate da virgole, potenzialmente racchiusa tra parentesi.
    - removeBrackets : flag booleano che indica se rimuovere il primo e l'ultimo carattere della stringa per eliminare parentesi quadre o tonde (di default True).

    Returns:
    - numpy.ndarray: vettore numpy di dimensione 1024 che rappresenta la somma degli embeddings delle frasi.
    """
    model = get_sentence_transformer_model()
    #remove brackets from the list
    if removeBrackets:
        listOfSentences = listOfSentences[1:-1]
    #split the list by comma
    listOfSentences = listOfSentences.split(",")

    #empty array of 1024
    embedding = np.zeros(1024)

    #embed each sentence in the list
    for sentence in listOfSentences:
        #embed the sentence
        sentenceEmbedding = model.encode(sentence)
        #add the sentence embedding to the empty array
        embedding = np.add(embedding, sentenceEmbedding)
    return embedding

