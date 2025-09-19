from typing import List, Optional

class AlgoritmoSRTF:
    def __init__(self) -> None:
        self._current: Optional[int] = None

    def setup(self, procesos: List[object], planificador=None) -> None:
        self._current = None

    def _tiempo_restante(self, p: object) -> int:
        tr = getattr(p, "tiempo_restante", None)
        if tr is None:
            tr = getattr(p, "tiempo_cpu", 0)
        try:
            tr = int(tr)
        except Exception:
            tr = 0
        return max(0, tr)

    def seleccionar(self, candidatos: List[object], planificador=None) -> Optional[int]:
        now = getattr(planificador, "tiempo_actual", 0) if planificador else 0
        elegibles = [
            p for p in candidatos
            if not getattr(p, "esta_terminado", lambda: False)()
            and getattr(p, "instante_llegada", 0) <= now
        ]
        if not elegibles:
            self._current = None
            return None

        min_tr = min(self._tiempo_restante(p) for p in elegibles)
        mejores = [p for p in elegibles if self._tiempo_restante(p) == min_tr]

        if self._current is not None and any(p.pid == self._current for p in mejores):
            return self._current

        elegido = min(mejores, key=lambda p: (p.instante_llegada, p.pid))
        self._current = elegido.pid
        return self._current
