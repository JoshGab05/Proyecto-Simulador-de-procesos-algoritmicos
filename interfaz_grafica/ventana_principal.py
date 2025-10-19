# interfaz_grafica/ventana_principal.py
import customtkinter as ctk
from interfaz_grafica.panel_estado import PanelEstado
from interfaz_grafica.panel_control import PanelControl

class VentanaPrincipal(ctk.CTk):
    def __init__(self, gestor_memoria, planificador):
        super().__init__()
        self.title("Simulador de Gestión de Procesos")
        self.geometry("1100x650")
        self.resizable(False, False)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Paneles
        self.panel_estado = PanelEstado(self, gestor_memoria, planificador)
        self.panel_estado.pack(side="right", fill="both", expand=True, padx=(8, 8), pady=8)

        self.panel_control = PanelControl(self, gestor_memoria, planificador, self.panel_estado)
        self.panel_control.pack(side="left", fill="y", padx=(8, 0), pady=8)

        # Cerrar
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self):
        try:
            self.panel_estado.cancelar_refrescos()
        except Exception:
            pass
        try:
            self.quit()
        except Exception:
            pass
        try:
            self.destroy()
        except Exception:
            pass