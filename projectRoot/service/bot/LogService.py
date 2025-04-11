import dto.Log as log
import jsonpickle
import persistence.LogPersistence as logPersistence

def save_log(logContent, date, agent, userId, printLog=False):
    if(printLog):
        print(logContent)
    logObj = log.Log(logContent, date, agent, userId)
    logJson= jsonpickle.encode(logObj)
    logPersistence.save_log(logJson)