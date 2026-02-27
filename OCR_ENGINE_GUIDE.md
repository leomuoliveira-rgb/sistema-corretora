# 📄 Guia do OCR Engine - Extração de Dados de PDFs

## Visão Geral

O **OCR Engine** é um sistema inteligente de extração de dados de documentos PDF usando **pdfplumber** e **expressões regulares (Regex)**. Ele identifica automaticamente o tipo de documento e extrai informações estruturadas.

## 🎯 Funcionalidades

### ✅ Extração Automática de Dados

O sistema extrai automaticamente:

#### 👤 Dados do Cliente
- **Nome do Cliente**
- **CPF/CNPJ**
- **Telefone** (se disponível)
- **E-mail** (se disponível)

#### 🏢 Dados da Seguradora
- **Nome da Seguradora** (SulAmérica, Porto Seguro, Bradesco, etc.)
- **Produto Contratado** (Amil, Bradesco Saúde, etc.)

#### 💰 Valores Financeiros
- **Valor Bruto** (valor total do contrato)
- **Valor Líquido** (valor após descontos)
- **Comissão** (percentual ou valor)

#### 📊 Impostos
- **ISS** (Imposto sobre Serviços)
- **IRPF** (Imposto de Renda)
- **PIS** (Programa de Integração Social)
- **COFINS** (Contribuição para Seguridade Social)
- **Total de Impostos**

#### 👨‍💼 Dados do Corretor
- **Nome do Corretor**
- **Código do Corretor** (se disponível)

#### 📅 Datas
- **Data da Venda**
- **Início de Vigência**
- **Fim de Vigência**

---

## 📦 Instalação

### Dependências:
```bash
py -m pip install pdfplumber
```

### Arquivos Necessários:
- `ocr_engine.py` - Motor principal
- `ocr_config.json` - Configuração de padrões (criado automaticamente)
- `database.py` - Modelos do banco de dados
- `finance_engine.py` - Motor financeiro

---

## 🚀 Como Usar

### 1. Uso Básico (Processar um PDF)

```python
from ocr_engine import processar_pdf

# Processar documento
resultado = processar_pdf('proposta_cliente.pdf')

# Verificar resultado
if resultado['sucesso']:
    print(f"✓ {resultado['mensagem']}")
    print(f"Tipo: {resultado['tipo_documento']}")
    print(f"Cliente: {resultado['dados_extraidos']['cliente_nome']}")
else:
    print(f"✗ Erro: {resultado['mensagem']}")
```

### 2. Uso Avançado (Controle Completo)

```python
from ocr_engine import OCREngine

# Criar instância
ocr = OCREngine()

# Processar documento
resultado = ocr.processar_documento('proposta.pdf')

# Acessar dados extraídos
dados = resultado['dados_extraidos']
print(f"Cliente: {dados['cliente_nome']}")
print(f"CPF/CNPJ: {dados['cpf_cnpj']}")
print(f"Seguradora: {dados['seguradora_nome']}")
print(f"Valor Bruto: R$ {dados['valor_bruto']:.2f}")
print(f"Corretor: {dados['corretor_nome']}")

# Fechar conexão
ocr.fechar()
```

---

## 🔧 Configuração Personalizada

### Arquivo `ocr_config.json`

O sistema usa um arquivo JSON com padrões regex configuráveis:

```json
{
  "cliente": {
    "nome": [
      "(?:Cliente|Segurado|Nome)[:\\s]+([A-ZÁÉÍÓÚ][A-Za-záéíóúàãõâêôç\\s]+?)(?:\\n|CPF|CNPJ)",
      "Nome do Cliente[:\\s]+([^\\n]+)"
    ],
    "cpf_cnpj": [
      "(?:CPF|CNPJ)[:\\s]*(\\d{3}\\.?\\d{3}\\.?\\d{3}-?\\d{2})",
      "(?:CPF|CNPJ)[:\\s]*(\\d{2}\\.?\\d{3}\\.?\\d{3}/?\\d{4}-?\\d{2})"
    ]
  },
  "valores": {
    "valor_bruto": [
      "(?:Valor Bruto|Valor Total)[:\\s]*R?\\$?\\s?([0-9]{1,3}(?:\\.[0-9]{3})*(?:,\\d{2})?)"
    ]
  }
}
```

### Adicionar Novos Padrões

```python
from ocr_engine import OCRConfig

# Carregar configuração
config = OCRConfig()

# Adicionar novo padrão
config.adicionar_pattern(
    categoria='cliente',
    campo='endereco',
    pattern=r"Endereço[:\\s]+([^\\n]+)"
)

# Configuração salva automaticamente
```

---

## 📋 Tipos de Documentos

### 🆕 PROPOSTA

Documentos identificados como proposta:
- Contêm: "PROPOSTA", "PROPOSTA DE SEGURO", "ADESÃO", "CONTRATO"
- **Ação**: Salva automaticamente no banco de dados
- **Gera**: Lançamentos financeiros automáticos

### 📊 RELATÓRIO DE PAGAMENTO

