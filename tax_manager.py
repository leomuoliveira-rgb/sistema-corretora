"""
Tax Manager - Gerenciamento de Impostos
Interface administrativa para cadastrar e gerenciar impostos
"""

import flet as ft
from database import criar_banco, obter_sessao, Configuracao
from config_manager import ConfigManager
from typing import List, Dict, Optional


class TaxCalculator:
    """Calculadora de impostos"""

    def __init__(self, session=None):
        """
        Inicializa calculadora

        Args:
            session: Sessão do SQLAlchemy (opcional)
        """
        if session is None:
            engine = criar_banco()
            self.session = obter_sessao(engine)
            self._own_session = True
        else:
            self.session = session
            self._own_session = False

        self.config = ConfigManager(session=self.session)

    def obter_impostos_ativos(self) -> Dict[str, float]:
        """
        Obtém todos os impostos ativos (com alíquota > 0)

        Returns:
            Dict[str, float]: Dicionário com nome e alíquota dos impostos
        """
        todos_impostos = self.config.listar_impostos()

        # Filtrar apenas impostos ativos (alíquota > 0)
        impostos_ativos = {
            nome: aliquota
            for nome, aliquota in todos_impostos.items()
            if aliquota > 0
        }

        return impostos_ativos

    def calcular_liquido(self, valor_bruto: float) -> Dict:
        """
        Calcula valor líquido após descontar TODOS os impostos ativos

        Esta função deve ser usada ANTES de calcular comissão do corretor,
        garantindo que a corretora nunca pague comissão sobre impostos.

        Args:
            valor_bruto: Valor bruto da apólice/contrato

        Returns:
            dict: {
                'valor_bruto': float,
                'impostos': {'NOME': {'aliquota': float, 'valor': float}},
                'total_impostos': float,
                'valor_liquido': float,
                'percentual_impostos': float
            }

        Exemplo:
            >>> calc = TaxCalculator()
            >>> resultado = calc.calcular_liquido(10000.00)
            >>> print(f"Líquido: R$ {resultado['valor_liquido']:.2f}")
            Líquido: R$ 7.436,00
        """
        impostos_ativos = self.obter_impostos_ativos()

        detalhamento = {}
        total_impostos = 0.0

        # Calcular cada imposto
        for nome, aliquota in impostos_ativos.items():
            valor_imposto = valor_bruto * (aliquota / 100)
            detalhamento[nome] = {
                'aliquota': aliquota,
                'valor': valor_imposto
            }
            total_impostos += valor_imposto

        valor_liquido = valor_bruto - total_impostos
        percentual_impostos = (total_impostos / valor_bruto * 100) if valor_bruto > 0 else 0

        return {
            'valor_bruto': valor_bruto,
            'impostos': detalhamento,
            'total_impostos': total_impostos,
            'valor_liquido': valor_liquido,
            'percentual_impostos': percentual_impostos
        }

    def adicionar_imposto(self, nome: str, aliquota: float) -> bool:
        """
        Adiciona ou atualiza um imposto

        Args:
            nome: Nome do imposto (ex: 'ISS', 'PIS')
            aliquota: Alíquota em percentual (ex: 5.0 para 5%)

        Returns:
            bool: True se sucesso
        """
        return self.config.set_imposto(nome, aliquota)

    def remover_imposto(self, nome: str) -> bool:
        """
        Remove um imposto

        Args:
            nome: Nome do imposto

        Returns:
            bool: True se removido
        """
        return self.config.remover_imposto(nome)

    def ativar_imposto(self, nome: str) -> bool:
        """
        Ativa um imposto (define alíquota padrão se estava em 0)

        Args:
            nome: Nome do imposto

        Returns:
            bool: True se ativado
        """
        aliquota_atual = self.config.get_imposto(nome)
        if aliquota_atual == 0:
            # Define alíquota padrão baseada no tipo
            aliquotas_padrao = {
                'ISS': 5.0,
                'IRPF': 15.0,
                'PIS': 0.65,
                'COFINS': 3.0,
                'CSLL': 1.0,
                'IOF': 0.38
            }
            aliquota = aliquotas_padrao.get(nome.upper(), 1.0)
            return self.config.set_imposto(nome, aliquota)
        return True

    def desativar_imposto(self, nome: str) -> bool:
        """
        Desativa um imposto (define alíquota como 0)

        Args:
            nome: Nome do imposto

        Returns:
            bool: True se desativado
        """
        return self.config.set_imposto(nome, 0.0)

    def fechar(self):
        """Fecha conexão com banco"""
        if self._own_session:
            self.session.close()


