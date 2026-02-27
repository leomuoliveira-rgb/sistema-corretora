# 📊 Guia da Aba "Repasses"

## Visão Geral

A aba **Repasses** foi adicionada ao sistema para gerenciar os valores que devem ser repassados aos corretores, já com todos os impostos descontados e a comissão aplicada.

## 🎯 Funcionalidades

### 1. Listagem de Corretores
- Mostra TODOS os corretores cadastrados
- Exibe um card detalhado para cada corretor
- Informações organizadas e visuais

### 2. Cálculos Automáticos
Para cada corretor, o sistema calcula automaticamente:

#### ✅ Valores Brutos
- **Total em Apólices**: Soma do valor bruto de todas as propostas
- **Comissão Bruta**: Aplicação do percentual de comissão sobre as apólices

#### ✅ Impostos Descontados
O sistema desconta automaticamente:
- **ISS** (Imposto sobre Serviços)
- **IRPF** (Imposto de Renda Pessoa Física)
- **PIS** (Programa de Integração Social)
- **COFINS** (Contribuição para Financiamento da Seguridade Social)
- **CSLL** (Contribuição Social sobre Lucro Líquido)
- **IOF** (se configurado)

#### ✅ Valor Líquido Final
- **Total Líquido a Repassar**: Valor final que deve ser pago ao corretor
- Fórmula: `Comissão Bruta - Impostos = Líquido`

#### ✅ Status de Lançamentos
- **Valores Pagos**: Lançamentos já marcados como pagos
- **Valores Pendentes**: Lançamentos ainda em aberto
- **Quantidade de Lançamentos**: Total de parcelas pendentes

### 3. Card do Corretor

Cada corretor possui um card com:

```
┌─────────────────────────────────────────────────────────────┐
│ 👤 Nome do Corretor                    TOTAL LÍQUIDO        │
│    Comissão padrão: 12%                R$ 1.329,30          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Apólices      │ Comissão Bruta │ Impostos │ Pendente │Pago│
│  R$ 15.000,00  │  R$ 1.800,00   │R$ 470,70 │R$ 1.033,90│... │
│  2 propostas   │  12% do total  │Descontados│2 lançam. │    │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  [📄 Gerar Extrato PDF]  [ℹ️ Ver Detalhes]                 │
└─────────────────────────────────────────────────────────────┘
```

### 4. Resumo Geral

No topo da aba, há um card destacado mostrando:
- **TOTAL GERAL A REPASSAR**: Soma de todos os valores líquidos de todos os corretores
- Visual destacado em verde

### 5. Botões de Ação

#### Por Corretor:
1. **📄 Gerar Extrato PDF**
   - Gera um PDF detalhado com todas as propostas do corretor
   - Inclui valores brutos, impostos e líquido
   - Status: Em desenvolvimento (estrutura pronta)

2. **ℹ️ Ver Detalhes**
   - Abre uma visão detalhada das propostas do corretor
   - Status: Em desenvolvimento (estrutura pronta)

#### Geral:
3. **🔄 Atualizar Valores**
   - Recalcula todos os valores
   - Atualiza a interface com dados mais recentes

## 💡 Como Funciona o Cálculo

### Exemplo Prático:

```
Corretor: Roberto Alves (Comissão: 12%)

Proposta 1:
  Apólice: R$ 10.000,00
  Comissão Bruta (12%): R$ 1.200,00

  Impostos:
  - ISS (6.5%):     R$ 78,00
  - IRPF (15%):     R$ 180,00
  - PIS (0.65%):    R$ 7,80
  - COFINS (3%):    R$ 36,00
  - CSLL (1%):      R$ 12,00
  ────────────────────────────
  Total Impostos:   R$ 313,80

  LÍQUIDO:          R$ 886,20 ✓

Proposta 2:
  Apólice: R$ 5.000,00
  Comissão Bruta (12%): R$ 600,00
  Impostos:             R$ 156,90
  LÍQUIDO:              R$ 443,10 ✓

────────────────────────────────────────
TOTAL LÍQUIDO ROBERTO:  R$ 1.329,30
```

## 🎨 Design Visual

### Cores por Status:
- **Verde (`#10b981`)**: Total líquido (destaque positivo)
- **Indigo (`#6366f1`)**: Valores principais
- **Cinza (`#94a3b8`)**: Informações secundárias
- **Vermelho (`#ef4444`)**: Botão PDF (destaque)

### Layout:
- Cards com bordas arredondadas (12px)
- Separadores visuais entre seções
- Ícones Material Design
- Espaçamento consistente
- Scroll automático quando necessário

## 📋 Informações Exibidas

### Para Cada Corretor:

1. **Identificação**
   - Nome completo
   - Percentual de comissão padrão
   - Ícone personalizado

