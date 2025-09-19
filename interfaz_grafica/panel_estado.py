# interfaz_grafica/panel_estado.py

import customtkinter as ctk
from tkinter import StringVar, END
import tkinter as tk
import time

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque

class PanelEstado(ctk.CTkFrame):
    def __init__(self, master, gestor_memoria, planificador):
        super().__init__(master)  # <-- SIEMPRE primero

        self.gestor_memoria = gestor_memoria
        self.planificador = planificador

        # Título
        self.label_titulo = ctk.CTkLabel(self, text="Estado de Memoria", font=("Arial", 20))
        self.label_titulo.pack(pady=10)

        # Latido para ver el tick avanzar
        self.lbl_tick = ctk.CTkLabel(self, text="t=0", font=("Arial", 12))
        self.lbl_tick.pack(pady=(0, 4))

        # Barra de memoria
        self.barra_memoria = ctk.CTkProgressBar(self, width=400)
        self.barra_memoria.pack(pady=10)
        self.barra_memoria.set(0)

        # Texto debajo de la barra
        self.texto_memoria = StringVar()
        self.label_memoria = ctk.CTkLabel(self, textvariable=self.texto_memoria, font=("Arial", 14))
        self.label_memoria.pack()

        # Lista de procesos
        self.lista_procesos = ctk.CTkTextbox(self, width=400, height=300, font=("Consolas", 12))
        self.lista_procesos.pack(pady=10)

        # Datos para gráfica
        self.historial_uso = deque(maxlen=30)
        self.tiempos = deque(maxlen=30)
        self.inicio = time.time()

        # Figura matplotlib
        self.figura, self.ax = plt.subplots(figsize=(5, 2.2), dpi=100)
        self.figura.patch.set_facecolor('#212121')
        self.ax.set_facecolor('#2c2c2c')
        self.ax.tick_params(colors='white')
        for spine in self.ax.spines.values():
            spine.set_color('gray')

        self.linea, = self.ax.plot([], [], linewidth=2)
        self.ax.set_ylim(0, 100)
        self.ax.set_xlim(0, 30)
        self.ax.set_title("Uso de memoria (%)", color="white", fontsize=12)
        self.ax.set_xlabel("Tiempo (s)", color="white")
        self.ax.set_ylabel("% RAM", color="white")

        # Integrar matplotlib en tkinter
        self.canvas = FigureCanvasTkAgg(self.figura, master=self)
        self.canvas.get_tk_widget().pack(pady=10)

        self.actualizar_estado()

    def actualizar_estado(self):
        if not self.winfo_exists():
            return

        # Tick en pantalla
        try:
            self.lbl_tick.configure(text=f"t={getattr(self.planificador, 'tiempo_actual', 0)}")
        except Exception:
            pass

        # ---- Lecturas del gestor ----
        try:
            porcentaje = self.gestor_memoria.obtener_porcentaje_uso()
            memoria_usada = self.gestor_memoria.obtener_memoria_usada()
            memoria_total = self.gestor_memoria.capacidad_total
        except Exception:
            porcentaje = 0
            memoria_usada = 0
            memoria_total = 0

        # ---- Barra y texto ----
        try:
            if self.barra_memoria.winfo_exists() and getattr(self.barra_memoria, "_canvas", None):
                self.barra_memoria.set(porcentaje / 100.0)
            self.texto_memoria.set(f"Memoria usada: {memoria_usada} MB / {memoria_total} MB ({porcentaje}%)")
        except tk.TclError:
            pass

        # ---- Lista de procesos ----
        try:
            if self.lista_procesos.winfo_exists():
                self.lista_procesos.delete("1.0", END)

                self.lista_procesos.insert(END, "Procesos en ejecución:\n")
                p_actual = self.planificador.proceso_actual   # propiedad, sin ()
                if p_actual:
                    self.lista_procesos.insert(END, f"{p_actual}\n")
                else:
                    self.lista_procesos.insert(END, "  (ninguno)\n")

                # <== ESTO iba mal indentado en tu versión
                self.lista_procesos.insert(END, "\nCola de espera:\n")
                for p in self.planificador.obtener_procesos():
                    self.lista_procesos.insert(END, f"{p}\n")
        except tk.TclError:
            pass

        # ---- Gráfica ----
        try:
            # Temporal: usa procesos pendientes para ver la gráfica moverse
            pendientes = sum(1 for p in self.planificador.obtener_procesos() if not p.esta_terminado())
            uso_actual = min(100, pendientes * 10)  # p.ej., 10% por proceso

            self.historial_uso.append(uso_actual)
            self.tiempos.append(round(time.time() - self.inicio))

            color = "limegreen" if uso_actual < 60 else ("orange" if uso_actual < 80 else "red")
            if len(self.tiempos) >= 2:
                self.linea.set_data(self.tiempos, self.historial_uso)
                self.linea.set_color(color)
                self.ax.set_xlim(max(0, self.tiempos[0]), self.tiempos[-1] + 1)
                if self.canvas.get_tk_widget().winfo_exists():
                    self.canvas.draw()
        except tk.TclError:
            pass

    def cancelar_refrescos(self):
        # Gancho por si en el futuro usas after() en este panel
        pass

        