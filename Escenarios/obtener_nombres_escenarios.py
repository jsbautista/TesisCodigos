# -*- coding: utf-8 -*-
"""
Created on Fri Dec  4 16:34:32 2020

@author: estudiante
"""

import os

tamano = "Small"

directory_path = "../Escenarios/" + tamano

directory = os.fsencode(directory_path)
for file in os.listdir(directory):
    filename = os.fsdecode(file)
    if filename.endswith(".json"): 
        file_path = os.path.join(directory_path, filename)
        f = open('../Resultados/small_stages.csv','a')
                
        f.write('\n')
        f.write(file_path) 
        
        f.close()