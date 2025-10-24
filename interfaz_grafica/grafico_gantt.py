# interfaz_grafica/grafico_gantt.py
# Módulo simplificado: mantenido por compatibilidad si lo usas en otro lado
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def generar_grafico_gantt(segmentos, nombre="Algoritmo", show=False):
    """
    (Compat) Genera un gráfico de Gantt simple desde una lista de
    segmentos: [{"t": inicio, "nombre": proceso, "duracion": ancho}, ...]
    Devuelve (fig, ax). En el panel_ejecucion ya no se usa crear/ destruir,
    se llama a un canvas persistente; este helper queda por si lo necesitas.
    """
    fig, ax = plt.subplots(figsize=(6.5, 3.2), dpi=100)
    if not segmentos:
        ax.set_title(f"Tabla de Procesos - {nombre}")
        ax.set_xlabel("Tiempo (ticks)")
        ax.set_ylabel("Proceso")
        ax.grid(axis="x", linestyle="--", alpha=0.6)
        return fig, ax

    procesos = []
    for s in segmentos:
        if s["nombre"] not in procesos:
            procesos.append(s["nombre"])
    ymap = {p: i for i, p in enumerate(procesos)}

    for seg in segmentos:
        y = ymap[seg["nombre"]]
        ax.barh(y, seg["duracion"], left=seg["t"], height=0.6, edgecolor="black", alpha=0.85)
        ax.text(seg["t"] + seg["duracion"] / 2, y, seg["nombre"], ha="center", va="center", fontsize=9, color="white")

    ax.set_yticks(list(ymap.values()), list(ymap.keys()))
    ax.set_xlim(0, max(s["t"] + s["duracion"] for s in segmentos) + 1)
    ax.set_xlabel("Tiempo (ticks)")
    ax.set_ylabel("Proceso")
    ax.set_title(f"Tabla de Procesos - {nombre}")
    ax.grid(axis="x", linestyle="--", alpha=0.6)

    if show:
        try:
            plt.show()
        except Exception:
            pass
    return fig, ax
