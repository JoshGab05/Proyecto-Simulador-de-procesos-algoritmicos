# logica/planificador_fifo.py
from typing import List, Callable
from algoritmos.fifo import AlgoritmoFIFO

class PlanificadorFIFO:

    def __init__(self,
                 on_context_switch: Callable = None,
                 on_tick: Callable = None,
                 on_finish: Callable = None):
        self.core = AlgoritmoFIFO(on_context_switch, on_tick, on_finish)
        self.t = 0
        self._pendientes: List = []

    def cargar_procesos(self, procesos: List):
        # Asegura .restante en cada proceso
        for p in procesos:
            if getattr(p, "restante", None) is None:
                p.restante = int(p.duracion)
        # Ordena por llegada (y por id para estabilidad)
        self._pendientes = sorted(procesos, key=lambda x: (x.llegada, x.id))

    def _arrivals_at(self, t: int):
        llegados = []
        while self._pendientes and self._pendientes[0].llegada == t:
            llegados.append(self._pendientes.pop(0))
        return llegados

    def step(self):
        nuevos = self._arrivals_at(self.t)
        if nuevos:
            self.core.push_arrivals(self.t, nuevos)
        self.core.tick(self.t)
        self.t += 1

    def running(self):
        return self.core.running()
