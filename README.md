# 🎵 Lector de Partituras Musicales con IA

Este proyecto utiliza visión por computadora (OpenCV) y reconocimiento de patrones para detectar y reproducir notas musicales desde imágenes de partituras.
Además, incluye una interfaz gráfica moderna basada en CustomTkinter, con control de tempo, reproducción MIDI y visualización interactiva de las notas.

## 🚀 Características principales

✅ Detección automática de notas musicales (redondas, blancas, negras, corcheas)

✅ Soporte para clave de sol

✅ Reproducción de la partitura mediante sonidos MIDI

✅ Interfaz gráfica moderna y responsiva (CustomTkinter + Pillow)

✅ Visualización de la partitura con notas resaltadas durante la reproducción

✅ Panel lateral con información detallada de cada nota:

- Nombre de la nota

- Frecuencia

- Tipo (redonda, blanca, etc.)

- Duración

- Pitch MIDI

- Nivel de confianza

---

## 🧰 Tecnologías utilizadas

Python 3.10+

OpenCV (cv2)

NumPy

Pillow (PIL)

CustomTkinter

Pygame.midi

Tkinter

Threading

---

## 📦 Instalación

### 1️⃣ Clona este repositorio:

```
git clone https://github.com/Jrdb03/lector-partituras.git
cd lector-partituras
```

### 2️⃣ Crea un entorno virtual (opcional pero recomendado):

```
python -m venv venv

source venv/bin/activate      # En Linux/Mac

venv\Scripts\activate         # En Windows
```


### 3️⃣ Instala las dependencias:
```
pip install -r requirements.txt
```
---

## 🖼️ Uso

### 1️⃣ Ejecuta la aplicación:

`python main.py`

## 2️⃣ En la ventana principal:

Pulsa “Cargar Imagen” para seleccionar una partitura (formatos .png, .jpg, .bmp).

Pulsa “Detectar Notas” para procesar la imagen.

Visualiza las notas detectadas sobre la partitura.

Pulsa “Reproducir” para escuchar la partitura con sonido MIDI.

Ajusta el tempo (BPM) con el control deslizante.

Selecciona una nota de la lista para ver su información detallada.

---

## 🎶 Créditos

**Autor:** Jorge Regalado del Barco

**Librerías:** OpenCV, Pillow, Pygame, CustomTkinter

Inspirado en proyectos de reconocimiento óptico de partituras (OMR)
