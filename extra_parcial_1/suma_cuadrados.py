import time
from concurrent.futures import ThreadPoolExecutor

def squared(x):
    return x*x

def sum_squared(list):
    with ThreadPoolExecutor() as ex:
        results = ex.map(squared, list)
    return sum(results)

if __name__ == '__main__':
    num = 10
    numeros = range(num+1)
    inicio = time.time()
    resultado = sum_squared(numeros)
    final = time.time()
    dif = final - inicio
    print(f"La suma de los cuadrados es: {resultado}")
    print(f"El tiempo fue de: {dif}")