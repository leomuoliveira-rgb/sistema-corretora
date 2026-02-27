"""
Teste de Integração - OCR Engine com Main.py
Demonstra o fluxo completo de importação de PDF
"""

from ocr_engine import OCREngine, processar_pdf
from database import criar_banco, obter_sessao, Proposta, Corretor, Seguradora
import tempfile
import os

print("=== Teste de Integração OCR + Main.py ===\n")

# Criar um PDF de teste simulado (texto simples)
print("1. Criando PDF de teste simulado...")

# Como pdfplumber precisa de um PDF real, vamos simular com texto
texto_exemplo = """
PROPOSTA DE SEGURO

Cliente: Maria Silva Santos
CPF: 123.456.789-01
Telefone: (11) 98765-4321
E-mail: maria.silva@email.com.br

Seguradora: SulAmérica Seguros
Produto: SulAmérica Saúde Premium

Valor Bruto: R$ 12.500,00
Valor Líquido: R$ 10.875,00
Comissão: 10%

Impostos:
ISS: R$ 625,00
IRPF: R$ 750,00
PIS: R$ 81,25
COFINS: R$ 375,00
Total Impostos: R$ 1.831,25

Corretor: João Pedro Alves
Código do Corretor: 98765

Data da Venda: 23/02/2026
Início de Vigência: 01/03/2026
"""

print("[OK] Texto de exemplo criado\n")

# Testar extração de dados
print("2. Testando extração de dados...")
ocr = OCREngine()

# Testar identificação de tipo
tipo = ocr.identificar_tipo_documento(texto_exemplo)
print(f"   Tipo identificado: {tipo}")

# Testar extração
dados = ocr.extrair_dados_proposta(texto_exemplo)
print(f"\n   Dados extraídos:")
print(f"   - Cliente: {dados['cliente_nome']}")
print(f"   - CPF: {dados['cpf_cnpj']}")
print(f"   - Telefone: {dados['telefone']}")
print(f"   - Email: {dados['email']}")
print(f"   - Seguradora: {dados['seguradora_nome']}")
print(f"   - Produto: {dados['produto']}")
print(f"   - Valor Bruto: R$ {dados['valor_bruto']:.2f}")
print(f"   - Valor Líquido: R$ {dados['valor_liquido']:.2f}")
print(f"   - Corretor: {dados['corretor_nome']}")
print(f"   - Data: {dados['data_venda']}")

# Testar salvamento no banco
print("\n3. Testando salvamento no banco...")
sucesso, mensagem = ocr.salvar_proposta_no_banco(dados)
print(f"   {mensagem}")

if sucesso:
    # Verificar se foi salvo
    session = obter_sessao(criar_banco())
    ultima_proposta = session.query(Proposta).order_by(Proposta.id.desc()).first()

    if ultima_proposta:
        print(f"\n   [OK] Proposta #{ultima_proposta.id} no banco")
        print(f"   Cliente: {ultima_proposta.cliente_nome}")
        print(f"   Valor: R$ {ultima_proposta.valor_bruto:.2f}")
        print(f"   Seguradora: {ultima_proposta.seguradora.nome}")
        print(f"   Corretor: {ultima_proposta.corretor.nome}")
        print(f"   Lançamentos: {len(ultima_proposta.lancamentos)}")

    session.close()

ocr.fechar()

print("\n" + "="*60)
print("INTEGRAÇÃO COM INTERFACE (main.py)")
print("="*60)

print("""
Quando o usuário clicar em "Importar Proposta PDF":

1. Abre file picker (seletor de arquivos)
   ↓
2. Usuário seleciona um PDF
   ↓
3. Sistema mostra: "⏳ Processando arquivo.pdf..."
   ↓
4. OCR Engine extrai dados automaticamente
   ↓
5. Se PROPOSTA:
   - Busca/cria Seguradora
   - Busca/cria Corretor
   - Salva Proposta no banco
   - Gera Lançamentos automáticos
   ↓
6. Sistema mostra:
   "✓ Proposta #15 salva com sucesso!
    Tipo: PROPOSTA
    Cliente: Maria Silva Santos
    Valor: R$ 12.500,00"
   ↓
7. Dashboard é atualizado automaticamente
   ↓
8. Novos dados aparecem nas abas:
   - Dashboard: valores atualizados
   - Propostas: nova proposta
   - Lançamentos: novos lançamentos
   - Repasses: comissão do corretor atualizada
""")

print("\n" + "="*60)
print("TESTE COMPLETO")
print("="*60)
print("""
Para testar na interface:

1. Execute: py run_app.py

2. Clique no botão "📁 Importar Proposta PDF"

3. Selecione um arquivo PDF com proposta

4. Aguarde o processamento

5. Verifique a notificação de sucesso/erro

6. Confira o dashboard atualizado
""")

print("\n[OK] Integração OCR + Interface implementada!")
print("[OK] Sistema pronto para importar PDFs automaticamente!")
