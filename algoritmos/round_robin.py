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
        now = getattr(planificador, 'tiempo_actual', 0) if planificador else 0
        elegibles = [p for p in candidatos if not p.esta_terminado()
                     and getattr(p, 'instante_llegada', 0) <= now]
        pids = [p.pid for p in elegibles]

        # depurar cola
        self.ready = deque([pid for pid in self.ready if pid in pids])

        # alta de nuevos (en orden visual)
        for p in elegibles:
            if p.pid not in self.ready:
                self.ready.append(p.pid)

        if not self.ready:
            self._current = None
            self._q_left = 0
            return None

        def getp(pid):
            for pr in elegibles:
                if pr.pid == pid:
                    return pr
            return None

        # si aún queda quantum, continúa el actual
        if (self._current in self.ready) and self._q_left > 0:
            pid_sel = self._current
        else:
            # rotar round-robin
            if self._current in self.ready:
                while self.ready and self.ready[0] != self._current:
                    self.ready.rotate(-1)
                if self.ready:
                    self.ready.rotate(-1)

            pid_sel = self.ready[0]
            pr = getp(pid_sel)
            q = getattr(pr, 'quantum', None) or self.default_quantum
            try:
                q = int(q)
            except Exception:
                q = self.default_quantum
            self._q_left = max(1, q)
            self._current = pid_sel

        # consumir 1 de quantum y retornar PID
        self._q_left = max(0, self._q_left - 1)
        return pid_sel
