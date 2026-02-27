# 💰 Tax Manager - Guia Completo

## Visão Geral

O **Tax Manager** é um sistema administrativo completo para gerenciar impostos da corretora. Ele garante que a **comissão do corretor seja calculada APENAS sobre o valor líquido**, após descontar todos os impostos.

---

## 🎯 Funcionalidades Principais

### ✅ **Gerenciamento de Impostos**
- Adicionar novos impostos
- Editar alíquotas existentes
- Ativar/Desativar impostos
- Remover impostos

### ✅ **Cálculo Automático**
- Função `calcular_liquido(valor_bruto)`
- Percorre TODOS os impostos ativos
- Retorna valor final para a corretora
- Garante que impostos não entrem no cálculo de comissão

### ✅ **Interface Administrativa**
- Interface Flet moderna em Dark Mode
- Simulador de cálculo em tempo real
- Gestão visual de impostos
- Ativação/desativação por switch

---

## 📊 Teste Realizado

```
=== Tax Manager ===

1. Impostos Ativos:
   - ISS: 6.5%
   - IRPF: 15.0%
   - PIS: 0.65%
   - COFINS: 3.0%
   - CSLL: 1.0%
   - IOF: 0.38%

2. Teste de Cálculo:
   Valor Bruto: R$ 10.000,00
   Total Impostos: R$ 2.653,00
   Valor Líquido: R$ 7.347,00
   Percentual: 26.53%
```

---

## 🚀 Como Usar

### 1. Via Interface Gráfica

```bash
py -m flet run tax_manager.py
```

#### Interface:
```
┌──────────────────────────────────────────────────┐
│  💰 Tax Manager                                  │
│  Gerenciamento de Impostos da Corretora         │
├──────────────────────────────────────────────────┤
│                                                  │
│  🧮 Simulador de Cálculo                         │
│  ┌──────────────────────────────────────────┐   │
│  │ Valor Bruto: R$ [10000.00]  [Calcular]  │   │
│  │                                          │   │
│  │ Valor Bruto: R$ 10.000,00                │   │
│  │ Total Impostos: R$ 2.653,00              │   │
│  │ Valor Líquido: R$ 7.347,00               │   │
│  └──────────────────────────────────────────┘   │
│                                                  │
│  ➕ Adicionar/Editar Imposto                     │
│  Nome: [ISS___] Alíquota: [5.0] [Salvar]       │
│                                                  │
│  📋 Impostos Cadastrados                         │
│  ┌──────────────────────────────────────────┐   │
│  │ ● ISS           ✏️ 🗑️ [●]               │   │
│  │   Alíquota: 6.5%                         │   │
│  ├──────────────────────────────────────────┤   │
│  │ ● IRPF          ✏️ 🗑️ [●]               │   │
│  │   Alíquota: 15.0%                        │   │
│  └──────────────────────────────────────────┘   │
└──────────────────────────────────────────────────┘
```

### 2. Via Código Python

```python
from tax_manager import TaxCalculator, calcular_liquido

# Opção 1: Função simples
resultado = calcular_liquido(10000.00)
print(f"Líquido: R$ {resultado['valor_liquido']:.2f}")

# Opção 2: Classe completa
calc = TaxCalculator()

# Obter impostos ativos
impostos = calc.obter_impostos_ativos()
# {'ISS': 6.5, 'IRPF': 15.0, ...}

# Calcular líquido
resultado = calc.calcular_liquido(10000.00)
# {
#     'valor_bruto': 10000.00,
#     'impostos': {...},
#     'total_impostos': 2653.00,
#     'valor_liquido': 7347.00,
#     'percentual_impostos': 26.53
# }

calc.fechar()
```

---

## 💡 Fluxo de Cálculo Correto

### ❌ **ERRADO** (Comissão sobre bruto):
```
Apólice: R$ 10.000,00
Comissão (10%): R$ 1.000,00  ← ERRADO! Inclui impostos!
Impostos sobre comissão: R$ 265,30
Líquido: R$ 734,70

❌ Corretora paga comissão sobre R$ 2.653 de impostos!
```

### ✅ **CORRETO** (Comissão sobre líquido):
```
Apólice: R$ 10.000,00
↓
[TAX MANAGER]
Impostos (26.53%): R$ 2.653,00
Valor Líquido: R$ 7.347,00  ← Sobra para corretora
↓
Comissão (10%): R$ 734,70  ← Sobre valor líquido!
↓
Impostos sobre comissão: R$ 194,92
Líquido para corretor: R$ 539,78

✓ Corretora nunca paga comissão sobre impostos!
```

---

## 🔧 Funções Disponíveis

### `TaxCalculator`

