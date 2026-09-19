# CRUD MongoDB — Mercado Livre

Exercício da disciplina de Banco de Dados Não Relacional (Fatec — 3º DSM).

## Como rodar

1. Crie o ambiente virtual e instale as dependências.

   Linux / macOS:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

   Windows (PowerShell ou cmd):

   ```bat
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Copie o `.env.example` para `.env` e preencha com a URI do seu cluster:

   ```bash
   cp .env.example .env      # Linux / macOS
   copy .env.example .env    # Windows
   ```

   | Variável      | Descrição                                   |
   |---------------|---------------------------------------------|
   | `MONGODB_URI` | String de conexão do MongoDB Atlas          |
   | `MONGODB_DB`  | Nome do banco (padrão: `mercado_livre`)     |

3. Execute:

   ```bash
   python src/menu.py
   ```
