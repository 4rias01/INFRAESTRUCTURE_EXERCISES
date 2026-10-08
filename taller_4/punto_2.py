import numpy as np
import time
import random  # para generar numeros aleatorios en la matriz
# Desarrollo del punto 2.

"""
def generar_matriz(dim):
    m = [
        [random.randint(1,100) # generada con numeros aleatorios entre 1 y 99
        for _ in range(dim)] 
          for _ in range(dim)]
    return m
"""

def imprimir_matriz(m):
    if m.size == 0: #si la matriz esta vacia, modificado ya que la matriz es generada con np.
        print("[]")
        return
        
    ancho = max(len(str(valor)) for fila in m for valor in fila)

    print("[")
    for fila in m:
        linea = "  ".join(f"{valor:>{ancho}}" for valor in fila)
        print(f"  [{linea}]")
    print("]")

def multiplicacion_numpy(m1, m2):
    return np.matmul(m1, m2)  # Utiliza la función de multiplicación de matrices de NumPy

def multiplicacion_clasica(m1,m2):
    filas_m1 = len(m1)
    columnas_m1 = len(m1[0])
    columnas_m2 = len(m2[0])

    # Inicializamos la matriz resultado con ceros
    resultado = [[0 for _ in range(columnas_m2)] for _ in range(filas_m1)]

    # Realizamos la multiplicación de matrices
    for i in range(filas_m1):
        for j in range(columnas_m2):
            for k in range(columnas_m1):
                resultado[i][j] += m1[i][k] * m2[k][j]

    return resultado

if __name__ == '__main__':
    TAM = 1000

    m1np = np.random.randint(1, 101, size=(TAM, TAM))
    m2np = np.random.randint(1, 101, size=(TAM, TAM))

    print("Iniciando multiplicación con NumPy (SIMD)...")
    inicio = time.perf_counter()
    resultado_numpy = multiplicacion_numpy(m1np, m2np)
    dif_numpy = time.perf_counter() - inicio
    print(f"Tiempo NumPy: {dif_numpy:.6f} s")

    m1, m2 = m1np.tolist(), m2np.tolist()
    print("Iniciando multiplicación secuencial...")
    inicio = time.perf_counter()
    resultado_secuencial = multiplicacion_clasica(m1, m2)
    dif_secuencial = time.perf_counter() - inicio
    print(f"Tiempo secuencial: {dif_secuencial:.6f} s")

    assert np.array_equal(resultado_numpy, resultado_secuencial)
    print(f"Aceleración: {dif_secuencial / dif_numpy:.2f}x")

    
