# -*- coding: utf-8 -*-
"""
Created on Thu Nov 19 14:43:52 2020

@author: Daniel
"""
import os, os.path
import generador
import json
import random
import numpy as np

limites = {
    "Small": {
        "minNumEmpleados": 1,
        "maxNumEmpleados": 3,
        "minNumOrdenes": 1,
        "maxNumOrdenes": 3,
        "minNumDiasOperacion": 1,
        "maxNumDiasOperacion": 2,
        "minNumHorasDiaLaboral": 4,
        "maxNumHorasDiaLaboral": 8,
        "minNumHabilidades": 1,
        "maxNumHabilidades": 2,
        "minNumHorasDisponiblesPorEmpleado": 4,
        "maxNumHorasDisponiblesPorEmpleado": 8,
        "minNumHorasDisponiblesPorOrden": 4,
        "maxNumHorasDisponiblesPorOrden": 8,
        "minCostoMinimoANS": 2,
        "maxCostoMinimoANS": 5,
        "minCostoMaximoANS": 6,
        "maxCostoMaximoANS": 10,
        "minSalarioMinimoEmpleados": 5,
        "maxSalarioMinimoEmpleados": 10,
        "minSalarioMaximoEmpleados": 15,
        "maxSalarioMaximoEmpleados": 20,
    },
    "Medium": {
        "minNumEmpleados": 3,
        "maxNumEmpleados": 5,
        "minNumOrdenes": 3,
        "maxNumOrdenes": 5,
        "minNumDiasOperacion": 1,
        "maxNumDiasOperacion": 3,
        "minNumHorasDiaLaboral": 4,
        "maxNumHorasDiaLaboral": 8,
        "minNumHabilidades": 1,
        "maxNumHabilidades": 3,
        "minNumHorasDisponiblesPorEmpleado": 4,
        "maxNumHorasDisponiblesPorEmpleado": 8,
        "minNumHorasDisponiblesPorOrden": 4,
        "maxNumHorasDisponiblesPorOrden": 8,
        "minCostoMinimoANS": 2,
        "maxCostoMinimoANS": 5,
        "minCostoMaximoANS": 6,
        "maxCostoMaximoANS": 10,
        "minSalarioMinimoEmpleados": 5,
        "maxSalarioMinimoEmpleados": 10,
        "minSalarioMaximoEmpleados": 15,
        "maxSalarioMaximoEmpleados": 20,
    },
    "Large": {
        "minNumEmpleados": 5,
        "maxNumEmpleados": 7,
        "minNumOrdenes": 5,
        "maxNumOrdenes": 7,
        "minNumDiasOperacion": 1,
        "maxNumDiasOperacion": 5,
        "minNumHorasDiaLaboral": 4,
        "maxNumHorasDiaLaboral": 8,
        "minNumHabilidades": 1,
        "maxNumHabilidades": 3,
        "minNumHorasDisponiblesPorEmpleado": 4,
        "maxNumHorasDisponiblesPorEmpleado": 8,
        "minNumHorasDisponiblesPorOrden": 4,
        "maxNumHorasDisponiblesPorOrden": 8,
        "minCostoMinimoANS": 2,
        "maxCostoMinimoANS": 5,
        "minCostoMaximoANS": 6,
        "maxCostoMaximoANS": 10,
        "minSalarioMinimoEmpleados": 5,
        "maxSalarioMinimoEmpleados": 10,
        "minSalarioMaximoEmpleados": 15,
        "maxSalarioMaximoEmpleados": 20,
   }    
}