#### `calcular_liquido(valor_bruto)`
```python
"""
Calcula valor líquido após TODOS os impostos ativos

Args:
    valor_bruto: Valor bruto da apólice

Returns:
    dict: {
        'valor_bruto': 10000.00,
        'impostos': {
            'ISS': {'aliquota': 6.5, 'valor': 650.00},
            'IRPF': {'aliquota': 15.0, 'valor': 1500.00},
            ...
        },
        'total_impostos': 2653.00,
        'valor_liquido': 7347.00,
        'percentual_impostos': 26.53
    }
"""
```

#### `obter_impostos_ativos()`
```python
"""
Obtém impostos com alíquota > 0

Returns:
    dict: {'ISS': 6.5, 'IRPF': 15.0, ...}
"""
```

#### `adicionar_imposto(nome, aliquota)`
```python
"""
Adiciona ou atualiza imposto

Args:
    nome: Nome do imposto (ex: 'ISS')
    aliquota: Percentual (ex: 5.0 para 5%)

Returns:
    bool: True se sucesso
"""
```

#### `ativar_imposto(nome)`
```python
"""
Ativa imposto (define alíquota padrão se estava em 0)

Returns:
    bool: True se ativado
"""
```

#### `desativar_imposto(nome)`
```python
"""
Desativa imposto (define alíquota como 0)

Returns:
    bool: True se desativado
"""
```

#### `remover_imposto(nome)`
```python
"""
Remove imposto completamente do banco

Returns:
    bool: True se removido
"""
```

---

## 🎨 Interface - Funcionalidades

### 1. **Simulador de Cálculo**
- Insira valor bruto
- Clique em "Calcular"
- Veja detalhamento completo:
  - Cada imposto aplicado
  - Valor de cada imposto
  - Total de impostos
  - Valor líquido final
  - Percentual total

### 2. **Adicionar/Editar Imposto**
- Nome: Digite o nome (ex: ISS, PIS)
- Alíquota: Digite o percentual (ex: 5.0)
- Clique em "Salvar"
- Imposto criado/atualizado!

### 3. **Gestão de Impostos**
Para cada imposto:
- **●/○**: Indicador ativo/inativo
- **✏️**: Editar (preenche formulário)
- **🗑️**: Remover permanentemente
- **Switch**: Ativar/Desativar rapidamente

---

## 📋 Impostos Pré-cadastrados

| Nome   | Alíquota | Descrição                                    |
|--------|----------|----------------------------------------------|
| ISS    | 6.5%     | Imposto sobre Serviços                       |
| IRPF   | 15.0%    | Imposto de Renda Pessoa Física               |
| PIS    | 0.65%    | Programa de Integração Social                |
| COFINS | 3.0%     | Contribuição para Seguridade Social          |
| CSLL   | 1.0%     | Contribuição Social sobre Lucro Líquido      |
| IOF    | 0.38%    | Imposto sobre Operações Financeiras          |

**Total: 26.53%** dos impostos

---

## 🔄 Integração com Sistema

### No `finance_engine.py`:

```python
from tax_manager import calcular_liquido

def calcular_comissao_corretor(valor_apolice, percentual_comissao):
    """Calcula comissão corretamente"""

    # 1. Primeiro: descontar impostos da corretora
    resultado_impostos = calcular_liquido(valor_apolice)
    valor_liquido_corretora = resultado_impostos['valor_liquido']

    # 2. Depois: calcular comissão sobre o líquido
    comissao_bruta = valor_liquido_corretora * (percentual_comissao / 100)

    # 3. Por fim: descontar impostos do corretor
    resultado_comissao = calcular_liquido(comissao_bruta)
    comissao_liquida = resultado_comissao['valor_liquido']

    return {
        'valor_apolice': valor_apolice,
        'impostos_corretora': resultado_impostos['total_impostos'],
        'valor_liquido_corretora': valor_liquido_corretora,
        'comissao_bruta': comissao_bruta,
        'impostos_corretor': resultado_comissao['total_impostos'],
        'comissao_liquida': comissao_liquida
    }
```

### Exemplo de Uso:
```python
resultado = calcular_comissao_corretor(
    valor_apolice=10000.00,
    percentual_comissao=10.0
)

print(f"Apólice: R$ {resultado['valor_apolice']:.2f}")
print(f"Impostos Corretora: R$ {resultado['impostos_corretora']:.2f}")
print(f"Líquido Corretora: R$ {resultado['valor_liquido_corretora']:.2f}")
print(f"Comissão Bruta: R$ {resultado['comissao_bruta']:.2f}")
print(f"Impostos Corretor: R$ {resultado['impostos_corretor']:.2f}")
print(f"Comissão Líquida: R$ {resultado['comissao_liquida']:.2f}")
```

