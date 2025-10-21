# logica/planificador.py
from typing import List, Optional, Any
from algoritmos.AlgoritmoFIFO import AlgoritmoFIFO
from algoritmos.algoritmo_sjf import AlgoritmoSJF
from algoritmos.algoritmo_srtf import AlgoritmoSRTF


class Planificador:
    def __init__(self, gestor_memoria):
        self.gestor_memoria = gestor_memoria
        self._procesos: List[Any] = []    # lista visual de procesos
        self.historial: List[dict] = []   # registro de eventos/ticks
        self.ejecutando: bool = False
        self.tiempo_actual: int = 0

        self.pid_en_ejecucion: Optional[int] = None
        self._algoritmo_nombre: str = 'FCFS'
        self._algoritmo = AlgoritmoFIFO()
        self._rr_quantum_default = 2

    # ============================================================== #
    # Gestión de procesos
    # ============================================================== #
    def agregar_proceso(self, proceso) -> bool:
        """Agrega un proceso y reserva memoria si es posible."""
        if not self.gestor_memoria.reservar(proceso.pid, proceso.memoria_requerida):
            # No hay memoria disponible
            self._registrar_evento('NO_HAY_MEMORIA', proceso)
            return False

        proceso.estado = 'En espera'
        self._procesos.append(proceso)
        self._registrar_evento('ALTA', proceso)
        self._reconfigurar_algoritmo()
        return True

    def obtener_procesos(self) -> List[Any]:
        """Devuelve una lista de procesos en memoria."""
        return list(self._procesos)

    def limpiar(self):
        """Limpia todos los procesos y reinicia la simulación."""
        for p in self._procesos:
            self.gestor_memoria.liberar(p.pid)
        self._procesos.clear()
        self.historial.clear()
        self.pid_en_ejecucion = None
        self.tiempo_actual = 0
        self.ejecutando = False

    # ============================================================== #
    # Selección de algoritmo
    # ============================================================== #
    def set_algoritmo(self, nombre: str):
        """Cambia el algoritmo de planificación activa."""
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
            # Import dinámico para evitar romper dependencias
            from algoritmos.round_robin import AlgoritmoRoundRobin
            self._algoritmo_nombre = 'RR'
            self._algoritmo = AlgoritmoRoundRobin(default_quantum=self._rr_quantum_default)
        else:
            raise ValueError(f"Algoritmo desconocido: {nombre}")

        self._reconfigurar_algoritmo()

    def set_rr_quantum(self, q: int):
        """Configura el quantum por defecto para Round Robin."""
        self._rr_quantum_default = max(1, int(q))
        if self._algoritmo_nombre == 'RR' and hasattr(self._algoritmo, 'default_quantum'):
            self._algoritmo.default_quantum = self._rr_quantum_default

    def _reconfigurar_algoritmo(self):
        """Llama al método setup del algoritmo actual si existe."""
        try:
            self._algoritmo.setup(self._procesos, self)
        except Exception:
            pass

    # ============================================================== #
    # Control de simulación
    # ============================================================== #
    def iniciar(self):
        self.ejecutando = True
        self._registrar_evento('INICIO_SIM', None)

    def detener(self):
        self.ejecutando = False
        self._registrar_evento('PAUSA_SIM', None)

    def reiniciar(self):
        """Reinicia el tiempo sin borrar procesos."""
        self.tiempo_actual = 0
        self.pid_en_ejecucion = None
        for p in self._procesos:
            p.cpu_restante = p.cpu_total
            p.estado = 'En espera'
            p.t_inicio = None
            p.t_fin = None
        self.historial.clear()
        self._reconfigurar_algoritmo()

    # ============================================================== #
    # Registro de eventos
    # ============================================================== #
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
            if not p.esta_terminado() and p.estado != 'En espera':
                p.estado = 'En espera'

    # ============================================================== #
    # Simulación paso a paso
    # ============================================================== #
    def simular_tick(self, delta: int = 1):
        if not self.ejecutando:
            return

        self.tiempo_actual += int(delta)

        # Candidatos disponibles
        candidatos = [p for p in self._procesos if p.instante_llegada <= self.tiempo_actual and not p.esta_terminado()]
        if not candidatos:
            self._clear_running()
            self._registrar_evento('IDLE', None)
            return

        # Decidir según el algoritmo
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

        # Ejecutar un tick
        proceso.ejecutar(1)
        self._registrar_evento('RUN', proceso, {"restante": proceso.cpu_restante, "alg": self._algoritmo_nombre})

        # Verificar finalización
        if proceso.esta_terminado():
            proceso.t_fin = self.tiempo_actual
            self.gestor_memoria.liberar(proceso.pid)
            self._registrar_evento('FIN', proceso)
            if hasattr(self._algoritmo, "on_proceso_terminado"):
                try:
                    self._algoritmo.on_proceso_terminado(proceso.pid)
                except Exception:
                    pass

    # ============================================================== #
    # Estado para la interfaz
    # ============================================================== #
    def estado_cpu(self) -> dict:
        """Devuelve el estado actual de la CPU (para la interfaz)."""
        running = None
        for p in self._procesos:
            if p.pid == self.pid_en_ejecucion and not p.esta_terminado():
                running = {"pid": p.pid, "nombre": p.nombre}
                break
        return {"t": self.tiempo_actual, "running": running, "alg": self._algoritmo_nombre}

    
    # ============================================================== #
    # Ejecución visual de Round Robin
    # ============================================================== #
    def ejecutar_round_robin_visual(self, quantum=2, on_tick=None):
        """
        Ejecuta Round Robin de forma visual sin alterar los otros algoritmos.
        Actualiza correctamente los estados, tiempos y orden de finalización.
        """
        try:
            self.detener()
        except Exception:
            pass

        procesos = list(self.obtener_procesos())
        if not procesos:
            print("⚠️ No hay procesos para ejecutar en Round Robin visual.")
            return None

        from algoritmos.round_robin import AlgoritmoRoundRobin as RR
        rr = RR(quantum)
        resultados = rr.ejecutar(procesos, on_tick)

        # 🔁 Sincronizar resultados con los procesos reales
        finalizados = []
        for p_final in resultados["procesos"]:
            for p_real in self._procesos:
                if p_real.pid == p_final.pid:
                    # Copiar todos los tiempos y métricas
                    p_real.t_inicio = getattr(p_final, "t_inicio", None)
                    p_real.t_fin = getattr(p_final, "t_fin", None)
                    p_real.t_retorno = getattr(p_final, "t_retorno", None)
                    p_real.t_espera = getattr(p_final, "t_espera", None)
                    p_real.t_respuesta = getattr(p_final, "t_respuesta", None)
                    p_real.eficiencia = getattr(p_final, "eficiencia", None)

                    # Marcar estado
                    p_real.estado = "Finalizado"
                    finalizados.append(p_real)
                    break

        # 🧾 Registrar el orden de finalización (solo si hay datos válidos)
        if finalizados:
            orden = ""
            for i, p in enumerate(finalizados, start=1):
                t_fin = getattr(p, "t_fin", "?")
                orden += f"{i}. {p.nombre} (PID {p.pid}) — t_fin = {t_fin}\n"

            # Guardar en historial para depuración y panel
            self._registrar_evento("ORDEN_FINALIZACION", None, {"orden": orden.strip()})

            # Registrar cada finalización individual
            for p in finalizados:
                self._registrar_evento("FIN", p, {"t_fin": p.t_fin})

        return resultados
