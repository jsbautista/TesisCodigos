# -*- coding: utf-8 -*-
"""
Created on Wed Dec  2 19:30:12 2020

@author: Sebastian
"""


import json 
import numpy as np
import math
import os, os.path

def generadorJsonsReales(path):
    
    with open(path) as myfile:
        data=myfile.read()
    
    # parse file
    problema = json.loads(data)
    
    calendarios = []
    idCale = []
    
    diaRef = int(problema['DateStartSolution'].split('T')[0].split('-')[2])
    horaRef = int(problema['DateStartSolution'].split('T')[1].split(':')[0])
    mesRef = int(problema['DateStartSolution'].split('T')[0].split('-')[1])
    
    numEmpleados = len(problema['WorkCenters'])
    numOrdenes = len(problema['Tasks'])
    numDiasOperacion = 7
    numHorasDiaLaboral = 24
    
    for i in problema['ServiceCalendars']:
        if i['Id'] not in idCale:
            idCale.append(i['Id'])
            calen = np.zeros((numDiasOperacion,numHorasDiaLaboral))
            for j in i['Availability']:
                a = int(j['StartTime'].split(':')[0])
                b = int(j['EndTime'].split(':')[0])
                c = b-a 
                for z in range(c):    
                    calen[j['WeekDay']-1][a+z] = 1
            calendarios.append(calen)
    prioridadOrdenes = np.zeros(numOrdenes)
    salarioEmpleados = np.zeros(numEmpleados)
    
    numHabilidades = 0
    
    for i in problema['WorkCenters']:
        var  = len(i['Skills'])
        if var > numHabilidades:
            numHabilidades = var
    
    for i in problema['Tasks']:
        var  = len(i['Skills'])
        if var > numHabilidades:
            numHabilidades = var
    
    
    habilidadesOperarios = np.zeros((numEmpleados, numHabilidades))
    habilidadesOrdenes = np.zeros((numOrdenes, numHabilidades))
    dispOperarios = np.zeros((numEmpleados, numDiasOperacion, numHorasDiaLaboral))
    x = problema['WorkCenters']
    for i in range(len(x)):
        salarioEmpleados[i] = x[i]['Cost']
        for k in x[i]['Skills']:
            habilidadesOperarios[i][k-1] = 1
        for j in x[i]['Availability']:
            a = int(j['StartTime'].split(':')[0])
            b = int(j['EndTime'].split(':')[0])
            c = b-a 
            for z in range(c):
                dispOperarios[i,j['WeekDay']-1,a+z] = 1
        f = x[i]['Tasks']
        for z in range(len(f)):
            d = int(f[z]['DateAttentionLimit'].split('T')[0].split('-')[2])
            h = int(f[z]['DateAttentionLimit'].split('T')[1].split(':')[0])
            m = int(f[z]['DateAttentionLimit'].split('T')[0].split('-')[1])
            c = d - diaRef
            if m == mesRef and c >= 0 and c < 8:
                dispOperarios[i,c,h] = 0
    
    print(dispOperarios)
    
    dispOrdenes = np.zeros((numOrdenes, numDiasOperacion, numHorasDiaLaboral))
    y= problema['Tasks']
    for i in range(len(y)):
        for s in y[i]['Skills']:
            habilidadesOrdenes[i][s-1] = 1
        if y[i]['IsPriority']:
            prioridadOrdenes[i] = 10
        if y[i]['CalendarId'] in idCale:
            index = idCale.index(y[i]['CalendarId'])
            calendario = calendarios[index]
            for z in range(numDiasOperacion):
                for k in range(numHorasDiaLaboral):
                    dispOrdenes[i,z,k] = calendario[z,k]
                    
    costosANS = np.zeros((numOrdenes, numDiasOperacion, numHorasDiaLaboral))     
    for i in range(len(y)):
        d = int(y[i]['DateAttentionLimit'].split('T')[0].split('-')[2])
        h = int(y[i]['DateAttentionLimit'].split('T')[1].split(':')[0])
        m = int(y[i]['DateAttentionLimit'].split('T')[0].split('-')[1])        
        c = d - diaRef
        if m == mesRef and c >= 0 and c < 8:
            for j in range(numDiasOperacion):
                for k in range(numHorasDiaLaboral):
                    if j <= c and h > k:
                        costosANS[i,j,k] = y[i]['TimeOutSLA']
                    if j < c:
                        costosANS[i,j,k] = y[i]['TimeOutSLA']
            
    
    numLugares = numOrdenes +1
    coordenadasLugares = []
    coordenadaLugar = {"latitud": "", "longitud": ""}
    coordenadaLugar["latitud"] = 4.6919
    coordenadaLugar["longitud"] = -74.074
    coordenadasLugares.append(coordenadaLugar)
    
    
    for i in range(len(y)):
            coordenadaLugar = {"latitud": "", "longitud": ""}
            coordenadaLugar["latitud"] = y[i]['Latitude']
            coordenadaLugar["longitud"] = y[i]['Longitude']
            coordenadasLugares.append(coordenadaLugar)
    
    distanciasOrdenes = np.zeros((numLugares, numLugares))
    for i in range(numLugares):
        for j in range(i+1, numLugares):
            if i != j:
                distanciaGenerada = abs(coordenadasLugares[i]["latitud"] - coordenadasLugares[j]["latitud"]) + abs(coordenadasLugares[i]["longitud"] - coordenadasLugares[j]["longitud"])
                distanciasOrdenes[i,j] = distanciaGenerada
                distanciasOrdenes[j,i] = distanciaGenerada
                
    porcentajeCumplimientoHabilidades = problema['Restrictions']['MinSkillQuantity'] / numHabilidades
    
    data = {"numEmpleados": numEmpleados,
            "numOrdenes": numOrdenes,
            "numDiasOperacion": numDiasOperacion,
            "numHorasDiaLaboral": numHorasDiaLaboral,
            "numHabilidades": numHabilidades,
            "numLugares": numLugares,
            "disponibilidadOperarios": dispOperarios.tolist(),
            "disponibilidadOrdenes": dispOrdenes.tolist(),
            "costosANS": costosANS.tolist(),
            "prioridad": prioridadOrdenes.tolist(),
            "salario": salarioEmpleados.tolist(),
            "habilidadesOperarios": habilidadesOperarios.tolist(),
            "habilidadesOrdenes": habilidadesOrdenes.tolist(),
            "porcentajeCumplimientoHabilidades": porcentajeCumplimientoHabilidades,
            "coordenadas": coordenadasLugares,
            "distanciasOrdenes": distanciasOrdenes.tolist()}
    
    category = 'DatosReales'
    currentDirectory = os.getcwd()
    currentDirectory2 = os.path.join(currentDirectory, 'resultados')
    
    currentLength = len([name for name in os.listdir(currentDirectory2) if os.path.isfile(os.path.join(currentDirectory2, name))])
    
    with open( 'resultados' + '/' +  str(currentLength + 1) + category[0] +  "_" + "E" + str(numEmpleados) + "O" + str(numOrdenes) + "D" + str(numDiasOperacion) + "H" + str(numHorasDiaLaboral) + "S" + str(numHabilidades) + '.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    f.close()


for file in os.listdir(os.getcwd()):
    filename = os.fsdecode(file)
    if filename.endswith(".json"): 
        generadorJsonsReales(filename)