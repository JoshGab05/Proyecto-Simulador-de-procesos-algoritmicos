# interfaz_grafica/cuadricula_tiempo.py
from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional


class CuadriculaTiempo(ttk.Frame):
    """
    Tabla fija con columnas 0..(num_cols-1) y una columna 'Proceso'.
    Permite marcar celdas por (nombre_proceso, tiempo) con un carácter (por ej. 'X').
    """
    def __init__(self, master: tk.Misc, num_cols: int = 30, *, col_width: int = 26, proc_col_width: int = 110):
        super().__init__(master)
        self.num_cols = int(num_cols)
        self._map_nombre_iid: Dict[str, str] = {}
        self._marcas: Dict[str, List[int]] = {}

        # --- Treeview ---
        cols = ["Proceso"] + [str(i) for i in range(self.num_cols)]
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=12)
        # Encabezados
        self.tree.heading("Proceso", text="Proceso")
        self.tree.column("Proceso", width=proc_col_width, anchor="w", stretch=False)
        for i in range(self.num_cols):
            c = str(i)
            self.tree.heading(c, text=c)
            self.tree.column(c, width=col_width, anchor="center", stretch=False)

        # Scrollbars
        yscroll = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        xscroll = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)

        # Layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")

        # Estilo básico (mejor contraste en modo oscuro de CTk)
        style = ttk.Style(self)
        try:
            style.theme_use(style.theme_use())
        except Exception:
            pass
        style.configure("Treeview", rowheight=22)

    # ----------------- API -----------------
    def limpiar(self):
        for iid in self.tree.get_children(""):
            self.tree.delete(iid)
        self._map_nombre_iid.clear()
        self._marcas.clear()

    def set_filas(self, nombres: List[str]):
        """Crea una fila por nombre de proceso (en orden dado)."""
        self.limpiar()
        for nombre in nombres:
            iid = self.tree.insert("", "end", values=[nombre] + [""] * self.num_cols)
            self._map_nombre_iid[nombre] = iid
            self._marcas[nombre] = []

    def marcar(self, tiempo: int, nombre: str, char: str = "X"):
        """Marca la celda (nombre, tiempo) con 'char' si existe la fila y la columna."""
        if nombre not in self._map_nombre_iid:
            return
        if not (0 <= tiempo < self.num_cols):
            return
        iid = self._map_nombre_iid[nombre]
        vals = list(self.tree.item(iid, "values"))
        # Columna 0 es "Proceso"; la 1 equivale a tiempo 0
        idx = 1 + tiempo
        if idx < len(vals):
            vals[idx] = char
            self.tree.item(iid, values=vals)
            try:
                t = int(tiempo)
            except Exception:
                t = None
            if t is not None and t not in self._marcas[nombre]:
                self._marcas[nombre].append(t)

    def get_marcas(self) -> Dict[str, List[int]]:
        """Devuelve dict nombre -> lista de tiempos marcados (sin duplicados, no ordenado)."""
        return {k: sorted(v) for k, v in self._marcas.items()}

    def get_segmentos(self):
        """
        Segmentos contiguos por proceso a partir de marcas: [{"t": ini, "nombre": p, "duracion": d}, ...]
        """
        segs = []
        for nombre, tiempos in self.get_marcas().items():
            if not tiempos:
                continue
            start = tiempos[0]
            prev = tiempos[0]
            dur = 1
            for t in tiempos[1:]:
                if t == prev + 1:
                    dur += 1
                else:
                    segs.append({"t": start, "nombre": nombre, "duracion": dur})
                    start = t
                    dur = 1
                prev = t
            segs.append({"t": start, "nombre": nombre, "duracion": dur})
        return segs

    def tiempo_max(self) -> int:
        """Último tiempo marcado + 1 (o 0 si vacío)."""
        m = 0
        for ts in self._marcas.values():
            if ts:
                m = max(m, max(ts) + 1)
        return m
