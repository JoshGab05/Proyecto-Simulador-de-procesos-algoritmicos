# interfaz_grafica/panel_estado.py

import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class PanelEstado(ctk.CTkFrame):
    def __init__(self, master, gestor_memoria, planificador):
        super().__init__(master)
        self.gestor_memoria = gestor_memoria
        self.planificador = planificador

        # ---------- Título ----------
        self.label_titulo = ctk.CTkLabel(self, text="Estado de Memoria", font=("Arial", 24))
        self.label_titulo.pack(pady=(10, 8))

        # ---------- Barra de memoria ----------
        self.progress = ctk.CTkProgressBar(self)
        self.progress.set(0)
        self.progress.pack(fill="x", padx=20, pady=(0, 6))

        self.label_mem = ctk.CTkLabel(self, text="Memoria usada: 0 MB / 0 MB (0.0%)")
        self.label_mem.pack(pady=(0, 10))

        # ---------- Texto de estado de procesos ----------
        self.textbox_estado = ctk.CTkTextbox(self, height=260, width=520)
        self.textbox_estado.pack(fill="both", expand=False, padx=20, pady=(0, 10))
        self.textbox_estado.configure(state="disabled")

        # ---------- Tiempo de simulación ----------
        self.label_tiempo = ctk.CTkLabel(self, text="Tiempo de simulación: 0")
        self.label_tiempo.pack(pady=(0, 8))

        # ---------- Gráfica de memoria ----------
        fig = Figure(figsize=(5.4, 2.2), dpi=100)
        self.ax = fig.add_subplot(111)
        self.ax.set_title("Uso de memoria (%)")
        self.ax.set_ylim(0, 100)
        self.ax.set_xlim(0, 40)
        self.ax.grid(True, alpha=0.2)
        self.mem_line, = self.ax.plot([], [], linewidth=2)

        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.get_tk_widget().pack(fill="x", padx=12, pady=(0, 12))

        self._t_hist = []
        self._m_hist = []

        # Pintar estado inicial
        self.actualizar_estado()

    # ====================== UTILIDADES DE MEMORIA ======================

    def _mem_total(self):
        # intenta varias convenciones comunes
        gm = self.gestor_memoria
        for attr in ("memoria_total", "total_memoria", "capacidad_total"):
            if hasattr(gm, attr):
                return int(getattr(gm, attr))
        # por si hay método
        for m in ("obtener_memoria_total", "get_mem_total"):
            if hasattr(gm, m):
                try:
                    return int(getattr(gm, m)())
                except Exception:
                    pass
        return 0

    def _mem_usada(self):
        gm = self.gestor_memoria
        # atributos comunes
        for attr in ("memoria_ocupada", "memoria_usada", "uso_actual"):
            if hasattr(gm, attr):
                return int(getattr(gm, attr))
        # métodos comunes
        for m in ("obtener_memoria_usada", "get_memoria_usada", "get_used"):
            if hasattr(gm, m):
                try:
                    return int(getattr(gm, m)())
                except Exception:
                    pass
        return 0

    # ====================== ACTUALIZACIÓN DE UI ======================

    def actualizar_estado(self):
        plan = self.planificador

        # ----- texto de procesos -----
        lineas = []

        # En ejecución
        lineas.append("Procesos en ejecución:")
        actual = plan.proceso_actual
        if actual is not None:
            lineas.append(f"  {actual}")
        else:
            lineas.append("  (ninguno)")

        # Cola de espera (excluye finalizados y al actual)
        lineas.append("\nCola de espera:")
        pid_actual = getattr(actual, "pid", None)
        hubo_espera = False
        for p in plan.obtener_procesos():
            if p.esta_terminado():
                continue
            if pid_actual is not None and p.pid == pid_actual:
                continue
            lineas.append(f"  {p}")
            hubo_espera = True
        if not hubo_espera:
            lineas.append("  (vacía)")

        # Historial (finalizados)
        lineas.append("\nHistorial de procesos:")
        hist = getattr(plan, "historial", [])
        if hist:
            for p in hist:
                lineas.append(f"  {p}")
        else:
            lineas.append("  (vacío)")

        texto = "\n".join(lineas)

        # Escribir en el textbox
        self.textbox_estado.configure(state="normal")
        self.textbox_estado.delete("1.0", "end")
        self.textbox_estado.insert("end", texto)
        self.textbox_estado.configure(state="disabled")

        # Tiempo
        try:
            self.label_tiempo.configure(text=f"Tiempo de simulación: {plan.tiempo_actual}")
        except Exception:
            pass

        # ----- memoria -----
        total = self._mem_total()
        usada = min(self._mem_usada(), total) if total else self._mem_usada()
        pct = (usada / total * 100.0) if total else 0.0

        # Barra y etiqueta
        try:
            self.progress.set(pct / 100.0)
        except Exception:
            pass
        self.label_mem.configure(text=f"Memoria usada: {usada} MB / {total} MB ({pct:.1f}%)")

        # Gráfica
        self._t_hist.append(len(self._t_hist))
        self._m_hist.append(pct)
        # Mantener 40 puntos
        if len(self._t_hist) > 40:
            self._t_hist = self._t_hist[-40:]
            self._m_hist = self._m_hist[-40:]

        self.mem_line.set_data(self._t_hist, self._m_hist)
        self.ax.set_xlim(0, max(40, len(self._t_hist)))
        self.canvas.draw()
