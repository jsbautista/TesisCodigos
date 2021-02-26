# -*- coding: utf-8 -*-
"""
Created on Tue Nov 24 09:16:12 2020

@author: estudiante
"""

import Modelado_Pyomo
import os

tamano = "Small"

directory_path = "../Escenarios/" + tamano

directory = os.fsencode(directory_path)
for file in os.listdir(directory):
    filename = os.fsdecode(file)
    if filename.endswith(".json"): 
        file_path = os.path.join(directory_path, filename)
        execResults = Modelado_Pyomo.ejecutarModeloPyomo(file_path)
        
        execResults["Tamano"] = tamano
        execResults["Modelo"] = "Pyomo"
        execResults["Escenario"] = filename[:-5]
         
        f = open('../Resultados/resultados.csv','a')
        
        resultsLine = str(execResults["Tamano"]) + "," + str(execResults["Modelo"]) + "," + str(execResults["Escenario"]) + "," + str(execResults["FO_Global"]) + "," + str(execResults["FO_Ordenes"]) + "," + str(execResults["FO_Costo"]) + "," + str(execResults["FO_ANS"]) + "," + str(execResults["FO_Prioridad"]) + "," +  str(execResults["FO_Distancia"]) + "," + str(execResults["Tiempo"])
        
        f.write('\n')
        f.write(resultsLine) 
        f.close()