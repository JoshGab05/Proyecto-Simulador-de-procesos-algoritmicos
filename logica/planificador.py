# logica/planificador.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class PCB:
    pid: int
    nombre: str
    instante_llegada: int
    cpu_total: int
    cpu_restante: int
    estado: str = "En espera"          # "En espera" | "En ejecución" | "Terminado"
    t_inicio: Optional[int] = None
    t_fin: Optional[int] = None
    # métricas
    respuesta: Optional[int] = None    # t_inicio - llegada
    retorno: Optional[int] = None      # t_fin - llegada
    espera: Optional[int] = None       # retorno - cpu_total
    eficiencia: Optional[float] = None # cpu_total / retorno

    # --- ALIAS de compatibilidad para la UI ---
    @property
    def llegada(self) -> int:
        return self.instante_llegada

    @property
    def cpu(self) -> int:
        return self.cpu_total


class Planificador:
    def __init__(self, gestor_memoria):
        self.gestor = gestor_memoria
        self._t: int = 0
        self._pid_counter: int = 1
        self._alg: str = "FCFS"
        self._quantum_cfg: int = 2

        self._procesos: List[PCB] = []
        self._nuevos: List[PCB] = []
        self._ready: List[PCB] = []
        self._finalizados_tick: List[PCB] = []
        self._running: Optional[PCB] = None

        # RR
        self._rr_q_left: int = 0
        self._rr_demote_pending: Optional[PCB] = None

        # NUEVO: orden global de finalización (para el panel de la izquierda)
        self._orden_finalizacion: List[PCB] = []

    # ---------------- Config ----------------
    def set_algoritmo(self, nombre: str):
        nombre = (nombre or "FCFS").strip().upper()
        if nombre not in ("FCFS", "SJF", "SRTF", "RR"):
            nombre = "FCFS"
        self._alg = nombre

    # Compatibilidad con otros nombres usados por la UI
    seleccionar_algoritmo = set_algoritmo
    configurar_algoritmo  = set_algoritmo

    def set_quantum(self, q: int):
        try:
            q = int(q)
        except Exception:
            q = 2
        self._quantum_cfg = max(1, q)

    # --------------- Altas ------------------
    def agregar_proceso(
        self,
        nombre: str,
        tiempo_cpu: Optional[int] = None,
        instante_llegada: Optional[int] = None,
        *,
        cpu: Optional[int] = None,
        llegada: Optional[int] = None,
    ):
        # Firma flexible
        if cpu is not None and tiempo_cpu is None:
            tiempo_cpu = cpu
        if llegada is not None and instante_llegada is None:
            instante_llegada = llegada
        if tiempo_cpu is None:
            tiempo_cpu = 1
        if instante_llegada is None:
            instante_llegada = 0

        pcb = PCB(
            pid=self._pid_counter,
            nombre=str(nombre),
            instante_llegada=int(instante_llegada),
            cpu_total=int(tiempo_cpu),
            cpu_restante=int(tiempo_cpu),
        )
        self._pid_counter += 1

        self._procesos.append(pcb)
        if pcb.instante_llegada <= self._t:
            self._ready.append(pcb)
        else:
            self._nuevos.append(pcb)

    def obtener_procesos(self) -> List[PCB]:
        return list(self._procesos)

    def esta_terminado(self) -> bool:
        """True si ya no queda nada por ejecutar ni por llegar."""
        return not (self._running or self._ready or self._nuevos or self._rr_demote_pending)

    # ------------- Estado para UI -----------
    def estado_cpu(self) -> Dict[str, Any]:
        running = {"nombre": self._running.nombre} if self._running else None
        ready = [{"nombre": p.nombre} for p in self._ready]
        final = [{"nombre": p.nombre, "t_fin": p.t_fin} for p in self._finalizados_tick]
        # NUEVO: estado con orden global acumulado
        orden = [{"pid": p.pid, "nombre": p.nombre, "t_fin": p.t_fin} for p in self._orden_finalizacion]
        return {
            "t": self._t,
            "alg": self._alg,
            "running": running,
            "ready": ready,
            "finalizados": final,
            "orden_finalizacion": orden,
        }

    # ------------- API pública --------------
    def tick(self):
        """Avanza exactamente 1 tick y devuelve un resumen para el UI."""
        return self._tick()

    avanzar = tick
    ejecutar_tick = tick

    def simular_tick(self, n: int = 1):
        for _ in range(max(1, int(n))):
            self._tick()

    def reiniciar(self):
        self._t = 0
        self._pid_counter = 1
        antiguos = self._procesos
        self._procesos = []
        self._nuevos = []
        self._ready = []
        self._finalizados_tick = []
        self._running = None
        self._rr_q_left = 0
        self._rr_demote_pending = None
        self._orden_finalizacion = []
        for p in antiguos:
            self.agregar_proceso(p.nombre, tiempo_cpu=p.cpu_total, instante_llegada=p.instante_llegada)

    # ------------- Métricas / Tabla de eficiencia -------------
    def obtener_metricas(self):
        """
        Devuelve una lista de filas con:
        (pid, nombre, llegada, cpu_total, t_fin, retorno, espera, respuesta, eficiencia)
        y una fila de promedios al final (con 'PROMEDIO' en la columna nombre).
        """
        filas = []
        for p in self._procesos:
            pid = p.pid
            nombre = p.nombre
            llegada = p.instante_llegada
            cpu = p.cpu_total

            t_fin = p.t_fin
            if t_fin is not None:
                retorno = t_fin - llegada
                espera = retorno - cpu
                respuesta = p.respuesta if p.respuesta is not None else None
                eficiencia = round(cpu / retorno, 2) if retorno and retorno > 0 else 0.0
            else:
                retorno = None
                espera = None
                respuesta = p.respuesta if p.respuesta is not None else None
                eficiencia = None

            filas.append((pid, nombre, llegada, cpu, t_fin, retorno, espera, respuesta, eficiencia))

        # Promedios (solo de columnas numéricas presentes)
        def _avg(idx: int):
            vals = [v[idx] for v in filas if isinstance(v[idx], (int, float))]
            return round(sum(vals) / len(vals), 2) if vals else 0

        fila_prom = (
            "", "PROMEDIO", "", "",
            _avg(4),  # t_fin
            _avg(5),  # retorno
            _avg(6),  # espera
            _avg(7),  # respuesta
            _avg(8),  # eficiencia
        )

        return filas, fila_prom

    def obtener_orden_finalizacion(self) -> List[Dict[str, Any]]:
        """Conveniencia para la UI."""
        return [{"pid": p.pid, "nombre": p.nombre, "t_fin": p.t_fin} for p in self._orden_finalizacion]

    # ------------- Interno ------------------
    def _tick(self):
        self._finalizados_tick = []

        # 1) mover llegadas del tiempo actual
        llegados = [p for p in self._nuevos if p.instante_llegada <= self._t]
        for p in llegados:
            self._nuevos.remove(p)
            self._ready.append(p)

        # 1.1) RR: reencolar el que agotó quantum, DESPUÉS de llegadas
        if self._alg == "RR" and self._rr_demote_pending is not None:
            self._rr_demote_pending.estado = "En espera"
            self._ready.append(self._rr_demote_pending)
            self._rr_demote_pending = None

        # 2) SRTF: preempción por llegadas en este mismo tick
        if self._alg == "SRTF" and self._running and self._ready:
            mejor = min(self._ready, key=lambda p: (p.cpu_restante, p.instante_llegada, p.pid))
            if mejor.cpu_restante < self._running.cpu_restante:
                self._running.estado = "En espera"
                self._ready.append(self._running)
                self._ready.remove(mejor)
                self._running = mejor
                # IMPORTANTE: setear inicio/respuesta/estado aquí porque el paso 3 no corre
                if self._running.t_inicio is None:
                    self._running.t_inicio = self._t
                    self._running.respuesta = self._running.t_inicio - self._running.instante_llegada
                self._running.estado = "En ejecución"

        # 3) si no hay running, seleccionar ahora
        if self._running is None and self._ready:
            if self._alg == "FCFS":
                cand = min(self._ready, key=lambda p: (p.instante_llegada, p.pid))
            elif self._alg == "SJF":
                cand = min(self._ready, key=lambda p: (p.cpu_total, p.instante_llegada, p.pid))
            elif self._alg == "SRTF":
                cand = min(self._ready, key=lambda p: (p.cpu_restante, p.instante_llegada, p.pid))
            else:  # RR
                cand = self._ready[0]
            self._ready.remove(cand)
            self._running = cand
            if self._running.t_inicio is None:
                self._running.t_inicio = self._t
                self._running.respuesta = self._running.t_inicio - self._running.instante_llegada
            self._running.estado = "En ejecución"
            if self._alg == "RR":
                self._rr_q_left = self._quantum_cfg

        # 4) ejecutar en este tick
        pid_en_cpu = None
        if self._running:
            pid_en_cpu = self._running.pid
            self._running.cpu_restante -= 1
            if self._alg == "RR":
                self._rr_q_left -= 1

            # 4.1) ¿terminó?
            if self._running.cpu_restante <= 0:
                self._running.estado = "Terminado"
                self._running.t_fin = self._t + 1
                self._running.retorno = self._running.t_fin - self._running.instante_llegada
                self._running.espera = self._running.retorno - self._running.cpu_total
                self._running.eficiencia = (self._running.cpu_total / self._running.retorno) if self._running.retorno else 0.0
                self._finalizados_tick.append(self._running)
                # NUEVO: registrar orden global
                self._orden_finalizacion.append(self._running)
                self._running = None
                self._rr_demote_pending = None  # por si acaso

            # 4.2) RR: agotó quantum (no terminó) → demorar reencolar al próximo tick
            elif self._alg == "RR" and self._rr_q_left <= 0:
                self._rr_demote_pending = self._running
                self._running = None
                # el quantum se repone cuando se asigne un nuevo running

        # 5) resumen
        resumen = {
            "t": self._t,
            "pid": pid_en_cpu,
            "finalizados": [p.pid for p in self._finalizados_tick],
            "alg": self._alg,
        }

        # 6) siguiente tick
        self._t += 1
        return resumen
