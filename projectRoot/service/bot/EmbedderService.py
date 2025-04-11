from sentence_transformers import SentenceTransformer
import numpy as np

# Global variable to store the model
sentence_transformer_model = None

def get_sentence_transformer_model():
    global sentence_transformer_model
    if sentence_transformer_model is None:
        sentence_transformer_model = SentenceTransformer('Alibaba-NLP/gte-large-en-v1.5', trust_remote_code=True)
    return sentence_transformer_model

def embed_list(listOfSentences, removeBrackets = True):
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

def embed_sentence(sentence):
    model = get_sentence_transformer_model()
    return model.encode(sentence)