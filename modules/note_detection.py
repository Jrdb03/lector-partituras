# -*- coding: utf-8 -*-
import cv2
import numpy as np
import os
import glob

def cargar_patrones_template_matching(base_path="dataset"):
    patrones = {}
    mapeo_carpetas = {
        "Whole Notes": ("whole", 1.0, (76, 175, 80), 0.60),
        "Half Notes": ("half", 0.5, (33, 150, 243), 0.65),
        "Quarter Notes": ("quarter", 0.25, (244, 67, 54), 0.72),
        "8th Notes": ("eighth", 0.125, (255, 193, 7), 0.78),
        "Clefs": ("clef", 0.0, (156, 39, 176), 0.70)
    }
    for carpeta, (tipo, duracion, color, umbral) in mapeo_carpetas.items():
        patrones[tipo] = []
        carpeta_path = os.path.join(base_path, carpeta)
        if os.path.exists(carpeta_path):
            archivos_png = sorted(glob.glob(os.path.join(carpeta_path, "*.png")))
            for archivo in archivos_png:
                img = cv2.imread(archivo, cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    _, img_bin = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)
                    patrones[tipo].append({
                        'imagen': img_bin,
                        'duracion': duracion,
                        'color': color,
                        'nombre': os.path.basename(archivo),
                        'tipo': tipo,
                        'umbral': umbral,
                        'w': img_bin.shape[1],
                        'h': img_bin.shape[0]
                    })
    return patrones

def detectar_notas_template_matching(img_gray, patrones):
    detecciones = []

    for tipo, lista_patrones in patrones.items():
        for pat in lista_patrones:
            template = pat['imagen']
            h, w = template.shape
            res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
            umbral = pat['umbral']
            loc = np.where(res >= umbral)
            for pt in zip(*loc[::-1]):
                x, y = int(pt[0]), int(pt[1])
                score = float(res[pt[1], pt[0]])
                nombre = f"{tipo}_{pat['nombre'].replace('.png','')}"
                detecciones.append({
                    'x': x, 'y': y, 'w': w, 'h': h,
                    'dur': pat['duracion'], 'tipo': tipo, 'nombre': nombre, 'score': score
                })

    # resolver solapamientos
    finales = []
    for d in sorted(detecciones, key=lambda x: -x['score']):
        x, y, w, h, tipo = d['x'], d['y'], d['w'], d['h'], d['tipo']
        keep = True
        remove_idx = None
        for i, f in enumerate(finales):
            x2, y2, w2, h2 = f['x'], f['y'], f['w'], f['h']
            x_overlap = max(0, min(x + w, x2 + w2) - max(x, x2))
            y_overlap = max(0, min(y + h, y2 + h2) - max(y, y2))
            if x_overlap > 0 and y_overlap > 0:
                area_overlap = x_overlap * y_overlap
                area_cur = w * h
                if area_overlap / area_cur > 0.2 or area_overlap / (w2*h2) > 0.2:
                    if d['score'] > f['score'] + 1e-6:
                        remove_idx = i
                        break
                    elif abs(d['score'] - f['score']) < 1e-6:
                        if d['tipo'] == 'eighth' and f['tipo'] == 'quarter':
                            remove_idx = i
                            break
                        else:
                            keep = False
                            break
                    else:
                        keep = False
                        break
        if remove_idx is not None:
            finales.pop(remove_idx)
            finales.append(d)
        elif keep:
            finales.append(d)

    notas = []
    for f in finales:
        notas.append([f['x'], f['y'], f['dur'], f['w'], f['h'], f['nombre'], f['tipo'], f['score']])
    return notas