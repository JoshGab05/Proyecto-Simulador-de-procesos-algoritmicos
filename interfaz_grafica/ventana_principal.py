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

        # Layout y cierre seguro
        self._app_closing=False
        self.protocol('WM_DELETE_WINDOW', self._on_close)
        try:
            self.panel_estado.pack(side='left', fill='both', expand=True, padx=10, pady=10)
            self.panel_control.pack(side='right', fill='y', padx=10, pady=10)
        except Exception:
            pass

    # Cierre seguro
        self._app_closing = False
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _cancel_all_afters(self):
        try:
            pending = list(self.tk.call('after', 'info'))
            for aid in pending:
                try:
                    self.after_cancel(aid)
                except Exception:
                    pass
        except Exception:
            pass

    def _on_close(self):
        if getattr(self, "_app_closing", False):
            return
        self._app_closing = True
        try:
            if hasattr(self, "panel_control"):
                try:
                    self.panel_control.detener_planificador()
                except Exception:
                    pass
            if hasattr(self, "panel_estado") and hasattr(self.panel_estado, "cancelar_refrescos"):
                try:
                    self.panel_estado.cancelar_refrescos()
                except Exception:
                    pass
            self._cancel_all_afters()
        finally:
            try:
                self.quit()
            except Exception:
                pass
            try:
                self.destroy()
            except Exception:
                pass

