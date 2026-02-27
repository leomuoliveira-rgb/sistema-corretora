"""
Script para inicializar dados e executar a aplicação
"""

import sys
from database import *
from config_manager import ConfigManager
from finance_engine import FinanceEngine
from datetime import datetime, timedelta

print("=== Inicializando Sistema ===\n")

# Criar banco
engine = criar_banco()
session = obter_sessao(engine)

# Verificar se já tem dados
propostas_existentes = session.query(Proposta).count()

if propostas_existentes == 0:
    print("Criando dados de exemplo...\n")

    # Configurar impostos
    config = ConfigManager(session=session)
    config.inicializar_impostos_padrao()
    print("[OK] Impostos configurados")

    # Criar seguradoras
    seguradoras = [
        Seguradora(nome="SulAmerica Seguros", regra_pagamento_dias="7/30/60", vitalicio_porcentagem=6.0),
        Seguradora(nome="Porto Seguro", regra_pagamento_dias="30/60/90", vitalicio_porcentagem=5.0),
        Seguradora(nome="Bradesco Seguros", regra_pagamento_dias="15/45", vitalicio_porcentagem=7.5),
        Seguradora(nome="Tokio Marine", regra_pagamento_dias="30", vitalicio_porcentagem=5.5),
    ]
    for seg in seguradoras:
        session.add(seg)
    session.commit()
    print(f"[OK] {len(seguradoras)} seguradoras criadas")

    # Criar corretores
    corretores = [
        Corretor(nome="Roberto Alves", comissao_padrao=12.0),
        Corretor(nome="Maria Silva", comissao_padrao=10.0),
        Corretor(nome="João Santos", comissao_padrao=15.0),
    ]
    for cor in corretores:
        session.add(cor)
    session.commit()
    print(f"[OK] {len(corretores)} corretores criados")

    # Criar propostas
    finance = FinanceEngine(session=session)

    propostas_dados = [
        ("Empresa ABC Ltda", 15000.00, 1, 1, 0),
        ("Comercio XYZ SA", 8000.00, 2, 2, -5),
        ("Industria 123", 25000.00, 1, 3, -10),
        ("Loja Beta", 5000.00, 3, 1, -15),
        ("Construtora Alfa", 12000.00, 2, 2, -20),
        ("Tech Solutions", 18000.00, 4, 3, -7),
        ("Consultoria Plus", 9500.00, 1, 1, -30),
        ("Mercado Central", 6000.00, 3, 2, -45),
    ]

    for cliente, valor, seg_id, cor_id, dias_atras in propostas_dados:
        proposta = Proposta(
            cliente_nome=cliente,
            valor_bruto=valor,
            seguradora_id=seg_id,
            corretor_id=cor_id,
            data_venda=datetime.now().date() + timedelta(days=dias_atras)
        )
        session.add(proposta)
        session.commit()

        # Gerar lançamentos
        finance.gerar_lancamentos(proposta)

    print(f"[OK] {len(propostas_dados)} propostas criadas com lancamentos")

    # Marcar alguns lançamentos como pagos
    lancamentos = session.query(Lancamento).limit(5).all()
    for lanc in lancamentos:
        lanc.status_pago = True
    session.commit()
    print(f"[OK] {len(lancamentos)} lancamentos marcados como pagos")

    print("\n[OK] Dados de exemplo criados com sucesso!\n")
else:
    print(f"[OK] Banco ja possui {propostas_existentes} propostas\n")

session.close()

# Executar aplicação
print("Iniciando interface...\n")
import main
import flet as ft

ft.app(main.main)
