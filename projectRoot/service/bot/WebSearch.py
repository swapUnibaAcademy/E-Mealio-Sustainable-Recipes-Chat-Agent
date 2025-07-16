import os
import anthropic
import dto.Response as resp
import service.bot.LogService as log
import datetime
from dotenv import load_dotenv, find_dotenv


PRINT_LOG = False

# Anthropic disponibile solo con i modelli : 
# claude-3-7-sonnet-20250219, claude-3-5-sonnet-latest, claude-3-5-haiku-latest

# claude-3-7-sonnet-20250219
load_dotenv(find_dotenv())

MODEL = "claude-3-7-sonnet-latest" 
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def get_response_text(response):
    """
    Estrae dalla riposta generata dal modello a seguito della ricerca web la risposta tesuale completa.

    Args : 
    - response : risposta generata dal modello di Web Search, contenente varie informazioni oltre alla risposta testuale.

    Returns : 
    - response_text : risposta testuale generata dal modello di Web Search.
    """
    # estraiamo tutti i blocchi di testo
    text_block = [
        block.text
        for block in response.content
        if getattr(block, 'type', None) == 'text' and getattr(block, 'text', None) is not None
    ]

    # concateniamo tutti i blocchi per ottenere la risposta finale
    response_text = ''.join(text_block)
    return response_text

def get_citations_and_urls(response):
    """
    Estrae dalla risposta generata dal modello di Web Search le citazioni delle risorse web usate considerate nella ricerca, con i loro rispettivi url.
    
    Args : 
    - response : risposta generata dal modello di Web Search, contenente varie informazioni oltre alla risposta testuale.

    Returns : 
    - citations_and_urls : citazioni da fonti esterne all'intero della risposta testuale generata, con i rispettivi url.
    """

    citations_and_urls = []
    
    for block in getattr(response, "content", []):
        if block.type == "text" and hasattr(block, "text") and block.text:
            citations = getattr(block, "citations", None)
            if citations:
                for citation in citations:
                    url = getattr(citation, "url", None)
                    cit = {
                        "url": url,
                        "title": getattr(citation, "title", None),
                        "cited_text": getattr(citation, "cited_text", None)
                    }
                    citations_and_urls.append(cit)
                    
    return citations_and_urls

def web_search(input_prompt, input_query, temperature, userData, memory=None, memory_enabled=False):
       
    """
    Invoca il modello di web search con la domanda effettuata dall'utente e viene restituita la risposta testuale
    con le relative fonti estratte.

    Args:
    - input_prompt : prompt di input.
    - input_query : query di input da inviare al modello.
    - temperature : valore della temperatura del modello (creatività).
    - userData : dati dell'utente sta interagendo con il sistema.
    - memory : memoria della conversazione, se già inizializzata.
    - memory_enabled : flag booleano che se True inizializza la memoria se non è già fornita (di default False).

    Returns:
    - Response: oggetto istanza della classe Response contenente la risposta generata,
                strutturando il campo answer come dizionario per differenziare la risposta testuale dalle fonti estratte.
    """
        
    print("***************************************************************\nweb_search()")

    # input prompt  : prompt già costruito tramite WEB_SEARCH.format(concept=concep)
    # input_query : serve per aggiornare la memoria solo con la domanda dell'utente senza salvare tutto il prompt

    log.save_log(input_query, datetime.datetime.now(), "User", userData.id, PRINT_LOG)
    log.save_log(input_prompt, datetime.datetime.now(), "System: input_prompt", userData.id, PRINT_LOG)

    # Se messages non è fornito, inizializza una lista vuota
    if memory is None and memory_enabled:
        memory = []

    # aggiungiamo la richiesta dell'utente alla memoria
    if memory_enabled:
        memory.append({"role": "user", "content": input_query})

    """
    print("\nMemory aggiornata:")
    for msg in memory:
        print(msg)
        print()
    """

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=input_prompt,
        messages=memory,
        temperature=temperature,
        tools=[{
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": 5
        }]
    )

    # estraiamo la risposta testuale e le citazioni con le rispettive fonti dalla risposta generata dal modello di Web Search
    clean_answer = get_response_text(response)
    citations_and_urls = get_citations_and_urls(response)

    # aggiungiamo la risposta del modello alla memoria
    if memory_enabled :
        memory.append({"role": "assistant", "content": clean_answer})

    """
    print("\nMemory :")
    for msg in memory:
        print(msg)
        print()
    """

    # mettiamo tutto in answer in modo da salvare tutto nella risposta finale
    answer = {
        'clean_answer': clean_answer,
        'citations_and_urls': citations_and_urls
    }

    # creiamo la risposta finale, oggetto istanza della classe Response
    final_response = resp.Response(answer, "", "", memory, '')

    log.save_log(final_response, datetime.datetime.now(), "Web Search", userData.id, PRINT_LOG)

    print("***************************************************************")

    return final_response
