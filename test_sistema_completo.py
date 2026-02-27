"""
Teste Completo do Sistema
Testa todos os componentes e identifica erros
"""

import sys
import traceback
from datetime import datetime, timedelta

print("="*70)
print("TESTE COMPLETO DO SISTEMA FINANCEIRO DE CORRETORA")
print("="*70)
print()

# Contador de testes
testes_passados = 0
testes_falhados = 0
erros = []

def testar(nome, funcao):
    """Executa um teste e registra resultado"""
    global testes_passados, testes_falhados, erros

    print(f"[TESTANDO] {nome}...", end=" ")
    try:
        funcao()
        print("[OK]")
        testes_passados += 1
        return True
    except Exception as e:
        print(f"[FALHOU]")
        print(f"  Erro: {str(e)}")
        testes_falhados += 1
        erros.append({
            'teste': nome,
            'erro': str(e),
            'traceback': traceback.format_exc()
        })
        return False

print("FASE 1: TESTES DE IMPORTAÇÃO")
print("-"*70)

def test_import_database():
    from database import criar_banco, obter_sessao, Proposta, Corretor, Seguradora, Lancamento, Configuracao
    assert criar_banco is not None
    assert obter_sessao is not None

def test_import_config_manager():
    from config_manager import ConfigManager
    assert ConfigManager is not None

def test_import_finance_engine():
    from finance_engine import FinanceEngine
    assert FinanceEngine is not None

def test_import_ocr_engine():
    from ocr_engine import OCREngine, processar_pdf
    assert OCREngine is not None
    assert processar_pdf is not None

def test_import_tax_manager():
    from tax_manager import TaxCalculator, calcular_liquido
    assert TaxCalculator is not None
    assert calcular_liquido is not None

def test_import_bot_integrator():
    from bot_integrator import ClawdBot, notificar_proposta, notificar_pagamento
    assert ClawdBot is not None

testar("Importar Database", test_import_database)
testar("Importar Config Manager", test_import_config_manager)
testar("Importar Finance Engine", test_import_finance_engine)
testar("Importar OCR Engine", test_import_ocr_engine)
testar("Importar Tax Manager", test_import_tax_manager)
testar("Importar Bot Integrator", test_import_bot_integrator)

print()
print("FASE 2: TESTES DE BANCO DE DADOS")
print("-"*70)

def test_criar_banco():
    from database import criar_banco, obter_sessao
    engine = criar_banco()
    session = obter_sessao(engine)
    assert session is not None
    session.close()

def test_criar_configuracao():
    from database import criar_banco, obter_sessao, Configuracao
    engine = criar_banco()
    session = obter_sessao(engine)

    config = Configuracao(chave="TESTE", valor="123")
    session.add(config)
    session.commit()

    resultado = session.query(Configuracao).filter_by(chave="TESTE").first()
    assert resultado is not None
    assert resultado.valor == "123"

    session.delete(resultado)
    session.commit()
    session.close()

def test_relacionamentos():
    from database import criar_banco, obter_sessao, Proposta, Corretor, Seguradora
    engine = criar_banco()
    session = obter_sessao(engine)

    # Buscar proposta existente
    proposta = session.query(Proposta).first()
    if proposta:
        assert proposta.corretor is not None
        assert proposta.seguradora is not None
        assert len(proposta.lancamentos) >= 0

    session.close()

testar("Criar Banco de Dados", test_criar_banco)
testar("Criar Configuração", test_criar_configuracao)
testar("Testar Relacionamentos", test_relacionamentos)

print()
print("FASE 3: TESTES DE CONFIG MANAGER")
print("-"*70)

def test_config_manager_get():
    from config_manager import ConfigManager
    config = ConfigManager()

    iss = config.get_imposto('ISS')
    assert isinstance(iss, (int, float))
    assert iss >= 0

    config.fechar()

def test_config_manager_set():
    from config_manager import ConfigManager
    config = ConfigManager()

    config.set_imposto('TESTE_CONFIG', 10.5)
    valor = config.get_imposto('TESTE_CONFIG')
    assert valor == 10.5

    config.remover_imposto('TESTE_CONFIG')
    config.fechar()

