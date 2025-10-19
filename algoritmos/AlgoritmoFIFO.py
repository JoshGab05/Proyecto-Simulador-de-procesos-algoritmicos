# algoritmos/AlgoritmoFIFO.py
class AlgoritmoFIFO:
    def setup(self, procesos, planificador=None):
        pass

    def seleccionar(self, candidatos, planificador=None):
        # Mantener el que ya corre si sigue elegible
        pid_actual = getattr(planificador, 'pid_en_ejecucion', None) if planificador else None
        if pid_actual is not None:
            for p in candidatos:
                if p.pid == pid_actual and not p.esta_terminado():
                    return p

        # Elegir el de menor instante de llegada (empate conserva orden dado)
        idx, _ = min(enumerate(candidatos), key=lambda t: (t[1].instante_llegada, t[0]))
        return candidatos[idx]