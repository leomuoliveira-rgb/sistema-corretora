# Sistema Financeiro de Corretora

Sistema completo de gestão financeira para corretoras de seguros, com interface desktop em Dark Mode, CRM, importação de extratos PDF e cálculo automático de comissões.

## Tecnologias

- **Python 3.11+**
- **Flet** — interface gráfica desktop/web
- **SQLAlchemy + SQLite** — banco de dados
- **pdfplumber** — extração de texto de PDFs
- **ReportLab** — geração de PDFs

---

## Funcionalidades

### Autenticação
- Login com usuário e senha
- Controle de acesso por tipo (`admin`, `corretor`, `corretora`)
- Credenciais padrão: `admin` / `admin123`

### Dashboard
- Cards com previsão de recebimentos (3, 6 e 12 meses)
- Gráfico de barras interativo
- Total pendente e total recebido

### Propostas
- Cadastro completo de propostas (cliente, seguradora, corretor, plano)
- Dados do titular: CPF, RG, data de nascimento, telefone, e-mail
- Dependentes com parentesco, sexo e estado civil
- Geração automática de lançamentos conforme regra da seguradora (ex: `7/30/60`)
- Importação via PDF com OCR (formato genérico e Allcare Benefícios)

### Lançamentos
- Listagem de parcelas com status (pago / pendente)
- Marcação individual ou em lote como pago
- Filtro por período e corretor

### CRM
- Cadastro de leads com origem, produto de interesse e status do funil
- Funil de vendas: `NOVO → CONTATO → QUALIFICADO → PROPOSTA → GANHO / PERDIDO`
- Histórico de interações (ligação, WhatsApp, e-mail, reunião)
- Agendamento de follow-up

### Módulo Financeiro
- Contas bancárias
- Transações de receita e despesa com categorias
- Metas financeiras com acompanhamento de progresso
- Relatórios por período

### Corretores e Seguradoras
- Cadastro com comissão padrão por corretor
- Regra de pagamento customizável por seguradora
- Percentual vitalício configurável

### Importação de Extratos PDF
| Formato | Descrição |
|---------|-----------|
| **Genérico** | Parser por regex para extratos padrão |
| **Allcare Benefícios** | Parser especializado com validação de soma e correspondência fuzzy de corretor |

O sistema detecta automaticamente o formato ao importar.

### Configurações
- Alíquotas editáveis via interface: ISS, IRPF, PIS, COFINS, CSLL
- Impostos aplicados automaticamente no cálculo de comissão líquida

---

## Estrutura do Projeto

```
sistema-corretora/
├── main.py                  # Interface principal (Flet)
├── database.py              # Modelos SQLAlchemy e migrações
├── finance_engine.py        # Cálculo de comissões e lançamentos
├── config_manager.py        # Gerenciamento de alíquotas
├── modulo_financeiro.py     # Transações, contas, metas
├── sistema_parcelas.py      # Parcelas automáticas (30/60/90 dias)
├── ocr_engine.py            # Extração e parsing de PDFs
├── pdf_export_avancado.py   # Exportação de relatórios PDF
├── login_system.py          # Autenticação de usuários
├── tax_manager.py           # Gestão de impostos
├── run_app.py               # Inicializa com dados de exemplo
├── verify_app.py            # Verifica dependências do sistema
└── corretora.db             # Banco SQLite (gerado automaticamente)
```

---

## Instalação

```bash
py -m pip install flet sqlalchemy pdfplumber reportlab
```

---

## Executar

### Com dados de exemplo
```bash
py run_app.py
```

### Direto
```bash
py main.py
```

### Modo web (acessível pelo browser)
```bash
py _web_launcher.py
# Acesse: http://localhost:8550
```

### Verificar dependências
```bash
py verify_app.py
```

---

## Banco de Dados

| Tabela | Descrição |
|--------|-----------|
| `usuarios` | Contas de acesso ao sistema |
| `corretores` | Corretores com comissão padrão |
| `seguradoras` | Seguradoras com regra de pagamento |
| `propostas` | Apólices com dados do cliente |
| `dependentes` | Dependentes vinculados à proposta |
| `lancamentos` | Parcelas geradas por proposta |
| `leads` | Prospects do CRM |
| `interacoes` | Histórico de contatos com leads |
| `configuracoes` | Chaves e valores de configuração |
| `conta_bancaria` | Contas do módulo financeiro |
| `transacao_financeira` | Receitas e despesas |
| `categoria_financeira` | Categorias de transação |
| `meta` | Metas financeiras |

---

## Exemplo de Cálculo

```
Proposta: R$ 10.000,00
Comissão (12%): R$ 1.200,00

Impostos sobre a comissão:
  PIS    (0,65%): R$   7,80
  COFINS (3,00%): R$  36,00
  ISS    (5,00%): R$  60,00
  IRPF  (15,00%): R$ 180,00
  CSLL   (1,00%): R$  12,00
─────────────────────────────
Total impostos:   R$ 295,80
Comissão líquida: R$ 904,20

Lançamentos (regra 7/30/60):
  Parcela 1: R$ 301,40  →  venc. 07/03/2026
  Parcela 2: R$ 301,40  →  venc. 30/03/2026
  Parcela 3: R$ 301,40  →  venc. 29/04/2026
```

---

## Regras de Pagamento

```
"30"           →  1 pagamento em 30 dias
"7/30/60"      →  3 pagamentos (7, 30 e 60 dias)
"15/45/90/120" →  4 pagamentos
```

---

## Alíquotas Padrão

| Imposto | Alíquota |
|---------|----------|
| ISS     | 5,00%    |
| IRPF    | 15,00%   |
| PIS     | 0,65%    |
| COFINS  | 3,00%    |
| CSLL    | 1,00%    |

Todas editáveis na aba **Configurações** da interface.
