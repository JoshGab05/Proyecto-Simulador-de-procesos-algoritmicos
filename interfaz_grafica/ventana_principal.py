# interfaz_grafica/ventana_principal.py
from __future__ import annotations
import customtkinter as ctk

from interfaz_grafica.panel_control import PanelControl
from interfaz_grafica.panel_estado import PanelEstado
from interfaz_grafica.panel_ejecucion import PanelEjecucion


class VentanaPrincipal(ctk.CTk):
    """
    Ventana principal estable (versión que ya tenías funcionando).
    - Construye PanelControl, PanelEstado y PanelEjecucion
      con la firma clásica: (master, planificador)
    - Bucle de ticks sencillo que invoca planificador.tick()
      y pinta 1 marca por tick en el Gantt.
    """
    TICK_MS = 300  # milisegundos por tick (ajústalo si quieres más/menos rápido)

    def __init__(self, gestor_memoria, planificador):
        super().__init__()
        self.title("Simulador de Gestión de Procesos Algorítmicos")
        self.geometry("1280x760")

        # Guardamos referencias
        self.gestor = gestor_memoria
        self.planificador = planificador

        # Estado de ejecución
        self._running = False
        self._after_job = None
        self._t = 0
        self._algoritmo_actual = "FCFS"

        # Layout de 3 columnas
        self.grid_columnconfigure(0, minsize=380)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Paneles ---
        # 1) Control (pasa callbacks directos)
        self.panel_control = PanelControl(
            self,
            self.gestor,
            self.planificador,
            panel_estado=None,  # se establece después
            ejecutar_algoritmo_callback=self.iniciar_simulacion,
            mostrar_tabla_callback=self.mostrar_tabla_eficiencia
        )
        self.panel_control.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        # 2) Estado (FIRMA CLÁSICA Y ESTABLE: (master, planificador))
        #    Si tu PanelEstado admite gestor, cámbialo por: PanelEstado(self, self.gestor, self.planificador)
        self.panel_estado = PanelEstado(self, self.planificador)
        self.panel_estado.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)

        # Damos referencia al control para que refresque tabla cuando agregas procesos
        self.panel_control.panel_estado = self.panel_estado

        # 3) Ejecución (FIRMA CLÁSICA Y ESTABLE: (master, planificador))
        #    Si tu PanelEjecucion admite gestor, cámbialo por: PanelEjecucion(self, self.gestor, self.planificador)
        self.panel_ejecucion = PanelEjecucion(self, self.planificador)
        self.panel_ejecucion.grid(row=0, column=2, sticky="nsew", padx=8, pady=8)

        if hasattr(self.panel_ejecucion, "set_titulo"):
            self.panel_ejecucion.set_titulo("FCFS")

    # ---------------------------------------------------------------------
    # API invocada por el Panel de Control
    # ---------------------------------------------------------------------

    def iniciar_simulacion(self, algorithm: str | None = None, quantum: int | None = None):
        """Arranca el bucle de ticks y fija algoritmo/quantum en el planificador."""
        # Lee algoritmo/quantum si no vienen
        if algorithm is None and hasattr(self.panel_control, "cbo_alg"):
            algorithm = (self.panel_control.cbo_alg.get() or "FCFS").strip()
        if quantum is None and hasattr(self.panel_control, "entry_quantum"):
            try:
                quantum = int(self.panel_control.entry_quantum.get())
            except Exception:
                quantum = None

        self._algoritmo_actual = algorithm or "FCFS"

        # Fijar algoritmo y quantum en el planificador (nombres de métodos estándar)
        if hasattr(self.planificador, "seleccionar_algoritmo"):
            self.planificador.seleccionar_algoritmo(self._algoritmo_actual)
        if quantum is not None and hasattr(self.planificador, "set_quantum"):
            self.planificador.set_quantum(int(quantum))

        # Título del Gantt
        if hasattr(self.panel_ejecucion, "set_titulo"):
            self.panel_ejecucion.set_titulo(self._algoritmo_actual)

        # Pasar base de procesos al Gantt (para dibujar filas)
        if hasattr(self.panel_ejecucion, "set_procesos_base"):
            self.panel_ejecucion.set_procesos_base(list(self.planificador.obtener_procesos()))

        # Lanzar el loop
        self._running = True
        if self._after_job is None:
            self._loop_tick()

    def detener_simulacion(self):
        self._running = False
        if self._after_job is not None:
            try:
                self.after_cancel(self._after_job)
            except Exception:
                pass
        self._after_job = None

    def reiniciar_simulacion(self):
        self.detener_simulacion()
        self._t = 0

        # Limpia planificador y gantt
        if hasattr(self.planificador, "reiniciar"):
            self.planificador.reiniciar()
        if hasattr(self.panel_ejecucion, "limpiar"):
            self.panel_ejecucion.limpiar()

        # Refresca tabla de estado
        if hasattr(self.panel_estado, "refrescar_tabla"):
            self.panel_estado.refrescar_tabla()

        # Limpiar “Orden de Finalización de Procesos”
        if hasattr(self.panel_estado, "mostrar_orden_finalizacion"):
            self.panel_estado.mostrar_orden_finalizacion([])

    def mostrar_tabla_eficiencia(self):
        # Llama al que la implemente (Estado o Ejecución)
        if hasattr(self.panel_estado, "mostrar_tabla_eficiencia"):
            self.panel_estado.mostrar_tabla_eficiencia()
        elif hasattr(self.panel_ejecucion, "mostrar_tabla_eficiencia"):
            self.panel_ejecucion.mostrar_tabla_eficiencia()

    # ---------------------------------------------------------------------
    # Bucle de ticks (estable)
    # ---------------------------------------------------------------------

    def _loop_tick(self):
        if not self._running:
            self._after_job = None
            return

        resumen = None
        try:
            resumen = self.planificador.tick()
        except Exception:
            resumen = None

        # Defaults
        t_actual = None
        pid_en_cpu = None
        llegadas = []

        if isinstance(resumen, dict):
            t_actual   = resumen.get("t")
            pid_en_cpu = resumen.get("pid")
            llegadas   = resumen.get("llegadas", [])
            self._algoritmo_actual = resumen.get("alg", self._algoritmo_actual)

        if t_actual is None:
            self._t += 1
            t_actual = self._t
        else:
            self._t = t_actual

        # 1) Pintar 'o' en llegadas de este tick
        try:
            if llegadas and hasattr(self.panel_ejecucion, "pintar_tick"):
                for pid in llegadas:
                    nombre = None
                    for p in self.planificador.obtener_procesos():
                        if getattr(p, "pid", None) == pid:
                            nombre = getattr(p, "nombre", str(pid))
                            break
                    self.panel_ejecucion.pintar_tick(nombre or str(pid), t_actual, simbolo="o")
        except Exception:
            pass

        # 2) Pintar 'X' al que ejecutó en este tick
        try:
            if pid_en_cpu is not None and hasattr(self.panel_ejecucion, "pintar_tick"):
                nombre = None
                for p in self.planificador.obtener_procesos():
                    if getattr(p, "pid", None) == pid_en_cpu:
                        nombre = getattr(p, "nombre", str(pid_en_cpu))
                        break
                self.panel_ejecucion.pintar_tick(nombre or str(pid_en_cpu), t_actual, simbolo="X")
        except Exception:
            pass

        # Estado pequeño
        try:
            if hasattr(self.panel_estado, "refrescar_estado_pequeno"):
                self.panel_estado.refrescar_estado_pequeno(t_actual, pid_en_cpu, self._algoritmo_actual)
        except Exception:
            pass

        # ¿terminó todo?
        try:
            if hasattr(self.planificador, "esta_terminado") and self.planificador.esta_terminado():
                self.detener_simulacion()
                # NUEVO: refrescar orden final (último tick)
                try:
                    if hasattr(self.panel_estado, "mostrar_orden_finalizacion"):
                        estado_final = self.planificador.estado_cpu()
                        orden_final = estado_final.get("orden_finalizacion", [])
                        self.panel_estado.mostrar_orden_finalizacion(orden_final)
                except Exception:
                    pass
                return
        except Exception:
            pass

        self._after_job = self.after(self.TICK_MS, self._loop_tick)

        # --- NUEVO: obtener estado y pintar “Orden de Finalización de Procesos” ---
        estado = None
        try:
            if hasattr(self.planificador, "estado_cpu"):
                estado = self.planificador.estado_cpu()
        except Exception:
            estado = None

        # Puntos de fin en el Gantt (como ya lo tenías)
        if estado and "finalizados" in estado:
            for fin in estado["finalizados"]:
                nom = fin.get("nombre")
                tfin = fin.get("t_fin")
                if nom is not None and tfin is not None and hasattr(self.panel_ejecucion, "pintar_fin"):
                    try:
                        self.panel_ejecucion.pintar_fin(nom, int(tfin) - 1)
                    except Exception:
                        pass

        # NUEVO: pasar el orden acumulado al panel
        try:
            if estado and hasattr(self.panel_estado, "mostrar_orden_finalizacion"):
                orden = estado.get("orden_finalizacion")
                # fallback por si tu planificador expone método directo
                if not orden and hasattr(self.planificador, "obtener_orden_finalizacion"):
                    orden = self.planificador.obtener_orden_finalizacion()
                self.panel_estado.mostrar_orden_finalizacion(orden or [])
        except Exception:
            pass
