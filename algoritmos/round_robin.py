import time
import copy

class AlgoritmoRoundRobin:
    def __init__(self, quantum: int = 2):
        # Guardamos el quantum como entero positivo
        self.quantum = max(1, int(quantum))

    def ejecutar(self, procesos, on_tick=None):
        """
        Ejecuta los procesos según el algoritmo Round Robin.
        Retorna una lista de procesos finalizados con métricas completas.
        """
        cola = [copy.deepcopy(p) for p in procesos]
        tiempo_actual = 0
        resultados = []
        grafico = []

        while cola:
            proceso = cola.pop(0)

            nombre = proceso.nombre
            llegada = proceso.instante_llegada
            restante = proceso.cpu_restante

            # Si aún no llegó, adelantamos el reloj
            if tiempo_actual < llegada:
                tiempo_actual = llegada

            # 🔹 Registrar tiempo de inicio si es la primera vez que ejecuta
            if getattr(proceso, "t_inicio", None) is None:
                proceso.t_inicio = tiempo_actual

            # Determinar cuánto ejecuta en este turno
            tiempo_ejec = min(self.quantum, restante)
            inicio = tiempo_actual
            fin = tiempo_actual + tiempo_ejec
            tiempo_actual += tiempo_ejec
            proceso.cpu_restante -= tiempo_ejec

            # Registrar tramo en gráfico
            grafico.append({
                "Proceso": nombre,
                "Inicio": inicio,
                "Fin": fin
            })

            # Callback visual (para interfaz)
            if on_tick:
                on_tick(tiempo_actual, proceso, [p.nombre for p in cola])
                time.sleep(3)

            # Si no terminó, vuelve al final de la cola
            if proceso.cpu_restante > 0:
                cola.append(proceso)
            else:
                # 🔹 Proceso terminado
                proceso.t_fin = tiempo_actual
                proceso.estado = "Finalizado"

                # Calcular métricas finales
                proceso.t_retorno = proceso.t_fin - proceso.instante_llegada
                proceso.t_espera = proceso.t_retorno - proceso.cpu_total
                proceso.t_respuesta = proceso.t_inicio - proceso.instante_llegada
                proceso.eficiencia = round(
                    proceso.cpu_total / proceso.t_retorno, 3
                ) if proceso.t_retorno else 0.0

                resultados.append(proceso)

        # Retornar resultados y datos del gráfico
        return {
            "procesos": resultados,
            "grafico": grafico
        }
