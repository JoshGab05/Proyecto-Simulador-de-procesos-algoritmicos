# interfaz_grafica/panel_ejecucion.py
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from interfaz_grafica.grafico_gantt import generar_grafico_gantt


def _get_attr(obj, key, default=None):
    """Obtiene un atributo o clave de un objeto o diccionario."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


class PanelEjecucion(ctk.CTkFrame):
    """
    Panel dinámico que muestra:
      - Barras de progreso por proceso.
      - Gráfico Gantt actualizado en tiempo real.
      - Estado de CPU y contador de tiempo.
    """

    def __init__(self, master):
        super().__init__(master)
        self.progresos = {}
        self.segmentos = []
        self.canvas = None
        self.fig = None
        self.ax = None
        self.tiempo_total = 0
        self.colores = {}
        self.algoritmo_actual = "RR"

        # ==========================================================
        # TÍTULO
        # ==========================================================
        ctk.CTkLabel(
            self,
            text="Ejecución de Procesos",
            font=("Arial", 20, "bold")
        ).pack(pady=(8, 0))

        # ==========================================================
        # BLOQUE DE ESTADO GENERAL (debajo del título)
        # ==========================================================
        estado_frame = ctk.CTkFrame(self, fg_color="transparent")
        estado_frame.pack(fill="x", pady=(4, 10))

        self.lbl_tiempo = ctk.CTkLabel(
            estado_frame,
            text="Tiempo: 0 ticks",
            font=("Arial", 14)
        )
        self.lbl_tiempo.pack(anchor="center", pady=(2, 2))

        self.lbl_estado_cpu = ctk.CTkLabel(
            estado_frame,
            text="CPU: IDLE | Alg: RR",
            font=("Consolas", 13)
        )
        self.lbl_estado_cpu.pack(anchor="center")

        # ==========================================================
        # BARRAS DE PROGRESO
        # ==========================================================
        self.frame_barras = ctk.CTkScrollableFrame(self, width=460, height=250)
        self.frame_barras.pack(fill="x", padx=8, pady=(0, 10))

        # ==========================================================
        # GRÁFICO GANTT (dinámico según algoritmo)
        # ==========================================================
        self.frame_grafico = ctk.CTkFrame(self, height=250)
        self.frame_grafico.pack(fill="both", expand=False, padx=8, pady=(0, 10))

        self.lbl_titulo_gantt = ctk.CTkLabel(
            self.frame_grafico,
            text="Diagrama Gantt",
            font=("Arial", 16, "italic")
        )
        self.lbl_titulo_gantt.pack(pady=(5, 0))

        # Mantener tamaño estable
        self.update_idletasks()
        self.pack_propagate(False)

    # ---------------------------------------------------------
    # MÉTODOS PRINCIPALES
    # ---------------------------------------------------------
    def inicializar_procesos(self, procesos, algoritmo_nombre="RR"):
        """Crea las barras iniciales para los procesos agregados."""
        self.algoritmo_actual = algoritmo_nombre
        for widget in self.frame_barras.winfo_children():
            widget.destroy()

        self.progresos.clear()
        self.segmentos.clear()
        self.colores.clear()

        # Paleta de colores predefinida
        base_colors = ["#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899"]

        for i, p in enumerate(procesos):
            nombre = _get_attr(p, "nombre", f"P{i+1}")
            total = _get_attr(p, "cpu_total", _get_attr(p, "duracion", 1))
            color = base_colors[i % len(base_colors)]

            frame = ctk.CTkFrame(self.frame_barras)
            frame.pack(fill="x", padx=4, pady=3)

            ctk.CTkLabel(frame, text=f"{nombre}", width=100).pack(side="left", padx=4)
            bar = ctk.CTkProgressBar(frame, progress_color=color)
            bar.pack(side="left", fill="x", expand=True, padx=6)
            bar.set(0)

            self.progresos[nombre] = {"bar": bar, "total": total, "ejecutado": 0}
            self.colores[nombre] = color

        self.lbl_tiempo.configure(text="Tiempo: 0 ticks")
        self.lbl_estado_cpu.configure(text=f"CPU: IDLE | Alg: {algoritmo_nombre}")
        self.lbl_titulo_gantt.configure(text=f"Diagrama Gantt - {algoritmo_nombre}")

    def actualizar_tick(self, t, proceso_actual, cola_ready):
        """Se llama cada tick para actualizar progreso y gráfico."""
        self.tiempo_total = t
        self.lbl_tiempo.configure(text=f"Tiempo: {t} ticks")

        # Mostrar estado del sistema
        if proceso_actual:
            self.lbl_estado_cpu.configure(
                text=f"CPU: {proceso_actual.nombre} (PID {proceso_actual.pid}) | Alg: {self.algoritmo_actual}"
            )
        else:
            self.lbl_estado_cpu.configure(text=f"CPU: IDLE | Alg: {self.algoritmo_actual}")

        # Actualizar título del gráfico según algoritmo actual
        self.lbl_titulo_gantt.configure(text=f"Diagrama Gantt - {self.algoritmo_actual}")

        if not proceso_actual:
            return

        nombre = _get_attr(proceso_actual, "nombre", "P?")
        self.segmentos.append({"t": t, "nombre": nombre, "duracion": 1})

        # Actualizar progreso de barra
        if nombre in self.progresos:
            p = self.progresos[nombre]
            p["ejecutado"] = min(p["ejecutado"] + 1, p["total"])
            progreso = p["ejecutado"] / p["total"]
            p["bar"].set(progreso)

        self.actualizar_grafico()

    def actualizar_grafico(self):
        """Redibuja el gráfico Gantt."""
        if not self.segmentos:
            return

        fig, ax = generar_grafico_gantt(self.segmentos, show=False)
        self.fig, self.ax = fig, ax

        for widget in self.frame_grafico.winfo_children():
            if not isinstance(widget, ctk.CTkLabel):
                widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=self.frame_grafico)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, pady=5)
        self.canvas = canvas

    def limpiar(self):
        """Limpia el panel para nueva simulación."""
        self.segmentos.clear()
        self.tiempo_total = 0
        self.lbl_tiempo.configure(text="Tiempo: 0 ticks")
        self.lbl_estado_cpu.configure(text=f"CPU: IDLE | Alg: {self.algoritmo_actual}")
        self.lbl_titulo_gantt.configure(text=f"Diagrama Gantt - {self.algoritmo_actual}")

        for p in self.progresos.values():
            p["bar"].set(0)
            p["ejecutado"] = 0

        for widget in self.frame_grafico.winfo_children():
            if not isinstance(widget, ctk.CTkLabel):
                widget.destroy()
