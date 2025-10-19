# logica/proceso.py
import itertools
_pid_seq = itertools.count(1)

class Proceso:
    def __init__(self, nombre, memoria_requerida=0, duracion=1, llegada=0, quantum=None, pid=None):
        self.pid = int(pid) if pid is not None else next(_pid_seq)
        self.nombre = nombre or f"Proceso {self.pid}"
        self.memoria_requerida = int(memoria_requerida or 0)

        # CPU total y restante (en "ticks")
        self.cpu_total = int(duracion if duracion is not None else 1)
        self.cpu_restante = self.cpu_total

        # Instante de llegada
        self.instante_llegada = int(llegada or 0)

        # Quantum opcional (para RR)
        self.quantum = None if quantum in (None, "", "-") else int(quantum)

        # Estados / métricas
        self.estado = 'Nuevo'          # Nuevo, En espera, En ejecución, Finalizado
        self.t_inicio = None           # tick en que comenzó a ejecutar por 1a vez
        self.t_fin = None              # tick en que terminó

    # --- API usada por Planificador ---
    def ejecutar(self, unidades=1):
        if self.estado == 'Finalizado':
            return 0
        n = max(1, int(unidades))
        ejecutado = min(n, self.cpu_restante)
        self.cpu_restante -= ejecutado
        if self.cpu_restante <= 0:
            self.cpu_restante = 0
            self.estado = 'Finalizado'
        return ejecutado

    def forzar_finalizacion(self):
        self.cpu_restante = 0
        self.estado = 'Finalizado'

    def esta_terminado(self) -> bool:
        return self.cpu_restante <= 0

    def __str__(self):
        qtxt = self.quantum if self.quantum is not None else "-"
        return (f"[{self.estado}] {self.nombre} (PID:{self.pid}) | RAM: {self.memoria_requerida} MB | "
                f"CPU total: {self.cpu_total} | llegada: {self.instante_llegada} | Quantum: {qtxt} | "
                f"Restante: {self.cpu_restante}")