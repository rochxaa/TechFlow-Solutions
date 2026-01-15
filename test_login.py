"""
Testes unitários para o sistema de login e gerenciamento de tarefas
"""
import pytest
import sqlite3
import os
import tempfile
import tkinter as tk
from datetime import datetime
import sys

# Adicionar o diretório atual ao path para importar o módulo login
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from login import App


@pytest.fixture
def temp_db():
    """Cria um banco de dados temporário para os testes"""
    # Criar arquivo temporário
    fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    yield db_path
    
    # Limpar após o teste
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def mock_root():
    """Cria uma janela root mock para os testes"""
    # Configurar variável de ambiente para evitar erros em ambiente headless
    os.environ['DISPLAY'] = os.environ.get('DISPLAY', ':99')
    
    root = tk.Tk()
    root.withdraw()  # Esconder a janela
    yield root
    root.destroy()


@pytest.fixture
def app_instance(temp_db, mock_root):
    """Cria uma instância da App com banco de dados temporário"""
    app = App(mock_root)
    app.db_file = temp_db
    app.init_database()
    yield app


class TestApp:
    """Testes para a classe App"""
    
    def test_init_database(self, temp_db, mock_root):
        """Testa a inicialização do banco de dados"""
        app = App(mock_root)
        app.db_file = temp_db
        app.init_database()
        
        # Verificar se as tabelas foram criadas
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        # Verificar tabela de usuários
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'")
        assert cursor.fetchone() is not None
        
        # Verificar tabela de tarefas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tarefas'")
        assert cursor.fetchone() is not None
        
        # Verificar se o admin foi criado
        cursor.execute("SELECT email FROM usuarios WHERE email = 'admin'")
        assert cursor.fetchone() is not None
        
        conn.close()
    
    def test_cadastrar_usuario(self, app_instance):
        """Testa o cadastro de um novo usuário"""
        resultado = app_instance.cadastrar_usuario("João Silva", "joao@teste.com", "senha123")
        assert resultado is True
        
        # Verificar se o usuário foi cadastrado
        assert app_instance.usuario_existe("joao@teste.com") is True
    
    def test_cadastrar_usuario_duplicado(self, app_instance):
        """Testa que não é possível cadastrar o mesmo email duas vezes"""
        app_instance.cadastrar_usuario("João Silva", "joao@teste.com", "senha123")
        
        # Tentar cadastrar o mesmo email novamente
        resultado = app_instance.cadastrar_usuario("João Silva", "joao@teste.com", "senha456")
        assert resultado is False
    
    def test_usuario_existe(self, app_instance):
        """Testa a verificação de existência de usuário"""
        # Usuário não existe
        assert app_instance.usuario_existe("inexistente@teste.com") is False
        
        # Cadastrar usuário
        app_instance.cadastrar_usuario("Maria Santos", "maria@teste.com", "senha123")
        
        # Usuário existe
        assert app_instance.usuario_existe("maria@teste.com") is True
    
    def test_verificar_usuario(self, app_instance):
        """Testa a verificação de credenciais de usuário"""
        # Cadastrar usuário
        app_instance.cadastrar_usuario("Pedro Costa", "pedro@teste.com", "senha123")
        
        # Credenciais corretas
        resultado = app_instance.verificar_usuario("pedro@teste.com", "senha123")
        assert resultado is not None
        assert resultado[0] == "Pedro Costa"
        assert resultado[1] == "pedro@teste.com"
        
        # Credenciais incorretas
        resultado = app_instance.verificar_usuario("pedro@teste.com", "senha_errada")
        assert resultado is None
        
        # Usuário não existe
        resultado = app_instance.verificar_usuario("inexistente@teste.com", "senha123")
        assert resultado is None
    
    def test_listar_usuarios(self, app_instance):
        """Testa a listagem de usuários"""
        # Inicialmente deve ter apenas o admin
        usuarios = app_instance.listar_usuarios()
        assert len(usuarios) >= 1  # Pelo menos o admin
        
        # Cadastrar mais usuários
        app_instance.cadastrar_usuario("Ana Silva", "ana@teste.com", "senha123")
        app_instance.cadastrar_usuario("Carlos Souza", "carlos@teste.com", "senha123")
        
        # Verificar listagem
        usuarios = app_instance.listar_usuarios()
        assert len(usuarios) >= 3  # Admin + 2 novos usuários
    
    def test_excluir_usuario(self, app_instance):
        """Testa a exclusão de usuário"""
        # Cadastrar usuário
        app_instance.cadastrar_usuario("Teste Exclusão", "excluir@teste.com", "senha123")
        assert app_instance.usuario_existe("excluir@teste.com") is True
        
        # Excluir usuário
        sucesso, mensagem = app_instance.excluir_usuario("excluir@teste.com")
        assert sucesso is True
        assert app_instance.usuario_existe("excluir@teste.com") is False
    
    def test_excluir_admin(self, app_instance):
        """Testa que não é possível excluir o usuário admin"""
        sucesso, mensagem = app_instance.excluir_usuario("admin")
        assert sucesso is False
        assert "administrador" in mensagem.lower()
    
    def test_adicionar_tarefa(self, app_instance):
        """Testa a adição de uma nova tarefa"""
        # Cadastrar usuário
        app_instance.cadastrar_usuario("Tarefa User", "tarefa@teste.com", "senha123")
        
        # Adicionar tarefa
        sucesso, tarefa_id = app_instance.adicionar_tarefa(
            "tarefa@teste.com",
            "Tarefa de Teste",
            "Descrição da tarefa",
            "A Fazer",
            0
        )
        assert sucesso is True
        assert isinstance(tarefa_id, int)
        assert tarefa_id > 0
    
    def test_adicionar_tarefa_prioritaria(self, app_instance):
        """Testa a adição de uma tarefa prioritária"""
        app_instance.cadastrar_usuario("Prioridade User", "prioridade@teste.com", "senha123")
        
        sucesso, tarefa_id = app_instance.adicionar_tarefa(
            "prioridade@teste.com",
            "Tarefa Prioritária",
            "Descrição",
            "A Fazer",
            1  # Prioridade alta
        )
        assert sucesso is True
        
        # Verificar prioridade
        prioridade = app_instance.obter_prioridade_tarefa(tarefa_id)
        assert prioridade == 1
    
    def test_listar_tarefas(self, app_instance):
        """Testa a listagem de tarefas"""
        app_instance.cadastrar_usuario("Lista User", "lista@teste.com", "senha123")
        
        # Adicionar tarefas
        app_instance.adicionar_tarefa("lista@teste.com", "Tarefa 1", "Desc 1", "A Fazer", 0)
        app_instance.adicionar_tarefa("lista@teste.com", "Tarefa 2", "Desc 2", "Em Progresso", 0)
        
        # Listar tarefas do usuário
        tarefas = app_instance.listar_tarefas("lista@teste.com")
        assert len(tarefas) == 2
    
    def test_atualizar_prioridade_tarefa(self, app_instance):
        """Testa a atualização de prioridade de uma tarefa"""
        app_instance.cadastrar_usuario("Prioridade User", "prio@teste.com", "senha123")
        
        # Adicionar tarefa sem prioridade
        sucesso, tarefa_id = app_instance.adicionar_tarefa(
            "prio@teste.com", "Tarefa", "Desc", "A Fazer", 0
        )
        assert sucesso is True
        
        # Verificar prioridade inicial
        assert app_instance.obter_prioridade_tarefa(tarefa_id) == 0
        
        # Atualizar para prioritária
        resultado = app_instance.atualizar_prioridade_tarefa(tarefa_id, 1)
        assert resultado is True
        assert app_instance.obter_prioridade_tarefa(tarefa_id) == 1
        
        # Despriorizar
        app_instance.atualizar_prioridade_tarefa(tarefa_id, 0)
        assert app_instance.obter_prioridade_tarefa(tarefa_id) == 0
    
    def test_atualizar_status_tarefa(self, app_instance):
        """Testa a atualização de status de uma tarefa"""
        app_instance.cadastrar_usuario("Status User", "status@teste.com", "senha123")
        
        # Adicionar tarefa
        sucesso, tarefa_id = app_instance.adicionar_tarefa(
            "status@teste.com", "Tarefa Status", "Desc", "A Fazer", 0
        )
        assert sucesso is True
        
        # Atualizar status
        sucesso, mensagem = app_instance.atualizar_status_tarefa(
            tarefa_id, "Em Progresso", "status@teste.com"
        )
        assert sucesso is True
        
        # Verificar status atualizado
        tarefas = app_instance.listar_tarefas("status@teste.com")
        tarefa = [t for t in tarefas if t[0] == tarefa_id][0]
        assert tarefa[3] == "Em Progresso"
    
    def test_atualizar_status_tarefa_outro_usuario(self, app_instance):
        """Testa que usuário não pode atualizar tarefa de outro usuário"""
        app_instance.cadastrar_usuario("User 1", "user1@teste.com", "senha123")
        app_instance.cadastrar_usuario("User 2", "user2@teste.com", "senha123")
        
        # User 1 cria tarefa
        sucesso, tarefa_id = app_instance.adicionar_tarefa(
            "user1@teste.com", "Tarefa User 1", "Desc", "A Fazer", 0
        )
        
        # User 2 tenta atualizar tarefa de User 1
        sucesso, mensagem = app_instance.atualizar_status_tarefa(
            tarefa_id, "Concluído", "user2@teste.com"
        )
        assert sucesso is False
        assert "permissão" in mensagem.lower()
    
    def test_admin_pode_atualizar_qualquer_tarefa(self, app_instance):
        """Testa que admin pode atualizar qualquer tarefa"""
        app_instance.cadastrar_usuario("User Normal", "user@teste.com", "senha123")
        
        # User cria tarefa
        sucesso, tarefa_id = app_instance.adicionar_tarefa(
            "user@teste.com", "Tarefa User", "Desc", "A Fazer", 0
        )
        
        # Admin atualiza tarefa do user
        sucesso, mensagem = app_instance.atualizar_status_tarefa(
            tarefa_id, "Concluído", "admin"
        )
        assert sucesso is True
    
    def test_excluir_tarefa(self, app_instance):
        """Testa a exclusão de uma tarefa"""
        app_instance.cadastrar_usuario("Excluir User", "excluir@teste.com", "senha123")
        
        # Adicionar tarefa
        sucesso, tarefa_id = app_instance.adicionar_tarefa(
            "excluir@teste.com", "Tarefa Excluir", "Desc", "A Fazer", 0
        )
        
        # Excluir tarefa
        sucesso, mensagem = app_instance.excluir_tarefa(tarefa_id, "excluir@teste.com")
        assert sucesso is True
        
        # Verificar que a tarefa foi excluída
        tarefas = app_instance.listar_tarefas("excluir@teste.com")
        assert len([t for t in tarefas if t[0] == tarefa_id]) == 0
    
    def test_excluir_tarefa_outro_usuario(self, app_instance):
        """Testa que usuário não pode excluir tarefa de outro usuário"""
        app_instance.cadastrar_usuario("User A", "usera@teste.com", "senha123")
        app_instance.cadastrar_usuario("User B", "userb@teste.com", "senha123")
        
        # User A cria tarefa
        sucesso, tarefa_id = app_instance.adicionar_tarefa(
            "usera@teste.com", "Tarefa User A", "Desc", "A Fazer", 0
        )
        
        # User B tenta excluir tarefa de User A
        sucesso, mensagem = app_instance.excluir_tarefa(tarefa_id, "userb@teste.com")
        assert sucesso is False
        assert "permissão" in mensagem.lower()
    
    def test_admin_pode_excluir_qualquer_tarefa(self, app_instance):
        """Testa que admin pode excluir qualquer tarefa"""
        app_instance.cadastrar_usuario("User Normal", "normal@teste.com", "senha123")
        
        # User cria tarefa
        sucesso, tarefa_id = app_instance.adicionar_tarefa(
            "normal@teste.com", "Tarefa Normal", "Desc", "A Fazer", 0
        )
        
        # Admin exclui tarefa do user
        sucesso, mensagem = app_instance.excluir_tarefa(tarefa_id, "admin")
        assert sucesso is True
    
    def test_verificar_propriedade_tarefa(self, app_instance):
        """Testa a verificação de propriedade de tarefa"""
        app_instance.cadastrar_usuario("Propriedade User", "prop@teste.com", "senha123")
        
        # Adicionar tarefa
        sucesso, tarefa_id = app_instance.adicionar_tarefa(
            "prop@teste.com", "Tarefa Propriedade", "Desc", "A Fazer", 0
        )
        
        # Verificar propriedade
        assert app_instance.verificar_propriedade_tarefa(tarefa_id, "prop@teste.com") is True
        assert app_instance.verificar_propriedade_tarefa(tarefa_id, "outro@teste.com") is False
    
    def test_excluir_usuario_exclui_tarefas(self, app_instance):
        """Testa que excluir usuário também exclui suas tarefas"""
        app_instance.cadastrar_usuario("Tarefas User", "tarefas@teste.com", "senha123")
        
        # Adicionar tarefas
        app_instance.adicionar_tarefa("tarefas@teste.com", "Tarefa 1", "Desc 1", "A Fazer", 0)
        app_instance.adicionar_tarefa("tarefas@teste.com", "Tarefa 2", "Desc 2", "Em Progresso", 0)
        
        # Verificar tarefas existem
        tarefas = app_instance.listar_tarefas("tarefas@teste.com")
        assert len(tarefas) == 2
        
        # Excluir usuário
        app_instance.excluir_usuario("tarefas@teste.com")
        
        # Verificar que as tarefas foram excluídas
        tarefas = app_instance.listar_tarefas("tarefas@teste.com")
        assert len(tarefas) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
