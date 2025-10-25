# interfaz_grafica/tabla_eficiencia_grid.py
from __future__ import annotations
import customtkinter as ctk
from tkinter import ttk
from typing import Any, List


def _ga(obj, k, d=None):
    if isinstance(obj, dict):
        return obj.get(k, d)
    return getattr(obj, k, d)


class TablaEficienciaGrid(ctk.CTkToplevel):
    """
    Formato:
    PID | Nombre | Llegada (ti) | CPU (t) | T. Fin (tf) | Retorno (r=tf-ti) | Espera (w=r-t) | Respuesta (t_inicio-ti) | Eficiencia (t/r)
    + fila de promedios.
    """
    COLS = ("PID","Nombre","Llegada","CPU","T. Fin","Retorno","Espera","Respuesta","Eficiencia")

    def __init__(self, parent, planificador):
        super().__init__(parent)
        self.title("Tabla de Eficiencia")
        self.geometry("980x520")
        self.minsize(880, 420)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        frame = ctk.CTkFrame(self)
        frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(frame, columns=self.COLS, show="headings", height=16)
        for col, w in zip(self.COLS, [60,120,80,70,80,80,80,95,90]):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center", stretch=True)
        yscroll = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=yscroll.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")

        ctk.CTkButton(self, text="Cerrar", command=self.destroy).grid(row=1, column=0, pady=10)

        # Poblar
        try:
            procesos = list(planificador.obtener_procesos())
        except Exception:
            procesos = getattr(planificador, "_procesos", [])

        filas = []
        for p in procesos:
            pid = _ga(p,"pid")
            nombre = _ga(p,"nombre", f"P{pid}")
            ti = int(_ga(p,"instante_llegada",0) or 0)
            t = int(_ga(p,"cpu_total", _ga(p,"cpu_restante",0)) or 0)
            tf = _ga(p,"t_fin", None)
            ti_ini = _ga(p,"t_inicio", None)
            r = w = resp = eff = None
            if tf is not None:
                r = int(tf) - ti
                w = r - t
                resp = None if ti_ini is None else int(ti_ini) - ti
                eff = round(t / r, 2) if r and r>0 else None
            filas.append((pid, nombre, ti, t,
                          "" if tf is None else int(tf),
                          "" if r is None else r,
                          "" if w is None else w,
                          "" if resp is None else resp,
                          "" if eff is None else eff))

        for row in filas:
            self.tree.insert("", "end", values=row)

        # Promedios (solo en columnas numéricas relevantes)
        def _avg(idx):
            vals = [v[idx] for v in filas if isinstance(v[idx], (int,float))]
            return round(sum(vals)/len(vals),2) if vals else ""
        avg_tf = _avg(4); avg_r = _avg(5); avg_w = _avg(6); avg_resp = _avg(7)
        eff_vals = [v[8] for v in filas if isinstance(v[8], (int,float))]
        avg_eff = round(sum(eff_vals)/len(eff_vals),2) if eff_vals else ""
        self.tree.insert("", "end", values=("", "PROMEDIO", "", "", avg_tf, avg_r, avg_w, avg_resp, avg_eff))
