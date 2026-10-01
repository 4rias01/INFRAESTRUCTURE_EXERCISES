import time
import multiprocessing
import os


FIN = None
TAM_BLOQUE = 60000


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



def leer_lineas(cola_entrada, ruta_entrada, n_workers):
    try:
        indice = 0
        with open(ruta_entrada, 'r') as f_in:
            bloque = []
            for linea in f_in:
                bloque.append(linea)
                if len(bloque) == TAM_BLOQUE:
                    cola_entrada.put((indice, bloque))
                    bloque = []  # lista nueva, no .clear()
                    indice += 1
            if bloque:  # las líneas que sobran al final
                cola_entrada.put((indice, bloque))
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {ruta_entrada}")
    finally:
        for _ in range(n_workers):
            cola_entrada.put(FIN)


def transformar_lineas(cola_entrada, cola_salida):
    while True:
        item = cola_entrada.get()
        if item is FIN:
            cola_salida.put(FIN)
            break
        indice, bloque = item
        lineas = [linea.strip().upper() for linea in bloque]
        cola_salida.put((indice, lineas))


def escribir_lineas(cola_salida, ruta_salida, n_trabajadores):
    """Los bloques pueden llegar desordenados (los trabajadores no terminan a la
    vez), así que se guardan en un diccionario y se escriben en orden."""
    pendientes = {}
    siguiente = 0
    fines = 0
    with open(ruta_salida, 'w') as f_out:
        while fines < n_trabajadores:
            item = cola_salida.get()
            if item is FIN:
                fines += 1
                continue
            indice, bloque = item
            pendientes[indice] = bloque
            while siguiente in pendientes:
                bloque = pendientes[siguiente]
                f_out.write('\n'.join(linea for linea in bloque) + '\n')
                siguiente += 1


def procesar_texto_paralelo(ruta_entrada, ruta_salida, n_workers):
    # maxsize acota la memoria: el lector no se adelanta demasiado
    cola_lectura = multiprocessing.Queue(maxsize=2 * n_workers)
    cola_transformación = multiprocessing.Queue(maxsize=2 * n_workers)

    proceso_leer = multiprocessing.Process(target=leer_lineas, args=(cola_lectura, ruta_entrada, n_workers))
    procesos_transformardores = [
        multiprocessing.Process(target=transformar_lineas, args=(cola_lectura, cola_transformación))
        for _ in range(n_workers)
    ]
    proceso_escribir = multiprocessing.Process(target=escribir_lineas, args=(cola_transformación, ruta_salida, n_workers))
        
    procesos = [proceso_leer, *procesos_transformardores, proceso_escribir]
    for p in procesos:
        p.start()
    for p in procesos:
        p.join()


if __name__ == '__main__':
    ruta_entrada = "taller_2/entrada/texto_entrada.txt"
    ruta_salida_sec = "taller_2/salida/texto_salida_secuencial.txt"
    ruta_salida_par = "taller_2/salida/texto_salida_paralelo.txt"
    trabajadores = os.cpu_count()


    inicio_sec = time.time()
    procesar_texto_secuencial(ruta_entrada, ruta_salida_sec)
    fin_sec = time.time()
    dif_sec = fin_sec - inicio_sec

    print(f"Tiempo total de procesamiento secuencial: {dif_sec:.2f} segundos")
    print(f"Archivo procesado secuencialmente guardado en {ruta_salida_sec}")


    
    inicio_par = time.time()
    procesar_texto_paralelo(ruta_entrada, ruta_salida_par, trabajadores)
    fin_par = time.time()
    dif_par = fin_par - inicio_par

    print(f"Tiempo total de procesamiento paralelo: {dif_par:.2f} segundos")
    print(f"Archivo procesado paralelamente guardado en {ruta_salida_par}")

    print(f"La aceleracion lograda fue de: {dif_sec/dif_par}")