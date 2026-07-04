


def imc(peso, altura):
    return peso/(altura ** 2)

def calculo_sal_hora(carga, salario):
    return salario /carga

def calculo_quantidade_extra50(quantidade, sal_hora):
    extra = sal_hora * 1.5
    q = quantidade * extra
    return q

def salario_total(extra, salario):
    return extra + salario


