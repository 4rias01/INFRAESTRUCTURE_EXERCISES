import numpy as np
import random  # para generar numeros aleatorios en la matriz
# Desarrollo del punto 2.

"""
def generar_matriz(dim):
    m = [
        [random.randint(1,100) # generada con numeros aleatorios entre 1 y 100
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
    ## Creemos las dos matrices con numeros alatorios de 1000*1000
    # (por pruebitas tripi tripi seran de 3*3)
    TAM = 3
    CHUNK = 1

    #matrices generadas con numpy
    m1np = np.random.randint(1, 100, size=(TAM, TAM))
    m2np = np.random.randint(1, 100, size=(TAM, TAM))

    #imprimimos matrices de numpy
    print("matriz 1:")
    imprimir_matriz(m1np)
    print("matriz 2:")
    imprimir_matriz(m2np)

    #probando multiplicacion con numpy
    resultado_numpy = multiplicacion_numpy(m1np, m2np)
    print("resultado multiplicacion con numpy:")
    imprimir_matriz(resultado_numpy)
    
    """
    #"resultado normal con listas"
    m1 = m1np.tolist()
    m2 = m2np.tolist()
    multiplicacion_clasica_resultado = multiplicacion_clasica(m1, m2)
    print("resultado multiplicacion clasica:")
    imprimir_matriz(multiplicacion_clasica_resultado)
    """
