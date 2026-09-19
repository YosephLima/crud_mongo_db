import os
from pathlib import Path
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import PyMongoError

# lê o .env da raiz do projeto e joga as variáveis no ambiente
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB", "mercado_livre")

def conectar():
    # abre a conexão com o Atlas e devolve o banco já escolhido
    if not MONGODB_URI:
        raise SystemExit("MONGODB_URI não definida. Copie o .env.example para .env e preencha.")

    client = MongoClient(
        MONGODB_URI, server_api=ServerApi("1"), serverSelectionTimeoutMS=5000, tz_aware=True
    )
    client.admin.command("ping")

    db = client[MONGODB_DB]
    criar_indices(db)
    return db

def criar_indices(db):
    # controle da unicidade (fica no banco)
    try:
        db.usuarios.create_index("cpf", unique=True)
        db.usuarios.create_index("email", unique=True)
        db.favoritos.create_index([("usu_id", 1), ("pro_id", 1)], unique=True)
    except PyMongoError as erro:
        print("Aviso: não foi possível criar os índices únicos.")
        print("Provavelmente já existem documentos repetidos no banco.")
        print(f"Detalhe: {erro}")