def test_config_manager_list():
    from config_manager import ConfigManager
    config = ConfigManager()

    impostos = config.listar_impostos()
    assert isinstance(impostos, dict)
    assert len(impostos) > 0

    config.fechar()

testar("Config Manager - Get", test_config_manager_get)
testar("Config Manager - Set", test_config_manager_set)
testar("Config Manager - List", test_config_manager_list)

print()
print("FASE 4: TESTES DE TAX MANAGER")
print("-"*70)

def test_tax_calculator():
    from tax_manager import TaxCalculator
    calc = TaxCalculator()

    resultado = calc.calcular_liquido(10000.00)
    assert 'valor_bruto' in resultado
    assert 'valor_liquido' in resultado
    assert 'total_impostos' in resultado
    assert resultado['valor_bruto'] == 10000.00
    assert resultado['valor_liquido'] < resultado['valor_bruto']

    calc.fechar()

def test_calcular_liquido_function():
    from tax_manager import calcular_liquido

    resultado = calcular_liquido(5000.00)
    assert resultado['valor_bruto'] == 5000.00
    assert resultado['valor_liquido'] > 0

def test_impostos_ativos():
    from tax_manager import TaxCalculator
    calc = TaxCalculator()

    impostos = calc.obter_impostos_ativos()
    assert isinstance(impostos, dict)
    # Deve ter pelo menos alguns impostos ativos
    assert len(impostos) > 0

    calc.fechar()

testar("Tax Calculator - Calcular Líquido", test_tax_calculator)
testar("Função calcular_liquido", test_calcular_liquido_function)
testar("Impostos Ativos", test_impostos_ativos)

print()
print("FASE 5: TESTES DE FINANCE ENGINE")
print("-"*70)

def test_finance_engine_init():
    from finance_engine import FinanceEngine
    from database import criar_banco, obter_sessao

    engine = criar_banco()
    session = obter_sessao(engine)
    finance = FinanceEngine(session=session)

    assert finance is not None
    finance.fechar()
    session.close()

def test_finance_calcular_impostos():
    from finance_engine import FinanceEngine

    finance = FinanceEngine()
    liquido, detalhes = finance.calcular_impostos(1000.00)

    assert liquido < 1000.00
    assert 'total_impostos' in detalhes
    assert detalhes['total_impostos'] > 0

    finance.fechar()

def test_finance_parsear_regra():
    from finance_engine import FinanceEngine

    finance = FinanceEngine()

    dias1 = finance.parsear_regra_pagamento("30")
    assert dias1 == [30]

    dias2 = finance.parsear_regra_pagamento("7/30/60")
    assert dias2 == [7, 30, 60]

    finance.fechar()

testar("Finance Engine - Init", test_finance_engine_init)
testar("Finance Engine - Calcular Impostos", test_finance_calcular_impostos)
testar("Finance Engine - Parsear Regra", test_finance_parsear_regra)

print()
print("FASE 6: TESTES DE OCR ENGINE")
print("-"*70)

def test_ocr_config():
    from ocr_engine import OCRConfig

    config = OCRConfig()
    assert config.patterns is not None
    assert 'cliente' in config.patterns
    assert 'valores' in config.patterns

def test_ocr_converter_valor():
    from ocr_engine import OCREngine

    ocr = OCREngine()

    valor1 = ocr.converter_valor_brasileiro("1.234,56")
    assert valor1 == 1234.56

    valor2 = ocr.converter_valor_brasileiro("10.000,00")
    assert valor2 == 10000.00

    ocr.fechar()

def test_ocr_identificar_tipo():
    from ocr_engine import OCREngine

    ocr = OCREngine()

    texto_proposta = "PROPOSTA DE SEGURO\nCliente: João"
    tipo1 = ocr.identificar_tipo_documento(texto_proposta)
    assert tipo1 == 'PROPOSTA'

    texto_relatorio = "RELATÓRIO DE PAGAMENTO\nValor: 1000"
    tipo2 = ocr.identificar_tipo_documento(texto_relatorio)
    assert tipo2 == 'RELATORIO'

    ocr.fechar()

testar("OCR Config", test_ocr_config)
testar("OCR - Converter Valor", test_ocr_converter_valor)
testar("OCR - Identificar Tipo", test_ocr_identificar_tipo)

