from PIL import Image
import os
import time
from concurrent.futures import ProcessPoolExecutor # Servirá para ignorar el GIL y realizar paralelismo por procesos
from functools import partial


def convertir_a_gris(ruta_imagen, carpeta_destino=None):
    """Convierte una imagen a escala de grises.
    Si carpeta_destino es None, guarda junto a la imagen original"""
    try:
        imagen = Image.open(ruta_imagen)
        imagen_gris = imagen.convert('L') # 'L' representa escala de grises

        # Separamos, carpeta, nombre y extension
        carpeta_original = os.path.dirname(ruta_imagen)
        nombre_completo = os.path.basename(ruta_imagen)
        nombre_archivo, extension = os.path.splitext(nombre_completo)

        # Decidimos 
        destino = carpeta_destino if carpeta_destino else carpeta_original
        if destino:
            os.makedirs(destino, exist_ok=True)

        ruta_gris = os.path.join(destino, nombre_archivo + "_gris" + extension)
        imagen_gris.save(ruta_gris)
        print(f"Imagen convertida: {ruta_imagen} -> {ruta_gris}")
    except FileNotFoundError:
        print(f"Error: No se encontró la imagen {ruta_imagen}")
    except Exception as e:
        print(f"Error al procesar {ruta_imagen}: {e}")


def procesar_imagenes_secuencial(lista_imagenes, dir):
    """Procesa una lista de imágenes secuencialmente."""
    for ruta_imagen in lista_imagenes:
        convertir_a_gris(ruta_imagen, dir)


def procesar_imagenes_paralelo(lista_imagenes, dir, num_hilos):
    tarea = partial(convertir_a_gris, carpeta_destino=dir)
    chunksize = max(1, len(lista_imagenes)//(num_hilos*4))
    with ProcessPoolExecutor(max_workers=num_hilos) as ex:
        ex.map(tarea, lista_imagenes, chunksize=chunksize)

if __name__ == '__main__':
    directorio_imagenes = "taller_2/imagenes" # Reemplaza con el nombre de tu directorio
    lista_imagenes = [os.path.join(directorio_imagenes, f) for f in 
                      os.listdir(directorio_imagenes) if
                      os.path.isfile(os.path.join(directorio_imagenes, f))]
    num_hilos = 8

    # Directorios de salida para las imagenes
    dir_paralelo = "taller_2/salida/par"
    dir_secuencial = "taller_2/salida/sec"
    
    inicio_secuencial = time.time()
    procesar_imagenes_secuencial(lista_imagenes, dir_secuencial)
    fin_secuencial = time.time()
    diferencia_secuencial = fin_secuencial - inicio_secuencial

    print(f"Tiempo total de procesamiento secuencial: {diferencia_secuencial:.2f} segundos")

    inicio_paralelo = time.time()
    procesar_imagenes_paralelo(lista_imagenes, dir_paralelo, num_hilos)
    fin_paralelo = time.time()
    diferencia_paralelo = fin_paralelo - inicio_paralelo

    print(f"Tiempo total de procesamiento paralelo: {diferencia_paralelo:.2f} segundos")

    aceleracion = diferencia_secuencial / diferencia_paralelo
    print(f"\nLa aceleración fue de: {aceleracion}x")