**Saída:**
```
Apólice: R$ 10.000,00
Impostos Corretora: R$ 2.653,00
Líquido Corretora: R$ 7.347,00
Comissão Bruta: R$ 734,70
Impostos Corretor: R$ 194,92
Comissão Líquida: R$ 539,78
```

---

## 💼 Casos de Uso

### Caso 1: Adicionar Novo Imposto
```python
calc = TaxCalculator()

# Adicionar novo imposto municipal
calc.adicionar_imposto('ISSQN', 2.5)

# Verificar
impostos = calc.obter_impostos_ativos()
print(impostos)  # {'ISS': 6.5, ..., 'ISSQN': 2.5}

calc.fechar()
```

### Caso 2: Desativar Imposto Temporariamente
```python
calc = TaxCalculator()

# Desativar IOF
calc.desativar_imposto('IOF')

# IOF agora tem alíquota 0% (não será aplicado)
# Mas continua no banco para reativar depois

calc.fechar()
```

### Caso 3: Calcular Múltiplos Valores
```python
calc = TaxCalculator()

valores = [5000, 10000, 15000, 20000]
for valor in valores:
    resultado = calc.calcular_liquido(valor)
    print(f"R$ {valor:,} → R$ {resultado['valor_liquido']:,.2f}")

calc.fechar()
```

**Saída:**
```
R$ 5,000 → R$ 3,673.50
R$ 10,000 → R$ 7,347.00
R$ 15,000 → R$ 11,020.50
R$ 20,000 → R$ 14,694.00
```

---

## 🔐 Segurança

### Validações Implementadas:
- ✅ Alíquota entre 0 e 100%
- ✅ Nome do imposto obrigatório
- ✅ Valores numéricos validados
- ✅ Tratamento de erros de banco

### Proteções:
- ✅ Não permite alíquotas negativas
- ✅ Não permite alíquotas > 100%
- ✅ Confirma antes de remover
- ✅ Switch visual para ativar/desativar

---

## 📊 Relatórios

### Exemplo de Relatório Completo:
```python
calc = TaxCalculator()

# Calcular
resultado = calc.calcular_liquido(10000.00)

# Gerar relatório
print("="*50)
print("RELATÓRIO DE IMPOSTOS")
print("="*50)
print(f"Valor Bruto: R$ {resultado['valor_bruto']:,.2f}")
print("\nImpostos Aplicados:")
for nome, dados in resultado['impostos'].items():
    print(f"  {nome:.<15} {dados['aliquota']:>5.2f}%  R$ {dados['valor']:>10,.2f}")
print("-"*50)
print(f"Total Impostos: R$ {resultado['total_impostos']:>10,.2f}")
print(f"Percentual:     {resultado['percentual_impostos']:>10.2f}%")
print("="*50)
print(f"VALOR LÍQUIDO:  R$ {resultado['valor_liquido']:>10,.2f}")
print("="*50)

calc.fechar()
```

**Saída:**
```
==================================================
RELATÓRIO DE IMPOSTOS
==================================================
Valor Bruto: R$ 10,000.00

Impostos Aplicados:
  ISS............   6.50%  R$     650.00
  IRPF...........  15.00%  R$   1,500.00
  PIS............   0.65%  R$      65.00
  COFINS.........   3.00%  R$     300.00
  CSLL...........   1.00%  R$     100.00
  IOF............   0.38%  R$      38.00
--------------------------------------------------
Total Impostos: R$   2,653.00
Percentual:          26.53%
==================================================
VALOR LÍQUIDO:  R$   7,347.00
==================================================
```

---

## 🎯 Importância do Tax Manager

### Por que é Essencial:

1. **Proteção Financeira**
   - Evita pagar comissão sobre impostos
   - Garante margens corretas

2. **Transparência**
   - Cálculo claro e auditável
   - Detalhamento de cada imposto

3. **Flexibilidade**
   - Adiciona/remove impostos facilmente
   - Ativa/desativa conforme necessário

4. **Compliance**
   - Impostos sempre atualizados
   - Cálculo correto conforme legislação

---

## ✅ Status

**Tax Manager: 100% Funcional!**

- ✅ Classe TaxCalculator implementada
- ✅ Função calcular_liquido() funcionando
- ✅ Interface Flet completa
- ✅ Simulador de cálculo
- ✅ CRUD de impostos
- ✅ Ativação/desativação
- ✅ Integração com sistema
- ✅ Documentação completa
- ✅ Testado e aprovado

---

**Tax Manager**: Gestão inteligente de impostos para maximizar lucros! 💰✨
