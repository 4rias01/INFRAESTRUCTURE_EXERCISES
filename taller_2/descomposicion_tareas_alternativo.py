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
def leer_bloques(cola_entrada, ruta_entrada):
    try:
        with open(ruta_entrada, 'rb') as f_in:
            indice = 0
            while True:
                bloque = f_in.read(TAM_BLOQUE)
                if not bloque:
                    break
                if not bloque.endswith(b'\n'):
                    bloque += f_in.readline()  # completar la última línea
                cola_entrada.put(bloque)
                indice += 1
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {ruta_entrada}")
    finally:
        cola_entrada.put(FIN)


# ---------------- TAREA 2: transformación (replicada) ----------------
def transformar_bloques(cola_entrada, cola_salida):
    while True:
        bloque = cola_entrada.get()
        if bloque is FIN:
            cola_salida.put(FIN)
            break
        lineas = bloque.decode('utf-8').split('\n')
        lineas.pop()  # el bloque termina en '\n' -> último elemento vacío
        resultado = '\n'.join([l.strip().upper() for l in lineas]) + '\n'
        cola_salida.put(resultado.encode('utf-8'))


# ---------------- TAREA 3: escritura ----------------
def escribir_bloques(cola_salida, ruta_salida):
    with open(ruta_salida, 'wb') as f_out:
        while True:
            item = cola_salida.get()
            if item is FIN:
                break
            bloque = item
            f_out.write(bloque)


def procesar_texto_paralelo(ruta_entrada, ruta_salida):
    # maxsize acota la memoria: el lector no se adelanta demasiado
    cola_entrada = multiprocessing.Queue()
    cola_salida = multiprocessing.Queue()

    lector = multiprocessing.Process(
        target=leer_bloques, args=(cola_entrada, ruta_entrada))
    trabajador = multiprocessing.Process(target=transformar_bloques, args=(cola_entrada, cola_salida))
    escritor = multiprocessing.Process(
        target=escribir_bloques, args=(cola_salida, ruta_salida))

    procesos = [lector, trabajador, escritor]
    for p in procesos:
        p.start()
    for p in procesos:
        p.join()


if __name__ == '__main__':
    ruta_entrada = "taller_2/entrada/texto_entrada.txt"
    ruta_salida_sec = "taller_2/salida/texto_salida_secuencial.txt"
    ruta_salida_par = "taller_2/salida/texto_salida_paralelo.txt"

    inicio_sec = time.time()
    procesar_texto_secuencial(ruta_entrada, ruta_salida_sec)
    dif_sec = time.time() - inicio_sec
    print(f"Tiempo total de procesamiento secuencial: {dif_sec:.2f} segundos")

    inicio_par = time.time()
    procesar_texto_paralelo(ruta_entrada, ruta_salida_par)
    dif_par = time.time() - inicio_par
    print(f"Tiempo total de procesamiento paralelo: {dif_par:.2f} segundos")
    print(f"La aceleracion lograda fue de: {dif_sec / dif_par:.2f}")