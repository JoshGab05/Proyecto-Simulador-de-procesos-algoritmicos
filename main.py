# main.py

from logica.gestor_memoria import GestorMemoria
from logica.planificador import Planificador
from interfaz_grafica.ventana_principal import VentanaPrincipal

def main():
    gestor = GestorMemoria(capacidad_total=1024)  #Cambio de ram
    planificador = Planificador(gestor)

    app = VentanaPrincipal(gestor, planificador)
    app.mainloop()

if __name__ == "__main__":
    main()
