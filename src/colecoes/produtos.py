from pymongo.errors import PyMongoError
import ui
import validacao
from colecoes import usuarios

# ------------- Produtos -------------

# Documento (exemplo completo em mocks_mongodb/produtos.json):
#   nome, descricao, preco_unitario (Decimal128), quantidade_estoque,
#   imagens [ nomes dos arquivos ], ativo (True/False),
#   vendedor { usu_id, nome_loja }


def menu(db):
    acoes = {
        "1": ("Create Produto", criar),
        "2": ("Read Produto", listar),
        "3": ("Update Produto", atualizar),
        "4": ("Delete Produto", remover),
    }

    while True:
        print("\n--- Menu do Produto ---")
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
    mycol = db.produtos
    print("\nInserindo um novo produto")

    vendedor = escolher_vendedor(db)
    if vendedor is None:
        return

    mydoc = {
        "nome": ui.ler("Nome: "),
        "descricao": ui.ler("Descrição: "),
        "preco_unitario": ui.ler("Preço unitário: ", validacao.dinheiro),
        "quantidade_estoque": ui.ler("Quantidade em estoque: ", validacao.quantidade),
        "imagens": ler_imagens(),
        "ativo": ui.confirmar("Produto ativo"),
        "vendedor": vendedor,
    }

    x = mycol.insert_one(mydoc)
    print("Documento inserido com ID ", x.inserted_id)


def listar(db):
    mycol = db.produtos
    nome = ui.ler("Deseja algum nome específico (vazio lista todos)? ", obrigatorio=False)

    if not nome:
        mydoc = mycol.find().sort("nome")
    else:
        mydoc = mycol.find({"nome": {"$regex": nome, "$options": "i"}}).sort("nome")

    print("\nProdutos cadastrados: ")
    encontrados = 0
    for x in mydoc:
        mostrar(x)
        encontrados += 1

    if not encontrados:
        print("Nenhum produto encontrado.")


def atualizar(db):
    mycol = db.produtos
    mydoc = buscar(db, "Nome do produto a ser alterado: ")
    if mydoc is None:
        return

    myquery = {"_id": mydoc["_id"]}
    print("\nDados do produto: ")
    mostrar(mydoc)
    print("(deixe em branco o que não quiser mudar)")

    novos = {}
    nome = ui.ler("Mudar Nome: ", obrigatorio=False)
    if nome:
        novos["nome"] = nome

    descricao = ui.ler("Mudar Descrição: ", obrigatorio=False)
    if descricao:
        novos["descricao"] = descricao

    preco = ui.ler("Mudar Preço unitário: ", validacao.dinheiro, obrigatorio=False)
    if preco is not None:
        novos["preco_unitario"] = preco

    estoque = ui.ler("Mudar Quantidade em estoque: ", validacao.quantidade, obrigatorio=False)
    if estoque is not None:
        novos["quantidade_estoque"] = estoque

    if ui.confirmar("Mudar as imagens"):
        novos["imagens"] = ler_imagens()

    if ui.confirmar("Mudar a situação do produto"):
        novos["ativo"] = ui.confirmar("Produto ativo")

    if not novos:
        print("Nada foi alterado.")
        return

    resultado = mycol.update_one(myquery, {"$set": novos})
    print(f"{resultado.modified_count} produto(s) alterado(s).")


def remover(db):
    mycol = db.produtos
    mydoc = buscar(db, "Nome do produto a ser deletado: ")
    if mydoc is None:
        return

    print("\nProduto encontrado: ")
    mostrar(mydoc)
    if not ui.confirmar("Confirma a exclusão"):
        print("Exclusão cancelada.")
        return

    resultado = mycol.delete_one({"_id": mydoc["_id"]})
    print(f"{resultado.deleted_count} produto(s) deletado(s).")


def buscar(db, pergunta="Nome do produto: "):
    # procura pelo nome e deixa escolher quando vem mais de um
    nome = ui.ler(pergunta)
    docs = list(db.produtos.find({"nome": {"$regex": nome, "$options": "i"}}).sort("nome"))

    if not docs:
        print("Nenhum produto encontrado.")
        return None

    return ui.escolher([(f"{d['nome']} - R$ {d['preco_unitario']}", d) for d in docs])


def escolher_vendedor(db):
    usuario = usuarios.buscar(db, "CPF do vendedor: ")
    if usuario is None:
        return None

    if "vendedor" not in usuario:
        print("Esse usuário não é vendedor.")
        return None

    return {"usu_id": usuario["_id"], "nome_loja": usuario["vendedor"]["nome_loja"]}


def ler_imagens():
    # lista de nomes de arquivo
    imagens = []
    while True:
        imagem = ui.ler("Nome do arquivo de imagem (vazio encerra): ", obrigatorio=False)
        if imagem is None:
            return imagens
        imagens.append(imagem)


def mostrar(doc):
    # imprime o documento de um jeito legível no terminal
    situacao = "ativo" if doc.get("ativo") else "inativo"
    print(f"\n  {doc.get('nome')} | R$ {doc.get('preco_unitario')} | {situacao}")
    print(f"  _id: {doc.get('_id')}")
    print(f"  {doc.get('descricao')} | estoque: {doc.get('quantidade_estoque')}")

    vendedor = doc.get("vendedor")
    if vendedor:
        print(f"  vendedor: {vendedor.get('nome_loja')}")

    imagens = doc.get("imagens")
    if imagens:
        print(f"  imagens: {', '.join(imagens)}")
