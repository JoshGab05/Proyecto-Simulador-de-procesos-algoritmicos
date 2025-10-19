# interfaz_grafica/panel_control.py
import tkinter as tk
import customtkinter as ctk
import random
from logica.proceso import Proceso

class PanelControl(ctk.CTkScrollableFrame):
    def __init__(self, master, gestor_memoria, planificador, panel_estado):
        super().__init__(master, width=350, height=620)
        self.gestor_memoria = gestor_memoria
        self.planificador = planificador
        self.panel_estado = panel_estado

        # ---------- Título ----------
        ctk.CTkLabel(self, text="Control", font=("Arial", 22)).pack(pady=(8, 6))

        # ---------- Algoritmo ----------
        row = ctk.CTkFrame(self)
        row.pack(fill="x", padx=10, pady=(0, 6))
        ctk.CTkLabel(row, text="Algoritmo:").pack(side="left", padx=(0, 6))
        self.alg_var = ctk.StringVar(value="FCFS")
        ctk.CTkOptionMenu(row, values=["FCFS","SJF","SRTF","RR"], variable=self.alg_var, command=self._on_alg_change).pack(side="left")
        # Quantum RR
        qrow = ctk.CTkFrame(self); qrow.pack(fill="x", padx=10, pady=(0,6))
        ctk.CTkLabel(qrow, text="Quantum (RR):").pack(side="left", padx=(0,6))
        self.quantum_var = tk.IntVar(value=2)
        qentry = ctk.CTkEntry(qrow, width=60, textvariable=self.quantum_var); qentry.pack(side="left")
        ctk.CTkButton(qrow, text="Aplicar", command=self._apply_quantum).pack(side="left", padx=6)

        # ---------- Formulario de Proceso ----------
        form = ctk.CTkFrame(self); form.pack(fill="x", padx=10, pady=(6,6))
        ctk.CTkLabel(form, text="Nombre:").grid(row=0, column=0, sticky="e", padx=4, pady=4)
        ctk.CTkLabel(form, text="RAM (MB):").grid(row=1, column=0, sticky="e", padx=4, pady=4)
        ctk.CTkLabel(form, text="CPU (ticks):").grid(row=2, column=0, sticky="e", padx=4, pady=4)
        ctk.CTkLabel(form, text="Llegada:").grid(row=3, column=0, sticky="e", padx=4, pady=4)
        ctk.CTkLabel(form, text="Quantum:").grid(row=4, column=0, sticky="e", padx=4, pady=4)

        self.nombre_var = tk.StringVar(value="")
        self.ram_var = tk.IntVar(value=128)
        self.cpu_var = tk.IntVar(value=5)
        self.llegada_var = tk.IntVar(value=0)
        self.pquantum_var = tk.StringVar(value="-")

        ctk.CTkEntry(form, textvariable=self.nombre_var, width=160).grid(row=0, column=1, sticky="w")
        ctk.CTkEntry(form, textvariable=self.ram_var, width=80).grid(row=1, column=1, sticky="w")
        ctk.CTkEntry(form, textvariable=self.cpu_var, width=80).grid(row=2, column=1, sticky="w")
        ctk.CTkEntry(form, textvariable=self.llegada_var, width=80).grid(row=3, column=1, sticky="w")
        ctk.CTkEntry(form, textvariable=self.pquantum_var, width=80).grid(row=4, column=1, sticky="w")

        ctk.CTkButton(form, text="Agregar Proceso", command=self._agregar_proceso).grid(row=5, column=0, columnspan=2, pady=8)

        # ---------- Botones de simulación ----------
        btns = ctk.CTkFrame(self); btns.pack(fill="x", padx=10, pady=(6,6))
        ctk.CTkButton(btns, text="Iniciar", command=self._iniciar).pack(side="left", padx=4)
        ctk.CTkButton(btns, text="Tick", command=self._tick).pack(side="left", padx=4)
        ctk.CTkButton(btns, text="Pausar", command=self._pausar).pack(side="left", padx=4)
        ctk.CTkButton(btns, text="Reiniciar", command=self._reiniciar).pack(side="left", padx=4)
        ctk.CTkButton(btns, text="Limpiar", command=self._limpiar).pack(side="left", padx=4)

        # ---------- Info ----------
        self.label_info = ctk.CTkLabel(self, text="Listo.", wraplength=300, justify="left")
        self.label_info.pack(pady=8, padx=10)

        # Set inicial
        try:
            self.planificador.set_algoritmo(self.alg_var.get())
        except Exception:
            pass

    # ---- Handlers ----
    def _on_alg_change(self, value):
        try:
            self.planificador.set_algoritmo(self.alg_var.get())
            self.label_info.configure(text=f"Algoritmo: {self.alg_var.get()}")
        except Exception as e:
            self.label_info.configure(text=f"Error algoritmo: {e}")

    def _apply_quantum(self):
        try:
            self.planificador.set_rr_quantum(int(self.quantum_var.get()))
            self.label_info.configure(text=f"Quantum RR={self.quantum_var.get()} aplicado")
        except Exception as e:
            self.label_info.configure(text=f"Error al aplicar quantum: {e}")

    def _agregar_proceso(self):
        nombre = self.nombre_var.get().strip() or None
        try:
            p = Proceso(
                nombre=nombre,
                memoria_requerida=int(self.ram_var.get()),
                duracion=int(self.cpu_var.get()),
                llegada=int(self.llegada_var.get()),
                quantum=(None if self.pquantum_var.get().strip() in ('', '-', 'None') else int(self.pquantum_var.get()))
            )
        except Exception as e:
            self.label_info.configure(text=f"Datos inválidos: {e}")
            return

        ok = self.planificador.agregar_proceso(p)
        if ok:
            self.label_info.configure(text=f"Proceso agregado: {p.nombre} (PID {p.pid})")
            self.panel_estado.refrescar_lista()
        else:
            self.label_info.configure(text="Sin memoria disponible para ese proceso")

    def _iniciar(self):
        self.planificador.iniciar()
        self.panel_estado.programar_refrescos()

    def _tick(self):
        self.planificador.simular_tick(1)
        self.panel_estado.refrescar_lista()

    def _pausar(self):
        self.planificador.detener()
        self.panel_estado.refrescar_lista()

    def _reiniciar(self):
        self.planificador.reiniciar()
        self.panel_estado.refrescar_lista()

    def _limpiar(self):
        self.planificador.limpiar()
        self.panel_estado.refrescar_lista()