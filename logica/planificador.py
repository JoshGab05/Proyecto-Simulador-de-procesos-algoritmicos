from typing import List, Optional, Any

class Planificador:
    def __init__(self, gestor_memoria):
        self.gestor_memoria = gestor_memoria

        # Lista estable para la UI (no reordenar)
        self._procesos: List[Any] = []

        # Simulación
        self.ejecutando: bool = False
        self.tiempo_actual: int = 0
        self.historial: List[Any] = []
        self.pid_en_ejecucion: Optional[int] = None
        self.historial_ticks: list[str] = []

        # Algoritmo
        self.algoritmo_seleccionado: Optional[str] = None
        self._alg_inst = None

    @property
    def pid_en_cpu(self) -> Optional[int]:
        """Alias para UI."""
        return self.pid_en_ejecucion

    # ---------------- Configuración ----------------
    def set_algoritmo(self, nombre: str):
        """Selecciona el algoritmo: FCFS, SJF, SRTF o Round Robin."""
        self.algoritmo_seleccionado = nombre
        self._alg_inst = None  # forzar recarga al aplicar

    def _ensure_alg_instance(self):
        """Carga (una vez) el módulo del algoritmo y devuelve la instancia."""
        if self._alg_inst is not None:
            return self._alg_inst
        if not self.algoritmo_seleccionado:
            return None

        # NOTA: SRTF apunta al módulo real del archivo .py
        mapping = {
            'FCFS': ('algoritmos.fcfs', 'AlgoritmoFIFO'),
            'SJF': ('algoritmos.sjf', 'AlgoritmoSJF'),
            'SRTF': ('algoritmos.srtf.AlgoritmoSRTF', 'AlgoritmoSRTF'),
            'Round Robin': ('algoritmos.round_robin', 'AlgoritmoRoundRobin'),
        }
        if self.algoritmo_seleccionado not in mapping:
            return None

        mod_name, class_name = mapping[self.algoritmo_seleccionado]
        try:
            mod = __import__(mod_name, fromlist=[class_name])
            AlgClass = getattr(mod, class_name, None)
            if AlgClass is None:
                return None
            self._alg_inst = AlgClass()
            return self._alg_inst
        except Exception:
            return None

    # ---------------- Gestión de procesos ----------------
    def agregar_proceso(self, proceso):
        self._procesos.append(proceso)

    def eliminar_proceso(self, pid):
        for p in self._procesos:
            if getattr(p, 'pid', None) == pid:
                # liberar memoria si estaba asignada
                if getattr(p, "_mem_asignada", False):
                    try:
                        self.gestor_memoria.liberar(p.pid)
                    except Exception:
                        pass
                    p._mem_asignada = False

                p.forzar_finalizacion()
                if p not in self.historial:
                    self.historial.append(p)
                break

    # ---------------- Ciclo de simulación ----------------
    def iniciar(self):
        self.ejecutando = True

    def detener(self):
        self.ejecutando = False
        if self.pid_en_ejecucion is not None:
            proc = self._by_pid(self.pid_en_ejecucion)
            if proc and not proc.esta_terminado():
                proc.estado = 'En espera'
        self.pid_en_ejecucion = None

    def aplicar_algoritmo(self):
        """Prepara el algoritmo (no reordena la lista visual)."""
        alg = self._ensure_alg_instance()
        if alg is None:
            return
        copia = list(self._procesos)
        if hasattr(alg, 'setup'):
            try:
                alg.setup(copia, planificador=self)
            except Exception:
                pass
        elif hasattr(alg, 'planificar'):
            try:
                alg.planificar(copia, planificador=self)
            except Exception:
                pass

    def simular_tick(self, delta: int = 1):
        """
        Avanza EXACTAMENTE 1 unidad de CPU del proceso elegido y
        luego incrementa el reloj. Sin reordenar la lista visual.
        """
        if not self.ejecutando:
            return

        # Elegibles que ya llegaron en el tiempo actual
        candidatos = [p for p in self._procesos
                      if (getattr(p, 'instante_llegada', 0) <= self.tiempo_actual) and not p.esta_terminado()]

        if not candidatos:
            self._clear_running()
            self.historial_ticks.append(f"[t={self.tiempo_actual}] (idle)")
            self.tiempo_actual += 1
            return

        # Preguntar al algoritmo
        elegido = None
        alg = self._ensure_alg_instance()
        if alg and hasattr(alg, 'seleccionar'):
            try:
                elegido = alg.seleccionar(list(candidatos), planificador=self)
            except Exception:
                elegido = None

        # Normalizar a Proceso
        if elegido is not None and hasattr(elegido, 'pid'):
            proc_elegido = elegido
        else:
            proc_elegido = self._by_pid(elegido) if elegido is not None else candidatos[0]
        if proc_elegido is None:
            proc_elegido = candidatos[0]

        # Marcar y (si aplica) reservar memoria
        self._marcar_en_ejecucion(proc_elegido)

        # Ejecutar 1 unidad de CPU
        proc_elegido.avanzar(delta=1)

        # Si terminó, a historial y liberar memoria
        if proc_elegido.esta_terminado():
            # liberar memoria si estaba asignada
            if getattr(proc_elegido, "_mem_asignada", False):
                try:
                    self.gestor_memoria.liberar(proc_elegido.pid)
                except Exception:
                    pass
                proc_elegido._mem_asignada = False

            if proc_elegido not in self.historial:
                self.historial.append(proc_elegido)
            self.pid_en_ejecucion = None

        # Log y reloj
        pidtxt = getattr(proc_elegido, 'pid', '?')
        self.historial_ticks.append(f"[t={self.tiempo_actual}] PID {pidtxt}")
        self.tiempo_actual += 1

    # ---------------- Utilidades para UI ----------------
    def obtener_procesos(self):
        return list(self._procesos)

    def obtener_procesos_activos(self):
        if self.pid_en_ejecucion is None:
            return []
        p = self._by_pid(self.pid_en_ejecucion)
        return [p] if p else []

    @property
    def proceso_actual(self):
        if self.pid_en_ejecucion is None:
            return None
        return self._by_pid(self.pid_en_ejecucion)

    def mover_a_historial(self, proceso):
        if proceso not in self.historial:
            self.historial.append(proceso)

        # liberar memoria si estaba asignada
        if getattr(proceso, "_mem_asignada", False):
            try:
                self.gestor_memoria.liberar(proceso.pid)
            except Exception:
                pass
            proceso._mem_asignada = False

        proceso.forzar_finalizacion()
        if self.pid_en_ejecucion == getattr(proceso, 'pid', None):
            self.pid_en_ejecucion = None

    # ---------------- Internos ----------------
    def _by_pid(self, pid) -> Optional[Any]:
        for p in self._procesos:
            if getattr(p, 'pid', None) == pid:
                return p
        return None

    def _clear_running(self):
        for p in self._procesos:
            if not p.esta_terminado():
                p.estado = 'En espera'
        self.pid_en_ejecucion = None

    def _marcar_en_ejecucion(self, proceso):
        self.pid_en_ejecucion = getattr(proceso, 'pid', None)

        # ---- RESERVA DE MEMORIA al entrar a CPU (una sola vez) ----
        if not getattr(proceso, "_mem_asignada", False):
            mem_req = int(getattr(proceso, "memoria_requerida", 0) or 0)
            if mem_req > 0:
                try:
                    ok = self.gestor_memoria.reservar(proceso.pid, mem_req)
                    if ok:
                        proceso._mem_asignada = True
                    else:
                        # si no hay memoria suficiente, simplemente no marcamos la bandera
                        # (se puede añadir política para bloquear ejecución si quieres)
                        proceso._mem_asignada = False
                except Exception:
                    proceso._mem_asignada = False

        for p in self._procesos:
            if p is proceso:
                if not p.esta_terminado():
                    p.estado = 'En ejecución'
            else:
                if not p.esta_terminado():
                    p.estado = 'En espera'
