import os
import time
import multiprocessing


FIN = None
TAM_BLOQUE = 4 * 1024 * 1024  # ~4 MB por bloque (unas 60-70k líneas)


def procesar_texto_secuencial(ruta_entrada, ruta_salida):
    """Procesa el archivo de texto secuencialmente."""
    try:
        with open(ruta_entrada, 'r') as f_in, open(ruta_salida, 'w') as f_out:
            for linea in f_in:
                linea_limpia = linea.strip()
                linea_mayusculas = linea_limpia.upper()
                f_out.write(linea_mayusculas + '\n')
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {ruta_entrada}")


# ---------------- TAREA 1: lectura ----------------
def leer_bloques(cola_entrada, ruta_entrada, n_trabajadores):
    """Lee el archivo en bloques que terminan en un salto de línea completo.
    Envía bytes (no listas de str): serializar bytes es casi una copia de memoria.
    Cada bloque lleva su índice para que el escritor pueda reordenarlos."""
    try:
        with open(ruta_entrada, 'rb') as f_in:
            indice = 0
            while True:
                bloque = f_in.read(TAM_BLOQUE)
                if not bloque:
                    break
                if not bloque.endswith(b'\n'):
                    bloque += f_in.readline()  # completar la última línea
                cola_entrada.put((indice, bloque))
                indice += 1
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {ruta_entrada}")
    finally:
        for _ in range(n_trabajadores):  # un FIN por trabajador
            cola_entrada.put(FIN)


# ---------------- TAREA 2: transformación (replicada) ----------------
def transformar_bloques(cola_entrada, cola_salida):
    """Varias copias de esta tarea corren en paralelo, cada una sobre bloques
    distintos: descomposición de datos dentro de la etapa de transformación."""
    while True:
        item = cola_entrada.get()
        if item is FIN:
            cola_salida.put(FIN)
            break
        indice, bloque = item
        lineas = bloque.decode('utf-8').split('\n')
        lineas.pop()  # el bloque termina en '\n' -> último elemento vacío
        resultado = '\n'.join([l.strip().upper() for l in lineas]) + '\n'
        cola_salida.put((indice, resultado.encode('utf-8')))


# ---------------- TAREA 3: escritura ----------------
def escribir_bloques(cola_salida, ruta_salida, n_trabajadores):
    """Los bloques pueden llegar desordenados (los trabajadores no terminan a la
    vez), así que se guardan en un diccionario y se escriben en orden."""
    pendientes = {}
    siguiente = 0
    fines = 0
    with open(ruta_salida, 'wb') as f_out:
        while fines < n_trabajadores:
            item = cola_salida.get()
            if item is FIN:
                fines += 1
                continue
            indice, bloque = item
            pendientes[indice] = bloque
            while siguiente in pendientes:
                f_out.write(pendientes.pop(siguiente))
                siguiente += 1


def procesar_texto_paralelo(ruta_entrada, ruta_salida, n_trabajadores):
    # maxsize acota la memoria: el lector no se adelanta demasiado
    cola_entrada = multiprocessing.Queue(maxsize=2 * n_trabajadores)
    cola_salida = multiprocessing.Queue(maxsize=2 * n_trabajadores)

    lector = multiprocessing.Process(
        target=leer_bloques, args=(cola_entrada, ruta_entrada, n_trabajadores))
    trabajadores = [
        multiprocessing.Process(target=transformar_bloques, args=(cola_entrada, cola_salida))
        for _ in range(n_trabajadores)
    ]
    escritor = multiprocessing.Process(
        target=escribir_bloques, args=(cola_salida, ruta_salida, n_trabajadores))

    procesos = [lector, *trabajadores, escritor]
    for p in procesos:
        p.start()
    for p in procesos:
        p.join()


if __name__ == '__main__':
    ruta_entrada = "taller_2/entrada/texto_entrada.txt"
    ruta_salida_sec = "taller_2/salida/texto_salida_secuencial.txt"
    ruta_salida_par = "taller_2/salida/texto_salida_paralelo.txt"
    # Lector y escritor pasan casi todo el tiempo esperando E/S o la cola,
    # así que conviene un transformador por núcleo (medido: mejor que núcleos-1)
    n_trabajadores = os.cpu_count()

    inicio_sec = time.time()
    procesar_texto_secuencial(ruta_entrada, ruta_salida_sec)
    dif_sec = time.time() - inicio_sec
    print(f"Tiempo total de procesamiento secuencial: {dif_sec:.2f} segundos")

    inicio_par = time.time()
    procesar_texto_paralelo(ruta_entrada, ruta_salida_par, n_trabajadores)
    dif_par = time.time() - inicio_par
    print(f"Tiempo total de procesamiento paralelo "
          f"(1 lector + {n_trabajadores} transformadores + 1 escritor): {dif_par:.2f} segundos")
    print(f"La aceleracion lograda fue de: {dif_sec / dif_par:.2f}")