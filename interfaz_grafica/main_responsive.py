# main_responsive.py
from logica.gestor_memoria import GestorMemoria
from logica.planificador import Planificador
from interfaz_grafica.ventana_principal import VentanaPrincipal
from interfaz_grafica.ui_responsive import enable_responsive

def main():
    gestor = GestorMemoria(capacidad_total=1024)
    planificador = Planificador(gestor)
    app = VentanaPrincipal(gestor, planificador)

    # <<< hacer la ventana y el layout redimensionables >>>
    enable_responsive(app, width=1200, height=750, minw=980, minh=600,
                      window_scale=0.95, widget_scale=0.95)

    app.mainloop()

if __name__ == "__main__":
    main()
