import customtkinter as ctk
from tkinter import ttk


class PanelEstado(ctk.CTkFrame):
    """
    Panel que muestra:
      - Procesos en memoria (estado, llegada, CPU)
      - Orden de finalización (lista numerada)
      - Estado general de CPU
    """

    def __init__(self, master, planificador):
        super().__init__(master)
        self.planificador = planificador
        self._after_id = None
        self._resultados_finales = None  # 🔹 nuevo: para vincular resultados_rr

        # =============================
        # TÍTULO PRINCIPAL
        # =============================
        ctk.CTkLabel(
            self,
            text="Estado del Sistema",
            font=("Arial", 22, "bold")
        ).pack(pady=(10, 6))

        # =============================
        # SECCIÓN: TABLA DE PROCESOS
        # =============================
        frame_tabla = ctk.CTkFrame(self)
        frame_tabla.pack(fill="x", padx=10, pady=(0, 8))

        ctk.CTkLabel(
            frame_tabla,
            text="Procesos en Memoria",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=6, pady=(6, 2))

        self.tree = ttk.Treeview(
            frame_tabla,
            columns=("pid", "nombre", "estado", "llegada", "cpu"),
            show="headings",
            height=6
        )

        for col, w in (
            ("pid", 40),
            ("nombre", 100),
            ("estado", 100),
            ("llegada", 80),
            ("cpu", 80)
        ):
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, width=w, stretch=False)
        self.tree.pack(fill="x", padx=6, pady=(0, 6))

        # =============================
        # SECCIÓN: ORDEN DE FINALIZACIÓN
        # =============================
        frame_orden = ctk.CTkFrame(self)
        frame_orden.pack(fill="x", padx=10, pady=(6, 8))

        ctk.CTkLabel(
            frame_orden,
            text="Orden de Finalización de Procesos",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=6, pady=(4, 2))

        self.txt_orden = ctk.CTkTextbox(frame_orden, height=140, width=300, font=("Consolas", 13))
        self.txt_orden.pack(fill="x", padx=6, pady=(2, 6))
        self.txt_orden.insert("1.0", "Aún no hay procesos finalizados...\n")
        self.txt_orden.configure(state="disabled")

        # =============================
        # LABEL: ESTADO GENERAL CPU
        # =============================
        self.status = ctk.CTkLabel(self, text="t=0 | CPU: IDLE | Alg: -")
        self.status.pack(fill="x", padx=10, pady=(6, 6))

        self.refrescar_lista()

    # ==========================================================
    # ACTUALIZACIONES AUTOMÁTICAS
    # ==========================================================
    def cancelar_refrescos(self):
        if self._after_id:
            try:
                self.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

    def programar_refrescos(self):
        """Actualiza la interfaz cada 400 ms (solo tabla y CPU)."""
        self.cancelar_refrescos()

        def tick():
            try:
                self.planificador.simular_tick(1)
                self.refrescar_lista()
            finally:
                self._after_id = self.after(400, tick)

        self._after_id = self.after(400, tick)

    # ==========================================================
    # MÉTODOS DE ACTUALIZACIÓN
    # ==========================================================
    def refrescar_lista(self):
        """Refresca la tabla de procesos."""
        for i in self.tree.get_children():
            self.tree.delete(i)

        procesos = self.planificador.obtener_procesos()
        procesos.sort(key=lambda p: (p.estado == "Finalizado", p.pid))

        for p in procesos:
            self.tree.insert("", "end", values=(
                p.pid, p.nombre, p.estado,
                p.instante_llegada, p.cpu_total
            ))

    def actualizar_estado(self, t, proceso_actual, cola_ready, algoritmo_nombre):
        """Actualiza el estado de CPU dinámicamente."""
        if proceso_actual:
            txt_cpu = f"t={t} | CPU: {proceso_actual.nombre} (PID {proceso_actual.pid}) | Alg: {algoritmo_nombre}"
        else:
            txt_cpu = f"t={t} | CPU: IDLE | Alg: {algoritmo_nombre}"
        self.status.configure(text=txt_cpu)

        self.refrescar_lista()

    # ==========================================================
    # NUEVO: mostrar orden de finalización al terminar
    # ==========================================================
    def mostrar_orden_finalizacion(self, resultados_rr):
        """Muestra el orden de finalización al finalizar Round Robin."""
        self._resultados_finales = resultados_rr

        procesos_finalizados = resultados_rr.get("procesos", [])
        procesos_finalizados.sort(key=lambda p: p.t_fin if p.t_fin is not None else 9999)

        self.txt_orden.configure(state="normal")
        self.txt_orden.delete("1.0", "end")

        if not procesos_finalizados:
            self.txt_orden.insert("1.0", "Aún no hay procesos finalizados...\n")
        else:
            for i, p in enumerate(procesos_finalizados, start=1):
                tfin = getattr(p, "t_fin", "?")
                self.txt_orden.insert("end", f"{i}. {p.nombre} (PID {p.pid}) — t_fin = {tfin}\n")

        self.txt_orden.configure(state="disabled")
