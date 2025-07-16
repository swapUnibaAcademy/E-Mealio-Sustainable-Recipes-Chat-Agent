import dto.Log as log
import jsonpickle
import persistence.LogPersistence as logPersistence

def save_log(logContent, date, agent, userId, printLog=False):
    """
    Salva il log nella collection dei logs nel db.

    Args : 
    - logContent : contentuto del log.
    - date : data corrente in cui è stato generato il log.
    - agent : agente che ha generato il log.
    - userId : utente che è coinvolto nell'azione del log.
    - printLog : flag booleano che indica se stampare a video il log (di default False)
    """
    if(printLog):
        print(logContent)
    logObj = log.Log(logContent, date, agent, userId)
    logJson= jsonpickle.encode(logObj)
    logPersistence.save_log(logJson)