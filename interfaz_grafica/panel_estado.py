# interfaz_grafica/panel_estado.py

import customtkinter as ctk
from tkinter import StringVar, END

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque
import time

class PanelEstado(ctk.CTkFrame):
    def __init__(self, master, gestor_memoria, planificador):
        super().__init__(master)
        self.gestor_memoria = gestor_memoria
        self.planificador = planificador

        self.label_titulo = ctk.CTkLabel(self, text="Estado de Memoria", font=("Arial", 20))
        self.label_titulo.pack(pady=10)

        # Barra de memoria
        self.barra_memoria = ctk.CTkProgressBar(self, width=400)
        self.barra_memoria.pack(pady=10)
        self.barra_memoria.set(0)

        # Texto debajo de la barra
        self.texto_memoria = StringVar()
        self.label_memoria = ctk.CTkLabel(self, textvariable=self.texto_memoria, font=("Arial", 14))
        self.label_memoria.pack()

        # Lista de procesos activos y en espera
        self.lista_procesos = ctk.CTkTextbox(self, width=400, height=300, font=("Consolas", 12))
        self.lista_procesos.pack(pady=10)

        # Inicializar datos para gráfica
        self.historial_uso = deque(maxlen=30)
        self.tiempos = deque(maxlen=30)
        self.inicio = time.time()

        # Crear figura de matplotlib con estilo
        self.figura, self.ax = plt.subplots(figsize=(5, 2.2), dpi=100)
        self.figura.patch.set_facecolor('#212121')  # Fondo figura
        self.ax.set_facecolor('#2c2c2c')            # Fondo gráfico
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
        """Actualiza barra, texto, lista y gráfica"""
        porcentaje = self.gestor_memoria.obtener_porcentaje_uso()
        memoria_usada = self.gestor_memoria.obtener_memoria_usada()
        memoria_total = self.gestor_memoria.capacidad_total

        # Actualizar barra y texto
        self.barra_memoria.set(porcentaje / 100)
        self.texto_memoria.set(f"Memoria usada: {memoria_usada} MB / {memoria_total} MB ({porcentaje}%)")

        # Mostrar lista de procesos
        self.lista_procesos.delete("1.0", END)

        # Procesos en ejecución
        procesos_activos = self.planificador.obtener_procesos_activos()
        self.lista_procesos.insert(END, "Procesos en ejecución:\n")
        if procesos_activos:
            for p in procesos_activos:
                self.lista_procesos.insert(END, f"{str(p)}\n")
        else:
            self.lista_procesos.insert(END, "  (ninguno)\n")

        # Procesos en espera
        procesos_espera = self.planificador.obtener_procesos()
        self.lista_procesos.insert(END, "\nCola de espera:\n")
        if procesos_espera:
            for p in procesos_espera:
                self.lista_procesos.insert(END, f"{str(p)}\n")
        else:
            self.lista_procesos.insert(END, "  (vacía)\n")

        # Actualizar gráfica
        uso_actual = self.gestor_memoria.obtener_porcentaje_uso()
        self.historial_uso.append(uso_actual)
        self.tiempos.append(round(time.time() - self.inicio))

        # Colores dinámicos
        if uso_actual < 60:
            color = "limegreen"
        elif uso_actual < 80:
            color = "orange"
        else:
            color = "red"

        self.linea.set_data(self.tiempos, self.historial_uso)
        self.linea.set_color(color)
        self.ax.set_xlim(max(0, self.tiempos[0]), self.tiempos[-1] + 1)
        self.canvas.draw()
