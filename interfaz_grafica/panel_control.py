# interfaz_grafica/panel_control.py

import tkinter as tk
import customtkinter as ctk
import random
from logica.proceso import Proceso

class PanelControl(ctk.CTkScrollableFrame):  # <— scrollable
    def __init__(self, master, gestor_memoria, planificador, panel_estado):
        # Puedes ajustar width/height si quieres más alto/ancho
        super().__init__(master, width=320, height=560)

        self.gestor_memoria = gestor_memoria
        self.planificador = planificador
        self.panel_estado = panel_estado
        self._after_id=None
        self._sim_running=False

        # ---------- Título ----------
        self.label_titulo = ctk.CTkLabel(self, text="Controles", font=("Arial", 20))
        self.label_titulo.pack(pady=10)

        # ---------- Selector de algoritmo ----------
        self.label_alg = ctk.CTkLabel(self, text="Algoritmo base", font=("Arial", 14))
        self.label_alg.pack(pady=(5, 0))

        opciones = ["FCFS", "SJF", "SRTF", "Round Robin"]
        self.alg_var = ctk.StringVar(value=opciones[0])
        self.menu_alg = ctk.CTkOptionMenu(self, values=opciones, variable=self.alg_var, command=self._on_alg_change)
        self.menu_alg.pack(pady=(0, 10), fill="x", padx=10)

        # ---------- Sección: Nuevo proceso ----------
        cont_proc = ctk.CTkFrame(self)
        cont_proc.pack(fill="x", padx=10, pady=(0, 10))

        lbl_np = ctk.CTkLabel(cont_proc, text="Nuevo proceso", font=("Arial", 16))
        lbl_np.pack(pady=(8, 6))

        # Nombre
        self.label_nombre = ctk.CTkLabel(cont_proc, text="Nombre del proceso")
        self.label_nombre.pack()
        self.entry_nombre = ctk.CTkEntry(cont_proc, placeholder_text="Ej: Proceso 1")
        self.entry_nombre.pack(pady=(0, 6), fill="x", padx=8)

        # Tiempo en CPU (duración total)
        self.label_cpu = ctk.CTkLabel(cont_proc, text="Tiempo en CPU (s)")
        self.label_cpu.pack()
        self.entry_cpu = ctk.CTkEntry(cont_proc, placeholder_text="Ej: 8")
        self.entry_cpu.pack(pady=(0, 6), fill="x", padx=8)

        # Instante de llegada
        self.label_llegada = ctk.CTkLabel(cont_proc, text="Instante de llegada")
        self.label_llegada.pack()
        self.entry_llegada = ctk.CTkEntry(cont_proc, placeholder_text="Ej: 0")
        self.entry_llegada.pack(pady=(0, 6), fill="x", padx=8)

        # Quantum (opcional, usado por RR)
        self.label_quantum = ctk.CTkLabel(cont_proc, text="Quantum (opcional)")
        self.label_quantum.pack()
        self.entry_quantum = ctk.CTkEntry(cont_proc, placeholder_text="Ej: 2")
        self.entry_quantum.pack(pady=(0, 6), fill="x", padx=8)

        # RAM (opcional)
        self.label_ram = ctk.CTkLabel(cont_proc, text="RAM requerida (MB, opcional)")
        self.label_ram.pack()
        self.entry_ram = ctk.CTkEntry(cont_proc, placeholder_text="Ej: 64")
        self.entry_ram.pack(pady=(0, 10), fill="x", padx=8)

        # Botón Agregar proceso
        self.btn_crear = ctk.CTkButton(cont_proc, text="Agregar proceso", command=self.crear_proceso)
        self.btn_crear.pack(pady=(0, 8), fill="x", padx=8)

        # ---------- Sección: Aleatorios ----------
        cont_rand = ctk.CTkFrame(self)
        cont_rand.pack(fill="x", padx=10, pady=(0, 10))

        lbl_rand = ctk.CTkLabel(cont_rand, text="Procesos aleatorios", font=("Arial", 16))
        lbl_rand.pack(pady=(8, 6))

        fila = ctk.CTkFrame(cont_rand)
        fila.pack(fill="x", padx=8, pady=(0, 6))

        ctk.CTkLabel(fila, text="Cantidad").grid(row=0, column=0, padx=4, pady=2, sticky="w")
        self.entry_rand_n = ctk.CTkEntry(fila, width=60)
        self.entry_rand_n.insert(0, "5")
        self.entry_rand_n.grid(row=0, column=1, padx=4, pady=2)

        ctk.CTkLabel(fila, text="CPU máx").grid(row=0, column=2, padx=4, pady=2, sticky="w")
        self.entry_rand_cpu = ctk.CTkEntry(fila, width=60)
        self.entry_rand_cpu.insert(0, "10")
        self.entry_rand_cpu.grid(row=0, column=3, padx=4, pady=2)

        ctk.CTkLabel(fila, text="Llegada máx").grid(row=1, column=0, padx=4, pady=2, sticky="w")
        self.entry_rand_lleg = ctk.CTkEntry(fila, width=60)
        self.entry_rand_lleg.insert(0, "10")
        self.entry_rand_lleg.grid(row=1, column=1, padx=4, pady=2)

        ctk.CTkLabel(fila, text="Quantum máx").grid(row=1, column=2, padx=4, pady=2, sticky="w")
        self.entry_rand_qmax = ctk.CTkEntry(fila, width=60)
        self.entry_rand_qmax.insert(0, "3")
        self.entry_rand_qmax.grid(row=1, column=3, padx=4, pady=2)

        self.btn_rand = ctk.CTkButton(cont_rand, text="Agregar aleatorios", command=self.crear_procesos_aleatorios)
        self.btn_rand.pack(pady=(4, 8), fill="x", padx=8)

        # ---------- Botones de algoritmo/simulación ----------
        cont_bot = ctk.CTkFrame(self)
        cont_bot.pack(fill="x", padx=10, pady=10)

        # No reordena la lista visual; solo prepara el algoritmo
        self.btn_aplicar_alg = ctk.CTkButton(cont_bot, text="Preparar algoritmo", command=self._aplicar_algoritmo)
        self.btn_aplicar_alg.pack(fill="x", pady=(0, 6), padx=8)

        self.btn_iniciar = ctk.CTkButton(cont_bot, text="Iniciar simulación", command=self.iniciar_planificador)
        self.btn_iniciar.pack(fill="x", pady=(0, 6), padx=8)

        self.btn_detener = ctk.CTkButton(cont_bot, text="Detener simulación", fg_color="#a33", hover_color="#922",
                                         command=self.detener_planificador)
        self.btn_detener.pack(fill="x", padx=8)

        # ---------- Info ----------
        self.label_info = ctk.CTkLabel(self, text="Listo.", wraplength=260, justify="left")
        self.label_info.pack(pady=8, padx=10)

        # Algoritmo inicial
        try:
            self.planificador.set_algoritmo(self.alg_var.get())
        except Exception:
            pass

    # ======================= LÓGICA =======================

    def _on_alg_change(self, value):
        try:
            self.planificador.set_algoritmo(value)
            self.label_info.configure(text=f"Algoritmo base: {value}")
        except Exception:
            self.label_info.configure(text=f"Error al establecer algoritmo: {value}")

    def _aplicar_algoritmo(self):
        try:
            self.detener_planificador()  # evita afters colgando
            self.planificador.aplicar_algoritmo()
            self.panel_estado.actualizar_estado()
            self.label_info.configure(text=f"Algoritmo preparado: {self.alg_var.get()}")
        except Exception:
            self.label_info.configure(text="No se pudo preparar el algoritmo (¿módulo vacío?).")



    def crear_proceso(self):
        nombre = (self.entry_nombre.get() or "").strip()
        if not nombre:
            nombre = f"Proceso {len(self.planificador.obtener_procesos()) + 1}"

        def _to_int_or(val, default=0):
            try:
                return int(val)
            except Exception:
                return default

        cpu = _to_int_or(self.entry_cpu.get(), 1)
        llegada = _to_int_or(self.entry_llegada.get(), 0)
        ram_req = _to_int_or(self.entry_ram.get(), 0)

        qtxt = (self.entry_quantum.get() or "").strip()
        quantum = int(qtxt) if qtxt.isdigit() else None

        p = Proceso(
            nombre=nombre,
            memoria_requerida=ram_req,
            duracion=cpu,
            llegada=llegada,
            quantum=quantum
        )
        try:
            self.planificador.agregar_proceso(p)
            self.label_info.configure(
                text=f"➕ Proceso agregado: {p.nombre} | CPU:{cpu}s | Llegada:{llegada} | Q:{quantum if quantum is not None else '-'} | RAM:{ram_req}MB"
            )
            self.panel_estado.actualizar_estado()
        except Exception as e:
            self.label_info.configure(text=f"No se pudo agregar el proceso: {e}")

    def crear_procesos_aleatorios(self):
        def _to_int_or(val, default=1):
            try:
                return int(val)
            except Exception:
                return default

        n = _to_int_or(self.entry_rand_n.get(), 5)
        cpu_max = max(1, _to_int_or(self.entry_rand_cpu.get(), 10))
        lleg_max = max(0, _to_int_or(self.entry_rand_lleg.get(), 10))
        qmax = max(1, _to_int_or(self.entry_rand_qmax.get(), 3))

        actual_alg = self.alg_var.get()

        for _ in range(n):
            nombre = f"Auto {len(self.planificador.obtener_procesos()) + 1}"
            cpu = random.randint(1, cpu_max)
            llegada = random.randint(0, lleg_max)
            quantum = random.randint(1, qmax) if actual_alg == "Round Robin" else None

            p = Proceso(nombre=nombre, memoria_requerida=0, duracion=cpu, llegada=llegada, quantum=quantum)
            self.planificador.agregar_proceso(p)

        self.panel_estado.actualizar_estado()
        self.label_info.configure(text=f"➕ Se agregaron {n} procesos aleatorios (algoritmo: {actual_alg}).")

    # ---------- Simulación ----------
    
    def _tick_sim(self):
        # si ya no estamos corriendo o el widget fue destruido, salir
        if not self._sim_running or not self.winfo_exists():
            return
        try:
            self.planificador.simular_tick(delta=1)
            if self.panel_estado.winfo_exists():
                self.panel_estado.actualizar_estado()
        except Exception as e:  # <- captura TODO para no “matar” el loop
            self._sim_running = False
            self._cancel_after()
        # opcional: ver error en la UI
            try:
                self.label_info.configure(text=f"Error en tick: {e}")
            except Exception:
                pass
            return
    # reprograma el próximo tick
        self._after_id = self.after(1000, self._tick_sim)  # cambia a 5000 si 1 unidad = 5 s

    def iniciar_planificador(self):
        self._cancel_after()
        try:
            self.planificador.iniciar()
            self._sim_running = True
            self.label_info.configure(text="▶️ Simulación iniciada.")
        # lanza el primer tick “ya” para que se vea vivo
            self._after_id = self.after(1, self._tick_sim)
        except Exception:
            self._sim_running = False
            self.label_info.configure(text="No se pudo iniciar la simulación.")

    def detener_planificador(self):
        self._sim_running = False
        self._cancel_after()
        try:
            self.planificador.detener()
            self.label_info.configure(text="⛔ Simulación detenida.")
            self.panel_estado.actualizar_estado()
        except Exception:
            self.label_info.configure(text="No se pudo detener la simulación.")

    def _cancel_after(self):
        if getattr(self, "_after_id", None) is not None:
            try:
                self.after_cancel(self._after_id)
            except Exception:
                pass
        self._after_id = None

    
    