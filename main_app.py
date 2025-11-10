# -*- coding: utf-8 -*-
import tkinter as tk
import customtkinter as ctk
from modules.gui_components import ModernMusicReaderGUI

def main():
    # Configurar apariencia de CustomTkinter
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    
    root = ctk.CTk()
    app = ModernMusicReaderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()