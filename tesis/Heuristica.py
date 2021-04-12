import random
import json
import copy
import CrearEscenario
import numpy
import winsound


def darProbabilidad(matriz, tiempo, nodoActual, feromonas, alpha, beta, habOrdenes, habEmpleados, q):
    probabilidad = []
    n = []

    for i in range(len(matriz)):
        if (matriz[nodoActual][i] != 0):
            if(sum(numpy.array(habOrdenes[i])*numpy.array(habEmpleados)) >= q * sum(numpy.array(habOrdenes[i]))):
                n.append(round(beta / matriz[nodoActual][i], 2))
            else:
                n.append(0)
        else:
            n.append(0)

    feromonas = feromonas * alpha

    vector = numpy.array(n) * numpy.array(feromonas[nodoActual])
    vector[0] = 0

    suma = sum(vector)
    if(suma == 0):
        return probabilidad

    for i in range(len(matriz)):
        if matriz[nodoActual][i] == 0:
            if len(probabilidad) > 0:
                probabilidad.append(probabilidad[i - 1])
            else:
                probabilidad.append(0)
        else:
            if (matriz[nodoActual][i] + matriz[i][0]) < tiempo:
                if len(probabilidad) > 0:
                    probabilidad.append(vector[i] / suma + probabilidad[i - 1])
                else:
                    probabilidad.append(vector[i] / suma)
            else:
                if len(probabilidad) > 0:

                    probabilidad.append(probabilidad[i - 1])
                else:
                    probabilidad.append(0)
    return probabilidad


def borrarNodo(nodoActual, matriz):
    for i in range(len(matriz)):
        matriz[i][nodoActual] = 0
    return matriz


def actualizarFeromonas(secuencia, feromonas, rho):
    deltaFeromonas = []

    for i in range(len(feromonas)):
        deltaFeromonas.append(numpy.repeat(0, len(feromonas)).tolist())

    for i in range(len(secuencia)):
        for j in range(len(secuencia[i]) - 1):
            deltaFeromonas[secuencia[i][j]][secuencia[i][j + 1]] += (len(secuencia[i]))

    return (numpy.array(deltaFeromonas) + numpy.array(feromonas)) * rho


def heuristica():
    CrearEscenario.crearEscenario(2, 33, 1)

    alpha = 1
    beta = 5
    rho = 0.5

    with open('Escenario.json') as file:
        data = json.load(file)
        tiempoDesplazamiento = data['tiempoDesplazamiento']
        tiempoAtencion = data['tiempoAtencion']
        tiempoD = data['horasTrabajo']
        numEmpleados = data['numEmpleados']
        numDias = data['numDiasOperacion']
        habEmp = data['habilidadesOperarios']
        habOrde = data['habilidadesOrdenes']
        qParametro = data['porcentajeCumplimientoHabilidades']


    tiempoTotal = []
    for i in range(len(tiempoDesplazamiento)):
        vectorActual = []
        for j in range(len(tiempoDesplazamiento)):
            if (tiempoDesplazamiento[i][j] != 0):
                vectorActual.append(tiempoDesplazamiento[i][j] + tiempoAtencion[j])
            else:
                vectorActual.append(0)
        tiempoTotal.append(vectorActual)

    iteraciones = 100
    feromonas = []

    for i in range(len(tiempoDesplazamiento)):
        feromonas.append(numpy.repeat(1, len(tiempoDesplazamiento)).tolist())

    hormigas = 20
    secuenciaM = []

    for j in range(iteraciones):
        secuencias = []
        for i in range(hormigas):
            tiempo = copy.deepcopy(tiempoTotal)
            secuencia = []
            for dias in range(numDias):
                for emp in range(numEmpleados):
                    habilidadesEmpleado = habEmp[emp]
                    vacio = True
                    nodoActual = 0

                    tiempoDisponible = tiempoD[emp][dias]


                    while (vacio or nodoActual != 0):

                        probabilidad = darProbabilidad(tiempo, tiempoDisponible, nodoActual, feromonas, alpha, beta, habOrde, habilidadesEmpleado, qParametro)
                        aleatorio = random.random()
                        contador = 0

                     #   if(probabilidad[len(probabilidad)-1] < 1):
                     #       aleatorio = aleatorio * probabilidad[len(probabilidad)-1]
                        while contador < len(probabilidad) and aleatorio > probabilidad[contador]:
                            contador += 1
                        if(len(probabilidad)) > 1:
                            if (probabilidad[len(probabilidad) - 1] < aleatorio):
                                contador = 0

                        tiempoDisponible -= tiempo[nodoActual][contador]
                        nodoActual = contador
                        secuencia.append(nodoActual)
                        vacio = False

                        tiempo = borrarNodo(nodoActual, tiempo)

            if len(secuencia) > len(secuenciaM):
                secuenciaM = secuencia
            secuencias.append(secuencia)

        feromonas = actualizarFeromonas(secuencias, feromonas, rho)

    print(secuenciaM)
    print(len(secuenciaM))
    while True:
        duration = 1000  # milliseconds
        freq = 440  # Hz
        winsound.Beep(freq, duration)



heuristica()
