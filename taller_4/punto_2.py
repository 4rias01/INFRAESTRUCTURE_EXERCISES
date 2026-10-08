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

# Funcion que multiplica dos matrices de NUMPY
def multiplicacion_numpy(m1, m2):
    return np.matmul(m1, m2)  # Utiliza la función de multiplicación de matrices de NumPy

#apuntes de recorderis: la multiplicacion de matrices se hace fila*columna y se suman
# Es decir, para la matriz de resultado de tamaño m x m, en su posicion m[i][j], se sacara con:
# fila [i] de m1 POR la columna [j] de m2.
def multiplicacion_tradicional(m1, m2):
    m1_aux = m1.tolist()
    m2_aux = m2.tolist()
    mp = [[]]
    cont = 0
    for i in range(len(m1_aux)):
        for j in range(len(m2_aux)):
            cont = 0
            while cont < 3:
                print("posicion: ")
                print(i,j,cont)
                cont += 1
          #      mp[i][j] += m1_aux[i][cont] * m1_aux[cont][j]
    return

#matriz[][] 




if __name__ == '__main__':
    ## Creemos las dos matrices con numeros alatorios de 1000*1000
    # (por pruebitas tripi tripi seran de 3*3)
    TAM = 3
    CHUNK = 1

    #matrices generadas con numpy para facilidad de trabajo
    m1np = np.random.randint(1, 10, size=(TAM, TAM))
    m2np = np.random.randint(1, 10, size=(TAM, TAM))

    #imprimimos matrices de numpy
    print("matriz 1:")
    imprimir_matriz(m1np)
    print("matriz 2:")
    imprimir_matriz(m2np)

    #probando multiplicacion con numpy
    resultado_numpy = multiplicacion_numpy(m1np, m2np)
    print("resultado multiplicacion con numpy:")
    imprimir_matriz(resultado_numpy)
    #vale, de momento la multiplicacion se hace bien

    #multiplicacion tradicional
    resultado_tradicional = multiplicacion_tradicional(m1np, m2np)


