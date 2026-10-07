import numpy as np
import random  # para generar numeros aleatorios en la matriz
# Desarrollo del punto 2.

def generar_matriz(dim):
    m = [
        [random.randint(1,100) # generada con numeros aleatorios entre 1 y 100
        for _ in range(dim)] 
          for _ in range(dim)]
    return m


def imprimir_matriz(m):
    if not m:
        print("[]")
        return

    ancho = max(len(str(valor)) for fila in m for valor in fila)

    print("[")
    for fila in m:
        linea = "  ".join(f"{valor:>{ancho}}" for valor in fila)
        print(f"  [{linea}]")
    print("]")

def multiplicacion_numpy(m1, m2):
    return np.matmul(m1, m2)

if __name__ == '__main__':
    ## Creemos las dos matrices con numeros alatorios de 1000*1000
    # (por pruebitas tripi tripi seran de 3*3)
    TAM = 3
    CHUNK = 1

    #m1 = generar_matriz(TAM)
    #m2 = generar_matriz(TAM)
    #matrices generadas con numpy
    m1np = np.random.randint(1, 100, size=(TAM, TAM))
    m2np = np.random.randint(1, 100, size=(TAM, TAM))
    #convertimos las matrices de numpy a listas para poder usar la funcion imprimir_matriz
    m1 = m1np.tolist()
    m2 = m2np.tolist()
    print("matriz 1:")
    imprimir_matriz(m1)
    print("matriz 2:")
    imprimir_matriz(m2)
    #multiplicamos las matrices con numpy
    resultado_numpy = multiplicacion_numpy(m1, m2)
    print("resultado de la multiplicacion con numpy:")
    imprimir_matriz(resultado_numpy)
    
