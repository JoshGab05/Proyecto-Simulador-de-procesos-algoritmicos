import customtkinter as ctk
import threading
from interfaz_grafica.panel_estado import PanelEstado
from interfaz_grafica.panel_control import PanelControl
from interfaz_grafica.tabla_eficiencia import TablaEficiencia
from interfaz_grafica.panel_ejecucion import PanelEjecucion


class VentanaPrincipal(ctk.CTk):
    def __init__(self, gestor_memoria, planificador):
        super().__init__()
        self.title("Simulador de Gestión de Procesos Algorítmicos")
        self.geometry("1200x680")
        self.resizable(False, False)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.gestor_memoria = gestor_memoria
        self.planificador = planificador
        self._resultados_rr = None

        # ================================
        # DISEÑO PRINCIPAL  (35 / 30 / 35)
        # ================================
        self.grid_columnconfigure(0, weight=35, uniform="column")
        self.grid_columnconfigure(1, weight=30, uniform="column")
        self.grid_columnconfigure(2, weight=35, uniform="column")
        self.grid_rowconfigure(0, weight=1)

        # -------- PANEL CONTROL --------
        self.panel_control = PanelControl(
            self,
            gestor_memoria,
            planificador,
            None,
            ejecutar_algoritmo_callback=self.ejecutar_round_robin,
            mostrar_tabla_callback=self.mostrar_tabla_eficiencia,
        )
        self.panel_control.grid(row=0, column=0, sticky="nswe", padx=(10, 5), pady=10)

        # -------- PANEL ESTADO --------
        self.panel_estado = PanelEstado(self, planificador)
        self.panel_estado.grid(row=0, column=1, sticky="nswe", padx=5, pady=10)

        # -------- PANEL EJECUCIÓN --------
        self.panel_ejecucion = PanelEjecucion(self)
        self.panel_ejecucion.grid(row=0, column=2, sticky="nswe", padx=(5, 10), pady=10)

        # Vincular panel de control con estado
        self.panel_control.panel_estado = self.panel_estado

        # Asegurar que el tamaño se mantenga fijo
        self.update_idletasks()
        self.minsize(self.winfo_width(), self.winfo_height())

        # Al cerrar la ventana
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ===============================================================
    # EJECUCIÓN DE ROUND ROBIN VISUAL
    # ===============================================================
    def ejecutar_round_robin(self, algorithm="RR", quantum=2):
        """Ejecuta el algoritmo seleccionado (por ahora Round Robin)."""
        if algorithm != "RR":
            self.planificador.set_algoritmo(algorithm)
            self.planificador.iniciar()
            self.panel_estado.programar_refrescos()
            return

        # Cancelar refrescos si estaban activos
        try:
            self.panel_estado.cancelar_refrescos()
        except Exception:
            pass

        # Limpiar interfaz antes de iniciar
        self._resultados_rr = None
        self.panel_ejecucion.limpiar()
        self.panel_ejecucion.inicializar_procesos(self.planificador.obtener_procesos())

        # Mantener tamaño fijo del centro (evita reducción visual)
        self.update_idletasks()
        fixed_width = self.winfo_width()
        fixed_height = self.winfo_height()
        self.minsize(fixed_width, fixed_height)
        self.maxsize(fixed_width, fixed_height)

        # ---------- EJECUCIÓN EN HILO SEPARADO ----------
        def _run():
            def safe_on_tick(t, proceso_actual, cola_ready):
                # Actualiza la interfaz en el hilo principal
                self.after(0, lambda: self.panel_ejecucion.actualizar_tick(t, proceso_actual, cola_ready))
                self.after(0, lambda: self.panel_estado.actualizar_estado(t, proceso_actual, cola_ready, "RR"))

            # Ejecutar Round Robin
            res = self.planificador.ejecutar_round_robin_visual(
                quantum=quantum,
                on_tick=safe_on_tick
            )
            self._resultados_rr = res

            # Al finalizar, mostrar tabla y orden de finalización
            self.after(0, self.mostrar_tabla_eficiencia)
            self.after(0, lambda: self.panel_estado.mostrar_orden_finalizacion(self._resultados_rr))

        threading.Thread(target=_run, daemon=True).start()

    # ===============================================================
    # MOSTRAR TABLA DE EFICIENCIA
    # ===============================================================
    def mostrar_tabla_eficiencia(self):
        """Abre la ventana con la tabla de eficiencia al terminar la simulación."""
        if not self._resultados_rr:
            print("⚠️ No hay resultados disponibles.")
            return
        TablaEficiencia(self, self._resultados_rr)

    # ===============================================================
    # CIERRE LIMPIO DE LA APLICACIÓN
    # ===============================================================
    def _on_close(self):
        try:
            self.panel_estado.cancelar_refrescos()
        except Exception:
            pass
        try:
            self.quit()
            self.destroy()
        except Exception:
            pass
