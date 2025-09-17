from logica.gestor_memoria import GestorMemoria
from logica.planificador import Planificador
from logica.proceso import Proceso

print("=== INICIO DE PRUEBA DEL PLANIFICADOR ===")

gestor = GestorMemoria(1024)
plan = Planificador(gestor)

# Crear procesos de prueba
p1 = Proceso("P1", duracion=5, llegada=0)
p2 = Proceso("P2", duracion=3, llegada=1)

plan.agregar_proceso(p1)
plan.agregar_proceso(p2)

# Simular un paso
plan.iniciar()
plan.simular_tick()
plan.detener()

print("Procesos en cola:")
for p in plan.obtener_procesos():
    print("  ->", p)

print("Tiempo actual:", plan.tiempo_actual)
print("=== FIN DE PRUEBA ===")
