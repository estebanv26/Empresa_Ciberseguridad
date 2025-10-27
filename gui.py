# gui.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from auth import login_user, register_user
from models import crear_incidente, listar_incidentes, agregar_evidencia, asignar_responsable, actualizar_estado
import os
from dotenv import load_dotenv

load_dotenv()
EVIDENCE_PATH = os.getenv("EVIDENCE_PATH", "./storage")
os.makedirs(EVIDENCE_PATH, exist_ok=True)

class App:
    def __init__(self, root):
        self.root = root
        root.title("Sistema de Gestión de Incidentes")
        root.geometry("1000x600")
        self.current_user = None
        self.build_login()

    def build_login(self):
        for w in self.root.winfo_children(): w.destroy()
        frm = ttk.Frame(self.root, padding=20)
        frm.pack(fill="both", expand=True)
        ttk.Label(frm, text="Email:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.email_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.email_var, width=40).grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(frm, text="Password:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.pass_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.pass_var, show="*", width=40).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(frm, text="Login", command=self.handle_login).grid(row=2, column=0, pady=10)
        ttk.Button(frm, text="Register (admin)", command=self.handle_register).grid(row=2, column=1, pady=10)

    def handle_register(self):
        try:
            register_user(self.email_var.get(), self.pass_var.get(), role="admin")
            messagebox.showinfo("OK","Usuario registrado (admin)")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def handle_login(self):
        user = login_user(self.email_var.get(), self.pass_var.get())
        if user:
            self.current_user = user
            self.build_main()
        else:
            messagebox.showerror("Error", "Credenciales inválidas")

    def build_main(self):
        for w in self.root.winfo_children(): w.destroy()
        pan = ttk.Panedwindow(self.root, orient=tk.HORIZONTAL)
        pan.pack(fill="both", expand=True)
        left = ttk.Frame(pan, width=260, padding=10)
        right = ttk.Frame(pan, padding=10)
        pan.add(left, weight=1)
        pan.add(right, weight=4)

        ttk.Label(left, text=f"Usuario: {self.current_user.get('email')}").pack(anchor="w", pady=(0,10))
        ttk.Button(left, text="Crear Incidente", command=self.form_crear_incidente).pack(fill="x", pady=5)
        ttk.Button(left, text="Listar Incidentes", command=self.lista_incidentes).pack(fill="x", pady=5)
        ttk.Button(left, text="Cerrar sesión", command=self.logout).pack(fill="x", pady=15)

        self.right = right
        ttk.Label(right, text="Panel principal").pack(anchor="nw")

    def logout(self):
        self.current_user = None
        self.build_login()

    def form_crear_incidente(self):
        for w in self.right.winfo_children(): w.destroy()
        frame = ttk.Frame(self.right, padding=10)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Crear Incidente", font=("TkDefaultFont", 12, "bold")).pack(anchor="w", pady=(0,10))

        titulo = tk.StringVar()
        descripcion = tk.StringVar()
        tipo = tk.StringVar()
        severity = tk.StringVar()

        ttk.Label(frame, text="Titulo").pack(anchor="w")
        ttk.Entry(frame, textvariable=titulo, width=80).pack(anchor="w", pady=2)
        ttk.Label(frame, text="Descripcion").pack(anchor="w")
        ttk.Entry(frame, textvariable=descripcion, width=80).pack(anchor="w", pady=2)
        ttk.Label(frame, text="Tipo").pack(anchor="w")
        ttk.Entry(frame, textvariable=tipo, width=40).pack(anchor="w", pady=2)
        ttk.Label(frame, text="Severidad").pack(anchor="w")
        ttk.Entry(frame, textvariable=severity, width=20).pack(anchor="w", pady=2)

        def submit():
            if not titulo.get():
                messagebox.showwarning("Validación", "El título es requerido")
                return
            idc = crear_incidente(titulo.get(), descripcion.get(), tipo.get(), severity.get(), self.current_user['email'])
            messagebox.showinfo("OK", f"Incidente creado: {idc}")
            self.lista_incidentes()

        ttk.Button(frame, text="Crear", command=submit).pack(pady=10)

    def lista_incidentes(self):
        for w in self.right.winfo_children(): w.destroy()
        frame = ttk.Frame(self.right, padding=5)
        frame.pack(fill="both", expand=True)
        rows = listar_incidentes()
        cols = ("_id","titulo","tipo","severidad","estado","creador","responsable")
        tree = ttk.Treeview(frame, columns=cols, show="headings")
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=120, anchor="w")
        for r in rows:
            tree.insert("", "end", values=(str(r.get("_id")), r.get("titulo"), r.get("tipo"), r.get("severidad"), r.get("estado"), r.get("creador"), r.get("responsable") or ""))
        tree.pack(fill="both", expand=True)
        btn_fr = ttk.Frame(self.right); btn_fr.pack(fill="x", pady=6)
        ttk.Button(btn_fr, text="Asignar responsable", command=lambda: self.asignar(tree)).pack(side="left", padx=5)
        ttk.Button(btn_fr, text="Agregar evidencia", command=lambda: self.subir_evidencia(tree)).pack(side="left", padx=5)
        ttk.Button(btn_fr, text="Actualizar estado", command=lambda: self.cambiar_estado(tree)).pack(side="left", padx=5)
        ttk.Button(btn_fr, text="Refrescar", command=self.lista_incidentes).pack(side="left", padx=5)

    def selected_item(self, tree):
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un incidente")
            return None
        vals = tree.item(sel[0])["values"]
        return vals[0]

    def asignar(self, tree):
        incidente_id = self.selected_item(tree)
        if not incidente_id: return
        email = simpledialog.askstring("Responsable", "Email del responsable:")
        if email:
            asignar_responsable(incidente_id, email, self.current_user['email'])
            messagebox.showinfo("OK", "Responsable asignado")
            self.lista_incidentes()

    def cambiar_estado(self, tree):
        incidente_id = self.selected_item(tree)
        if not incidente_id: return
        estado = simpledialog.askstring("Estado", "Nuevo estado:")
        if estado:
            actualizar_estado(incidente_id, estado, self.current_user['email'])
            messagebox.showinfo("OK", "Estado actualizado")
            self.lista_incidentes()

    def subir_evidencia(self, tree):
        incidente_id = self.selected_item(tree)
        if not incidente_id: return
        filepath = filedialog.askopenfilename()
        if not filepath: return
        fname = os.path.basename(filepath)
        dest = os.path.join(EVIDENCE_PATH, f"{incidente_id}_{fname}")
        with open(filepath, "rb") as fr, open(dest, "wb") as fw:
            fw.write(fr.read())
        agregar_evidencia(incidente_id, dest, self.current_user['email'])
        messagebox.showinfo("OK", "Evidencia subida")
