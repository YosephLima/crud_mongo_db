from decimal import Decimal, InvalidOperation
from bson.decimal128 import Decimal128

def somente_digitos(valor):
    # tira pontuação; serve para buscar por um CPF já cadastrado
    digitos = "".join(c for c in valor if c.isdigit())
    if not digitos:
        raise ValueError("Informe ao menos um dígito.")
    return digitos

def cpf(valor):
    digitos = somente_digitos(valor)
    if len(digitos) != 11:
        raise ValueError("CPF deve ter 11 dígitos.")
    if digitos == digitos[0] * 11:
        raise ValueError("CPF inválido (todos os dígitos iguais).")
    return digitos

def email(valor):
    # precisa ter @ e "." (.com, .com.br e .br passam)
    endereco = valor.lower()

    if "@" not in endereco or "." not in endereco:
        raise ValueError("Email inválido (ex: nome@dominio.com).")

    return endereco

def quantidade(valor):
    # inteiro de zero para cima
    if not valor.isdigit():
        raise ValueError("Informe um número inteiro (zero ou mais).")
    return int(valor)

def quantidade_maior_que_zero(valor):
    numero = quantidade(valor)
    if numero == 0:
        raise ValueError("A quantidade deve ser pelo menos 1.")
    return numero

def quantidade_ate(maximo):
    # devolve um validador que também limita pelo estoque disponível
    def validador(valor):
        numero = quantidade_maior_que_zero(valor)
        if numero > maximo:
            raise ValueError(f"Só existem {maximo} em estoque.")
        return numero
    return validador

def dinheiro(valor):
    try:
        numero = Decimal(valor.replace(",", ".")).quantize(Decimal("0.01"))
    except InvalidOperation:
        raise ValueError("Informe um valor em reais (ex: 4500.00).")

    if numero < 0:
        raise ValueError("O valor não pode ser negativo.")

    return Decimal128(numero)

def estado(valor):
    sigla = valor.upper()
    if len(sigla) != 2 or not sigla.isalpha():
        raise ValueError("Estado deve ser a sigla de 2 letras (ex: SP).")
    return sigla

def cep(valor):
    digitos = somente_digitos(valor)
    if len(digitos) != 8:
        raise ValueError("CEP deve ter 8 dígitos.")
    return f"{digitos[:5]}-{digitos[5:]}"
