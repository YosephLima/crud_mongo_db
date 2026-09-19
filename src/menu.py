from pymongo.errors import PyMongoError

from db import conectar
from colecoes import usuarios, produtos, favoritos, compras

COLECOES = {
    "1": ("Usuários", usuarios.menu),
    "2": ("Produtos", produtos.menu),
    "3": ("Favoritos", favoritos.menu),
    "4": ("Compras", compras.menu),
}

def main():
    try:
        db = conectar()
    except PyMongoError as erro:
        print("Não foi possível conectar no MongoDB.")
        print(f"Detalhe: {erro}")
        print("Confira a MONGODB_URI no .env e se o seu IP está liberado no Atlas.")
        return

    while True:
        print("\n=== Mercado Livre ===")
        for tecla, (titulo, _) in COLECOES.items():
            print(f"{tecla} - CRUD {titulo}")
        opcao = input("Digite a opção desejada (S para sair): ").strip().upper()

        if opcao == "S":
            break
        if opcao not in COLECOES:
            print("Opção inválida.")
            continue

        COLECOES[opcao][1](db)

if __name__ == "__main__":
    # Ctrl+C e Ctrl+D
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nTchau Prof...")
