# interfaz_grafica/panel_estado.py
import customtkinter as ctk
from tkinter import ttk

class PanelEstado(ctk.CTkFrame):
    def __init__(self, master, gestor_memoria, planificador):
        super().__init__(master)
        self.gestor_memoria = gestor_memoria
        self.planificador = planificador
        self._after_id = None

        # Título
        ctk.CTkLabel(self, text="Estado del Sistema", font=("Arial", 22)).pack(pady=(10, 6))

        # Memoria
        memf = ctk.CTkFrame(self); memf.pack(fill="x", padx=12, pady=(0,8))
        self.mem_label = ctk.CTkLabel(memf, text="Memoria usada: 0 / 0 (0%)")
        self.mem_label.pack(anchor="w", padx=6, pady=6)
        self.mem_bar = ctk.CTkProgressBar(memf); self.mem_bar.set(0.0); self.mem_bar.pack(fill="x", padx=6, pady=(0,6))

        # Tabla de procesos
        tf = ctk.CTkFrame(self); tf.pack(fill="both", expand=True, padx=12, pady=(0,8))
        ctk.CTkLabel(tf, text="Procesos").pack(anchor="w", padx=6, pady=(6,2))
        self.tree = ttk.Treeview(tf, columns=("pid","nombre","estado","llegada","cpu","resta","ram"), show="headings", height=9)
        for col, w in (("pid",60),("nombre",140),("estado",110),("llegada",70),("cpu",70),("resta",70),("ram",70)):
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, width=w, stretch=False)
        self.tree.pack(fill="x", padx=6, pady=(0,6))

        # Historial
        hf = ctk.CTkFrame(self); hf.pack(fill="both", expand=True, padx=12, pady=(0,8))
        ctk.CTkLabel(hf, text="Historial").pack(anchor="w", padx=6, pady=(6,2))
        self.his = ttk.Treeview(hf, columns=("t","tipo","pid","nombre","alg","restante"), show="headings", height=8)
        for col, w in (("t",60),("tipo",90),("pid",60),("nombre",140),("alg",70),("restante",80)):
            self.his.heading(col, text=col.upper())
            self.his.column(col, width=w, stretch=False)
        self.his.pack(fill="both", expand=True, padx=6, pady=(0,6))

        # Pie
        self.status = ctk.CTkLabel(self, text="t=0 | CPU: IDLE")
        self.status.pack(fill="x", padx=12, pady=(0,8))

        # Primer refresco
        self.refrescar_lista()

    def cancelar_refrescos(self):
        if self._after_id is not None:
            try:
                self.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

    def programar_refrescos(self):
        self.cancelar_refrescos()
        # refresco simple cada 400ms
        def tick():
            try:
                self.planificador.simular_tick(1)
                self.refrescar_lista()
            finally:
                self._after_id = self.after(400, tick)
        self._after_id = self.after(400, tick)

    def refrescar_lista(self):
        # Memoria
        usada = self.gestor_memoria.obtener_memoria_usada()
        total = self.gestor_memoria.capacidad_total
        pct = 0.0 if total <= 0 else usada/total
        self.mem_label.configure(text=f"Memoria usada: {usada} MB / {total} MB ({pct*100:.1f}%)")
        self.mem_bar.set(min(1.0, max(0.0, pct)))

        # Procesos
        for i in self.tree.get_children():
            self.tree.delete(i)
        for p in self.planificador.obtener_procesos():
            self.tree.insert("", "end", values=(p.pid, p.nombre, p.estado, p.instante_llegada, p.cpu_total, p.cpu_restante, p.memoria_requerida))

        # Historial (últimos 30 eventos)
        for i in self.his.get_children():
            self.his.delete(i)
        for e in self.planificador.historial[-30:]:
            self.his.insert("", "end", values=(e.get("t"), e.get("tipo"), e.get("pid"), e.get("nombre"), e.get("alg","-"), e.get("restante","-")))

        # Status
        st = self.planificador.estado_cpu()
        run = st.get("running")
        if run:
            txt = f"t={st.get('t')} | CPU: {run['nombre']} (PID {run['pid']}) | Alg: {st.get('alg')}"
        else:
            txt = f"t={st.get('t')} | CPU: IDLE | Alg: {st.get('alg')}"
        self.status.configure(text=txt)