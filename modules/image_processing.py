# -*- coding: utf-8 -*-
import cv2
import numpy as np
import os

def Lineas_Horizontales_Morph(gray):
    horizontal = gray.copy()
    kernel_size = min(100, max(3, gray.shape[1] // 3))
    horizontalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, 1))
    horizontal = cv2.morphologyEx(horizontal, cv2.MORPH_OPEN, horizontalStructure)
    return horizontal

def listar_notas_corregida(horizontal_inv):
    rows, cols = horizontal_inv.shape
    centro = cols // 2
    lineas = np.where(horizontal_inv[:, centro] == 255)[0]
    if len(lineas) == 0:
        return []
    diferencias = np.diff(lineas)
    mascara = np.concatenate(([True], diferencias >= 5))
    lineas_filtradas = lineas[mascara]
    return lineas_filtradas.tolist()

def div_notas(lista):
    if len(lista) == 0:
        return []
    arr = np.array(lista)
    n_pentagramas = len(arr) // 5
    if n_pentagramas == 0:
        return []
    pentagramas = arr[:n_pentagramas * 5].reshape(n_pentagramas, 5)
    return pentagramas.tolist()

def agre_notas(lista):
    total_lista = []
    for pentagrama in lista:
        if len(pentagrama) < 2:
            continue
        pentagrama_arr = np.array(pentagrama)
        space_height = int((pentagrama_arr[1] - pentagrama_arr[0]) // 2)
        todas_posiciones = []
        todas_posiciones.append(int(pentagrama_arr[0] - space_height))
        for i in range(len(pentagrama_arr)):
            todas_posiciones.append(int(pentagrama_arr[i]))
            if i < len(pentagrama_arr) - 1:
                todas_posiciones.append(int(pentagrama_arr[i] + space_height))
        todas_posiciones.append(int(pentagrama_arr[-1] + space_height))
        total_lista.append(todas_posiciones)
    return total_lista

def procesar_imagen(ruta_imagen):
    if not os.path.exists(ruta_imagen):
        print(f"Error: No se encontró el archivo {ruta_imagen}")
        return None, None, None
    img = cv2.imread(ruta_imagen)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_invertida = cv2.bitwise_not(img_gray)
    _, gray = cv2.threshold(img_invertida, 100, 255, cv2.THRESH_BINARY)
    lineas_horizontales = Lineas_Horizontales_Morph(gray)
    posiciones_lineas = listar_notas_corregida(lineas_horizontales)
    pentagramas = div_notas(posiciones_lineas)
    posiciones_notas = agre_notas(pentagramas)
    return img, gray, posiciones_notas