from pymongo.errors import DuplicateKeyError, PyMongoError
import ui
from colecoes import produtos, usuarios

# ------------- Favoritos -------------

# Documento (exemplo completo em mocks_mongodb/favoritos.json):
#   usu_id, pro_id, nome_produto


def menu(db):
    acoes = {
        "1": ("Create Favorito", criar),
        "2": ("Read Favorito", listar),
        "3": ("Update Favorito", atualizar),
        "4": ("Delete Favorito", remover),
    }

    while True:
        print("\n--- Menu do Favorito ---")
        for tecla, (titulo, _) in acoes.items():
            print(f"{tecla} - {titulo}")
        opcao = input("Digite a opção desejada (V para voltar): ").strip().upper()

        if opcao == "V":
            return
        if opcao not in acoes:
            print("Opção inválida.")
            continue

        try:
            acoes[opcao][1](db)
        except DuplicateKeyError:
            print("Esse produto já está nos favoritos desse usuário.")
        except PyMongoError as erro:
            print(f"Erro no banco: {erro}")


def criar(db):
    mycol = db.favoritos
    print("\nInserindo um novo favorito")

    usuario = usuarios.buscar(db, "CPF do usuário: ")
    if usuario is None:
        return

    produto = produtos.buscar(db)
    if produto is None:
        return

    mydoc = {
        "usu_id": usuario["_id"],
        "pro_id": produto["_id"],
        "nome_produto": produto["nome"],
    }

    x = mycol.insert_one(mydoc)
    print("Documento inserido com ID ", x.inserted_id)


def listar(db):
    mycol = db.favoritos
    myquery = {}

    if ui.confirmar("Filtrar pelos favoritos de um usuário"):
        usuario = usuarios.buscar(db)
        if usuario is None:
            return
        myquery = {"usu_id": usuario["_id"]}

    print("\nFavoritos cadastrados: ")
    encontrados = 0
    for x in mycol.find(myquery).sort("nome_produto"):
        mostrar(x)
        encontrados += 1

    if not encontrados:
        print("Nenhum favorito encontrado.")


def atualizar(db):
    mycol = db.favoritos
    mydoc = escolher(db, "alterar")
    if mydoc is None:
        return

    print("\nTrocando o produto desse favorito.")
    produto = produtos.buscar(db, "Nome do novo produto: ")
    if produto is None:
        return

    novos = {"pro_id": produto["_id"], "nome_produto": produto["nome"]}
    resultado = mycol.update_one({"_id": mydoc["_id"]}, {"$set": novos})
    print(f"{resultado.modified_count} favorito(s) alterado(s).")


def remover(db):
    mycol = db.favoritos
    mydoc = escolher(db, "deletar")
    if mydoc is None:
        return

    print("\nFavorito encontrado: ")
    mostrar(mydoc)
    if not ui.confirmar("Confirma a exclusão"):
        print("Exclusão cancelada.")
        return

    resultado = mycol.delete_one({"_id": mydoc["_id"]})
    print(f"{resultado.deleted_count} favorito(s) deletado(s).")


def escolher(db, acao):
    # mostra os favoritos de um usuário para escolher qual alterar/deletar
    usuario = usuarios.buscar(db, f"CPF do usuário do favorito a {acao}: ")
    if usuario is None:
        return None

    docs = list(db.favoritos.find({"usu_id": usuario["_id"]}).sort("nome_produto"))
    if not docs:
        print("Esse usuário não tem favoritos.")
        return None

    return ui.escolher([(d["nome_produto"], d) for d in docs])


def mostrar(doc):
    # imprime o documento de um jeito legível no terminal
    print(f"\n  {doc.get('nome_produto')}")
    print(f"  _id: {doc.get('_id')} | usu_id: {doc.get('usu_id')} | pro_id: {doc.get('pro_id')}")
