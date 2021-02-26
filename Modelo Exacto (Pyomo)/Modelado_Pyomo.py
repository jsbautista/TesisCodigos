# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 18:32:44 2020

@author: estudiante
"""
import matplotlib.pyplot as plt
from datetime import datetime
from pyomo.environ import *
from pyomo.opt import SolverFactory
import matplotlib.pyplot as plt
import sys
import os
import json
import numpy as np
import math
import time
import random

def ejecutarModeloPyomo(filePath):
    
    #FUNCION ELIMINAR COMPONENTE
    def delete_component(model, comp_name):
    
            list_del = [vr for vr in vars(model)
                        if comp_name == vr
                        or vr.startswith(comp_name + '_index')
                        or vr.startswith(comp_name + '_domain')]
    
            list_del_str = ', '.join(list_del)
            print('Deleting model components ({}).'.format(list_del_str))
    
            for kk in list_del:
                model.del_component(kk)
    
    #Modelo -----------------------------------
    
    model = ConcreteModel()

    #Lectura JSON
    
    stageFile = open(filePath,)
    stageData = json.load(stageFile)
    
    numEmpleados = stageData["numEmpleados"]
    numOrdenes = stageData["numOrdenes"]
    numDiasOperacion = stageData["numDiasOperacion"]
    numHorasDiaLaboral = stageData["numHorasDiaLaboral"]
    numHabilidades = stageData["numHabilidades"]
    numLugares = stageData["numLugares"]
    #Conjunto de Habilidades
    model.S = RangeSet (1, numHabilidades)
    #conjunto de empleados
    model.E = RangeSet (1, numEmpleados)
    #conjunto de ordenes
    model.O = RangeSet (1, numOrdenes)
    #conjunto de horas
    model.H = RangeSet (1, numHorasDiaLaboral)
    #conjunto de dias
    model.D = RangeSet(1,numDiasOperacion)
    #Conjunto de sitios
    model.L = RangeSet(1,numLugares)
    
    #Definición de parametros
    disp = np.asarray(stageData["disponibilidadOperarios"])
    model.horDisp = Param(model.E,model.D,model.H,mutable = True)
    for e in model.E:
        for d in model.D:
            for h in model.H:
                model.horDisp[e,d,h] = disp[e-1][d-1][h-1]
    
    prio = np.asarray(stageData["prioridad"])
    model.p = Param(model.O,mutable=True)  
    for o in model.O:
        model.p[o] = prio[o-1]
        
    cos =  np.asarray(stageData["costosANS"])
    model.costoANS = Param(model.O,model.D,model.H,mutable=True)
    for o in model.O:
        for d in model.D:
            for h in model.H:
                model.costoANS[o,d,h] = cos[o-1][d-1][h-1]
    
    he =np.asarray(stageData["habilidadesOperarios"])
    model.habEmp = Param(model.E, model.S, mutable= True)    
    for e in model.E:
        for s in model.S:    
            model.habEmp[e,s] = he[e-1][s-1]

    ho = np.asarray(stageData["habilidadesOrdenes"])
    model.habOrd = Param(model.O, model.S, mutable = True)    
    for o in model.O:
        for s in model.S:
            model.habOrd[o,s] = ho[o-1][s-1]
    
    costE = np.asarray(stageData["salario"])
    model.costHorEmp =Param(model.E, mutable=True)
    for e in model.E:
        model.costHorEmp[e] = costE[e-1]

    hord = np.asarray(stageData["disponibilidadOrdenes"])
    model.horOrd = Param(model.O,model.D,model.H,mutable = True)
    for o in model.O:
        for d in model.D:
            for h in model.H:
                model.horOrd[o,d,h] = hord[o-1][d-1][h-1]
    
    
    
    porcentajeCumplimientoHabilidades = np.asarray(stageData["porcentajeCumplimientoHabilidades"])
    model.q = Param(model.O,mutable=True)  
    for o in model.O:
        model.q[o] = porcentajeCumplimientoHabilidades[o-1] 
    
    model.costD = Param(model.L, model.L, mutable=True)
    coordenadas = np.asarray(stageData["coordenadas"])
    dist = np.asarray(stageData["distanciasOrdenes"])
    
    for l1 in model.L:
        for l2 in model.L:
            model.costD[l1,l2] = dist[l1-1][l2-1]
    
    stageFile.close()                                                                                  
    #Variables .............................................
    
    model.x = Var(model.E, model.O, model.D,model.H,  domain = Binary)
    
    model.y = Var(model.L,model.L,model.E,model.D,model.H,model.H,domain = Binary)
    
    model.z = Var(model.E,model.D, domain = Binary)
    
    #Restricciones
    
    def unEmpleadoPorOrden(model,o):
        return sum(model.x[e,o,d,h] for e in model.E for d in model.D for h in model.H) <= 1
    
    def unEmpleadoPorOrdenHoraDia(model,e,d,h):
        return sum(model.x[e,o,d,h] for o in model.O ) <= 1
    
    def asignacionEnHorario(model,e,d,h):
        return inequality(0,sum(model.x[e,o,d,h] for o in model.O),model.horDisp[e,d,h])
    #    return(sum(model.x[e,o,d,h] for o in model.O) <= model.horDisp[e,d,h])
    
    def horasOrden(model,o, d, h):
        return(sum(model.x[e,o,d,h] for e in model.E) <= model.horOrd[o,d,h])
    
    def habilidadesMinimas(model,o,e,d,h):
        return sum(model.x[e,o,d,h]*model.habOrd[o,s]*model.habEmp[e,s] for s in model.S) >= model.q[o]*sum(model.x[e,o,d,h]*model.habOrd[o,s] for s in model.S)
    
    def aux_dist(model,e,d):
        return model.z[e,d] >= (sum(model.x[e,o,d,h] for o in model.O for h in model.H )/1000000)
    
    def aux_dist2(model,e,d):
        return model.z[e,d] - 0.999 <= (sum(model.x[e,o,d,h] for o in model.O for h in model.H )/1000)
    
    def source_rule(model,i,k,d):
        if i==1:
            return sum(model.y[i,j,k,d,h,h2] for j in model.L for h in model.H for h2 in model.H) == model.z[k,d]
        else:
            return Constraint.Skip
    
    def destination_rule(model,j,k,d):
        if j==1:
            return sum(model.y[i,j,k,d,h,h2] for i in model.L for h in model.H for h2 in model.H) == model.z[k,d]
        else:
            return Constraint.Skip
    
    def intermediate_rule(model,j,k,d,h2):
        if j!=1:
            return sum(model.y[i,j,k,d,h,h2] for i in model.L for h in model.H) - sum(model.y[j,i,k,d,h2,h] for i in model.L for h in model.H )==0
        else:
            return Constraint.Skip
    
    def lugarOrden(model,o,l,e,d,h):
        if (o+1)==l:
            return sum(model.y[i,l,e,d,h1,h] for i in model.L for h1 in model.H ) >= model.x[e,o,d,h] 
        else:
            return Constraint.Skip
    
    def lugarOrden2(model,o,l,e,d,h):
        if (o+1)==l:
            return sum(model.y[i,l,e,d,h1,h] for i in model.L for h1 in model.H) <= model.x[e,o,d,h] 
        else:
            return Constraint.Skip
        
    def volver(model,i,j,e,h2):
        if i != 1 and j != 1:
            return (sum(model.y[i,j,e,h,h2] for h in model.H ) + sum(model.y[j,i,e,h2,h] for h in model.H)) <= 1
        else:
            return Constraint.Skip
        
    def ciclos(model,i):
        return sum(model.y[i,i,e,d,h1,h2] for e in model.E for d in model.D for h1 in model.H for h2 in model.H) == 0
    
    
    def horas(model,d,h,h2,e):
        if h >= h2:
            return sum(model.y[i,j,e,d,h,h2] for i in model.L for j in model.L) == 0
        else:
            return Constraint.Skip
        
    def horasCont(model,i,j,e,h1,h2):
        if h2 != h1 + 1:
            return model.y[i,j,e,h1,h2] == 0
        else:
            return Constraint.Skip
        
    delete_component(model, 'c1')
    delete_component(model, 'c2')
    delete_component(model, 'c3')
    delete_component(model, 'c4')
    delete_component(model, 'c6')
    delete_component(model, 'c8')
    delete_component(model, 'c9')
    delete_component(model, 'c10')
    delete_component(model, 'c11')
    delete_component(model, 'c12')
    delete_component(model, 'c13')
    delete_component(model, 'source')
    delete_component(model, 'destination')
    delete_component(model, 'intermediate')
    
    model.c1 =Constraint(model.O, rule=unEmpleadoPorOrden)
    model.c2 =Constraint(model.E, model.D, model.H,  rule=unEmpleadoPorOrdenHoraDia)
    model.c3 =Constraint(model.E, model.D, model.H,  rule=asignacionEnHorario)
    model.c4 =Constraint(model.O, model.D, model.H,  rule=horasOrden)
    model.c6 =Constraint(model.O, model.E, model.D, model.H,rule=habilidadesMinimas)
    model.source=Constraint(model.L, model.E, model.D, rule=source_rule)
    model.destination=Constraint(model.L, model.E, model.D, rule=destination_rule)
    model.intermediate=Constraint(model.L, model.E, model.D, model.H,rule=intermediate_rule)
    model.c8 = Constraint(model.O, model.L, model.E, model.D, model.H, rule=lugarOrden)
    model.c9 = Constraint(model.O, model.L, model.E, model.D, model.H, rule=lugarOrden2)
    model.c10 = Constraint(model.E, model.D, rule = aux_dist)
    model.c11 = Constraint(model.E, model.D, rule = aux_dist2)
    model.c12 = Constraint(model.D, model.H, model.H, model.E, rule=horas)
    model.c13 = Constraint(model.L, rule= ciclos)
    #model.c13 = Constraint(model.L, model.L, model.E, model.H, model.H, rule= horasCont)
    
    #Funciones Objetivo..............................................
    
    #Maximizar el numero de ordenes completadas
    #model.obj = Objective(expr = sum(model.x[i,j,k,l] for i in model.E for j in model.O for k in model.H for l in model.D), sense=maximize)
    
    #Maximizar Fairness
    #model.obj = Objective(expr = model.z,sense=maximize)
    
    #Minimizar costo de ANS
    #model.obj = Objective(expr = sum(model.x[i,j,k,l]*model.costoANS[j,k,l] for i in model.E for j in model.O for k in model.H for l in model.D),sense=minimize)
    
    #Maximizar el cumplimiento por Prioridad
    #model.obj = Objective(expr = sum(model.x[i,j,k,l]*model.p[j] for i in model.E for j in model.O for k in model.H for l in model.D),sense=maximize)
    
    #Minimizar el Costo de operación
    #model.obj = Objective(expr = sum(model.x[i,j,k,l]*model.costHorEmp[i] for i in model.E for j in model.O for k in model.H for l in model.D),sense=minimize)
    
    #Minimizar la distancia recorrida
    #model.obj = Objective(expr = sum(model.y[i,j]*cost[i,j] for i in model.L for j in model.L))
    
    model.f0 = Var()
    model.f2 = Var()
    model.f3 = Var()
    model.f4 = Var()
    model.f5 = Var()
    #model.f6 = Var()
    
    w = 1/5
    w1 = 0.5
    w2 = 1/2
    #w3 = 0.999
    #w4 = (w3/2)/4
    w3 = 0.95
    w4 = (1-w3)/5
    f0 = (-1*sum(model.x[i,j,k,l] for i in model.E for j in model.O for k in model.D for l in model.H))
    f2 = sum(model.x[i,j,k,l]*model.costoANS[j,k,l] for i in model.E for j in model.O for k in model.D for l in model.H)
    f3 = (-1*sum(model.x[i,j,k,l]*model.p[j] for i in model.E for j in model.O for k in model.D for l in model.H))
    f4 = sum(model.x[i,j,k,l]*model.costHorEmp[i] for i in model.E for j in model.O for k in model.D for l in model.H)
    f5 = sum(model.y[i,j,k,d,h,h2]*model.costD[i,j] for i in model.L for j in model.L for k in model.E for d in model.D for h in model.H for h2 in model.H)
    
   #f6 = (-1*((sum(model.x[i,j,k,l] for i in model.E 
   #                           for j in model.O 
   #                           for k in model.D 
   #                           for l in model.H)**2) /  ((numEmpleados * ( 1 + sum((sum(model.x[i,j,k,l] for j in model.O 
   #                                                                                                     for k in model.D 
   #                                                                                                     for l in model.H)**2) for i in model.E))))))
    
    
    # Ejecucion modelo
    timerGeneralInicial = time.time()                                      
                                      
    #model.obj = Objective(expr = w1*f0 + w*f1 + w*f2 + w*f3 + 0.15*f4,sense = minimize)
    
    #model.obj = Objective(expr = (f0*(w3/2) + f2*(w4)+ f3*(w4)+ f4*(w4)+ f5*(1-w3) + f6*(w4)),sense = minimize)
    model.obj = Objective(expr = (f0*(w3) + f2*(w4)+ f3*(w4)+ f4*(w4)+ f5*(w4)),sense = minimize)
    #model.obj = Objective(expr = (f0*(1-w1) + f6*(w1)),sense = minimize)
    #model.obj = Objective(expr = (f0*w3 + (1-w3)*f5 ),sense = minimize)
    SolverFactory("glpk").solve(model)
    
    timerGeneralFinal = time.time()
    timerGeneral = timerGeneralFinal - timerGeneralInicial
    #SolverFactory('scip', executable="C:/Users/estudiante/anaconda3/Library/bin/scipampl.exe").solve(model)
    #SolverFactory('mindtpy').solve(model, mip_solver='glpk', nlp_solver='ipopt') 
    #results = solver.solve(model)☺
    #solver_manager = SolverManagerFactory('neos')
    #results = solver_manager.solve(model, opt='bonmin')
    
    # =============================================================================
    #model.display()
    # =============================================================================
    valorF0 =value(sum(model.x[i,j,k,l] for i in model.E for j in model.O for k in model.D for l in model.H))
    valorF2= value(sum(model.x[i,j,k,l]*model.costoANS[j,k,l] for i in model.E for j in model.O for k in model.D for l in model.H))
    valorF3=value(sum(model.x[i,j,k,l]*model.p[j] for i in model.E for j in model.O for k in model.D for l in model.H))
    valorF4=value(sum(model.x[i,j,k,l]*model.costHorEmp[i] for i in model.E for j in model.O for k in model.D for l in model.H))
    valorF5=value(sum(model.y[i,j,k,d,h,h2]*model.costD[i,j] for i in model.L for j in model.L for k in model.E for d in model.D for h in model.H for h2 in model.H))
    #valorF6 = value((sum(model.x[i,j,k,l] for i in model.E 
    #                          for j in model.O 
    #                          for k in model.D
    #                          for l in model.H)**2) / ((numEmpleados * ( 1 + sum((sum(model.x[i,j,k,l] for j in model.O 
    #                                                                                                    for k in model.D 
    #                                                                                                    for l in model.H)**2) for i in model.E)))))
    
    print("Función 0 Max Ordenes "+ str(valorF0))
    print("Función 2 ANS " + str(valorF2))
    print("Función 3 Prioridad " +  str(valorF3))
    print("Función 4 Costo " +  str(valorF4))
    print("Función 5 Distancia " +  str(valorF5))
    #print("Función 6 Fairness " + str(valorF6))
    
    #model.pprint()
    
    #model.x.pprint()
    
    #Funcion auxiliar
    
    list1 = []
    for i in model.E:
        a=0
        for y in model.O:
            for d in model.D:
                for z in model.H:
                    if(value(model.x[i, y, d, z]) == 1):
                        print(str(value(model.x[i, y, d, z])))
                        a+=1
                        print ("....................................................")
                        print ("Para el especialista " + str(i) + " se le asigno la orden " + str(y) + " el dia " + str(d) +" a la hora " + str(z))
                        print (a)
                        list1.append(a)
                  
        print ("....................................................")
        print ("Para el especialista " + str(i) + " se le asignaron " + str(a) + " ordenes")
        print (a)
        
    list1
    
    
    
    for e in model.E:
        for d in model.D:
            for h in model.H:
                for h2 in model.H:
                    for l in model.L:
                        for lu in model.L:
                            if value(model.y[l,lu,e,d,h,h2]) == 1:
                                print ("El dia " + str(d)+" de " +str(l)+ " a " + str(lu) + " con un costo de " +  str(dist[l-1,lu-1]) + " el empl " + str(e) + " de la hora " + str(h)+" a la hora " + str(h2))
    """      
    for i in model.E:
        a=0
        for y in model.O:
            for d in model.D:
                for z in model.H:
                    for l in model.L:
                        for lu in model.L:
                            if value(model.y[l,lu,i]) == 1 and value(model.x[i,y,z,d]) == 1:
                                print( str(i) + " " + str(y) + " de " + str(l) + " a " + str(lu))
                                print(value(model.x[i,y,z,d]))
                                print(value(model.y[l,lu,i]))
                                print ("....................................................")
    """   
    colors = [np.random.rand(3) for i in range(numEmpleados)]
    for d in model.D:
        for y in model.O:
            for i in model.E:
                for z in model.H:
                    for h in model.H:
                        for l in model.L:
                            for lu in model.L:
                                if value(model.y[l,lu,i,d,z,h]) == 1:                         
                                    lugarOrigen = coordenadas[l-1]
                                    lugarDestino = coordenadas[lu-1]
                                    plt.plot([lugarOrigen["latitud"], lugarDestino["latitud"]],[lugarOrigen["longitud"], lugarDestino["longitud"]], color=colors[e-1])
        for i in model.L:
            lugar = coordenadas[i-1]
            plt.plot(lugar["latitud"], lugar["longitud"],'o')
            plt.text(lugar["latitud"], lugar["longitud"]-2, i, horizontalalignment='left',verticalalignment='center')
        
        plt.title("Dia " + str(d))
        plt.xlabel('Latitud')
        plt.ylabel('Longitud')
        plt.show()                            
    
    results = {"FO_Global": (-1*valorF0*(w3) + valorF2*(w4)+ -1*valorF3*(w4)+ valorF4*(w4)+ valorF5*(w4)),
               "FO_Ordenes": valorF0,
               "FO_Costo": valorF4,
               "FO_ANS": valorF2,
               "FO_Prioridad": valorF3,
               "FO_Distancia": valorF5,
               "Tiempo": timerGeneral}
    return results
    
        