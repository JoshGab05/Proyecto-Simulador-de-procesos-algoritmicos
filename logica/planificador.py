# logica/planificador.py
# Delegador SIN reordenar la lista visual:
# - Mantiene la lista en el mismo orden en que agregas procesos.
# - La ejecución por algoritmo ocurre internamente.
# - El algoritmo debe decidir "a quién correr" por tick, pero NO tocar el orden visual.

from typing import List, Optional, Any

class Planificador:
    def __init__(self, gestor_memoria):
        self.gestor_memoria = gestor_memoria

        # Lista estable que se muestra en UI (no se reordena)
        self._procesos: List[Any] = []

        # Simulación
        self.ejecutando: bool = False
        self.tiempo_actual: int = 0
        self.historial: List[Any] = []          # finalizados (no se quitan de la lista visual)
        self.pid_en_ejecucion: Optional[int] = None

        # Algoritmo
        self.algoritmo_seleccionado: Optional[str] = None
        self._alg_inst = None  # instancia del algoritmo cargado

    # ---------------- Configuración ----------------
    def set_algoritmo(self, nombre: str):
        """Selecciona el algoritmo: FCFS, SJF, SRTF o Round Robin."""
        self.algoritmo_seleccionado = nombre
        self._alg_inst = None  # forzar recarga en aplicar_algoritmo()

    def _ensure_alg_instance(self):
        """Carga (una vez) el módulo del algoritmo y devuelve la instancia."""
        if self._alg_inst is not None:
            return self._alg_inst

        if not self.algoritmo_seleccionado:
            return None

        mapping = {
            'FCFS': ('algoritmos.fcfs', 'AlgoritmoFIFO'),
            'SJF': ('algoritmos.sjf', 'AlgoritmoSJF'),
            'SRTF': ('algoritmos.srtf', 'AlgoritmoSRTF'),
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
            # Si aún no existe el archivo o la clase, no reventamos la app.
            return None

    # ---------------- Gestión de procesos ----------------
    def agregar_proceso(self, proceso):
        """Agrega un proceso al final (orden visual estable)."""
        self._procesos.append(proceso)

    def eliminar_proceso(self, pid):
        # No la usaremos normalmente (queremos lista estable). Si la llamas, respeta eso.
        for p in self._procesos:
            if getattr(p, 'pid', None) == pid:
                # En vez de quitarlo, lo marcamos Finalizado (si se desea "remover", cámbialo).
                p.forzar_finalizacion()
                if p not in self.historial:
                    self.historial.append(p)
                break

    # ---------------- Ciclo de simulación ----------------
    def iniciar(self):
        self.ejecutando = True

    def detener(self):
        self.ejecutando = False
        # Al detener, si había uno en ejecución y no terminó, vuelve a "En espera"
        if self.pid_en_ejecucion is not None:
            proc = self._by_pid(self.pid_en_ejecucion)
            if proc and not proc.esta_terminado():
                proc.estado = 'En espera'
        self.pid_en_ejecucion = None

    def aplicar_algoritmo(self):
        """
        Preparación del algoritmo (no reordena la lista visual).
        Llama opcionalmente a setup() o planificar() del algoritmo, pero siempre le pasa
        una COPIA de la lista (para que no pueda reordenar la visual).
        """
        alg = self._ensure_alg_instance()
        if alg is None:
            return
        # Pasamos copia de la lista (mismos objetos Proceso), así no puede reordenar la visual.
        copia = list(self._procesos)
        # Soportamos ambos nombres por compatibilidad:
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
        Avanza el tiempo y pide al algoritmo "a quién correr" SIN reordenar la lista.
        Protocolo sugerido del algoritmo:
          - implementar seleccionar(candidatos, planificador) -> pid | Proceso | None
          - candidatos: procesos que ya llegaron y no están finalizados, en el MISMO orden visual.
        Si el algoritmo no está o no implementa seleccionar(), usamos un fallback estable:
          - primer proceso elegible en orden visual.
        """
        if not self.ejecutando:
            return

        self.tiempo_actual += int(delta)

        # Candidatos: llegaron y no terminaron (en orden visual)
        candidatos = [p for p in self._procesos
                      if (getattr(p, 'instante_llegada', 0) <= self.tiempo_actual) and not p.esta_terminado()]

        if not candidatos:
            # Nadie para ejecutar en este tick
            self._clear_running()
            return

        # Preguntar al algoritmo (si existe) a quién correr
        elegido = None
        alg = self._ensure_alg_instance()
        if alg and hasattr(alg, 'seleccionar'):
            try:
                elegido = alg.seleccionar(list(candidatos), planificador=self)  # pasar copia para no alterar orden
            except Exception:
                elegido = None

        # Normalizar a objeto Proceso
        proc_elegido = None
        if elegido is not None:
            if hasattr(elegido, 'pid'):
                proc_elegido = elegido
            else:
                # quizá retornó un pid:
                proc_elegido = self._by_pid(elegido)

        # Fallback estable: primer candidato en orden visual
        if proc_elegido is None:
            proc_elegido = candidatos[0]

        # Actualizar estados visuales
        self._marcar_en_ejecucion(proc_elegido)

        # Avanzar el proceso seleccionado
        proc_elegido.avanzar(delta=delta)

        # Si terminó, lo registramos en historial (pero NO lo quitamos de la lista)
        if proc_elegido.esta_terminado():
            if proc_elegido not in self.historial:
                self.historial.append(proc_elegido)
            # El que estaba corriendo ya terminó
            self.pid_en_ejecucion = None

    # ---------------- Utilidades visibles por la UI ----------------
    def obtener_procesos(self):
        """Lista en el orden EXACTO en que fueron agregados (visual)."""
        return list(self._procesos)

    def obtener_procesos_activos(self):
        """Solo para compatibilidad; aquí podemos devolver el 'en ejecución' si quieres."""
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
        """Puedes llamarla desde tu algoritmo si decides finalizar manualmente."""
        if proceso not in self.historial:
            self.historial.append(proceso)
        # NO eliminar de la lista visual
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
        """Pone todos los no-finalizados en 'En espera' y limpia marcador."""
        for p in self._procesos:
            if not p.esta_terminado():
                p.estado = 'En espera'
        self.pid_en_ejecucion = None

    def _marcar_en_ejecucion(self, proceso):
        """Marca solo a 'proceso' como En ejecución; los demás elegibles quedan En espera."""
        self.pid_en_ejecucion = getattr(proceso, 'pid', None)
        for p in self._procesos:
            if p is proceso:
                if not p.esta_terminado():
                    p.estado = 'En ejecución'
            else:
                if not p.esta_terminado():
                    p.estado = 'En espera'
