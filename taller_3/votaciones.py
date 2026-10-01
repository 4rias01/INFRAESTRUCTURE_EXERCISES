import multiprocessing
import random
import time
from pathlib import Path
from collections import Counter
from itertools import islice


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


def contar_votos_secuencial(rutas_entrada):
    resultados_mesas = []
    resultados_finales = Counter()

    for ruta in rutas_entrada:
        with open(ruta, 'r') as f_in:
            contador = Counter(linea.strip() for linea in f_in)
            resultado_mesa = {candidato:votos for candidato, votos in contador.items()}
            resultados_mesas.append(resultado_mesa)

            for candidato, votos in resultado_mesa.items():
                resultados_finales[candidato] += votos

    imprimir_resultados(resultados_mesas, resultados_finales)
    return resultados_finales


def map_function(ruta_entrada):
    with open(ruta_entrada, 'r') as f_in:
        return Counter(linea.strip() for linea in f_in)


def reduce_function(mapped_results):
    total_count = Counter()
    for count in mapped_results:
        for candidato, votos in count.items():
            total_count[candidato] += votos
    return total_count


def contar_votos_paralelo(rutas_entrada):
    with multiprocessing.Pool(processes=len(rutas_entrada)) as pool:
        resultados = pool.map(map_function, rutas_entrada)   # MAP

    resultado_final = reduce_function(resultados)            # REDUCE
    imprimir_resultados(resultados_mesas=resultados,
                        resultados_finales=resultado_final)
    return resultado_final


# ==================== PRODUCTOR / CONSUMIDOR ====================

def productor_mesa(id_mesa, ruta_entrada, cola, tam_lote):
    """
    PRODUCTOR: una mesa de votación.
    Escruta su urna por lotes de `tam_lote` votos y envía el conteo
    parcial de cada lote a la cola. Al terminar envía un centinela.
    """
    with open(ruta_entrada, 'r') as f_in:
        while True:
            lote = list(islice(f_in, tam_lote))   # siguientes tam_lote líneas
            if not lote:                          # se acabó el archivo
                break
            parcial = Counter(linea.strip() for linea in lote)
            cola.put((id_mesa, parcial))          # se bloquea si el buffer está lleno

    cola.put((id_mesa, None))                     # CENTINELA: "esta mesa cerró"


def imprimir_boletin(num_boletin, acumulado, votos_contados, votos_esperados,
                     mesas_cerradas, num_mesas):
    pct_votos = 100 * votos_contados / votos_esperados
    porcentajes = "  ".join(f"{c} {100 * v / votos_contados:5.2f}%"
                            for c, v in sorted(acumulado.items()))
    print(f"Boletín #{num_boletin:<3}| "
          f"Escrutado: {pct_votos:5.1f}% ({votos_contados:,} votos) | "
          f"Mesas cerradas: {mesas_cerradas}/{num_mesas} | {porcentajes}")


def contar_votos_productor_consumidor(rutas_entrada, votos_esperados,
                                      tam_lote, tam_buffer,
                                      frecuencia_boletin=0.10):
    num_mesas = len(rutas_entrada)

    # Buffer ACOTADO compartido entre productores y consumidor
    cola = multiprocessing.Queue(maxsize=tam_buffer)

    # --- Lanzar los PRODUCTORES (un proceso por mesa) ---
    productores = [multiprocessing.Process(target=productor_mesa,
                                           args=(i, ruta, cola, tam_lote))
                   for i, ruta in enumerate(rutas_entrada)]
    for p in productores:
        p.start()

    # --- CONSUMIDOR: la Registraduría (el proceso principal) ---
    resultados_mesas = [Counter() for _ in range(num_mesas)]
    acumulado = Counter()
    votos_contados = 0
    mesas_cerradas = 0
    num_boletin = 0
    paso_boletin = max(1, int(votos_esperados * frecuencia_boletin))
    siguiente_boletin = paso_boletin

    print("\n++++++++++ BOLETINES EN VIVO ++++++++++\n")

    # Consumir hasta recibir un centinela por cada mesa
    while mesas_cerradas < num_mesas:
        id_mesa, parcial = cola.get()             # se bloquea si la cola está vacía

        if parcial is None:                       # centinela
            mesas_cerradas += 1
            print(f"   -> La mesa_{id_mesa} cerró su escrutinio "
                  f"({mesas_cerradas}/{num_mesas})")
            continue

        resultados_mesas[id_mesa].update(parcial)
        acumulado.update(parcial)
        votos_contados += sum(parcial.values())

        # Publicar un boletín cada vez que se cruza un umbral (10%, 20%, ...)
        if votos_contados >= siguiente_boletin:
            num_boletin += 1
            imprimir_boletin(num_boletin, acumulado, votos_contados,
                             votos_esperados, mesas_cerradas, num_mesas)
            while siguiente_boletin <= votos_contados:
                siguiente_boletin += paso_boletin

    # Todos los centinelas llegaron -> la cola está vacía, se puede hacer join
    for p in productores:
        p.join()

    print("\nBOLETÍN FINAL:")
    imprimir_boletin(num_boletin + 1, acumulado, votos_contados,
                     votos_esperados, mesas_cerradas, num_mesas)

    imprimir_resultados(resultados_mesas, acumulado)
    return acumulado


