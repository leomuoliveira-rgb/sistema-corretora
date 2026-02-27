# 🎨 Preview Visual - Aba Repasses

## Layout da Aba

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  💰 Sistema Financeiro de Corretora                        23/02/2026 14:30  │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  📊 Dashboard  │  📄 Propostas  │  💳 Lançamentos  │  💼 Repasses  │  ⚙️    │
│                                                       ══════════              │
│                                                                              │
│  Repasses aos Corretores                              [🔄 Atualizar Valores] │
│  ────────────────────────────────────────────────────────────────────────    │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  💰  TOTAL GERAL A REPASSAR                                            │ │
│  │                                                                        │ │
│  │      R$ 3.544,80                                                       │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ────────────────────────────────────────────────────────────────────────    │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  👤 Roberto Alves                              TOTAL LÍQUIDO            │ │
│  │     Comissão padrão: 12%                       R$ 1.329,30              │ │
│  │  ─────────────────────────────────────────────────────────────────────  │ │
│  │                                                                         │ │
│  │  Apólices        │ Comissão Bruta │ Impostos   │ Pendente   │ Pago    │ │
│  │  R$ 15.000,00    │ R$ 1.800,00    │ R$ 470,70  │ R$ 1.033,90│ R$ 295  │ │
│  │  2 propostas     │ 12% do total   │ Descontados│ 2 lançam.  │Repassado│ │
│  │                                                                         │ │
│  │  ─────────────────────────────────────────────────────────────────────  │ │
│  │  [📄 Gerar Extrato PDF]  [ℹ️ Ver Detalhes]                             │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  👤 Maria Santos                               TOTAL LÍQUIDO            │ │
│  │     Comissão padrão: 12.5%                     R$ 738,50                │ │
│  │  ─────────────────────────────────────────────────────────────────────  │ │
│  │                                                                         │ │
│  │  Apólices        │ Comissão Bruta │ Impostos   │ Pendente   │ Pago    │ │
│  │  R$ 8.000,00     │ R$ 1.000,00    │ R$ 261,50  │ R$ 0,00    │ R$ 1.000│ │
│  │  1 proposta      │ 12.5% do total │ Descontados│ 0 lançam.  │Completo │ │
│  │                                                                         │ │
│  │  ─────────────────────────────────────────────────────────────────────  │ │
│  │  [📄 Gerar Extrato PDF]  [ℹ️ Ver Detalhes]                             │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  👤 João Silva                                 TOTAL LÍQUIDO            │ │
│  │     Comissão padrão: 10%                       R$ 369,25                │ │
│  │  ─────────────────────────────────────────────────────────────────────  │ │
│  │                                                                         │ │
│  │  Apólices        │ Comissão Bruta │ Impostos   │ Pendente   │ Pago    │ │
│  │  R$ 5.000,00     │ R$ 500,00      │ R$ 130,75  │ R$ 1.000,00│ R$ 0,00 │ │
│  │  1 proposta      │ 10% do total   │ Descontados│ 2 lançam.  │Pendente │ │
│  │                                                                         │ │
│  │  ─────────────────────────────────────────────────────────────────────  │ │
│  │  [📄 Gerar Extrato PDF]  [ℹ️ Ver Detalhes]                             │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Detalhamento dos Elementos

### 1. Cabeçalho da Aba
```
Repasses aos Corretores                    [🔄 Atualizar Valores]
────────────────────────────────────────────────────────────────
```
- Título grande e destacado
- Botão de atualização no canto direito
- Linha separadora

### 2. Card de Total Geral
```
┌────────────────────────────────────────────────────┐
│  💰  TOTAL GERAL A REPASSAR                        │
│                                                    │
│      R$ 3.544,80                                   │
└────────────────────────────────────────────────────┘
```
**Características:**
- Fundo: `#1e293b` (Surface color)
- Borda: 2px `#10b981` (Verde accent)
- Ícone: Account Balance (Indigo)
- Valor: 32px, Bold, Verde
- Altura: Auto
- Padding: 25px
- Border radius: 12px

### 3. Card Individual do Corretor

#### Estrutura Completa:
```
┌──────────────────────────────────────────────────────────┐
│  👤 [Nome]                        TOTAL LÍQUIDO          │
│     [Comissão %]                  [R$ Valor]             │
│  ──────────────────────────────────────────────────────  │
│                                                          │
│  [Info 1]  │  [Info 2]  │  [Info 3]  │  [Info 4]  │ ... │
│  [Valor 1] │  [Valor 2] │  [Valor 3] │  [Valor 4] │     │
│  [Desc 1]  │  [Desc 2]  │  [Desc 3]  │  [Desc 4]  │     │
│                                                          │
│  ──────────────────────────────────────────────────────  │
│  [Botão 1]  [Botão 2]                                    │
└──────────────────────────────────────────────────────────┘
```

#### Seção Superior (Cabeçalho):
```
👤 Roberto Alves              TOTAL LÍQUIDO
   Comissão padrão: 12%       R$ 1.329,30
```
- Ícone Person (Indigo, 32px)
- Nome: 20px, Bold, Branco
- Comissão: 14px, Cinza claro
- Label "TOTAL LÍQUIDO": 12px, Cinza
- Valor líquido: 24px, Bold, Verde

#### Seção de Dados (5 Colunas):

**Coluna 1 - Apólices:**
```
Apólices
R$ 15.000,00
2 propostas
```
- Título: 12px, Cinza, Medium
- Valor: 16px, Branco, Bold
- Descrição: 11px, Cinza claro

