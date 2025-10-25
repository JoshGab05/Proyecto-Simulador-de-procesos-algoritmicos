# interfaz_grafica/panel_control.py
from __future__ import annotations
import customtkinter as ctk


class PanelControl(ctk.CTkFrame):
    """
    Panel de control (versión estable):
      - Lee CPU de 'CPU (ticks)' y llegada de 'Llegada'.
      - Llama planificador.agregar_proceso(nombre, cpu, llegada).
      - Dispara iniciar/pausar/reiniciar de VentanaPrincipal.
    """
    def __init__(self, master, gestor_memoria, planificador,
                 panel_estado=None,
                 ejecutar_algoritmo_callback=None,
                 mostrar_tabla_callback=None):
        super().__init__(master)
        self.gestor = gestor_memoria
        self.planificador = planificador
        self.panel_estado = panel_estado
        self._ejecutar_algoritmo = ejecutar_algoritmo_callback
        self._mostrar_tabla = mostrar_tabla_callback

        self.grid_rowconfigure(99, weight=1)
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="Control de Simulación",
                     font=ctk.CTkFont(size=22, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=8, pady=(8, 6))

        r = 1
        # Algoritmo
        ctk.CTkLabel(self, text="Algoritmo:").grid(row=r, column=0, sticky="w", padx=8)
        self.cbo_alg = ctk.CTkOptionMenu(self, values=["FCFS", "SJF", "SRTF", "RR"])
        self.cbo_alg.set("FCFS")
        self.cbo_alg.grid(row=r, column=0, sticky="ew", padx=(90, 8), pady=4)

        # Quantum (RR)
        r += 1
        ctk.CTkLabel(self, text="Quantum (RR):").grid(row=r, column=0, sticky="w", padx=8)
        self.entry_quantum = ctk.CTkEntry(self, width=90)
        self.entry_quantum.insert(0, "2")
        self.entry_quantum.grid(row=r, column=0, sticky="e", padx=8, pady=4)

        # Nombre
        r += 1
        ctk.CTkLabel(self, text="Nombre:").grid(row=r, column=0, sticky="w", padx=8)
        self.entry_nombre = ctk.CTkEntry(self)
        self.entry_nombre.grid(row=r, column=0, sticky="ew", padx=(80, 8), pady=4)

        # RAM (decorativo)
        r += 1
        ctk.CTkLabel(self, text="RAM (MB):").grid(row=r, column=0, sticky="w", padx=8)
        self.entry_ram = ctk.CTkEntry(self, width=90)
        self.entry_ram.insert(0, "128")
        self.entry_ram.grid(row=r, column=0, sticky="e", padx=8, pady=4)

        # CPU (ticks)
        r += 1
        ctk.CTkLabel(self, text="CPU (ticks):").grid(row=r, column=0, sticky="w", padx=8)
        self.entry_cpu = ctk.CTkEntry(self, width=90)
        self.entry_cpu.insert(0, "1")
        self.entry_cpu.grid(row=r, column=0, sticky="e", padx=8, pady=4)

        # Llegada
        r += 1
        ctk.CTkLabel(self, text="Llegada:").grid(row=r, column=0, sticky="w", padx=8)
        self.entry_llegada = ctk.CTkEntry(self, width=90)
        self.entry_llegada.insert(0, "0")
        self.entry_llegada.grid(row=r, column=0, sticky="e", padx=8, pady=4)

        # Quantum “decorativo” (lo dejas si lo usas para mostrar algo)
        r += 1
        ctk.CTkLabel(self, text="Quantum:").grid(row=r, column=0, sticky="w", padx=8)
        self.entry_quantum2 = ctk.CTkEntry(self, width=90)
        self.entry_quantum2.insert(0, "1")
        self.entry_quantum2.grid(row=r, column=0, sticky="e", padx=8, pady=4)

        # Botones
        r += 1
        ctk.CTkButton(self, text="Agregar Proceso", command=self._agregar_proceso).grid(
            row=r, column=0, padx=8, pady=(6, 10), sticky="ew")

        r += 1
        ctk.CTkButton(self, text="► Iniciar", command=self._iniciar).grid(
            row=r, column=0, padx=8, pady=4, sticky="ew")
        r += 1
        ctk.CTkButton(self, text="⏸ Pausar", command=self._pausar).grid(
            row=r, column=0, padx=8, pady=4, sticky="ew")
        r += 1
        ctk.CTkButton(self, text="↻ Reiniciar", command=self._reiniciar).grid(
            row=r, column=0, padx=8, pady=4, sticky="ew")

        r += 1
        ctk.CTkButton(self, text="🗎 Ver Tabla de Eficiencia", command=self._abrir_tabla).grid(
            row=r, column=0, padx=8, pady=(8, 8), sticky="ew")

        r += 1
        self.lbl_estado = ctk.CTkLabel(self, text="Listo.")
        self.lbl_estado.grid(row=r, column=0, sticky="w", padx=8, pady=(4, 8))

    # -------------------- acciones --------------------

    def _leer_int(self, entry, default=0) -> int:
        try:
            return int(entry.get())
        except Exception:
            return default

    def _agregar_proceso(self):

        def _i(entry, default=0):
            try:
                return int(entry.get())
            except Exception:
                return default

        nombre  = (self.entry_nombre.get() or "").strip()
        if not nombre:
            # nombre por defecto si está vacío
            try:
                n = len(self.planificador.obtener_procesos()) + 1
            except Exception:
                n = 1
            nombre = f"P{n}"

        cpu      = _i(self.entry_cpu, 1)          # <-- CPU correcto
        llegada  = _i(self.entry_llegada, 0)      # <-- Llegada correcta

        # si el usuario cambió quantum, actualízalo en el planificador (para RR)
        if hasattr(self, "entry_quantum") and hasattr(self.planificador, "set_quantum"):
            self.planificador.set_quantum(_i(self.entry_quantum, 2))

        # Alta en el planificador
        self.planificador.agregar_proceso(nombre=nombre, cpu=cpu, llegada=llegada)

        # Refrescos UI
        if getattr(self.master, "panel_estado", None) and hasattr(self.master.panel_estado, "refrescar_tabla"):
            self.master.panel_estado.refrescar_tabla()

        # Actualiza filas del gantt (panel ejecución)
        try:
            procs = list(self.planificador.obtener_procesos())
            top = self.winfo_toplevel()
            if hasattr(top, "panel_ejecucion") and hasattr(top.panel_ejecucion, "set_procesos_base"):
                top.panel_ejecucion.set_procesos_base(procs)
        except Exception:
            pass

        self.lbl_estado.configure(text=f"Proceso agregado: {nombre}")

    

    def _iniciar(self):
        alg = self.cbo_alg.get().strip()
        q = self._leer_int(self.entry_quantum, 2)
        if callable(self._ejecutar_algoritmo):
            # VentanaPrincipal.iniciar_simulacion(algorithm, quantum)
            self._ejecutar_algoritmo(algorithm=alg, quantum=q)
        self.lbl_estado.configure(text=f"Iniciando simulación ({alg})...")

    def _pausar(self):
        top = self.winfo_toplevel()
        if hasattr(top, "detener_simulacion"):
            top.detener_simulacion()
        self.lbl_estado.configure(text="Simulación pausada.")

    def _reiniciar(self):
        top = self.winfo_toplevel()
        if hasattr(top, "reiniciar_simulacion"):
            top.reiniciar_simulacion()
        self.lbl_estado.configure(text="Simulación reiniciada.")

    def _abrir_tabla(self):
        if callable(self._mostrar_tabla):
            self._mostrar_tabla()
