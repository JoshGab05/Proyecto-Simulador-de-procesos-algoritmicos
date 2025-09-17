# logica/gestor_memoria.py

class GestorMemoria:
    def __init__(self, capacidad_total=1024):
        self.capacidad_total = capacidad_total  # en MB
        self.memoria_ocupada = 0
        self.procesos_en_memoria = {}  # pid: memoria_asignada

    def puede_reservar(self, memoria):
        return self.memoria_ocupada + memoria <= self.capacidad_total

    def reservar(self, pid, memoria):
        if self.puede_reservar(memoria):
            self.procesos_en_memoria[pid] = memoria
            self.memoria_ocupada += memoria
            return True
        return False

    def liberar(self, pid):
        if pid in self.procesos_en_memoria:
            memoria_liberada = self.procesos_en_memoria.pop(pid)
            self.memoria_ocupada -= memoria_liberada

    def obtener_memoria_usada(self):
        return self.memoria_ocupada

    def obtener_memoria_disponible(self):
        return self.capacidad_total - self.memoria_ocupada

    def obtener_porcentaje_uso(self):
        return round((self.memoria_ocupada / self.capacidad_total) * 100, 2)
