# logica/planificador.py
from typing import List, Optional, Any, Union
from algoritmos.AlgoritmoFIFO import AlgoritmoFIFO
from algoritmos.round_robin import AlgoritmoRoundRobin
from algoritmos.algoritmo_sjf import AlgoritmoSJF
from algoritmos.algoritmo_srtf import AlgoritmoSRTF

class Planificador:
    def __init__(self, gestor_memoria):
        self.gestor_memoria = gestor_memoria
        self._procesos: List[Any] = []    # orden visual
        self.historial: List[dict] = []   # lista de eventos/ticks
        self.ejecutando: bool = False
        self.tiempo_actual: int = 0

        self.pid_en_ejecucion: Optional[int] = None
        self._algoritmo_nombre: str = 'FCFS'
        self._algoritmo = AlgoritmoFIFO()
        self._rr_quantum_default = 2

    # -------- Procesos --------
    def agregar_proceso(self, proceso) -> bool:
        # Intentar reservar RAM al llegar el proceso a memoria
        if not self.gestor_memoria.reservar(proceso.pid, proceso.memoria_requerida):
            # No hay memoria: queda "Nuevo" sin entrar a RAM
            self._registrar_evento('NO_HAY_MEMORIA', proceso)
            return False
        proceso.estado = 'En espera'
        self._procesos.append(proceso)
        self._registrar_evento('ALTA', proceso)
        self._reconfigurar_algoritmo()
        return True

    def obtener_procesos(self) -> List[Any]:
        return list(self._procesos)

    def limpiar(self):
        for p in self._procesos:
            self.gestor_memoria.liberar(p.pid)
        self._procesos.clear()
        self.historial.clear()
        self.pid_en_ejecucion = None
        self.tiempo_actual = 0
        self.ejecutando = False

    # -------- Algoritmo --------
    def set_algoritmo(self, nombre: str):
        nombre = (nombre or '').upper()
        if nombre in ('FCFS', 'FIFO'):
            self._algoritmo_nombre = 'FCFS'
            self._algoritmo = AlgoritmoFIFO()
        elif nombre in ('SJF',):
            self._algoritmo_nombre = 'SJF'
            self._algoritmo = AlgoritmoSJF()
        elif nombre in ('SRTF', 'SJF-P'):
            self._algoritmo_nombre = 'SRTF'
            self._algoritmo = AlgoritmoSRTF()
        elif nombre in ('RR', 'ROUND ROBIN'):
            self._algoritmo_nombre = 'RR'
            self._algoritmo = AlgoritmoRoundRobin(default_quantum=self._rr_quantum_default)
        else:
            raise ValueError(f"Algoritmo desconocido: {nombre}")
        self._reconfigurar_algoritmo()

    def set_rr_quantum(self, q: int):
        self._rr_quantum_default = max(1, int(q))
        if self._algoritmo_nombre == 'RR' and hasattr(self._algoritmo, 'default_quantum'):
            self._algoritmo.default_quantum = self._rr_quantum_default

    def _reconfigurar_algoritmo(self):
        try:
            self._algoritmo.setup(self._procesos, self)
        except Exception:
            pass

    # -------- Simulación --------
    def iniciar(self):
        self.ejecutando = True
        self._registrar_evento('INICIO_SIM', None)

    def detener(self):
        self.ejecutando = False
        self._registrar_evento('PAUSA_SIM', None)

    def reiniciar(self):
        # No borra procesos, solo resetea tiempo y estado de CPU
        self.tiempo_actual = 0
        self.pid_en_ejecucion = None
        for p in self._procesos:
            p.cpu_restante = p.cpu_total
            p.estado = 'En espera'
            p.t_inicio = None
            p.t_fin = None
        self.historial.clear()
        self._reconfigurar_algoritmo()

    def _registrar_evento(self, tipo: str, proceso: Optional[Any], extra: dict | None = None):
        self.historial.append({
            "t": self.tiempo_actual,
            "tipo": tipo,
            "pid": getattr(proceso, 'pid', None),
            "nombre": getattr(proceso, 'nombre', None),
            **(extra or {})
        })

    def _clear_running(self):
        self.pid_en_ejecucion = None
        for p in self._procesos:
            if not p.esta_terminado():
                if p.estado != 'En espera':
                    p.estado = 'En espera'

    def simular_tick(self, delta:int=1):
        if not self.ejecutando:
            return

        self.tiempo_actual += int(delta)

        # Candidatos: ya llegaron y no han terminado
        candidatos = [p for p in self._procesos if p.instante_llegada <= self.tiempo_actual and not p.esta_terminado()]
        if not candidatos:
            self._clear_running()
            self._registrar_evento('IDLE', None)
            return

        # Decidir según algoritmo
        elegido = self._algoritmo.seleccionar(candidatos, self)
        if elegido is None:
            self._clear_running()
            self._registrar_evento('IDLE', None)
            return

        proceso = None
        if isinstance(elegido, int):
            for p in candidatos:
                if p.pid == elegido:
                    proceso = p
                    break
        else:
            proceso = elegido

        if proceso is None:
            self._clear_running()
            self._registrar_evento('IDLE', None)
            return

        # Marcar en ejecución
        self.pid_en_ejecucion = proceso.pid
        if proceso.t_inicio is None:
            proceso.t_inicio = self.tiempo_actual
        for p in self._procesos:
            if p is proceso:
                if not p.esta_terminado():
                    p.estado = 'En ejecución'
            else:
                if not p.esta_terminado():
                    p.estado = 'En espera'

        # Ejecutar 1 unidad
        proceso.ejecutar(1)
        self._registrar_evento('RUN', proceso, {"restante": proceso.cpu_restante, "alg": self._algoritmo_nombre})

        # Al terminar
        if proceso.esta_terminado():
            proceso.t_fin = self.tiempo_actual
            self.gestor_memoria.liberar(proceso.pid)
            self._registrar_evento('FIN', proceso)
            # Notificar al algoritmo si ofrece hook
            if hasattr(self._algoritmo, "on_proceso_terminado"):
                try:
                    self._algoritmo.on_proceso_terminado(proceso.pid)
                except Exception:
                    pass

    # Para auto-refresco UI: estado simple de CPU
    def estado_cpu(self) -> dict:
        running = None
        for p in self._procesos:
            if p.pid == self.pid_en_ejecucion and not p.esta_terminado():
                running = {"pid": p.pid, "nombre": p.nombre}
                break
        return {"t": self.tiempo_actual, "running": running, "alg": self._algoritmo_nombre}