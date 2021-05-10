import ejecucion_gurobi
import Heuristica
import EscenarioAleatorio
import winsound


def test(it):

    f = open('resultados.txt', 'w')
    f.write('Modelo exacto' + '\t' + '\t' + '\t' + 'Heuristica' + '\n' + 'FO' + '\t' + 'Ordenes' + '\t' + 'Tiempo'+ '\t' + 'FO' + '\t' + 'Ordenes' + '\t'+'Tiempo')
    f.close()
    for i in range(it):
        iteraciones = 10
        f = open('resultados.txt', 'a')
        f.write('\n' + 'Iteración: ' + str(i))
        f.close()
        EscenarioAleatorio.escenarioAleatorio(2, 42, 3, 0.05, 0.2)
        ejecucion_gurobi.ejecucion_gurobi()
        while iteraciones < 100:
            hormigas = 10
            while hormigas < 100:
                f = open('resultados.txt', 'a')
                f.write('\n' + 'hormigas: ' + str(hormigas) + ' iteraciones:' + str(iteraciones))
                f.close()
                for i in range(20):
                    Heuristica.heuristica(iteraciones,hormigas)
                hormigas +=10
            iteraciones += 10

    while True:
        duration = 1000  # milliseconds
        freq = 440  # Hz
        winsound.Beep(freq, duration)

test(30)