class TaxManagerApp:
    """Interface administrativa para gerenciar impostos"""

    def __init__(self, page: ft.Page):
        """
        Inicializa interface

        Args:
            page: Página Flet
        """
        self.page = page
        self.page.title = "Tax Manager - Gerenciamento de Impostos"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 20
        self.page.window_width = 900
        self.page.window_height = 700

        # Cores
        self.primary_color = "#6366f1"
        self.success_color = "#10b981"
        self.error_color = "#ef4444"
        self.warning_color = "#f59e0b"
        self.surface_color = "#1e293b"
        self.text_primary = "#f8fafc"
        self.text_secondary = "#94a3b8"

        # Tax Calculator
        self.tax_calc = TaxCalculator()

        # Campos de entrada
        self.nome_input = None
        self.aliquota_input = None
        self.impostos_list = None

        # Construir UI
        self.build_ui()

    def build_ui(self):
        """Constrói interface"""
        # Título
        titulo = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text("💰", size=40),
                            ft.Text(
                                "Tax Manager",
                                size=32,
                                weight=ft.FontWeight.BOLD,
                                color=self.text_primary,
                            ),
                        ],
                        spacing=10,
                    ),
                    ft.Text(
                        "Gerenciamento de Impostos da Corretora",
                        size=16,
                        color=self.text_secondary,
                    ),
                ],
                spacing=5,
            ),
            padding=20,
        )

        # Simulador
        simulador = self.build_simulador()

        # Formulário de adicionar imposto
        form = self.build_form()

        # Lista de impostos
        impostos = self.build_impostos_list()

        # Montar página
        self.page.add(
            titulo,
            ft.Divider(height=20, color="#334155"),
            simulador,
            ft.Divider(height=20, color="#334155"),
            form,
            ft.Divider(height=20, color="#334155"),
            impostos,
        )

    def build_simulador(self):
        """Constrói simulador de cálculo"""
        valor_input = ft.TextField(
            label="Valor Bruto da Apólice",
            prefix_text="R$ ",
            keyboard_type=ft.KeyboardType.NUMBER,
            width=300,
            value="10000.00",
        )

        resultado_container = ft.Container(
            content=ft.Text("Insira um valor e clique em Calcular"),
            padding=20,
            bgcolor=self.surface_color,
            border_radius=10,
        )

        def calcular_click(e):
            try:
                valor = float(valor_input.value.replace(',', '.'))
                resultado = self.tax_calc.calcular_liquido(valor)

                # Montar detalhamento
                impostos_text = ""
                for nome, dados in resultado['impostos'].items():
                    impostos_text += f"  • {nome}: {dados['aliquota']:.2f}% = R$ {dados['valor']:.2f}\n"

                texto_resultado = f"""
📊 Cálculo de Impostos

Valor Bruto: R$ {resultado['valor_bruto']:,.2f}

Impostos Aplicados:
{impostos_text}
Total de Impostos: R$ {resultado['total_impostos']:,.2f}
Percentual: {resultado['percentual_impostos']:.2f}%

💰 Valor Líquido: R$ {resultado['valor_liquido']:,.2f}

⚠️ Este é o valor que sobra para a corretora.
A comissão do corretor será calculada sobre este valor líquido.
                """

                resultado_container.content = ft.Text(
                    texto_resultado,
                    color=self.text_primary,
                    size=14,
                )
                self.page.update()
                self.show_snackbar("Cálculo realizado!", self.success_color)

            except ValueError:
                self.show_snackbar("Valor inválido!", self.error_color)

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "🧮 Simulador de Cálculo",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=self.text_primary,
                    ),
                    ft.Row(
                        controls=[
                            valor_input,
                            ft.ElevatedButton(
                                text="Calcular",
                                style=ft.ButtonStyle(
                                    bgcolor=self.primary_color,
                                    color=self.text_primary,
                                ),
                                on_click=calcular_click,
                            ),
                        ],
                        spacing=10,
                    ),
                    resultado_container,
                ],
                spacing=10,
            ),
            padding=20,
            bgcolor=self.surface_color,
            border_radius=12,
        )

    def build_form(self):
        """Constrói formulário de adicionar imposto"""
        self.nome_input = ft.TextField(
            label="Nome do Imposto",
            hint_text="Ex: ISS, PIS, COFINS",
            width=300,
        )

        self.aliquota_input = ft.TextField(
            label="Alíquota (%)",
            hint_text="Ex: 5.0",
            keyboard_type=ft.KeyboardType.NUMBER,
            width=150,
        )

        def adicionar_click(e):
            nome = self.nome_input.value.strip().upper()
            aliquota_str = self.aliquota_input.value.strip()

            if not nome or not aliquota_str:
                self.show_snackbar("Preencha todos os campos!", self.error_color)
                return

            try:
                aliquota = float(aliquota_str.replace(',', '.'))

                if aliquota < 0 or aliquota > 100:
                    self.show_snackbar("Alíquota deve estar entre 0 e 100%", self.error_color)
                    return

                # Adicionar imposto
                sucesso = self.tax_calc.adicionar_imposto(nome, aliquota)

                if sucesso:
                    self.show_snackbar(
                        f"Imposto {nome} cadastrado com {aliquota}%!",
                        self.success_color
                    )
                    self.nome_input.value = ""
                    self.aliquota_input.value = ""
                    self.atualizar_lista()
                else:
                    self.show_snackbar("Erro ao adicionar imposto", self.error_color)

            except ValueError:
                self.show_snackbar("Alíquota inválida!", self.error_color)

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "➕ Adicionar/Editar Imposto",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=self.text_primary,
                    ),
                    ft.Row(
                        controls=[
                            self.nome_input,
                            self.aliquota_input,
                            ft.ElevatedButton(
                                text="Salvar",
                                style=ft.ButtonStyle(
                                    bgcolor=self.success_color,
                                    color=self.text_primary,
                                ),
                                on_click=adicionar_click,
                            ),
                        ],
                        spacing=10,
                    ),
                ],
                spacing=10,
            ),
            padding=20,
            bgcolor=self.surface_color,
            border_radius=12,
        )

    def build_impostos_list(self):
        """Constrói lista de impostos cadastrados"""
        impostos = self.tax_calc.config.listar_impostos()

        self.impostos_list = ft.Column(spacing=10)

        if not impostos:
            self.impostos_list.controls.append(
                ft.Text(
                    "Nenhum imposto cadastrado ainda.",
                    color=self.text_secondary,
                )
            )
        else:
            for nome, aliquota in impostos.items():
                self.impostos_list.controls.append(
                    self.create_imposto_card(nome, aliquota)
                )

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "📋 Impostos Cadastrados",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=self.text_primary,
                    ),
                    self.impostos_list,
                ],
                spacing=10,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=20,
            bgcolor=self.surface_color,
            border_radius=12,
        )

    def create_imposto_card(self, nome: str, aliquota: float):
        """Cria card para um imposto"""
        ativo = aliquota > 0

        def editar_click(e):
            self.nome_input.value = nome
            self.aliquota_input.value = str(aliquota)
            self.page.update()
            self.show_snackbar(f"Editando {nome}", self.primary_color)

        def remover_click(e):
            sucesso = self.tax_calc.remover_imposto(nome)
            if sucesso:
                self.show_snackbar(f"{nome} removido!", self.warning_color)
                self.atualizar_lista()
            else:
                self.show_snackbar("Erro ao remover", self.error_color)

        def toggle_ativo(e):
            if ativo:
                self.tax_calc.desativar_imposto(nome)
                self.show_snackbar(f"{nome} desativado", self.warning_color)
            else:
                self.tax_calc.ativar_imposto(nome)
                self.show_snackbar(f"{nome} ativado", self.success_color)
            self.atualizar_lista()

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Text(
                            "●" if ativo else "○",
                            size=20,
                            color=self.success_color if ativo else self.text_secondary,
                        ),
                        width=30,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(
                                nome,
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=self.text_primary if ativo else self.text_secondary,
                            ),
                            ft.Text(
                                f"Alíquota: {aliquota:.2f}%",
                                size=14,
                                color=self.text_secondary,
                            ),
                        ],
                        spacing=2,
                    ),
                    ft.Container(expand=True),
                    ft.Row(
                        controls=[
                            ft.IconButton(
                                content=ft.Text("✏️", size=20),
                                tooltip="Editar",
                                on_click=editar_click,
                            ),
                            ft.IconButton(
                                content=ft.Text("🗑️", size=20),
                                tooltip="Remover",
                                on_click=remover_click,
                            ),
                            ft.Switch(
                                value=ativo,
                                on_change=toggle_ativo,
                                active_color=self.success_color,
                            ),
                        ],
                        spacing=5,
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
            ),
            padding=15,
            bgcolor="#0f172a",
            border_radius=8,
            border=ft.Border.all(1, self.success_color if ativo else "#334155"),
        )

    def atualizar_lista(self):
        """Atualiza lista de impostos"""
        impostos = self.tax_calc.config.listar_impostos()
        self.impostos_list.controls.clear()

        if not impostos:
            self.impostos_list.controls.append(
                ft.Text(
                    "Nenhum imposto cadastrado ainda.",
                    color=self.text_secondary,
                )
            )
        else:
            for nome, aliquota in impostos.items():
                self.impostos_list.controls.append(
                    self.create_imposto_card(nome, aliquota)
                )

        self.page.update()

    def show_snackbar(self, message: str, color: str):
        """Mostra notificação"""
        snackbar = ft.SnackBar(
            content=ft.Text(message, color=self.text_primary),
            bgcolor=color,
        )
        self.page.snack_bar = snackbar
        snackbar.open = True
        self.page.update()


