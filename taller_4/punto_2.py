import numpy as np
import time
import random  # para generar numeros aleatorios en la matriz
# Desarrollo del punto 2.

# Funcion generica que imprime la matriz de manera legible
# recibe como argumento una matriz m para conocer sus dimensiones
def imprimir_matriz(m):
    if m.size == 0: #si la matriz esta vacia imprime [], modificado ya que la matriz es generada con numpy.
        print("[]")
        return

    # Calcula el ancho del valor ms grande en la matriz para formatear la salida
    ancho = max(len(str(valor)) for fila in m for valor in fila)

    print("[")
    for fila in m:
        linea = "  ".join(f"{valor:>{ancho}}" for valor in fila)
        print(f"  [{linea}]")
    print("]")

# Funcion de multiplicacion usando la NUMPY, especificamente su funcion de multiplicacion de matrices matmul.
# recibe como argumentos las dos matrices numpy a ser multiplicadas
def multiplicacion_numpy(m1, m2):
    return np.matmul(m1, m2)  # Utiliza la función de multiplicación de matrices de NumPy

# Funcion de multiplicacion clasica de matrices usando bucles tradicionales de python.
# recibe como argumentos las dos matrices a ser multiplicadas.
def multiplicacion_clasica(m1,m2):
    filas_m1 = len(m1) # numero de filas de la matriz 1
    columnas_m1 = len(m1[0]) # numero de columnas de matriz 1
    columnas_m2 = len(m2[0]) # numero de columnas de matriz 1

    # Inicializamos la matriz resultado con ceros
    resultado = [[0 for _ in range(columnas_m2)] for _ in range(filas_m1)]

    # Realizamos la multiplicación de matrices
    for i in range(filas_m1):
        for j in range(columnas_m2):
            for k in range(columnas_m1):
                resultado[i][j] += m1[i][k] * m2[k][j]

    return resultado

# funcion principal main del archivo
if __name__ == '__main__':
    TAM = 1000 # definimos el tamaño de la matriz a generar

    # inicializamos las matrices haciedno uso de numpy
    m1np = np.random.randint(1, 101, size=(TAM, TAM))
    m2np = np.random.randint(1, 101, size=(TAM, TAM))

    # realizamos multiplicacion usando numpy (SIMD) y tomamos tiempos
    print("Iniciando multiplicación con NumPy (SIMD)...")
    inicio = time.perf_counter()
    resultado_numpy = multiplicacion_numpy(m1np, m2np) # almacenamos para hacer verificaciones y comparacion
    dif_numpy = time.perf_counter() - inicio
    print(f"Tiempo NumPy: {dif_numpy:.6f} s")

    # realizamos multiplicacion de manera secuencial y tomamos tiempos
    m1, m2 = m1np.tolist(), m2np.tolist() # convertimos a listas (para poder manipularlas en multiplicacion_clasica)
    print("Iniciando multiplicación secuencial...")
    inicio = time.perf_counter()
    resultado_secuencial = multiplicacion_clasica(m1, m2) # almacenamos para hacer verificaciones y comparacion
    dif_secuencial = time.perf_counter() - inicio
    print(f"Tiempo secuencial: {dif_secuencial:.6f} s")

    # Realizamos una verificacion para ver que ambas coinciden en resultados
    assert np.array_equal(resultado_numpy, resultado_secuencial)
    print("====== RESULTADOS ======")
    print(f"| Numpy: {dif_numpy:.6f} s  | Tradicional: {dif_secuencial:.6f} s |")
    
    # Calculamos la aceleracion:
    print(f"Aceleración: {dif_secuencial / dif_numpy:.2f}x")

    