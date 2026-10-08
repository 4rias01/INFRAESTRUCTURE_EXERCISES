from threading import Thread #importamos libreria de threading para hacer uso de los hilos.
import random # para generar numeros aleatorios en la matriz
import time # mediciones y comparacion.


# Funcion que genera la matriz de tamaño dim x dim con numeros aleatorios entre 1 y 99.
def generar_matriz(dim):
    m = [[random.randint(1,100) # generada con numeros aleatorios entre 1 y 99
          for _ in range(dim)] 
          for _ in range(dim)]
    return m

# Funcion que imprime la matriz de manera legible
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


# funcion de sima de matriz secuencial, recibe la matriz y los indices de inicio y fin de filas y columnas a sumar.
# este sencillamente recorre toda la matriz posicion a posicion y va sumand los elementos de manera acumulativa.
def sumar_matriz_secuencial(m, fil_inicio, fil_final, col_inicio, col_final):
    total = 0 # inicializamos variable acumuladora como un 0.
    for i in range (fil_inicio, fil_final): #recorremos filas
        for j in range (col_inicio, col_final): #recorremos columnas
            total += m[i][j] # sumamos elemento de cada posicion a la variable acumuladora
    return total


def sumar_bloque(m, fil_inicio, fil_final, col_inicio, col_final, resultados, idx):
    resultados[idx] = sumar_matriz_secuencial(m, fil_inicio, fil_final, col_inicio, col_final)


def sumar_matriz_smp(m, chunksize):
    num_bloques_filas = len(m) // chunksize
    num_bloques_columnas = len(m[0]) // chunksize
    resultados = [0] * (num_bloques_filas * num_bloques_columnas)
    hilos = []

    for i in range(num_bloques_filas):
        for j in range(num_bloques_columnas):
            idx = i * num_bloques_columnas + j
            t = Thread(
                target=sumar_bloque,
                args=(m, i * chunksize, (i + 1) * chunksize,
                      j * chunksize, (j + 1) * chunksize,
                      resultados, idx),
            )
            hilos.append(t)
            t.start()

    for t in hilos:
        t.join()          # esperar a que todos terminen antes de combinar

    return sum(resultados)

    
if __name__ == '__main__':
    TAM = 1000
    CHUNK = 100
    m1 = generar_matriz(TAM)

    inicio = time.perf_counter()
    resultado_sec = sumar_matriz_secuencial(m1, 0, TAM, 0, TAM)
    dif_sec = time.perf_counter() - inicio

    inicio = time.perf_counter()
    resultado_smp = sumar_matriz_smp(m1, CHUNK)
    dif_smp = time.perf_counter() - inicio

    assert resultado_sec == resultado_smp   # verifica que ambas versiones coinciden
    print(f"Secuencial: {dif_sec:.4f} s | SMP: {dif_smp:.4f} s")
    
    