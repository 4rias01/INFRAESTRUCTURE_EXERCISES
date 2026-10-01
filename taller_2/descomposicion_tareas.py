import time
import multiprocessing #modulo de multiprocesamiento para python


FIN = None # <-- es una bandera de finalización
TAM_BLOQUE = 4 * 1024 * 1024  # ~4 MB por bloque (unas 60-70k líneas)

# Funcion original de procesamiento secuencial de texto.
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
# En este bloque se lee el archivo de entrada en bloques de bytes, se realizan validaciones para no tomar
# una línea a medias y se envía a la cola de entrada para que otro trabajador comience su procesamiento.
#  Se utiliza la bandera FIN para indicar el final del archivo.
def leer_bloques(cola_entrada, ruta_entrada):
    try:
        with open(ruta_entrada, 'rb') as f_in: # rb -> lectura en btyes
            while True:
                bloque = f_in.read(TAM_BLOQUE) # leemos el por tamaño de bloque definido
                if not bloque:
                    break
                if not bloque.endswith(b'\n'): # validacion para no tomar lineas incompletas
                    bloque += f_in.readline()  # completar la última línea
                cola_entrada.put(bloque) # metemos el bloque en la cola de entrada para que otro trabajador lo procese
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {ruta_entrada}")
    finally:
        cola_entrada.put(FIN) # indicamos que ya no quedan mas bloques que procesar.


# ---------------- TAREA 2: transformación (replicada) ----------------
# Esta se encarga de tomar los bloques de la cola de entrada, los procesa, conviertiendo a texto comun, 
# transformando a mayusculas y eliminando espacios en blanco, y luego los envia a la cola de salida para que 
# otro trabajador los escriba en el archivo de salida.
def transformar_bloques(cola_entrada, cola_salida):
    while True:
        bloque = cola_entrada.get() # toma de la cola de entrada
        if bloque is FIN: # comprobacion de bandera de FIN
            cola_salida.put(FIN)
            break
        lineas = bloque.decode('utf-8').split('\n') # dividimos el bloque en líneas
        lineas.pop()  # el bloque termina en '\n' -> último elemento vacío
        resultado = '\n'.join([l.strip().upper() for l in lineas]) + '\n' # procesamos cada línea, eliminando espacios y convirtiendo a mayúsculas
        cola_salida.put(resultado.encode('utf-8')) # metemos el resultado en la cola de salida en bytes para que el escritor pueda comenzar su trabajo


# ---------------- TAREA 3: escritura ----------------
# Esta tarea sencillamente toma los bloques dados en cola_salida y los escribe en el archivo de salida. 
# Aca tambien se utiliza la bandera FIN para indicar que ya no quedan más bloques que escribir (cola_salida vacía).
def escribir_bloques(cola_salida, ruta_salida):
    with open(ruta_salida, 'wb') as f_out: #abrimos el archivo de salida en modo escritura de bytes
        while True:
            bloque = cola_salida.get()  # tomamos un bloque de la cola
            if bloque is FIN:  # validacion de bandera de FIN
                break
            f_out.write(bloque)  # escribimos en el archivo de salida


# Procesamiento paralelo.
# Esta funcion se encarga como tal de orquestar y poner en marcha la implementacion paralela.
# Se crean las colas de entrada y salida mediante los cuales los procesos se van a comunicar,
#  y luego se crean los procesos de lectura, transformación y escritura, cada uno con sus respectivos paarametros.
def procesar_texto_paralelo(ruta_entrada, ruta_salida):
    cola_entrada = multiprocessing.Queue() #creacion de la cola de entrada
    cola_salida = multiprocessing.Queue() #creacion de la cola de salida

    # Se crean los procesos de lectura, transformación y escritura
    lector = multiprocessing.Process(
        target=leer_bloques, args=(cola_entrada, ruta_entrada))
    trabajador = multiprocessing.Process(target=transformar_bloques, args=(cola_entrada, cola_salida))
    escritor = multiprocessing.Process(
        target=escribir_bloques, args=(cola_salida, ruta_salida))

    # Se ponen a trabajar los procesos, y se hace el join para esperar a que todos estos terminen antes de cortar la
    # ejecucion de nuestro programa.
    procesos = [lector, trabajador, escritor]
    for p in procesos:
        p.start()
    for p in procesos:
        p.join()

# bloque main del codigo.
if __name__ == '__main__':
    ruta_entrada = r"C:\Users\HP\Desktop\infra\INFRAESTRUCTURE_EXERCISES\taller_2\entrada\texto_entrada.txt"
    ruta_salida_sec = r"C:\Users\HP\Desktop\infra\INFRAESTRUCTURE_EXERCISES\taller_2\salida\texto_salida_secuencial.txt"
    ruta_salida_par = r"C:\Users\HP\Desktop\infra\INFRAESTRUCTURE_EXERCISES\taller_2\salida\texto_salida_paralelo.txt"

    inicio_sec = time.time()
    procesar_texto_secuencial(ruta_entrada, ruta_salida_sec)
    dif_sec = time.time() - inicio_sec
    print(f"Tiempo total de procesamiento secuencial: {dif_sec:.2f} segundos")

    inicio_par = time.time()
    procesar_texto_paralelo(ruta_entrada, ruta_salida_par)
    dif_par = time.time() - inicio_par
    print(f"Tiempo total de procesamiento paralelo: {dif_par:.2f} segundos")
    print(f"La aceleracion lograda fue de: {dif_sec / dif_par:.2f}")