"""
Verifica se a aplicação está pronta para executar
"""

print("=== Verificação do Sistema ===\n")

# Teste 1: Importações
print("1. Testando importações...")
try:
    import flet as ft
    print("   [OK] Flet importado")
except ImportError as e:
    print(f"   [ERRO] Flet: {e}")
    exit(1)

try:
    from database import *
    print("   [OK] Database importado")
except ImportError as e:
    print(f"   [ERRO] Database: {e}")
    exit(1)

try:
    from config_manager import ConfigManager
    print("   [OK] ConfigManager importado")
except ImportError as e:
    print(f"   [ERRO] ConfigManager: {e}")
    exit(1)

try:
    from finance_engine import FinanceEngine
    print("   [OK] FinanceEngine importado")
except ImportError as e:
    print(f"   [ERRO] FinanceEngine: {e}")
    exit(1)

# Teste 2: Sintaxe do main.py
print("\n2. Verificando sintaxe do main.py...")
try:
    import main
    print("   [OK] main.py sem erros de sintaxe")
except Exception as e:
    print(f"   [ERRO] main.py: {e}")
    exit(1)

# Teste 3: Banco de dados
print("\n3. Testando conexão com banco de dados...")
try:
    engine = criar_banco()
    session = obter_sessao(engine)
    propostas = session.query(Proposta).count()
    lancamentos = session.query(Lancamento).count()
    session.close()
    print(f"   [OK] Banco conectado")
    print(f"   [OK] {propostas} propostas no banco")
    print(f"   [OK] {lancamentos} lancamentos no banco")
except Exception as e:
    print(f"   [ERRO] Banco: {e}")
    exit(1)

# Teste 4: Verificar estrutura da aplicação
print("\n4. Verificando componentes da aplicação...")
try:
    # Verificar se a classe principal existe
    assert hasattr(main, 'CorretoraApp'), "Classe CorretoraApp não encontrada"
    print("   [OK] Classe CorretoraApp encontrada")

    # Verificar método main
    assert hasattr(main, 'main'), "Função main não encontrada"
    print("   [OK] Função main encontrada")

except AssertionError as e:
    print(f"   [ERRO] {e}")
    exit(1)

print("\n" + "="*50)
print("SISTEMA PRONTO PARA USO!")
print("="*50)
print("\nPara executar a aplicação, use:")
print("  py run_app.py")
print("\nOu diretamente:")
print("  py main.py")
print("\n" + "="*50)
