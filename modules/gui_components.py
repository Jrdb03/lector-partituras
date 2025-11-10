# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import customtkinter as ctk
import threading
import cv2
import os
import time
import pygame.midi

# Importar módulos
from .image_processing import procesar_imagen
from .note_detection import cargar_patrones_template_matching, detectar_notas_template_matching
from .pitch_mapping import asignar_pitch_por_pentagrama, obtener_nombre_nota_simple, obtener_info_nota
from .midi_player import iniciar_midi, cambiar_instrumento, reproducir_nota_midi

class ModernMusicReaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Lector de Partituras Musicales - IA")
        self.root.geometry("1600x1000")
        self.root.minsize(1400, 800)
        
        # Variables
        self.image_path = None
        self.original_image = None
        self.processed_image = None
        self.detected_notes = []
        self.notes_with_pitch = []
        self.playing = False
        self.current_note_index = -1
        self.user_selected_note_index = -1
        
        # Lista de instrumentos MIDI
        self.instrumentos = {
            "Piano Acústico": 0,
            "Piano Eléctrico": 4,
            "Órgano": 16,
            "Guitarra Acústica": 24,
            "Guitarra Eléctrica": 27,
            "Bajo": 32,
            "Violín": 40,
            "Cello": 42,
            "Trompeta": 56,
            "Trombón": 57,
            "Saxofón Alto": 65,
            "Flauta": 73,
            "Flauta Dulce": 74,
            "Pan Flute": 75,
            "Synth Lead": 80,
            "Synth Pad": 88
        }
        
        self.instrumento_actual = 0  # Piano por defecto
        self.player = None  # Referencia al reproductor MIDI
        
        # Configurar estilo
        self.setup_styles()
        
        # Crear interfaz
        self.create_widgets()
        
        # Cargar patrones
        self.patrones = cargar_patrones_template_matching()
        
    def setup_styles(self):
        """Configurar estilos personalizados"""
        self.colors = {
            'primary': '#2B5B84',
            'secondary': '#1E3A5F',
            'accent': '#4CAF50',
            'background': '#1a1a1a',
            'surface': '#2d2d2d',
            'text': '#ffffff'
        }
        
    def create_widgets(self):
        # Frame principal
        self.main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        self.create_header()
        
        # Content area
        self.create_content_area()
        
        # Status bar
        self.create_status_bar()
        
    def create_header(self):
        """Crear la barra superior con controles"""
        header_frame = ctk.CTkFrame(self.main_frame, height=80)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        header_frame.pack_propagate(False)
        
        # Título
        title_label = ctk.CTkLabel(
            header_frame, 
            text="Lector de Partituras Musicales",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=20)
        
        # Controles
        controls_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        controls_frame.pack(side=tk.RIGHT, padx=20, pady=15)
        
        # Selector de instrumentos
        instrument_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        instrument_frame.pack(side=tk.LEFT, padx=10)
        
        ctk.CTkLabel(instrument_frame, text="Instrumento:", 
                    font=ctk.CTkFont(size=12)).pack(side=tk.LEFT)
        
        self.instrumento_var = tk.StringVar(value="Piano Acústico")
        instrument_combo = ctk.CTkComboBox(
            instrument_frame,
            values=list(self.instrumentos.keys()),
            variable=self.instrumento_var,
            width=150,
            height=30,
            font=ctk.CTkFont(size=12),
            command=self.cambiar_instrumento
        )
        instrument_combo.pack(side=tk.LEFT, padx=5)
        
        # Botones principales
        btn_load = ctk.CTkButton(
            controls_frame, 
            text="Cargar Imagen",
            command=self.load_image,
            width=120,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        btn_load.pack(side=tk.LEFT, padx=5)
        
        btn_detect = ctk.CTkButton(
            controls_frame,
            text="Detectar Notas", 
            command=self.detect_symbols,
            width=120,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        btn_detect.pack(side=tk.LEFT, padx=5)
        
        # Frame para reproducción
        play_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        play_frame.pack(side=tk.LEFT, padx=10)
        
        btn_play = ctk.CTkButton(
            play_frame,
            text="Reproducir",
            command=self.play_midi,
            width=100,
            height=35,
            fg_color="#4CAF50",
            hover_color="#45a049",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        btn_play.pack(side=tk.LEFT, padx=2)
        
        btn_stop = ctk.CTkButton(
            play_frame,
            text="Detener", 
            command=self.stop_playback,
            width=80,
            height=35,
            fg_color="#f44336",
            hover_color="#da190b",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        btn_stop.pack(side=tk.LEFT, padx=2)
        
        # Control de tempo
        tempo_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        tempo_frame.pack(side=tk.LEFT, padx=15)
        
        ctk.CTkLabel(tempo_frame, text="Tempo:", font=ctk.CTkFont(size=12)).pack(side=tk.LEFT)
        
        self.tempo_var = tk.IntVar(value=120)
        tempo_slider = ctk.CTkSlider(
            tempo_frame, 
            from_=40, 
            to=200, 
            variable=self.tempo_var,
            width=120,
            height=20
        )
        tempo_slider.pack(side=tk.LEFT, padx=10)
        
        self.tempo_label = ctk.CTkLabel(tempo_frame, text="120 BPM", font=ctk.CTkFont(size=12))
        self.tempo_label.pack(side=tk.LEFT)
        
        # Actualizar label del tempo
        def update_tempo_label(*args):
            self.tempo_label.configure(text=f"{self.tempo_var.get()} BPM")
        
        self.tempo_var.trace('w', update_tempo_label)
        
    def cambiar_instrumento(self, instrumento_nombre):
        """Cambia el instrumento MIDI seleccionado"""
        if instrumento_nombre in self.instrumentos:
            self.instrumento_actual = self.instrumentos[instrumento_nombre]
            if self.player:
                cambiar_instrumento(self.player, self.instrumento_actual)
            self.update_status(f"Instrumento cambiado a: {instrumento_nombre}")
        
    def create_content_area(self):
        """Crear el área de contenido principal"""
        content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Panel izquierdo - Visualización de partitura
        self.create_score_panel(content_frame)
        
        # Panel derecho - Información de notas
        self.create_info_panel(content_frame)
        
    def create_score_panel(self, parent):
        """Panel para visualizar la partitura"""
        score_frame = ctk.CTkFrame(parent, width=900)
        score_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Título del panel
        ctk.CTkLabel(
            score_frame, 
            text="Visualización de Partitura",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15, 10))
        
        # Canvas para la imagen
        self.canvas_frame = ctk.CTkFrame(score_frame)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Canvas con scrollbars
        self.canvas = tk.Canvas(
            self.canvas_frame, 
            bg='#1a1a1a',
            highlightthickness=0,
            cursor="crosshair"
        )
        
        # Scrollbars
        v_scrollbar = ctk.CTkScrollbar(self.canvas_frame, orientation="vertical", command=self.canvas.yview)
        h_scrollbar = ctk.CTkScrollbar(self.canvas_frame, orientation="horizontal", command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout para canvas y scrollbars
        self.canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)
        
        # Placeholder inicial
        self.show_placeholder()
        
    def create_info_panel(self, parent):
        """Panel derecho con información de notas"""
        info_frame = ctk.CTkFrame(parent, width=400)
        info_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        info_frame.pack_propagate(False)
        
        # Título del panel
        ctk.CTkLabel(
            info_frame, 
            text="Información de Notas",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(15, 10))
        
        # Lista de notas
        self.create_notes_list(info_frame)
        
        # Información detallada (se mostrará cuando se seleccione una nota)
        self.create_note_details(info_frame)
        
    def create_notes_list(self, parent):
        """Crear la lista de notas detectadas"""
        # Header con estadísticas
        stats_frame = ctk.CTkFrame(parent, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 10), padx=10)
        
        ctk.CTkLabel(stats_frame, text="Notas Detectadas:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(side=tk.LEFT, anchor="w")
        
        self.notes_count_label = ctk.CTkLabel(stats_frame, text="Total: 0 notas", 
                                            font=ctk.CTkFont(size=12))
        self.notes_count_label.pack(side=tk.RIGHT, anchor="e")
        
        # Frame para la lista con scrollbar
        list_container = ctk.CTkFrame(parent)
        list_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.notes_listbox = tk.Listbox(
            list_container,
            bg='#2d2d2d',
            fg='white',
            selectbackground='#4CAF50',
            selectforeground='white',
            font=('Arial', 12),
            relief='flat',
            highlightthickness=0
        )
        
        scrollbar = ctk.CTkScrollbar(list_container, command=self.notes_listbox.yview)
        self.notes_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.notes_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selección
        self.notes_listbox.bind('<<ListboxSelect>>', self.on_note_select)
        
    def create_note_details(self, parent):
        """Crear el área de información detallada de la nota CON SCROLL"""
        # Frame principal para detalles
        details_main_frame = ctk.CTkFrame(parent)
        details_main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Canvas y scrollbar para el área de detalles
        self.details_canvas = tk.Canvas(
            details_main_frame,
            bg='#2d2d2d',
            highlightthickness=0
        )
        
        # Scrollbar vertical
        details_scrollbar = ctk.CTkScrollbar(
            details_main_frame, 
            orientation="vertical", 
            command=self.details_canvas.yview
        )
        
        self.details_canvas.configure(yscrollcommand=details_scrollbar.set)
        
        # Frame que contendrá todo el contenido (se colocará dentro del canvas)
        self.details_frame = ctk.CTkFrame(self.details_canvas, fg_color='#2d2d2d')
        
        # Crear ventana en el canvas para el frame
        self.details_window = self.details_canvas.create_window(
            (0, 0), 
            window=self.details_frame, 
            anchor="nw",
            width=380
        )
        
        # Configurar grid
        self.details_canvas.grid(row=0, column=0, sticky="nsew")
        details_scrollbar.grid(row=0, column=1, sticky="ns")
        
        details_main_frame.grid_rowconfigure(0, weight=1)
        details_main_frame.grid_columnconfigure(0, weight=1)
        
        # Bind para ajustar el tamaño del frame interno cuando cambie el tamaño del canvas
        def configure_canvas(event):
            self.details_canvas.itemconfig(self.details_window, width=event.width)
            
        self.details_canvas.bind('<Configure>', configure_canvas)
        
        # Bind para actualizar la región de scroll
        def on_frame_configure(event):
            self.details_canvas.configure(scrollregion=self.details_canvas.bbox("all"))
            
        self.details_frame.bind('<Configure>', on_frame_configure)
        
        # Placeholder inicial
        self.info_placeholder = ctk.CTkLabel(
            self.details_frame,
            text="Selecciona una nota de la lista para ver información detallada",
            font=ctk.CTkFont(size=14),
            text_color="#888888",
            wraplength=350
        )
        self.info_placeholder.pack(expand=True, pady=50, padx=20)
        
    def create_status_bar(self):
        """Crear la barra de estado inferior"""
        status_frame = ctk.CTkFrame(self.main_frame, height=40)
        status_frame.pack(fill=tk.X, pady=(20, 0))
        status_frame.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(
            status_frame, 
            text="Listo para cargar una partitura musical",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Progreso
        self.progress_bar = ctk.CTkProgressBar(status_frame, width=200, height=15)
        self.progress_bar.pack(side=tk.RIGHT, padx=20, pady=10)
        self.progress_bar.set(0)
        
    def show_placeholder(self):
        """Mostrar placeholder cuando no hay imagen"""
        self.canvas.delete("all")
        self.canvas.create_text(
            self.canvas.winfo_width() // 2,
            self.canvas.winfo_height() // 2,
            text="Carga una partitura para comenzar\n\nHaz clic en 'Cargar Imagen'",
            fill="#666666",
            font=('Arial', 16),
            justify=tk.CENTER
        )
    
    def load_image(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar imagen de partitura",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff")]
        )
        
        if file_path:
            self.image_path = file_path
            self.original_image = cv2.imread(file_path)
            if self.original_image is not None:
                self.display_image(self.original_image)
                self.update_status(f"Imagen cargada: {os.path.basename(file_path)}")
                self.detected_notes = []
                self.notes_with_pitch = []
                self.notes_listbox.delete(0, tk.END)
                self.notes_count_label.configure(text="Total: 0 notas")
                self.clear_note_info()
                self.current_note_index = -1
                self.user_selected_note_index = -1
            else:
                messagebox.showerror("Error", "No se pudo cargar la imagen")
    
    def display_image(self, image):
        """Mostrar imagen en el canvas"""
        # Convertir BGR a RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Redimensionar para ajustar al canvas
        h, w = image_rgb.shape[:2]
        max_size = 800
        if h > max_size or w > max_size:
            scale = min(max_size/h, max_size/w)
            new_h, new_w = int(h*scale), int(w*scale)
            image_rgb = cv2.resize(image_rgb, (new_w, new_h))
        
        self.processed_image = Image.fromarray(image_rgb)
        self.photo = ImageTk.PhotoImage(self.processed_image)
        
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
    
    def display_image_with_detections(self, image, current_note_idx=-1):
        """Muestra la imagen con las detecciones y resalta la nota actual"""
        img_with_detections = image.copy()
        
        for i, nota in enumerate(self.notes_with_pitch):
            pitch, dur, x, y, w, h, nombre, tipo, pent_idx, score = nota
            
            # Color según tipo (en formato BGR para OpenCV)
            if tipo == "eighth":
                color = (0, 255, 255)  # Amarillo en BGR
                border_color = (0, 200, 200)
            elif tipo == "quarter":
                color = (0, 0, 255)    # Rojo en BGR
                border_color = (0, 0, 200)
            elif tipo == "half":
                color = (255, 0, 0)    # Azul en BGR
                border_color = (200, 0, 0)
            elif tipo == "whole":
                color = (0, 255, 0)    # Verde en BGR
                border_color = (0, 200, 0)
            else:  # clef
                color = (128, 0, 128)  # Morado en BGR
                border_color = (100, 0, 100)
            
            nombre_nota = obtener_nombre_nota_simple(pitch)
            
            # Resaltar nota actual durante reproducción
            if i == current_note_idx:
                # SOLO el rectángulo resaltado - SIN texto durante reproducción
                cv2.rectangle(img_with_detections, (x-8, y-8), (x + w + 8, y + h + 8), (255, 255, 255), 4)
                cv2.rectangle(img_with_detections, (x-6, y-6), (x + w + 6, y + h + 6), color, 3)
                
            else:
                # Para notas no activas: rectángulo + texto centrado SIN relieve
                cv2.rectangle(img_with_detections, (x-2, y-2), (x + w + 2, y + h + 2), border_color, 2)
                cv2.rectangle(img_with_detections, (x, y), (x + w, y + h), color, 1)
                
                # Etiqueta centrada debajo del rectángulo - TEXTO SIMPLE SIN RELIEVE
                label = nombre_nota
                label_y = y + h + 25
                text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)[0]
                label_x = x + (w - text_size[0]) // 2  # Centrar horizontalmente
                
                # Texto simple sin sombra/relieve
                cv2.putText(img_with_detections, label, 
                          (label_x, label_y), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1)
        
        self.display_image(img_with_detections)
    
    def detect_symbols(self):
        if self.image_path is None:
            messagebox.showwarning("Advertencia", "Primero carga una imagen")
            return
        
        self.update_status("Detectando símbolos musicales...")
        self.progress_bar.set(0.3)
        self.root.update()
        
        try:
            # Procesar imagen
            img, gray, posiciones_notas = procesar_imagen(self.image_path)
            
            # Detectar notas
            notas_raw = detectar_notas_template_matching(gray, self.patrones)
            
            # Asignar pitches
            notas_con_pitch = asignar_pitch_por_pentagrama(notas_raw, posiciones_notas, clave='sol', debug=False)
            
            self.detected_notes = notas_raw
            self.notes_with_pitch = [n for n in notas_con_pitch if n[7] != 'clef']
            self.notes_with_pitch.sort(key=lambda x: (x[8], x[2]))
            
            # Actualizar lista de notas
            self.notes_listbox.delete(0, tk.END)
            for i, nota in enumerate(self.notes_with_pitch):
                pitch, dur, x, y, w, h, nombre, tipo, pent_idx, score = nota
                nombre_nota = obtener_nombre_nota_simple(pitch)
                tipo_traducido = {
                    'whole': 'Redonda',
                    'half': 'Blanca',
                    'quarter': 'Negra', 
                    'eighth': 'Corchea'
                }.get(tipo, tipo)
                
                # Formatear la entrada de la lista
                entry_text = f"{i+1:02d}. {nombre_nota} - {tipo_traducido}"
                self.notes_listbox.insert(tk.END, entry_text)
            
            # Mostrar imagen con detecciones
            self.display_image_with_detections(img)
            
            # Actualizar interfaz
            self.notes_count_label.configure(text=f"Total: {len(self.notes_with_pitch)} notas")
            self.update_status(f"Detección completada: {len(notas_raw)} símbolos ({len(self.notes_with_pitch)} notas)")
            self.progress_bar.set(1.0)
            
            # Programar ocultamiento de la barra de progreso
            self.root.after(2000, lambda: self.progress_bar.set(0))
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en detección: {str(e)}")
            self.update_status("Error en la detección")
            self.progress_bar.set(0)
    
    def on_note_select(self, event):
        """Cuando el usuario selecciona manualmente una nota de la lista"""
        if not self.notes_listbox.curselection() or self.playing:
            return
        
        index = self.notes_listbox.curselection()[0]
        if index < len(self.notes_with_pitch):
            self.user_selected_note_index = index
            nota = self.notes_with_pitch[index]
            self.mostrar_info_detallada(nota)
    
    def mostrar_info_detallada(self, nota):
        """Muestra información detallada de la nota seleccionada"""
        pitch, dur, x, y, w, h, nombre, tipo, pent_idx, score = nota
        info = obtener_info_nota(pitch, tipo)
        
        # Limpiar widgets anteriores
        for widget in self.details_frame.winfo_children():
            widget.destroy()
        
        # Crear tarjeta principal
        main_card = ctk.CTkFrame(
            self.details_frame, 
            fg_color=info['color_hex'],
            corner_radius=20,
            border_width=2,
            border_color="#FFFFFF"
        )
        main_card.pack(fill="x", padx=10, pady=10)
        
        # Contenido de la tarjeta principal
        content_frame = ctk.CTkFrame(main_card, fg_color="transparent")
        content_frame.pack(fill="x", padx=20, pady=20)
        
        # Icono y nombre de la nota
        icon_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        icon_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            icon_frame,
            text="Nota Musical",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="white"
        ).pack(side=tk.LEFT)
        
        ctk.CTkLabel(
            icon_frame,
            text=info['tipo'],
            font=ctk.CTkFont(size=18),
            text_color="white"
        ).pack(side=tk.RIGHT)
        
        # Información detallada en tarjetas pequeñas
        details_grid = ctk.CTkFrame(self.details_frame, fg_color="transparent")
        details_grid.pack(fill="x", padx=10, pady=10)
        
        # Primera fila
        row1_frame = ctk.CTkFrame(details_grid, fg_color="transparent")
        row1_frame.pack(fill="x", pady=5)
        
        # Duración
        duration_card = self.create_info_card(
            row1_frame, "Duración", info['duracion'], info['color_hex']
        )
        duration_card.pack(side=tk.LEFT, fill="x", expand=True, padx=5)
        
        # Pitch MIDI
        pitch_card = self.create_info_card(
            row1_frame, "Pitch MIDI", str(info['pitch']), info['color_hex']
        )
        pitch_card.pack(side=tk.LEFT, fill="x", expand=True, padx=5)
        
        # Segunda fila
        row2_frame = ctk.CTkFrame(details_grid, fg_color="transparent")
        row2_frame.pack(fill="x", pady=5)
        
        # Frecuencia
        freq_card = self.create_info_card(
            row2_frame, "Frecuencia", info['frecuencia'], info['color_hex']
        )
        freq_card.pack(side=tk.LEFT, fill="x", expand=True, padx=5)
        
        # Pentagrama
        staff_card = self.create_info_card(
            row2_frame, "Pentagrama", f"{pent_idx + 1}", info['color_hex']
        )
        staff_card.pack(side=tk.LEFT, fill="x", expand=True, padx=5)
        
        # Tercera fila
        row3_frame = ctk.CTkFrame(details_grid, fg_color="transparent")
        row3_frame.pack(fill="x", pady=5)
        
        # Posición
        pos_card = self.create_info_card(
            row3_frame, "Posición", f"({x}, {y})", info['color_hex']
        )
        pos_card.pack(side=tk.LEFT, fill="x", expand=True, padx=5)
        
        # Score
        score_card = self.create_info_card(
            row3_frame, "Confianza", f"{score:.3f}", info['color_hex']
        )
        score_card.pack(side=tk.LEFT, fill="x", expand=True, padx=5)
        
        # Actualizar el scrollregion del canvas
        self.details_frame.update_idletasks()
        self.details_canvas.configure(scrollregion=self.details_canvas.bbox("all"))
        
        # Scroll al inicio
        self.details_canvas.yview_moveto(0)
    
    def create_info_card(self, parent, title, value, color):
        """Crear una tarjeta de información pequeña"""
        card = ctk.CTkFrame(
            parent,
            fg_color="#2d2d2d",
            corner_radius=15,
            border_width=1,
            border_color=color
        )
        
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        ctk.CTkLabel(
            content_frame,
            text=title,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=color
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            content_frame,
            text=value,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        ).pack(anchor="w", pady=(5, 0))
        
        return card
    
    def clear_note_info(self):
        """Limpiar la información de nota mostrada"""
        for widget in self.details_frame.winfo_children():
            widget.destroy()
        
        self.info_placeholder = ctk.CTkLabel(
            self.details_frame,
            text="Selecciona una nota de la lista para ver información detallada",
            font=ctk.CTkFont(size=14),
            text_color="#888888",
            wraplength=350
        )
        self.info_placeholder.pack(expand=True, pady=50, padx=20)
        
        # Actualizar el scrollregion
        self.details_frame.update_idletasks()
        self.details_canvas.configure(scrollregion=self.details_canvas.bbox("all"))
    
    def play_midi(self):
        if not self.notes_with_pitch:
            messagebox.showwarning("Advertencia", "Primero detecta los símbolos")
            return
        
        if self.playing:
            return
        
        self.playing = True
        self.current_note_index = -1
        threading.Thread(target=self._play_midi_thread, daemon=True).start()
    
    def _play_midi_thread(self):
        try:
            self.player = iniciar_midi()
            
            # Aplicar el instrumento seleccionado
            if self.player:
                cambiar_instrumento(self.player, self.instrumento_actual)
            
            tempo_bpm = self.tempo_var.get()
            SECONDS_PER_BEAT = 60.0 / tempo_bpm
            
            total = len(self.notes_with_pitch)
            
            for i, n in enumerate(self.notes_with_pitch):
                if not self.playing:
                    break
                    
                self.current_note_index = i
                pitch, duracion, x, y, w, h, nombre, tipo, pent_idx, score = n
                dur_secs = duracion * 4 * SECONDS_PER_BEAT
                
                # Actualizar interfaz
                self.root.after(0, self._update_playback_display, i, total, pitch, tipo)
                
                # Reproducir nota
                if self.player:
                    reproducir_nota_midi(self.player, pitch, dur_secs)
                else:
                    time.sleep(dur_secs)
            
            self.current_note_index = -1
            if self.player:
                self.player.close()
                pygame.midi.quit()
                self.player = None
                
            self.root.after(0, self._playback_finished)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error en reproducción: {str(e)}"))
            self.root.after(0, self._playback_finished)
    
    def _update_playback_display(self, current, total, pitch, tipo):
        nombre_nota = obtener_nombre_nota_simple(pitch)
        self.update_status(f"Reproduciendo: {current+1}/{total} - {nombre_nota} ({tipo})")
        
        # Actualizar lista seleccionada (solo visual, no cambia la información de detalles)
        self.notes_listbox.selection_clear(0, tk.END)
        self.notes_listbox.selection_set(current)
        self.notes_listbox.see(current)
        
        # Actualizar imagen con nota actual resaltada (SOLO rectángulo, sin texto)
        if self.original_image is not None:
            self.display_image_with_detections(self.original_image.copy(), current)
    
    def _playback_finished(self):
        self.playing = False
        self.current_note_index = -1
        self.update_status("Reproducción finalizada")
        
        # Restaurar imagen con todas las etiquetas visibles
        if self.original_image is not None:
            self.display_image_with_detections(self.original_image.copy())
    
    def stop_playback(self):
        self.playing = False
        self.current_note_index = -1
        self.update_status("Reproducción detenida")
        
        # Cerrar el reproductor MIDI si está activo
        if self.player:
            self.player.close()
            pygame.midi.quit()
            self.player = None
        
        # Restaurar imagen con todas las etiquetas visibles
        if self.original_image is not None:
            self.display_image_with_detections(self.original_image.copy())
    
    def update_status(self, message):
        """Actualizar el mensaje de estado"""
        self.status_label.configure(text=message)