import time
import copy
from collections import deque

class AlgoritmoRoundRobin:
    def __init__(self, quantum: int = 2):
        # Quantum mínimo = 1
        self.quantum = max(1, int(quantum))

    def ejecutar(self, procesos, on_tick=None):
        """
        Ejecuta los procesos según el algoritmo Round Robin,
        respetando los instantes de llegada y generando las métricas
        y datos del gráfico para el simulador.
        """
        # Copiar procesos y ordenar por instante de llegada
        pendientes = sorted(
            (copy.deepcopy(p) for p in procesos),
            key=lambda x: int(x.instante_llegada)
        )
        listos = deque()
        tiempo_actual = 0
        resultados = []
        grafico = []

        # Función auxiliar: mueve a los procesos que ya llegaron
        def mover_llegados():
            nonlocal pendientes, listos, tiempo_actual
            while pendientes and int(pendientes[0].instante_llegada) <= tiempo_actual:
                p = pendientes.pop(0)
                p.estado = "Listo"
                listos.append(p)

        # Si no hay nadie en t=0, adelanta al primer arribo
        if pendientes and int(pendientes[0].instante_llegada) > 0:
            tiempo_actual = int(pendientes[0].instante_llegada)
        mover_llegados()

        # Bucle principal
        while listos or pendientes:
            if not listos:
                # No hay procesos listos → saltar al siguiente arribo
                tiempo_actual = max(tiempo_actual, int(pendientes[0].instante_llegada))
                mover_llegados()
                continue

            # Tomar siguiente proceso en la cola
            proceso = listos.popleft()

            nombre = proceso.nombre
            llegada = int(proceso.instante_llegada)
            restante = int(proceso.cpu_restante)

            # Registrar primera ejecución
            if getattr(proceso, "t_inicio", None) is None:
                proceso.t_inicio = tiempo_actual
                proceso.estado = "Ejecutando"

            # Ejecutar hasta el quantum o hasta terminar
            tiempo_ejec = min(self.quantum, restante)
            inicio = tiempo_actual
            fin = tiempo_actual + tiempo_ejec

            # Actualizar reloj y CPU restante
            tiempo_actual += tiempo_ejec
            proceso.cpu_restante -= tiempo_ejec

            # Registrar tramo en el gráfico
            grafico.append({
                "Proceso": nombre,
                "Inicio": inicio,
                "Fin": fin
            })

            # Callback visual (para interfaz)
            if on_tick:
                try:
                    on_tick(tiempo_actual, proceso, [p.nombre for p in listos])
                    time.sleep(3)
                except Exception:
                    pass

            # Mover procesos que llegaron durante este quantum
            mover_llegados()

            # Si terminó
            if proceso.cpu_restante <= 0:
                proceso.t_fin = tiempo_actual
                proceso.estado = "Finalizado"

                # Calcular métricas
                proceso.t_retorno = proceso.t_fin - llegada
                proceso.t_espera = proceso.t_retorno - proceso.cpu_total
                proceso.t_respuesta = proceso.t_inicio - llegada
                proceso.eficiencia = round(
                    proceso.cpu_total / proceso.t_retorno, 3
                ) if proceso.t_retorno else 0.0

                resultados.append(proceso)
            else:
                # Si no terminó, re-encolar
                proceso.estado = "Listo"
                listos.append(proceso)

        # Retornar resultados y datos para el gráfico
        return {
            "procesos": resultados,
            "grafico": grafico
        }
