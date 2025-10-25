#  Proyecto: Simulador de Procesos Algorítmicos

Este proyecto es un **simulador gráfico de planificación de procesos** que implementa distintos **algoritmos de planificación de CPU**.  
Fue desarrollado en **Python** con soporte para interfaz gráfica usando **CustomTkinter**.

<img width="96" height="25" alt="image" src="https://github.com/user-attachments/assets/f2925711-d7c6-41e6-9d14-6fc1d50fc4f8" />
<img width="156" height="25" alt="image" src="https://github.com/user-attachments/assets/2b94aaf3-5a63-43ec-aa9d-5a1f15e080eb" />



---

##  Características principales

- Simulación de **procesos con llegada, duración, quantum y memoria RAM**.
- Interfaz gráfica moderna con **CustomTkinter**.
- Visualización en tiempo real de:
  - Estado de la memoria.
  - Procesos en ejecución y en espera.
  - Historial de ejecución (ticks).

## Visualización Avanzada
-  Diagrama de Gantt interactivo en tiempo real.
-  Tabla de ejecución con marcas por tick.
-  Panel de métricas con cálculos automáticos.
- Orden de finalización de procesos.
- Interfaz responsive adaptable a diferentes tamaños.

- Soporte para múltiples algoritmos de planificación:
  - **FCFS (First Come, First Served)**: Planificación no expropiativa.
  - **SJF (Shortest Job First)**: Selecciona el proceso más corto.
  - **SRTF (Shortest Remaining Time First)**: Versión expropiativa de SJF.
  - **Round Robin** (con quantum configurable).
- Gestión de memoria con asignación y liberación dinámica.

## Funcionalidades
- Configuración flexible de procesos (nombre, CPU, llegada, RAM).
- Control de simulación (iniciar, pausar, reiniciar).
- Cálculo automático de métricas de desempeño.
- Gestión de memoria con límites configurables.
- Exportación visual de resultados.

## Tecnologías Utilizadas

Backend

<img width="85" height="19" alt="image" src="https://github.com/user-attachments/assets/c49a358e-9878-4759-8910-1c1c8bd48758" />
<img width="102" height="17" alt="image" src="https://github.com/user-attachments/assets/ebe5485b-1185-4cf4-913e-21e5a6f807d9" />
<img width="20" height="18" alt="image" src="https://github.com/user-attachments/assets/9c529df0-e79f-4d20-abc6-0cec29c0a577" />
<img width="20" height="18" alt="image" src="https://github.com/user-attachments/assets/5e03bf19-5b8b-456f-ba7c-09421a920be7" />
<img width="20" height="18" alt="image" src="https://github.com/user-attachments/assets/5875227c-218e-472d-9720-c69a71c36242" />

Frontend

<img width="157" height="25" alt="image" src="https://github.com/user-attachments/assets/de746c74-8477-4414-9d45-1df5d3ccc7c7" />
<img width="129" height="27" alt="image" src="https://github.com/user-attachments/assets/f5e84bbb-62eb-4631-8a19-8a37fad868d2" />



---

##  Estructura del proyecto
1. Clonar el repositorio:
   ```bash
    Proyecto-Simulador-de-procesos-algoritmicos/
    ├── logica/
    │   ├── gestor_memoria.py      # Gestión de memoria
    │   ├── planificador.py        # Núcleo del planificador
    │   └── proceso.py             # Modelo de proceso
    ├── algoritmos/
    │   ├── fifo.py               # Algoritmo FCFS
    │   ├── sjf.py                # Algoritmo SJF
    │   ├── srtf.py               # Algoritmo SRTF
    │   └── round_robin.py        # Algoritmo Round Robin
    ├── interfaz_grafica/
    │   ├── ventana_principal.py  # Ventana principal
    │   ├── panel_control.py      # Panel de control
    │   ├── panel_estado.py       # Panel de estado
    │   ├── panel_ejecucion.py    # Visualización ejecución
    │   └── tabla_eficiencia.py   # Tablas de métricas
    └── main.py                   # Punto de entrada
    │── requirements.txt # Dependencias del proyecto
---

##  Requisitos
- Python **3.10+** (probado en 3.13.3).
- Librerías externas (se instalan desde `requirements.txt`):
  - `customtkinter`

---

##  Instalación y configuración
1. Clonar el repositorio:
   ```bash
   git clone https://github.com/JoshGab05/Proyecto-Simulador-de-procesos-algoritmicos.git
   cd Proyecto-Simulador-de-procesos-algoritmicos

2. Crear y activar entorno virtual:
    ```bash
    py -m venv .venv
    .\.venv\Scripts\activate   # En Windows PowerShell

3. Instalar dependencias:
    ```bash
    pip install -r requirements.txt