2. **Valores Financeiros**
   - Total em apólices (soma dos valores brutos)
   - Total de comissão bruta (antes dos impostos)
   - Total de impostos descontados
   - **Total líquido a repassar** (destaque)

3. **Status de Propostas**
   - Quantidade de propostas
   - Valores já pagos
   - Valores pendentes
   - Quantidade de lançamentos pendentes

4. **Ações Disponíveis**
   - Gerar extrato em PDF
   - Ver detalhes completos

## 🔧 Configurações

### Impostos Utilizados
Os impostos são lidos da tabela `Configuracoes` e podem ser alterados na aba **Configurações**.

Impostos padrão:
```
ISS:     6.5%
IRPF:    15.0%
PIS:     0.65%
COFINS:  3.0%
CSLL:    1.0%
IOF:     0.38% (se configurado)
```

### Comissões
Cada corretor tem sua comissão padrão configurada no cadastro.
Ao calcular repasses, o sistema usa a comissão individual de cada corretor.

## 📊 Relatório de Teste

Baseado nos dados de exemplo:

```
═══════════════════════════════════════════════════════════
RESUMO GERAL - TODOS OS CORRETORES
═══════════════════════════════════════════════════════════
Total Comissões Brutas:     R$      4.800,00
Total Impostos:             R$      1.255,20
TOTAL LÍQUIDO A REPASSAR:   R$      3.544,80
═══════════════════════════════════════════════════════════
```

## 🚀 Próximas Implementações

### Em Desenvolvimento:

1. **Geração de PDF Real**
   - Extrato completo do corretor
   - Logo da empresa
   - Detalhamento por proposta
   - Assinatura digital

2. **Filtros e Buscas**
   - Filtrar por período
   - Buscar por nome do corretor
   - Ordenar por valor líquido

3. **Exportação**
   - Excel com todos os dados
   - CSV para importação em outros sistemas

4. **Histórico**
   - Repasses já efetuados
   - Comparação mensal
   - Gráficos de evolução

5. **Marcação de Pagamento**
   - Marcar repasse como efetuado
   - Data do pagamento
   - Comprovante anexado

## 💻 Código - Funções Principais

### `build_repasses_tab()`
- Constrói a interface da aba
- Lista todos os corretores
- Calcula totais gerais

### `calcular_repasse_corretor(corretor)`
- Calcula todos os valores para um corretor específico
- Retorna dicionário com:
  - `total_bruto`: Total em apólices
  - `total_comissao_bruto`: Comissão antes dos impostos
  - `total_impostos`: Soma de todos os impostos
  - `total_liquido`: Valor final a repassar
  - `num_propostas`: Quantidade de propostas
  - `valor_pendente`: Lançamentos não pagos
  - `valor_pago`: Lançamentos já pagos

### `create_corretor_card(corretor, dados)`
- Cria o card visual do corretor
- Organiza informações em colunas
- Adiciona botões de ação

### `gerar_extrato_pdf(corretor, dados)`
- Prepara geração de PDF (em desenvolvimento)
- Mostra notificação ao usuário

## 📖 Como Usar

### 1. Acessar a Aba
```bash
py run_app.py
```
- Clique na aba **"Repasses"** (ícone: 💼)

### 2. Visualizar Valores
- Veja o total geral no topo
- Role para baixo para ver cada corretor
- Valores são calculados automaticamente

### 3. Gerar Extrato
- Clique em **"Gerar Extrato PDF"** no card do corretor
- (Funcionalidade em desenvolvimento)

### 4. Atualizar Dados
- Clique em **"Atualizar Valores"** no topo
- Sistema recalcula tudo

## ⚠️ Notas Importantes

1. **Impostos são da Corretora**
   - Os impostos descontados são da corretora, não do corretor
   - O corretor recebe o valor líquido

2. **Comissão Individual**
   - Cada corretor tem sua própria taxa de comissão
   - É respeitada no cálculo

3. **Lançamentos vs Repasses**
   - **Lançamentos**: Quando a seguradora paga a corretora
   - **Repasses**: Quando a corretora paga o corretor
   - Valores podem ser diferentes se houver impostos

4. **Valores em Tempo Real**
   - Sempre que uma nova proposta é criada, os valores são atualizados
   - Use o botão "Atualizar" para ver mudanças

## 🎯 Casos de Uso

### Caso 1: Calcular Repasse Mensal
1. Acesse a aba Repasses
2. Veja o total de cada corretor
3. Gere o extrato PDF
4. Efetue o pagamento

### Caso 2: Verificar Pendências
1. Veja a coluna "Pendente" de cada corretor
2. Compare com "Pago"
3. Identifique quem está com valores em atraso

### Caso 3: Auditoria
1. Compare "Comissão Bruta" com "Impostos"
2. Verifique se os impostos estão corretos
3. Use "Ver Detalhes" para análise profunda

---

**Aba Repasses**: Gestão completa e automática de comissões líquidas! 🎉
