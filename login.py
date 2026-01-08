import tkinter as tk
from tkinter import messagebox, ttk
import json
import os

class LoginScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Tela de Login")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Centralizar janela
        self.center_window()
        
        # Carregar usuários
        self.users_file = "users.json"
        self.users = self.load_users()
        
        # Frame principal
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(
            main_frame, 
            text="Sistema de Login", 
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=(0, 30))
        
        # Frame para campos de entrada
        entry_frame = ttk.Frame(main_frame)
        entry_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Campo de Login
        login_label = ttk.Label(entry_frame, text="Login:", font=("Arial", 10))
        login_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        self.login_entry = ttk.Entry(entry_frame, font=("Arial", 11), width=30)
        self.login_entry.grid(row=1, column=0, pady=(0, 15))
        self.login_entry.focus()
        
        # Campo de Senha
        senha_label = ttk.Label(entry_frame, text="Senha:", font=("Arial", 10))
        senha_label.grid(row=2, column=0, sticky=tk.W, pady=(0, 10))
        
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
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Botão Entrar
        entrar_btn = ttk.Button(
            button_frame,
            text="Entrar",
            command=self.entrar,
            width=15
        )
        entrar_btn.pack(side=tk.LEFT, padx=(0, 10), expand=True, fill=tk.X)
        
        # Botão Cadastrar
        cadastrar_btn = ttk.Button(
            button_frame,
            text="Cadastrar",
            command=self.cadastrar,
            width=15
        )
        cadastrar_btn.pack(side=tk.LEFT, expand=True, fill=tk.X)
    
    def center_window(self):
        """Centraliza a janela na tela"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def load_users(self):
        """Carrega usuários do arquivo JSON"""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_users(self):
        """Salva usuários no arquivo JSON"""
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, indent=4, ensure_ascii=False)
    
    def entrar(self):
        """Função do botão Entrar"""
        login = self.login_entry.get().strip()
        senha = self.senha_entry.get()
        
        if not login:
            messagebox.showwarning("Aviso", "Por favor, digite o login!")
            self.login_entry.focus()
            return
        
        if not senha:
            messagebox.showwarning("Aviso", "Por favor, digite a senha!")
            self.senha_entry.focus()
            return
        
        # Verificar credenciais
        if login in self.users and self.users[login] == senha:
            messagebox.showinfo("Sucesso", f"Bem-vindo, {login}!")
            self.clear_fields()
        else:
            messagebox.showerror("Erro", "Login ou senha incorretos!")
            self.senha_entry.delete(0, tk.END)
            self.senha_entry.focus()
    
    def cadastrar(self):
        """Função do botão Cadastrar"""
        login = self.login_entry.get().strip()
        senha = self.senha_entry.get()
        
        if not login:
            messagebox.showwarning("Aviso", "Por favor, digite o login!")
            self.login_entry.focus()
            return
        
        if not senha:
            messagebox.showwarning("Aviso", "Por favor, digite a senha!")
            self.senha_entry.focus()
            return
        
        # Verificar se usuário já existe
        if login in self.users:
            messagebox.showerror("Erro", "Este login já está cadastrado!")
            self.login_entry.focus()
            return
        
        # Cadastrar novo usuário
        self.users[login] = senha
        self.save_users()
        messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")
        self.clear_fields()
    
    def clear_fields(self):
        """Limpa os campos de entrada"""
        self.login_entry.delete(0, tk.END)
        self.senha_entry.delete(0, tk.END)
        self.login_entry.focus()


def main():
    root = tk.Tk()
    app = LoginScreen(root)
    root.mainloop()


if __name__ == "__main__":
    main()
