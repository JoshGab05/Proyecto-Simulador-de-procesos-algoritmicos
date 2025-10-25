# interfaz_grafica/panel_estado.py
from __future__ import annotations
import customtkinter as ctk
from typing import List, Dict, Any, Optional

MONO = ("Consolas", 12)

class PanelEstado(ctk.CTkFrame):
    def __init__(self, master, planificador):
        super().__init__(master)
        self.planificador = planificador

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Caja: Procesos en Memoria ---
        frame_mem = ctk.CTkFrame(self)
        frame_mem.grid(row=0, column=0, sticky="nsew", padx=8, pady=(8, 4))

        lbl1 = ctk.CTkLabel(frame_mem, text="Procesos en Memoria", font=("Segoe UI", 18, "bold"))
        lbl1.pack(anchor="w", padx=10, pady=(8, 4))

        self.txt_mem = ctk.CTkTextbox(frame_mem, height=180, font=MONO)
        self.txt_mem.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.txt_mem.configure(state="disabled")

        # --- Caja: Orden de Finalización ---
        frame_fin = ctk.CTkFrame(self)
        frame_fin.grid(row=1, column=0, sticky="nsew", padx=8, pady=(4, 8))

        lbl2 = ctk.CTkLabel(frame_fin, text="Orden de Finalización de Procesos", font=("Segoe UI", 18, "bold"))
        lbl2.pack(anchor="w", padx=10, pady=(8, 4))

        self.txt_final = ctk.CTkTextbox(frame_fin, height=220, font=MONO)
        self.txt_final.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.txt_final.configure(state="normal")
        self.txt_final.delete("1.0", "end")
        self.txt_final.insert("end", "Aún no hay procesos finalizados...\n")
        self.txt_final.configure(state="disabled")

        # pie de estado pequeño (opcional)
        self.lbl_peq = ctk.CTkLabel(self, text="t=0 | CPU: - | Alg: -", font=("Segoe UI", 12))
        self.lbl_peq.grid(row=2, column=0, sticky="w", padx=12, pady=(0, 6))

        # primera carga
        self.refrescar_tabla()

    # ========== API esperada por VentanaPrincipal ==========

    def refrescar_tabla(self):
        """Repinta la tabla de memoria usando planificador.obtener_procesos()."""
        try:
            procs = self.planificador.obtener_procesos()
        except Exception:
            procs = []

        header = " PID  NOMBRE   ESTADO        LLEGADA  CPU\n" + "-" * 52 + "\n"
        lineas = [header]
        for p in procs:
            pid = getattr(p, "pid", "")
            nom = getattr(p, "nombre", "")
            est = getattr(p, "estado", "")
            leg = getattr(p, "instante_llegada", getattr(p, "llegada", ""))
            cpu = getattr(p, "cpu_total", getattr(p, "cpu", ""))
            lineas.append(f"{pid:>4}  {str(nom)[:10]:<10} {est:<12} {leg:>7}  {cpu:>3}\n")

        texto = "".join(lineas) if len(procs) else "Sin procesos cargados.\n"

        self.txt_mem.configure(state="normal")
        self.txt_mem.delete("1.0", "end")
        self.txt_mem.insert("end", texto)
        self.txt_mem.configure(state="disabled")

    def refrescar_estado_pequeno(self, t: int, pid_en_cpu: Optional[int], alg: str):
        cpu_txt = f"PID {pid_en_cpu}" if pid_en_cpu is not None else "IDLE"
        self.lbl_peq.configure(text=f"t={t} | CPU: {cpu_txt} | Alg: {alg}")

    def mostrar_tabla_eficiencia(self):
        """Abre una ventana con la tabla de métricas."""
        try:
            filas, prom = self.planificador.obtener_metricas()
        except Exception:
            filas, prom = ([], ("", "PROMEDIO", "", "", 0, 0, 0, 0, 0))

        win = ctk.CTkToplevel(self)
        win.title("Tabla de Eficiencia")
        win.geometry("700x360")

        lbl = ctk.CTkLabel(win, text="Tabla de Eficiencia", font=("Segoe UI", 16, "bold"))
        lbl.pack(anchor="w", padx=12, pady=(10, 6))

        txt = ctk.CTkTextbox(win, font=MONO)
        txt.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        header = "PID  Nombre      Llegada  CPU  T. Fin  Retorno  Espera  Respuesta  Eficiencia\n" + "-" * 90 + "\n"
        txt.insert("end", header)
        for (pid, nombre, llegada, cpu, tfin, ret, esp, resp, eff) in filas:
            eff_str = f"{eff:.2f}" if isinstance(eff, (int, float)) and eff is not None else ""
            txt.insert("end", f"{pid:>3}  {str(nombre)[:10]:<10}  {str(llegada):>7}  {str(cpu):>3}  {str(tfin):>5}  {str(ret):>7}  {str(esp):>6}  {str(resp):>9}  {eff_str:>10}\n")

        # Promedios
        _, pnom, _, _, ptfin, pret, pesp, presp, peff = prom
        peff_str = f"{peff:.2f}" if isinstance(peff, (int, float)) else peff
        txt.insert("end", "\n" + "-" * 90 + "\n")
        txt.insert("end", f"     {pnom:<10}              {str(ptfin):>5}  {str(pret):>7}  {str(pesp):>6}  {str(presp):>9}  {peff_str:>10}\n")
        txt.configure(state="disabled")

        btn = ctk.CTkButton(win, text="Cerrar", command=win.destroy)
        btn.pack(pady=(0, 10))

    # ========== NUEVO: orden de finalización ==========

    def mostrar_orden_finalizacion(self, orden: List[Dict[str, Any]]):
        """
        orden: lista de dicts como [{"pid": int, "nombre": str, "t_fin": int}, ...]
        """
        self.txt_final.configure(state="normal")
        self.txt_final.delete("1.0", "end")
        if not orden:
            self.txt_final.insert("end", "Aún no hay procesos finalizados...\n")
        else:
            for i, item in enumerate(orden, start=1):
                pid = item.get("pid")
                nom = item.get("nombre", "")
                tfin = item.get("t_fin")
                self.txt_final.insert("end", f"{i:>2}. {nom} (PID {pid})  t_fin={tfin}\n")
        self.txt_final.configure(state="disabled")
    