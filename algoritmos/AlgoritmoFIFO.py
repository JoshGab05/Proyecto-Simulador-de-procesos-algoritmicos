# FCFS (First-Come, First-Served) no expropiativo.
# NO reordena la lista visual: solo decide a quién ejecutar en cada tick.

class AlgoritmoFIFO:
    """
    Protocolo con el Planificador:
      - setup(procesos, planificador)   -> opcional
      - seleccionar(candidatos, planificador) -> devuelve Proceso o pid
    """

    def setup(self, procesos, planificador):
        # FCFS no requiere preparación
        pass

    def seleccionar(self, candidatos, planificador):
        # Mantener el que ya está corriendo (si sigue elegible)
        pid_actual = planificador.pid_en_ejecucion
        if pid_actual is not None:
            for p in candidatos:
                if p.pid == pid_actual and not p.esta_terminado():
                    return p

        # Elegir por menor instante de llegada; empate -> orden visual recibido
        idx_min, _ = min(
            enumerate(candidatos),
            key=lambda t: (t[1].instante_llegada, t[0])
        )
        return candidatos[idx_min]
