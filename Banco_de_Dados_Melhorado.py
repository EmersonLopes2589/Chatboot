import hashlib
import tkinter as tk
from tkinter import ttk, messagebox

from sqlalchemy import create_engine, Column, String, Integer, Boolean, ForeignKey, text
from sqlalchemy.orm import sessionmaker, declarative_base

# ─────────────────────────────────────────
#  BANCO DE DADOS
# ─────────────────────────────────────────
db = create_engine("sqlite:///meubanco.db")
Session = sessionmaker(bind=db)
session = Session()
Base = declarative_base()


def hash_senha(senha: str) -> str:
    """Converte a senha em hash SHA-256 antes de salvar."""
    return hashlib.sha256(senha.encode()).hexdigest()


def verificar_senha(senha_digitada: str, hash_salvo: str) -> bool:
    """Compara a senha digitada com o hash salvo no banco."""
    return hash_senha(senha_digitada) == hash_salvo


# ─────────────────────────────────────────
#  MODELOS (TABELAS)
# ─────────────────────────────────────────
class Usuario(Base):
    __tablename__ = "usuarios"

    id    = Column("id",    Integer, primary_key=True, autoincrement=True)
    nome  = Column("nome",  String)
    email = Column("email", String, unique=True)
    senha = Column("senha", String)   # salvo como hash
    ativo = Column("ativo", Boolean)

    def __init__(self, nome, email, senha, ativo=True):
        self.nome  = nome
        self.email = email
        self.senha = hash_senha(senha)   # já salva o hash
        self.ativo = ativo


class Livro(Base):
    __tablename__ = "livros"

    id           = Column("id",           Integer, primary_key=True, autoincrement=True)
    titulo       = Column("titulo",       String)
    qtde_paginas = Column("qtde_paginas", Integer)
    dono         = Column("dono",         ForeignKey("usuarios.id"))

    def __init__(self, titulo, qtde_paginas, dono):
        self.titulo       = titulo
        self.qtde_paginas = qtde_paginas
        self.dono         = dono


Base.metadata.create_all(bind=db)


# ─────────────────────────────────────────
#  FUNÇÕES DE CRUD
# ─────────────────────────────────────────
def cadastrar_usuario(nome, email, senha):
    if session.query(Usuario).filter_by(email=email).first():
        return False, "E-mail já cadastrado."
    u = Usuario(nome=nome, email=email, senha=senha)
    session.add(u)
    session.commit()
    return True, "Usuário cadastrado com sucesso!"


def listar_usuarios():
    return session.query(Usuario).all()


def deletar_usuario(usuario_id):
    u = session.query(Usuario).filter_by(id=usuario_id).first()
    if u:
        session.delete(u)
        session.commit()
        return True
    return False


def cadastrar_livro(titulo, paginas, dono_id):
    l = Livro(titulo=titulo, qtde_paginas=paginas, dono=dono_id)
    session.add(l)
    session.commit()
    return True, "Livro cadastrado com sucesso!"


def listar_livros():
    return session.query(Livro).all()


def deletar_livro(livro_id):
    l = session.query(Livro).filter_by(id=livro_id).first()
    if l:
        session.delete(l)
        session.commit()
        return True
    return False


