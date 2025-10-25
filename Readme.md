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
- Soporte para múltiples algoritmos de planificación:
  - **FCFS (First Come, First Served)**.
  - **SJF (Shortest Job First)**.
  - **SRTF (Shortest Remaining Time First)**.
  - **Round Robin** (con quantum configurable).
- Gestión de memoria con asignación y liberación dinámica.


---

##  Estructura del proyecto
1. Clonar el repositorio:
   ```bash
    Proyecto-Simulador-de-procesos-algoritmicos/
    │── algoritmos/ # Implementación de los algoritmos de planificación
    │ ├── fcfs.AlgoritmoFIFO.py
    │ ├── sjf.AlgoritmoSJF.py
    │ ├── srtf.AlgoritmoSRTF.py
    │ └── round_robin.py
    │
    │── interfaz_grafica/ # Interfaz gráfica (ventanas y paneles)
    │ ├── panel_control.py
    │ ├── panel_estado.py
    │ └── ventana_principal.py
    │
    │── logica/ # Lógica de simulación y gestión de procesos
    │ ├── gestor_memoria.py
    │ ├── planificador.py
    │ └── proceso.py
    │
    │── main.py # Punto de entrada principal
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

## Autores

Proyecto desarrollado en el curso de Sistemas Operativos.

Universidad Mariano Gálvez – 6to semestre.

