# interfaz_grafica/panel_control.py
import tkinter as tk
import customtkinter as ctk
from logica.proceso import Proceso


def _to_int(s: str, default: int = 0) -> int:
    try:
        return int(str(s).strip())
    except Exception:
        return default


class PanelControl(ctk.CTkScrollableFrame):
    def __init__(
        self,
        master,
        gestor_memoria,
        planificador,
        panel_estado,
        ejecutar_algoritmo_callback=None,   # callback visual (RR/FCFS y futuros)
        mostrar_tabla_callback=None,        # para abrir la tabla de eficiencia
    ):
        super().__init__(master, width=350, height=620)

        self.gestor_memoria = gestor_memoria
        self.planificador = planificador
        self.panel_estado = panel_estado
        self.ejecutar_algoritmo_callback = ejecutar_algoritmo_callback
        self.mostrar_tabla_callback = mostrar_tabla_callback

        # ---------- Título ----------
        ctk.CTkLabel(self, text="Control de Simulación", font=("Arial", 22)).pack(pady=(8, 6))

        # ---------- Selección de algoritmo ----------
        row = ctk.CTkFrame(self)
        row.pack(fill="x", padx=10, pady=(0, 6))
        ctk.CTkLabel(row, text="Algoritmo:").pack(side="left", padx=(0, 6))
        self.alg_var = ctk.StringVar(value="FCFS")
        ctk.CTkOptionMenu(
            row,
            values=["FCFS", "SJF", "SRTF", "RR"],
            variable=self.alg_var,
            command=self._on_alg_change,
        ).pack(side="left")

        # ---------- Quantum (solo RR) ----------
        qrow = ctk.CTkFrame(self)
        qrow.pack(fill="x", padx=10, pady=(0, 6))
        ctk.CTkLabel(qrow, text="Quantum (RR):").pack(side="left", padx=(0, 6))
        self.quantum_var = tk.StringVar(value="2")
        ctk.CTkEntry(qrow, width=60, textvariable=self.quantum_var).pack(side="left")
        ctk.CTkButton(qrow, text="Aplicar", command=self._apply_quantum).pack(side="left", padx=6)

        # ---------- Formulario de Proceso ----------
        form = ctk.CTkFrame(self)
        form.pack(fill="x", padx=10, pady=(6, 6))
        ctk.CTkLabel(form, text="Nombre:").grid(row=0, column=0, sticky="e", padx=4, pady=4)
        ctk.CTkLabel(form, text="RAM (MB):").grid(row=1, column=0, sticky="e", padx=4, pady=4)
        ctk.CTkLabel(form, text="CPU (ticks):").grid(row=2, column=0, sticky="e", padx=4, pady=4)
        ctk.CTkLabel(form, text="Llegada:").grid(row=3, column=0, sticky="e", padx=4, pady=4)
        ctk.CTkLabel(form, text="Quantum:").grid(row=4, column=0, sticky="e", padx=4, pady=4)

        self.nombre_var = tk.StringVar(value="")
        self.ram_var = tk.StringVar(value="128")
        self.cpu_var = tk.StringVar(value="5")
        self.llegada_var = tk.StringVar(value="0")
        self.pquantum_var = tk.StringVar(value="-")

        ctk.CTkEntry(form, textvariable=self.nombre_var, width=160).grid(row=0, column=1, sticky="w")
        ctk.CTkEntry(form, textvariable=self.ram_var, width=80).grid(row=1, column=1, sticky="w")
        ctk.CTkEntry(form, textvariable=self.cpu_var, width=80).grid(row=2, column=1, sticky="w")
        ctk.CTkEntry(form, textvariable=self.llegada_var, width=80).grid(row=3, column=1, sticky="w")
        ctk.CTkEntry(form, textvariable=self.pquantum_var, width=80).grid(row=4, column=1, sticky="w")

        ctk.CTkButton(form, text="Agregar Proceso", command=self._agregar_proceso)\
            .grid(row=5, column=0, columnspan=2, pady=8)

        # ---------- Botones de simulación ----------
        btns = ctk.CTkFrame(self)
        btns.pack(fill="x", padx=10, pady=(6, 6))
        ctk.CTkButton(btns, text="▶ Iniciar", command=self._iniciar).pack(side="left", padx=4)
        ctk.CTkButton(btns, text="⏸ Pausar", command=self._pausar).pack(side="left", padx=4)
        ctk.CTkButton(btns, text="⟳ Reiniciar", command=self._reiniciar).pack(side="left", padx=4)
        ctk.CTkButton(btns, text="🗑 Limpiar", command=self._limpiar).pack(side="left", padx=4)

        # ---------- Tabla de eficiencia ----------
        ctk.CTkButton(self, text="📊 Ver Tabla de Eficiencia", command=self._show_table)\
            .pack(fill="x", padx=10, pady=(2, 8))

        # ---------- Info ----------
        self.label_info = ctk.CTkLabel(self, text="Listo.", wraplength=300, justify="left")
        self.label_info.pack(pady=4, padx=10)

        # Config inicial
        try:
            self.planificador.set_algoritmo(self.alg_var.get())
        except Exception:
            pass

    # ------------------------------------------------------------------
    # HANDLERS
    # ------------------------------------------------------------------
    def _on_alg_change(self, value):
        try:
            self.planificador.set_algoritmo(self.alg_var.get())
            self.label_info.configure(text=f"Algoritmo seleccionado: {self.alg_var.get()}")
        except Exception as e:
            self.label_info.configure(text=f"Error al cambiar algoritmo: {e}")

    def _apply_quantum(self):
        q = _to_int(self.quantum_var.get(), default=2)
        try:
            self.planificador.set_rr_quantum(q)
            self.label_info.configure(text=f"Quantum RR={q} aplicado.")
        except Exception as e:
            self.label_info.configure(text=f"Error al aplicar quantum: {e}")

    def _agregar_proceso(self):
        nombre = (self.nombre_var.get() or "").strip() or None
        try:
            p = Proceso(
                nombre=nombre,
                memoria_requerida=_to_int(self.ram_var.get(), 128),
                duracion=_to_int(self.cpu_var.get(), 1),
                llegada=_to_int(self.llegada_var.get(), 0),
                quantum=(
                    None if (self.pquantum_var.get() or "").strip() in ("", "-", "None")
                    else _to_int(self.pquantum_var.get(), 1)
                ),
            )
        except Exception as e:
            self.label_info.configure(text=f"Datos inválidos: {e}")
            return

        ok = self.planificador.agregar_proceso(p)
        if ok:
            self.label_info.configure(text=f"Proceso agregado: {p.nombre} (PID {p.pid})")
            if self.panel_estado:
                self.panel_estado.refrescar_lista()
        else:
            self.label_info.configure(text="❌ Sin memoria disponible para ese proceso.")

    # ------------------------------------------------------------------
    # BOTONES DE SIMULACIÓN
    # ------------------------------------------------------------------
    def _iniciar(self):
        """
        Inicia la simulación:
        - RR y FCFS: intentan usar el callback visual si está presente.
        - SJF/SRTF (u otros): usan el planificador normal con auto-refresco.
        """
        alg = (self.alg_var.get() or "").upper()

        # Visuales (si hay callback): RR y FCFS
        if alg in ("RR", "FCFS") and self.ejecutar_algoritmo_callback:
            q = _to_int(self.quantum_var.get(), 2)
            if alg == "RR":
                self.label_info.configure(text=f"Iniciando simulación (RR, Q={q})...")
                self.ejecutar_algoritmo_callback(algorithm="RR", quantum=q)
            else:
                self.label_info.configure(text="Iniciando simulación (FCFS visual)...")
                self.ejecutar_algoritmo_callback(algorithm="FCFS", quantum=q)  # quantum se ignora en FCFS
            return

        # No visual (clásico)
        try:
            self.planificador.set_algoritmo(alg)
            self.planificador.iniciar()
            if self.panel_estado:
                self.panel_estado.programar_refrescos()
            self.label_info.configure(text=f"Iniciando simulación ({alg})...")
        except Exception as e:
            self.label_info.configure(text=f"Error al iniciar: {e}")

    def _pausar(self):
        self.planificador.detener()
        if self.panel_estado:
            self.panel_estado.refrescar_lista()
        self.label_info.configure(text="⏸ Simulación pausada.")

    def _reiniciar(self):
        self.planificador.reiniciar()
        if self.panel_estado:
            self.panel_estado.refrescar_lista()
        self.label_info.configure(text="🔁 Simulación reiniciada.")

    def _limpiar(self):
        self.planificador.limpiar()
        if self.panel_estado:
            self.panel_estado.refrescar_lista()
        self.label_info.configure(text="🗑 Todo limpio.")

    # ------------------------------------------------------------------
    # TABLA DE EFICIENCIA
    # ------------------------------------------------------------------
    def _show_table(self):
        if self.mostrar_tabla_callback:
            self.mostrar_tabla_callback()
        else:
            self.label_info.configure(text="No hay resultados para mostrar.")
