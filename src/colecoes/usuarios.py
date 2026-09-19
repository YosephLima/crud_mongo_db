import hashlib
from pymongo.errors import DuplicateKeyError, PyMongoError
import ui
import validacao

# ------------- Usuarios -------------

# Documento (exemplo completo em mocks_mongodb/usuarios.json):
#   nome, email, senha (sha256), cpf,
#   enderecos [ { rua, num, bairro, cidade, estado, cep } ],
#   vendedor { nome_loja, total_vendas }  -> opcional


def menu(db):
    acoes = {
        "1": ("Create Usuário", criar),
        "2": ("Read Usuário", listar),
        "3": ("Update Usuário", atualizar),
        "4": ("Delete Usuário", remover),
    }

    while True:
        print("\n--- Menu do Usuário ---")
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
            print("Já existe um usuário com esse CPF ou email.")
        except PyMongoError as erro:
            print(f"Erro no banco: {erro}")


def criar(db):
    mycol = db.usuarios
    print("\nInserindo um novo usuário")

    nome = ui.ler("Nome Completo: ")
    email = ui.ler("Email: ", validacao.email)
    senha = hashlib.sha256(ui.ler("Senha: ").encode()).hexdigest()
    cpf = ui.ler("CPF: ", validacao.cpf)

    mydoc = {
        "nome": nome,
        "email": email,
        "senha": senha,
        "cpf": cpf,
        "enderecos": ler_enderecos(),
    }

    if ui.confirmar("Ele é vendedor"):
        mydoc["vendedor"] = {
            "nome_loja": ui.ler("Qual é o nome da loja: "),
            "total_vendas": ui.ler("Total de Vendas: ", validacao.quantidade),
        }

    x = mycol.insert_one(mydoc)
    print("Documento inserido com ID ", x.inserted_id)


def listar(db):
    mycol = db.usuarios
    nome = ui.ler("Deseja algum nome específico (vazio lista todos)? ", obrigatorio=False)

    if not nome:
        mydoc = mycol.find().sort("nome")
    else:
        mydoc = mycol.find({"nome": {"$regex": nome, "$options": "i"}}).sort("nome")

    print("\nUsuários existentes: ")
    encontrados = 0
    for x in mydoc:
        mostrar(x)
        encontrados += 1

    if not encontrados:
        print("Nenhum usuário encontrado.")


def atualizar(db):
    mycol = db.usuarios
    mydoc = buscar(db, "CPF do usuário a ser alterado: ")
    if mydoc is None:
        return

    myquery = {"_id": mydoc["_id"]}
    print("\nDados do usuário: ")
    mostrar(mydoc)
    print("(deixe em branco o que não quiser mudar)")

    novos = {}
    nome = ui.ler("Mudar Nome: ", obrigatorio=False)
    if nome:
        novos["nome"] = nome

    email = ui.ler("Mudar Email: ", validacao.email, obrigatorio=False)
    if email:
        novos["email"] = email

    novo_cpf = ui.ler("Mudar CPF: ", validacao.cpf, obrigatorio=False)
    if novo_cpf:
        novos["cpf"] = novo_cpf

    if ui.confirmar("Mudar os endereços"):
        novos["enderecos"] = ler_enderecos()

    if not novos:
        print("Nada foi alterado.")
        return

    resultado = mycol.update_one(myquery, {"$set": novos})
    print(f"{resultado.modified_count} usuário(s) alterado(s).")


def remover(db):
    mycol = db.usuarios
    mydoc = buscar(db, "CPF do usuário a ser deletado: ")
    if mydoc is None:
        return

    myquery = {"_id": mydoc["_id"]}
    print("\nUsuário encontrado: ")
    mostrar(mydoc)
    if not ui.confirmar("Confirma a exclusão"):
        print("Exclusão cancelada.")
        return

    resultado = mycol.delete_one(myquery)
    print(f"{resultado.deleted_count} usuário(s) deletado(s).")


def buscar(db, pergunta="CPF do usuário: "):
    # procura pelo CPF; devolve None quando não existe
    cpf = ui.ler(pergunta, validacao.somente_digitos)
    doc = db.usuarios.find_one({"cpf": cpf})
    if doc is None:
        print("Usuário não encontrado.")
    return doc


def ler_enderecos():
    # lê um ou mais endereços do teclado e devolve a lista
    enderecos = []
    while True:
        endereco = {  # isso nao eh json, isso é chave-valor, eh um obj
            "rua": ui.ler("Rua: "),
            "num": ui.ler("Num: "),
            "bairro": ui.ler("Bairro: "),
            "cidade": ui.ler("Cidade: "),
            "estado": ui.ler("Estado (sigla): ", validacao.estado),
            "cep": ui.ler("CEP: ", validacao.cep),
        }
        enderecos.append(endereco)  # estou inserindo na lista
        if not ui.confirmar("Deseja cadastrar um novo endereço"):
            return enderecos


def mostrar(doc):
    # imprime o documento no terminal
    print(f"\n  {doc.get('nome')} | CPF: {doc.get('cpf')} | {doc.get('email')}")
    print(f"  _id: {doc.get('_id')}")

    for endereco in doc.get("enderecos", []):
        print(
            f"  end: {endereco.get('rua')}, {endereco.get('num')} - "
            f"{endereco.get('bairro')}, {endereco.get('cidade')}/{endereco.get('estado')} "
            f"- CEP {endereco.get('cep')}"
        )

    vendedor = doc.get("vendedor")
    if vendedor:
        print(f"  vendedor: {vendedor.get('nome_loja')} ({vendedor.get('total_vendas')} vendas)")
