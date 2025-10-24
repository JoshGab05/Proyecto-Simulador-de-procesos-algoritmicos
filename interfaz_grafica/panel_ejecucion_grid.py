from __future__ import annotations
import customtkinter as ctk
from tkinter import Canvas
from typing import Any, Dict, List, Optional


def _get_name(x: Any) -> Optional[str]:
    """Obtiene un nombre de proceso desde dict/obj/str."""
    if x is None:
        return None
    if isinstance(x, dict):
        n = x.get("nombre")
        if n is None:
            for k in ("name", "id", "pid"):
                if k in x:
                    n = str(x[k])
                    break
        return n
    # objeto
    for k in ("nombre", "name", "id", "pid"):
        if hasattr(x, k):
            v = getattr(x, k)
            return str(v)
    # str plano
    if isinstance(x, str):
        return x
    return None


class PanelEjecucionGrid(ctk.CTkFrame):
    """
    Gantt en cuadrícula 0..29 con filas = procesos.
    Dibuja una 'X' en la celda (fila del proceso, columna = tick) cuando
    ese proceso está en CPU.
    """

    def __init__(self, master):
        super().__init__(master)
        self.configure(fg_color="#1c1c1c")

        self.algoritmo: str = "FCFS"
        self.filas: List[str] = []           # nombres de filas (procesos)
        self.t_actual: int = 0

        # --- top bar
        top = ctk.CTkFrame(self, fg_color="#262626")
        top.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        top.grid_columnconfigure(0, weight=1)
        self.lbl_title = ctk.CTkLabel(top, text="Tabla de Procesos - FCFS", anchor="w")
        self.lbl_title.grid(row=0, column=0, sticky="w", padx=8, pady=6)
        self.lbl_tiempo = ctk.CTkLabel(top, text="Tiempo: 0 ticks")
        self.lbl_tiempo.grid(row=0, column=1, sticky="e", padx=8, pady=6)

        # --- cpu header
        self.lbl_cpu = ctk.CTkLabel(self, text="CPU: IDLE | Alg: FCFS", anchor="e")
        self.lbl_cpu.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 6))

        # --- canvas
        self.canvas = Canvas(self, bg="#111111", highlightthickness=0)
        self.canvas.grid(row=2, column=0, sticky="nsew", padx=8, pady=8)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- layout de cuadrícula
        self.left_pad = 70
        self.top_pad = 26
        self.col_gap = 1
        self.row_gap = 6
        self.cell_w = 26
        self.cell_h = 18
        self.cols = 30  # 0..29

        # buffers de dibujo
        self.circulos_fin = {}   # nombre -> (x,y) del circulito de fin
        self._redibujar_base([])

    # --------------- API pública -----------------
    def set_algoritmo(self, nombre: str):
        self.algoritmo = (nombre or "-")
        self.lbl_cpu.configure(text=f"CPU: IDLE | Alg: {self.algoritmo}")
        self.lbl_title.configure(text=f"Tabla de Procesos - {self.algoritmo}")

    def set_procesos_base(self, procesos: List[Any]):
        """Fija filas con los nombres de los procesos y limpia la cuadrícula."""
        filas = []
        for p in procesos or []:
            n = _get_name(p)
            if n and n not in filas:
                filas.append(n)

        self.filas = filas
        self.circulos_fin.clear()
        self._redibujar_base(self.filas)

    def marcar_fin(self, nombre: str, t_fin: int):
        """Marca con un circulito el fin de un proceso en la columna t_fin (si entra en 0..29)."""
        if nombre not in self.filas:
            return
        if not (0 <= int(t_fin) < self.cols):
            return
        r = self.filas.index(nombre)
        x0 = self.left_pad + int(t_fin) * (self.cell_w + self.col_gap) + self.cell_w // 2
        y0 = self.top_pad + r * (self.cell_h + self.row_gap) + self.cell_h // 2
        self.circulos_fin[nombre] = (x0, y0)
        self.canvas.create_oval(x0 - 5, y0 - 5, x0 + 5, y0 + 5, outline="#ff9f1a", width=2)

    def limpiar(self):
        self.circulos_fin.clear()
        self._redibujar_base(self.filas)

    def actualizar_tick(self, t: int, running: Any, ready: List[Any]):
        """
        t: tick actual
        running: dict/obj/str con 'nombre' (None -> IDLE)
        ready: no lo usamos aún, pero se deja para extensiones
        """
        self.t_actual = int(t)
        self.lbl_tiempo.configure(text=f"Tiempo: {self.t_actual} ticks")

        nombre = _get_name(running)
        self.lbl_cpu.configure(text=f"CPU: {nombre if nombre else 'IDLE'} | Alg: {self.algoritmo}")

        if nombre and nombre in self.filas and 0 <= self.t_actual < self.cols:
            r = self.filas.index(nombre)
            x0 = self.left_pad + self.t_actual * (self.cell_w + self.col_gap)
            y0 = self.top_pad + r * (self.cell_h + self.row_gap)
            x1 = x0 + self.cell_w
            y1 = y0 + self.cell_h
            self._draw_x(x0, y0, x1, y1, fill="#ffffff")

    # --------------- internos de dibujo -----------------
    def _redibujar_base(self, filas: List[str]):
        self.canvas.delete("all")

        # líneas verticales (0..29)
        for c in range(self.cols):
            x0 = self.left_pad + c * (self.cell_w + self.col_gap)
            self.canvas.create_text(x0 + self.cell_w / 2, 12, text=str(c), fill="#bbbbbb", font=("Arial", 10))

        # etiquetas izquierda (nombres de proceso)
        for i, name in enumerate(filas):
            y = self.top_pad + i * (self.cell_h + self.row_gap) + self.cell_h / 2
            self.canvas.create_text(self.left_pad - 8, y, text=name, fill="#dddddd", anchor="e", font=("Arial", 12))

        # celdas
        for r in range(len(filas)):
            for c in range(self.cols):
                x0 = self.left_pad + c * (self.cell_w + self.col_gap)
                y0 = self.top_pad + r * (self.cell_h + self.row_gap)
                x1 = x0 + self.cell_w
                y1 = y0 + self.cell_h
                self.canvas.create_rectangle(x0, y0, x1, y1, outline="#3a3a3a")

    def _draw_x(self, x0, y0, x1, y1, fill="#ffffff"):
        pad = 4
        self.canvas.create_line(x0 + pad, y0 + pad, x1 - pad, y1 - pad, fill=fill, width=2)
        self.canvas.create_line(x0 + pad, y1 - pad, x1 - pad, y0 + pad, fill=fill, width=2)
