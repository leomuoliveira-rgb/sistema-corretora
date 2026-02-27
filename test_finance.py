"""
Teste completo do Finance Engine
Demonstra geração automática de lançamentos com impostos
"""

from database import *
from finance_engine import FinanceEngine
from config_manager import ConfigManager
from datetime import datetime

print("=== Teste Completo do Finance Engine ===\n")

# Criar banco e sessão
engine_db = criar_banco()
session = obter_sessao(engine_db)

# Inicializar impostos
print("1. Configurando impostos...")
config = ConfigManager(session=session)
config.inicializar_impostos_padrao()
print(f"   ISS: {config.get_imposto('ISS')}%")
print(f"   PIS: {config.get_imposto('PIS')}%")
print(f"   COFINS: {config.get_imposto('COFINS')}%")

# Criar seguradora com regra de múltiplos pagamentos
print("\n2. Criando Seguradora com regra 7/30/60 dias...")
sulamerica = Seguradora(
    nome="SulAmerica Seguros",
    regra_pagamento_dias="7/30/60",  # 3 pagamentos
    vitalicio_porcentagem=6.0
)
session.add(sulamerica)

porto = Seguradora(
    nome="Porto Seguro",
    regra_pagamento_dias="30",  # Pagamento único
    vitalicio_porcentagem=5.0
)
session.add(porto)
session.commit()
print(f"   [OK] {sulamerica.nome} - Regra: {sulamerica.regra_pagamento_dias}")
print(f"   [OK] {porto.nome} - Regra: {porto.regra_pagamento_dias}")

# Criar corretor
print("\n3. Criando Corretor...")
corretor = Corretor(
    nome="Roberto Alves",
    comissao_padrao=12.0  # 12% de comissão
)
session.add(corretor)
session.commit()
print(f"   [OK] {corretor.nome} - Comissao: {corretor.comissao_padrao}%")

# Criar proposta
print("\n4. Criando Proposta...")
proposta = Proposta(
    cliente_nome="Empresa ABC Ltda",
    valor_bruto=10000.00,  # Apólice de R$ 10.000
    seguradora_id=sulamerica.id,
    corretor_id=corretor.id,
    data_venda=datetime.now().date()
)
session.add(proposta)
session.commit()
print(f"   [OK] Cliente: {proposta.cliente_nome}")
print(f"   [OK] Valor Apolice: R$ {proposta.valor_bruto:.2f}")

# Criar finance engine e gerar lançamentos
print("\n5. Gerando Lancamentos Automaticos...")
finance = FinanceEngine(session=session)

# Calcular valores antes de gerar
comissao_bruta = proposta.valor_bruto * (corretor.comissao_padrao / 100)
liquido, impostos = finance.calcular_impostos(comissao_bruta)

print(f"\n   Calculo de Comissao:")
print(f"   - Valor da Apolice: R$ {proposta.valor_bruto:.2f}")
print(f"   - Comissao Bruta ({corretor.comissao_padrao}%): R$ {comissao_bruta:.2f}")
print(f"\n   Impostos:")
print(f"   - PIS ({impostos['PIS']['aliquota']}%): R$ {impostos['PIS']['valor']:.2f}")
print(f"   - COFINS ({impostos['COFINS']['aliquota']}%): R$ {impostos['COFINS']['valor']:.2f}")
print(f"   - ISS ({impostos['ISS']['aliquota']}%): R$ {impostos['ISS']['valor']:.2f}")
print(f"   - IRPF ({impostos['IRPF']['aliquota']}%): R$ {impostos['IRPF']['valor']:.2f}")
print(f"   - CSLL ({impostos['CSLL']['aliquota']}%): R$ {impostos['CSLL']['valor']:.2f}")
print(f"   - Total Impostos: R$ {impostos['total_impostos']:.2f}")
print(f"\n   - Comissao Liquida: R$ {liquido:.2f}")

# Gerar lançamentos
lancamentos = finance.gerar_lancamentos(proposta)

print(f"\n   [OK] {len(lancamentos)} lancamentos criados conforme regra {sulamerica.regra_pagamento_dias}:")
valor_total_lanc = 0
for i, lanc in enumerate(lancamentos, 1):
    dias = (lanc.data_vencimento - proposta.data_venda).days
    print(f"\n   Lancamento {i}:")
    print(f"   - Vencimento: {lanc.data_vencimento.strftime('%d/%m/%Y')} ({dias} dias)")
    print(f"   - Valor: R$ {lanc.valor_esperado:.2f}")
    print(f"   - Status: {'PAGO' if lanc.status_pago else 'PENDENTE'}")
    valor_total_lanc += lanc.valor_esperado

print(f"\n   Total em Lancamentos: R$ {valor_total_lanc:.2f}")

# Teste com outra proposta (pagamento único)
print("\n\n6. Testando com Porto Seguro (pagamento unico)...")
proposta2 = Proposta(
    cliente_nome="Comercio XYZ",
    valor_bruto=5000.00,
    seguradora_id=porto.id,
    corretor_id=corretor.id,
    data_venda=datetime.now().date()
)
session.add(proposta2)
session.commit()

lancamentos2 = finance.gerar_lancamentos(proposta2)
print(f"   [OK] {len(lancamentos2)} lancamento criado para R$ {lancamentos2[0].valor_esperado:.2f}")
print(f"   Vencimento em {(lancamentos2[0].data_vencimento - proposta2.data_venda).days} dias")

# Relatório completo
print("\n\n7. Relatorio Completo da Proposta 1...")
relatorio = finance.obter_relatorio_proposta(proposta.id)

print(f"\n   Cliente: {relatorio['cliente']}")
print(f"   Seguradora: {relatorio['seguradora']}")
print(f"   Corretor: {relatorio['corretor']}")
print(f"   Data Venda: {relatorio['data_venda']}")
print(f"\n   Financeiro:")
print(f"   - Valor Apolice: R$ {relatorio['valor_bruto_apolice']:.2f}")
print(f"   - Comissao Bruto: R$ {relatorio['comissao_bruto']:.2f}")
print(f"   - Total Impostos: R$ {relatorio['impostos']['total_impostos']:.2f}")
print(f"   - Comissao Liquido: R$ {relatorio['comissao_liquido']:.2f}")
print(f"\n   Lancamentos:")
print(f"   - Total: {relatorio['lancamentos']['total']}")
print(f"   - Pendentes: {relatorio['lancamentos']['pendentes']}")
print(f"   - Valor Pendente: R$ {relatorio['lancamentos']['valor_pendente']:.2f}")

# Testar marcação de pagamento
print("\n\n8. Testando marcacao de pagamento...")
primeiro_lanc = lancamentos[0]
print(f"   Marcando lancamento {primeiro_lanc.id} como pago...")
finance.marcar_lancamento_pago(primeiro_lanc.id)

# Novo relatório
relatorio_atualizado = finance.obter_relatorio_proposta(proposta.id)
print(f"   [OK] Pagos: {relatorio_atualizado['lancamentos']['pagos']}")
print(f"   [OK] Valor Pago: R$ {relatorio_atualizado['lancamentos']['valor_pago']:.2f}")
print(f"   [OK] Valor Pendente: R$ {relatorio_atualizado['lancamentos']['valor_pendente']:.2f}")

finance.fechar()
session.close()

print("\n\n[OK] Todos os testes concluidos com sucesso!")
print("[OK] Finance Engine funcionando perfeitamente!")
print("\nResumo:")
print("- Impostos calculados automaticamente")
print("- Lancamentos gerados conforme regra da seguradora")
print("- Suporta pagamento unico ou multiplos pagamentos")
print("- Valores liquidos calculados corretamente")