Documentos identificados como relatório:
- Contêm: "RELATÓRIO DE PAGAMENTO", "EXTRATO", "DEMONSTRATIVO"
- **Ação**: Envia para função de auditoria (a ser implementada)
- **Status**: Aguardando auditoria

---

## 🔄 Fluxo de Processamento

```
┌─────────────────┐
│  Arquivo PDF    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  Extrair Texto          │
│  (pdfplumber)           │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Identificar Tipo       │
│  (PROPOSTA/RELATÓRIO)   │
└────────┬────────────────┘
         │
         ├─── PROPOSTA ───►┌──────────────────┐
         │                 │ Extrair Dados    │
         │                 │ (Regex)          │
         │                 └────────┬─────────┘
         │                          │
         │                          ▼
         │                 ┌──────────────────┐
         │                 │ Buscar/Criar     │
         │                 │ Seguradora       │
         │                 └────────┬─────────┘
         │                          │
         │                          ▼
         │                 ┌──────────────────┐
         │                 │ Buscar/Criar     │
         │                 │ Corretor         │
         │                 └────────┬─────────┘
         │                          │
         │                          ▼
         │                 ┌──────────────────┐
         │                 │ Salvar Proposta  │
         │                 │ no Banco         │
         │                 └────────┬─────────┘
         │                          │
         │                          ▼
         │                 ┌──────────────────┐
         │                 │ Gerar Lançamentos│
         │                 │ (FinanceEngine)  │
         │                 └────────┬─────────┘
         │                          │
         │                          ▼
         │                    ✓ Concluído
         │
         └── RELATÓRIO ───►┌──────────────────┐
                           │ Extrair Dados    │
                           └────────┬─────────┘
                                    │
                                    ▼
                           ┌──────────────────┐
                           │ Enviar para      │
                           │ Auditoria        │
                           └────────┬─────────┘
                                    │
                                    ▼
                              ⏱ Aguardando
```

---

## 📊 Exemplo de Resultado

```python
{
    'sucesso': True,
    'tipo_documento': 'PROPOSTA',
    'arquivo': 'proposta_001.pdf',
    'mensagem': 'Proposta #15 salva com sucesso!',
    'dados_extraidos': {
        'cliente_nome': 'Empresa ABC Ltda',
        'cpf_cnpj': '12.345.678/0001-90',
        'telefone': '(11) 98765-4321',
        'email': 'contato@empresaabc.com.br',
        'seguradora_nome': 'SulAmérica',
        'produto': 'SulAmérica Saúde Plano Premium',
        'valor_bruto': 15000.00,
        'valor_liquido': 13500.00,
        'comissao': '10%',
        'corretor_nome': 'Roberto Alves',
        'corretor_codigo': '12345',
        'data_venda': datetime.date(2026, 2, 23),
        'impostos': {
            'iss': 750.00,
            'irpf': 450.00,
            'pis': 97.50,
            'cofins': 450.00,
            'total': 1747.50
        }
    }
}
```

---

## 🎨 Estrutura de Classes

### `OCRConfig`
Gerencia configuração de padrões regex.

**Métodos:**
- `carregar_configuracao()` - Carrega padrões do JSON
- `salvar_configuracao()` - Salva padrões no JSON
- `adicionar_pattern(categoria, campo, pattern)` - Adiciona novo padrão

### `OCREngine`
Motor principal de extração.

**Métodos:**
- `extrair_texto_pdf(file_path)` - Extrai texto do PDF
- `identificar_tipo_documento(texto)` - Identifica PROPOSTA/RELATÓRIO
- `extrair_dados_proposta(texto)` - Extrai dados estruturados
- `salvar_proposta_no_banco(dados)` - Salva no banco de dados
- `processar_documento(file_path)` - **Função principal**
- `fechar()` - Fecha conexões

---

## 🔍 Padrões Regex Implementados

### Cliente

#### Nome do Cliente
```regex
(?:Cliente|Segurado|Nome)[:\s]+([A-ZÁÉÍÓÚ][A-Za-záéíóúàãõâêôç\s]+?)(?:\n|CPF|CNPJ)
```
**Busca**: "Cliente: João Silva" → Extrai "João Silva"

#### CPF
```regex
(?:CPF|CNPJ)[:\s]*(\d{3}\.?\d{3}\.?\d{3}-?\d{2})
```
**Busca**: "CPF: 123.456.789-01" → Extrai "123.456.789-01"

#### CNPJ
```regex
(?:CPF|CNPJ)[:\s]*(\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2})
```
**Busca**: "CNPJ: 12.345.678/0001-90" → Extrai "12.345.678/0001-90"

### Valores

#### Valor Bruto
```regex
(?:Valor Bruto|Valor Total)[:\s]*R?\$?\s?([0-9]{1,3}(?:\.[0-9]{3})*(?:,\d{2})?)
```
**Busca**: "Valor Total: R$ 1.234,56" → Extrai "1.234,56"

### Seguradoras

#### Nome da Seguradora
```regex
(SulAm[eé]rica|Porto Seguro|Bradesco|Amil|Unimed|Tokio Marine|Allianz)
```
**Busca**: Texto contendo "SulAmérica" → Extrai "SulAmérica"

