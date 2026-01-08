import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import os
import re

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Tela de Login")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Inicializar banco de dados
        self.db_file = "users.db"
        self.init_database()
        
        # Container principal que vai conter os frames de login, cadastro e página inicial
        self.container = ttk.Frame(root)
        self.container.pack(fill=tk.BOTH, expand=True)
        
        # Criar frames de login, cadastro e página inicial
        self.login_frame = LoginScreen(self.container, self)
        self.cadastro_frame = CadastroScreen(self.container, self)
        self.pagina_inicial_frame = PaginaInicialScreen(self.container, self)
        
        # Variável para armazenar usuário logado
        self.usuario_logado = None
        
        # Mostrar inicialmente a tela de login
        self.mostrar_login()
        
        # Centralizar janela
        self.center_window()
    
    def center_window(self):
        """Centraliza a janela na tela"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def mostrar_login(self):
        """Mostra a tela de login e esconde as outras"""
        self.root.title("Tela de Login")
        self.root.geometry("400x300")
        self.cadastro_frame.esconder()
        self.pagina_inicial_frame.esconder()
        self.login_frame.mostrar()
        self.usuario_logado = None
        self.center_window()
    
    def mostrar_cadastro(self):
        """Mostra a tela de cadastro e esconde as outras"""
        self.root.title("Cadastro de Usuário")
        self.root.geometry("450x400")
        self.login_frame.esconder()
        self.pagina_inicial_frame.esconder()
        self.cadastro_frame.mostrar()
        self.center_window()
    
    def mostrar_pagina_inicial(self, nome_usuario):
        """Mostra a página inicial e esconde as outras"""
        # Esconder todas as outras telas primeiro
        self.login_frame.esconder()
        self.cadastro_frame.esconder()
        
        # Configurar usuário logado
        self.usuario_logado = nome_usuario
        
        # Atualizar título e tamanho da janela
        self.root.title("Página Inicial")
        self.root.geometry("600x500")
        
        # Mostrar página inicial
        self.pagina_inicial_frame.mostrar()
        
        # Centralizar e atualizar janela
        self.center_window()
        self.root.update_idletasks()
    
    def init_database(self):
        """Inicializa o banco de dados SQLite e cria a tabela se não existir"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Criar tabela de usuários se não existir
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        
        # Criar usuário administrador padrão se não existir
        cursor.execute('SELECT email FROM usuarios WHERE email = ?', ('admin',))
        if cursor.fetchone() is None:
            cursor.execute('''
                INSERT INTO usuarios (nome, email, senha)
                VALUES (?, ?, ?)
            ''', ('Administrador', 'admin', 'admin'))
            conn.commit()
        
        conn.close()
    
    def get_connection(self):
        """Retorna uma conexão com o banco de dados"""
        return sqlite3.connect(self.db_file)
    
    def verificar_usuario(self, email, senha):
        """Verifica se o email e senha correspondem a um usuário"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT nome, email, senha FROM usuarios 
            WHERE email = ? AND senha = ?
        ''', (email, senha))
        
        resultado = cursor.fetchone()
        conn.close()
        
        return resultado
    
    def usuario_existe(self, email):
        """Verifica se um email já está cadastrado"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT email FROM usuarios WHERE email = ?', (email,))
        resultado = cursor.fetchone()
        conn.close()
        
        return resultado is not None
    
    def cadastrar_usuario(self, nome, email, senha):
        """Cadastra um novo usuário no banco de dados"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO usuarios (nome, email, senha)
                VALUES (?, ?, ?)
            ''', (nome, email, senha))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False


class LoginScreen:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        
        # Frame principal que ocupa toda a janela
        self.main_frame = ttk.Frame(parent)
        
        # Frame centralizado que contém todo o conteúdo
        center_frame = ttk.Frame(self.main_frame)
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Título
        title_label = ttk.Label(
            center_frame, 
            text="Sistema de Login", 
            font=("Arial", 18, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 30))
        
        # Frame para campos de entrada
        entry_frame = ttk.Frame(center_frame)
        entry_frame.grid(row=1, column=0, pady=(0, 20))
        
        # Campo de Login (Email)
        login_label = ttk.Label(entry_frame, text="Email:", font=("Arial", 10))
        login_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.login_entry = ttk.Entry(entry_frame, font=("Arial", 11), width=30)
        self.login_entry.grid(row=1, column=0, pady=(0, 15))
        
        # Campo de Senha
        senha_label = ttk.Label(entry_frame, text="Senha:", font=("Arial", 10))
        senha_label.grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        
        self.senha_entry = ttk.Entry(
            entry_frame, 
            font=("Arial", 11), 
            width=30, 
            show="*"
        )
        self.senha_entry.grid(row=3, column=0, pady=(0, 20))
        
        # Bind Enter key
        self.login_entry.bind("<Return>", lambda e: self.senha_entry.focus())
        self.senha_entry.bind("<Return>", lambda e: self.entrar())
        
        # Frame para botões
        button_frame = ttk.Frame(center_frame)
        button_frame.grid(row=2, column=0)
        
        # Botão Entrar
        entrar_btn = ttk.Button(
            button_frame,
            text="Entrar",
            command=self.entrar,
            width=15
        )
        entrar_btn.grid(row=0, column=0, padx=(0, 5), sticky=tk.EW)
        
        # Botão Cadastrar
        cadastrar_btn = ttk.Button(
            button_frame,
            text="Cadastrar",
            command=self.abrir_cadastro,
            width=15
        )
        cadastrar_btn.grid(row=0, column=1, sticky=tk.EW)
        
        # Configurar colunas para expandir igualmente
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
    
    def mostrar(self):
        """Mostra o frame de login"""
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.login_entry.focus()
    
    def esconder(self):
        """Esconde o frame de login"""
        self.main_frame.pack_forget()
    
    def entrar(self):
        """Função do botão Entrar"""
        login = self.login_entry.get().strip()
        senha = self.senha_entry.get()
        
        if not login:
            messagebox.showwarning("Aviso", "Por favor, digite o email!")
            self.login_entry.focus()
            return
        
        if not senha:
            messagebox.showwarning("Aviso", "Por favor, digite a senha!")
            self.senha_entry.focus()
            return
        
        # Verificar credenciais no banco de dados
        resultado = self.app.verificar_usuario(login, senha)
        
        if resultado:
            nome = resultado[0]
            # Limpar campos primeiro
            self.clear_fields()
            # Esconder a tela de login imediatamente
            self.esconder()
            # Abrir página inicial substituindo a tela de login
            self.app.mostrar_pagina_inicial(nome)
            # Atualizar a janela para garantir que a troca seja visível
            self.app.root.update_idletasks()
        else:
            messagebox.showerror("Erro", "Email ou senha incorretos!")
            self.senha_entry.delete(0, tk.END)
            self.senha_entry.focus()
    
    def abrir_cadastro(self):
        """Troca para a tela de cadastro"""
        self.app.mostrar_cadastro()
    
    def clear_fields(self):
        """Limpa os campos de entrada"""
        self.login_entry.delete(0, tk.END)
        self.senha_entry.delete(0, tk.END)
        self.login_entry.focus()


class CadastroScreen:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        
        # Frame principal que ocupa toda a janela
        self.main_frame = ttk.Frame(parent)
        
        # Frame centralizado que contém todo o conteúdo
        center_frame = ttk.Frame(self.main_frame)
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Título
        title_label = ttk.Label(
            center_frame, 
            text="Cadastro de Usuário", 
            font=("Arial", 18, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 30))
        
        # Frame para campos de entrada
        entry_frame = ttk.Frame(center_frame)
        entry_frame.grid(row=1, column=0, pady=(0, 20))
        
        # Campo de Nome
        nome_label = ttk.Label(entry_frame, text="Nome:", font=("Arial", 10))
        nome_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.nome_entry = ttk.Entry(entry_frame, font=("Arial", 11), width=35)
        self.nome_entry.grid(row=1, column=0, pady=(0, 15))
        
        # Campo de Email
        email_label = ttk.Label(entry_frame, text="Email:", font=("Arial", 10))
        email_label.grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        
        self.email_entry = ttk.Entry(entry_frame, font=("Arial", 11), width=35)
        self.email_entry.grid(row=3, column=0, pady=(0, 15))
        
        # Campo de Senha
        senha_label = ttk.Label(entry_frame, text="Senha:", font=("Arial", 10))
        senha_label.grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        
        self.senha_entry = ttk.Entry(
            entry_frame, 
            font=("Arial", 11), 
            width=35, 
            show="*"
        )
        self.senha_entry.grid(row=5, column=0, pady=(0, 20))
        
        # Bind Enter key
        self.nome_entry.bind("<Return>", lambda e: self.email_entry.focus())
        self.email_entry.bind("<Return>", lambda e: self.senha_entry.focus())
        self.senha_entry.bind("<Return>", lambda e: self.cadastrar())
        
        # Frame para botões
        button_frame = ttk.Frame(center_frame)
        button_frame.grid(row=2, column=0)
        
        # Botão Cadastrar
        cadastrar_btn = ttk.Button(
            button_frame,
            text="Cadastrar",
            command=self.cadastrar,
            width=15
        )
        cadastrar_btn.grid(row=0, column=0, padx=(0, 5), sticky=tk.EW)
        
        # Botão Voltar
        voltar_btn = ttk.Button(
            button_frame,
            text="Voltar",
            command=self.voltar,
            width=15
        )
        voltar_btn.grid(row=0, column=1, sticky=tk.EW)
        
        # Configurar colunas para expandir igualmente
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
    
    def mostrar(self):
        """Mostra o frame de cadastro"""
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.clear_fields()
        self.nome_entry.focus()
    
    def esconder(self):
        """Esconde o frame de cadastro"""
        self.main_frame.pack_forget()
    
    def validar_email(self, email):
        """Valida formato de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def cadastrar(self):
        """Função do botão Cadastrar"""
        nome = self.nome_entry.get().strip()
        email = self.email_entry.get().strip()
        senha = self.senha_entry.get()
        
        # Validações
        if not nome:
            messagebox.showwarning("Aviso", "Por favor, digite o nome!")
            self.nome_entry.focus()
            return
        
        if not email:
            messagebox.showwarning("Aviso", "Por favor, digite o email!")
            self.email_entry.focus()
            return
        
        if not self.validar_email(email):
            messagebox.showerror("Erro", "Por favor, digite um email válido!")
            self.email_entry.focus()
            return
        
        if not senha:
            messagebox.showwarning("Aviso", "Por favor, digite a senha!")
            self.senha_entry.focus()
            return
        
        # Verificar se email já está cadastrado
        if self.app.usuario_existe(email):
            messagebox.showerror("Erro", "Este email já está cadastrado!")
            self.email_entry.focus()
            return
        
        # Cadastrar novo usuário no banco de dados
        if self.app.cadastrar_usuario(nome, email, senha):
            messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")
            self.voltar()
        else:
            messagebox.showerror("Erro", "Erro ao cadastrar usuário. Tente novamente.")
    
    def voltar(self):
        """Volta para a tela de login"""
        self.app.mostrar_login()
    
    def clear_fields(self):
        """Limpa os campos de entrada"""
        self.nome_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.senha_entry.delete(0, tk.END)


