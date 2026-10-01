import multiprocessing
import random
import time
from pathlib import Path
from collections import Counter
from itertools import islice


# genera los votos de una sola mesa y los va guardando en su archivo,
# un voto por linea
def generar_votos_mesa(contexto, ruta_salida):
    candidatos = contexto[0]
    probabilidades = contexto[1]
    num_votantes = contexto[2]
    with open(ruta_salida, 'w') as f_out:
        for i in range(num_votantes):
            # se escoge un candidato al azar pero respetando las probabilidades
            resultado = random.choices(candidatos, weights=probabilidades, k=1)
            f_out.write(resultado[0] +'\n')


# aca cada mesa se genera en su propio proceso, 
# entonces se hacen todas al tiempo
def generar_votos_paralelo(contexto, rutas_salida):
    candidatos = contexto[0]
    probabilidades = contexto[1]
    num_votantes = contexto[2]
    num_mesas = contexto[3]
    # repartimos los votantes entre las mesas
    votos_por_mesa = num_votantes // num_mesas
    procesos = []
    nuevo_contexto = [candidatos, probabilidades, votos_por_mesa, num_mesas]

    # un proceso por cada archivo de mesa
    for ruta in rutas_salida:
        proceso = multiprocessing.Process(target=generar_votos_mesa,
                                             args=(nuevo_contexto, ruta))
        procesos.append(proceso)

    # primero arrancamos todos y despues esperamos a que terminen
    for proceso in procesos:
        proceso.start()
    for proceso in procesos:
        proceso.join()


# lo mismo que el anterior pero una mesa despues de la otra,
# sirve para comparar los tiempos
def generar_votos_secuencial(contexto, rutas_salida):
    candidatos = contexto[0]
    probabilidades = contexto[1]
    num_votantes = contexto[2]
    num_mesas = contexto[3]
    votos_por_mesa = num_votantes // num_mesas
    nuevo_contexto = [candidatos, probabilidades, votos_por_mesa, num_mesas]

    for ruta in rutas_salida:
        generar_votos_mesa(nuevo_contexto, ruta)


# aca se decide si se generan los votos de las dos formas para comparar,
# o solo en paralelo si los archivos no existen todavia
def generar_votos(contexto, rutas_votos_sec, rutas_votos_par):
    respuesta = input("Quieres realizar la comparación? (S/n): ")
    if (respuesta == "S" or respuesta == "s"):
        # se mide cuanto se demora la version secuencial
        print("Generando votos secuenciales, por favor espere...")
        inicio = time.time()
        generar_votos_secuencial(contexto, rutas_votos_sec)
        fin = time.time()
        tiempo_sec = fin - inicio
        print(f"Tiempo de los votos secuenciales: {tiempo_sec:.2f}\n")

        # y luego la paralela
        print("Generando votos paralelos, por favor espere")
        inicio = time.time()
        generar_votos_paralelo(contexto, rutas_votos_par)
        fin = time.time()
        tiempo_par = fin - inicio
        print(f"Tiempo de los votos paralelos: {tiempo_par:.2f}\n")

        # la aceleracion es simplemente tiempo secuencial / tiempo paralelo
        print(f"La aceleración fue de {(tiempo_sec/tiempo_par):.2f}")
        print("Los votos ya se encuentran disponibles!\n")

    # si no se quiere comparar pero falta algun archivo, se generan en paralelo
    elif not all(Path(a).is_file() for a in rutas_votos_par):
        print("Generando votos por cada mesa...")
        generar_votos_paralelo(contexto, rutas_votos_par)
        print("Los votos ya se encuentran disponibles!\n")

    # si ya estan todos los archivos no hay que hacer nada
    else:
        print("Los votos ya se encuentran disponibles!\n")


# cuenta los votos leyendo las mesas una por una
def contar_votos_secuencial(rutas_entrada):
    resultados_mesas = []
    resultados_finales = Counter()

    for ruta in rutas_entrada:
        with open(ruta, 'r') as f_in:
            # el Counter cuenta cuantas veces aparece cada candidato en la mesa
            contador = Counter(linea.strip() for linea in f_in)
            resultado_mesa = {candidato:votos for candidato, votos in contador.items()}
            resultados_mesas.append(resultado_mesa)

            # se van sumando los votos de la mesa al total
            for candidato, votos in resultado_mesa.items():
                resultados_finales[candidato] += votos

    imprimir_resultados(resultados_mesas, resultados_finales)
    return resultados_finales


# parte del map: cada proceso cuenta los votos de una mesa
def map_function(ruta_entrada):
    with open(ruta_entrada, 'r') as f_in:
        return Counter(linea.strip() for linea in f_in)


