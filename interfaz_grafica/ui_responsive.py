# interfaz_grafica/ui_responsive.py
from __future__ import annotations
import tkinter as tk
try:
    import customtkinter as ctk
except Exception:
    ctk = None  # por si se ejecuta sin CTk

def _is_container(widget: tk.Widget) -> bool:
    # Consideramos contenedores comunes
    names = (
        "Frame", "Labelframe", "Panedwindow",
        "CTkFrame", "CTkScrollableFrame", "CTkTabview",
        "Canvas"
    )
    cls = widget.__class__.__name__
    return any(n in cls for n in names)

def _configure_container(w: tk.Widget):
    # Hacer crecer el contenedor y su celda
    parent = w.nametowidget(w.winfo_parent()) if w.winfo_parent() else None
    if parent is not None:
        try:
            info = w.grid_info()
            r = int(info.get("row", 0)); c = int(info.get("column", 0))
            parent.grid_rowconfigure(r, weight=1)
            parent.grid_columnconfigure(c, weight=1)
        except Exception:
            pass

def _walk_and_make_sticky(root: tk.Misc):
    # Recorre jerarquía y aplica sticky/expand fill
    for child in root.winfo_children():
        # Si usa grid, pegajoso en ambas direcciones
        try:
            if child.grid_info():
                child.grid_configure(sticky="nsew")
        except Exception:
            # Si usa pack, fill/expand
            try:
                if child.pack_info():
                    child.pack_configure(fill="both", expand=True)
            except Exception:
                pass

        if _is_container(child):
            _configure_container(child)
            # Dentro del contenedor, su primera fila/columna deben crecer
            try:
                child.grid_rowconfigure(0, weight=1)
                child.grid_columnconfigure(0, weight=1)
            except Exception:
                pass

        _walk_and_make_sticky(child)

def enable_responsive(app: tk.Tk | tk.Toplevel, *,
                      width: int = 1200,
                      height: int = 750,
                      minw: int = 980,
                      minh: int = 600,
                      window_scale: float = 0.95,
                      widget_scale: float = 0.95):
    """Convierte la ventana y su contenido en redimensionables."""
    # Tamaños de ventana
    app.title(app.title() or "Aplicación")
    try:
        app.geometry(f"{width}x{height}")
        app.minsize(minw, minh)
        app.resizable(True, True)
    except Exception:
        pass

    # Escalado en CustomTkinter (opcional)
    if ctk is not None:
        try:
            ctk.set_window_scaling(window_scale)
            ctk.set_widget_scaling(widget_scale)
        except Exception:
            pass

    # El root debe tener filas/columnas elásticas
    try:
        # Si el diseño principal es 3 columnas (izq/centro/der)
        app.grid_columnconfigure((0, 1, 2), weight=1, uniform="cols")
        app.grid_rowconfigure(0, weight=1)
    except Exception:
        # Si no usa grid en root, no pasa nada
        pass

    # Hacer sticky todos los widgets hijos
    _walk_and_make_sticky(app)

def make_toplevel_responsive(top: tk.Toplevel,
                             width: int = 900, height: int = 500,
                             minw: int = 720, minh: int = 380):
    """Para ventanas secundarias (Tabla de Eficiencia, etc.)."""
    try:
        top.geometry(f"{width}x{height}")
        top.minsize(minw, minh)
        top.resizable(True, True)
        top.grid_rowconfigure(0, weight=1)
        top.grid_columnconfigure(0, weight=1)
        _walk_and_make_sticky(top)
    except Exception:
        pass
