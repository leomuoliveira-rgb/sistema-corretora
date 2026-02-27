"""
Teste da funcionalidade de Repasses
Demonstra cálculos de comissões líquidas por corretor
"""

from database import *
from finance_engine import FinanceEngine
from config_manager import ConfigManager
from datetime import datetime

print("=== Teste de Repasses aos Corretores ===\n")

# Criar banco e sessão
engine = criar_banco()
session = obter_sessao(engine)
finance = FinanceEngine(session=session)

# Listar todos os corretores
corretores = session.query(Corretor).all()

if not corretores:
    print("Nenhum corretor encontrado. Execute run_app.py primeiro.")
    exit()

print(f"Total de corretores cadastrados: {len(corretores)}\n")
print("="*80)

total_geral_liquido = 0
total_geral_bruto = 0
total_geral_impostos = 0

for corretor in corretores:
    print(f"\n{corretor.nome}")
    print("-" * 80)
    print(f"Comissao padrao: {corretor.comissao_padrao}%\n")

    # Buscar propostas do corretor
    propostas = corretor.propostas

    if not propostas:
        print("  Nenhuma proposta cadastrada para este corretor.\n")
        continue

    total_bruto = 0
    total_comissao_bruto = 0
    total_impostos = 0
    total_liquido = 0
    valor_pendente = 0
    valor_pago = 0

    print(f"  Propostas ({len(propostas)}):")
    print("  " + "-" * 76)

    for i, proposta in enumerate(propostas, 1):
        # Calcular comissão
        comissao_bruto = proposta.valor_bruto * (corretor.comissao_padrao / 100)
        liquido, detalhes = finance.calcular_impostos(comissao_bruto)

        total_bruto += proposta.valor_bruto
        total_comissao_bruto += comissao_bruto
        total_impostos += detalhes['total_impostos']
        total_liquido += liquido

        # Lançamentos
        lanc_pendente = sum(l.valor_esperado for l in proposta.lancamentos if not l.status_pago)
        lanc_pago = sum(l.valor_esperado for l in proposta.lancamentos if l.status_pago)

        valor_pendente += lanc_pendente
        valor_pago += lanc_pago

        print(f"  {i}. {proposta.cliente_nome}")
        print(f"     Apolice: R$ {proposta.valor_bruto:.2f}")
        print(f"     Comissao Bruta: R$ {comissao_bruto:.2f} ({corretor.comissao_padrao}%)")
        print(f"     Impostos: R$ {detalhes['total_impostos']:.2f}")
        print(f"     Liquido: R$ {liquido:.2f}")
        print(f"     Lancamentos: Pago R$ {lanc_pago:.2f} | Pendente R$ {lanc_pendente:.2f}")
        print()

    print("  " + "=" * 76)
    print(f"  TOTAIS PARA {corretor.nome.upper()}:")
    print("  " + "=" * 76)
    print(f"  Total em Apolices:          R$ {total_bruto:>12.2f}")
    print(f"  Total Comissao Bruta:       R$ {total_comissao_bruto:>12.2f}")
    print(f"  Total Impostos:             R$ {total_impostos:>12.2f}")
    print(f"  TOTAL LIQUIDO A REPASSAR:   R$ {total_liquido:>12.2f}")
    print()
    print(f"  Valores de Lancamentos:")
    print(f"    - Ja Pagos:               R$ {valor_pago:>12.2f}")
    print(f"    - Pendentes:              R$ {valor_pendente:>12.2f}")
    print("  " + "=" * 76)

    # Acumular totais gerais
    total_geral_liquido += total_liquido
    total_geral_bruto += total_comissao_bruto
    total_geral_impostos += total_impostos

print("\n" + "="*80)
print("RESUMO GERAL - TODOS OS CORRETORES")
print("="*80)
print(f"Total Comissoes Brutas:     R$ {total_geral_bruto:>12.2f}")
print(f"Total Impostos:             R$ {total_geral_impostos:>12.2f}")
print(f"TOTAL LIQUIDO A REPASSAR:   R$ {total_geral_liquido:>12.2f}")
print("="*80)

# Detalhamento de impostos
print("\nDETALHAMENTO DE IMPOSTOS (sobre comissoes):")
print("-" * 80)
config = ConfigManager(session=session)
impostos = config.listar_impostos()
for nome, aliquota in impostos.items():
    valor_imposto = total_geral_bruto * (aliquota / 100)
    print(f"  {nome:.<20} {aliquota:>6.2f}%    R$ {valor_imposto:>12.2f}")
print("-" * 80)
total_calc = sum(total_geral_bruto * (v / 100) for v in impostos.values())
print(f"  {'Total':.<20} {'':>6}      R$ {total_calc:>12.2f}")
print("="*80)

session.close()

print("\n[OK] Teste de repasses concluido!")
print("\nPara visualizar na interface grafica:")
print("  py run_app.py")
print("\nDica: Acesse a aba 'Repasses' para ver os cards dos corretores!")
