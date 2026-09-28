import time
import multiprocessing

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



def leer_lineas(cola_entrada, ruta_entrada):
    try:
        with open(ruta_entrada, 'r') as f_in:
            bloque = []
            for linea in f_in:
                bloque.append(linea.strip())
                if len(bloque) == TAM_BLOQUE:
                    cola_entrada.put(bloque)
                    bloque = []  # lista nueva, no .clear()
            if bloque:  # las líneas que sobran al final
                cola_entrada.put(bloque)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {ruta_entrada}")
    finally:
        cola_entrada.put(FIN)


def transformar_lineas(cola_entrada, cola_salida):
    while True:
        bloque = cola_entrada.get()
        if bloque is FIN:
            cola_salida.put(FIN)
            break
        cola_salida.put([linea.upper() for linea in bloque])


def escribir_lineas(cola_salida, ruta_salida):
    with open(ruta_salida, 'w') as f_out:
        while True:
            bloque = cola_salida.get()
            if bloque is FIN:
                break
            f_out.write('\n'.join(bloque) + '\n')

if __name__ == '__main__':
    ruta_entrada = "taller_2/entrada/texto_entrada.txt"
    ruta_salida_sec = "taller_2/salida/texto_salida_secuencial.txt"
    ruta_salida_par = "taller_2/salida/texto_salida_paralelo.txt"

    cola_lectura = multiprocessing.Queue()
    cola_transformación = multiprocessing.Queue()


    inicio_sec = time.time()
    procesar_texto_secuencial(ruta_entrada, ruta_salida_sec)
    fin_sec = time.time()
    dif_sec = fin_sec - inicio_sec

    print(f"Tiempo total de procesamiento secuencial: {dif_sec:.2f} segundos")
    print(f"Archivo procesado secuencialmente guardado en {ruta_salida_sec}")


    proceso_leer = multiprocessing.Process(target=leer_lineas, args=(cola_lectura, ruta_entrada))
    proceso_transformar = multiprocessing.Process(target=transformar_lineas, args=(cola_lectura, cola_transformación))
    proceso_escribir = multiprocessing.Process(target=escribir_lineas, args=(cola_transformación, ruta_salida_par))
    
    inicio_par = time.time()

    proceso_leer.start()
    proceso_transformar.start()
    proceso_escribir.start()

    proceso_leer.join()
    proceso_transformar.join()
    proceso_escribir.join()

    fin_par = time.time()
    dif_par = fin_par - inicio_par

    print(f"Tiempo total de procesamiento paralelo: {dif_par:.2f} segundos")
    print(f"Archivo procesado paralelamente guardado en {ruta_salida_par}")

    print(f"La aceleracion lograda fue de: {dif_sec/dif_par}")