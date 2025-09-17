# interfaz_grafica/ventana_principal.py

import customtkinter as ctk
from interfaz_grafica.panel_estado import PanelEstado
from interfaz_grafica.panel_control import PanelControl

class VentanaPrincipal(ctk.CTk):
    def __init__(self, gestor_memoria, planificador):
        super().__init__()
        self.title("Simulador de Gestión de Procesos")
        self.geometry("1000x600")
        self.resizable(False, False)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Referencias lógicas
        self.gestor_memoria = gestor_memoria
        self.planificador = planificador

        # Paneles
        self.panel_estado = PanelEstado(self, gestor_memoria, planificador)
        self.panel_estado.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.panel_control = PanelControl(self, gestor_memoria, planificador, self.panel_estado)
        self.panel_control.pack(side="right", fill="y", padx=10, pady=10)
