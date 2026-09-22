import time
import queue
from concurrent.futures import ThreadPoolExecutor

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

def procesar_texto_paralelo(ruta_entrada, ruta_salida, ex):
    fila_inicio_limpiar = queue.Queue()
    fila_limpiar_agrandar = queue.Queue()
    

    FIN = object()

    def etapa1():
        try:
            with open(ruta_entrada, 'r') as f_in:
                for linea in f_in: 
                    fila_inicio_limpiar.put(linea.strip())
                fila_inicio_limpiar.put(FIN)
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo {ruta_entrada}")

    def etapa2():
        while True:
            linea = fila_inicio_limpiar.get()
            if linea is FIN:
                fila_limpiar_agrandar.put(FIN)
                break 
            fila_limpiar_agrandar.put(linea.upper())

    def etapa3():
        try:
            with open(ruta_salida, 'w') as f_out:
                while True:
                    linea = fila_limpiar_agrandar.get()
                    if linea is FIN:
                        break
                    f_out.write(linea + '\n')
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo {ruta_entrada}")

    etapas = [etapa1, etapa2, etapa3]
    futuros = [ex.submit(etapa) for etapa in etapas]

    for f in futuros:
        f.result()


if __name__ == '__main__':
    ruta_entrada = "taller_2/entrada/texto_entrada.txt"
    ruta_salida_sec = "taller_2/salida/texto_salida_secuencial.txt"
    ruta_salida_par = "taller_2/salida/texto_salida_paralelo.txt"

    inicio_sec = time.time()
    procesar_texto_secuencial(ruta_entrada, ruta_salida_sec)
    fin_sec = time.time()
    dif_sec = fin_sec - inicio_sec

    print(f"Tiempo total de procesamiento secuencial: {dif_sec:.2f} segundos")
    print(f"Archivo procesado secuencialmente guardado en {ruta_salida_sec}")


    inicio_par = time.time()
    with ThreadPoolExecutor(max_workers=3) as ex:
        procesar_texto_paralelo(ruta_entrada, ruta_salida_par, ex)
    fin_par = time.time()
    dif_par = fin_par - inicio_par

    print(f"Tiempo total de procesamiento paralelo: {dif_par:.2f} segundos")
    print(f"Archivo procesado secuencialmente guardado en {ruta_salida_par}")

    print(f"La aceleracion lograda fue de: {dif_sec/dif_par}")