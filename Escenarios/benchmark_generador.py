# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 18:50:02 2020

@author: danie
"""

import numpy as np
import generador
import time

#pequeño: 1-5
#mediano: 6-10
#grande: 11-20
numEmpleados = 20
numOrdenes = 20
numDiasOperacion = 5
numHorasDiaLaboral = 8
numHabilidades = 5

numHorasDisponiblesPorEmpleado = 7
numHorasDisponiblesPorOrden = 7

costoMinimoANS = 2
costoMaximoANS = 8
umbralEleccionANS = 0.1

prioridadMinimaOrdenes = 1
prioridadMaximaOrdenes = 5

salarioMinimoEmpleados = 5
salarioMaximoEmpleados = 20

porcentajeCumplimientoHabilidades = 1


def generarEscenario():
    
    f = open("demofile.txt", "w")
    
    
    # Parámetro de diponibilidad horaria por empleado
    P = generador.generarDisponibilidadOperarios(numEmpleados, numDiasOperacion, numHorasDiaLaboral, numHorasDisponiblesPorEmpleado)
    f.write(np.array_str(P))
    
    # Parámetro de diponibilidad horaria por orden
    Q = generador.generarDisponibilidadOrdenes(numOrdenes, numDiasOperacion, numHorasDiaLaboral, numHorasDisponiblesPorOrden)
    f.write(np.array_str(Q))
    
    # Parámetro de costos de ANS 
    NN = generador.generarCostosANS(numOrdenes, numDiasOperacion, numHorasDiaLaboral, costoMinimoANS, costoMaximoANS, umbralEleccionANS)
    f.write(np.array_str(NN))
    
    # Parámetro de prioridad de cada órden
    QQ = generador.generarPrioridadOrdenes(numOrdenes, prioridadMinimaOrdenes, prioridadMaximaOrdenes)
    f.write(np.array_str(QQ))
    
    # Parámetro de costo por hora de cada operario
    J = generador.generarSalarioEmpleados(numEmpleados, salarioMinimoEmpleados, salarioMaximoEmpleados)
    f.write(np.array_str(J))
    
    # Parámetro de las habilidades de cada empleado
    K = generador.generarHabilidadesOperarios(numEmpleados, numHabilidades)
    f.write(np.array_str(K))
    
    # Parámetro de las habilidades requeridas en cada orden
    Y = generador.generarHabilidadesOrdenes(numOrdenes, numHabilidades)
    f.write(np.array_str(Y))
    
    f.close()

timerGeneralInicial = time.time()
repeticiones = 100
escenarios = 1000
for i in range(repeticiones):
    for i in range(escenarios):
        generarEscenario()

timerGeneralFinal = time.time()
timerGeneral = timerGeneralFinal - timerGeneralInicial
print(timerGeneral/repeticiones)