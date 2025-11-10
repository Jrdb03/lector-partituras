# -*- coding: utf-8 -*-
import numpy as np

def construir_map_de_pitches(posiciones, clave='sol'):
    n = len(posiciones)
    if n == 0:
        return np.array([])
    if clave == 'sol' and n == 11:
        vec = np.array([77, 76, 74, 72, 71, 69, 67, 65, 64, 62, 60])
        return vec
    if clave == 'sol':
        top_midi = 79
        bottom_midi = 62
    else:
        top_midi = 67
        bottom_midi = 48
    pitches = np.linspace(top_midi, bottom_midi, num=n)
    return np.round(pitches).astype(int)

def asignar_pitch_por_pentagrama(notas_detectadas, posiciones_notas, clave='sol', debug=True):
    mapas = []
    posiciones_ordenadas = []
    for pos in posiciones_notas:
        pos_sorted = sorted(pos)
        posiciones_ordenadas.append(np.array(pos_sorted))
        mapas.append(construir_map_de_pitches(pos_sorted, clave=clave))

    notas_finales = []

    for idx_n, nota in enumerate(notas_detectadas):
        x, y, duracion, w, h, nombre, tipo, score = nota
        pent_idx = None
        min_dist = float('inf')
        best_pos_idx = None

        for i, pos_array in enumerate(posiciones_ordenadas):
            if pos_array.size == 0:
                continue
            dists = np.abs(pos_array - y)
            local_min = float(np.min(dists))
            local_idx = int(np.argmin(dists))
            if local_min < min_dist:
                min_dist = local_min
                pent_idx = i
                best_pos_idx = local_idx

        if pent_idx is None:
            pent_idx = 0
            best_pos_idx = 0

        pitch_map = mapas[pent_idx]
        if pitch_map.size == 0:
            pitch = 60
        else:
            best_pos_idx = max(0, min(best_pos_idx, len(pitch_map)-1))
            pitch = int(pitch_map[best_pos_idx])

        notas_finales.append([pitch, duracion, x, y, w, h, nombre, tipo, pent_idx, score])

    return notas_finales

def obtener_nombre_nota_simple(pitch):
    """Convierte pitch MIDI a nombre de nota musical SIN octava"""
    notas = ['Do', 'Do#', 'Re', 'Re#', 'Mi', 'Fa', 'Fa#', 'Sol', 'Sol#', 'La', 'La#', 'Si']
    nota_idx = pitch % 12
    return notas[nota_idx]

def obtener_nombre_nota(pitch):
    """Convierte pitch MIDI a nombre de nota musical"""
    return obtener_nombre_nota_simple(pitch)

def obtener_info_nota(pitch, tipo):
    """Obtiene información detallada de la nota"""
    nombre = obtener_nombre_nota_simple(pitch)
    frecuencia = 440 * (2 ** ((pitch - 69) / 12))
    
    tipo_dict = {
        'whole': 'Redonda',
        'half': 'Blanca', 
        'quarter': 'Negra',
        'eighth': 'Corchea'
    }
    nombre_tipo = tipo_dict.get(tipo, tipo)
    
    duracion_dict = {
        'whole': '4 tiempos',
        'half': '2 tiempos',
        'quarter': '1 tiempo',
        'eighth': '1/2 tiempo'
    }
    
    color_dict = {
        'whole': '#4CAF50',
        'half': '#2196F3',
        'quarter': '#F44336',
        'eighth': '#FFC107'
    }
    
    return {
        'pitch': pitch,
        'nombre': nombre,
        'frecuencia': f"{frecuencia:.2f} Hz",
        'tipo': nombre_tipo,
        'duracion': duracion_dict.get(tipo, 'Desconocida'),
        'color_hex': color_dict.get(tipo, '#666666')
    }