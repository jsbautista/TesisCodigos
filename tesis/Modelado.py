from pyomo.environ import *
from pyomo.opt import SolverFactory
import json
import numpy as np
import time
import matplotlib.pyplot as plt



def ejecutarModeloPyomo(filePath):
    # FUNCION ELIMINAR COMPONENTE
    def delete_component(model, comp_name):

        list_del = [vr for vr in vars(model)
                    if comp_name == vr
                    or vr.startswith(comp_name + '_index')
                    or vr.startswith(comp_name + '_domain')]

        list_del_str = ', '.join(list_del)
        print('Deleting model components ({}).'.format(list_del_str))

        for kk in list_del:
            model.del_component(kk)

    # Modelo -----------------------------------

    model = ConcreteModel()

    # Lectura JSON

    stageFile = open(filePath, )
    stageData = json.load(stageFile)

    numEmpleados = stageData["numEmpleados"]
    numOrdenes = stageData["numOrdenes"]
    numDiasOperacion = stageData["numDiasOperacion"]
    numHabilidades = stageData["numHabilidades"]
    # Conjunto de Habilidades
    model.S = RangeSet(1, numHabilidades)
    # conjunto de empleados
    model.E = RangeSet(1, numEmpleados)
    # conjunto de ordenes
    model.O = RangeSet(0, numOrdenes)
    # conjunto de dias
    model.D = RangeSet(1, numDiasOperacion)

    # Definición de parametros
    tiemD = np.asarray(stageData["tiempoDesplazamiento"])
    model.tD = Param(model.O, model.O, mutable=True)
    for e in model.O:
        for d in model.O:
                model.tD[e, d] = tiemD[e][d]

    tiemA = np.asarray(stageData["tiempoAtencion"])
    model.tA = Param(model.O, mutable=True)
    for o in model.O:
        model.tA[o] = tiemA[o]

    he = np.asarray(stageData["habilidadesOperarios"])
    model.habEmp = Param(model.E, model.S, mutable=True)
    for e in model.E:
        for s in model.S:
            model.habEmp[e, s] = he[e - 1][s - 1]

    ho = np.asarray(stageData["habilidadesOrdenes"])
    model.habOrd = Param(model.O, model.S, mutable=True)
    for o in model.O:
        for s in model.S:
            model.habOrd[o, s] = ho[o][s - 1]

    porcentajeCumplimientoHabilidades = stageData["porcentajeCumplimientoHabilidades"]

    model.Q = porcentajeCumplimientoHabilidades

    horas = np.asarray(stageData["horasTrabajo"])
    model.ht = Param(model.E, model.D, mutable=True)
    for e in model.E:
        for d in model.D:
            model.ht[e, d] = horas[e-1][d-1]

    stageFile.close()
    # Variables .............................................

    model.x = Var(model.E, model.O, model.D, model.O, domain=pyomo.environ.Binary)

    model.aux = Var(model.E, model.D, domain=pyomo.environ.Binary)

    model.u = Var(model.E, model.O, model.D, domain=Integers)

    model.min = Var(model.D, domain = pyomo.environ.PositiveIntegers)

    model.auxU = Var(model.E, model.O, model.D, model.O,domain=pyomo.environ.Binary)


    # Restricciones

    #Una orden solo puede tener un empleado asignado, solo puede ser atendida en un día y solo debe tener un antecesor
    def unEmpleadoPorOrden(model, o):
        if o != 0:
            return sum(model.x[e, o, d, a] for e in model.E for d in model.D for a in model.O) <= 1
        else:
            return Constraint.Skip


    #Un empleado solo puede trabajar Ht horas al día
    def horasMaximasEmpleado(model, e, d):
        return sum(model.x[e, o, d, a] * (model.tD[o, a] + model.tA[o]) for o in model.O for a in model.O) <= model.ht[
            e, d]


    #El antecesor debe ser diferente de la orden
    def antecesor(model):
        return sum(model.x[e, o, d, o] for o in model.O for e in model.E for d in model.D) <= 0


    #Los empleados deben partir de la orden 0
    def source_rule(model, e, d):
        return sum(model.x[e, o, d, 0] for o in model.O) - model.aux[e, d] == 0


    #Los empleados deben llegar al punto 0 (la empresa)
    def todosLleganA0(model, e, d):
        return sum(model.x[e, 0, d, o] for o in model.O) - model.aux[e, d] == 0


    #Ordenes Intermedias
    def intermediate_rule(model, e, d, a):
        if a != 0:
            return sum(model.x[e, o, d, a] for o in model.O) - sum(model.x[e, a, d, o] for o in model.O) == 0
        else:
            return Constraint.Skip

    #Evitar sub ciclos
    def subCiclos1(model, e, o, d):
        if o != 0:
            return model.u[e, o, d] <= 999 * sum(model.x[e, o, d, a] for a in model.O)
        else:
            return Constraint.Skip

    def subCiclos2(model, e, o, d):
        if o != 0:
            return model.u[e, o, d] >= sum(model.x[e, o, d, a] for a in model.O)
        else:
            return Constraint.Skip

    def subCiclos3(model, e, o, d, a):
        if o != 0 and a != 0:
            return model.u[e, o, d] - model.u[e, a, d] <= 999 * (1 -
                model.x[e, o ,d, a]) - 1 + 999 * (1 - sum(model.x[e, a, d, i] for i in model.O))
        else:
            return Constraint.Skip

    def subCiclos4(model, e, d):
        return model.u[e, 0, d] == 0

    def subCiclos5(model, e, o, d):
        return model.u[e, o, d] <= sum(model.x[e, i, d, a] for a in model.O for i in model.O)



    #El empleado debe cumplir con unas habilidades minimas
    def habilidades(model, e, o, d, a):
        return sum(model.x[e, o, d, a] * model.habEmp[e, s] * model.habOrd[o, s] for s in model.S) >= model.Q * sum(model.x[e, o, d, a] *
                    model.habOrd[o, s] for s in model.S)


    #Acotar variable auxiliar
    def aux1(model, e, d):
        return sum(model.x[e, o, d, a] for o in model.O for a in model.O) <= 999 * model.aux[e, d]

    def aux2(model, e, d):
        return sum(model.x[e, o, d, a] for o in model.O for a in model.O) >= model.aux[e, d]

    #MinMax
    def minMax(model, e, d):
        #return model.min[d] <= sum(
        #    model.x[e, o, d, a] + 999 * (1 - model.aux[e, d]) for e in model.E for o in model.O for a in model.O)
        return model.min[d] <= sum(model.x[e, o, d, a] for o in model.O for a in model.O)



    delete_component(model, 'c1')
    delete_component(model, 'c2')
    delete_component(model, 'c3')
    delete_component(model, 'c4')
    delete_component(model, 'c5')
    delete_component(model, 'c6')
    delete_component(model, 'c7')
    delete_component(model, 'c8')
    delete_component(model, 'c9')
    delete_component(model, 'c10')
    delete_component(model, 'c11')
    delete_component(model, 'c12')
    delete_component(model, 'c13')
    delete_component(model, 'c14')
    delete_component(model, 'c15')
    delete_component(model, 'c16')
    delete_component(model, 'c17')

    model.c1 = Constraint(model.O, rule=unEmpleadoPorOrden)
    model.c2 = Constraint(model.E, model.D, rule=horasMaximasEmpleado)
    model.c3 = Constraint(rule=antecesor)
    model.c4 = Constraint(model.E, model.D, rule=source_rule)
    model.c6 = Constraint(model.E, model.D, rule=todosLleganA0)
    model.c7 = Constraint(model.E, model.D, rule=source_rule)
    model.c8 = Constraint(model.E, model.D, model.O, rule=intermediate_rule)
    model.c9 = Constraint(model.E, model.O, model.D, rule=subCiclos1)
    model.c10 = Constraint(model.E, model.O, model.D, rule=subCiclos2)
    model.c11 = Constraint(model.E, model.O, model.D, model.O, rule=subCiclos3)
    model.c12 = Constraint(model.E, model.D, rule=subCiclos4)
    model.c13 = Constraint(model.E, model.O,model.D, model.O, rule=habilidades)
    model.c14 = Constraint(model.E, model.D, rule=aux1)
    model.c15 = Constraint(model.E, model.D, rule=aux2)
    model.c16 = Constraint(model.E, model.D, rule=minMax)
    model.c17 = Constraint(model.E, model.O, model.D, rule=subCiclos5)


    model.f0 = Var()



    f0 = (sum(model.x[e, o, d, a] for e in model.E for o in model.O for d in model.D for a in model.O) + sum(model.min[d]for d in model.D))


    # Ejecucion modelo
    timerGeneralInicial = time.time()

    #Funció objetivo
    model.obj = Objective(expr = f0, sense = maximize)

    SolverFactory('glpk', executable="C:/glpk-4.65/w64/glpsol.exe").solve(model)
   # SolverFactory('ipopt',executable="C:/Users/PC/Ipopt/bin/ipopt.exe").solve(model)

    timerGeneralFinal = time.time()
    timerGeneral = timerGeneralFinal - timerGeneralInicial

    # =============================================================================
    # model.display()
    # =============================================================================
    valorF0 = value(sum(model.x[i, j, k, l] for i in model.E for j in model.O for k in model.D for l in model.O))


    for d in model.D:
        print(model.min[d])
        print(value(model.min[d]) - 1)

    for d in model.D:
        for e in model.E:
            print(model.aux[e, d])
            print(value(model.aux[e, d]))


    for e in model.E:
        for d in model.D:
            for o in model.O:
                for a in model.O:
                    if value(model.x[e, o, d, a]) == 1:
                        print(model.x[e, o, d, a])
                        print(value(model.x[e, o, d, a]))

    contarActivos = 0
    for e in model.E:
        for d in model.D:
            nombre = "Empleado " + str(e) + " dia " + str(d)
            plt.title(nombre)
            lista = []
            salida = True
            antecesor = 0
            lista.append(0)
            while salida:
                for o in model.O:
                    if value(model.x[e, o, d, antecesor]) == 1 and salida:
                        lista.append(o)
                        antecesor = o
                        if antecesor == 0:
                            contarActivos += 1
                            salida = False

            print(lista)
            plt.plot(lista,'ro',lista,'k')
            plt.show()


    for d in model.D:
        print(model.min[d])
        print(value(model.min[d]) - 1)



    print("Función 0 Max Ordenes " + str(valorF0-contarActivos))

    results = {
        "FO_Global": (valorF0 - contarActivos ),
        "Tiempo": timerGeneral}
    return results

