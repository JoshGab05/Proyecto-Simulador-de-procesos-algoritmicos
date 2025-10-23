import customtkinter as ctk
import threading
import time
from interfaz_grafica.panel_estado import PanelEstado
from interfaz_grafica.panel_control import PanelControl
from interfaz_grafica.tabla_eficiencia import TablaEficiencia
from interfaz_grafica.panel_ejecucion import PanelEjecucion


class VentanaPrincipal(ctk.CTk):
    def __init__(self, gestor_memoria, planificador):
        super().__init__()
        self.title("Simulador de Gestión de Procesos Algorítmicos")
        self.geometry("1000x600")
        self.resizable(False, False)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.gestor_memoria = gestor_memoria
        self.planificador = planificador
        self._resultados_rr = None  # usamos este mismo contenedor para RR/FCFS visual

        # ================================
        # DISEÑO PRINCIPAL  (35 / 30 / 35)
        # ================================
        self.grid_columnconfigure(0, weight=35, uniform="column")
        self.grid_columnconfigure(1, weight=30, uniform="column")
        self.grid_columnconfigure(2, weight=35, uniform="column")
        self.grid_rowconfigure(0, weight=1)

        # -------- PANEL CONTROL --------
        self.panel_control = PanelControl(
            self,
            gestor_memoria,
            planificador,
            None,
            ejecutar_algoritmo_callback=self.ejecutar_round_robin,  # maneja RR y FCFS
            mostrar_tabla_callback=self.mostrar_tabla_eficiencia,
        )
        self.panel_control.grid(row=0, column=0, sticky="nswe", padx=(10, 5), pady=10)

        # -------- PANEL ESTADO --------
        self.panel_estado = PanelEstado(self, planificador)
        self.panel_estado.grid(row=0, column=1, sticky="nswe", padx=5, pady=10)

        # -------- PANEL EJECUCIÓN --------
        self.panel_ejecucion = PanelEjecucion(self)
        self.panel_ejecucion.grid(row=0, column=2, sticky="nswe", padx=(5, 10), pady=10)

        # Vincular panel de control con estado
        self.panel_control.panel_estado = self.panel_estado

        # Asegurar que el tamaño se mantenga fijo
        self.update_idletasks()
        self.minsize(self.winfo_width(), self.winfo_height())

        # Al cerrar la ventana
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ===============================================================
    # EJECUCIÓN VISUAL (RR y FCFS)
    # ===============================================================
    def ejecutar_round_robin(self, algorithm="RR", quantum=2):
        """
        Ejecuta la visualización del algoritmo seleccionado:
        - RR: usa planificador.ejecutar_round_robin_visual(quantum, on_tick)
        - FCFS: bucle visual interno (FIFO) sin modificar el planificador.
        """
        alg = (algorithm or "RR").upper()

        # Cancelar refrescos si estaban activos para evitar doble dibujado
        try:
            self.panel_estado.cancelar_refrescos()
        except Exception:
            pass

        # Limpiar interfaz antes de iniciar
        self._resultados_rr = None
        try:
            self.panel_ejecucion.limpiar()
        except Exception as e:
            print(f"[UI] limpiar panel_ejecucion falló: {e}")

        # Inicializar procesos en el panel de ejecución
        try:
            procs_for_ui = self._get_procesos_snapshot()
            self.panel_ejecucion.inicializar_procesos(procs_for_ui)
        except Exception as e:
            print(f"[UI] inicializar_procesos falló: {e}")

        # Mantener tamaño fijo del centro (evita reducción visual)
        self.update_idletasks()
        fixed_width = self.winfo_width()
        fixed_height = self.winfo_height()
        self.minsize(fixed_width, fixed_height)
        self.maxsize(fixed_width, fixed_height)

        # ---------- RR en hilo separado ----------
        def _run_rr():
            try:
                def safe_on_tick(t, proceso_actual, cola_ready):
                    self.after(0, lambda: self.panel_ejecucion.actualizar_tick(t, proceso_actual, cola_ready))
                    self.after(0, lambda: self.panel_estado.actualizar_estado(t, proceso_actual, cola_ready, "RR"))

                res = self.planificador.ejecutar_round_robin_visual(
                    quantum=quantum,
                    on_tick=safe_on_tick
                )
                self._resultados_rr = res
                self.after(0, self.mostrar_tabla_eficiencia)
                self.after(0, lambda: self.panel_estado.mostrar_orden_finalizacion(self._resultados_rr))
            except Exception as e:
                print(f"[RR] Error en ejecución visual: {e}")

        # ---------- FCFS (FIFO) visual en hilo separado ----------
        def _run_fcfs():
            """
            Animación simple FCFS: orden de llegada, no expropiativo.
            No modifica tu planificador; solo lee los procesos para animar.
            """
            try:
                # Snapshot de procesos actuales
                procs = list(self._get_procesos_snapshot())
            except Exception as e:
                print(f"[FCFS] No pude obtener procesos: {e}")
                procs = []

            if not procs:
                print("[FCFS] No hay procesos para animar.")
                self.after(0, lambda: self.panel_estado.actualizar_estado(0, None, [], "FCFS"))
                return

            # Construimos un estado ligero para animar
            items = []
            for p in procs:
                try:
                    restante = getattr(p, "restante", None)
                    dur = getattr(p, "duracion", None)
                    llegada = getattr(p, "llegada", 0)
                    pid = getattr(p, "pid", None)
                    nombre = getattr(p, "nombre", str(pid))
                    if restante is None:
                        restante = int(dur) if dur is not None else 1
                    items.append({
                        "ref": p,
                        "pid": pid if pid is not None else 0,
                        "nombre": nombre,
                        "llegada": int(llegada),
                        "restante": int(restante)
                    })
                except Exception as e:
                    print(f"[FCFS] Proceso inválido ignorado: {e}")

            if not items:
                print("[FCFS] Lista de items vacía tras limpiar datos.")
                self.after(0, lambda: self.panel_estado.actualizar_estado(0, None, [], "FCFS"))
                return

            # Orden por llegada y pid
            items.sort(key=lambda x: (x["llegada"], x["pid"]))

            t = 0
            ready = []
            running = None
            fin_orden = []
            idx = 0  # índice de llegadas (items ordenados)
            finished = 0
            total = len(items)

            # Velocidad de animación (ajústala si quieres más rápido/lento)
            delay_s = 0.12

            def cola_ready_refs():
                return [it["ref"] for it in ready]

            # Bucle principal
            while finished < total:
                # 1) Llegadas en t
                while idx < len(items) and items[idx]["llegada"] == t:
                    ready.append(items[idx])
                    idx += 1

                # 2) Despacho si CPU ociosa
                if running is None and ready:
                    running = ready.pop(0)

                # 3) Dibujar tick
                proceso_actual_ref = running["ref"] if running else None
                try:
                    self.after(0, lambda tt=t, pr=proceso_actual_ref:
                               self.panel_ejecucion.actualizar_tick(tt, pr, cola_ready_refs()))
                    self.after(0, lambda tt=t, pr=proceso_actual_ref:
                               self.panel_estado.actualizar_estado(tt, pr, cola_ready_refs(), "FCFS"))
                except Exception as e:
                    print(f"[FCFS] Error al actualizar UI: {e}")

                # 4) Avance CPU
                if running is not None:
                    running["restante"] -= 1
                    if running["restante"] <= 0:
                        fin_orden.append(running["ref"])
                        running = None
                        finished += 1

                # 5) Espera visual y avanzar tiempo
                time.sleep(delay_s)
                t += 1

            # Resultado para tabla/estado
            self._resultados_rr = {
                "algoritmo": "FCFS",
                "orden_finalizacion": fin_orden,
            }
            self.after(0, self.mostrar_tabla_eficiencia)
            self.after(0, lambda: self.panel_estado.mostrar_orden_finalizacion(self._resultados_rr))

        if alg == "RR":
            threading.Thread(target=_run_rr, daemon=True).start()
        elif alg == "FCFS":
            threading.Thread(target=_run_fcfs, daemon=True).start()
        else:
            # Para SJF/SRTF u otros: modo clásico (no visual)
            try:
                self.planificador.set_algoritmo(alg)
                self.planificador.iniciar()
                self.panel_estado.programar_refrescos()
            except Exception as e:
                print(f"[{alg}] Error iniciando modo clásico: {e}")

    # ---------------------------------------------------------------
    # Utilidad: snapshot de procesos, tolerante a distintas APIs
    # ---------------------------------------------------------------
    def _get_procesos_snapshot(self):
        """
        Intenta obtener la lista de procesos desde el planificador, probando:
        - planificador.obtener_procesos()
        - planificador.procesos
        - planificador._procesos
        Retorna siempre una lista (posiblemente vacía).
        """
        # 1) Método explícito
        try:
            if hasattr(self.planificador, "obtener_procesos"):
                procs = self.planificador.obtener_procesos()
                return list(procs) if procs is not None else []
        except Exception as e:
            print(f"[SNAP] Error en obtener_procesos(): {e}")

        # 2) Atributos comunes
        for attr in ("procesos", "_procesos"):
            try:
                if hasattr(self.planificador, attr):
                    procs = getattr(self.planificador, attr)
                    return list(procs) if procs is not None else []
            except Exception as e:
                print(f"[SNAP] Error leyendo {attr}: {e}")

        return []

    # ===============================================================
    # MOSTRAR TABLA DE EFICIENCIA
    # ===============================================================
    def mostrar_tabla_eficiencia(self):
        """Abre la ventana con la tabla de eficiencia al terminar la simulación."""
        if not self._resultados_rr:
            print("⚠️ No hay resultados disponibles para la tabla.")
            return
        try:
            TablaEficiencia(self, self._resultados_rr)
        except Exception as e:
            print(f"[UI] No pude mostrar la tabla de eficiencia: {e}")

    # ===============================================================
    # CIERRE LIMPIO DE LA APLICACIÓN
    # ===============================================================
    def _on_close(self):
        try:
            self.panel_estado.cancelar_refrescos()
        except Exception:
            pass
        try:
            self.quit()
            self.destroy()
        except Exception:
            pass