## Uso

Ejecuta el archivo principal:

    python main.py

## En la interfaz podrás:

- Seleccionar el algoritmo de planificación.

- Agregar procesos manualmente (nombre, duración, llegada, quantum, RAM).

- Generar procesos aleatorios.

- Iniciar/detener la simulación.

- Visualizar el uso de memoria y la cola de procesos.

## Ejemplo de algoritmos implementados

- FCFS: Atiende los procesos en el orden en que llegan.

- SJF: Atiende primero los procesos con menor duración total.

- SRTF: Atiende primero al proceso con menor tiempo restante (preemptivo).

- Round Robin: Atiende por turnos con un quantum definido.

## ¿CÓMO FUNCIONA EL PROYECTO?

Este simulador replica el comportamiento de un sistema operativo gestionando múltiples procesos usando diferentes algoritmos de planificación. Veremos paso a paso cómo funciona:

## Conoce nuestra interfaz:

<img width="1365" height="718" alt="image" src="https://github.com/user-attachments/assets/0846beab-532f-4291-8c25-07c81fcf5a95" />

## Iniciaremos la prueba con el Algoritmo FCFS (First-Come, First-Served)

 -Al cuál le ingresaremos los siguientes datos:
  -Procesos:
   -A: CPU=5, Llegada=0
   -B: CPU=3, Llegada=1  
   -C: CPU=4, Llegada=2

<img width="227" height="296" alt="image" src="https://github.com/user-attachments/assets/70a01d8c-75c5-4e79-b041-cbfaa9f11bd5" />

<img width="1365" height="715" alt="image" src="https://github.com/user-attachments/assets/0d24a0ca-704a-42f5-be5e-3432d1600c14" />

<img width="696" height="387" alt="image" src="https://github.com/user-attachments/assets/91069817-06c1-428e-960e-dc9d7bc9e6ad" />

## Características
  -No expropiativo: Una vez que empieza, termina.
  -Orden estricto por tiempo de llegada.
  -Simple de implementar.

## SJF (Shortest Job First)

-Procesos:
   -A: CPU=5, Llegada=0
   -B: CPU=3, Llegada=1  
   -C: CPU=1, Llegada=2

<img width="1365" height="718" alt="image" src="https://github.com/user-attachments/assets/ee692ba6-6a49-494c-a7cf-4e9e918a5219" />
<img width="698" height="391" alt="image" src="https://github.com/user-attachments/assets/e897a37c-bf02-4105-b56b-5fc5b5364479" />


## Características
  -No expropiativo: Sólo decide al terminar un proceso.
  -Minimiza el tiempo de espera promedio.
  -Requiere conocer la duración de antemano.

Problema: Inanición (Starvation)
-Si constantemente llegan procesos cortos, un proceso largo puede NUNCA ejecutarse.


## SRTF (Shortest Remaining Time First)

-Procesos:
   -A: CPU=5, Llegada=0
   -B: CPU=3, Llegada=1  
   -C: CPU=1, Llegada=2

<img width="1365" height="715" alt="image" src="https://github.com/user-attachments/assets/7946c627-de58-4225-8f49-a838884d498a" />
<img width="696" height="389" alt="image" src="https://github.com/user-attachments/assets/b8876c4a-e1bb-4d61-b8e6-a7b100e73bc7" />

## Características
  -SÍ es expropiativo: Puede interrumpir en cualquier momento.
  -Optimiza el tiempo de respuesta.
  -Mayor overhead por cambios de contexto.

  Ventaja sobre SJF
  -SRTF puede expropiar cuando llega un proceso más corto, mientras que SJF espera a que termine el actual.


## ROUND ROBIN (RR)

En éste algoritmo, al tener la característica de sistema de tiempo compartido,
tendremos que especificar el Quantum.

-QUANTUM = 2 

-Procesos:
   -A: CPU=5, Llegada=0
   -B: CPU=3, Llegada=1  
   -C: CPU=4, Llegada=2

<img width="1365" height="713" alt="image" src="https://github.com/user-attachments/assets/fe36d9ca-5f6b-4fb8-b109-a4c61cd79798" />
<img width="695" height="387" alt="image" src="https://github.com/user-attachments/assets/26f80fe4-4197-4ffe-ad93-5227e9058cb1" />

## Características
  -SÍ es expropiativo: Por tiempo, no por prioridad
  -Equitativo: Todos los procesos reciben tiempo de CPU
  -Buen tiempo de respuesta

Overhead por cambios frecuentes de contexto


## Autores

Proyecto desarrollado en el curso de Sistemas Operativos.

Universidad Mariano Gálvez – 6to semestre.