# parte del reduce: junta los conteos de todas las mesas en uno solo
def reduce_function(mapped_results):
    total_count = Counter()
    for count in mapped_results:
        for candidato, votos in count.items():
            total_count[candidato] += votos
    return total_count


# conteo en paralelo usando la idea de map reduce
def contar_votos_paralelo(rutas_entrada):
    # el pool reparte las mesas entre los procesos, uno por mesa
    with multiprocessing.Pool(processes=len(rutas_entrada)) as pool:
        resultados = pool.map(map_function, rutas_entrada)   # MAP

    resultado_final = reduce_function(resultados)            # REDUCE
    imprimir_resultados(resultados_mesas=resultados,
                        resultados_finales=resultado_final)
    return resultado_final


# ==================== PRODUCTOR / CONSUMIDOR ====================

def productor_mesa(id_mesa, ruta_entrada, cola, tam_lote):
    """
    Este es el productor, osea una mesa de votacion.
    En vez de contar todo de una, va leyendo la urna por lotes y cada
    vez que cuenta un lote lo manda a la cola. Cuando termina manda un
    None para avisar que ya cerro.
    """
    with open(ruta_entrada, 'r') as f_in:
        while True:
            # islice saca las siguientes tam_lote lineas del archivo
            lote = list(islice(f_in, tam_lote))
            if not lote:                          # ya no hay mas votos
                break
            parcial = Counter(linea.strip() for linea in lote)
            # si la cola esta llena el productor se queda esperando aca
            cola.put((id_mesa, parcial))

    # el centinela, para que el consumidor sepa que esta mesa ya acabo
    cola.put((id_mesa, None))


# imprime como va el conteo en ese momento, los boletines de la registraduria
def imprimir_boletin(num_boletin, acumulado, votos_contados, votos_esperados,
                     mesas_cerradas, num_mesas):
    pct_votos = 100 * votos_contados / votos_esperados
    # porcentaje de cada candidato sobre los votos que van contados
    porcentajes = "  ".join(f"{c} {100 * v / votos_contados:5.2f}%"
                            for c, v in sorted(acumulado.items()))
    print(f"Boletín #{num_boletin:<3}| "
          f"Escrutado: {pct_votos:5.1f}% ({votos_contados:,} votos) | "
          f"Mesas cerradas: {mesas_cerradas}/{num_mesas} | {porcentajes}")


def contar_votos_productor_consumidor(rutas_entrada, votos_esperados,
                                      tam_lote, tam_buffer,
                                      frecuencia_boletin=0.10):
    num_mesas = len(rutas_entrada)

    # la cola que comparten todos, con tamaño maximo para que no se llene la memoria
    cola = multiprocessing.Queue(maxsize=tam_buffer)

    # se crea un productor por cada mesa y se ponen a correr
    productores = [multiprocessing.Process(target=productor_mesa,
                                           args=(i, ruta, cola, tam_lote))
                   for i, ruta in enumerate(rutas_entrada)]
    for p in productores:
        p.start()

    # el consumidor es el proceso principal, como si fuera la registraduria
    resultados_mesas = [Counter() for _ in range(num_mesas)]
    acumulado = Counter()
    votos_contados = 0
    mesas_cerradas = 0
    num_boletin = 0
    # cada cuantos votos se saca un boletin (por defecto cada 10%)
    paso_boletin = max(1, int(votos_esperados * frecuencia_boletin))
    siguiente_boletin = paso_boletin

    print("\n++++++++++ BOLETINES EN VIVO ++++++++++\n")

    # se sigue sacando de la cola hasta que todas las mesas hayan cerrado
    while mesas_cerradas < num_mesas:
        # si la cola esta vacia se queda esperando a que llegue algo
        id_mesa, parcial = cola.get()

        # si llega None es porque una mesa termino
        if parcial is None:
            mesas_cerradas += 1
            print(f"   -> La mesa_{id_mesa} cerró su escrutinio "
                  f"({mesas_cerradas}/{num_mesas})")
            continue

        # se suma el lote a la mesa que lo mando y al total general
        resultados_mesas[id_mesa].update(parcial)
        acumulado.update(parcial)
        votos_contados += sum(parcial.values())

        # cuando se pasa del siguiente porcentaje (10%, 20%, ...) se saca boletin
        if votos_contados >= siguiente_boletin:
            num_boletin += 1
            imprimir_boletin(num_boletin, acumulado, votos_contados,
                             votos_esperados, mesas_cerradas, num_mesas)
            # por si un lote grande se salto varios umbrales de una
            while siguiente_boletin <= votos_contados:
                siguiente_boletin += paso_boletin

    # ya llegaron todos los centinelas, entonces la cola quedo vacia y
    # se puede hacer el join sin que se bloquee
    for p in productores:
        p.join()

    print("\nBOLETÍN FINAL:")
    imprimir_boletin(num_boletin + 1, acumulado, votos_contados,
                     votos_esperados, mesas_cerradas, num_mesas)

    imprimir_resultados(resultados_mesas, acumulado)
    return acumulado