# ─────────────────────────────────────────
#  INTERFACE GRÁFICA (TKINTER)
# ─────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gerenciador — Usuários & Livros")
        self.geometry("750x540")
        self.resizable(False, False)
        self.configure(bg="#f0f2f5")

        # Abas
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.aba_usuarios = tk.Frame(notebook, bg="#f0f2f5")
        self.aba_livros   = tk.Frame(notebook, bg="#f0f2f5")

        notebook.add(self.aba_usuarios, text="👤  Usuários")
        notebook.add(self.aba_livros,   text="📚  Livros")

        self._build_aba_usuarios()
        self._build_aba_livros()

    # ── ABA USUÁRIOS ──────────────────────
    def _build_aba_usuarios(self):
        frm = self.aba_usuarios

        # Formulário
        form = tk.LabelFrame(frm, text="Cadastrar Usuário", bg="#f0f2f5",
                             font=("Segoe UI", 10, "bold"), padx=10, pady=8)
        form.pack(fill="x", padx=12, pady=(12, 6))

        for i, (lbl, attr) in enumerate([("Nome", "u_nome"), ("E-mail", "u_email"), ("Senha", "u_senha")]):
            tk.Label(form, text=lbl + ":", bg="#f0f2f5",
                     font=("Segoe UI", 9)).grid(row=0, column=i*2, padx=(0,4), sticky="e")
            entry = tk.Entry(form, width=18, font=("Segoe UI", 9),
                             show="*" if lbl == "Senha" else "")
            entry.grid(row=0, column=i*2+1, padx=(0,12))
            setattr(self, attr, entry)

        tk.Button(form, text="Cadastrar", bg="#4a90d9", fg="white",
                  font=("Segoe UI", 9, "bold"), relief="flat", padx=10,
                  command=self._cadastrar_usuario).grid(row=0, column=6, padx=(4,0))

        # Tabela
        cols = ("ID", "Nome", "E-mail", "Ativo")
        self.tree_u = ttk.Treeview(frm, columns=cols, show="headings", height=10)
        for c in cols:
            self.tree_u.heading(c, text=c)
            self.tree_u.column(c, width=150 if c != "ID" else 50, anchor="center")
        self.tree_u.pack(fill="x", padx=12, pady=4)

        tk.Button(frm, text="🗑  Deletar selecionado", bg="#e05c5c", fg="white",
                  font=("Segoe UI", 9), relief="flat", padx=8,
                  command=self._deletar_usuario).pack(pady=(2, 8))

        self._atualizar_tabela_usuarios()

    def _cadastrar_usuario(self):
        ok, msg = cadastrar_usuario(
            self.u_nome.get(), self.u_email.get(), self.u_senha.get()
        )
        messagebox.showinfo("Resultado", msg)
        if ok:
            for e in (self.u_nome, self.u_email, self.u_senha):
                e.delete(0, tk.END)
            self._atualizar_tabela_usuarios()

    def _deletar_usuario(self):
        sel = self.tree_u.selection()
        if not sel:
            messagebox.showwarning("Atenção", "Selecione um usuário.")
            return
        uid = self.tree_u.item(sel[0])["values"][0]
        if messagebox.askyesno("Confirmar", f"Deletar usuário ID {uid}?"):
            deletar_usuario(uid)
            self._atualizar_tabela_usuarios()

    def _atualizar_tabela_usuarios(self):
        self.tree_u.delete(*self.tree_u.get_children())
        for u in listar_usuarios():
            self.tree_u.insert("", "end",
                values=(u.id, u.nome, u.email, "Sim" if u.ativo else "Não"))

    # ── ABA LIVROS ────────────────────────
    def _build_aba_livros(self):
        frm = self.aba_livros

        form = tk.LabelFrame(frm, text="Cadastrar Livro", bg="#f0f2f5",
                             font=("Segoe UI", 10, "bold"), padx=10, pady=8)
        form.pack(fill="x", padx=12, pady=(12, 6))

        for i, (lbl, attr) in enumerate([("Título", "l_titulo"), ("Páginas", "l_paginas"), ("ID do Dono", "l_dono")]):
            tk.Label(form, text=lbl + ":", bg="#f0f2f5",
                     font=("Segoe UI", 9)).grid(row=0, column=i*2, padx=(0,4), sticky="e")
            entry = tk.Entry(form, width=18, font=("Segoe UI", 9))
            entry.grid(row=0, column=i*2+1, padx=(0,12))
            setattr(self, attr, entry)

        tk.Button(form, text="Cadastrar", bg="#4a90d9", fg="white",
                  font=("Segoe UI", 9, "bold"), relief="flat", padx=10,
                  command=self._cadastrar_livro).grid(row=0, column=6, padx=(4,0))

        cols = ("ID", "Título", "Páginas", "Dono (ID)")
        self.tree_l = ttk.Treeview(frm, columns=cols, show="headings", height=10)
        for c in cols:
            self.tree_l.heading(c, text=c)
            self.tree_l.column(c, width=150 if c != "ID" else 50, anchor="center")
        self.tree_l.pack(fill="x", padx=12, pady=4)

        tk.Button(frm, text="🗑  Deletar selecionado", bg="#e05c5c", fg="white",
                  font=("Segoe UI", 9), relief="flat", padx=8,
                  command=self._deletar_livro).pack(pady=(2, 8))

        self._atualizar_tabela_livros()

    def _cadastrar_livro(self):
        try:
            paginas = int(self.l_paginas.get())
            dono_id = int(self.l_dono.get())
        except ValueError:
            messagebox.showerror("Erro", "Páginas e ID do Dono devem ser números inteiros.")
            return
        ok, msg = cadastrar_livro(self.l_titulo.get(), paginas, dono_id)
        messagebox.showinfo("Resultado", msg)
        if ok:
            for e in (self.l_titulo, self.l_paginas, self.l_dono):
                e.delete(0, tk.END)
            self._atualizar_tabela_livros()

    def _deletar_livro(self):
        sel = self.tree_l.selection()
        if not sel:
            messagebox.showwarning("Atenção", "Selecione um livro.")
            return
        lid = self.tree_l.item(sel[0])["values"][0]
        if messagebox.askyesno("Confirmar", f"Deletar livro ID {lid}?"):
            deletar_livro(lid)
            self._atualizar_tabela_livros()

    def _atualizar_tabela_livros(self):
        self.tree_l.delete(*self.tree_l.get_children())
        for l in listar_livros():
            self.tree_l.insert("", "end",
                values=(l.id, l.titulo, l.qtde_paginas, l.dono))


# ─────────────────────────────────────────
#  INICIAR
# ─────────────────────────────────────────
if __name__ == "__main__":
    app = App()
    app.mainloop()
