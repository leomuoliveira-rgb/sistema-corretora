"""
Sistema Financeiro de Corretora - Interface Principal
Interface moderna em Dark Mode usando Flet
"""

import flet as ft
import os
from datetime import datetime, timedelta
from database import criar_banco, obter_sessao, Lancamento, Proposta, Corretor
from sqlalchemy import and_
from finance_engine import FinanceEngine
from config_manager import ConfigManager


class CorretoraApp:
    """Aplicação principal da corretora"""

    def __init__(self, page: ft.Page, usuario_logado=None):
        self.page = page
        self.usuario_logado = usuario_logado  # Usuário autenticado
        self.page.title = f"Sistema Financeiro - {usuario_logado.nome_completo if usuario_logado else 'Corretora'}"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 0
        self.page.window_width = 1400
        self.page.window_height = 900

        # Cores do tema dark
        self.primary_color = "#6366f1"  # Indigo
        self.secondary_color = "#8b5cf6"  # Purple
        self.background_color = "#0f172a"  # Dark blue
        self.surface_color = "#1e293b"  # Lighter dark blue
        self.accent_color = "#10b981"  # Green
        self.error_color = "#ef4444"  # Red
        self.text_primary = "#f8fafc"
        self.text_secondary = "#94a3b8"

        # Banco de dados
        engine = criar_banco()
        self.session = obter_sessao(engine)
        self.finance_engine = FinanceEngine(session=self.session)

        # Construir interface
        self.build_ui()

    def build_ui(self):
        """Constrói a interface do usuário"""
        # Container principal
        self.main_container = ft.Container(
            content=ft.Column(
                controls=[
                    self.build_header(),
                    self.build_tabs(),
                ],
                spacing=0,
                expand=True,
            ),
            bgcolor=self.background_color,
            expand=True,
        )

        self.page.add(self.main_container)

    def build_header(self):
        """Constrói o cabeçalho"""
        def fazer_logout(e):
            """Logout do sistema"""
            self.page.clean()
            from login_system import mostrar_tela_login

            def on_login_success(usuario):
                self.usuario_logado = usuario
                self.page.clean()
                self.__init__(self.page, usuario)

            mostrar_tela_login(self.page, on_login_success)

        usuario_nome = self.usuario_logado.nome_completo if self.usuario_logado else "Usuário"
        usuario_tipo = self.usuario_logado.tipo.upper() if self.usuario_logado else ""

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text("💰", size=32),
                    ft.Text(
                        "Sistema Financeiro de Corretora",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=self.text_primary,
                    ),
                    ft.Container(expand=True),
                    ft.Column([
                        ft.Text(usuario_nome, size=14, weight=ft.FontWeight.BOLD, color=self.text_primary),
                        ft.Text(f"👤 {usuario_tipo}", size=12, color=self.text_secondary),
                    ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.END),
                    ft.Container(width=20),
                    ft.OutlinedButton(
                        content=ft.Text("🚪 Sair", size=14),
                        style=ft.ButtonStyle(color=self.error_color),
                        on_click=fazer_logout,
                    ),
                    ft.Container(width=10),
                    ft.Text(
                        datetime.now().strftime("%d/%m/%Y %H:%M"),
                        size=14,
                        color=self.text_secondary,
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
            ),
            bgcolor=self.surface_color,
            padding=20,
            border=ft.Border.only(bottom=ft.BorderSide(1, "#334155")),
        )

    def build_tabs(self):
        """Constrói as abas principais"""
        # Criar TabBar com os títulos das tabs
        tab_bar = ft.TabBar(
            tabs=[
                ft.Tab(label="📊 Dashboard"),
                ft.Tab(label="🎯 CRM"),
                ft.Tab(label="📄 Propostas"),
                ft.Tab(label="💳 Lançamentos"),
                ft.Tab(label="💼 Repasses"),
                ft.Tab(label="💰 Financeiro"),
                ft.Tab(label="👥 Corretores"),
                ft.Tab(label="⚙️ Configurações"),
            ],
        )

        # Criar TabBarView com o conteúdo de cada tab
        tab_view = ft.TabBarView(
            controls=[
                self.build_dashboard(),
                self.build_crm_tab(),
                self.build_propostas_tab(),
                self.build_lancamentos_tab(),
                self.build_repasses_tab(),
                self.build_financeiro_tab(),
                self.build_corretores_tab(),
                self.build_config_tab(),
            ],
            expand=True,
        )

        # Combinar em um Tabs component
        tabs = ft.Tabs(
            content=ft.Column([tab_bar, tab_view], expand=True, spacing=0),
            length=8,
            selected_index=0,
            animation_duration=300,
        )

        return ft.Container(content=tabs, expand=True, padding=0)

    def build_dashboard(self):
        """Constrói o dashboard com gráficos"""
        # Calcular previsões
        previsoes = self.calcular_previsoes()

        # Criar gráfico de barras (placeholder - BarChart não disponível nesta versão do Flet)
        chart = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("📊 Gráfico de Previsões", size=20, weight=ft.FontWeight.BOLD, color=self.text_primary),
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Text("3 Meses", color=self.text_secondary),
                                        ft.Container(
                                            width=80,
                                            height=int(previsoes['3_meses'] / 50) if previsoes['3_meses'] > 0 else 10,
                                            bgcolor=self.accent_color,
                                            border_radius=5,
                                        ),
                                        ft.Text(f"R$ {previsoes['3_meses']:.2f}", size=12, color=self.text_primary),
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                                padding=10,
                            ),
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Text("6 Meses", color=self.text_secondary),
                                        ft.Container(
                                            width=80,
                                            height=int(previsoes['6_meses'] / 50) if previsoes['6_meses'] > 0 else 10,
                                            bgcolor=self.primary_color,
                                            border_radius=5,
                                        ),
                                        ft.Text(f"R$ {previsoes['6_meses']:.2f}", size=12, color=self.text_primary),
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                                padding=10,
                            ),
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Text("12 Meses", color=self.text_secondary),
                                        ft.Container(
                                            width=80,
                                            height=int(previsoes['12_meses'] / 50) if previsoes['12_meses'] > 0 else 10,
                                            bgcolor=self.secondary_color,
                                            border_radius=5,
                                        ),
                                        ft.Text(f"R$ {previsoes['12_meses']:.2f}", size=12, color=self.text_primary),
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                                padding=10,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                    ),
                ],
                spacing=20,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=self.surface_color,
            padding=30,
            border_radius=12,
            border=ft.Border.all(1, "#334155"),
            height=300,
        )

        # Cards de estatísticas
        stats_cards = ft.Row(
            controls=[
                self.create_stat_card(
                    "3 Meses",
                    f"R$ {previsoes['3_meses']:.2f}",
                    "📅",
                    self.accent_color,
                ),
                self.create_stat_card(
                    "6 Meses",
                    f"R$ {previsoes['6_meses']:.2f}",
                    "📆",
                    self.primary_color,
                ),
                self.create_stat_card(
                    "12 Meses",
                    f"R$ {previsoes['12_meses']:.2f}",
                    "📋",
                    self.secondary_color,
                ),
                self.create_stat_card(
                    "Total Pendente",
                    f"R$ {previsoes['total_pendente']:.2f}",
                    "⏱️",
                    self.error_color,
                ),
            ],
            spacing=20,
            wrap=True,
        )

        # Botão de importar PDF
        import_button = ft.FilledButton(
            content=ft.Text("📁 Importar Proposta PDF", size=14, weight=ft.FontWeight.BOLD),
            style=ft.ButtonStyle(
                bgcolor=self.primary_color,
                color=self.text_primary,
                padding=20,
            ),
            on_click=self.importar_pdf,
            height=50,
        )

        # Botões de ação
        action_buttons = ft.Row(
            controls=[
                import_button,
                ft.FilledButton(
                    content=ft.Text("🔄 Atualizar Dados", size=14, weight=ft.FontWeight.BOLD),
                    style=ft.ButtonStyle(
                        bgcolor=self.accent_color,
                        color=self.text_primary,
                        padding=20,
                    ),
                    on_click=self.atualizar_dashboard,
                    height=50,
                ),
            ],
            spacing=15,
        )

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Text(
                            "Previsão de Recebimentos",
                            size=28,
                            weight=ft.FontWeight.BOLD,
                            color=self.text_primary,
                        ),
                        padding=ft.Padding(bottom=10),
                    ),
                    stats_cards,
                    ft.Divider(height=30, color="#334155"),
                    ft.Container(
                        content=ft.Text(
                            "Gráfico de Previsão",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color=self.text_primary,
                        ),
                        padding=ft.Padding(bottom=10),
                    ),
                    chart,
                    ft.Divider(height=30, color="#334155"),
                    action_buttons,
                ],
                spacing=20,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=30,
            bgcolor=self.background_color,
            expand=True,
        )

    def create_stat_card(self, title, value, icon, color):
        """Cria um card de estatística"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(icon, size=32),
                            ft.Container(expand=True),
                        ],
                    ),
                    ft.Text(
                        title,
                        size=14,
                        color=self.text_secondary,
                        weight=ft.FontWeight.W_500,
                    ),
                    ft.Text(
                        value,
                        size=24,
                        color=self.text_primary,
                        weight=ft.FontWeight.BOLD,
                    ),
                ],
                spacing=8,
            ),
            bgcolor=self.surface_color,
            padding=20,
            border_radius=12,
            border=ft.Border.all(1, "#334155"),
            width=300,
            height=140,
        )

    def create_bar_chart(self, previsoes):
        """Cria o gráfico de barras"""
        chart = ft.BarChart(
            bar_groups=[
                ft.BarChartGroup(
                    x=0,
                    bar_rods=[
                        ft.BarChartRod(
                            from_y=0,
                            to_y=previsoes['3_meses'],
                            width=40,
                            color=self.accent_color,
                            tooltip=f"R$ {previsoes['3_meses']:.2f}",
                            border_radius=5,
                        ),
                    ],
                ),
                ft.BarChartGroup(
                    x=1,
                    bar_rods=[
                        ft.BarChartRod(
                            from_y=0,
                            to_y=previsoes['6_meses'],
                            width=40,
                            color=self.primary_color,
                            tooltip=f"R$ {previsoes['6_meses']:.2f}",
                            border_radius=5,
                        ),
                    ],
                ),
                ft.BarChartGroup(
                    x=2,
                    bar_rods=[
                        ft.BarChartRod(
                            from_y=0,
                            to_y=previsoes['12_meses'],
                            width=40,
                            color=self.secondary_color,
                            tooltip=f"R$ {previsoes['12_meses']:.2f}",
                            border_radius=5,
                        ),
                    ],
                ),
            ],
            border=ft.Border.all(1, "#334155"),
            left_axis=ft.ChartAxis(
                labels_size=40,
                title=ft.Text("Valor (R$)", color=self.text_secondary, size=12),
                title_size=40,
            ),
            bottom_axis=ft.ChartAxis(
                labels=[
                    ft.ChartAxisLabel(value=0, label=ft.Text("3 Meses", color=self.text_secondary)),
                    ft.ChartAxisLabel(value=1, label=ft.Text("6 Meses", color=self.text_secondary)),
                    ft.ChartAxisLabel(value=2, label=ft.Text("12 Meses", color=self.text_secondary)),
                ],
                labels_size=40,
            ),
            horizontal_grid_lines=ft.ChartGridLines(
                color="#334155",
                width=1,
                dash_pattern=[3, 3],
            ),
            tooltip_bgcolor="#1e293b",
            max_y=previsoes['12_meses'] * 1.2 if previsoes['12_meses'] > 0 else 1000,
            interactive=True,
            expand=True,
        )

        return ft.Container(
            content=chart,
            bgcolor=self.surface_color,
            padding=20,
            border_radius=12,
            border=ft.Border.all(1, "#334155"),
            height=400,
        )

    def calcular_previsoes(self):
        """Calcula previsões de recebimento"""
        hoje = datetime.now().date()

        # 3 meses
        data_3m = hoje + timedelta(days=90)
        valor_3m = self.session.query(Lancamento).filter(
            and_(
                Lancamento.status_pago == False,
                Lancamento.data_vencimento <= data_3m,
            )
        ).all()
        total_3m = sum(l.valor_esperado for l in valor_3m)

        # 6 meses
        data_6m = hoje + timedelta(days=180)
        valor_6m = self.session.query(Lancamento).filter(
            and_(
                Lancamento.status_pago == False,
                Lancamento.data_vencimento <= data_6m,
            )
        ).all()
        total_6m = sum(l.valor_esperado for l in valor_6m)

        # 12 meses
        data_12m = hoje + timedelta(days=365)
        valor_12m = self.session.query(Lancamento).filter(
            and_(
                Lancamento.status_pago == False,
                Lancamento.data_vencimento <= data_12m,
            )
        ).all()
        total_12m = sum(l.valor_esperado for l in valor_12m)

        # Total pendente
        total_pendente = self.session.query(Lancamento).filter_by(status_pago=False).all()
        total_pend = sum(l.valor_esperado for l in total_pendente)

        return {
            '3_meses': total_3m,
            '6_meses': total_6m,
            '12_meses': total_12m,
            'total_pendente': total_pend,
        }

    def build_crm_tab(self):
        """Constrói a aba de CRM - Gestão de Leads"""
        from database import Lead, Corretor, Interacao, Usuario
        from datetime import datetime, timedelta

        # Buscar todos os leads
        leads = self.session.query(Lead).order_by(Lead.data_criacao.desc()).all()
        corretores = self.session.query(Corretor).all()

        # Estatísticas
        total_leads = len(leads)
        novos = len([l for l in leads if l.status == 'NOVO'])
        qualificados = len([l for l in leads if l.status == 'QUALIFICADO'])
        propostas = len([l for l in leads if l.status == 'PROPOSTA'])
        ganhos = len([l for l in leads if l.status == 'GANHO'])

        def adicionar_lead(e):
            """Adiciona novo lead"""
            print("[DEBUG] Botão Adicionar Lead clicado!")  # Debug

            nome_field = ft.TextField(label="Nome *", width=250)
            email_field = ft.TextField(label="E-mail", width=250)
            telefone_field = ft.TextField(label="Telefone *", width=200)
            produto_field = ft.TextField(label="Produto de Interesse", width=250)
            origem_field = ft.Dropdown(
                label="Origem",
                width=200,
                options=[
                    ft.dropdown.Option("Google Ads"),
                    ft.dropdown.Option("Facebook"),
                    ft.dropdown.Option("Instagram"),
                    ft.dropdown.Option("Indicação"),
                    ft.dropdown.Option("Site"),
                    ft.dropdown.Option("Telefone"),
                    ft.dropdown.Option("WhatsApp"),
                ],
            )
            corretor_dropdown = ft.Dropdown(
                label="Corretor Responsável",
                width=250,
                options=[ft.dropdown.Option(key=str(c.id), text=c.nome) for c in corretores],
            )

            def salvar_lead(e):
                print("[DEBUG] Salvando lead...")  # Debug
                try:
                    if not nome_field.value or not telefone_field.value:
                        self.show_snackbar("❌ Nome e telefone são obrigatórios!", self.error_color)
                        return

                    novo_lead = Lead(
                        nome=nome_field.value,
                        email=email_field.value if email_field.value else None,
                        telefone=telefone_field.value,
                        produto_interesse=produto_field.value if produto_field.value else None,
                        origem=origem_field.value if origem_field.value else None,
                        corretor_id=int(corretor_dropdown.value) if corretor_dropdown.value else None,
                        status='NOVO',
                    )

                    self.session.add(novo_lead)
                    self.session.commit()
                    print(f"[DEBUG] Lead {novo_lead.nome} salvo com ID {novo_lead.id}")  # Debug

                    self.show_snackbar(f"✅ Lead {nome_field.value} adicionado!", self.accent_color)

                    dialog.open = False
                    self.page.update()

                    # Recarregar a aba CRM
                    self.page.clean()
                    self.build_ui()
                    self.page.update()

                except Exception as ex:
                    print(f"[ERROR] Erro ao salvar lead: {ex}")  # Debug
                    self.show_snackbar(f"❌ Erro: {str(ex)}", self.error_color)

            dialog = ft.AlertDialog(
                title=ft.Text("➕ Novo Lead"),
                content=ft.Column([
                    nome_field, telefone_field, email_field, produto_field, origem_field, corretor_dropdown
                ], tight=True, spacing=10, scroll=ft.ScrollMode.AUTO, height=400),
                actions=[
                    ft.TextButton(
                        content=ft.Text("Cancelar"),
                        on_click=lambda e: (setattr(dialog, 'open', False), self.page.update())
                    ),
                    ft.FilledButton(
                        content=ft.Text("Salvar"),
                        on_click=salvar_lead
                    ),
                ],
            )

            self.page.dialog = dialog
            dialog.open = True
            self.page.update()
            print("[DEBUG] Dialog aberto")  # Debug

        def editar_lead(lead):
            """Edita um lead existente"""
            print(f"[DEBUG] Editando lead {lead.id}: {lead.nome}")  # Debug

            nome_field = ft.TextField(label="Nome *", value=lead.nome, width=250)
            email_field = ft.TextField(label="E-mail", value=lead.email or "", width=250)
            telefone_field = ft.TextField(label="Telefone *", value=lead.telefone, width=200)
            produto_field = ft.TextField(label="Produto", value=lead.produto_interesse or "", width=250)
            status_dropdown = ft.Dropdown(
                label="Status",
                width=200,
                value=lead.status,
                options=[
                    ft.dropdown.Option("NOVO"),
                    ft.dropdown.Option("CONTATO"),
                    ft.dropdown.Option("QUALIFICADO"),
                    ft.dropdown.Option("PROPOSTA"),
                    ft.dropdown.Option("GANHO"),
                    ft.dropdown.Option("PERDIDO"),
                ],
            )
            corretor_dropdown = ft.Dropdown(
                label="Corretor",
                width=250,
                value=str(lead.corretor_id) if lead.corretor_id else None,
                options=[ft.dropdown.Option(key=str(c.id), text=c.nome) for c in corretores],
            )
            obs_field = ft.TextField(label="Observações", value=lead.observacoes or "", width=400, multiline=True, min_lines=3)

            def salvar_edicao(e):
                print(f"[DEBUG] Salvando edição do lead {lead.id}...")  # Debug
                try:
                    if not nome_field.value or not telefone_field.value:
                        self.show_snackbar("❌ Nome e telefone são obrigatórios!", self.error_color)
                        return

                    lead.nome = nome_field.value
                    lead.email = email_field.value if email_field.value else None
                    lead.telefone = telefone_field.value
                    lead.produto_interesse = produto_field.value if produto_field.value else None
                    lead.status = status_dropdown.value
                    lead.corretor_id = int(corretor_dropdown.value) if corretor_dropdown.value else None
                    lead.observacoes = obs_field.value if obs_field.value else None
                    lead.data_ultima_interacao = datetime.now()

                    self.session.commit()
                    print(f"[DEBUG] Lead {lead.id} atualizado")  # Debug
                    self.show_snackbar("✅ Lead atualizado!", self.accent_color)

                    dialog.open = False
                    self.page.update()

                    self.page.clean()
                    self.build_ui()
                    self.page.update()

                except Exception as ex:
                    print(f"[ERROR] Erro ao atualizar lead: {ex}")  # Debug
                    self.show_snackbar(f"❌ Erro: {str(ex)}", self.error_color)

            dialog = ft.AlertDialog(
                title=ft.Text(f"✏️ Editar Lead: {lead.nome}"),
                content=ft.Column([
                    nome_field, telefone_field, email_field, produto_field, status_dropdown, corretor_dropdown, obs_field
                ], tight=True, spacing=10, scroll=ft.ScrollMode.AUTO, height=450),
                actions=[
                    ft.TextButton(
                        content=ft.Text("Cancelar"),
                        on_click=lambda e: (setattr(dialog, 'open', False), self.page.update())
                    ),
                    ft.FilledButton(
                        content=ft.Text("Salvar"),
                        on_click=salvar_edicao
                    ),
                ],
            )

            self.page.dialog = dialog
            dialog.open = True
            self.page.update()
            print(f"[DEBUG] Dialog de edição aberto para lead {lead.id}")  # Debug

        # Construir lista de leads por status
        def get_status_color(status):
            colors = {
                'NOVO': '#3b82f6',
                'CONTATO': '#8b5cf6',
                'QUALIFICADO': '#f59e0b',
                'PROPOSTA': '#10b981',
                'GANHO': '#22c55e',
                'PERDIDO': '#ef4444',
            }
            return colors.get(status, '#6b7280')

        leads_list = []
        for lead in leads[:50]:  # Mostrar últimos 50
            status_color = get_status_color(lead.status)

            leads_list.append(
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            width=4,
                            height=60,
                            bgcolor=status_color,
                            border_radius=2,
                        ),
                        ft.Column([
                            ft.Text(lead.nome, size=16, weight=ft.FontWeight.BOLD, color=self.text_primary),
                            ft.Text(f"📞 {lead.telefone} | {lead.produto_interesse or 'N/A'}", size=12, color=self.text_secondary),
                        ], spacing=2),
                        ft.Container(expand=True),
                        ft.Container(
                            content=ft.Text(lead.status, size=12, weight=ft.FontWeight.BOLD),
                            bgcolor=status_color + "30",
                            padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                            border_radius=5,
                        ),
                        ft.Text(f"{lead.origem or 'N/A'}", size=12, color=self.text_secondary),
                        ft.OutlinedButton(
                            content=ft.Text("✏️", size=14),
                            width=40,
                            on_click=lambda e, l=lead: editar_lead(l),
                        ),
                    ], spacing=10),
                    bgcolor=self.surface_color,
                    padding=15,
                    border_radius=10,
                    border=ft.Border.all(1, "#334155"),
                )
            )

        return ft.Container(
            content=ft.Column([
                # Header com estatísticas
                ft.Row([
                    ft.Text("🎯 CRM - Gestão de Leads", size=24, weight=ft.FontWeight.BOLD, color=self.text_primary),
                    ft.Container(expand=True),
                    ft.FilledButton(
                        content=ft.Text("➕ Novo Lead", size=14),
                        style=ft.ButtonStyle(bgcolor=self.accent_color),
                        on_click=adicionar_lead,
                    ),
                ]),

                ft.Divider(height=10, color="#334155"),

                # KPIs
                ft.Row([
                    ft.Container(
                        content=ft.Column([
                            ft.Text(str(total_leads), size=32, weight=ft.FontWeight.BOLD, color=self.primary_color),
                            ft.Text("Total Leads", size=14, color=self.text_secondary),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        bgcolor=self.surface_color,
                        padding=20,
                        border_radius=10,
                        expand=True,
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text(str(novos), size=32, weight=ft.FontWeight.BOLD, color="#3b82f6"),
                            ft.Text("Novos", size=14, color=self.text_secondary),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        bgcolor=self.surface_color,
                        padding=20,
                        border_radius=10,
                        expand=True,
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text(str(qualificados), size=32, weight=ft.FontWeight.BOLD, color="#f59e0b"),
                            ft.Text("Qualificados", size=14, color=self.text_secondary),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        bgcolor=self.surface_color,
                        padding=20,
                        border_radius=10,
                        expand=True,
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text(str(propostas), size=32, weight=ft.FontWeight.BOLD, color=self.accent_color),
                            ft.Text("Em Proposta", size=14, color=self.text_secondary),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        bgcolor=self.surface_color,
                        padding=20,
                        border_radius=10,
                        expand=True,
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text(str(ganhos), size=32, weight=ft.FontWeight.BOLD, color="#22c55e"),
                            ft.Text("Ganhos", size=14, color=self.text_secondary),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        bgcolor=self.surface_color,
                        padding=20,
                        border_radius=10,
                        expand=True,
                    ),
                ], spacing=10),

                ft.Divider(height=20, color="#334155"),

                # Lista de leads
                ft.Column(
                    controls=leads_list if leads_list else [
                        ft.Container(
                            content=ft.Text("Nenhum lead cadastrado", size=16, color=self.text_secondary),
                            padding=20,
                        )
                    ],
                    spacing=8,
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                ),
            ], spacing=15, expand=True),
            padding=20,
            expand=True,
        )

    def build_propostas_tab(self):
        """Constrói a aba de propostas"""
        from database import Proposta, Corretor, Seguradora

        # Buscar todas as propostas
        propostas = self.session.query(Proposta).order_by(Proposta.data_venda.desc()).all()

        def editar_proposta(proposta):
            """Edita uma proposta existente"""
            # Buscar corretores e seguradoras para os dropdowns
            corretores = self.session.query(Corretor).all()
            seguradoras = self.session.query(Seguradora).all()

            cliente_field = ft.TextField(label="Cliente", value=proposta.cliente_nome, width=300)
            cpf_field = ft.TextField(label="CPF/CNPJ", value=proposta.cliente_cpf or "", width=200)
            valor_field = ft.TextField(label="Valor Bruto (R$)", value=str(proposta.valor_bruto), width=150, keyboard_type=ft.KeyboardType.NUMBER)

            corretor_dropdown = ft.Dropdown(
                label="Corretor",
                width=250,
                options=[ft.dropdown.Option(key=str(c.id), text=c.nome) for c in corretores],
                value=str(proposta.corretor_id),
            )

            seguradora_dropdown = ft.Dropdown(
                label="Seguradora",
                width=250,
                options=[ft.dropdown.Option(key=str(s.id), text=s.nome) for s in seguradoras],
                value=str(proposta.seguradora_id),
            )

            def salvar_edicao(e):
                try:
                    proposta.cliente_nome = cliente_field.value
                    proposta.cliente_cpf = cpf_field.value
                    proposta.valor_bruto = float(valor_field.value)
                    proposta.corretor_id = int(corretor_dropdown.value)
                    proposta.seguradora_id = int(seguradora_dropdown.value)

                    self.session.commit()
                    self.show_snackbar("✅ Proposta atualizada!", self.accent_color)

                    dialog.open = False
                    self.page.update()

                    # Recarregar
                    self.page.clean()
                    self.build_ui()
                    self.page.update()

                except Exception as ex:
                    self.show_snackbar(f"❌ Erro: {str(ex)}", self.error_color)

            dialog = ft.AlertDialog(
                title=ft.Text(f"Editar Proposta #{proposta.id}"),
                content=ft.Column([
                    cliente_field,
                    cpf_field,
                    valor_field,
                    corretor_dropdown,
                    seguradora_dropdown,
                ], tight=True, spacing=10, scroll=ft.ScrollMode.AUTO),
                actions=[
                    ft.TextButton(content=ft.Text("Cancelar"), on_click=lambda e: (setattr(dialog, 'open', False), self.page.update())),
                    ft.FilledButton(content=ft.Text("Salvar"), on_click=salvar_edicao),
                ],
            )

            self.page.dialog = dialog
            dialog.open = True
            self.page.update()

        def excluir_proposta(proposta):
            """Exclui uma proposta"""
            def confirmar_exclusao(e):
                try:
                    # Excluir lançamentos relacionados primeiro
                    for lanc in proposta.lancamentos:
                        self.session.delete(lanc)

                    # Excluir proposta
                    self.session.delete(proposta)
                    self.session.commit()

                    self.show_snackbar("✅ Proposta excluída!", self.accent_color)

                    dialog.open = False
                    self.page.update()

                    # Recarregar
                    self.page.clean()
                    self.build_ui()
                    self.page.update()

                except Exception as ex:
                    self.show_snackbar(f"❌ Erro: {str(ex)}", self.error_color)

            dialog = ft.AlertDialog(
                title=ft.Text("Confirmar Exclusão"),
                content=ft.Text(f"Deseja realmente excluir a proposta de {proposta.cliente_nome}?\n\nIsso também excluirá todos os lançamentos relacionados."),
                actions=[
                    ft.TextButton(content=ft.Text("Cancelar"), on_click=lambda e: (setattr(dialog, 'open', False), self.page.update())),
                    ft.FilledButton(
                        content=ft.Text("Excluir"),
                        on_click=confirmar_exclusao,
                        style=ft.ButtonStyle(bgcolor=self.error_color)
                    ),
                ],
            )

            self.page.dialog = dialog
            dialog.open = True
            self.page.update()

        # Construir lista de propostas
        propostas_list = []
        for proposta in propostas:
            propostas_list.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Column([
                                ft.Text(f"#{proposta.id} - {proposta.cliente_nome}", size=18, weight=ft.FontWeight.BOLD, color=self.text_primary),
                                ft.Text(f"📋 CPF/CNPJ: {proposta.cliente_cpf or 'N/A'}", size=14, color=self.text_secondary),
                                ft.Text(f"💼 Corretor: {proposta.corretor.nome}", size=14, color=self.text_secondary),
                                ft.Text(f"🏢 Seguradora: {proposta.seguradora.nome}", size=14, color=self.text_secondary),
                            ], spacing=5),
                            ft.Container(expand=True),
                            ft.Column([
                                ft.Text(f"R$ {proposta.valor_bruto:,.2f}", size=24, weight=ft.FontWeight.BOLD, color=self.accent_color),
                                ft.Text(f"Data: {proposta.data_venda.strftime('%d/%m/%Y')}", size=12, color=self.text_secondary),
                            ], horizontal_alignment=ft.CrossAxisAlignment.END),
                            ft.Row([
                                ft.OutlinedButton(
                                    content=ft.Text("✏️ Editar", size=12),
                                    style=ft.ButtonStyle(color=self.primary_color),
                                    on_click=lambda e, p=proposta: editar_proposta(p),
                                ),
                                ft.OutlinedButton(
                                    content=ft.Text("🗑️ Excluir", size=12),
                                    style=ft.ButtonStyle(color=self.error_color),
                                    on_click=lambda e, p=proposta: excluir_proposta(p),
                                ),
                            ], spacing=5),
                        ]),
                    ]),
                    bgcolor=self.surface_color,
                    padding=20,
                    border_radius=10,
                    border=ft.Border.all(1, "#334155"),
                )
            )

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("📄 Gestão de Propostas", size=24, weight=ft.FontWeight.BOLD, color=self.text_primary),
                    ft.Container(expand=True),
                    ft.Text(f"Total: {len(propostas)} proposta(s)", size=16, color=self.text_secondary),
                ]),
                ft.Divider(height=20, color="#334155"),
                ft.Column(
                    controls=propostas_list if propostas_list else [
                        ft.Container(
                            content=ft.Text("Nenhuma proposta cadastrada", size=16, color=self.text_secondary),
                            padding=20,
                        )
                    ],
                    spacing=10,
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                ),
            ], spacing=20, expand=True),
            padding=20,
            expand=True,
        )

    def build_lancamentos_tab(self):
        """Constrói a aba de lançamentos"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Lançamentos Financeiros",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color=self.text_primary,
                    ),
                    ft.Text(
                        "Em desenvolvimento...",
                        size=16,
                        color=self.text_secondary,
                    ),
                ],
            ),
            padding=30,
        )

    def build_repasses_tab(self):
        """Constrói a aba de repasses para corretores"""
        # Buscar todos os corretores
        corretores = self.session.query(Corretor).all()

        if not corretores:
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            "Repasses aos Corretores",
                            size=28,
                            weight=ft.FontWeight.BOLD,
                            color=self.text_primary,
                        ),
                        ft.Divider(height=20, color="#334155"),
                        ft.Text(
                            "Nenhum corretor cadastrado no sistema.",
                            size=16,
                            color=self.text_secondary,
                        ),
                    ],
                ),
                padding=30,
            )

        # Calcular valores para cada corretor
        corretores_cards = []
        total_geral_liquido = 0

        for corretor in corretores:
            # Calcular total líquido do corretor
            dados_corretor = self.calcular_repasse_corretor(corretor)
            total_geral_liquido += dados_corretor['total_liquido']

            # Criar card do corretor
            card = self.create_corretor_card(corretor, dados_corretor)
            corretores_cards.append(card)

        # Card de total geral
        total_card = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text("💰", size=40),
                    ft.Column(
                        controls=[
                            ft.Text(
                                "TOTAL GERAL A REPASSAR",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=self.text_secondary,
                            ),
                            ft.Text(
                                f"R$ {total_geral_liquido:.2f}",
                                size=32,
                                weight=ft.FontWeight.BOLD,
                                color=self.accent_color,
                            ),
                        ],
                        spacing=5,
                    ),
                ],
                spacing=20,
            ),
            bgcolor=self.surface_color,
            padding=25,
            border_radius=12,
            border=ft.Border.all(2, self.accent_color),
        )

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(
                                "Repasses aos Corretores",
                                size=28,
                                weight=ft.FontWeight.BOLD,
                                color=self.text_primary,
                            ),
                            ft.Container(expand=True),
                            ft.FilledButton(
                                content=ft.Text("🔄 Atualizar Valores", size=14),
                                style=ft.ButtonStyle(
                                    bgcolor=self.primary_color,
                                    color=self.text_primary,
                                ),
                                on_click=self.atualizar_repasses,
                            ),
                        ],
                    ),
                    ft.Divider(height=20, color="#334155"),
                    total_card,
                    ft.Divider(height=20, color="#334155"),
                    ft.Column(
                        controls=corretores_cards,
                        spacing=15,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                ],
                spacing=20,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=30,
            bgcolor=self.background_color,
            expand=True,
        )

    def calcular_repasse_corretor(self, corretor):
        """Calcula valores de repasse para um corretor"""
        # Buscar todas as propostas do corretor
        propostas = corretor.propostas

        total_bruto = 0
        total_comissao_bruto = 0
        total_impostos = 0
        total_liquido = 0
        num_propostas = len(propostas)
        num_lancamentos_pendentes = 0
        valor_pendente = 0
        valor_pago = 0

        for proposta in propostas:
            # Valor bruto da apólice
            total_bruto += proposta.valor_bruto

            # Calcular comissão bruta
            comissao_bruto = proposta.valor_bruto * (corretor.comissao_padrao / 100)
            total_comissao_bruto += comissao_bruto

            # Calcular impostos e valor líquido
            liquido, detalhes_impostos = self.finance_engine.calcular_impostos(comissao_bruto)
            total_impostos += detalhes_impostos['total_impostos']
            total_liquido += liquido

            # Calcular valores de lançamentos
            for lancamento in proposta.lancamentos:
                if lancamento.status_pago:
                    valor_pago += lancamento.valor_esperado
                else:
                    num_lancamentos_pendentes += 1
                    valor_pendente += lancamento.valor_esperado

        return {
            'total_bruto': total_bruto,
            'total_comissao_bruto': total_comissao_bruto,
            'total_impostos': total_impostos,
            'total_liquido': total_liquido,
            'num_propostas': num_propostas,
            'num_lancamentos_pendentes': num_lancamentos_pendentes,
            'valor_pendente': valor_pendente,
            'valor_pago': valor_pago,
        }

    def create_corretor_card(self, corretor, dados):
        """Cria um card para o corretor com suas informações"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    # Cabeçalho do card
                    ft.Row(
                        controls=[
                            ft.Text("👤", size=32),
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        corretor.nome,
                                        size=20,
                                        weight=ft.FontWeight.BOLD,
                                        color=self.text_primary,
                                    ),
                                    ft.Text(
                                        f"Comissão padrão: {corretor.comissao_padrao}%",
                                        size=14,
                                        color=self.text_secondary,
                                    ),
                                ],
                                spacing=2,
                            ),
                            ft.Container(expand=True),
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        "TOTAL LÍQUIDO",
                                        size=12,
                                        color=self.text_secondary,
                                        text_align=ft.TextAlign.RIGHT,
                                    ),
                                    ft.Text(
                                        f"R$ {dados['total_liquido']:.2f}",
                                        size=24,
                                        weight=ft.FontWeight.BOLD,
                                        color=self.accent_color,
                                        text_align=ft.TextAlign.RIGHT,
                                    ),
                                ],
                                spacing=2,
                                horizontal_alignment=ft.CrossAxisAlignment.END,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    ft.Divider(height=10, color="#334155"),
                    # Detalhes financeiros
                    ft.Row(
                        controls=[
                            self.create_info_column(
                                "Apólices",
                                f"R$ {dados['total_bruto']:.2f}",
                                f"{dados['num_propostas']} propostas",
                            ),
                            ft.VerticalDivider(width=1, color="#334155"),
                            self.create_info_column(
                                "Comissão Bruta",
                                f"R$ {dados['total_comissao_bruto']:.2f}",
                                f"{corretor.comissao_padrao}% do total",
                            ),
                            ft.VerticalDivider(width=1, color="#334155"),
                            self.create_info_column(
                                "Impostos",
                                f"R$ {dados['total_impostos']:.2f}",
                                "Descontados",
                            ),
                            ft.VerticalDivider(width=1, color="#334155"),
                            self.create_info_column(
                                "Pendente",
                                f"R$ {dados['valor_pendente']:.2f}",
                                f"{dados['num_lancamentos_pendentes']} lançamentos",
                            ),
                            ft.VerticalDivider(width=1, color="#334155"),
                            self.create_info_column(
                                "Pago",
                                f"R$ {dados['valor_pago']:.2f}",
                                "Já repassado",
                            ),
                        ],
                        spacing=15,
                        wrap=True,
                    ),
                    ft.Divider(height=10, color="#334155"),
                    # Botões de ação
                    ft.Row(
                        controls=[
                            ft.FilledButton(
                                content=ft.Text("📄 Gerar Extrato PDF", size=14),
                                style=ft.ButtonStyle(
                                    bgcolor=self.error_color,
                                    color=self.text_primary,
                                ),
                                on_click=lambda e, c=corretor, d=dados: self.gerar_extrato_pdf(c, d),
                            ),
                            ft.OutlinedButton(
                                content=ft.Text("ℹ️ Ver Detalhes", size=14),
                                style=ft.ButtonStyle(
                                    color=self.primary_color,
                                ),
                                on_click=lambda e, c=corretor: self.ver_detalhes_corretor(c),
                            ),
                        ],
                        spacing=10,
                    ),
                ],
                spacing=15,
            ),
            bgcolor=self.surface_color,
            padding=20,
            border_radius=12,
            border=ft.Border.all(1, "#334155"),
        )

    def create_info_column(self, titulo, valor, descricao):
        """Cria uma coluna de informação"""
        return ft.Column(
            controls=[
                ft.Text(
                    titulo,
                    size=12,
                    color=self.text_secondary,
                    weight=ft.FontWeight.W_500,
                ),
                ft.Text(
                    valor,
                    size=16,
                    color=self.text_primary,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    descricao,
                    size=11,
                    color=self.text_secondary,
                ),
            ],
            spacing=3,
            horizontal_alignment=ft.CrossAxisAlignment.START,
        )

    def gerar_extrato_pdf(self, corretor, dados):
        """Gera extrato AVANÇADO em PDF para o corretor com cruzamento automático"""
        print(f"[DEBUG] Gerando PDF AVANÇADO para corretor {corretor.id}: {corretor.nome}")  # Debug

        try:
            from pdf_export_avancado import exportar_comissoes_corretor
            import subprocess

            # Gerar PDF avançado com cruzamento automático
            print("[DEBUG] Chamando PDF Avançado com cruzamento de dados...")  # Debug
            pdf_path = exportar_comissoes_corretor(corretor.id)
            print(f"[DEBUG] PDF gerado em: {pdf_path}")  # Debug

            # Abrir PDF automaticamente
            if pdf_path:
                self.show_snackbar(
                    f"✅ PDF completo gerado: {os.path.basename(pdf_path)}",
                    self.accent_color,
                )

                # Abrir o PDF no visualizador padrão
                try:
                    print(f"[DEBUG] Abrindo PDF: {pdf_path}")  # Debug
                    subprocess.Popen([pdf_path], shell=True)
                    print("[DEBUG] PDF aberto com sucesso")  # Debug
                except Exception as e:
                    # Se falhar ao abrir, mostrar caminho
                    print(f"[WARN] Falha ao abrir PDF: {e}")  # Debug
                    self.show_snackbar(
                        f"📁 Salvo em: {pdf_path}",
                        self.primary_color,
                    )

        except ImportError as ie:
            print(f"[ERROR] ImportError: {ie}")  # Debug
            self.show_snackbar(
                "❌ Biblioteca reportlab não instalada! Execute: pip install reportlab",
                self.error_color,
            )
        except Exception as ex:
            print(f"[ERROR] Erro ao gerar PDF: {ex}")  # Debug
            import traceback
            traceback.print_exc()
            self.show_snackbar(
                f"❌ Erro ao gerar PDF: {str(ex)}",
                self.error_color,
            )

    def ver_detalhes_corretor(self, corretor):
        """Mostra detalhes completos do corretor"""
        self.show_snackbar(
            f"Visualizando detalhes de {corretor.nome}... (em desenvolvimento)",
            self.primary_color,
        )

    def verificar_parcelas_vencidas(self, e):
        """Verifica parcelas vencidas e envia emails"""
        print("[DEBUG] Verificando parcelas vencidas...")

        try:
            from sistema_parcelas import GerenciadorParcelas

            gerenciador = GerenciadorParcelas(session=self.session)
            resultado = gerenciador.notificar_parcelas_vencidas()
            gerenciador.fechar()

            mensagem = f"✅ Verificação concluída!\n"
            mensagem += f"📊 {resultado['total_vencidas']} parcelas vencidas\n"
            mensagem += f"📧 {resultado['emails_enviados']} emails enviados\n"

            if resultado['emails_erros'] > 0:
                mensagem += f"⚠️ {resultado['emails_erros']} erros"

            self.show_snackbar(mensagem, self.accent_color if resultado['emails_erros'] == 0 else self.error_color)

        except Exception as ex:
            print(f"[ERROR] Erro ao verificar parcelas: {ex}")
            import traceback
            traceback.print_exc()
            self.show_snackbar(f"❌ Erro: {str(ex)}", self.error_color)

    def criar_parcelas_proposta(self, proposta_id: int, data_quitacao=None):
        """Cria parcelas automáticas quando uma proposta tem primeira parcela quitada"""
        print(f"[DEBUG] Criando parcelas para proposta {proposta_id}...")

        try:
            from sistema_parcelas import GerenciadorParcelas
            from database import Proposta, Lancamento

            # Buscar proposta
            proposta = self.session.query(Proposta).get(proposta_id)
            if not proposta:
                self.show_snackbar("❌ Proposta não encontrada", self.error_color)
                return

            # Buscar lançamento da proposta
            lancamento = self.session.query(Lancamento).filter_by(proposta_id=proposta_id).first()
            if not lancamento:
                self.show_snackbar("❌ Lançamento não encontrado", self.error_color)
                return

            if data_quitacao is None:
                data_quitacao = datetime.now().date()

            gerenciador = GerenciadorParcelas(session=self.session)
            parcelas = gerenciador.criar_parcelas_automaticas(
                lancamento_id=lancamento.id,
                proposta_id=proposta.id,
                corretor_id=proposta.corretor_id,
                valor_total=lancamento.valor_liquido,
                data_primeira_quitacao=data_quitacao
            )
            gerenciador.fechar()

            self.show_snackbar(
                f"✅ {len(parcelas)} parcelas criadas!\nVencimentos: 30, 60 e 90 dias",
                self.accent_color
            )

        except Exception as ex:
            print(f"[ERROR] Erro ao criar parcelas: {ex}")
            import traceback
            traceback.print_exc()
            self.show_snackbar(f"❌ Erro: {str(ex)}", self.error_color)

    def atualizar_repasses(self, e):
        """Atualiza os valores de repasse"""
        self.show_snackbar("Valores atualizados!", self.accent_color)
        self.page.clean()
        self.build_ui()
        self.page.update()

    def build_financeiro_tab(self):
        """Constrói a aba de Controle Financeiro Completo"""
        from modulo_financeiro import ControleFinanceiro, ContaBancaria, CategoriaFinanceira, TransacaoFinanceira, Meta
        from datetime import datetime, timedelta
        from calendar import monthrange

        print("[DEBUG] Construindo aba Financeiro...")  # Debug

        # Inicializar controle financeiro
        controle = ControleFinanceiro(session=self.session)

        # Período padrão: mês atual
        hoje = datetime.now()
        primeiro_dia = datetime(hoje.year, hoje.month, 1)
        ultimo_dia_num = monthrange(hoje.year, hoje.month)[1]
        ultimo_dia = datetime(hoje.year, hoje.month, ultimo_dia_num)

        # ===== SEÇÃO 1: FLUXO DE CAIXA =====
        fluxo = controle.obter_fluxo_caixa(primeiro_dia, ultimo_dia)

        fluxo_section = ft.Container(
            content=ft.Column([
                ft.Text("💵 Fluxo de Caixa", size=22, weight=ft.FontWeight.BOLD, color=self.text_primary),
                ft.Text(f"Período: {fluxo['periodo']['inicio']} a {fluxo['periodo']['fim']}", size=14, color=self.text_secondary),
                ft.Divider(height=10, color="#334155"),

                # Resumo financeiro
                ft.Row([
                    ft.Container(
                        content=ft.Column([
                            ft.Text("📈 Receitas", size=14, color=self.text_secondary),
                            ft.Text(f"R$ {fluxo['total_receitas']:,.2f}", size=24, weight=ft.FontWeight.BOLD, color=self.accent_color),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        bgcolor=self.surface_color,
                        padding=20,
                        border_radius=10,
                        expand=True,
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("📉 Despesas", size=14, color=self.text_secondary),
                            ft.Text(f"R$ {fluxo['total_despesas']:,.2f}", size=24, weight=ft.FontWeight.BOLD, color=self.error_color),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        bgcolor=self.surface_color,
                        padding=20,
                        border_radius=10,
                        expand=True,
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("💰 Saldo", size=14, color=self.text_secondary),
                            ft.Text(
                                f"R$ {fluxo['saldo']:,.2f}",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=self.accent_color if fluxo['saldo'] >= 0 else self.error_color
                            ),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        bgcolor=self.surface_color,
                        padding=20,
                        border_radius=10,
                        expand=True,
                    ),
                ], spacing=10),
            ], spacing=10),
            bgcolor=self.background_color,
            padding=20,
            border_radius=10,
        )

        # ===== SEÇÃO 2: CONTAS A RECEBER =====
        contas_receber = controle.obter_contas_receber()
        contas_receber_vencidas = controle.obter_contas_receber(vencidas=True)

        receber_items = []
        for conta in contas_receber[:10]:  # Mostrar últimas 10
            is_vencida = conta.data_vencimento and conta.data_vencimento < hoje.date()
            receber_items.append(
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            width=4,
                            height=50,
                            bgcolor=self.error_color if is_vencida else self.accent_color,
                            border_radius=2,
                        ),
                        ft.Column([
                            ft.Text(conta.descricao, size=14, weight=ft.FontWeight.BOLD, color=self.text_primary),
                            ft.Text(
                                f"Venc: {conta.data_vencimento.strftime('%d/%m/%Y') if conta.data_vencimento else 'Sem data'}",
                                size=12,
                                color=self.error_color if is_vencida else self.text_secondary
                            ),
                        ], spacing=2),
                        ft.Container(expand=True),
                        ft.Text(f"R$ {conta.valor:,.2f}", size=16, weight=ft.FontWeight.BOLD, color=self.accent_color),
                    ], spacing=10),
                    bgcolor=self.surface_color,
                    padding=15,
                    border_radius=8,
                    border=ft.Border.all(1, "#334155"),
                )
            )

        receber_section = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("📥 Contas a Receber", size=20, weight=ft.FontWeight.BOLD, color=self.text_primary),
                    ft.Container(expand=True),
                    ft.Container(
                        content=ft.Text(f"{len(contas_receber_vencidas)} Vencidas", size=12, weight=ft.FontWeight.BOLD),
                        bgcolor=self.error_color + "30",
                        padding=ft.Padding(left=10, right=10, top=5, bottom=5),
                        border_radius=5,
                    ),
                ]),
                ft.Divider(height=10, color="#334155"),
                ft.Column(receber_items if receber_items else [
                    ft.Text("Nenhuma conta a receber", size=14, color=self.text_secondary, italic=True)
                ], spacing=8, scroll=ft.ScrollMode.AUTO, height=250),
            ], spacing=10),
            bgcolor=self.background_color,
            padding=20,
            border_radius=10,
        )

        # ===== SEÇÃO 3: CONTAS A PAGAR =====
        contas_pagar = controle.obter_contas_pagar()
        contas_pagar_vencidas = controle.obter_contas_pagar(vencidas=True)

        pagar_items = []
        for conta in contas_pagar[:10]:  # Mostrar últimas 10
            is_vencida = conta.data_vencimento and conta.data_vencimento < hoje.date()
            pagar_items.append(
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            width=4,
                            height=50,
                            bgcolor=self.error_color if is_vencida else "#f59e0b",
                            border_radius=2,
                        ),
                        ft.Column([
                            ft.Text(conta.descricao, size=14, weight=ft.FontWeight.BOLD, color=self.text_primary),
                            ft.Text(
                                f"Venc: {conta.data_vencimento.strftime('%d/%m/%Y') if conta.data_vencimento else 'Sem data'}",
                                size=12,
                                color=self.error_color if is_vencida else self.text_secondary
                            ),
                        ], spacing=2),
                        ft.Container(expand=True),
                        ft.Text(f"R$ {conta.valor:,.2f}", size=16, weight=ft.FontWeight.BOLD, color=self.error_color),
                    ], spacing=10),
                    bgcolor=self.surface_color,
                    padding=15,
                    border_radius=8,
                    border=ft.Border.all(1, "#334155"),
                )
            )

        pagar_section = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("📤 Contas a Pagar", size=20, weight=ft.FontWeight.BOLD, color=self.text_primary),
                    ft.Container(expand=True),
                    ft.Container(
                        content=ft.Text(f"{len(contas_pagar_vencidas)} Vencidas", size=12, weight=ft.FontWeight.BOLD),
                        bgcolor=self.error_color + "30",
                        padding=ft.Padding(left=10, right=10, top=5, bottom=5),
                        border_radius=5,
                    ),
                ]),
                ft.Divider(height=10, color="#334155"),
                ft.Column(pagar_items if pagar_items else [
                    ft.Text("Nenhuma conta a pagar", size=14, color=self.text_secondary, italic=True)
                ], spacing=8, scroll=ft.ScrollMode.AUTO, height=250),
            ], spacing=10),
            bgcolor=self.background_color,
            padding=20,
            border_radius=10,
        )

        # ===== SEÇÃO 4: DRE (Demonstração do Resultado) =====
        dre = controle.gerar_dre(hoje.month, hoje.year)

        dre_section = ft.Container(
            content=ft.Column([
                ft.Text("📊 DRE - Demonstração do Resultado do Exercício", size=20, weight=ft.FontWeight.BOLD, color=self.text_primary),
                ft.Text(f"Período: {dre['periodo']}", size=14, color=self.text_secondary),
                ft.Divider(height=10, color="#334155"),

                # Tabela DRE
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text("Receita Bruta", size=14, weight=ft.FontWeight.BOLD),
                            ft.Container(expand=True),
                            ft.Text(f"R$ {dre['receita_bruta']:,.2f}", size=14, weight=ft.FontWeight.BOLD, color=self.accent_color),
                        ]),
                        ft.Divider(height=1, color="#334155"),
                        ft.Row([
                            ft.Text("(-) Custos Operacionais", size=14),
                            ft.Container(expand=True),
                            ft.Text(f"R$ {dre['custos_operacionais']:,.2f}", size=14, color=self.error_color),
                        ]),
                        ft.Divider(height=1, color="#334155"),
                        ft.Row([
                            ft.Text("(=) Lucro Operacional", size=16, weight=ft.FontWeight.BOLD),
                            ft.Container(expand=True),
                            ft.Text(
                                f"R$ {dre['lucro_operacional']:,.2f}",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=self.accent_color if dre['lucro_operacional'] >= 0 else self.error_color
                            ),
                        ]),
                        ft.Divider(height=1, color="#334155"),
                        ft.Row([
                            ft.Text("Margem de Lucro", size=14),
                            ft.Container(expand=True),
                            ft.Text(f"{dre['margem_lucro']:.1f}%", size=14, weight=ft.FontWeight.BOLD),
                        ]),
                    ], spacing=10),
                    bgcolor=self.surface_color,
                    padding=20,
                    border_radius=10,
                ),
            ], spacing=10),
            bgcolor=self.background_color,
            padding=20,
            border_radius=10,
        )

        # ===== SEÇÃO 5: GERENCIAMENTO DE PARCELAS =====
        from sistema_parcelas import Parcela

        todas_parcelas = self.session.query(Parcela).order_by(Parcela.data_vencimento).all()
        parcelas_pendentes = [p for p in todas_parcelas if p.status in ['PENDENTE', 'VENCIDA', 'NOTIFICADA']]

        def quitar_parcela_ui(parcela_id):
            """Interface para quitar parcela"""
            from sistema_parcelas import GerenciadorParcelas
            gerenciador = GerenciadorParcelas(session=self.session)

            if gerenciador.quitar_parcela(parcela_id):
                self.show_snackbar("✅ Parcela quitada!", self.accent_color)
                self.page.clean()
                self.build_ui()
                self.page.update()
            else:
                self.show_snackbar("❌ Erro ao quitar parcela", self.error_color)

            gerenciador.fechar()

        parcelas_items = []
        for parcela in parcelas_pendentes[:15]:  # Mostrar até 15
            corretor = parcela.corretor
            proposta = parcela.proposta
            is_vencida = parcela.status in ['VENCIDA', 'NOTIFICADA']
            dias_venc = (datetime.now().date() - parcela.data_vencimento).days if is_vencida else 0

            parcelas_items.append(
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            width=4,
                            height=60,
                            bgcolor=self.error_color if is_vencida else self.primary_color,
                            border_radius=2,
                        ),
                        ft.Column([
                            ft.Text(f"{corretor.nome} - {proposta.cliente_nome}", size=13, weight=ft.FontWeight.BOLD, color=self.text_primary),
                            ft.Text(
                                f"Parcela {parcela.numero_parcela}/3 | Venc: {parcela.data_vencimento.strftime('%d/%m/%Y')}" +
                                (f" | {dias_venc} dias atraso" if is_vencida else ""),
                                size=11,
                                color=self.error_color if is_vencida else self.text_secondary
                            ),
                        ], spacing=2),
                        ft.Container(expand=True),
                        ft.Text(f"R$ {parcela.valor:,.2f}", size=15, weight=ft.FontWeight.BOLD, color=self.text_primary),
                        ft.FilledButton(
                            content=ft.Text("✓ Quitar", size=12),
                            style=ft.ButtonStyle(bgcolor=self.accent_color),
                            on_click=lambda e, pid=parcela.id: quitar_parcela_ui(pid),
                        ),
                    ], spacing=10),
                    bgcolor=self.surface_color,
                    padding=12,
                    border_radius=8,
                    border=ft.Border.all(1, "#334155"),
                )
            )

        parcelas_section = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("💳 Gestão de Parcelas", size=20, weight=ft.FontWeight.BOLD, color=self.text_primary),
                    ft.Container(expand=True),
                    ft.Container(
                        content=ft.Text(f"{len(parcelas_pendentes)} Pendentes", size=12, weight=ft.FontWeight.BOLD),
                        bgcolor=self.primary_color + "30",
                        padding=ft.Padding(left=10, right=10, top=5, bottom=5),
                        border_radius=5,
                    ),
                ]),
                ft.Divider(height=10, color="#334155"),
                ft.Column(parcelas_items if parcelas_items else [
                    ft.Text("✅ Nenhuma parcela pendente", size=14, color=self.text_secondary, italic=True)
                ], spacing=8, scroll=ft.ScrollMode.AUTO, height=300),
            ], spacing=10),
            bgcolor=self.background_color,
            padding=20,
            border_radius=10,
        )

        # ===== SEÇÃO 6: BOTÕES DE AÇÃO =====
        def nova_transacao(e):
            self.show_snackbar("📝 Nova transação (em desenvolvimento)", self.primary_color)

        def gerenciar_categorias(e):
            self.show_snackbar("🏷️ Gerenciar categorias (em desenvolvimento)", self.primary_color)

        def criar_meta(e):
            self.show_snackbar("🎯 Criar meta (em desenvolvimento)", self.primary_color)

        acoes_section = ft.Row([
            ft.FilledButton(
                content=ft.Text("🔍 Verificar Vencimentos", size=14),
                style=ft.ButtonStyle(bgcolor=self.error_color),
                on_click=self.verificar_parcelas_vencidas,
            ),
            ft.FilledButton(
                content=ft.Text("➕ Nova Transação", size=14),
                style=ft.ButtonStyle(bgcolor=self.accent_color),
                on_click=nova_transacao,
            ),
            ft.OutlinedButton(
                content=ft.Text("🏷️ Categorias", size=14),
                on_click=gerenciar_categorias,
            ),
            ft.OutlinedButton(
                content=ft.Text("🎯 Metas", size=14),
                on_click=criar_meta,
            ),
        ], spacing=10)

        # Retornar layout completo
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("💰 Controle Financeiro", size=24, weight=ft.FontWeight.BOLD, color=self.text_primary),
                    ft.Container(expand=True),
                ]),
                ft.Divider(height=10, color="#334155"),

                fluxo_section,

                ft.Row([
                    receber_section,
                    pagar_section,
                ], spacing=15, expand=True),

                dre_section,

                parcelas_section,

                acoes_section,
            ], spacing=15, scroll=ft.ScrollMode.AUTO),
            bgcolor=self.background_color,
            padding=20,
            expand=True,
        )

    def build_corretores_tab(self):
        """Constrói a aba de gestão de corretores"""
        from database import Corretor

        # Buscar todos os corretores
        corretores = self.session.query(Corretor).all()

        # Campos para adicionar novo corretor
        nome_field = ft.TextField(
            label="Nome do Corretor",
            width=300,
            bgcolor=self.surface_color,
            border_color=self.primary_color,
            color=self.text_primary,
        )

        email_field = ft.TextField(
            label="E-mail",
            width=300,
            bgcolor=self.surface_color,
            border_color=self.primary_color,
            color=self.text_primary,
        )

        telefone_field = ft.TextField(
            label="Telefone",
            width=200,
            bgcolor=self.surface_color,
            border_color=self.primary_color,
            color=self.text_primary,
        )

        comissao_field = ft.TextField(
            label="Comissão Padrão (%)",
            width=150,
            value="10.0",
            bgcolor=self.surface_color,
            border_color=self.primary_color,
            color=self.text_primary,
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        def adicionar_corretor(e):
            """Adiciona novo corretor"""
            if not nome_field.value:
                self.show_snackbar("❌ Nome é obrigatório!", self.error_color)
                return

            try:
                comissao = float(comissao_field.value or 10.0)

                novo_corretor = Corretor(
                    nome=nome_field.value,
                    email=email_field.value or "",
                    telefone=telefone_field.value or "",
                    comissao_padrao=comissao,
                )

                self.session.add(novo_corretor)
                self.session.commit()

                self.show_snackbar(f"✅ Corretor {nome_field.value} adicionado!", self.accent_color)

                # Limpar campos
                nome_field.value = ""
                email_field.value = ""
                telefone_field.value = ""
                comissao_field.value = "10.0"

                # Recarregar
                self.page.clean()
                self.build_ui()
                self.page.update()

            except Exception as ex:
                self.show_snackbar(f"❌ Erro: {str(ex)}", self.error_color)

        def editar_corretor(corretor):
            """Edita corretor existente"""
            def salvar_edicao(e):
                try:
                    corretor.nome = nome_edit.value
                    corretor.email = email_edit.value
                    corretor.telefone = telefone_edit.value
                    corretor.comissao_padrao = float(comissao_edit.value)

                    self.session.commit()
                    self.show_snackbar(f"✅ Corretor atualizado!", self.accent_color)

                    dialog.open = False
                    self.page.update()

                    # Recarregar
                    self.page.clean()
                    self.build_ui()
                    self.page.update()

                except Exception as ex:
                    self.show_snackbar(f"❌ Erro: {str(ex)}", self.error_color)

            nome_edit = ft.TextField(label="Nome", value=corretor.nome, width=300)
            email_edit = ft.TextField(label="E-mail", value=corretor.email or "", width=300)
            telefone_edit = ft.TextField(label="Telefone", value=corretor.telefone or "", width=200)
            comissao_edit = ft.TextField(label="Comissão (%)", value=str(corretor.comissao_padrao), width=150)

            dialog = ft.AlertDialog(
                title=ft.Text(f"Editar Corretor"),
                content=ft.Column([
                    nome_edit,
                    email_edit,
                    telefone_edit,
                    comissao_edit,
                ], tight=True, spacing=10),
                actions=[
                    ft.TextButton(content=ft.Text("Cancelar"), on_click=lambda e: setattr(dialog, 'open', False) or self.page.update()),
                    ft.FilledButton(content=ft.Text("Salvar"), on_click=salvar_edicao),
                ],
            )

            self.page.dialog = dialog
            dialog.open = True
            self.page.update()

        def remover_corretor(corretor):
            """Remove corretor"""
            def confirmar_remocao(e):
                try:
                    self.session.delete(corretor)
                    self.session.commit()
                    self.show_snackbar(f"✅ Corretor removido!", self.accent_color)

                    dialog.open = False
                    self.page.update()

                    # Recarregar
                    self.page.clean()
                    self.build_ui()
                    self.page.update()

                except Exception as ex:
                    self.show_snackbar(f"❌ Erro: {str(ex)}", self.error_color)

            dialog = ft.AlertDialog(
                title=ft.Text("Confirmar Remoção"),
                content=ft.Text(f"Deseja realmente remover o corretor {corretor.nome}?"),
                actions=[
                    ft.TextButton(content=ft.Text("Cancelar"), on_click=lambda e: setattr(dialog, 'open', False) or self.page.update()),
                    ft.FilledButton(content=ft.Text("Remover"), on_click=confirmar_remocao, style=ft.ButtonStyle(bgcolor=self.error_color)),
                ],
            )

            self.page.dialog = dialog
            dialog.open = True
            self.page.update()

        # Lista de corretores
        corretores_list = []
        for corretor in corretores:
            corretores_list.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text(corretor.nome, size=18, weight=ft.FontWeight.BOLD, color=self.text_primary),
                                    ft.Text(f"📧 {corretor.email or 'Sem e-mail'}", size=14, color=self.text_secondary),
                                    ft.Text(f"📱 {corretor.telefone or 'Sem telefone'}", size=14, color=self.text_secondary),
                                ],
                                spacing=5,
                            ),
                            ft.Container(expand=True),
                            ft.Container(
                                content=ft.Text(f"{corretor.comissao_padrao}%", size=24, weight=ft.FontWeight.BOLD, color=self.accent_color),
                                padding=10,
                            ),
                            ft.Row(
                                controls=[
                                    ft.OutlinedButton(
                                        content=ft.Text("✏️ Editar", size=12),
                                        style=ft.ButtonStyle(
                                            color=self.primary_color,
                                        ),
                                        tooltip="Editar corretor",
                                        on_click=lambda e, c=corretor: editar_corretor(c),
                                    ),
                                    ft.OutlinedButton(
                                        content=ft.Text("🗑️ Remover", size=12),
                                        style=ft.ButtonStyle(
                                            color=self.error_color,
                                        ),
                                        tooltip="Remover corretor",
                                        on_click=lambda e, c=corretor: remover_corretor(c),
                                    ),
                                ],
                                spacing=5,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    bgcolor=self.surface_color,
                    padding=20,
                    border_radius=10,
                    border=ft.Border.all(1, "#334155"),
                )
            )

        return ft.Container(
            content=ft.Column(
                controls=[
                    # Header
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Text("👥 Gestão de Corretores", size=24, weight=ft.FontWeight.BOLD, color=self.text_primary),
                            ],
                        ),
                        padding=ft.Padding(bottom=20),
                    ),

                    # Formulário de Novo Corretor
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text("➕ Adicionar Novo Corretor", size=18, weight=ft.FontWeight.BOLD, color=self.primary_color),
                                ft.Row(
                                    controls=[
                                        nome_field,
                                        email_field,
                                        telefone_field,
                                        comissao_field,
                                        ft.FilledButton(
                                            content=ft.Text("Adicionar", size=14),
                                            style=ft.ButtonStyle(bgcolor=self.accent_color, color=self.text_primary),
                                            on_click=adicionar_corretor,
                                            height=56,
                                        ),
                                    ],
                                    wrap=True,
                                    spacing=10,
                                ),
                            ],
                            spacing=15,
                        ),
                        bgcolor=self.surface_color,
                        padding=20,
                        border_radius=10,
                        border=ft.Border.all(2, self.accent_color),
                    ),

                    ft.Divider(height=20, color="#334155"),

                    # Lista de Corretores
                    ft.Text(f"📋 Corretores Cadastrados ({len(corretores)})", size=18, weight=ft.FontWeight.BOLD, color=self.text_primary),

                    ft.Column(
                        controls=corretores_list if corretores_list else [
                            ft.Container(
                                content=ft.Text("Nenhum corretor cadastrado", size=16, color=self.text_secondary),
                                padding=20,
                            )
                        ],
                        spacing=10,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                ],
                spacing=20,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=20,
            expand=True,
        )

    def build_config_tab(self):
        """Constrói a aba de configurações"""
        config = ConfigManager(session=self.session)
        impostos = config.listar_impostos()

        impostos_list = ft.Column(
            controls=[
                ft.ListTile(
                    leading=ft.Text("%", size=24, color=self.primary_color),
                    title=ft.Text(f"{nome}", color=self.text_primary),
                    subtitle=ft.Text(f"Alíquota: {valor}%", color=self.text_secondary),
                    trailing=ft.TextButton(
                        content=ft.Text("✏️"),
                        tooltip="Editar",
                    ),
                )
                for nome, valor in impostos.items()
            ],
            spacing=5,
        )

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Configurações de Impostos",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color=self.text_primary,
                    ),
                    ft.Divider(height=20, color="#334155"),
                    impostos_list,
                ],
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=30,
        )

    def importar_pdf(self, e):
        """Abre dialog para importar PDF"""
        caminho_field = ft.TextField(
            label="Caminho do arquivo PDF",
            hint_text="Cole o caminho completo do arquivo aqui",
            width=500,
            multiline=False,
        )

        def processar_arquivo(e):
            """Processa o PDF do caminho informado"""
            caminho = caminho_field.value

            if not caminho:
                self.show_snackbar("❌ Informe o caminho do arquivo!", self.error_color)
                return

            # Fechar dialog
            dialog.open = False
            self.page.update()

            # Mostrar mensagem de processamento
            self.show_snackbar(f"⏳ Processando PDF...", self.primary_color)

            try:
                # Processar PDF com OCR Engine
                from ocr_engine import processar_pdf

                resultado = processar_pdf(caminho)

                if resultado['sucesso']:
                    # Sucesso - mostrar detalhes
                    tipo = resultado['tipo_documento']
                    dados = resultado['dados_extraidos']

                    mensagem = f"✅ {resultado['mensagem']}"

                    self.show_snackbar(mensagem, self.accent_color)

                    # Atualizar dashboard
                    self.atualizar_dashboard(None)
                else:
                    # Erro no processamento
                    self.show_snackbar(
                        f"❌ Erro: {resultado['mensagem']}",
                        self.error_color
                    )

            except Exception as ex:
                # Erro inesperado
                self.show_snackbar(
                    f"❌ Erro ao processar: {str(ex)}",
                    self.error_color
                )

        dialog = ft.AlertDialog(
            title=ft.Text("📄 Importar Proposta PDF"),
            content=ft.Column(
                controls=[
                    ft.Text("Cole o caminho completo do arquivo PDF abaixo:", size=14),
                    caminho_field,
                    ft.Text("Exemplo: C:\\Users\\Documentos\\proposta.pdf", size=12, color=self.text_secondary),
                ],
                tight=True,
                spacing=10,
            ),
            actions=[
                ft.TextButton(
                    content=ft.Text("Cancelar"),
                    on_click=lambda e: (setattr(dialog, 'open', False), self.page.update())
                ),
                ft.FilledButton(
                    content=ft.Text("Processar"),
                    on_click=processar_arquivo,
                    style=ft.ButtonStyle(bgcolor=self.accent_color),
                ),
            ],
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def on_pdf_selected_OLD(self, e):
        """Callback quando um PDF é selecionado - DESABILITADO"""
        if False:
            file_path = e.files[0].path
            file_name = e.files[0].name

            # Mostrar mensagem de processamento
            self.show_snackbar(
                f"⏳ Processando {file_name}...",
                self.primary_color,
            )

            try:
                # Processar PDF com OCR Engine
                from ocr_engine import processar_pdf

                resultado = processar_pdf(file_path)

                if resultado['sucesso']:
                    # Sucesso - mostrar detalhes
                    tipo = resultado['tipo_documento']
                    dados = resultado['dados_extraidos']

                    mensagem = f"✓ {resultado['mensagem']}\n"
                    mensagem += f"Tipo: {tipo}\n"

                    if dados.get('cliente_nome'):
                        mensagem += f"Cliente: {dados['cliente_nome']}\n"
                    if dados.get('valor_bruto', 0) > 0:
                        mensagem += f"Valor: R$ {dados['valor_bruto']:.2f}"

                    self.show_snackbar(mensagem, self.accent_color)

                    # Atualizar dashboard
                    self.atualizar_dashboard(None)
                else:
                    # Erro no processamento
                    self.show_snackbar(
                        f"✗ Erro: {resultado['mensagem']}",
                        self.error_color
                    )

            except Exception as ex:
                # Erro inesperado
                self.show_snackbar(
                    f"✗ Erro ao processar PDF: {str(ex)}",
                    self.error_color
                )
        else:
            self.show_snackbar("Nenhum arquivo selecionado", self.error_color)

    def atualizar_dashboard(self, e):
        """Atualiza os dados do dashboard"""
        self.show_snackbar("Dashboard atualizado!", self.accent_color)
        # Reconstruir dashboard
        self.page.clean()
        self.build_ui()
        self.page.update()

    def show_snackbar(self, message, color):
        """Exibe uma notificação"""
        snackbar = ft.SnackBar(
            content=ft.Text(message, color=self.text_primary),
            bgcolor=color,
            action="OK",
        )
        self.page.snack_bar = snackbar
        snackbar.open = True
        self.page.update()


def main(page: ft.Page):
    """Função principal"""
    page.title = "Sistema Financeiro - Corretora"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0

    # Variável para armazenar usuário logado
    usuario_logado = None

    def on_login_success(usuario):
        """Callback quando login for bem-sucedido"""
        nonlocal usuario_logado
        usuario_logado = usuario

        # Limpar página e mostrar sistema
        page.clean()
        app = CorretoraApp(page, usuario_logado)
        page.update()

    # Mostrar tela de login
    from login_system import mostrar_tela_login
    mostrar_tela_login(page, on_login_success)


if __name__ == "__main__":
    ft.run(main)