def generarEscenarios(category, amount):
    
    for i in range(amount):
    
        ### Parámetros de generación de datos
        
        numEmpleados = random.randint(limites[category]["minNumEmpleados"], limites[category]["maxNumEmpleados"])
        numOrdenes = random.randint(limites[category]["minNumOrdenes"], limites[category]["maxNumOrdenes"])
        numDiasOperacion = random.randint(limites[category]["minNumDiasOperacion"], limites[category]["maxNumDiasOperacion"])
        numHorasDiaLaboral = random.randint(limites[category]["minNumHorasDiaLaboral"], limites[category]["maxNumHorasDiaLaboral"])
        numHabilidades = random.randint(limites[category]["minNumHabilidades"], limites[category]["maxNumHabilidades"])
        
        numHorasDisponiblesPorEmpleado = min(numHorasDiaLaboral, random.randint(limites[category]["minNumHorasDisponiblesPorEmpleado"], limites[category]["maxNumHorasDisponiblesPorEmpleado"]))
        numHorasDisponiblesPorOrden = min(numHorasDiaLaboral, random.randint(limites[category]["minNumHorasDisponiblesPorOrden"], limites[category]["maxNumHorasDisponiblesPorOrden"]))
        
        costoMinimoANS = random.randint(limites[category]["minCostoMinimoANS"], limites[category]["maxCostoMinimoANS"])
        costoMaximoANS = random.randint(limites[category]["minCostoMaximoANS"], limites[category]["maxCostoMaximoANS"])
        umbralEleccionANS = random.random() / 2
        
        prioridadMinimaOrdenes = 1
        prioridadMaximaOrdenes = 5
        
        salarioMinimoEmpleados = random.randint(limites[category]["minSalarioMinimoEmpleados"], limites[category]["maxSalarioMinimoEmpleados"])
        salarioMaximoEmpleados = random.randint(limites[category]["minSalarioMaximoEmpleados"], limites[category]["maxSalarioMaximoEmpleados"])
        
        porcentajeCumplimientoHabilidades = random.random()
        
        numLugares = numOrdenes + 1
        latitudMinima = 0
        latitudMaxima = 100
        longitudMinima = 0
        longitudMaxima = 100
    
        ### Parámetros
        
        # Parámetro de disponibilidad horaria por empleado
        disponibilidadOperarios = generador.generarDisponibilidadOperarios(numEmpleados, numDiasOperacion, numHorasDiaLaboral, numHorasDisponiblesPorEmpleado)
        
        # Parámetro de disponibilidad horaria por orden
        disponibilidadOrdenes = generador.generarDisponibilidadOrdenes(numOrdenes, numDiasOperacion, numHorasDiaLaboral, numHorasDisponiblesPorOrden)
        
        # Parámetro de costos de ANS 
        costosANS = generador.generarCostosANS(numOrdenes, numDiasOperacion, numHorasDiaLaboral, costoMinimoANS, costoMaximoANS, umbralEleccionANS)
        
        # Parámetro de prioridad de cada órden
        prioridad = generador.generarPrioridadOrdenes(numOrdenes, prioridadMinimaOrdenes, prioridadMaximaOrdenes)
        
        # Parámetro de costo por hora de cada operario
        salario = generador.generarSalarioEmpleados(numEmpleados, salarioMinimoEmpleados, salarioMaximoEmpleados)
        
        # Parámetro de las habilidades de cada empleado
        habilidadesOperarios = generador.generarHabilidadesOperarios(numEmpleados, numHabilidades)
        
        # Parámetro de las habilidades requeridas en cada orden
        habilidadesOrdenes = generador.generarHabilidadesOrdenes(numOrdenes, numHabilidades)
        
        # Parámetro de porcentaje de cumplimiento de requerimiento en habilidades en cada orden
        porcentajeCumplimientoHabilidades =  porcentajeCumplimientoHabilidades
        
        # Parámetro de las coordenadas de los sitios de cada orden
        coordenadas = generador.generarCoordenadasLugares(numLugares, latitudMinima, latitudMaxima, longitudMinima, longitudMaxima)
        
        # Parámetro de las distancias entre los sitios de cada orden
        distanciasOrdenes = generador.generarDistanciasOrdenes(numLugares, coordenadas)
        
        data = {"numEmpleados": numEmpleados,
                "numOrdenes": numOrdenes,
                "numDiasOperacion": numDiasOperacion,
                "numHorasDiaLaboral": numHorasDiaLaboral,
                "numHabilidades": numHabilidades,
                "numLugares": numLugares,
                "disponibilidadOperarios": disponibilidadOperarios.tolist(),
                "disponibilidadOrdenes": disponibilidadOrdenes.tolist(),
                "costosANS": costosANS.tolist(),
                "prioridad": prioridad.tolist(),
                "salario": salario.tolist(),
                "habilidadesOperarios": habilidadesOperarios.tolist(),
                "habilidadesOrdenes": habilidadesOrdenes.tolist(),
                "porcentajeCumplimientoHabilidades": porcentajeCumplimientoHabilidades,
                "coordenadas": coordenadas,
                "distanciasOrdenes": distanciasOrdenes.tolist()}
        
        currentDirectory = './' + category
        currentLength = len([name for name in os.listdir(currentDirectory) if os.path.isfile(os.path.join(currentDirectory, name))])
        
        with open('./' + category + '/' + category[0] + str(currentLength + 1) + "_" + "E" + str(numEmpleados) + "O" + str(numOrdenes) + "D" + str(numDiasOperacion) + "H" + str(numHorasDiaLaboral) + "S" + str(numHabilidades) + '.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        f.close()

generarEscenarios("Small", 1)
#generarEscenarios("Medium", 10)
#generarEscenarios("Large", 10)