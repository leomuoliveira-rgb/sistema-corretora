"""
Script para criar dados de teste no sistema
"""

from database import criar_banco, obter_sessao, Corretor, Seguradora, Proposta, Usuario
from datetime import datetime, timedelta

print("=" * 60)
print("CRIANDO DADOS DE TESTE")
print("=" * 60)

# Criar banco
engine = criar_banco()
session = obter_sessao(engine)

# Criar corretores
print("\n[1] Criando corretores...")
corretores = []

corretor1 = Corretor(
    nome="Roberto Alves",
    email="roberto@corretora.com",
    telefone="(11) 98765-4321",
    comissao_padrao=10.0
)

corretor2 = Corretor(
    nome="Maria Silva",
    email="maria@corretora.com",
    telefone="(11) 97654-3210",
    comissao_padrao=12.0
)

corretor3 = Corretor(
    nome="João Santos",
    email="joao@corretora.com",
    telefone="(11) 96543-2109",
    comissao_padrao=8.0
)

session.add_all([corretor1, corretor2, corretor3])
session.commit()
print(f"   [OK] {len([corretor1, corretor2, corretor3])} corretores criados")

# Criar seguradoras
print("\n[2] Criando seguradoras...")
seguradoras = []

seg1 = Seguradora(
    nome="SulAmerica Seguros",
    vitalicio_porcentagem=10.0,
    regra_pagamento_dias="30"
)

seg2 = Seguradora(
    nome="Porto Seguro",
    vitalicio_porcentagem=12.0,
    regra_pagamento_dias="7/30/60"
)

seg3 = Seguradora(
    nome="Bradesco Seguros",
    vitalicio_porcentagem=8.5,
    regra_pagamento_dias="45"
)

session.add_all([seg1, seg2, seg3])
session.commit()
print(f"   [OK] {len([seg1, seg2, seg3])} seguradoras criadas")

# Criar propostas
print("\n[3] Criando propostas...")
propostas = []

prop1 = Proposta(
    cliente_nome="João Silva",
    cliente_cpf="123.456.789-01",
    valor_bruto=15000.00,
    seguradora_id=seg1.id,
    corretor_id=corretor1.id,
    data_venda=datetime.now().date() - timedelta(days=10)
)

prop2 = Proposta(
    cliente_nome="Maria Santos",
    cliente_cpf="987.654.321-09",
    valor_bruto=22000.00,
    seguradora_id=seg2.id,
    corretor_id=corretor1.id,
    data_venda=datetime.now().date() - timedelta(days=5)
)

prop3 = Proposta(
    cliente_nome="Carlos Oliveira",
    cliente_cpf="456.789.123-45",
    valor_bruto=8500.00,
    seguradora_id=seg1.id,
    corretor_id=corretor2.id,
    data_venda=datetime.now().date() - timedelta(days=3)
)

prop4 = Proposta(
    cliente_nome="Ana Paula Costa",
    cliente_cpf="321.654.987-12",
    valor_bruto=18000.00,
    seguradora_id=seg3.id,
    corretor_id=corretor2.id,
    data_venda=datetime.now().date() - timedelta(days=1)
)

prop5 = Proposta(
    cliente_nome="Pedro Henrique",
    cliente_cpf="789.123.456-78",
    valor_bruto=12000.00,
    seguradora_id=seg2.id,
    corretor_id=corretor3.id,
    data_venda=datetime.now().date()
)

session.add_all([prop1, prop2, prop3, prop4, prop5])
session.commit()
print(f"   [OK] {len([prop1, prop2, prop3, prop4, prop5])} propostas criadas")

# Gerar lançamentos para cada proposta
print("\n[4] Gerando lançamentos automáticos...")
from finance_engine import FinanceEngine

finance = FinanceEngine(session=session)
total_lancamentos = 0

for proposta in [prop1, prop2, prop3, prop4, prop5]:
    lancamentos = finance.gerar_lancamentos(proposta)
    total_lancamentos += len(lancamentos)
    print(f"   [OK] {len(lancamentos)} lançamentos para proposta #{proposta.id} ({proposta.cliente_nome})")

finance.fechar()

print(f"\n   Total: {total_lancamentos} lançamentos criados")

# Resumo
print("\n" + "=" * 60)
print("RESUMO DOS DADOS CRIADOS")
print("=" * 60)
print(f"[OK] Corretores: 3")
print(f"[OK] Seguradoras: 3")
print(f"[OK] Propostas: 5")
print(f"[OK] Lançamentos: {total_lancamentos}")
print(f"[OK] Valor total em propostas: R$ {sum([p.valor_bruto for p in [prop1, prop2, prop3, prop4, prop5]]):,.2f}")
print("=" * 60)
print("\n[SUCESSO] DADOS DE TESTE CRIADOS COM SUCESSO!")
print("\nAgora você pode:")
print("  1. Acessar a aba 'Repasses'")
print("  2. Clicar em 'Gerar Extrato PDF'")
print("  3. Ver o PDF gerado automaticamente")
print("=" * 60)

session.close()