print()
print("FASE 7: TESTES DE BOT INTEGRATOR")
print("-"*70)

def test_webhook_config():
    from bot_integrator import WebhookConfig

    config = WebhookConfig()
    assert config.config is not None
    assert 'webhooks' in config.config
    assert 'templates' in config.config

def test_clawdbot_init():
    from bot_integrator import ClawdBot

    bot = ClawdBot()
    assert bot is not None
    assert bot.webhook_url is not None

def test_payload_structure():
    from bot_integrator import ClawdBot
    from database import criar_banco, obter_sessao, Proposta

    engine = criar_banco()
    session = obter_sessao(engine)

    proposta = session.query(Proposta).first()
    if proposta:
        bot = ClawdBot()
        # Apenas testar estrutura, não enviar
        assert bot.config is not None

    session.close()

testar("Webhook Config", test_webhook_config)
testar("ClawdBot Init", test_clawdbot_init)
testar("Payload Structure", test_payload_structure)

print()
print("FASE 8: TESTES DE INTEGRAÇÃO")
print("-"*70)

def test_integracao_tax_finance():
    """Testa integração entre Tax Manager e Finance Engine"""
    from tax_manager import calcular_liquido
    from finance_engine import FinanceEngine

    # Calcular com Tax Manager
    resultado_tax = calcular_liquido(10000.00)

    # Calcular com Finance Engine
    finance = FinanceEngine()
    comissao_bruta = 10000.00 * 0.10
    liquido_finance, _ = finance.calcular_impostos(comissao_bruta)

    # Ambos devem descontar impostos
    assert resultado_tax['valor_liquido'] < 10000.00
    assert liquido_finance < comissao_bruta

    finance.fechar()

def test_integracao_ocr_finance():
    """Testa integração entre OCR e Finance Engine"""
    from ocr_engine import OCREngine
    from finance_engine import FinanceEngine

    ocr = OCREngine()
    finance = FinanceEngine()

    # Simular extração
    texto = "Valor Bruto: R$ 15.000,00"
    valor = ocr.converter_valor_brasileiro("15.000,00")

    # Calcular impostos
    liquido, _ = finance.calcular_impostos(valor)

    assert valor == 15000.00
    assert liquido < valor

    ocr.fechar()
    finance.fechar()

def test_fluxo_completo():
    """Testa fluxo completo: Proposta -> Lançamentos -> Impostos"""
    from database import criar_banco, obter_sessao, Proposta
    from finance_engine import FinanceEngine
    from tax_manager import calcular_liquido

    engine = criar_banco()
    session = obter_sessao(engine)

    proposta = session.query(Proposta).first()
    if proposta:
        # 1. Calcular impostos da corretora
        resultado_impostos = calcular_liquido(proposta.valor_bruto)

        # 2. Calcular comissão sobre líquido
        finance = FinanceEngine(session=session)
        relatorio = finance.obter_relatorio_proposta(proposta.id)

        assert 'comissao_liquido' in relatorio
        assert relatorio['comissao_liquido'] > 0

        finance.fechar()

    session.close()

testar("Integração Tax + Finance", test_integracao_tax_finance)
testar("Integração OCR + Finance", test_integracao_ocr_finance)
testar("Fluxo Completo", test_fluxo_completo)

print()
print("="*70)
print("RESUMO DOS TESTES")
print("="*70)
print()
print(f"Total de Testes: {testes_passados + testes_falhados}")
print(f"[+] Testes Passados: {testes_passados}")
print(f"[-] Testes Falhados: {testes_falhados}")
print()

if testes_falhados > 0:
    print("ERROS ENCONTRADOS:")
    print("-"*70)
    for i, erro in enumerate(erros, 1):
        print(f"\n{i}. {erro['teste']}")
        print(f"   Erro: {erro['erro']}")
        if '--verbose' in sys.argv:
            print(f"\n   Traceback:")
            print(f"   {erro['traceback']}")
    print()
    print("Execute com --verbose para ver tracebacks completos")
    print()
    sys.exit(1)
else:
    print("*** TODOS OS TESTES PASSARAM! ***")
    print()
    print("Sistema 100% funcional e pronto para uso!")
    print()
    sys.exit(0)
