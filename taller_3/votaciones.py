import multiprocessing
import random
import time
from pathlib import Path
from collections import Counter


def generar_votos_mesa(contexto, ruta_salida):
    candidatos = contexto[0]
    probabilidades = contexto[1]
    num_votantes = contexto[2]
    with open(ruta_salida, 'w') as f_out:
        for i in range(num_votantes):
            resultado = random.choices(candidatos, weights=probabilidades, k=1)
            f_out.write(resultado[0] +'\n')


def generar_votos_paralelo(contexto, rutas_salida):
    candidatos = contexto[0]
    probabilidades = contexto[1]
    num_votantes = contexto[2]
    num_mesas = contexto[3]
    votos_por_mesa = num_votantes // num_mesas
    procesos = []
    nuevo_contexto = [candidatos, probabilidades, votos_por_mesa, num_mesas]

    for ruta in rutas_salida:
        proceso = multiprocessing.Process(target=generar_votos_mesa, 
                                             args=(nuevo_contexto, ruta))
        procesos.append(proceso)

    for proceso in procesos:
        proceso.start()
    for proceso in procesos:
        proceso.join()


def generar_votos_secuencial(contexto, rutas_salida):
    candidatos = contexto[0]
    probabilidades = contexto[1]
    num_votantes = contexto[2]
    num_mesas = contexto[3]
    votos_por_mesa = num_votantes // num_mesas
    nuevo_contexto = [candidatos, probabilidades, votos_por_mesa, num_mesas]

    for ruta in rutas_salida:
        generar_votos_mesa(nuevo_contexto, ruta)


def generar_votos(contexto, rutas_votos_sec, rutas_votos_par):   
    respuesta = input("Quieres realizar la comparación? (S/n): ")
    if (respuesta == "S" or respuesta == "s"):
        print("Generando votos secuenciales, por favor espere...")
        inicio = time.time()
        generar_votos_secuencial(contexto, rutas_votos_sec)
        fin = time.time()
        tiempo_sec = fin - inicio
        print(f"Tiempo de los votos secuenciales: {tiempo_sec:.2f}\n")

        print("Generando votos paralelos, por favor espere")
        inicio = time.time()
        generar_votos_paralelo(contexto, rutas_votos_par)
        fin = time.time()
        tiempo_par = fin - inicio
        print(f"Tiempo de los votos paralelos: {tiempo_par:.2f}\n")

        print(f"La aceleración fue de {(tiempo_sec/tiempo_par):.2f}")
        print("Los votos ya se encuentran disponibles!\n")
    elif not all(Path(a).is_file() for a in rutas_votos_par):
        print("Generando votos por cada mesa...")
        generar_votos_paralelo(contexto, rutas_votos_par)
        print("Los votos ya se encuentran disponibles!\n")
    else: 
        print("Los votos ya se encuentran disponibles!\n")


def contar_votos_mesa(ruta_entrada):
    with open(ruta_entrada, 'r') as f_in:
        contador = Counter(linea.strip() for linea in f_in)
        resultados = {candidato:votos for candidato, votos in contador.items()}
    return resultados

def contar_votos_secuencial1(rutas_entrada):
    resultados_mesas = []
    resultados_finales = Counter()
    for ruta in rutas_entrada:
        resultado_mesa = contar_votos_mesa(ruta)
        resultados_mesas.append(resultado_mesa)

        for candidato, votos in resultado_mesa.items():
            resultados_finales[candidato] += votos

    print("++++++++++++ RESULTADOS ++++++++++++")
    for i in range(len(resultados_mesas)):
        print(f"mesa_{i}: {resultados_mesas[i]}")
    print(f"resultados finales: {resultados_finales}")

def contar_votos_secuencial(rutas_entrada):
    resultados_mesas = []
    resultados_finales = Counter()

    for ruta in rutas_entrada:
        resultado_mesa = contar_votos_mesa(ruta)
        resultados_mesas.append(resultado_mesa)

        for candidato, votos in resultado_mesa.items():
            resultados_finales[candidato] += votos

    # Obtener todos los candidatos
    candidatos = sorted(resultados_finales.keys())

    print("\n++++++++++++ RESULTADOS ++++++++++++\n")

    # Encabezado
    print(f"{'Mesa':<10}", end="")
    for candidato in candidatos:
        print(f"{candidato:<10}", end="")
    print()

    # Separador
    print("-" * (10 + 10 * len(candidatos)))

    # Resultados de cada mesa
    for i, resultado_mesa in enumerate(resultados_mesas):
        print(f"{'mesa_' + str(i):<10}", end="")

        for candidato in candidatos:
            votos = resultado_mesa.get(candidato, 0)
            print(f"{votos:<10}", end="")

        print()

    # Separador
    print("-" * (10 + 10 * len(candidatos)))

    # Resultados finales
    print(f"{'TOTAL':<10}", end="")

    for candidato in candidatos:
        print(f"{resultados_finales[candidato]:<10}", end="")

    print()


if __name__ == '__main__':
    CANDIDATOS = ['ADLE', 'IC', 'PV']
    PROBABILIDADES = [0.40, 0.40, 0.20]
    NUM_VOTANTES = 10000000
    MESAS_VOTACION = 8
    contexto = [CANDIDATOS, PROBABILIDADES, NUM_VOTANTES, MESAS_VOTACION]
    rutas_votos_sec = [f"taller_3/salida/mesas/mesa_{i}_sec.txt" for i in range(MESAS_VOTACION)]
    rutas_votos_par = [f"taller_3/salida/mesas/mesa_{i}_par.txt" for i in range(MESAS_VOTACION)]

    generar_votos(contexto, rutas_votos_sec, rutas_votos_par)
    contar_votos_secuencial(rutas_votos_par)