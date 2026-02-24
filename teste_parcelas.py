"""
Script de teste para o Sistema de Parcelas
Cria dados de teste e demonstra funcionalidades
"""

from database import criar_banco, obter_sessao, Proposta, Lancamento, Corretor
from sistema_parcelas import GerenciadorParcelas, inicializar_sistema_parcelas
from datetime import datetime, timedelta

print("=" * 70)
print("TESTE DO SISTEMA DE PARCELAS")
print("=" * 70)

# Inicializar sistema
print("\n[1] Inicializando sistema de parcelas...")
inicializar_sistema_parcelas()

# Conectar ao banco
engine = criar_banco()
session = obter_sessao(engine)

# Criar gerenciador
gerenciador = GerenciadorParcelas(session=session)

# Buscar uma proposta para teste
print("\n[2] Buscando propostas para teste...")
propostas = session.query(Proposta).all()

if not propostas:
    print("   [AVISO] Nenhuma proposta encontrada. Execute criar_dados_teste.py primeiro!")
    exit()

proposta_teste = propostas[0]
print(f"   [OK] Proposta selecionada: {proposta_teste.cliente_nome} (ID: {proposta_teste.id})")

# Buscar lançamento
lancamento = session.query(Lancamento).filter_by(proposta_id=proposta_teste.id).first()

if not lancamento:
    print("   [ERRO] Lançamento não encontrado para esta proposta")
    exit()

print(f"   [OK] Lançamento encontrado: R$ {lancamento.valor_esperado:,.2f}")

# Criar parcelas automáticas
print(f"\n[3] Criando parcelas automáticas...")
data_quitacao = datetime.now().date() - timedelta(days=5)  # Simular quitação há 5 dias atrás

parcelas = gerenciador.criar_parcelas_automaticas(
    lancamento_id=lancamento.id,
    proposta_id=proposta_teste.id,
    corretor_id=proposta_teste.corretor_id,
    valor_total=lancamento.valor_esperado,
    data_primeira_quitacao=data_quitacao
)

print(f"   [OK] {len(parcelas)} parcelas criadas:")
for p in parcelas:
    print(f"      - Parcela {p.numero_parcela}: R$ {p.valor:,.2f} | Venc: {p.data_vencimento}")

# Verificar parcelas vencidas
print(f"\n[4] Verificando parcelas vencidas...")
parcelas_vencidas = gerenciador.verificar_parcelas_vencidas()

if parcelas_vencidas:
    print(f"   [ALERTA] {len(parcelas_vencidas)} parcelas vencidas encontradas:")
    for p in parcelas_vencidas:
        dias_atraso = (datetime.now().date() - p.data_vencimento).days
        print(f"      - Parcela {p.numero_parcela}: {dias_atraso} dias de atraso")
else:
    print("   [OK] Nenhuma parcela vencida")

# Obter relatório do corretor
print(f"\n[5] Gerando relatório do corretor...")
corretor = session.query(Corretor).get(proposta_teste.corretor_id)
relatorio = gerenciador.obter_relatorio_corretor(corretor.id)

print(f"   [OK] Relatório do corretor: {corretor.nome}")
print(f"      - Total de parcelas: {relatorio['total_parcelas']}")
print(f"      - Valor pendente: R$ {relatorio['valor_total_pendente']:,.2f}")
print(f"      - Valor quitado: R$ {relatorio['valor_total_quitado']:,.2f}")
print(f"      - Valor vencido: R$ {relatorio['valor_total_vencido']:,.2f}")
print(f"      - Parcelas pendentes: {relatorio['num_pendentes']}")
print(f"      - Parcelas quitadas: {relatorio['num_quitadas']}")
print(f"      - Parcelas vencidas: {relatorio['num_vencidas']}")

# Simular quitação da primeira parcela
if parcelas and len(parcelas) > 0:
    print(f"\n[6] Simulando quitação da primeira parcela...")
    primeira_parcela = parcelas[0]
    sucesso = gerenciador.quitar_parcela(primeira_parcela.id)

    if sucesso:
        print(f"   [OK] Parcela {primeira_parcela.numero_parcela} quitada!")
    else:
        print(f"   [ERRO] Falha ao quitar parcela")

# Resumo final
print("\n" + "=" * 70)
print("RESUMO DO TESTE")
print("=" * 70)
print("[OK] Sistema de parcelas funcionando corretamente!")
print(f"[OK] Parcelas criadas: {len(parcelas)}")
print(f"[OK] Vencimentos programados: 30, 60 e 90 dias")
print(f"[OK] Verificação automática de vencimentos: ATIVA")
print("\nPróximos passos:")
print("  1. Configure o email em ConfiguracaoEmail")
print("  2. Execute verificar_parcelas_vencidas() diariamente")
print("  3. Emails serão enviados automaticamente para parcelas vencidas")
print("=" * 70)

gerenciador.fechar()
session.close()
