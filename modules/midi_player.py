# -*- coding: utf-8 -*-
import pygame.midi
import time

def iniciar_midi():
    try:
        pygame.midi.init()
    except Exception as e:
        print("Error iniciando pygame.midi:", e)
        return None
    if pygame.midi.get_count() == 0:
        print("No hay dispositivos MIDI disponibles.")
        return None
    device_id = pygame.midi.get_default_output_id()
    player = pygame.midi.Output(device_id)
    player.set_instrument(0)  # Piano por defecto
    return player

def cambiar_instrumento(player, instrumento_id):
    """Cambia el instrumento MIDI"""
    if player is not None:
        try:
            player.set_instrument(instrumento_id)
            return True
        except Exception as e:
            print(f"Error cambiando instrumento: {e}")
            return False
    return False

def reproducir_nota_midi(player, pitch, duracion_seg):
    if player is None:
        time.sleep(duracion_seg)
        return
    velocity = 100
    player.note_on(int(pitch), velocity)
    time.sleep(duracion_seg)
    player.note_off(int(pitch), velocity)