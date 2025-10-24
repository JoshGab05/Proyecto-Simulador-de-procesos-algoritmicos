# interfaz_grafica/panel_ejecucion.py
from __future__ import annotations
import customtkinter as ctk


class PanelEjecucion(ctk.CTkFrame):
    """
    Panel de ejecución con un Gantt sencillo.
    Firma flexible:
      - (master, planificador)  o  (master, gestor, planificador)
    API esperada por VentanaPrincipal:
      - set_titulo(texto)
      - set_procesos_base(lista_de_procesos)
      - pintar_tick(nombre_o_pid, t, simbolo="X")
      - marcar(...), pintar(...)  (alias)
      - limpiar()
    """
    def __init__(self, master, *args):
        super().__init__(master)
        self.gestor = None
        self.planificador = None

        if len(args) >= 2:
            self.gestor, self.planificador = args[0], args[1]
        elif len(args) == 1:
            self.planificador = args[0]
        else:
            raise TypeError("PanelEjecucion requiere al menos 'planificador'")

        self._titulo = "Tabla de Ejecucion de procesos"
        self._max_t = 30  # columnas (0..19)
        self._row_names = []  # nombres de procesos
        self._row_index = {}  # nombre -> índice de fila

        # Encabezado
        self.frame_head = ctk.CTkFrame(self)
        self.frame_head.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        self.lbl_titulo = ctk.CTkLabel(self.frame_head, text=self._titulo + " - FCFS",
                                       font=ctk.CTkFont(size=16, weight="bold"))
        self.lbl_titulo.pack(side="left", padx=8)

       # self.lbl_info = ctk.CTkLabel(self.frame_head, text="Tiempo: 0 ticks     CPU: IDLE | Alg: -")
       # self.lbl_info.pack(side="right", padx=8)

        # Canvas
        self.canvas = ctk.CTkCanvas(self, width=780, height=360, bg="#111111", highlightthickness=0)
        self.canvas.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._cell_w = 28
        self._cell_h = 22
        self._top_pad = 26
        self._left_pad = 60

        self._dibujar_grid()

    # ---------- API ----------

    def set_titulo(self, texto: str):
        self._titulo = texto or self._titulo
        self.lbl_titulo.configure(text=f"Tabla de Procesos - {self._titulo}")

    def set_procesos_base(self, procesos):
        # Establece nombres de filas según lista de procesos
        names = []
        for p in procesos or []:
            nombre = getattr(p, "nombre", None)
            pid = getattr(p, "pid", getattr(p, "id", None))
            names.append(str(nombre or pid or "?"))
        if not names:
            names = ["A", "B", "C"]
        self._row_names = names
        self._row_index = {n: i for i, n in enumerate(self._row_names)}
        self._dibujar_grid()

    def limpiar(self):
        self.canvas.delete("all")
        self._dibujar_grid()

    def pintar_tick(self, nombre_o_pid, t, simbolo="X"):
        """Pinta un símbolo en la celda (fila segun nombre, columna t)."""
        if t is None:
            return
        col = int(t)  # 0..N
        if col < 0 or col >= self._max_t:
            # Auto-expandir un poco si nos pasamos
            self._max_t = max(self._max_t, col + 5)
            self._dibujar_grid()

        name = str(nombre_o_pid)
        # si no existe la fila, la agregamos al final
        if name not in self._row_index:
            self._row_index[name] = len(self._row_names)
            self._row_names.append(name)
            self._dibujar_grid()

        row = self._row_index[name]
        x0 = self._left_pad + col * self._cell_w + 4
        y0 = self._top_pad + row * self._cell_h + 4
        x1 = x0 + self._cell_w - 8
        y1 = y0 + self._cell_h - 8

        if simbolo.upper() == "O":
            self.canvas.create_oval(x0, y0, x1, y1, outline="#ffaa00")
        else:
            # 'X' por defecto
            self.canvas.create_line(x0, y0, x1, y1, fill="#ffffff")
            self.canvas.create_line(x0, y1, x1, y0, fill="#ffffff")

    # alias compatibles
    def marcar(self, nombre_o_pid, t, simbolo="X"):
        self.pintar_tick(nombre_o_pid, t, simbolo)

    def pintar(self, nombre_o_pid, t, simbolo="X"):
        self.pintar_tick(nombre_o_pid, t, simbolo)

    def pintar_fin(self, nombre: str, t: int):
        """Marca fin de un proceso en el tick 't' (no en t+1).Debe usar el mismo mecanismo de coordenadas que 'pintar_tick'."""
        try:
            # Si usas una tabla: self._set_cell(nombre, t, "○")
            # Si usas canvas, reemplaza por create_text en la celda (nombre, t):
            self._pintar_simbolo(nombre, t, "○")  # reutiliza tu helper interno si lo tienes
        except Exception:
            pass


    # ---------- helpers de dibujo ----------

    def _dibujar_grid(self):
        self.canvas.delete("all")

        # Ejes de tiempo (encabezado)
        for c in range(self._max_t):
            x = self._left_pad + c * self._cell_w + self._cell_w / 2
            self.canvas.create_text(x, 12, text=str(c), fill="#cccccc", font=("Arial", 10))

        # Líneas verticales y horizontales
        # filas (procesos)
        n_rows = max(1, len(self._row_names))
        for r in range(n_rows + 1):
            y = self._top_pad + r * self._cell_h
            self.canvas.create_line(self._left_pad, y,
                                    self._left_pad + self._max_t * self._cell_w, y,
                                    fill="#2a2a2a")

        for c in range(self._max_t + 1):
            x = self._left_pad + c * self._cell_w
            self.canvas.create_line(x, self._top_pad,
                                    x, self._top_pad + n_rows * self._cell_h,
                                    fill="#2a2a2a")

        # Nombres de las filas
        for i, name in enumerate(self._row_names or ["A", "B", "C"]):
            y = self._top_pad + i * self._cell_h + self._cell_h / 2
            self.canvas.create_text(self._left_pad - 20, y, text=name, fill="#dddddd", anchor="e")
