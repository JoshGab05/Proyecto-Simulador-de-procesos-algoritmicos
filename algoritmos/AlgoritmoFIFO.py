# algoritmos/fifo.py
from collections import deque

class AlgoritmoFIFO:
    """
    Planificación no expropiativa (First-Come, First-Served).
    Reutiliza los mismos callbacks que Round Robin para que la GUI pinte igual.
    Callbacks:
      - on_context_switch(t, prev, nxt)
      - on_tick(t, running)
      - on_finish(t, proceso)
    El 'proceso' debe tener: id, nombre, llegada, duracion, restante.
    """

    def __init__(self, on_context_switch=None, on_tick=None, on_finish=None):
        self.ready = deque()
        self._running = None
        self.on_context_switch = on_context_switch or (lambda *_: None)
        self.on_tick = on_tick or (lambda *_: None)
        self.on_finish = on_finish or (lambda *_: None)
        self.finished_ids = set()

    def push_arrivals(self, t, nuevos):
        # 'nuevos' viene de la lógica de tu planificador, ya con llegada==t.
        for p in sorted(nuevos, key=lambda x: (p.llegada, p.id)):
            self.ready.append(p)

    def _dispatch_if_idle(self, t):
        if self._running is None and self.ready:
            nxt = self.ready.popleft()
            prev = None
            self._running = nxt
            self.on_context_switch(t, prev, nxt)

    def tick(self, t):
        self._dispatch_if_idle(t)

        if self._running is None:
            self.on_tick(t, None)  # CPU ociosa
            return None

        self._running.restante -= 1
        self.on_tick(t, self._running)

        if self._running.restante <= 0:
            fin = self._running
            self._running = None
            self.finished_ids.add(fin.id)
            self.on_finish(t, fin)

        return self._running

    def running(self):
        return self._running
