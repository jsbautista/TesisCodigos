# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 11:56:40 2020

@author: Daniel
"""

import modelado_gurobi
#import modelado_gurobi_copia
import os

import CrearEscenario

tamano = "Small"

directory_path = "./" 

CrearEscenario.crearEscenario(2,33,1)

directory = os.fsencode(directory_path)
    
for file in os.listdir(directory):
    filename = os.fsdecode(file)
    if filename.endswith("ario.json"):
        print (filename)    
        file_path = os.path.join(directory_path, filename)
        
        execResults = modelado_gurobi.ejecutarModeloGurobi(file_path)
         
        execResults["Tamano"] = tamano
        execResults["Modelo"] = "Gurobi"
        execResults["Escenario"] = filename[:-5]
        
        resultsLine = str(execResults["Modelo"]) + "," + str(execResults["Escenario"]) + "," + \
                      str(execResults["FO_Global"]) + str(execResults["Tiempo"])
         

