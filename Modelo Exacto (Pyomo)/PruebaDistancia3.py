# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 11:41:23 2020

@author: Sebastian
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
import random

#os.system("clear")


"""
Este modelo tiene como función objetivo minimizar el costo de asignación de los
agentes. Se pueden quedar agentes sin ordenenes asignadas, pero todas las 
ordenes deben asignarse. 
No se tiene en cuenta la función del Fairness. 
Se tienen las siguientes restricciones:
    1. Solo un empleado puede cumplir una orden 
    2. Un empleado solo puede tener una orden en una hora y dia dados
    3. Se debe asignar en una orden en los horarios disponibles del empleado
    4. Se debe asignar un empleado a una orden en los horarios disponibles de 
       cumplimiento de la orden
    5. Todas las ordenes se deben cumplir
"""



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
    
model = ConcreteModel()

"""
Primer escenario de prueba:
Conjuntos:
    3 Habilidades
    3 Empleados
    3 Ordenes
    3 Horas
    1 Día
Parametros:
    Prioridad de la orden: 1,3,2 en orden
    Habilidades del empleado: 3,2,1 en orden
    Habilidades para las ordenes: 1,3,2 en orden
    Todas las horas estan disponibles para empleados y ordenes
    No hay limite, excepto para la primera orden a la ultima hora
    El costo de hora de un empleado es de un valor de 3
    Los costos de ANS para las ordenes son: 3,4,3
"""
#Coordenadas

coorX=[20,30,50,30,45,32] 
coorY=[20,60,60,40,20,40] 

dist=999*np.ones((6,6))

fig1=plt.figure(1)
def paint(num):

    for i in range(num):
        x=coorX[i]
        y=coorY[i]
        plt.plot(x, y, 'ko', label='Nodes')
        textPosX=x; textPosY=y
        offsetX=0.5; offsetY=0
        texto=str(i+1)
        plt.text(textPosX + offsetX, textPosY + offsetY, texto, rotation=0, size=10)
 
    for i in range(num):
        for j in range(num):
            dij= (abs(coorX[i]-coorX[j] )+abs( coorY[i]-coorY[j]))
            #dist[i][j]=dij
            #plt.plot([coorX[i],coorX[j]],[coorY[i],coorY[j]],'k--')        
            if i!=j:
                dist[i][j]=dij
                plt.plot([coorX[i],coorX[j]],[coorY[i],coorY[j]],'k--')


#dist[0][0] = 999


#Conjuntos................................................

#cojunto de habilidades
numHabi = 1
model.S = RangeSet (1, numHabi)

#conjunto de empleados
numEmp = 2
model.E = RangeSet (1, numEmp)

#conjunto de ordenes
numOrd = 3
model.O = RangeSet (1, numOrd)

#conjunto de horas
numHor = 5
model.H = RangeSet (1, numHor)

#conjunto de dias
numDias = 2
model.D = RangeSet(1,numDias)

#Conjunto de sitios
numS = numOrd +1
model.L = RangeSet(1,numS)

paint(numS)

model.costD = Param(model.L, model.L, mutable=True)

i_temp=-1
for i in model.L:
    i_temp=i_temp+1
    j_temp=-1
    for j in model.L:
        j_temp=j_temp+1
        model.costD[i,j]=dist[i_temp][j_temp]


#Parametros--------------------------------------------


#Prioridad de la Orden

model.p = Param(model.O,mutable=True)
for o in model.O:
    model.p[o] = 1

#Costo de ANS

model.costoANS = Param(model.O,model.D,model.H,mutable=True)
for o in model.O:
    for h in model.H:
        for d in model.D:
            model.costoANS[o,d,h] = 0



#Si el empleado tiene la habilidad

model.habEmp = Param(model.E, model.S, mutable= True)

for e in model.E:
    for h in model.S:
        model.habEmp[e,h] = 1
     

#Habilidades que requiere una orden 
        
model.habOrd = Param(model.O, model.S, mutable = True)

for o in model.O:
    for h in model.S:
        model.habOrd[o,h] = 1

#model.habOrd[1,1]=1
#model.habOrd[2,1]=1
#Salario de cada empleado

model.costHorEmp =Param(model.E, mutable=True)

for h in model.E:
    model.costHorEmp[h]= 3

#Hora disponible de los empleados
model.horDisp = Param(model.E,model.D,model.H,mutable = True)
for e in model.E:
    for d in model.D:
        for h in model.H:
            model.horDisp[e,d,h] = 1

                
#Horas en las que se puede cumplir una orden 
model.horOrd = Param(model.O,model.D,model.H,mutable = True)
for o in model.O:
    for d in model.D:
        for h in model.H:
            model.horOrd[o,d,h] = 1