def imprimir_resultados(resultados_mesas, resultados_finales):
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

    presidente = max(resultados_finales, key=resultados_finales.get)
    print(f"\n\nEL NUEVO PRESIDENTE DE LA REPUBLICA DE COLOMBIA ES {presidente} !!!\n")

if __name__ == '__main__':
    CANDIDATOS = ['ADLE', 'IC', 'PV']
    PROBABILIDADES = [0.40, 0.40, 0.20]
    NUM_VOTANTES = 10000000
    MESAS_VOTACION = 8
    TAM_LOTE = 100_000      # votos por cada reporte parcial de una mesa
    TAM_BUFFER = 16         # capacidad máxima de la cola (buffer acotado)
    contexto = [CANDIDATOS, PROBABILIDADES, NUM_VOTANTES, MESAS_VOTACION]
    rutas_votos_sec = [f"taller_3/salida/mesas/mesa_{i}_sec.txt" for i in range(MESAS_VOTACION)]
    rutas_votos_par = [f"taller_3/salida/mesas/mesa_{i}_par.txt" for i in range(MESAS_VOTACION)]
    votos_esperados = (NUM_VOTANTES // MESAS_VOTACION) * MESAS_VOTACION

    generar_votos(contexto, rutas_votos_sec, rutas_votos_par)

    print(f"GENERANDO VOTACIONES SECUENCIALES...\n")
    inicio = time.time()
    total_sec = contar_votos_secuencial(rutas_votos_par)
    final = time.time()
    tiempo_sec = final - inicio
    print(f"el tiempo de ejecucíon secuencial fue de {tiempo_sec:.2f}\n")


    print(f"GENERANDO VOTACIONES PARALELAS...\n")
    inicio = time.time()
    total_par = contar_votos_paralelo(rutas_votos_par)
    final = time.time()
    tiempo_par = final - inicio
    print(f"el tiempo de ejecucíon paralelo fue de {tiempo_par:.2f}\n")

    aceleracion = tiempo_sec/tiempo_par
    print(f"La aceleración del programa fue de {aceleracion:.2f}x\n")


    print(f"GENERANDO VOTACIONES PRODUCTOR/CONSUMIDOR...\n")
    inicio = time.time()
    total_pc = contar_votos_productor_consumidor(rutas_votos_par, votos_esperados,
                                                 TAM_LOTE, TAM_BUFFER)
    final = time.time()
    tiempo_pc = final - inicio
    print(f"el tiempo de ejecucíon productor/consumidor fue de {tiempo_pc:.2f}\n")
    print(f"La aceleración del productor/consumidor fue de {tiempo_sec/tiempo_pc:.2f}x\n")


    # Verificación: los tres métodos deben dar exactamente el mismo resultado
    if total_sec == total_par == total_pc:
        print("Verificación OK: los tres métodos dan el mismo resultado.")
    else:
        print("ERROR: los resultados de los métodos no coinciden.")