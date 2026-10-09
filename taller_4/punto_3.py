"""
Ejercicio integrador: simulación de un sistema híbrido SMP-SIMD.

La matriz 10000x10000 se divide en 100 bloques de 1000x1000.

- SMP : cada bloque se asigna a un hilo (threading.Thread), 100 hilos.
- SIMD: cada bloque se suma con NumPy (np.sum con axis=1), que se ejecuta
        en C con instrucciones vectoriales SIMD del procesador.

Para ver cuánto aporta cada técnica por separado se miden 4 versiones,
todas sobre los mismos 100 bloques:
1. Secuencial pura 
2. Solo SIMD
3. Solo hilos        
4. Híbrido SMP+SIMD

Así, comparando 1 vs 2 se ve el efecto de SIMD, el efecto de los
hilos, y 4 muestra las dos técnicas combinadas.
"""

import os
import time
from threading import Thread

import numpy as np

TAM = 10000          # dimensión de la matriz (10000 x 10000)
BLOQUE = 1000        # dimensión de cada bloque (1000 x 1000)
REPETICIONES = 5     # cada medición se repite y se toma la mediana


def generar_matriz(dim):
    rng = np.random.default_rng()
    return rng.integers(1, 101, size=(dim, dim))


def generar_bloques(filas, cols, tam_bloque):
    # Devuelve los límites (fila_ini, fila_fin, col_ini, col_fin) de cada bloque.
    return [(i, i + tam_bloque, j, j + tam_bloque)
            for i in range(0, filas, tam_bloque)
            for j in range(0, cols, tam_bloque)]


# Formas de sumar UN bloque
def suma_bloque_pura(m_lista, limites):
    # Sin SIMD: recorre el bloque de la lista de listas número a número.
    fi, ff, ci, cf = limites
    total = 0
    for i in range(fi, ff):
        fila = m_lista[i]
        for j in range(ci, cf):
            total += fila[j]
    return total


def suma_bloque_simd(m, limites):
    # Con SIMD: NumPy suma las filas del bloque de forma vectorizada.
    # El slicing de NumPy crea una "vista": no copia los datos del bloque.
    fi, ff, ci, cf = limites
    sumas_filas = np.sum(m[fi:ff, ci:cf], axis=1)
    return int(sumas_filas.sum())


# Formas de recorrer LOS bloques
def ejecutar_secuencial(suma_bloque, datos, bloques):
    # Sin hilos: los bloques se suman uno tras otro en el hilo principal.
    total = 0
    for limites in bloques:
        total += suma_bloque(datos, limites)
    return total


def trabajador(suma_bloque, datos, limites, resultados, idx):
    resultados[idx] = suma_bloque(datos, limites)


def ejecutar_con_hilos(suma_bloque, datos, bloques):
    # Con hilos (SMP): un hilo por bloque (100 hilos).
    # Cada hilo escribe en su propia posición: no hay condición de carrera
    # y no se necesita Lock.
    resultados = [0] * len(bloques)
    hilos = [Thread(target=trabajador,
                    args=(suma_bloque, datos, lim, resultados, idx))
             for idx, lim in enumerate(bloques)]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join()      # esperar a todos los hilos antes de combinar
    return sum(resultados)


def medir(func, *args):
    # Ejecuta func REPETICIONES veces y devuelve (resultado, mediana de tiempos).
    tiempos = []
    for _ in range(REPETICIONES):
        inicio = time.perf_counter()
        resultado = func(*args)
        tiempos.append(time.perf_counter() - inicio)
    tiempos.sort()
    return resultado, tiempos[len(tiempos) // 2]


if __name__ == '__main__':
    print(f"Núcleos disponibles: {os.cpu_count()}")
    print(f"Generando matriz {TAM}x{TAM}...")
    m = generar_matriz(TAM)

    # La conversión a listas es preparación de datos: no entra en la medición.
    print("Convirtiendo la matriz a listas de Python...")
    m_lista = m.tolist()

    bloques = generar_bloques(TAM, TAM, BLOQUE)

    casos = [
        ("1. Secuencial pura",          ejecutar_secuencial, suma_bloque_pura, m_lista),
        ("2. Solo SIMD (1 hilo)",       ejecutar_secuencial, suma_bloque_simd, m),
        ("3. Solo hilos (100 hilos)",   ejecutar_con_hilos,  suma_bloque_pura, m_lista),
        ("4. Híbrido SMP+SIMD",         ejecutar_con_hilos,  suma_bloque_simd, m),
    ]

    resultados = {}
    for nombre, ejecutar, suma_bloque, datos in casos:
        print(f"Midiendo: {nombre}...")
        resultados[nombre] = medir(ejecutar, suma_bloque, datos, bloques)

    # Todas las versiones deben dar exactamente la misma suma.
    totales = {total for total, _ in resultados.values()}
    assert len(totales) == 1, f"Las sumas no coinciden: {totales}"

    base = resultados["1. Secuencial pura"][1]
    print(f"\nSuma total de la matriz: {totales.pop():,}\n")
    print(f"{'Versión':<30}{'Tiempo (s)':>12}{'Aceleración':>14}")
    print("-" * 56)
    for nombre, (_, t) in resultados.items():
        print(f"{nombre:<30}{t:>12.4f}{base / t:>13.2f}x")