from threading import Thread #importamos libreria de threading para hacer uso de los hilos.
import random # para generar numeros aleatorios en la matriz
import time # mediciones y comparacion.


# Funcion que genera la matriz de tamaño dim x dim con numeros aleatorios entre 1 y 100.
# recibe como argumento la dimension deseada en la matriz a generar.
def generar_matriz(dim):
    m = [[random.randint(1,100) # generada con numeros aleatorios entre 1 y 100
          for _ in range(dim)] 
          for _ in range(dim)]
    return m

# Funcion generica que imprime la matriz de manera legible
# recibe como argumento una matriz m para conocer sus dimensiones
def imprimir_matriz(m):
    if not m: #si la matriz esta vacia, imprime []
        print("[]")
        return

    # Calcula el ancho del valor ms grande en la matriz para formatear la salida
    ancho = max(len(str(valor)) for fila in m for valor in fila)

    print("[")
    for fila in m:
        linea = "  ".join(f"{valor:>{ancho}}" for valor in fila)
        print(f"  [{linea}]")
    print("]")


# funcion de suma de matriz secuencial, recibe la matriz y los indices de inicio y fin de filas y columnas a sumar.
# este sencillamente recorre toda la matriz posicion a posicion y va sumand los elementos de manera acumulativa.
def sumar_matriz_secuencial(m, fil_inicio, fil_final, col_inicio, col_final):
    total = 0 # inicializamos variable acumuladora como un 0.
    for i in range (fil_inicio, fil_final): #recorremos filas
        for j in range (col_inicio, col_final): #recorremos columnas
            total += m[i][j] # sumamos elemento de cada posicion a la variable acumuladora
    return total

# funcion de suma por BLOQUE, usada en la implementacion de SMP, recibe la matriz y los indices de inicio y fin de 
# filas y columnas a sumar ademas de un arreglo donde se guardara el resultado y el indice donde se guardara.
# resultados es una lista donde cada hilo guardara su resultado parcial.
def sumar_bloque(m, fil_inicio, fil_final, col_inicio, col_final, resultados, idx):
    resultados[idx] = sumar_matriz_secuencial(m, fil_inicio, fil_final, col_inicio, col_final)

# Suma de matriz aplicando SMP, recibe la matriz y el tamaño de los bloques a sumar, divide la matriz en bloques y
#  crea un hilo para cada bloque. recibe una matriz y un tamaño de bloque (chunksize).
def sumar_matriz_smp(m, chunksize): 
    num_bloques_filas = len(m) // chunksize # cantidad de filas de bloques
    num_bloques_columnas = len(m[0]) // chunksize # cantidad de columnas de bloques
    resultados = [0] * (num_bloques_filas * num_bloques_columnas) # inicializamos lista de resultados parciales para cada hilo
    hilos = [] # lista que almacenara los hilos creados

    # recorremos toda esta matriz de bloques
    for i in range(num_bloques_filas):
        for j in range(num_bloques_columnas):
            idx = i * num_bloques_columnas + j # Asignamos un indice para cada hilo
            # creamos un hilo para cada bloque y le pasamos la funcion sumar_bloque con los indices de inicio y fin de filas y columnas
            t = Thread(
                target=sumar_bloque,
                args=(m, i * chunksize, (i + 1) * chunksize,
                      j * chunksize, (j + 1) * chunksize,
                      resultados, idx),
            )
            hilos.append(t) # agregamos el hilo creado a la lista de hilos
            t.start() # iniciamos cada hilo.

    # despues de creados e iniciados todos los hilos, con join() esperamos a que todos terminen
    #  antes de combinar los resultados parciales.
    for t in hilos:
        t.join()          # esperar a que todos terminen antes de combinar

    return sum(resultados) # retornamos la suma de todos los resultados parciales


# funcion principal main del archivo
if __name__ == '__main__':
    #se define el tamaño de la matriz en 1000, y el tamaño de cada bloque/chunk en 100. (quedandonos en total 10 bloques.)
    TAM = 1000 
    CHUNK = 100
    m1 = generar_matriz(TAM) # generamos la matriz

    # invocamos la suma secuencial y tomamos los tiempos 
    inicio = time.perf_counter()
    resultado_sec = sumar_matriz_secuencial(m1, 0, TAM, 0, TAM)
    dif_sec = time.perf_counter() - inicio
    # invoamos la suma paralela usando smp y tomamos los tiempos
    inicio = time.perf_counter()
    resultado_smp = sumar_matriz_smp(m1, CHUNK)
    dif_smp = time.perf_counter() - inicio

    # Realizamos una verificacion para ver que ambas sumas coinciden en resultados
    assert resultado_sec == resultado_smp   
    print("====== RESULTADOS ======")
    print(f"Secuencial: {dif_sec:.6f} s | SMP: {dif_smp:.6f} s")

    # calculamos la aceleracion: 
    aceleracion = dif_sec/dif_smp
    print(f"\nLa aceleración usando SMP fue de: {aceleracion}x")