"""
            if d >= 6:
                model.horOrd[o,h,d] = 0
            elif h < 7 or h > 19:
                model.horOrd[o,h,d] = 0
            else:
                model.horOrd[o,h,d] = 1
"""
#Horas limite para una orden
model.horOrdLim = Param(model.O,model.D,model.H,mutable = True)
for o in model.O:
    for d in model.D:
        for h in model.H:
            model.horOrdLim[o,d,h] = 1


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
    return sum(model.x[e,o,d,h]*model.habOrd[o,s]*model.habEmp[e,s] for s in model.S) >= 0.5*sum(model.x[e,o,d,h]*model.habOrd[o,s] for s in model.S)

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
model.f6 = Var()

w = 1/5
w1 = 0.5
w2 = 1/2
w3 = 0.999
w4 = (w3/2)/3
f0 = (-1*sum(model.x[i,j,k,l] for i in model.E for j in model.O for k in model.D for l in model.H))
f2 = sum(model.x[i,j,k,l]*model.costoANS[j,k,l] for i in model.E for j in model.O for k in model.D for l in model.H)
f3 = (-1*sum(model.x[i,j,k,l]*model.p[j] for i in model.E for j in model.O for k in model.D for l in model.H))
f4 = sum(model.x[i,j,k,l]*model.costHorEmp[i] for i in model.E for j in model.O for k in model.D for l in model.H)
f5 = sum(model.y[i,j,k,d,h,h2]*model.costD[i,j] for i in model.L for j in model.L for k in model.E for d in model.D for h in model.H for h2 in model.H)

f6 = (-1*((sum(model.x[i,j,k,l] for i in model.E 
                          for j in model.O 
                          for k in model.D 
                          for l in model.H)**2) /  0.1+((numEmp * sum(
                                                                (sum(model.x[i,j,k,l] for j in model.O 
                                                                                    for k in model.D 
                                                                                    for l in model.H)**2) for i in model.E)))))


#model.obj = Objective(expr = w1*f0 + w*f1 + w*f2 + w*f3 + 0.15*f4,sense = minimize)

model.obj = Objective(expr = (f0*(w3/2) + f2*(w4)+ f3*(w4)+ f4*(w4)+ f5*(1-w3) + f6*(w4)),sense = minimize)
#model.obj = Objective(expr = (f0*(1-w1) + f6*(w1)),sense = minimize)
#model.obj = Objective(expr = (f0*w3 + (1-w3)*f5 ),sense = minimize)
SolverFactory('bonmin', executable="C:/Users/estudiante/Downloads/Couenne-0.3.2-win32-msvc9/Couenne-0.3.2-win32-msvc9/bin/bonmin.exe").solve(model)

#SolverFactory('scip', executable="C:/Users/estudiante/anaconda3/Library/bin/scipampl.exe").solve(model)
#SolverFactory('mindtpy').solve(model, mip_solver='glpk', nlp_solver='ipopt') 
#results = solver.solve(model)☺
#solver_manager = SolverManagerFactory('neos')
#results = solver_manager.solve(model, opt='bonmin')

# =============================================================================
#model.display()
# =============================================================================
valorF0 =value(sum(model.x[i,j,k,l] for i in model.E for j in model.O for k in model.D for l in model.H))
valorF2=value(sum(model.x[i,j,k,l]*model.costoANS[j,k,l] for i in model.E for j in model.O for k in model.D for l in model.H))
valorF3=value(sum(model.x[i,j,k,l]*model.p[j] for i in model.E for j in model.O for k in model.D for l in model.H))
valorF4=value(sum(model.x[i,j,k,l]*model.costHorEmp[i] for i in model.E for j in model.O for k in model.D for l in model.H))
valorF5=value(sum(model.y[i,j,k,d,h,h2]*model.costD[i,j] for i in model.L for j in model.L for k in model.E for d in model.D for h in model.H for h2 in model.H))
valorF6 = value((sum(model.x[i,j,k,l] for i in model.E 
                          for j in model.O 
                          for k in model.D
                          for l in model.H)**2) / (numEmp * sum(
                                                                (sum(model.x[i,j,k,l] for j in model.O 
                                                                                    for k in model.D 
                                                                                    for l in model.H)**2) for i in model.E)))

print("Función 0 Max Ordenes "+ str(valorF0))
print("Función 2 ANS " + str(valorF2))
print("Función 3 Prioridad " +  str(valorF3))
print("Función 4 Costo " +  str(valorF4))
print("Función 5 Distancia " +  str(valorF5))
print("Función 6 Fairness " + str(valorF6))

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
colors = ['b--','g--','r--','c--','y--','w--']
for d in model.D:
    paint(numS) 
    for y in model.O:
        for i in model.E:
            for z in model.H:
                for h in model.H:
                    for l in model.L:
                        for lu in model.L:
                            if value(model.y[l,lu,i,d,z,h]) == 1:                         
                                plt.plot([coorX[l-1],coorX[lu-1]],[coorY[l-1],coorY[lu-1]],colors[i-1])
    plt.title("Dia " + str(d))
    plt.xlabel('Latitud')
    plt.ylabel('Longitud')
    plt.show()                            

