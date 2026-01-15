# Sistema de Login e Gerenciamento de Tarefas

Sistema de gerenciamento de tarefas com autenticação de usuários e quadro Kanban.

## Funcionalidades

- Sistema de login e cadastro de usuários
- Autenticação de usuários
- Gerenciamento de usuários (apenas admin)
- Quadro Kanban para gerenciamento de tarefas
- Priorização de tarefas
- Diferentes níveis de acesso (admin e usuários normais)

## Instalação

O sistema utiliza Python 3 com as seguintes bibliotecas:
- `tkinter` (geralmente incluído com Python)
- `sqlite3` (incluído com Python)

Para executar os testes, é necessário instalar o pytest:

```bash
pip install pytest
```

Ou usando o arquivo requirements.txt:

```bash
pip install -r requirements.txt
```

## Execução

Para executar o sistema:

```bash
python3 login.py
```

Para executar os testes:

```bash
pytest test_login.py -v
```

## Estrutura

- `login.py`: Código principal da aplicação
- `test_login.py`: Testes unitários usando pytest
- `users.db`: Banco de dados SQLite (criado automaticamente)
- `requirements.txt`: Dependências do projeto

## Credenciais padrão- **Admin**: 
  - Email: `admin`
  - Senha: `admin`