# imprime la tabla con los votos de cada mesa y el total
def imprimir_resultados(resultados_mesas, resultados_finales):
    # los candidatos ordenados para que siempre salgan en el mismo orden
    candidatos = sorted(resultados_finales.keys())

    print("\n++++++++++++ RESULTADOS ++++++++++++\n")

    # encabezado de la tabla
    print(f"{'Mesa':<10}", end="")
    for candidato in candidatos:
        print(f"{candidato:<10}", end="")
    print()

    print("-" * (10 + 10 * len(candidatos)))

    # una fila por mesa
    for i, resultado_mesa in enumerate(resultados_mesas):
        print(f"{'mesa_' + str(i):<10}", end="")

        for candidato in candidatos:
            # si un candidato no saco votos en esa mesa se pone 0
            votos = resultado_mesa.get(candidato, 0)
            print(f"{votos:<10}", end="")

        print()

    print("-" * (10 + 10 * len(candidatos)))

    # fila del total
    print(f"{'TOTAL':<10}", end="")

    for candidato in candidatos:
        print(f"{resultados_finales[candidato]:<10}", end="")

    # el que tenga mas votos gana
    presidente = max(resultados_finales, key=resultados_finales.get)
    print(f"\n\nEL NUEVO PRESIDENTE DE LA REPUBLICA DE COLOMBIA ES {presidente} !!!\n")

if __name__ == '__main__':
    # configuracion de la simulacion
    CANDIDATOS = ['ADLE', 'IC', 'PV']
    PROBABILIDADES = [0.40, 0.40, 0.20]
    NUM_VOTANTES = 10000000
    MESAS_VOTACION = 8
    TAM_LOTE = 100_000      # cuantos votos cuenta una mesa antes de reportar
    TAM_BUFFER = 16         # cuantos reportes caben en la cola como maximo
    contexto = [CANDIDATOS, PROBABILIDADES, NUM_VOTANTES, MESAS_VOTACION]
    rutas_votos_sec = [f"taller_3/mesas/mesa_{i}_sec.txt" for i in range(MESAS_VOTACION)]
    rutas_votos_par = [f"taller_3/mesas/mesa_{i}_par.txt" for i in range(MESAS_VOTACION)]
    # puede que no sea exactamente NUM_VOTANTES por la division entera entre mesas
    votos_esperados = (NUM_VOTANTES // MESAS_VOTACION) * MESAS_VOTACION

    generar_votos(contexto, rutas_votos_sec, rutas_votos_par)

    # 1. conteo normal, una mesa tras otra
    print(f"CONTANDO VOTOS SECUENCIALEMENTE...\n")
    inicio = time.time()
    total_sec = contar_votos_secuencial(rutas_votos_par)
    final = time.time()
    tiempo_sec = final - inicio
    print(f"el tiempo de ejecucíon secuencial fue de {tiempo_sec:.2f}\n")


    # 2. conteo con map reduce
    print(f"CONTANDO VOTOS PARALELAMENTE...\n")
    inicio = time.time()
    total_par = contar_votos_paralelo(rutas_votos_par)
    final = time.time()
    tiempo_par = final - inicio
    print(f"el tiempo de ejecucíon paralelo fue de {tiempo_par:.2f}\n")

    aceleracion = tiempo_sec/tiempo_par
    print(f"La aceleración del programa fue de {aceleracion:.2f}x\n")


    # 3. conteo con productor/consumidor y boletines en vivo
    print(f"CONTANDO VOTOS CON PRODUCTOR/CONSUMIDOR...\n")
    inicio = time.time()
    total_pc = contar_votos_productor_consumidor(rutas_votos_par, votos_esperados,
                                                 TAM_LOTE, TAM_BUFFER)
    final = time.time()
    tiempo_pc = final - inicio
    print(f"el tiempo de ejecucíon productor/consumidor fue de {tiempo_pc:.2f}\n")
    print(f"La aceleración del productor/consumidor fue de {tiempo_sec/tiempo_pc:.2f}x\n")


    # revisamos que las tres formas den lo mismo, si no algo quedo mal
    if total_sec == total_par == total_pc:
        print("Verificación OK: los tres métodos dan el mismo resultado.")
    else:
        print("ERROR: los resultados de los métodos no coinciden.")