**Coluna 2 - Comissão Bruta:**
```
Comissão Bruta
R$ 1.800,00
12% do total
```

**Coluna 3 - Impostos:**
```
Impostos
R$ 470,70
Descontados
```

**Coluna 4 - Pendente:**
```
Pendente
R$ 1.033,90
2 lançamentos
```

**Coluna 5 - Pago:**
```
Pago
R$ 295,40
Já repassado
```

#### Separadores Verticais:
```
│
```
- Cor: `#334155`
- Largura: 1px
- Entre cada coluna

#### Seção de Ações (Botões):
```
[📄 Gerar Extrato PDF]  [ℹ️ Ver Detalhes]
```

**Botão "Gerar Extrato PDF":**
- Fundo: `#ef4444` (Vermelho)
- Texto: Branco
- Ícone: PICTURE_AS_PDF
- Padding: 10-15px
- Border radius: 8px
- Hover: Elevação sutil

**Botão "Ver Detalhes":**
- Estilo: Outlined (sem preenchimento)
- Borda: `#6366f1` (Indigo)
- Texto: Indigo
- Ícone: INFO_OUTLINE
- Hover: Fundo Indigo claro

### 4. Cores e Estados

#### Estados de Valor:
- **Positivo/Destaque**: Verde `#10b981`
- **Neutro**: Branco `#f8fafc`
- **Secundário**: Cinza `#94a3b8`
- **Atenção**: Vermelho `#ef4444` (para pendências altas)

#### Cores de Fundo:
- **Background geral**: `#0f172a`
- **Cards**: `#1e293b`
- **Bordas**: `#334155`
- **Total geral**: Borda verde `#10b981`

## Fluxo de Interação

### 1. Ao Abrir a Aba
```
[Usuario clica em "Repasses"]
         ↓
[Sistema busca todos os corretores]
         ↓
[Para cada corretor:]
  → Busca propostas
  → Calcula comissão bruta
  → Aplica impostos
  → Calcula líquido
         ↓
[Soma totais gerais]
         ↓
[Renderiza interface]
         ↓
[Exibe cards organizados]
```

### 2. Ao Clicar em "Gerar Extrato PDF"
```
[Usuario clica no botão]
         ↓
[Sistema prepara dados do corretor]
         ↓
[Gera PDF com:]
  • Logo da empresa
  • Nome do corretor
  • Período
  • Lista de propostas
  • Detalhamento de impostos
  • Total líquido
  • Assinatura
         ↓
[Abre/Baixa PDF]
         ↓
[Exibe notificação de sucesso]
```

### 3. Ao Clicar em "Ver Detalhes"
```
[Usuario clica no botão]
         ↓
[Abre modal/janela com:]
  • Todas as propostas do corretor
  • Detalhamento por proposta
  • Gráficos de evolução
  • Histórico de pagamentos
         ↓
[Usuario pode filtrar/ordenar]
```

### 4. Ao Clicar em "Atualizar Valores"
```
[Usuario clica no botão]
         ↓
[Sistema recalcula tudo]
         ↓
[Atualiza interface]
         ↓
[Mostra notificação: "Valores atualizados!"]
```

## Responsividade

### Desktop (1400px+):
- 5 colunas de informações
- Cards lado a lado (se houver espaço)
- Botões em linha

### Tablet (768px - 1399px):
- 3 colunas de informações (wrap)
- Cards empilhados
- Botões em linha

### Mobile (< 768px):
- 2 colunas de informações
- Cards empilhados
- Botões empilhados

## Animações

### Ao Carregar:
```
Cards surgem com fade-in (300ms)
Valores contam de 0 até o total (animação)
```

### Ao Hover em Card:
```
Elevação sutil (box-shadow)
Borda fica mais clara
Transição suave (200ms)
```

### Ao Clicar em Botão:
```
Efeito de "press"
Feedback visual imediato
Notificação após ação
```

## Acessibilidade

### Contrastes (WCAG AAA):
- ✅ Branco sobre Dark Blue: 15.7:1
- ✅ Verde sobre Dark Blue: 4.8:1
- ✅ Indigo sobre Dark Blue: 4.2:1

### Navegação por Teclado:
- Tab: Navega entre botões
- Enter/Space: Ativa botão
- Esc: Fecha modais

### Screen Readers:
- Títulos semânticos (h1, h2)
- Labels descritivos
- ARIA labels em ícones

## Casos de Uso Visual

### Corretor Sem Pendências:
```
👤 Maria Santos                    R$ 738,50
   12.5%

   Pago: R$ 1.000,00 ✓
   Pendente: R$ 0,00

   Status: COMPLETO (Verde)
```

### Corretor Com Pendências:
```
👤 João Silva                      R$ 369,25
   10%

   Pago: R$ 0,00
   Pendente: R$ 1.000,00 ⚠️

   Status: PENDENTE (Amarelo)
```

### Corretor Sem Propostas:
```
👤 Pedro Costa                     R$ 0,00
   15%

   Nenhuma proposta cadastrada

   Status: SEM ATIVIDADE (Cinza)
```

## Performance

### Otimizações:
- ✅ Queries agrupadas (1 query por corretor)
- ✅ Cálculos em memória
- ✅ Lazy loading de cards
- ✅ Virtualização de lista (se >50 corretores)
- ✅ Cache de impostos

### Tempos Esperados:
- 1-10 corretores: < 100ms
- 10-50 corretores: < 500ms
- 50-100 corretores: < 1s
- 100+ corretores: Paginação recomendada

---

**Interface Repasses**: Visual limpo, informações claras, ações rápidas! 🎯
