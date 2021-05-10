import json
import math
from datetime import datetime
import numpy

def evaluarRespuesta(costoAns):

    stageFile = open("./pro1_response.json")
    stageData = json.load(stageFile)
    tasks = stageData[0]['Tasks']
    ordenes = len(stageData[0]['Tasks'])-1

    fo = ordenes


    for i in tasks:
        prioridad = 1
        if i['IsPriority']:
            prioridad += 0.1
        #Contar penalizaciones

        diaAtencion = datetime.strptime(i['DateStartAttention'][0:19],'%Y-%m-%dT%H:%M:%S')
        diaLimite = datetime.strptime(i['DateSolutionlimit'][0:19],'%Y-%m-%dT%H:%M:%S')
        deltaDias = (diaAtencion-diaLimite).days
        print(deltaDias)
        if deltaDias > 0:
            ordenes -= deltaDias * costoAns * prioridad
    print(ordenes)

evaluarRespuesta(0.05)

