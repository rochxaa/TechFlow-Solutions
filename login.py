import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import os
import re
from datetime import datetime

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
        
        # Variáveis para armazenar informações do usuário logado
        self.usuario_logado = None
        self.email_logado = None
        
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
        self.email_logado = None
        self.center_window()
    
    def mostrar_cadastro(self):
        """Mostra a tela de cadastro e esconde as outras"""
        self.root.title("Cadastro de Usuário")
        self.root.geometry("450x400")
        self.login_frame.esconder()
        self.pagina_inicial_frame.esconder()
        self.cadastro_frame.mostrar()
        self.center_window()
    
    def mostrar_pagina_inicial(self, nome_usuario, email_usuario):
        """Mostra a página inicial e esconde as outras"""
        # Esconder todas as outras telas primeiro
        self.login_frame.esconder()
        self.cadastro_frame.esconder()
        
        # Configurar usuário logado
        self.usuario_logado = nome_usuario
        self.email_logado = email_usuario
        
        # Atualizar título e tamanho da janela
        if email_usuario == "admin":
            self.root.title("Página Inicial - Admin")
            self.root.geometry("1200x800")
        else:
            self.root.title("Quadro Kanban")
            self.root.geometry("1000x700")
        
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
        
        # Criar tabela de tarefas se não existir
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tarefas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_email TEXT NOT NULL,
                titulo TEXT NOT NULL,
                descricao TEXT,
                status TEXT NOT NULL,
                prioridade INTEGER DEFAULT 0,
                data_criacao TEXT NOT NULL,
                FOREIGN KEY (usuario_email) REFERENCES usuarios(email)
            )
        ''')
        
        # Migração: adicionar colunas se não existirem
        cursor.execute("PRAGMA table_info(tarefas)")
        colunas_existentes = [col[1] for col in cursor.fetchall()]
        
        if 'prioridade' not in colunas_existentes:
            cursor.execute('ALTER TABLE tarefas ADD COLUMN prioridade INTEGER DEFAULT 0')
        
        if 'data_criacao' not in colunas_existentes:
            data_default = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(f'ALTER TABLE tarefas ADD COLUMN data_criacao TEXT DEFAULT "{data_default}"')
            # Atualizar tarefas existentes com data atual
            cursor.execute('UPDATE tarefas SET data_criacao = ? WHERE data_criacao IS NULL OR data_criacao = ""',
                         (data_default,))
        
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
    
    def listar_usuarios(self):
        """Lista todos os usuários cadastrados"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, nome, email FROM usuarios ORDER BY nome')
        usuarios = cursor.fetchall()
        conn.close()
        
        return usuarios
    
    def excluir_usuario(self, email):
        """Exclui um usuário do banco de dados"""
        # Não permitir excluir o próprio admin
        if email == "admin":
            return False, "Não é possível excluir o usuário administrador!"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Excluir tarefas do usuário primeiro
            cursor.execute('DELETE FROM tarefas WHERE usuario_email = ?', (email,))
            # Excluir o usuário
            cursor.execute('DELETE FROM usuarios WHERE email = ?', (email,))
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                return True, "Usuário excluído com sucesso!"
            else:
                conn.close()
                return False, "Usuário não encontrado!"
        except Exception as e:
            conn.close()
            return False, f"Erro ao excluir usuário: {str(e)}"
    
    def listar_tarefas(self, usuario_email=None):
        """Lista todas as tarefas de um usuário (ou de todos se usuario_email for None)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if usuario_email:
            cursor.execute('''
                SELECT id, titulo, descricao, status, prioridade, data_criacao FROM tarefas 
                WHERE usuario_email = ? 
                ORDER BY prioridade DESC, id DESC
            ''', (usuario_email,))
        else:
            # Se None, retorna todas as tarefas (para admin)
            cursor.execute('''
                SELECT id, titulo, descricao, status, prioridade, data_criacao, usuario_email 
                FROM tarefas 
                ORDER BY prioridade DESC, id DESC
            ''')
        
        tarefas = cursor.fetchall()
        conn.close()
        
        return tarefas
    
    def adicionar_tarefa(self, usuario_email, titulo, descricao, status="A Fazer", prioridade=0):
        """Adiciona uma nova tarefa"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            data_criacao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                INSERT INTO tarefas (usuario_email, titulo, descricao, status, prioridade, data_criacao)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (usuario_email, titulo, descricao, status, prioridade, data_criacao))
            
            conn.commit()
            tarefa_id = cursor.lastrowid
            conn.close()
            return True, tarefa_id
        except Exception as e:
            conn.close()
            return False, str(e)
    
    def atualizar_prioridade_tarefa(self, tarefa_id, prioridade):
        """Atualiza a prioridade de uma tarefa"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('UPDATE tarefas SET prioridade = ? WHERE id = ?', (prioridade, tarefa_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            return False
    
    def verificar_propriedade_tarefa(self, tarefa_id, usuario_email):
        """Verifica se uma tarefa pertence a um usuário"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT usuario_email FROM tarefas WHERE id = ?', (tarefa_id,))
        resultado = cursor.fetchone()
        conn.close()
        
        if resultado and resultado[0] == usuario_email:
            return True
        return False
    
    def atualizar_status_tarefa(self, tarefa_id, novo_status, usuario_email=None):
        """Atualiza o status de uma tarefa (apenas se pertencer ao usuário ou for admin)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Admin pode modificar qualquer tarefa
            # Usuários normais só podem modificar suas próprias tarefas
            if usuario_email and usuario_email != "admin":
                if not self.verificar_propriedade_tarefa(tarefa_id, usuario_email):
                    conn.close()
                    return False, "Você não tem permissão para modificar esta tarefa!"
            
            cursor.execute('UPDATE tarefas SET status = ? WHERE id = ?', (novo_status, tarefa_id))
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                return True, "Tarefa atualizada com sucesso!"
            else:
                conn.close()
                return False, "Tarefa não encontrada!"
        except Exception as e:
            conn.close()
            return False, f"Erro ao atualizar tarefa: {str(e)}"
    
    def excluir_tarefa(self, tarefa_id, usuario_email=None):
        """Exclui uma tarefa (apenas se pertencer ao usuário ou for admin)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Admin pode excluir qualquer tarefa
            # Usuários normais só podem excluir suas próprias tarefas
            if usuario_email and usuario_email != "admin":
                if not self.verificar_propriedade_tarefa(tarefa_id, usuario_email):
                    conn.close()
                    return False, "Você não tem permissão para excluir esta tarefa!"
            
            cursor.execute('DELETE FROM tarefas WHERE id = ?', (tarefa_id,))
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                return True, "Tarefa excluída com sucesso!"
            else:
                conn.close()
                return False, "Tarefa não encontrada!"
        except Exception as e:
            conn.close()
            return False, f"Erro ao excluir tarefa: {str(e)}"


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
            email = resultado[1]
            # Limpar campos primeiro
            self.clear_fields()
            # Esconder a tela de login imediatamente
            self.esconder()
            # Abrir página inicial substituindo a tela de login
            self.app.mostrar_pagina_inicial(nome, email)
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
        
        # Frame superior para conteúdo geral
        top_frame = ttk.Frame(self.main_frame)
        top_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Mensagem de boas-vindas
        self.welcome_label = ttk.Label(
            top_frame,
            text="Bem-vindo!",
            font=("Arial", 16, "bold")
        )
        self.welcome_label.pack(pady=(0, 20))
        
        # Frame para seção de usuários (apenas admin)
        self.usuarios_frame = ttk.LabelFrame(
            top_frame, 
            text="Gerenciamento de Usuários", 
            padding=10
        )
        
        # Botões de ação (Cadastrar e Atualizar)
        buttons_frame = ttk.Frame(self.usuarios_frame)
        buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        cadastrar_btn = ttk.Button(
            buttons_frame,
            text="Cadastrar Novo Usuário",
            command=self.cadastrar_usuario,
            width=25
        )
        cadastrar_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        atualizar_btn = ttk.Button(
            buttons_frame,
            text="Atualizar Lista",
            command=self.atualizar_lista,
            width=20
        )
        atualizar_btn.pack(side=tk.LEFT)
        
        # Treeview para listar usuários
        tree_frame = ttk.Frame(self.usuarios_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("ID", "Nome", "Email"),
            show="headings",
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set,
            height=10
        )
        
        # Configurar colunas
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Email", text="Email")
        
        self.tree.column("ID", width=50, anchor=tk.CENTER)
        self.tree.column("Nome", width=200)
        self.tree.column("Email", width=250)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.config(command=self.tree.yview)
        h_scrollbar.config(command=self.tree.xview)
        
        # Variável para armazenar o usuário selecionado no Kanban (admin)
        self.usuario_kanban_selecionado = None
        
        # Evento de seleção: quando admin clica em um usuário, mostrar seu Kanban
        self.tree.bind("<<TreeviewSelect>>", self.on_usuario_selected)
        
        # Botão Excluir
        excluir_btn = ttk.Button(
            self.usuarios_frame,
            text="Excluir Usuário Selecionado",
            command=self.excluir_usuario,
            width=30
        )
        excluir_btn.pack(pady=(10, 0))
        
        # Frame inferior para botão Sair
        bottom_frame = ttk.Frame(self.main_frame)
        bottom_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Frame para quadro Kanban (todos os usuários, admin vê todos)
        self.kanban_frame = ttk.LabelFrame(
            top_frame,
            text="Quadro Kanban",
            padding=10
        )
        
        # Label para mostrar de quem é o Kanban (será atualizado dinamicamente)
        self.kanban_label_titulo = ttk.Label(
            self.kanban_frame,
            text="Quadro Kanban",
            font=("Arial", 11, "bold")
        )
        
        # Frame para seletor de usuário (apenas admin - será mostrado dinamicamente)
        self.usuario_kanban_frame = ttk.Frame(self.kanban_frame)
        
        info_label = ttk.Label(
            self.usuario_kanban_frame, 
            text="Selecione um usuário na lista acima para visualizar seu Kanban", 
            font=("Arial", 9),
            foreground="gray"
        )
        info_label.pack(side=tk.LEFT)
        
        # Botões do Kanban
        kanban_buttons_frame = ttk.Frame(self.kanban_frame)
        kanban_buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        nova_tarefa_btn = ttk.Button(
            kanban_buttons_frame,
            text="Nova Tarefa",
            command=self.nova_tarefa,
            width=20
        )
        nova_tarefa_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        atualizar_kanban_btn = ttk.Button(
            kanban_buttons_frame,
            text="Atualizar",
            command=lambda: self.carregar_kanban_admin() if self.app.email_logado == "admin" else self.carregar_kanban(),
            width=15
        )
        atualizar_kanban_btn.pack(side=tk.LEFT)
        
        # Frame para colunas do Kanban
        kanban_columns_frame = ttk.Frame(self.kanban_frame)
        kanban_columns_frame.pack(fill=tk.BOTH, expand=True)
        
        # Colunas do Kanban
        self.colunas_kanban = {
            "A Fazer": [],
            "Em Progresso": [],
            "Concluído": []
        }
        
        # Criar colunas
        self.kanban_widgets = {}
        for i, coluna in enumerate(["A Fazer", "Em Progresso", "Concluído"]):
            # Frame da coluna
            col_frame = ttk.LabelFrame(
                kanban_columns_frame,
                text=coluna,
                padding=5
            )
            col_frame.grid(row=0, column=i, padx=5, sticky=tk.NSEW, pady=5)
            kanban_columns_frame.columnconfigure(i, weight=1)
            
            # Listbox para tarefas da coluna
            listbox = tk.Listbox(
                col_frame,
                height=15,
                font=("Arial", 10),
                selectmode=tk.SINGLE
            )
            listbox.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
            
            # Frame para botões da coluna
            col_buttons = ttk.Frame(col_frame)
            col_buttons.pack(fill=tk.X, pady=(5, 0))
            
            if coluna == "A Fazer":
                mover_btn = ttk.Button(
                    col_buttons,
                    text="▶ Em Progresso",
                    command=lambda: self.mover_tarefa("A Fazer", "Em Progresso")
                )
                mover_btn.pack(side=tk.LEFT, padx=2)
            elif coluna == "Em Progresso":
                mover_esq_btn = ttk.Button(
                    col_buttons,
                    text="◀ A Fazer",
                    command=lambda: self.mover_tarefa("Em Progresso", "A Fazer")
                )
                mover_esq_btn.pack(side=tk.LEFT, padx=2)
                mover_dir_btn = ttk.Button(
                    col_buttons,
                    text="▶ Concluído",
                    command=lambda: self.mover_tarefa("Em Progresso", "Concluído")
                )
                mover_dir_btn.pack(side=tk.LEFT, padx=2)
            elif coluna == "Concluído":
                mover_btn = ttk.Button(
                    col_buttons,
                    text="◀ Em Progresso",
                    command=lambda: self.mover_tarefa("Concluído", "Em Progresso")
                )
                mover_btn.pack(side=tk.LEFT, padx=2)
            
            excluir_btn = ttk.Button(
                col_buttons,
                text="Excluir",
                command=lambda c=coluna: self.excluir_tarefa_kanban(c)
            )
            excluir_btn.pack(side=tk.LEFT, padx=2)
            
            self.kanban_widgets[coluna] = {
                "frame": col_frame,
                "listbox": listbox
            }
        
        # Botão Sair
        sair_btn = ttk.Button(
            bottom_frame,
            text="Sair",
            command=self.sair,
            width=20
        )
        sair_btn.pack(side=tk.RIGHT)
    
    def mostrar(self):
        """Mostra o frame da página inicial"""
        # Empacotar o frame principal
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Atualizar mensagem de boas-vindas com o nome do usuário
        if self.app.usuario_logado:
            self.welcome_label.config(text=f"Bem-vindo, {self.app.usuario_logado}!")
        
        # Se for admin, mostrar seção de gerenciamento de usuários e Kanban
        if self.app.email_logado == "admin":
            self.usuarios_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
            self.kanban_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
            self.kanban_label_titulo.pack(pady=(0, 5))
            self.usuario_kanban_frame.pack(fill=tk.X, pady=(0, 10))
            self.atualizar_lista()
            self.usuario_kanban_selecionado = None
            # Limpar Kanban inicialmente (mostrará apenas quando selecionar um usuário)
            self.carregar_kanban_admin()
        else:
            # Se não for admin, mostrar apenas quadro Kanban
            self.usuarios_frame.pack_forget()
            self.usuario_kanban_frame.pack_forget()
            self.kanban_label_titulo.pack_forget()
            self.kanban_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
            self.carregar_kanban()
    
    def esconder(self):
        """Esconde o frame da página inicial"""
        self.main_frame.pack_forget()
    
    def atualizar_lista(self):
        """Atualiza a lista de usuários"""
        # Limpar itens existentes
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Buscar usuários do banco de dados
        usuarios = self.app.listar_usuarios()
        
        # Adicionar usuários à lista
        for usuario in usuarios:
            self.tree.insert("", tk.END, values=usuario)
    
    def on_usuario_selected(self, event):
        """Evento disparado quando o admin seleciona um usuário na lista"""
        if self.app.email_logado != "admin":
            return
        
        selecionado = self.tree.selection()
        if not selecionado:
            return
        
        # Obter dados do usuário selecionado
        item = self.tree.item(selecionado[0])
        valores = item['values']
        email = valores[2]
        nome = valores[1]
        
        # Armazenar usuário selecionado e carregar seu Kanban
        self.usuario_kanban_selecionado = email
        self.kanban_label_titulo.config(text=f"Quadro Kanban - {nome} ({email})")
        self.carregar_kanban_admin()
    
    def excluir_usuario(self):
        """Exclui o usuário selecionado"""
        selecionado = self.tree.selection()
        
        if not selecionado:
            messagebox.showwarning("Aviso", "Por favor, selecione um usuário para excluir!")
            return
        
        # Obter dados do usuário selecionado
        item = self.tree.item(selecionado[0])
        valores = item['values']
        email = valores[2]
        nome = valores[1]
        
        # Confirmar exclusão
        resposta = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Deseja realmente excluir o usuário {nome} ({email})?"
        )
        
        if resposta:
            sucesso, mensagem = self.app.excluir_usuario(email)
            if sucesso:
                messagebox.showinfo("Sucesso", mensagem)
                # Se o usuário excluído estava selecionado no Kanban, limpar seleção
                if self.usuario_kanban_selecionado == email:
                    self.usuario_kanban_selecionado = None
                    self.kanban_label_titulo.config(text="Quadro Kanban - Selecione um usuário para visualizar")
                self.atualizar_lista()
                self.carregar_kanban_admin()
            else:
                messagebox.showerror("Erro", mensagem)
    
    def cadastrar_usuario(self):
        """Abre a tela de cadastro de usuário"""
        # Criar janela de cadastro
        cadastro_window = tk.Toplevel(self.app.root)
        cadastro_window.title("Cadastrar Novo Usuário")
        cadastro_window.geometry("450x400")
        cadastro_window.resizable(False, False)
        cadastro_window.transient(self.app.root)
        cadastro_window.grab_set()
        
        # Centralizar janela
        cadastro_window.update_idletasks()
        width = cadastro_window.winfo_width()
        height = cadastro_window.winfo_height()
        x = (cadastro_window.winfo_screenwidth() // 2) - (width // 2)
        y = (cadastro_window.winfo_screenheight() // 2) - (height // 2)
        cadastro_window.geometry(f'{width}x{height}+{x}+{y}')
        
        # Frame principal
        main_frame = ttk.Frame(cadastro_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame centralizado
        center_frame = ttk.Frame(main_frame)
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Título
        title_label = ttk.Label(
            center_frame,
            text="Cadastrar Novo Usuário",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 25))
        
        # Campos de entrada
        entry_frame = ttk.Frame(center_frame)
        entry_frame.grid(row=1, column=0, pady=(0, 20))
        
        # Nome
        nome_label = ttk.Label(entry_frame, text="Nome:", font=("Arial", 10))
        nome_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        nome_entry = ttk.Entry(entry_frame, font=("Arial", 11), width=35)
        nome_entry.grid(row=1, column=0, pady=(0, 15))
        nome_entry.focus()
        
        # Email
        email_label = ttk.Label(entry_frame, text="Email:", font=("Arial", 10))
        email_label.grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        email_entry = ttk.Entry(entry_frame, font=("Arial", 11), width=35)
        email_entry.grid(row=3, column=0, pady=(0, 15))
        
        # Senha
        senha_label = ttk.Label(entry_frame, text="Senha:", font=("Arial", 10))
        senha_label.grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        senha_entry = ttk.Entry(entry_frame, font=("Arial", 11), width=35, show="*")
        senha_entry.grid(row=5, column=0, pady=(0, 20))
        
        def validar_email(email):
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return re.match(pattern, email) is not None
        
        def salvar():
            nome = nome_entry.get().strip()
            email = email_entry.get().strip()
            senha = senha_entry.get()
            
            if not nome:
                messagebox.showwarning("Aviso", "Por favor, digite o nome!")
                nome_entry.focus()
                return
            
            if not email:
                messagebox.showwarning("Aviso", "Por favor, digite o email!")
                email_entry.focus()
                return
            
            if not validar_email(email):
                messagebox.showerror("Erro", "Por favor, digite um email válido!")
                email_entry.focus()
                return
            
            if not senha:
                messagebox.showwarning("Aviso", "Por favor, digite a senha!")
                senha_entry.focus()
                return
            
            if self.app.usuario_existe(email):
                messagebox.showerror("Erro", "Este email já está cadastrado!")
                email_entry.focus()
                return
            
            if self.app.cadastrar_usuario(nome, email, senha):
                messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")
                cadastro_window.destroy()
                self.atualizar_lista()
            else:
                messagebox.showerror("Erro", "Erro ao cadastrar usuário. Tente novamente.")
        
        # Botões
        buttons_frame = ttk.Frame(center_frame)
        buttons_frame.grid(row=2, column=0)
        
        salvar_btn = ttk.Button(buttons_frame, text="Salvar", command=salvar, width=15)
        salvar_btn.grid(row=0, column=0, padx=(0, 10))
        
        cancelar_btn = ttk.Button(
            buttons_frame, 
            text="Cancelar", 
            command=cadastro_window.destroy, 
            width=15
        )
        cancelar_btn.grid(row=0, column=1)
        
        # Bind Enter
        nome_entry.bind("<Return>", lambda e: email_entry.focus())
        email_entry.bind("<Return>", lambda e: senha_entry.focus())
        senha_entry.bind("<Return>", lambda e: salvar())
    
    def carregar_kanban(self):
        """Carrega as tarefas do usuário logado no Kanban"""
        # Limpar todas as listboxes
        for coluna in self.kanban_widgets:
            self.kanban_widgets[coluna]["listbox"].delete(0, tk.END)
        
        # Verificar se há usuário logado
        if not self.app.email_logado:
            return
        
        # Buscar apenas as tarefas do usuário logado
        tarefas = self.app.listar_tarefas(self.app.email_logado)
        
        # Organizar tarefas por coluna
        self.colunas_kanban = {
            "A Fazer": [],
            "Em Progresso": [],
            "Concluído": []
        }
        
        for tarefa in tarefas:
            tarefa_id, titulo, descricao, status, prioridade, data_criacao = tarefa[:6]
            # Garantir que o status existe
            if status not in self.colunas_kanban:
                status = "A Fazer"
            prioridade = prioridade if prioridade else 0
            self.colunas_kanban[status].append((tarefa_id, titulo, descricao, prioridade, data_criacao))
        
        # Adicionar tarefas nas listboxes
        for coluna, tarefas_lista in self.colunas_kanban.items():
            for tarefa_id, titulo, descricao, prioridade, data_criacao in tarefas_lista:
                # Formatar data
                try:
                    data_obj = datetime.strptime(data_criacao, '%Y-%m-%d %H:%M:%S')
                    data_formatada = data_obj.strftime('%d/%m/%Y')
                except:
                    data_formatada = data_criacao
                
                display_text = f"[{tarefa_id}] {titulo}"
                if prioridade == 1:
                    display_text = f"🔴 {display_text}"
                display_text += f"\n📅 {data_formatada}"
                if descricao:
                    display_text += f"\n  {descricao[:25]}..."
                
                self.kanban_widgets[coluna]["listbox"].insert(tk.END, display_text)
                # Destacar tarefas prioritárias em vermelho
                index = self.kanban_widgets[coluna]["listbox"].size() - 1
                if prioridade == 1:
                    self.kanban_widgets[coluna]["listbox"].itemconfig(index, {'bg': '#ffcccc', 'fg': '#cc0000'})
                else:
                    self.kanban_widgets[coluna]["listbox"].itemconfig(index, {'bg': '#f0f0f0'})
    
    def carregar_kanban_admin(self):
        """Carrega as tarefas no Kanban para o admin (pode ver todos os usuários)"""
        # Limpar todas as listboxes
        for coluna in self.kanban_widgets:
            self.kanban_widgets[coluna]["listbox"].delete(0, tk.END)
        
        # Se não houver usuário selecionado, não mostrar tarefas
        if not self.usuario_kanban_selecionado:
            self.kanban_label_titulo.config(text="Quadro Kanban - Selecione um usuário para visualizar")
            return
        
        # Buscar tarefas do usuário selecionado
        tarefas = self.app.listar_tarefas(self.usuario_kanban_selecionado)
        
        # Organizar tarefas por coluna
        self.colunas_kanban = {
            "A Fazer": [],
            "Em Progresso": [],
            "Concluído": []
        }
        
        for tarefa in tarefas:
            tarefa_id, titulo, descricao, status, prioridade, data_criacao = tarefa[:6]
            
            # Garantir que o status existe
            if status not in self.colunas_kanban:
                status = "A Fazer"
            prioridade = prioridade if prioridade else 0
            self.colunas_kanban[status].append((tarefa_id, titulo, descricao, prioridade, data_criacao))
        
        # Adicionar tarefas nas listboxes
        for coluna, tarefas_lista in self.colunas_kanban.items():
            for tarefa_id, titulo, descricao, prioridade, data_criacao in tarefas_lista:
                # Formatar data
                try:
                    data_obj = datetime.strptime(data_criacao, '%Y-%m-%d %H:%M:%S')
                    data_formatada = data_obj.strftime('%d/%m/%Y')
                except:
                    data_formatada = data_criacao
                
                display_text = f"[{tarefa_id}] {titulo}"
                if prioridade == 1:
                    display_text = f"🔴 {display_text}"
                display_text += f"\n📅 {data_formatada}"
                if descricao:
                    display_text += f"\n  {descricao[:25]}..."
                
                self.kanban_widgets[coluna]["listbox"].insert(tk.END, display_text)
                # Destacar tarefas prioritárias em vermelho
                index = self.kanban_widgets[coluna]["listbox"].size() - 1
                if prioridade == 1:
                    self.kanban_widgets[coluna]["listbox"].itemconfig(index, {'bg': '#ffcccc', 'fg': '#cc0000'})
                else:
                    self.kanban_widgets[coluna]["listbox"].itemconfig(index, {'bg': '#f0f0f0'})
    
    def nova_tarefa(self):
        """Abre janela para adicionar nova tarefa"""
        # Se for admin, verificar se há usuário selecionado
        if self.app.email_logado == "admin" and not self.usuario_kanban_selecionado:
            messagebox.showwarning("Aviso", "Por favor, selecione um usuário na lista para criar uma tarefa!")
            return
        
        janela = tk.Toplevel(self.app.root)
        janela.title("Nova Tarefa")
        janela.geometry("450x400")
        janela.resizable(False, False)
        janela.transient(self.app.root)
        janela.grab_set()
        
        # Centralizar
        janela.update_idletasks()
        width = janela.winfo_width()
        height = janela.winfo_height()
        x = (janela.winfo_screenwidth() // 2) - (width // 2)
        y = (janela.winfo_screenheight() // 2) - (height // 2)
        janela.geometry(f'{width}x{height}+{x}+{y}')
        
        # Frame principal
        main_frame = ttk.Frame(janela, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame para conteúdo (evita que expanda demais)
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título - mostrar para qual usuário será criada a tarefa (se admin)
        titulo_texto = "Nova Tarefa"
        if self.app.email_logado == "admin" and self.usuario_kanban_selecionado:
            usuarios = self.app.listar_usuarios()
            nome_usuario = self.usuario_kanban_selecionado
            for u in usuarios:
                if u[2] == self.usuario_kanban_selecionado:
                    nome_usuario = u[1]
                    break
            titulo_texto = f"Nova Tarefa - {nome_usuario}"
        
        ttk.Label(content_frame, text=titulo_texto, font=("Arial", 14, "bold")).pack(pady=(0, 15))
        
        # Frame para campos
        fields_frame = ttk.Frame(content_frame)
        fields_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título da tarefa
        ttk.Label(fields_frame, text="Título:", font=("Arial", 10)).pack(anchor=tk.W, pady=(0, 5))
        titulo_entry = ttk.Entry(fields_frame, font=("Arial", 11), width=40)
        titulo_entry.pack(fill=tk.X, pady=(0, 15))
        titulo_entry.focus()
        
        # Descrição
        ttk.Label(fields_frame, text="Descrição:", font=("Arial", 10)).pack(anchor=tk.W, pady=(0, 5))
        
        # Frame para Text com scrollbar
        desc_frame = ttk.Frame(fields_frame)
        desc_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        descricao_text = tk.Text(desc_frame, font=("Arial", 10), width=40, height=6, wrap=tk.WORD)
        desc_scrollbar = ttk.Scrollbar(desc_frame, orient=tk.VERTICAL, command=descricao_text.yview)
        descricao_text.config(yscrollcommand=desc_scrollbar.set)
        
        descricao_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        desc_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Prioridade
        prioridade_frame = ttk.Frame(fields_frame)
        prioridade_frame.pack(fill=tk.X, pady=(0, 15))
        
        prioridade_var = tk.IntVar(value=0)
        prioridade_check = ttk.Checkbutton(
            prioridade_frame,
            text="Tarefa Prioritária (destacar em vermelho)",
            variable=prioridade_var
        )
        prioridade_check.pack(side=tk.LEFT)
        
        def salvar():
            titulo = titulo_entry.get().strip()
            descricao = descricao_text.get("1.0", tk.END).strip()
            prioridade = 1 if prioridade_var.get() == 1 else 0
            
            if not titulo:
                messagebox.showwarning("Aviso", "Por favor, digite o título da tarefa!")
                titulo_entry.focus()
                return
            
            # Se for admin visualizando outro usuário, criar tarefa para o usuário selecionado
            usuario_destino = self.app.email_logado
            if self.app.email_logado == "admin" and self.usuario_kanban_selecionado:
                usuario_destino = self.usuario_kanban_selecionado
            
            sucesso, resultado = self.app.adicionar_tarefa(
                usuario_destino,
                titulo,
                descricao,
                "A Fazer",
                prioridade
            )
            
            if sucesso:
                messagebox.showinfo("Sucesso", "Tarefa adicionada com sucesso!")
                janela.destroy()
                if self.app.email_logado == "admin":
                    if self.usuario_kanban_selecionado:
                        self.carregar_kanban_admin()
                else:
                    self.carregar_kanban()
            else:
                messagebox.showerror("Erro", f"Erro ao adicionar tarefa: {resultado}")
        
        # Frame para botões (fixo na parte inferior)
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        salvar_btn = ttk.Button(buttons_frame, text="Salvar", command=salvar, width=15)
        salvar_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        cancelar_btn = ttk.Button(buttons_frame, text="Cancelar", command=janela.destroy, width=15)
        cancelar_btn.pack(side=tk.LEFT)
        
        titulo_entry.bind("<Return>", lambda e: descricao_text.focus())
    
    def mover_tarefa(self, origem, destino):
        """Move uma tarefa entre colunas"""
        listbox_origem = self.kanban_widgets[origem]["listbox"]
        selecionado = listbox_origem.curselection()
        
        if not selecionado:
            messagebox.showwarning("Aviso", "Por favor, selecione uma tarefa para mover!")
            return
        
        # Obter o texto da tarefa selecionada
        texto = listbox_origem.get(selecionado[0])
        # Extrair tarefa_id do texto [id] titulo ou 🔴 [id] titulo
        try:
            texto_id = texto.replace('🔴', '').strip()
            tarefa_id = int(texto_id.split(']')[0].replace('[', '').strip())
        except:
            messagebox.showerror("Erro", "Erro ao identificar a tarefa!")
            return
        
        # Atualizar status no banco de dados (com validação de propriedade)
        sucesso, mensagem = self.app.atualizar_status_tarefa(tarefa_id, destino, self.app.email_logado)
        if sucesso:
            if self.app.email_logado == "admin":
                self.carregar_kanban_admin()
            else:
                self.carregar_kanban()
        else:
            messagebox.showerror("Erro", mensagem)
    
    def excluir_tarefa_kanban(self, coluna):
        """Exclui uma tarefa selecionada"""
        listbox = self.kanban_widgets[coluna]["listbox"]
        selecionado = listbox.curselection()
        
        if not selecionado:
            messagebox.showwarning("Aviso", "Por favor, selecione uma tarefa para excluir!")
            return
        
        # Obter o texto da tarefa selecionada
        texto = listbox.get(selecionado[0])
        # Extrair tarefa_id do texto [id] titulo ou 🔴 [id] titulo
        try:
            texto_id = texto.replace('🔴', '').strip()
            tarefa_id = int(texto_id.split(']')[0].replace('[', '').strip())
            titulo = texto_id.split(']')[1].strip().split('\n')[0].strip()
            if titulo.startswith('[Usuário:'):
                titulo = texto_id.split(']')[1].split('[Usuário:')[0].strip()
        except:
            messagebox.showerror("Erro", "Erro ao identificar a tarefa!")
            return
        
        # Confirmar exclusão
        resposta = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Deseja realmente excluir a tarefa \"{titulo}\"?"
        )
        
        if resposta:
            # Excluir tarefa (com validação de propriedade)
            sucesso, mensagem = self.app.excluir_tarefa(tarefa_id, self.app.email_logado)
            if sucesso:
                messagebox.showinfo("Sucesso", mensagem)
                if self.app.email_logado == "admin":
                    self.carregar_kanban_admin()
                else:
                    self.carregar_kanban()
            else:
                messagebox.showerror("Erro", mensagem)
    
    def sair(self):
        """Volta para a tela de login"""
        self.app.mostrar_login()


def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
