import time
import concurrent.futures

# Número de terminos de la sucesión de fibonacci a calcular.
# Se cambio por 32 en lugar de 20 para que la paralelización 
# muestre una aceleración real.
N = 32 

# --------------------------------------------------------
# Función de trabajo: Fibonacci recursivo secuencial
# --------------------------------------------------------
# Complejidad temporal exponencial porque recalcula los mismos subproblemas 
# muchas veces (no usa memoización). Esto es intencional ya que es una tarea 
# costosa y secuencial, ideal para comparar ejecución secuencial vs. paralela.
def fibonacci(n):
    # Casos base: fibonacci(0) = 0 y fibonacci(1) = 1
    if n <= 1:
        return n
    # Caso recursivo
    return fibonacci(n - 1) + fibonacci(n - 2)


# --------------------------------------------------------
# Versión secuencial
# --------------------------------------------------------
# Calcula los n_elementos primeros términos uno detrás de otro en un solo
# proceso/hilo y devuelve el tiempo total que tardó.

def calcular_fibonacci_secuencial(n_elementos):
    # Marca de tiempo inicial
    inicio = time.time()
    # Lista inicial llenada con 0s
    resultados = [0] * n_elementos

    # Cada iteración es independiente de las demás (fib(i) no usa el
    # resultado guardado de otra iteración), por eso el ciclo es paralelizable
    for i in range(0, n_elementos):
        resultados[i] = fibonacci(i)

    # Marca de tiempo final y duración total
    fin = time.time()
    tiempo_ejecucion = fin - inicio

    # Muestra la lista de resultados y el tiempo 
    print(f"Fibonacci Secuencial ({n_elementos}): {resultados}")
    print(f"Tiempo de ejecución: {tiempo_ejecucion:.4f} segundos")

    # Se devuelve el tiempo para poder calcular luego la aceleración
    return tiempo_ejecucion


# ------------------------------------------------------
# Versión paralela de fibonacci
# ------------------------------------------------------
# executor_type es la CLASE del pool a usar (no una instancia), por ejemplo:
#   - concurrent.futures.ProcessPoolExecutor -> varios procesos del SO.
#     Cada proceso tiene su propio intérprete y su propio GIL, así que sí
#     hay paralelismo real en varios núcleos para tareas CPU-bound.
#   - concurrent.futures.ThreadPoolExecutor -> varios hilos en el mismo
#     proceso. Por el GIL de CPython el cálculo no tendría aceleración real.

def calcular_fibonacci_paralelo(n_elementos, executor_type):
    # Marca de tiempo inicial
    inicio = time.time()
    # Lista inicial llenada con 0s
    resultados = [0] * n_elementos

    # Se crea el pool con el número de trabajadores por defecto
    # (para procesos: la cantidad de CPUs de la máquina).
    with executor_type() as executor:

        # executor.submit(fibonacci, i) programa la llamada fibonacci(i) en
        # el pool y devuelve inmediatamente un objeto Future (una "promesa"
        # del resultado). Con un diccionario por comprensión se asocia cada
        # Future con el índice i que le corresponde.
        # Esta forma de guardar los resultados de fibonacci difiere en la del
        # código báse, ya que este solo guardaba los objetos futures en una lista
        future_a_indice = {
            executor.submit(fibonacci, i): i for i in range(n_elementos)
        }

        # as_completed entrega los Futures en el orden en que TERMINAN, no en
        # el orden en que se enviaron (los términos pequeños suelen acabar
        # primero). Por eso se necesita el diccionario: para saber en qué
        # posición de la lista va cada resultado.
        for future in concurrent.futures.as_completed(future_a_indice):
            indice = future_a_indice[future]
            resultados[indice] = future.result()

    # Marca de tiempo final y duración total
    fin = time.time()
    tiempo_ejecucion = fin - inicio

    # Muestra la lista de resultados y el tiempo 
    print(f"Fibonacci Paralelo ({n_elementos}): {resultados}")
    print(f"Tiempo de ejecución: {tiempo_ejecucion:.4f} segundos")

    # Se devuelve el tiempo para poder calcular luego la aceleración
    return tiempo_ejecucion


# ------------------------------------------------------
# Programa principal
# ------------------------------------------------------
# Este bloque solo se ejecuta si el archivo se corre directamente.
if __name__ == "__main__":
    # Encabezado decorativo con 10 asteriscos a cada lado
    print("\n","*"*10, "DATOS SECUENCIALES", "*"*10)
    tiempo_secuencial = calcular_fibonacci_secuencial(N)

    # Encabezado decorativo con 10 asteriscos a cada lado
    print("\n","*"*10, "DATOS PARALELOS", "*"*10)
    tiempo_paralelo = calcular_fibonacci_paralelo(
        N,concurrent.futures.ProcessPoolExecutor) #o ThreadPoolExecutor

    # IMPORTANTE: Por cuestiones de overhead, la paralelización solo 
    # empieza a mostrar una aceleración a partir de N > 30
    aceleracion = tiempo_secuencial / tiempo_paralelo
    print(f"\nLa aceleración fue de {aceleracion}")