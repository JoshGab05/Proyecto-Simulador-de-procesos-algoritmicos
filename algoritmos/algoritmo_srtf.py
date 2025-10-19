# algoritmos/algoritmo_srtf.py
class AlgoritmoSRTF:
    def __init__(self):
        self._current = None

    def setup(self, procesos, planificador=None):
        self._current = None

    def _restante(self, p):
        v = getattr(p, 'tiempo_restante', None)
        if v is None:
            v = getattr(p, 'cpu_restante', None)
        if v is None:
            v = getattr(p, 'cpu_total', 0)
        try:
            return int(v)
        except Exception:
            return 0

    def seleccionar(self, candidatos, planificador=None):
        elegibles = [p for p in candidatos if not p.esta_terminado()]
        if not elegibles:
            self._current = None
            return None

        min_r = min(self._restante(p) for p in elegibles)
        mejores = [p for p in elegibles if self._restante(p) == min_r]

        # Si el actual está en los mejores, se mantiene
        if self._current is not None and any(p.pid == self._current for p in mejores):
            return self._current

        elegido = min(mejores, key=lambda p: (p.instante_llegada, p.pid))
        self._current = elegido.pid
        return self._current