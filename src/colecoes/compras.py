from datetime import datetime, timezone
from decimal import Decimal
from bson.decimal128 import Decimal128
from pymongo.errors import PyMongoError
import ui
import validacao
from colecoes import produtos, usuarios

# ------------- Compras -------------

# Documento (exemplo completo em mocks_mongodb/compras.json):
#   data, valor_total (Decimal128),
#   comprador { usu_id, nome, email },
#   itens [ { pro_id, nome, preco_unitario, quantidade_adquirida,
#             vendedor { usu_id, nome_loja } } ]

def menu(db):
    acoes = {
        "1": ("Create Compra", criar),
        "2": ("Read Compra", listar),
        "3": ("Update Compra", atualizar),
        "4": ("Delete Compra", remover),
    }

    while True:
        print("\n--- Menu da Compra ---")
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
        except PyMongoError as erro:
            print(f"Erro no banco: {erro}")


def criar(db):
    mycol = db.compras
    print("\nInserindo uma nova compra")

    usuario = usuarios.buscar(db, "CPF do comprador: ")
    if usuario is None:
        return

    itens = ler_itens(db)
    if not itens:
        print("Compra sem itens, nada foi inserido.")
        return

    mydoc = {
        "data": datetime.now(timezone.utc),
        "valor_total": calcular_total(itens),
        "comprador": {
            "usu_id": usuario["_id"],
            "nome": usuario.get("nome"),
            "email": usuario.get("email"),
        },
        "itens": itens,
    }

    x = mycol.insert_one(mydoc)
    for item in itens:
        ajustar_estoque(db, item["pro_id"], -item["quantidade_adquirida"])

    print("Documento inserido com ID ", x.inserted_id)
    print("Estoque dos produtos atualizado.")


def listar(db):
    mycol = db.compras
    myquery = {}

    if ui.confirmar("Filtrar pelas compras de um usuário"):
        usuario = usuarios.buscar(db, "CPF do comprador: ")
        if usuario is None:
            return
        myquery = {"comprador.usu_id": usuario["_id"]}

    print("\nCompras cadastradas: ")
    encontrados = 0
    for x in mycol.find(myquery).sort("data"):
        mostrar(x)
        encontrados += 1

    if not encontrados:
        print("Nenhuma compra encontrada.")


def atualizar(db):
    mycol = db.compras
    mydoc = escolher(db, "alterar")
    if mydoc is None:
        return

    print("\nDados da compra: ")
    mostrar(mydoc)

    itens = mydoc["itens"]
    item = ui.escolher([(f"{i['nome']} x{i['quantidade_adquirida']}", i) for i in itens])
    anterior = item["quantidade_adquirida"]

    produto = db.produtos.find_one({"_id": item["pro_id"]})
    estoque = produto.get("quantidade_estoque", 0) if produto else 0
    item["quantidade_adquirida"] = ui.ler(
        f"Nova quantidade de {item['nome']} (máximo {estoque + anterior}): ",
        validacao.quantidade_ate(estoque + anterior),
    )

    # a lista inteira volta para o banco (com o valor_total recalculado)
    novos = {"itens": itens, "valor_total": calcular_total(itens)}
    resultado = mycol.update_one({"_id": mydoc["_id"]}, {"$set": novos})
    ajustar_estoque(db, item["pro_id"], anterior - item["quantidade_adquirida"])
    print(f"{resultado.modified_count} compra(s) alterada(s).")


def remover(db):
    mycol = db.compras
    mydoc = escolher(db, "deletar")
    if mydoc is None:
        return

    print("\nCompra encontrada: ")
    mostrar(mydoc)
    if not ui.confirmar("Confirma a exclusão"):
        print("Exclusão cancelada.")
        return

    resultado = mycol.delete_one({"_id": mydoc["_id"]})
    for item in mydoc.get("itens", []):
        ajustar_estoque(db, item["pro_id"], item["quantidade_adquirida"])

    print(f"{resultado.deleted_count} compra(s) deletada(s).")
    print("Itens devolvidos ao estoque.")


def ler_itens(db):
    # cada item guarda uma cópia dos dados do produto no momento da compra
    itens = []
    while True:
        produto = produtos.buscar(db)

        if produto is not None:
            estoque = produto.get("quantidade_estoque", 0)

            if estoque == 0:
                print("Produto sem estoque.")
            else:
                itens.append({
                    "pro_id": produto["_id"],
                    "nome": produto["nome"],
                    "preco_unitario": produto["preco_unitario"],
                    "quantidade_adquirida": ui.ler(
                        f"Quantidade (estoque: {estoque}): ", validacao.quantidade_ate(estoque)
                    ),
                    "vendedor": produto.get("vendedor"),
                })

        if not ui.confirmar("Deseja incluir outro produto"):
            return itens


def ajustar_estoque(db, pro_id, quantidade):
    db.produtos.update_one({"_id": pro_id}, {"$inc": {"quantidade_estoque": quantidade}})


def calcular_total(itens):
    # soma preço x quantidade de cada item
    total = Decimal("0")
    for item in itens:
        total += Decimal(str(item["preco_unitario"])) * item["quantidade_adquirida"]
    return Decimal128(total)


def escolher(db, acao):
    # mostra as compras de um usuário para escolher qual alterar/deletar
    usuario = usuarios.buscar(db, f"CPF do comprador da compra a {acao}: ")
    if usuario is None:
        return None

    docs = list(db.compras.find({"comprador.usu_id": usuario["_id"]}).sort("data"))
    if not docs:
        print("Esse usuário não tem compras.")
        return None

    return ui.escolher([(f"{formatar_data(d.get('data'))} - R$ {d.get('valor_total')}", d) for d in docs])


def formatar_data(data):
    # o banco guarda em UTC; mostra no fuso de quem está rodando
    return data.astimezone().strftime("%d/%m/%Y %H:%M") if data else "sem data"


def mostrar(doc):
    # imprime o documento de um jeito legível no terminal
    comprador = doc.get("comprador", {})
    print(f"\n  {formatar_data(doc.get('data'))} | R$ {doc.get('valor_total')} | {comprador.get('nome')}")
    print(f"  _id: {doc.get('_id')}")

    for item in doc.get("itens", []):
        vendedor = item.get("vendedor") or {}
        print(
            f"  item: {item.get('nome')} x{item.get('quantidade_adquirida')} "
            f"- R$ {item.get('preco_unitario')} - {vendedor.get('nome_loja')}"
        )
