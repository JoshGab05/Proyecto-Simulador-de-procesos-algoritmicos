# interfaz_grafica/tabla_eficiencia.py
from __future__ import annotations
import customtkinter as ctk
from tkinter import ttk


def _ga(obj, key, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


class TablaEficiencia(ctk.CTkToplevel):
    """
    Ventana de métricas con formato:
    PID | Nombre | Llegada (ti) | CPU (t) | T. Fin (tf) | Retorno (r=tf-ti) | Espera (w=r-t) | Respuesta (t_inicio-ti) | Eficiencia (t/r)
    Incluye fila de promedios al final.
    """

    COLS = ("PID", "Nombre", "Llegada", "CPU", "T. Fin", "Retorno", "Espera", "Respuesta", "Eficiencia")

    def __init__(self, parent, planificador):
        super().__init__(parent)
        self.title("Tabla de Eficiencia")
        self.geometry("980x520")
        self.minsize(860, 420)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        frame = ctk.CTkFrame(self)
        frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(frame, columns=self.COLS, show="headings", height=16)
        for c in self.COLS:
            self.tree.heading(c, text=c)
        # anchos sugeridos
        widths = [70, 120, 90, 80, 90, 100, 90, 105, 100]
        for c, w in zip(self.COLS, widths):
            self.tree.column(c, width=w, anchor="center", stretch=True)

        yscroll = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=yscroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")

        btn = ctk.CTkButton(self, text="Cerrar", command=self.destroy)
        btn.grid(row=1, column=0, pady=10)

        # ---- Poblar datos ----
        try:
            procesos = list(planificador.obtener_procesos())
        except Exception:
            procesos = getattr(planificador, "_procesos", [])

        filas = []
        for p in procesos:
            pid = _ga(p, "pid")
            nombre = _ga(p, "nombre", f"P{pid}")
            ti = int(_ga(p, "instante_llegada", 0) or 0)
            t = int(_ga(p, "cpu_total", _ga(p, "cpu_restante", 0)) or 0)
            tf = _ga(p, "t_fin", None)
            ti_inicio = _ga(p, "t_inicio", None)

            r = None
            w = None
            resp = None
            eff = None

            if tf is not None:
                r = int(tf) - ti
                w = r - t
                resp = None if ti_inicio is None else (int(ti_inicio) - ti)
                try:
                    eff = round(t / r, 2) if r and r > 0 else None
                except Exception:
                    eff = None

            filas.append((pid, nombre, ti, t,
                          ("" if tf is None else int(tf)),
                          ("" if r is None else r),
                          ("" if w is None else w),
                          ("" if resp is None else resp),
                          ("" if eff is None else eff)))

        # Insertar filas
        for row in filas:
            self.tree.insert("", "end", values=row)

        # Promedios
        def _avg(ii):
            vals = [v[ii] for v in filas if isinstance(v[ii], (int, float))]
            return round(sum(vals) / len(vals), 2) if vals else ""

        avg_tfin = _avg(4)
        avg_r = _avg(5)
        avg_w = _avg(6)
        avg_resp = _avg(7)
        # Promedio de eficiencias individuales (t/r)
        eff_vals = [v[8] for v in filas if isinstance(v[8], (int, float))]
        avg_eff = round(sum(eff_vals) / len(eff_vals), 2) if eff_vals else ""

        self.tree.insert("", "end", values=("", "PROMEDIO", "", "", avg_tfin, avg_r, avg_w, avg_resp, avg_eff))
