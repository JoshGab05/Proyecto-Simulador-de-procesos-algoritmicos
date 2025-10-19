# logica/gestor_memoria.py

class GestorMemoria:
    def __init__(self, capacidad_total=1024):
        self.capacidad_total = int(capacidad_total)  # MB
        self.memoria_ocupada = 0
        self.procesos_en_memoria = {}  # pid -> memoria_asignada

    # ---- Consultas ----
    def obtener_memoria_usada(self) -> int:
        return int(self.memoria_ocupada)

    def obtener_memoria_disponible(self) -> int:
        return int(self.capacidad_total - self.memoria_ocupada)

    def obtener_porcentaje_uso(self) -> float:
        if self.capacidad_total <= 0:
            return 0.0
        return round(self.memoria_ocupada * 100.0 / self.capacidad_total, 2)

    # ---- Reservas ----
    def puede_reservar(self, memoria: int) -> bool:
        try:
            m = int(memoria)
        except Exception:
            m = 0
        return (self.memoria_ocupada + max(0, m)) <= self.capacidad_total

    def reservar(self, pid: int, memoria: int) -> bool:
        try:
            m = int(memoria)
        except Exception:
            m = 0
        if m < 0:
            m = 0
        if self.puede_reservar(m):
            self.procesos_en_memoria[pid] = m
            self.memoria_ocupada += m
            return True
        return False

    def liberar(self, pid: int) -> None:
        if pid in self.procesos_en_memoria:
            m = self.procesos_en_memoria.pop(pid)
            self.memoria_ocupada -= int(m)
            if self.memoria_ocupada < 0:
                self.memoria_ocupada = 0