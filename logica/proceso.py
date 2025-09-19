import itertools
_pid_seq = itertools.count(1)

class Proceso:
    def __init__(self, nombre, memoria_requerida=0, duracion=1, llegada=0, quantum=None, pid=None):
        self.pid = int(pid) if pid is not None else next(_pid_seq)

        self.nombre = nombre or f"Proceso {self.pid}"
        self.memoria_requerida = int(memoria_requerida or 0)

        # CPU: total y restante
        self.cpu_total = int(duracion if duracion is not None else 1)
        self.cpu_restante = self.cpu_total

        # llegada (mapea al nombre que usa el planificador)
        self.llegada = int(llegada or 0)
        self.instante_llegada = self.llegada

        # quantum por proceso (opcional)
        self.quantum = int(quantum) if quantum is not None else None

        # estado inicial
        self.estado = 'En espera'

    def avanzar(self, delta: int = 1):
        """Consume exactamente 1 unidad por tick."""
        if self.esta_terminado():
            self.estado = 'Finalizado'
            return
        self.estado = 'En ejecución'
        self.cpu_restante = max(0, self.cpu_restante - 1)
        if self.cpu_restante == 0:
            self.estado = 'Finalizado'

    def forzar_finalizacion(self):
        self.cpu_restante = 0
        self.estado = 'Finalizado'

    def esta_terminado(self) -> bool:
        return self.cpu_restante <= 0

    def __str__(self):
        qtxt = self.quantum if self.quantum is not None else "-"
        return (f"[{self.estado}] {self.nombre} (PID:{self.pid}) | RAM: {self.memoria_requerida} MB | "
                f"CPU total: {self.cpu_total} s | llegada: {self.instante_llegada} | Quantum: {qtxt} | "
                f"Restante: {self.cpu_restante} s")
