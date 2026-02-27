"""
Teste completo do database.py
Cria dados de exemplo e testa relacionamentos
"""

from database import *
from datetime import datetime, timedelta

# Criar banco e sessão
print("=== Teste Completo do Sistema de Banco de Dados ===\n")
engine = criar_banco()
session = obter_sessao(engine)

print("1. Criando Seguradoras...")
seg1 = Seguradora(nome="Porto Seguro", regra_pagamento_dias=30, vitalicio_porcentagem=5.0)
seg2 = Seguradora(nome="Bradesco Seguros", regra_pagamento_dias=45, vitalicio_porcentagem=7.5)
session.add_all([seg1, seg2])
session.commit()
print(f"   [OK] {seg1}")
print(f"   [OK] {seg2}")

print("\n2. Criando Corretores...")
cor1 = Corretor(nome="João Silva", comissao_padrao=10.0)
cor2 = Corretor(nome="Maria Santos", comissao_padrao=12.5)
session.add_all([cor1, cor2])
session.commit()
print(f"   [OK]{cor1}")
print(f"   [OK]{cor2}")

print("\n3. Criando Propostas...")
prop1 = Proposta(
    cliente_nome="Carlos Oliveira",
    valor_bruto=5000.00,
    seguradora_id=seg1.id,
    corretor_id=cor1.id,
    data_venda=datetime.now().date()
)
prop2 = Proposta(
    cliente_nome="Ana Costa",
    valor_bruto=8000.00,
    seguradora_id=seg2.id,
    corretor_id=cor2.id,
    data_venda=datetime.now().date()
)
session.add_all([prop1, prop2])
session.commit()
print(f"   [OK]{prop1}")
print(f"   [OK]{prop2}")

print("\n4. Criando Lançamentos...")
# Lançamentos para proposta 1
lanc1 = Lancamento(
    proposta_id=prop1.id,
    data_vencimento=datetime.now().date() + timedelta(days=30),
    valor_esperado=500.00,
    status_pago=False
)
lanc2 = Lancamento(
    proposta_id=prop1.id,
    data_vencimento=datetime.now().date() + timedelta(days=60),
    valor_esperado=500.00,
    status_pago=False
)
# Lançamento para proposta 2
lanc3 = Lancamento(
    proposta_id=prop2.id,
    data_vencimento=datetime.now().date() + timedelta(days=45),
    valor_esperado=1000.00,
    status_pago=True
)
session.add_all([lanc1, lanc2, lanc3])
session.commit()
print(f"   [OK]{lanc1}")
print(f"   [OK]{lanc2}")
print(f"   [OK]{lanc3}")

print("\n5. Testando Relacionamentos...")
# Buscar proposta e ver dados relacionados
proposta = session.query(Proposta).filter_by(cliente_nome="Carlos Oliveira").first()
print(f"\n   Proposta: {proposta.cliente_nome}")
print(f"   Valor: R$ {proposta.valor_bruto:.2f}")
print(f"   Seguradora: {proposta.seguradora.nome}")
print(f"   Corretor: {proposta.corretor.nome}")
print(f"   Comissão: {proposta.corretor.comissao_padrao}%")
print(f"   Número de lançamentos: {len(proposta.lancamentos)}")

print("\n6. Consultando Todos os Lançamentos Pendentes...")
lancamentos_pendentes = session.query(Lancamento).filter_by(status_pago=False).all()
total_pendente = sum(l.valor_esperado for l in lancamentos_pendentes)
print(f"   Total de lançamentos pendentes: {len(lancamentos_pendentes)}")
print(f"   Valor total pendente: R$ {total_pendente:.2f}")

print("\n7. Estatísticas Gerais...")
print(f"   Total de Seguradoras: {session.query(Seguradora).count()}")
print(f"   Total de Corretores: {session.query(Corretor).count()}")
print(f"   Total de Propostas: {session.query(Proposta).count()}")
print(f"   Total de Lançamentos: {session.query(Lancamento).count()}")

# Calcular valor total em propostas
total_propostas = session.query(Proposta).all()
valor_total = sum(p.valor_bruto for p in total_propostas)
print(f"   Valor total em propostas: R$ {valor_total:.2f}")

session.close()
print("\n[OK] Todos os testes concluidos com sucesso!")
print("[OK] Banco de dados 'corretora.db' criado e populado!")