class PaginaInicialScreen:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        
        # Frame principal que ocupa toda a janela
        self.main_frame = ttk.Frame(parent)
        
        # Frame centralizado que contém todo o conteúdo
        center_frame = ttk.Frame(self.main_frame)
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Título
        self.title_label = ttk.Label(
            center_frame, 
            text="Página Inicial", 
            font=("Arial", 20, "bold")
        )
        self.title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Mensagem de boas-vindas (será atualizada)
        self.welcome_label = ttk.Label(
            center_frame,
            text="Bem-vindo!",
            font=("Arial", 14)
        )
        self.welcome_label.grid(row=1, column=0, pady=(0, 30))
        
        # Botão Sair
        sair_btn = ttk.Button(
            center_frame,
            text="Sair",
            command=self.sair,
            width=20
        )
        sair_btn.grid(row=2, column=0, pady=(20, 0))
    
    def mostrar(self):
        """Mostra o frame da página inicial"""
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        # Atualizar mensagem de boas-vindas com o nome do usuário
        if self.app.usuario_logado:
            self.welcome_label.config(text=f"Bem-vindo, {self.app.usuario_logado}!")
    
    def esconder(self):
        """Esconde o frame da página inicial"""
        self.main_frame.pack_forget()
    
    def sair(self):
        """Encerra o aplicativo"""
        self.app.root.quit()
        self.app.root.destroy()


def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
