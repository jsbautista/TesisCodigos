import numpy as np
import random

def generarDisponibilidadOperarios(numEmpleados, numDiasOperacion, numHorasDiaLaboral, numHorasDisponiblesPorEmpleado):
    dispOperarios = np.zeros((numEmpleados, numDiasOperacion, numHorasDiaLaboral))
    for i in range(numEmpleados):
        for j in range(numDiasOperacion):
            arr = list(range(0, numHorasDiaLaboral))
            elecciones = random.choices(arr, k=numHorasDisponiblesPorEmpleado)
            for y in elecciones:
                dispOperarios[i,j,y] = 1
    return dispOperarios

def generarDisponibilidadOrdenes(numOrdenes, numDiasOperacion, numHorasDiaLaboral, numHorasDisponiblesPorOrden):
    dispOrdenes = np.zeros((numOrdenes, numDiasOperacion, numHorasDiaLaboral))
    for i in range(numOrdenes):
        for j in range(numDiasOperacion):
            arr = list(range(0, numHorasDiaLaboral))
            elecciones = random.choices(arr, k=numHorasDisponiblesPorOrden)
            for y in elecciones:
                dispOrdenes[i,j,y] = 1
    return dispOrdenes

def generarPrioridadOrdenes(numOrdenes, prioridadMinima, prioridadMaxima):
    prioridadOrdenes = np.zeros(numOrdenes)
    for i in range(numOrdenes):
        prioridadGenerada = random.randint(prioridadMinima, prioridadMaxima)
        prioridadOrdenes[i] = prioridadGenerada
    return prioridadOrdenes
    
def generarSalarioEmpleados(numEmpleados, salarioMinimo, salarioMaximo):
    salarioEmpleados = np.zeros(numEmpleados)
    for i in range(numEmpleados):
        salarioGenerado = random.randint(salarioMinimo, salarioMaximo)
        salarioEmpleados[i] = salarioGenerado
    return salarioEmpleados

def generarHabilidadesOperarios(numEmpleados, numHabilidades):
    habilidadesOperarios = np.zeros((numEmpleados, numHabilidades))
    for i in range(numEmpleados):
            arr = list(range(0, numHabilidades))
            elecciones = random.choices(arr, k=numHabilidades)
            for j in elecciones:
                habilidadesOperarios[i,j] = 1
    return habilidadesOperarios

def generarHabilidadesOrdenes(numOrdenes, numHabilidades):
    habilidadesOrdenes = np.zeros((numOrdenes, numHabilidades))
    for i in range(numOrdenes):
            arr = list(range(0, numHabilidades))
            elecciones = random.choices(arr, k=numHabilidades)
            for j in elecciones:
                habilidadesOrdenes[i,j] = 1
    return habilidadesOrdenes

def generarCostosANS(numOrdenes, numDias, numHorasPorDia, costoMinimo, costoMaximo, umbral):
    costosANS = np.zeros((numOrdenes, numDias, numHorasPorDia))
    for i in range(numOrdenes):
        costoOrdenANS = np.random.randint(costoMinimo, costoMaximo)
        indicador = False
        for j in range(numDias):
            for k in range(numHorasPorDia):
                eleccion = random.random()
                if(eleccion < umbral):
                    indicador = True
                if(indicador):
                    costosANS[i,j,k] = costoOrdenANS
    return costosANS

# def generarDistanciasOrdenes(numLugares, distanciaMinima, distanciaMaxima):
#     distanciasOrdenes = np.zeros((numLugares, numLugares))
#     for i in range(numLugares):
#         for j in range(i+1, numLugares):
#             if i != j:
#                 distanciaGenerada = np.random.randint(distanciaMinima, distanciaMaxima)
#                 distanciasOrdenes[i,j] = distanciaGenerada
#                 distanciasOrdenes[j,i] = distanciaGenerada
#     return distanciasOrdenes
                         
def generarCoordenadasLugares(numLugares, latitudMinima, latitudMaxima, longitudMinima, longitudMaxima):
    coordenadasLugares = []
    for i in range(numLugares):
        coordenadaLugar = {"latitud": "", "longitud": ""}
        latitudGenerada = np.random.randint(latitudMinima, latitudMaxima)
        longitudGenerada = np.random.randint(longitudMinima, longitudMaxima)
        coordenadaLugar["latitud"] = latitudGenerada
        coordenadaLugar["longitud"] = longitudGenerada
        coordenadasLugares.append(coordenadaLugar)
    return coordenadasLugares

def generarDistanciasOrdenes(numLugares, coordenadas):
    distanciasOrdenes = np.zeros((numLugares, numLugares))
    for i in range(numLugares):
        for j in range(i+1, numLugares):
            if i != j:
                distanciaGenerada = abs(coordenadas[i]["latitud"] - coordenadas[j]["latitud"]) + abs(coordenadas[i]["longitud"] - coordenadas[j]["longitud"])
                distanciasOrdenes[i,j] = distanciaGenerada
                distanciasOrdenes[j,i] = distanciaGenerada
    return distanciasOrdenes
    
