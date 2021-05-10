import Heuristica
import HeuristicaT
import winsound


def tesE(veces):
    iteraciones = 20
    contador = 0
    hormigas = 12
    while contador < veces:
        f = open('escalabilidad.txt', 'a')
        f.write('\n' + 'Iteraciones: ' + str(iteraciones) + ' Hormigas : ' + str(hormigas))
        f.close()
        Heuristica.heuristica(iteraciones, hormigas)
        HeuristicaT.heuristica(iteraciones, hormigas)
        contador += 1


    while True:
        duration = 1000  # milliseconds
        freq = 440  # Hz
        winsound.Beep(freq, duration)

tesE(5)
