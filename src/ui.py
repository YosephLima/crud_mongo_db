import validacao

def ler(pergunta, validador=None, obrigatorio=True):
    while True:
        valor = input(pergunta).strip()

        if not valor:
            if not obrigatorio:
                return None
            print("  ! Campo obrigatório.")
            continue

        if validador is None:
            return valor

        try:
            return validador(valor)
        except ValueError as erro:
            print(f"  ! {erro}")

def confirmar(pergunta):
    return input(f"{pergunta} (S/N)? ").strip().upper() == "S"

def escolher(opcoes):
    if len(opcoes) == 1:
        return opcoes[0][1]

    print()
    for numero, (texto, _) in enumerate(opcoes, 1):
        print(f"  {numero} - {texto}")

    while True:
        escolha = ler("Escolha o número: ", validacao.quantidade)
        if 1 <= escolha <= len(opcoes):
            return opcoes[escolha - 1][1]
        print("  ! Número fora da lista.")
