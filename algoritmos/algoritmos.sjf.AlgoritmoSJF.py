from typing import List, Optional

class AlgoritmoSJF:
    def __init__(self) -> None:
        self._proceso_ejecutando: Optional[int] = None

    def setup(self, procesos: List[object], planificador=None) -> None:
        """Reinicia el estado del algoritmo"""
        self._proceso_ejecutando = None

    def _get_duracion_cpu(self, proceso: object) -> int:
        """Obtiene de forma segura la duración de CPU de un proceso"""
        try:
            # Intentar múltiples nombres de atributos posibles
            if hasattr(proceso, 'tiempo_cpu'):
                tiempo = proceso.tiempo_cpu
            elif hasattr(proceso, 'duracion'):
                tiempo = proceso.duracion
            elif hasattr(proceso, 'burst_time'):
                tiempo = proceso.burst_time
            else:
                return 0
            
            # Asegurar que es un entero válido
            tiempo_int = int(tiempo)
            return max(1, tiempo_int)  # Mínimo 1 para evitar problemas
            
        except (ValueError, TypeError, AttributeError):
            return 0

    def _get_tiempo_actual(self, planificador) -> int:
        """Obtiene de forma segura el tiempo actual del planificador"""
        if planificador and hasattr(planificador, 'tiempo_actual'):
            try:
                return int(planificador.tiempo_actual)
            except (ValueError, TypeError):
                pass
        return 0

    def _puede_ejecutar(self, proceso: object, tiempo_actual: int) -> bool:
        """Verifica si un proceso es elegible para ejecutar"""
        # Verificar si el proceso ya terminó
        if getattr(proceso, 'esta_terminado', lambda: False)():
            return False
        
        # Verificar si el proceso ha llegado
        instante_llegada = getattr(proceso, 'instante_llegada', float('inf'))
        return instante_llegada <= tiempo_actual

    def _esta_ocupado(self) -> bool:
        """Verifica si ya hay un proceso ejecutándose"""
        return self._proceso_ejecutando is not None

    def seleccionar(self, candidatos: List[object], planificador=None) -> Optional[int]:
        """
        Selecciona el proceso con el menor tiempo de CPU (SJF no preemptivo)
        
        SJF no interrumpe procesos en ejecución, así que si hay uno ejecutándose,
        continúa con él hasta que termine.
        """
        tiempo_actual = self._get_tiempo_actual(planificador)
        
        # Si ya hay un proceso ejecutándose, continuar con él (no preemptivo)
        if self._esta_ocupado():
            # Buscar el proceso actual en la lista de candidatos
            proceso_actual = next(
                (p for p in candidatos if getattr(p, 'pid', None) == self._proceso_ejecutando),
                None
            )
            
            # Si el proceso actual existe y puede ejecutar, continuar con él
            if (proceso_actual and 
                self._puede_ejecutar(proceso_actual, tiempo_actual) and
                not getattr(proceso_actual, 'esta_terminado', lambda: False)()):
                return self._proceso_ejecutando
        
        # Si no hay proceso ejecutándose o el actual terminó, buscar nuevo proceso
        self._proceso_ejecutando = None
        
        # Filtrar procesos elegibles (que han llegado y no han terminado)
        elegibles = [
            p for p in candidatos 
            if self._puede_ejecutar(p, tiempo_actual)
        ]
        
        if not elegibles:
            return None

        try:
            # Seleccionar el proceso con el menor tiempo de CPU
            # En SJF usamos el tiempo total de CPU, no el tiempo restante
            mejor_proceso = min(
                elegibles,
                key=lambda p: (
                    self._get_duracion_cpu(p),          # Primero por tiempo de CPU
                    getattr(p, 'instante_llegada', 0),  # Luego por tiempo de llegada
                    getattr(p, 'pid', 0)                # Finalmente por PID
                )
            )
            
            self._proceso_ejecutando = mejor_proceso.pid
            return self._proceso_ejecutando
            
        except (ValueError, AttributeError):
            # Fallback en caso de error
            if elegibles:
                first = elegibles[0]
                self._proceso_ejecutando = getattr(first, 'pid', None)
                return self._proceso_ejecutando
            return None

    def on_proceso_terminado(self, pid: int) -> None:
        """Maneja la terminación de un proceso"""
        if self._proceso_ejecutando == pid:
            self._proceso_ejecutando = None

    def on_proceso_expulsado(self, pid: int) -> None:
        """Maneja la expulsión de un proceso (no debería ocurrir en SJF puro)"""
        if self._proceso_ejecutando == pid:
            self._proceso_ejecutando = None

    def __str__(self) -> str:
        return "Algoritmo SJF (Shortest Job First) - No Preemptivo"