---

## 💡 Casos de Uso

### Caso 1: Importação em Massa
```python
from ocr_engine import processar_pdf
import os

# Processar todos os PDFs de uma pasta
pasta = "C:/propostas/"
for arquivo in os.listdir(pasta):
    if arquivo.endswith('.pdf'):
        caminho = os.path.join(pasta, arquivo)
        resultado = processar_pdf(caminho)
        print(f"{arquivo}: {resultado['mensagem']}")
```

### Caso 2: Validação de Dados
```python
from ocr_engine import OCREngine

ocr = OCREngine()
resultado = ocr.processar_documento('proposta.pdf')

# Validar dados extraídos
dados = resultado['dados_extraidos']
if not dados['cliente_nome']:
    print("⚠️ Nome do cliente não encontrado!")
if dados['valor_bruto'] == 0:
    print("⚠️ Valor bruto não encontrado!")

ocr.fechar()
```

### Caso 3: Integração com Interface
```python
def importar_pdf_button_click(file_path):
    """Função chamada ao clicar no botão 'Importar PDF'"""
    from ocr_engine import processar_pdf

    resultado = processar_pdf(file_path)

    if resultado['sucesso']:
        # Mostrar mensagem de sucesso
        show_success(f"✓ {resultado['mensagem']}")
        # Atualizar dashboard
        atualizar_dashboard()
    else:
        # Mostrar erro
        show_error(f"✗ {resultado['mensagem']}")
```

---

## 🛠️ Personalização

### Adicionar Nova Seguradora

```python
from ocr_engine import OCRConfig

config = OCRConfig()

# Adicionar padrão para Allianz
config.adicionar_pattern(
    categoria='seguradora',
    campo='nome',
    pattern=r"(Allianz Seguros)"
)
```

### Adicionar Novo Campo

```python
# Adicionar extração de número da apólice
config.adicionar_pattern(
    categoria='proposta',
    campo='numero_apolice',
    pattern=r"Apólice[:\s]*(\d+)"
)
```

### Modificar Padrões Existentes

Edite diretamente `ocr_config.json`:
```json
{
  "cliente": {
    "nome": [
      "seu-novo-pattern-aqui"
    ]
  }
}
```

---

## 🧪 Testes

### Teste Básico
```bash
py ocr_engine.py
```

### Teste com PDF Real
```python
from ocr_engine import processar_pdf

# Teste com PDF de exemplo
resultado = processar_pdf('exemplo_proposta.pdf')
print(f"Tipo: {resultado['tipo_documento']}")
print(f"Dados: {resultado['dados_extraidos']}")
```

---

## ⚠️ Limitações e Considerações

### ✅ Funciona Bem Com:
- PDFs com texto selecionável
- Documentos bem formatados
- Padrões consistentes

### ⚠️ Pode Ter Dificuldades Com:
- PDFs escaneados (imagens) - requer OCR real (Tesseract)
- Layouts muito variados
- Tabelas complexas
- Texto manuscrito

### 💡 Dicas:
1. **Teste os padrões** com seus PDFs reais
2. **Ajuste os regex** conforme necessário
3. **Valide os dados** extraídos antes de salvar
4. **Use try-except** para erros de processamento

---

## 🔜 Próximas Implementações

### Em Desenvolvimento:
- [ ] Função de auditoria para relatórios
- [ ] OCR real para PDFs escaneados (Tesseract)
- [ ] Extração de tabelas
- [ ] Validação automática de CPF/CNPJ
- [ ] Integração com API de CEP
- [ ] Detecção de idioma
- [ ] Exportação de dados extraídos

### Melhorias Futuras:
- [ ] Machine Learning para melhor identificação
- [ ] Interface gráfica para configuração
- [ ] Relatórios de qualidade de extração
- [ ] Backup automático de PDFs processados

---

## 📞 Integração com Sistema Principal

### No `main.py` (Botão Importar PDF):

```python
def importar_pdf(self, e):
    """Abre o seletor de arquivos para importar PDF"""
    file_picker = ft.FilePicker(on_result=self.on_pdf_selected)
    self.page.overlay.append(file_picker)
    self.page.update()

    file_picker.pick_files(
        allowed_extensions=["pdf"],
        dialog_title="Selecione a Proposta em PDF",
    )

def on_pdf_selected(self, e: ft.FilePickerResultEvent):
    """Callback quando um PDF é selecionado"""
    if e.files:
        file_path = e.files[0].path

        # PROCESSAR COM OCR ENGINE
        from ocr_engine import processar_pdf
        resultado = processar_pdf(file_path)

        if resultado['sucesso']:
            self.show_snackbar(
                f"✓ {resultado['mensagem']}",
                self.accent_color
            )
            # Atualizar dashboard
            self.atualizar_dashboard(None)
        else:
            self.show_snackbar(
                f"✗ Erro: {resultado['mensagem']}",
                self.error_color
            )
```

---

**OCR Engine**: Extração inteligente de dados de PDFs com Regex configurável! 🎯
