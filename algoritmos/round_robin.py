# algoritmos/round_robin.py
from collections import deque

class AlgoritmoRoundRobin:
    def __init__(self, default_quantum: int = 2):
        self.default_quantum = max(1, int(default_quantum))
        self.ready = deque()
        self._current = None
        self._q_left = 0

    def setup(self, procesos, planificador=None):
        self.ready.clear()
        self._current = None
        self._q_left = 0

    def seleccionar(self, candidatos, planificador=None):
        # helpers
        def getp(pid):
            for p in candidatos:
                if p.pid == pid:
                    return p
            return None

        # Depurar cola: mantener solo pids elegibles y no terminados
        elegibles = set(p.pid for p in candidatos if not p.esta_terminado())
        self.ready = deque(pid for pid in self.ready if pid in elegibles)

        # Añadir nuevos pids al final si no están ya
        for p in candidatos:
            if p.pid not in self.ready and not p.esta_terminado():
                self.ready.append(p.pid)

        # Si hay un actual con quantum restante y sigue elegible, mantenerlo
        if self._current is not None and self._q_left > 0 and self._current in elegibles:
            pid_sel = self._current
        else:
            # Rotar cola
            if not self.ready:
                self._current = None
                self._q_left = 0
                return None
            self.ready.rotate(-1)
            pid_sel = self.ready[0]
            pr = getp(pid_sel)
            # Calcular quantum (propio o default)
            q = getattr(pr, 'quantum', None) or self.default_quantum
            try:
                q = int(q)
            except Exception:
                q = self.default_quantum
            self._q_left = max(1, q)
            self._current = pid_sel

        # Consumir 1 de quantum y devolver selección
        self._q_left = max(0, self._q_left - 1)
        return pid_sel