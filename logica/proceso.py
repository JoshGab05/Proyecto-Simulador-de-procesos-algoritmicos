# logica/proceso.py
# Modelo de proceso según enunciado:
#  - PID (auto)
#  - Nombre
#  - Tiempo en CPU (total requerido)
#  - Instante de llegada
#  - Quantum (cuando aplique)

import itertools

_pid_seq = itertools.count(1)

class Proceso:
    def __init__(self, nombre, memoria_requerida=0, duracion=0, llegada=0, quantum=None, pid=None):
        """
        Compatibilidad hacia atrás:
          - 'duracion' se mantiene y ahora representa 'Tiempo en CPU total'.
          - 'memoria_requerida' se conserva para la UI/estadística que ya tenías.
        Nuevos campos:
          - 'llegada'  -> instante de llegada (entero)
          - 'quantum'  -> quantum (opcional, útil para Round Robin)
        """
        self.pid = pid if pid is not None else next(_pid_seq)
        self.nombre = nombre
        self.memoria_requerida = int(memoria_requerida) if memoria_requerida is not None else 0

        # Enunciado
        self.tiempo_cpu_total = int(duracion)            # Tiempo en CPU total requerido
        self.instante_llegada = int(llegada)             # Instante de llegada
        self.quantum = None if quantum in (None, "", 0) else int(quantum)

        # Estado de simulación
        self.tiempo_restante = int(duracion)
        self.estado = 'En espera'  # En espera | En ejecución | Finalizado

    # Utilidades mínimas (compatibles con tu versión previa)
    def avanzar(self, delta=1):
        """Consume 'delta' unidades de CPU del proceso."""
        if self.estado != 'Finalizado':
            self.tiempo_restante = max(0, self.tiempo_restante - int(delta))
            if self.tiempo_restante == 0:
                self.estado = 'Finalizado'

    def forzar_finalizacion(self):
        """Marca el proceso como finalizado inmediatamente."""
        self.tiempo_restante = 0
        self.estado = 'Finalizado'

    def esta_terminado(self):
        return self.estado == 'Finalizado'

    def __str__(self):
        pid_corto = str(self.pid)[-4:]
        qtxt = self.quantum if self.quantum is not None else '-'
        return (f"[{self.estado}] {self.nombre} (PID:{pid_corto}) | "
                f"RAM: {self.memoria_requerida} MB | "
                f"CPU total: {self.tiempo_cpu_total}s | Llegada: {self.instante_llegada} | "
                f"Quantum: {qtxt} | Restante: {self.tiempo_restante}s")
