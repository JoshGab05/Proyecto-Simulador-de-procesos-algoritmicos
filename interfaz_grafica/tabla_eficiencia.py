# interfaz_grafica/tabla_eficiencia.py
import customtkinter as ctk
from tkinter import ttk

def _get(p, k, default=None):
    """Obtiene valores de dict o de objeto."""
    if isinstance(p, dict):
        return p.get(k, default)
    return getattr(p, k, default)

class TablaEficiencia(ctk.CTkToplevel):
    """Ventana que muestra la tabla de eficiencia de los procesos."""
    def __init__(self, master, resultados):
        super().__init__(master)
        self.title("Tabla de Eficiencia")
        self.geometry("950x480")
        self.resizable(True, True)

        # Normalizar estructura de resultados
        if isinstance(resultados, dict):
            self.procesos = list(resultados.get("procesos", resultados.get("resultados", [])))
        else:
            self.procesos = list(resultados)

        # Calcular métricas de eficiencia si faltan
        for p in self.procesos:
            llegada = _get(p, "llegada", _get(p, "instante_llegada", 0))
            cpu = _get(p, "cpu_total", _get(p, "duracion", 0))
            t_inicio = _get(p, "t_inicio", 0)
            t_fin = _get(p, "t_fin", 0)

            retorno = max(0, t_fin - llegada) if t_fin and llegada is not None else 0
            espera = max(0, retorno - (cpu or 0))
            respuesta = max(0, t_inicio - llegada)
            eficiencia = (cpu / retorno) if retorno > 0 else 0.0

            if isinstance(p, dict):
                p.update({
                    "retorno": retorno,
                    "espera": espera,
                    "respuesta": respuesta,
                    "eficiencia": eficiencia
                })
            else:
                setattr(p, "retorno", retorno)
                setattr(p, "espera", espera)
                setattr(p, "respuesta", respuesta)
                setattr(p, "eficiencia", eficiencia)

        # Crear la tabla
        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        columnas = (
            "PID", "Nombre", "Llegada", "CPU", "T. Fin",
            "Retorno", "Espera", "Respuesta", "Eficiencia"
        )
        self.tree = ttk.Treeview(frame, columns=columnas, show="headings", height=16)

        for col in columnas:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=90)

        self.tree.pack(fill="both", expand=True)

        for p in self.procesos:
            self.tree.insert("", "end", values=(
                _get(p, "pid", "-"),
                _get(p, "nombre", "-"),
                _get(p, "llegada", "-"),
                _get(p, "cpu_total", _get(p, "duracion", "-")),
                _get(p, "t_fin", "-"),
                _get(p, "retorno", "-"),
                _get(p, "espera", "-"),
                _get(p, "respuesta", "-"),
                f"{_get(p, 'eficiencia', 0):.2f}"
            ))

        ctk.CTkButton(self, text="Cerrar", command=self.destroy).pack(pady=8)
