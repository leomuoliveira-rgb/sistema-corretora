# 🎨 Preview da Interface - Sistema Financeiro

## Aparência Visual (Dark Mode)

```
┌────────────────────────────────────────────────────────────────────────────┐
│  💰 Sistema Financeiro de Corretora                      23/02/2026 14:30  │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  📊 Dashboard  |  📄 Propostas  |  💳 Lançamentos  |  ⚙️ Configurações    │
│  ═══════════                                                               │
│                                                                            │
│  Previsão de Recebimentos                                                 │
│  ──────────────────────────────────────────────────────────────────       │
│                                                                            │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ ┌──────────┐│
│  │ 📅              │ │ 📅              │ │ 📅              │ │ ⏱        ││
│  │                 │ │                 │ │                 │ │          ││
│  │ 3 Meses         │ │ 6 Meses         │ │ 12 Meses        │ │ Total    ││
│  │                 │ │                 │ │                 │ │ Pendente ││
│  │ R$ 2.952,60     │ │ R$ 5.905,20     │ │ R$ 8.857,80     │ │ R$ 9.800 ││
│  │                 │ │                 │ │                 │ │          ││
│  └─────────────────┘ └─────────────────┘ └─────────────────┘ └──────────┘│
│                                                                            │
│  ──────────────────────────────────────────────────────────────────       │
│                                                                            │
│  Gráfico de Previsão                                                      │
│  ──────────────────────────────────────────────────────────────────       │
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │                                                                   │    │
│  │  Valor (R$)                                                       │    │
│  │  10000 ┤                                                          │    │
│  │   9000 ┤                                           ████           │    │
│  │   8000 ┤                                           ████           │    │
│  │   7000 ┤                                           ████           │    │
│  │   6000 ┤                       ████                ████           │    │
│  │   5000 ┤                       ████                ████           │    │
│  │   4000 ┤                       ████                ████           │    │
│  │   3000 ┤   ████                ████                ████           │    │
│  │   2000 ┤   ████                ████                ████           │    │
│  │   1000 ┤   ████                ████                ████           │    │
│  │      0 └─────────────────────────────────────────────────        │    │
│  │          3 Meses          6 Meses          12 Meses              │    │
│  │                                                                   │    │
│  └──────────────────────────────────────────────────────────────────┘    │
│                                                                            │
│  ──────────────────────────────────────────────────────────────────       │
│                                                                            │
│  ┌────────────────────────────┐  ┌──────────────────────────────┐        │
│  │ 📁 Importar Proposta PDF   │  │ 🔄 Atualizar Dados          │        │
│  └────────────────────────────┘  └──────────────────────────────┘        │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

## Paleta de Cores

### Backgrounds
- **Fundo Principal**: `#0f172a` - Azul escuro profundo
- **Superfícies/Cards**: `#1e293b` - Azul escuro mais claro
- **Bordas**: `#334155` - Cinza azulado

### Cores de Destaque
- **Primária (3 meses)**: `#10b981` - Verde vibrante
- **Secundária (6 meses)**: `#6366f1` - Indigo
- **Terciária (12 meses)**: `#8b5cf6` - Roxo
- **Erro/Alerta**: `#ef4444` - Vermelho

### Textos
- **Primário**: `#f8fafc` - Branco suave
- **Secundário**: `#94a3b8` - Cinza claro

## Características Visuais

### 1. Cabeçalho
- Fundo: Dark surface (`#1e293b`)
- Ícone: 💰 Account Balance (Indigo)
- Título: Sistema Financeiro de Corretora (Bold, 24px)
- Data/Hora: Tempo real
- Borda inferior sutil

### 2. Cards de Estatísticas
- Tamanho: 300x140px
- Bordas arredondadas: 12px
- Ícone grande no topo
- Título em cinza claro
- Valor em branco, bold, 24px
- Hover effect: Sutil elevação

### 3. Gráfico de Barras
- Altura: 400px
- Barras com bordas arredondadas (5px)
- Largura das barras: 40px
- Grid horizontal pontilhado
- Tooltips interativos
- Cores diferentes por período:
  - 3 meses: Verde (`#10b981`)
  - 6 meses: Indigo (`#6366f1`)
  - 12 meses: Roxo (`#8b5cf6`)

### 4. Botões de Ação
- Altura: 50px
- Padding: 20px
- Bordas arredondadas
- Ícones à esquerda
- Hover: Efeito de elevação
- Cores vibrantes

### 5. Navegação por Abas
- Animação suave (300ms)
- Ícones + Texto
- Indicador de aba ativa
- 4 abas principais:
  1. 📊 Dashboard
  2. 📄 Propostas
  3. 💳 Lançamentos
  4. ⚙️ Configurações

## Aba de Configurações

```
┌────────────────────────────────────────────────────────┐
│  Configurações de Impostos                             │
│  ─────────────────────────────────────────────────     │
│                                                         │
│  🔢 ISS                                      ✏️         │
│     Alíquota: 5.0%                                      │
│                                                         │
│  🔢 IRPF                                     ✏️         │
│     Alíquota: 15.0%                                     │
│                                                         │
│  🔢 PIS                                      ✏️         │
│     Alíquota: 0.65%                                     │
│                                                         │
│  🔢 COFINS                                   ✏️         │
│     Alíquota: 3.0%                                      │
│                                                         │
│  🔢 CSLL                                     ✏️         │
│     Alíquota: 1.0%                                      │
│                                                         │
└────────────────────────────────────────────────────────┘
```

## Interações

### Botão "Importar Proposta PDF"
1. Clique no botão
2. Abre seletor de arquivos nativo
3. Filtra apenas arquivos .pdf
4. Exibe notificação com nome do arquivo selecionado
5. (Processamento a ser implementado)

### Botão "Atualizar Dados"
1. Clique no botão
2. Recarrega dados do banco
3. Atualiza gráficos e cards
4. Exibe notificação de sucesso
5. Animação suave de transição

### Gráfico Interativo
- Hover: Tooltip com valor exato
- Cores vibrantes por período
- Escala automática baseada nos valores
- Animação ao carregar

## Notificações (SnackBar)

```
┌─────────────────────────────────────────┐
│ ✓ Dashboard atualizado!           OK   │
└─────────────────────────────────────────┘
```

- Aparece na parte inferior
- Fundo colorido (verde = sucesso, vermelho = erro)
- Desaparece automaticamente
- Botão "OK" para fechar

## Responsividade

- Janela padrão: 1400x900px
- Cards se reorganizam em telas menores
- Scroll automático quando necessário
- Texto escalável
- Ícones adaptativos

## Animações

- **Transição de abas**: 300ms smooth
- **Hover nos cards**: Elevação sutil
- **Tooltips**: Fade in/out
- **Carregamento**: Progressivo
- **Notificações**: Slide in/out

## Acessibilidade

- Alto contraste (WCAG AA)
- Ícones descritivos
- Tooltips informativos
- Navegação por teclado
- Textos legíveis (mínimo 14px)

---

**Design System**: Material Design 3 + Custom Dark Theme
**Framework**: Flet (Flutter para Python)
**Estilo**: Corporate Dark Mode - Moderno e Profissional
