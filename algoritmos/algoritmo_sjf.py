# algoritmos/algoritmo_sjf.py
class AlgoritmoSJF:
    def __init__(self):
        self._current = None

    def setup(self, procesos, planificador=None):
        self._current = None

    def _dur(self, p):
        # tratar varios nombres posibles
        for attr in ('tiempo_cpu', 'cpu_total', 'duracion'):
            if hasattr(p, attr):
                try:
                    return int(getattr(p, attr))
                except Exception:
                    pass
        return 0

    def seleccionar(self, candidatos, planificador=None):
        # mantener si sigue siendo el más corto entre los elegibles
        if self._current is not None:
            cur = None
            for p in candidatos:
                if p.pid == self._current and not p.esta_terminado():
                    cur = p
                    break
            if cur is not None:
                min_d = min(self._dur(x) for x in candidatos if not x.esta_terminado())
                if self._dur(cur) <= min_d:
                    return cur

        # Elegir por menor duración total; empate: llegada y luego orden dado
        mejores = sorted(
            [p for p in candidatos if not p.esta_terminado()],
            key=lambda p: (self._dur(p), p.instante_llegada)
        )
        if not mejores:
            self._current = None
            return None
        self._current = mejores[0].pid
        return mejores[0]