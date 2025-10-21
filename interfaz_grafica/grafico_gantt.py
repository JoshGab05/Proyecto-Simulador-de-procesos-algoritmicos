# interfaz_grafica/grafico_gantt.py
import matplotlib
matplotlib.use("Agg")  # Evita conflictos al generar figuras fuera del hilo principal
import matplotlib.pyplot as plt

def generar_grafico_gantt(segmentos, nombre="Round Robin", show=False):
    """
    Genera un gráfico Gantt seguro para usar dentro de Tkinter.
    Cada segmento: {"t": inicio, "nombre": proceso, "duracion": ancho}
    - show=False evita plt.show() en hilos secundarios.
    - Devuelve (fig, ax) para embebido.
    """
    if not segmentos:
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.set_title(f"Diagrama Gantt - {nombre}")
        ax.set_xlabel("Tiempo (ticks)")
        ax.set_ylabel("Procesos")
        ax.grid(axis="x", linestyle="--", alpha=0.6)
        return fig, ax

    procesos = sorted(list({s["nombre"] for s in segmentos}))
    cmap = plt.cm.get_cmap("tab10", len(procesos))
    colores = {p: cmap(i) for i, p in enumerate(procesos)}

    fig, ax = plt.subplots(figsize=(10, 3 + len(procesos) * 0.3))
    for seg in segmentos:
        ax.barh(
            seg["nombre"], seg["duracion"], left=seg["t"],
            color=colores[seg["nombre"]], edgecolor="black"
        )
        ax.text(
            seg["t"] + seg["duracion"] / 2,
            seg["nombre"],
            seg["nombre"],
            ha="center", va="center", color="white", fontsize=8
        )

    ax.set_xlabel("Tiempo (ticks)")
    ax.set_ylabel("Procesos")
    ax.set_title(f"Diagrama Gantt - {nombre}")
    ax.set_xlim(0, max(s["t"] + s["duracion"] for s in segmentos) + 1)
    ax.grid(axis="x", linestyle="--", alpha=0.6)

    if show:
        try:
            plt.show()
        except Exception:
            pass

    return fig, ax