# Função auxiliar para calcular líquido
def calcular_liquido(valor_bruto: float) -> Dict:
    """
    Função auxiliar para calcular valor líquido

    Args:
        valor_bruto: Valor bruto

    Returns:
        dict: Resultado do cálculo
    """
    calc = TaxCalculator()
    resultado = calc.calcular_liquido(valor_bruto)
    calc.fechar()
    return resultado


# Função principal
def main(page: ft.Page):
    """Função principal da interface"""
    TaxManagerApp(page)


if __name__ == '__main__':
    print("=== Tax Manager ===\n")

    # Teste da calculadora
    calc = TaxCalculator()

    print("1. Impostos Ativos:")
    impostos = calc.obter_impostos_ativos()
    for nome, aliquota in impostos.items():
        print(f"   - {nome}: {aliquota}%")

    print("\n2. Teste de Cálculo:")
    resultado = calc.calcular_liquido(10000.00)
    print(f"   Valor Bruto: R$ {resultado['valor_bruto']:,.2f}")
    print(f"   Total Impostos: R$ {resultado['total_impostos']:,.2f}")
    print(f"   Valor Líquido: R$ {resultado['valor_liquido']:,.2f}")
    print(f"   Percentual: {resultado['percentual_impostos']:.2f}%")

    calc.fechar()

    print("\n[OK] Tax Manager pronto!")
    print("\nPara abrir interface:")
    print("  py -m flet run tax_manager.py")
