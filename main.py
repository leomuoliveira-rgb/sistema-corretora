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

        # FilePickers — Services no Flet 0.81
        self.file_picker = ft.FilePicker()          # para propostas
        self.file_picker_com = ft.FilePicker()      # para comissões
        self.page.services.append(self.file_picker)
        self.page.services.append(self.file_picker_com)

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

        # Botões de importar PDF
        import_proposta_button = ft.FilledButton(
            content=ft.Row([
                ft.Icon(ft.Icons.UPLOAD_FILE, color="white", size=18),
                ft.Text("  Importar Proposta", size=13, weight=ft.FontWeight.BOLD, color="white"),
            ]),
            style=ft.ButtonStyle(bgcolor=self.primary_color, padding=18),
            on_click=self.importar_pdf,
            height=48,
            tooltip="Importar PDF de proposta de seguro",
        )
        import_comissao_button = ft.FilledButton(
            content=ft.Row([
                ft.Icon(ft.Icons.RECEIPT_LONG, color="white", size=18),
                ft.Text("  Importar Comissões", size=13, weight=ft.FontWeight.BOLD, color="white"),
            ]),
            style=ft.ButtonStyle(bgcolor="#7c3aed", padding=18),
            on_click=self.importar_comissoes,
            height=48,
            tooltip="Importar PDF de extrato/relatório de comissões",
        )

        # Botões de ação
        action_buttons = ft.Row(
            controls=[
                import_proposta_button,
                import_comissao_button,
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
        """Constrói a aba de CRM - Gestão de Leads completa"""
        from database import Lead, Corretor, Interacao
        from datetime import datetime

        corretores = self.session.query(Corretor).all()

        STATUS_COLORS = {
            'NOVO':        '#3b82f6',
            'CONTATO':     '#8b5cf6',
            'QUALIFICADO': '#f59e0b',
            'PROPOSTA':    '#10b981',
            'GANHO':       '#22c55e',
            'PERDIDO':     '#ef4444',
        }
        STATUS_LIST = ['NOVO', 'CONTATO', 'QUALIFICADO', 'PROPOSTA', 'GANHO', 'PERDIDO']

        # ── Estado de filtro (lista mutável para closure) ─────────────────────
        filtro_status = [None]   # None = todos

        # ── Helpers ───────────────────────────────────────────────────────────
        def _cor(status):
            return STATUS_COLORS.get(status, '#6b7280')

        def _reload():
            self.page.clean()
            self.build_ui()
            self.page.update()

        def _fechar(dlg):
            dlg.open = False
            self.page.update()

        # ── Tela cheia de Lead (adicionar / editar) ────────────────────────────
        def _abrir_tela_lead(lead=None):
            """Abre janela de cadastro/edição de lead com validação completa"""
            is_edit = lead is not None
            COR = self.primary_color

            def _voltar_crm():
                self.page.clean(); self.build_ui(); self.page.update()

            # Corretor pré-selecionado (se usuario logado for corretor)
            corretor_pre = None
            if self.usuario_logado and self.usuario_logado.tipo == 'corretor':
                corretor_pre = str(self.usuario_logado.corretor_id) if self.usuario_logado.corretor_id else None

            f_nome   = ft.TextField(label="Nome completo *", width=340,
                                    value=lead.nome if is_edit else "",
                                    bgcolor=self.surface_color)
            f_tel    = ft.TextField(label="Telefone / WhatsApp *", width=210,
                                    value=lead.telefone if is_edit else "",
                                    hint_text="(11) 99999-9999",
                                    bgcolor=self.surface_color)
            f_email  = ft.TextField(label="E-mail", width=280,
                                    value=lead.email or "" if is_edit else "",
                                    bgcolor=self.surface_color)
            f_cpf    = ft.TextField(label="CPF / CNPJ", width=200,
                                    value=lead.cpf_cnpj or "" if is_edit else "",
                                    bgcolor=self.surface_color)
            f_prod   = ft.TextField(label="Produto de Interesse", width=320,
                                    value=lead.produto_interesse or "" if is_edit else "",
                                    bgcolor=self.surface_color)
            f_obs    = ft.TextField(label="Observações", width=560,
                                    value=lead.observacoes or "" if is_edit else "",
                                    multiline=True, min_lines=3, max_lines=5,
                                    bgcolor=self.surface_color)
            f_origem = ft.Dropdown(
                label="Origem", width=210,
                value=lead.origem if is_edit else None,
                options=[ft.dropdown.Option(o) for o in
                         ["Google Ads","Facebook","Instagram","Indicação","Site","Telefone","WhatsApp","Outro"]],
                bgcolor=self.surface_color,
            )
            f_corretor = ft.Dropdown(
                label="Corretor Responsável", width=280,
                value=str(lead.corretor_id) if (is_edit and lead.corretor_id) else corretor_pre,
                options=[ft.dropdown.Option(key=str(c.id), text=c.nome) for c in corretores],
                bgcolor=self.surface_color,
            )
            f_status = ft.Dropdown(
                label="Status", width=200,
                value=lead.status if is_edit else 'NOVO',
                options=[ft.dropdown.Option(s) for s in STATUS_LIST],
                bgcolor=self.surface_color,
            )

            erro_geral = ft.Text("", color=self.error_color, size=12, visible=False)

            def salvar(e):
                # Validação com feedback visual no campo
                valido = self._validar([
                    (f_nome, bool(f_nome.value.strip()), "Nome é obrigatório"),
                    (f_tel,  self._ok_tel(f_tel.value),  "Telefone inválido (mín. 8 dígitos)"),
                    (f_email, not f_email.value.strip() or self._ok_email(f_email.value),
                     "E-mail inválido"),
                    (f_cpf, not f_cpf.value.strip() or self._ok_cpf(f_cpf.value),
                     "CPF/CNPJ inválido"),
                ])
                if not valido:
                    erro_geral.value = "⚠️ Corrija os campos em vermelho antes de salvar."
                    erro_geral.visible = True
                    self.page.update()
                    return
                try:
                    if is_edit:
                        lead.nome             = f_nome.value.strip()
                        lead.telefone         = f_tel.value.strip()
                        lead.email            = f_email.value.strip() or None
                        lead.cpf_cnpj         = f_cpf.value.strip() or None
                        lead.produto_interesse = f_prod.value.strip() or None
                        lead.origem           = f_origem.value or None
                        lead.status           = f_status.value or lead.status
                        lead.corretor_id      = int(f_corretor.value) if f_corretor.value else None
                        lead.observacoes      = f_obs.value.strip() or None
                        lead.data_ultima_interacao = datetime.now()
                        self.session.commit()
                        self.show_snackbar("✅ Lead atualizado!", self.accent_color)
                    else:
                        self.session.add(Lead(
                            nome=f_nome.value.strip(),
                            telefone=f_tel.value.strip(),
                            email=f_email.value.strip() or None,
                            cpf_cnpj=f_cpf.value.strip() or None,
                            produto_interesse=f_prod.value.strip() or None,
                            origem=f_origem.value or None,
                            corretor_id=int(f_corretor.value) if f_corretor.value else None,
                            observacoes=f_obs.value.strip() or None,
                            status='NOVO',
                        ))
                        self.session.commit()
                        self.show_snackbar(f"✅ Lead {f_nome.value.strip()} adicionado!", self.accent_color)
                    _voltar_crm()
                except Exception as ex:
                    self.show_snackbar(f"❌ Erro: {str(ex)}", self.error_color)

            # ── Layout tela ─────────────────────────────────────────────────
            topo = ft.Container(
                content=ft.Row([
                    ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=self.text_primary,
                                  tooltip="Voltar sem salvar", on_click=lambda e: _voltar_crm()),
                    ft.Column([
                        ft.Text("✏️ Editar Lead" if is_edit else "➕ Novo Lead", size=16,
                                weight=ft.FontWeight.BOLD, color=self.text_primary),
                        ft.Text(lead.nome if is_edit else "Preencha os dados do contato",
                                size=11, color=self.text_secondary, italic=True),
                    ], spacing=1),
                    ft.Container(expand=True),
                    ft.OutlinedButton(
                        content=ft.Text("Cancelar", color=self.error_color),
                        style=ft.ButtonStyle(side=ft.BorderSide(1, self.error_color)),
                        on_click=lambda e: _voltar_crm(),
                    ),
                    ft.FilledButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.SAVE_ALT, size=16, color="white"),
                            ft.Text("  Salvar Lead", color="white", weight=ft.FontWeight.BOLD),
                        ]),
                        style=ft.ButtonStyle(bgcolor=COR, padding=18), height=44,
                        on_click=salvar,
                    ),
                ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=self.surface_color,
                padding=ft.Padding.symmetric(horizontal=20, vertical=12),
                border=ft.Border(bottom=ft.BorderSide(1, "#334155")),
            )

            painel = ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.PERSON_ADD_ALT, color=COR, size=20),
                            ft.Text(" Dados do Contato", size=14,
                                    weight=ft.FontWeight.BOLD, color=self.text_primary),
                        ]),
                        bgcolor="#0d1f3c",
                        padding=ft.Padding.symmetric(horizontal=14, vertical=10),
                        border_radius=8, border=ft.Border.all(1, COR + "50"),
                    ),
                    ft.Text("Campos marcados com * são obrigatórios.",
                            size=11, color=self.text_secondary, italic=True),
                    erro_geral,
                    ft.Divider(height=8, color="#334155"),
                    ft.Text("👤 Identificação", size=12, weight=ft.FontWeight.BOLD, color=COR),
                    ft.Row([f_nome, f_tel], spacing=10, wrap=True),
                    ft.Row([f_email, f_cpf, f_origem], spacing=10, wrap=True),
                    ft.Divider(height=8, color="#334155"),
                    ft.Text("🎯 Classificação", size=12, weight=ft.FontWeight.BOLD, color=COR),
                    ft.Row([f_prod, f_status, f_corretor], spacing=10, wrap=True),
                    ft.Divider(height=8, color="#334155"),
                    ft.Text("📝 Observações", size=12, weight=ft.FontWeight.BOLD, color=COR),
                    f_obs,
                ], spacing=10, scroll=ft.ScrollMode.AUTO),
                bgcolor=self.surface_color,
                padding=24, border_radius=12,
                border=ft.Border.all(1, "#334155"),
                expand=True,
            )

            tela = ft.Container(
                content=ft.Column([
                    topo,
                    ft.Container(content=painel,
                                 expand=True,
                                 padding=ft.Padding.symmetric(horizontal=40, vertical=20)),
                ], spacing=0, expand=True),
                bgcolor=self.background_color, expand=True,
            )
            self.page.clean()
            self.page.add(tela)
            self.page.update()

        def adicionar_lead(e):
            _abrir_tela_lead()

        def editar_lead(lead):
            _abrir_tela_lead(lead)

        # ── Excluir Lead ───────────────────────────────────────────────────────
        def excluir_lead(lead):
            def confirmar(e):
                try:
                    self.session.delete(lead)
                    self.session.commit()
                    self.show_snackbar(f"✅ Lead {lead.nome} excluído!", self.accent_color)
                    _fechar(dlg)
                    _reload()
                except Exception as ex:
                    self.show_snackbar(f"❌ Erro: {str(ex)}", self.error_color)

            dlg = ft.AlertDialog(
                title=ft.Text("Confirmar Exclusão"),
                content=ft.Text(f"Excluir o lead '{lead.nome}'?\nTodo o histórico de interações será removido."),
                actions=[
                    ft.TextButton(content=ft.Text("Cancelar"), on_click=lambda e: _fechar(dlg)),
                    ft.FilledButton(
                        content=ft.Text("Excluir"),
                        on_click=confirmar,
                        style=ft.ButtonStyle(bgcolor=self.error_color),
                    ),
                ],
            )
            self.page.dialog = dlg
            dlg.open = True
            self.page.update()

        # ── Adicionar Interação ────────────────────────────────────────────────
        def adicionar_interacao(lead, on_saved=None):
            f_tipo = ft.Dropdown(
                label="Tipo de Contato *", width=220,
                options=[ft.dropdown.Option(t) for t in
                         ["LIGAÇÃO","WHATSAPP","EMAIL","REUNIÃO","PROPOSTA","OUTRO"]],
                value="LIGAÇÃO",
                bgcolor=self.surface_color,
            )
            f_desc     = ft.TextField(label="Descrição *", width=500,
                                      multiline=True, min_lines=4, max_lines=6,
                                      hint_text="Descreva o contato realizado...",
                                      bgcolor=self.surface_color)
            f_followup = ft.TextField(
                label="Próximo Follow-up", hint_text="dd/mm/aaaa",
                width=200, bgcolor=self.surface_color,
            )
            f_status_novo = ft.Dropdown(
                label="Atualizar Status do Lead", width=220,
                value=lead.status,
                options=[ft.dropdown.Option(s) for s in STATUS_LIST],
                bgcolor=self.surface_color,
            )

            def salvar(e):
                valido = self._validar([
                    (f_tipo, bool(f_tipo.value), "Selecione o tipo"),
                    (f_desc, bool(f_desc.value.strip()), "Descreva o contato realizado"),
                    (f_followup,
                     not f_followup.value.strip() or
                     bool(__import__('re').match(r'\d{2}/\d{2}/\d{4}', f_followup.value.strip())),
                     "Formato dd/mm/aaaa"),
                ])
                if not valido:
                    return
                try:
                    followup = None
                    if f_followup.value.strip():
                        from datetime import datetime as _dt
                        followup = _dt.strptime(f_followup.value.strip(), '%d/%m/%Y')

                    uid = self.usuario_logado.id if self.usuario_logado else 1
                    self.session.add(Interacao(
                        lead_id=lead.id,
                        usuario_id=uid,
                        tipo=f_tipo.value,
                        descricao=f_desc.value.strip(),
                        proximo_followup=followup,
                    ))
                    lead.data_ultima_interacao = datetime.now()
                    if f_status_novo.value and f_status_novo.value != lead.status:
                        lead.status = f_status_novo.value
                    self.session.commit()
                    self.show_snackbar("✅ Interação registrada!", self.accent_color)
                    _fechar(dlg)
                    if on_saved:
                        on_saved()
                    else:
                        _reload()
                except Exception as ex:
                    self.show_snackbar(f"❌ Erro: {str(ex)}", self.error_color)

            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Row([
                    ft.Icon(ft.Icons.CHAT, color=self.primary_color, size=20),
                    ft.Text(f"  Registrar Contato — {lead.nome}", size=14,
                            weight=ft.FontWeight.BOLD),
                ]),
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([f_tipo, f_followup, f_status_novo], spacing=10, wrap=True),
                        f_desc,
                    ], spacing=10),
                    width=560, height=280, padding=4,
                ),
                actions=[
                    ft.TextButton(content=ft.Text("Cancelar", color=self.error_color),
                                  on_click=lambda e: _fechar(dlg)),
                    ft.FilledButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.SAVE, size=15, color="white"),
                            ft.Text("  Salvar Interação", color="white"),
                        ]),
                        style=ft.ButtonStyle(bgcolor=self.primary_color),
                        on_click=salvar,
                    ),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            self.page.dialog = dlg
            dlg.open = True
            self.page.update()

        # ── Ver Detalhes / Histórico ───────────────────────────────────────────
        def ver_detalhes_lead(lead):
            from database import Seguradora
            TIPO_ICONS = {
                'LIGAÇÃO': '📞', 'WHATSAPP': '💬', 'EMAIL': '✉️',
                'REUNIÃO': '🤝', 'PROPOSTA': '📄', 'OUTRO': '📌',
            }

            def _build_historico():
                interacoes = (
                    self.session.query(Interacao)
                    .filter(Interacao.lead_id == lead.id)
                    .order_by(Interacao.data_hora.desc())
                    .all()
                )
                if not interacoes:
                    return [ft.Text("Nenhuma interação registrada.", size=12, color=self.text_secondary)]
                rows = []
                for inter in interacoes:
                    icone = TIPO_ICONS.get(inter.tipo, '📌')
                    followup_txt = ""
                    if inter.proximo_followup:
                        followup_txt = f"  •  Follow-up: {inter.proximo_followup.strftime('%d/%m/%Y')}"
                    rows.append(
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Text(f"{icone} {inter.tipo}", size=12, weight=ft.FontWeight.BOLD,
                                           color=self.primary_color),
                                    ft.Text(inter.data_hora.strftime('%d/%m/%Y %H:%M'), size=11,
                                           color=self.text_secondary),
                                    ft.Text(followup_txt, size=11, color="#f59e0b") if followup_txt else ft.Text(""),
                                ], spacing=10),
                                ft.Text(inter.descricao, size=12, color=self.text_primary),
                            ], spacing=3),
                            bgcolor="#1a2744",
                            padding=ft.Padding.symmetric(horizontal=10, vertical=6),
                            border_radius=6,
                        )
                    )
                return rows

            hist_column = ft.Column(controls=_build_historico(), spacing=6,
                                    scroll=ft.ScrollMode.AUTO, height=220)

            def nova_interacao_e_atualiza(e):
                def on_saved():
                    hist_column.controls = _build_historico()
                    self.page.update()
                adicionar_interacao(lead, on_saved=on_saved)

            # ── Converter em Proposta ──────────────────────────────────────
            def converter_em_proposta(e):
                if lead.status != 'GANHO':
                    self.show_snackbar("⚠️ Altere o status para GANHO antes de converter!", "#f59e0b")
                    return
                seguradoras = self.session.query(Seguradora).all()
                f_valor = ft.TextField(label="Valor do Contrato (R$)", width=180,
                                       keyboard_type=ft.KeyboardType.NUMBER)
                f_plano = ft.TextField(label="Tipo de Plano", width=280)
                f_seg   = ft.Dropdown(
                    label="Seguradora", width=260,
                    options=[ft.dropdown.Option(key=str(s.id), text=s.nome) for s in seguradoras],
                )
                f_cor   = ft.Dropdown(
                    label="Corretor", width=260,
                    value=str(lead.corretor_id) if lead.corretor_id else None,
                    options=[ft.dropdown.Option(key=str(c.id), text=c.nome) for c in corretores],
                )

                def salvar_proposta(e):
                    if not f_seg.value or not f_cor.value or not f_valor.value:
                        self.show_snackbar("❌ Seguradora, corretor e valor são obrigatórios!", self.error_color)
                        return
                    try:
                        from database import Proposta
                        from finance_engine import FinanceEngine
                        nova = Proposta(
                            cliente_nome=lead.nome,
                            cliente_cpf=lead.cpf_cnpj,
                            cliente_telefone=lead.telefone,
                            cliente_email=lead.email,
                            tipo_plano=f_plano.value.strip() or None,
                            valor_bruto=float(f_valor.value),
                            seguradora_id=int(f_seg.value),
                            corretor_id=int(f_cor.value),
                        )
                        self.session.add(nova)
                        self.session.commit()
                        FinanceEngine(session=self.session).gerar_lancamentos(nova)
                        lead.status = 'GANHO'
                        self.session.commit()
                        _fechar(dlg_conv)
                        _fechar(dlg)
                        self.show_snackbar(f"✅ Proposta #{nova.id} criada para {lead.nome}!", self.accent_color)
                        _reload()
                    except Exception as ex:
                        self.show_snackbar(f"❌ Erro: {str(ex)}", self.error_color)

                dlg_conv = ft.AlertDialog(
                    title=ft.Text(f"🔀 Converter em Proposta — {lead.nome}"),
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([f_valor, f_plano], spacing=8, wrap=True),
                            ft.Row([f_seg, f_cor], spacing=8, wrap=True),
                        ], spacing=10),
                        width=560, height=160,
                    ),
                    actions=[
                        ft.TextButton(content=ft.Text("Cancelar"), on_click=lambda e: _fechar(dlg_conv)),
                        ft.FilledButton(content=ft.Text("Criar Proposta"), on_click=salvar_proposta,
                                        style=ft.ButtonStyle(bgcolor=self.accent_color)),
                    ],
                )
                self.page.dialog = dlg_conv
                dlg_conv.open = True
                self.page.update()

            # ── Info do lead ───────────────────────────────────────────────
            cor_nome = lead.corretor.nome if lead.corretor else "—"
            ult = lead.data_ultima_interacao.strftime('%d/%m/%Y %H:%M') if lead.data_ultima_interacao else "—"
            status_color = _cor(lead.status)

            info_col = ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Text(lead.status, size=12, weight=ft.FontWeight.BOLD),
                        bgcolor=status_color + "40",
                        padding=ft.Padding(left=10, right=10, top=4, bottom=4),
                        border_radius=12,
                    ),
                    ft.Text(f"Origem: {lead.origem or '—'}", size=12, color=self.text_secondary),
                ], spacing=10),
                ft.Text(f"📞 {lead.telefone}  |  ✉️ {lead.email or '—'}", size=12, color=self.text_secondary),
                ft.Text(f"CPF/CNPJ: {lead.cpf_cnpj or '—'}  |  Corretor: {cor_nome}", size=12, color=self.text_secondary),
                ft.Text(f"Produto: {lead.produto_interesse or '—'}", size=12, color=self.text_secondary),
                ft.Text(f"Última interação: {ult}", size=12, color=self.text_secondary),
                ft.Text(f"Obs: {lead.observacoes or '—'}", size=12, color=self.text_secondary) if lead.observacoes else ft.Text(""),
            ], spacing=4)

            dlg = ft.AlertDialog(
                title=ft.Text(f"👤 {lead.nome}", size=15, weight=ft.FontWeight.BOLD),
                content=ft.Container(
                    content=ft.Column([
                        info_col,
                        ft.Divider(height=10, color="#334155"),
                        ft.Row([
                            ft.Text("📋 Histórico de Interações", size=13,
                                    weight=ft.FontWeight.BOLD, color=self.primary_color),
                            ft.TextButton(
                                content=ft.Text("+ Nova Interação", size=12, color=self.accent_color),
                                on_click=nova_interacao_e_atualiza,
                            ),
                        ]),
                        hist_column,
                    ], spacing=8, scroll=ft.ScrollMode.AUTO),
                    width=560, height=460,
                ),
                actions=[
                    ft.TextButton(content=ft.Text("Fechar"), on_click=lambda e: _fechar(dlg)),
                    ft.OutlinedButton(
                        content=ft.Text("✏️ Editar Lead"),
                        on_click=lambda e: (_fechar(dlg), editar_lead(lead)),
                    ),
                    ft.FilledButton(
                        content=ft.Text("🔀 Converter em Proposta"),
                        on_click=converter_em_proposta,
                        style=ft.ButtonStyle(bgcolor="#22c55e"),
                    ),
                ],
                actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            )
            self.page.dialog = dlg
            dlg.open = True
            self.page.update()

        # ── Montar lista de leads ──────────────────────────────────────────────
        todos_leads = self.session.query(Lead).order_by(Lead.data_criacao.desc()).all()

        total_leads  = len(todos_leads)
        cnt = {s: len([l for l in todos_leads if l.status == s]) for s in STATUS_LIST}

        filtrado = (
            [l for l in todos_leads if l.status == filtro_status[0]]
            if filtro_status[0]
            else todos_leads
        )

        leads_list = []
        for lead in filtrado[:60]:
            status_color = _cor(lead.status)

            # Follow-up vencido?
            followup_alert = ""
            ult_inter = (
                self.session.query(Interacao)
                .filter(Interacao.lead_id == lead.id)
                .order_by(Interacao.data_hora.desc())
                .first()
            )
            if ult_inter and ult_inter.proximo_followup:
                from datetime import date
                if ult_inter.proximo_followup.date() <= date.today():
                    followup_alert = f"⚠️ Follow-up: {ult_inter.proximo_followup.strftime('%d/%m/%Y')}"

            leads_list.append(
                ft.Container(
                    content=ft.Row([
                        ft.Container(width=4, bgcolor=status_color, border_radius=2),
                        ft.Column([
                            ft.Text(lead.nome, size=14, weight=ft.FontWeight.BOLD, color=self.text_primary),
                            ft.Text(
                                f"📞 {lead.telefone}  •  {lead.produto_interesse or '—'}  •  {lead.origem or '—'}",
                                size=11, color=self.text_secondary,
                            ),
                            ft.Text(followup_alert, size=11, color="#f59e0b") if followup_alert else ft.Text(""),
                        ], spacing=2, expand=True),
                        ft.Container(
                            content=ft.Text(lead.status, size=11, weight=ft.FontWeight.BOLD),
                            bgcolor=status_color + "30",
                            padding=ft.Padding(left=8, right=8, top=3, bottom=3),
                            border_radius=10,
                        ),
                        ft.Row([
                            ft.OutlinedButton(
                                content=ft.Text("👁️ Detalhes", size=11),
                                style=ft.ButtonStyle(color=self.accent_color),
                                on_click=lambda e, l=lead: ver_detalhes_lead(l),
                            ),
                            ft.OutlinedButton(
                                content=ft.Text("📝", size=13),
                                width=42,
                                style=ft.ButtonStyle(color=self.primary_color),
                                on_click=lambda e, l=lead: adicionar_interacao(l),
                            ),
                            ft.OutlinedButton(
                                content=ft.Text("🗑️", size=13),
                                width=42,
                                style=ft.ButtonStyle(color=self.error_color),
                                on_click=lambda e, l=lead: excluir_lead(l),
                            ),
                        ], spacing=4),
                    ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=self.surface_color,
                    padding=ft.Padding.symmetric(horizontal=14, vertical=10),
                    border_radius=10,
                    border=ft.Border.all(1, "#334155"),
                )
            )

        # ── Botões de filtro por status ────────────────────────────────────────
        def _filtro_btn(label, status_val, count, color):
            selecionado = filtro_status[0] == status_val
            return ft.OutlinedButton(
                content=ft.Text(f"{label}  {count}", size=12,
                                color="white" if selecionado else color,
                                weight=ft.FontWeight.BOLD if selecionado else ft.FontWeight.NORMAL),
                style=ft.ButtonStyle(
                    bgcolor=color if selecionado else "transparent",
                    side=ft.BorderSide(width=1, color=color),
                ),
                on_click=lambda e, sv=status_val: _aplicar_filtro(sv),
            )

        def _aplicar_filtro(status_val):
            filtro_status[0] = None if filtro_status[0] == status_val else status_val
            _reload()

        filtros_row = ft.Row([
            _filtro_btn("Todos", None, total_leads, "#6b7280"),
            _filtro_btn("Novo", "NOVO", cnt['NOVO'], '#3b82f6'),
            _filtro_btn("Contato", "CONTATO", cnt['CONTATO'], '#8b5cf6'),
            _filtro_btn("Qualificado", "QUALIFICADO", cnt['QUALIFICADO'], '#f59e0b'),
            _filtro_btn("Proposta", "PROPOSTA", cnt['PROPOSTA'], '#10b981'),
            _filtro_btn("Ganho", "GANHO", cnt['GANHO'], '#22c55e'),
            _filtro_btn("Perdido", "PERDIDO", cnt['PERDIDO'], '#ef4444'),
        ], spacing=6, wrap=True)

        return ft.Container(
            content=ft.Column([
                # Header
                ft.Row([
                    ft.Text("🎯 CRM — Gestão de Leads", size=22, weight=ft.FontWeight.BOLD, color=self.text_primary),
                    ft.Container(expand=True),
                    ft.FilledButton(
                        content=ft.Text("➕ Novo Lead", size=13),
                        style=ft.ButtonStyle(bgcolor=self.accent_color),
                        on_click=adicionar_lead,
                    ),
                ]),
                ft.Divider(height=8, color="#334155"),
                # KPIs rápidos
                ft.Row([
                    ft.Container(
                        content=ft.Column([
                            ft.Text(str(total_leads), size=28, weight=ft.FontWeight.BOLD, color=self.primary_color),
                            ft.Text("Total", size=12, color=self.text_secondary),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        bgcolor=self.surface_color, padding=16, border_radius=10, expand=True,
                    ),
                    *[
                        ft.Container(
                            content=ft.Column([
                                ft.Text(str(cnt[s]), size=28, weight=ft.FontWeight.BOLD, color=_cor(s)),
                                ft.Text(s.capitalize(), size=12, color=self.text_secondary),
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            bgcolor=self.surface_color, padding=16, border_radius=10, expand=True,
                        )
                        for s in STATUS_LIST
                    ],
                ], spacing=8),
                ft.Divider(height=8, color="#334155"),
                # Filtros
                filtros_row,
                ft.Divider(height=6, color="#334155"),
                # Lista
                ft.Column(
                    controls=leads_list if leads_list else [
                        ft.Container(
                            content=ft.Text(
                                "Nenhum lead encontrado." if filtro_status[0] else "Nenhum lead cadastrado.",
                                size=15, color=self.text_secondary,
                            ),
                            padding=30,
                        )
                    ],
                    spacing=6,
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                ),
            ], spacing=12, expand=True),
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

            from datetime import datetime as _dt
            cliente_field = ft.TextField(label="Nome do Cliente", value=proposta.cliente_nome, width=300)
            cpf_field = ft.TextField(label="CPF/CNPJ", value=proposta.cliente_cpf or "", width=190)
            rg_field = ft.TextField(label="RG", value=proposta.cliente_rg or "", width=160)
            nasc_field = ft.TextField(
                label="Data de Nascimento",
                value=proposta.cliente_data_nascimento.strftime('%d/%m/%Y') if proposta.cliente_data_nascimento else "",
                hint_text="dd/mm/aaaa",
                width=155,
            )
            tel_field = ft.TextField(label="Telefone", value=proposta.cliente_telefone or "", width=175)
            email_field = ft.TextField(label="E-mail", value=proposta.cliente_email or "", width=270)
            plano_field = ft.TextField(label="Tipo de Plano", value=proposta.tipo_plano or "", width=300)
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
                    proposta.cliente_nome = cliente_field.value.strip()
                    proposta.cliente_cpf = cpf_field.value.strip() or None
                    proposta.cliente_rg = rg_field.value.strip() or None
                    proposta.cliente_telefone = tel_field.value.strip() or None
                    proposta.cliente_email = email_field.value.strip() or None
                    proposta.tipo_plano = plano_field.value.strip() or None
                    proposta.valor_bruto = float(valor_field.value)
                    proposta.corretor_id = int(corretor_dropdown.value)
                    proposta.seguradora_id = int(seguradora_dropdown.value)
                    if nasc_field.value.strip():
                        try:
                            proposta.cliente_data_nascimento = _dt.strptime(nasc_field.value.strip(), '%d/%m/%Y').date()
                        except Exception:
                            pass

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
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Dados do Titular", size=13, weight=ft.FontWeight.BOLD, color=self.primary_color),
                        ft.Row([cliente_field, cpf_field, rg_field], spacing=8, wrap=True),
                        ft.Row([nasc_field, tel_field, email_field], spacing=8, wrap=True),
                        ft.Divider(height=10, color="#334155"),
                        ft.Text("Contrato", size=13, weight=ft.FontWeight.BOLD, color=self.primary_color),
                        ft.Row([plano_field, valor_field], spacing=8, wrap=True),
                        ft.Row([corretor_dropdown, seguradora_dropdown], spacing=8, wrap=True),
                    ], tight=True, spacing=10, scroll=ft.ScrollMode.AUTO),
                    width=640, height=360,
                ),
                actions=[
                    ft.TextButton(content=ft.Text("Cancelar"), on_click=lambda e: (setattr(dialog, 'open', False), self.page.update())),
                    ft.FilledButton(content=ft.Text("Salvar"), on_click=salvar_edicao),
                ],
            )

            self.page.dialog = dialog
            dialog.open = True
            self.page.update()

        def ver_detalhes_proposta(proposta):
            """Exibe todos os dados cadastrais do cliente, plano e dependentes"""
            from database import Dependente

            def _linha(label, valor, cor=None):
                return ft.Row([
                    ft.Text(label, size=12, color=self.text_secondary, width=160),
                    ft.Text(str(valor) if valor else "—", size=12,
                            color=cor or self.text_primary, weight=ft.FontWeight.W_500),
                ], spacing=4)

            # ── Titular ──────────────────────────────────────────────
            nascimento = (
                proposta.cliente_data_nascimento.strftime('%d/%m/%Y')
                if proposta.cliente_data_nascimento else None
            )
            titular_col = ft.Column([
                ft.Text("👤 Dados do Titular", size=13, weight=ft.FontWeight.BOLD, color=self.primary_color),
                _linha("Nome:", proposta.cliente_nome),
                _linha("CPF/CNPJ:", proposta.cliente_cpf),
                _linha("RG:", proposta.cliente_rg),
                _linha("Nascimento:", nascimento),
                _linha("Telefone:", proposta.cliente_telefone),
                _linha("E-mail:", proposta.cliente_email),
            ], spacing=6)

            # ── Contrato ──────────────────────────────────────────────
            contrato_col = ft.Column([
                ft.Text("📋 Dados do Contrato", size=13, weight=ft.FontWeight.BOLD, color=self.primary_color),
                _linha("Tipo de Plano:", proposta.tipo_plano),
                _linha("Seguradora:", proposta.seguradora.nome),
                _linha("Corretor:", proposta.corretor.nome),
                _linha("Data de Venda:", proposta.data_venda.strftime('%d/%m/%Y')),
                _linha("Valor do Contrato:", f"R$ {proposta.valor_bruto:,.2f}", self.accent_color),
            ], spacing=6)

            # ── Dependentes ───────────────────────────────────────────
            dependentes_db = self.session.query(Dependente).filter(
                Dependente.proposta_id == proposta.id
            ).all()

            dep_rows = []
            for dep in dependentes_db:
                dep_nasc = dep.data_nascimento.strftime('%d/%m/%Y') if dep.data_nascimento else "—"
                dep_rows.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(dep.nome, size=12, weight=ft.FontWeight.BOLD, color=self.text_primary),
                            ft.Row([
                                ft.Text(f"Parentesco: {dep.parentesco or '—'}", size=11, color=self.text_secondary),
                                ft.Text(f"CPF: {dep.cpf or '—'}", size=11, color=self.text_secondary),
                                ft.Text(f"RG: {dep.rg or '—'}", size=11, color=self.text_secondary),
                                ft.Text(f"Nasc.: {dep_nasc}", size=11, color=self.text_secondary),
                            ], spacing=12, wrap=True),
                        ], spacing=4),
                        bgcolor="#1a2744",
                        padding=ft.Padding.symmetric(horizontal=10, vertical=6),
                        border_radius=6,
                    )
                )

            dependentes_col = ft.Column([
                ft.Text(
                    f"👥 Dependentes ({len(dependentes_db)})",
                    size=13, weight=ft.FontWeight.BOLD, color=self.primary_color,
                ),
                *(dep_rows if dep_rows else [ft.Text("Nenhum dependente cadastrado.", size=12, color=self.text_secondary)]),
            ], spacing=6)

            conteudo = ft.Column([
                titular_col,
                ft.Divider(height=14, color="#334155"),
                contrato_col,
                ft.Divider(height=14, color="#334155"),
                dependentes_col,
            ], spacing=12, scroll=ft.ScrollMode.AUTO, width=520)

            dialog = ft.AlertDialog(
                title=ft.Text(f"Detalhes — #{proposta.id} {proposta.cliente_nome}", size=15, weight=ft.FontWeight.BOLD),
                content=ft.Container(content=conteudo, width=540, height=440),
                actions=[
                    ft.TextButton(
                        content=ft.Text("Fechar"),
                        on_click=lambda e: (setattr(dialog, 'open', False), self.page.update()),
                    ),
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
            # Linha de informações secundárias (campos novos se preenchidos)
            infos_extras = []
            if proposta.cliente_telefone:
                infos_extras.append(f"📞 {proposta.cliente_telefone}")
            if proposta.cliente_email:
                infos_extras.append(f"✉️ {proposta.cliente_email}")
            if proposta.tipo_plano:
                infos_extras.append(f"🏷️ {proposta.tipo_plano}")

            # Contar dependentes
            from database import Dependente
            ndeps = self.session.query(Dependente).filter(Dependente.proposta_id == proposta.id).count()

            propostas_list.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Column([
                                ft.Text(f"#{proposta.id} — {proposta.cliente_nome}", size=16, weight=ft.FontWeight.BOLD, color=self.text_primary),
                                ft.Text(
                                    f"📋 CPF: {proposta.cliente_cpf or '—'}  |  RG: {proposta.cliente_rg or '—'}",
                                    size=12, color=self.text_secondary,
                                ),
                                ft.Text(f"💼 {proposta.corretor.nome}  •  🏢 {proposta.seguradora.nome}", size=12, color=self.text_secondary),
                                ft.Text("  |  ".join(infos_extras) if infos_extras else "", size=12, color=self.text_secondary),
                                ft.Text(
                                    f"👥 {ndeps} dependente(s)" if ndeps else "",
                                    size=12, color=self.accent_color,
                                ),
                            ], spacing=3, expand=True),
                            ft.Column([
                                ft.Text(f"R$ {proposta.valor_bruto:,.2f}", size=20, weight=ft.FontWeight.BOLD, color=self.accent_color),
                                ft.Text(f"📅 {proposta.data_venda.strftime('%d/%m/%Y')}", size=12, color=self.text_secondary),
                                ft.Row([
                                    ft.OutlinedButton(
                                        content=ft.Text("👁️ Detalhes", size=11),
                                        style=ft.ButtonStyle(color=self.accent_color),
                                        on_click=lambda e, p=proposta: ver_detalhes_proposta(p),
                                    ),
                                    ft.OutlinedButton(
                                        content=ft.Text("✏️ Editar", size=11),
                                        style=ft.ButtonStyle(color=self.primary_color),
                                        on_click=lambda e, p=proposta: editar_proposta(p),
                                    ),
                                    ft.OutlinedButton(
                                        content=ft.Text("🗑️", size=11),
                                        style=ft.ButtonStyle(color=self.error_color),
                                        on_click=lambda e, p=proposta: excluir_proposta(p),
                                    ),
                                ], spacing=4),
                            ], horizontal_alignment=ft.CrossAxisAlignment.END, spacing=6),
                        ], vertical_alignment=ft.CrossAxisAlignment.START),
                    ]),
                    bgcolor=self.surface_color,
                    padding=16,
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
        from database import Lancamento, Proposta
        from datetime import date

        hoje = date.today()

        # Buscar todos os lançamentos com proposta
        lancamentos = (
            self.session.query(Lancamento)
            .join(Proposta)
            .order_by(Lancamento.data_vencimento.asc())
            .all()
        )

        total_lancamentos = len(lancamentos)
        total_pendente = sum(l.valor_esperado for l in lancamentos if not l.status_pago)
        total_pago = sum(l.valor_esperado for l in lancamentos if l.status_pago)
        vencidos = sum(1 for l in lancamentos if not l.status_pago and l.data_vencimento < hoje)

        # ---- Funções de ação ----
        def marcar_pago(lancamento):
            """Marca um lançamento como pago"""
            def confirmar(e):
                try:
                    lancamento.status_pago = True
                    self.session.commit()
                    self.show_snackbar("✅ Lançamento quitado!", self.accent_color)
                    dialog.open = False
                    self.page.update()
                    self.page.clean()
                    self.build_ui()
                    self.page.update()
                except Exception as ex:
                    self.show_snackbar(f"❌ Erro: {str(ex)}", self.error_color)

            dialog = ft.AlertDialog(
                title=ft.Text("Confirmar Quitação"),
                content=ft.Text(
                    f"Marcar lançamento de R$ {lancamento.valor_esperado:,.2f} "
                    f"({lancamento.proposta.cliente_nome}) como PAGO?"
                ),
                actions=[
                    ft.TextButton(
                        content=ft.Text("Cancelar"),
                        on_click=lambda e: (setattr(dialog, 'open', False), self.page.update()),
                    ),
                    ft.FilledButton(
                        content=ft.Text("✅ Confirmar"),
                        on_click=confirmar,
                        style=ft.ButtonStyle(bgcolor=self.accent_color),
                    ),
                ],
            )
            self.page.dialog = dialog
            dialog.open = True
            self.page.update()

        def desfazer_pagamento(lancamento):
            """Desfaz marcação de pago"""
            try:
                lancamento.status_pago = False
                self.session.commit()
                self.show_snackbar("↩️ Pagamento revertido.", self.primary_color)
                self.page.clean()
                self.build_ui()
                self.page.update()
            except Exception as ex:
                self.show_snackbar(f"❌ Erro: {str(ex)}", self.error_color)

        # ---- Cards de estatísticas ----
        stats_row = ft.Row(
            controls=[
                self.create_stat_card("Total", str(total_lancamentos), "📋", self.primary_color),
                self.create_stat_card("Pendente", f"R$ {total_pendente:,.2f}", "⏳", self.error_color),
                self.create_stat_card("Pago", f"R$ {total_pago:,.2f}", "✅", self.accent_color),
                self.create_stat_card("Vencidos", str(vencidos), "⚠️", "#f59e0b"),
            ],
            spacing=15,
            wrap=True,
        )

        # ---- Lista de lançamentos ----
        items = []
        for lanc in lancamentos:
            is_pago = lanc.status_pago
            is_vencido = not is_pago and lanc.data_vencimento < hoje

            # Cor da barra lateral
            bar_color = self.accent_color if is_pago else (self.error_color if is_vencido else self.primary_color)

            # Badge de status
            if is_pago:
                badge_text = "PAGO"
                badge_bgcolor = "#14532d"
                badge_color = "#86efac"
            elif is_vencido:
                badge_text = f"VENCIDO ({(hoje - lanc.data_vencimento).days}d)"
                badge_bgcolor = "#450a0a"
                badge_color = "#fca5a5"
            else:
                badge_text = "PENDENTE"
                badge_bgcolor = "#1e1b4b"
                badge_color = "#a5b4fc"

            # Botão de ação
            if is_pago:
                action_btn = ft.OutlinedButton(
                    content=ft.Text("↩️ Reverter", size=12),
                    style=ft.ButtonStyle(color=self.text_secondary),
                    on_click=lambda e, l=lanc: desfazer_pagamento(l),
                    height=36,
                )
            else:
                action_btn = ft.FilledButton(
                    content=ft.Text("✅ Quitar", size=12),
                    style=ft.ButtonStyle(bgcolor=self.accent_color, color="#fff"),
                    on_click=lambda e, l=lanc: marcar_pago(l),
                    height=36,
                )

            items.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Container(width=4, height=60, bgcolor=bar_color, border_radius=2),
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        lanc.proposta.cliente_nome,
                                        size=14,
                                        weight=ft.FontWeight.BOLD,
                                        color=self.text_primary,
                                    ),
                                    ft.Text(
                                        f"📅 Venc: {lanc.data_vencimento.strftime('%d/%m/%Y')}  "
                                        f"| Seguradora: {lanc.proposta.seguradora.nome}  "
                                        f"| Corretor: {lanc.proposta.corretor.nome}",
                                        size=12,
                                        color=self.text_secondary,
                                    ),
                                ],
                                spacing=3,
                                expand=True,
                            ),
                            ft.Container(
                                content=ft.Text(
                                    badge_text,
                                    size=11,
                                    weight=ft.FontWeight.BOLD,
                                    color=badge_color,
                                ),
                                bgcolor=badge_bgcolor,
                                padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                                border_radius=20,
                            ),
                            ft.Text(
                                f"R$ {lanc.valor_esperado:,.2f}",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=self.accent_color if is_pago else self.text_primary,
                                width=130,
                                text_align=ft.TextAlign.RIGHT,
                            ),
                            action_btn,
                        ],
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    bgcolor=self.surface_color,
                    padding=ft.Padding.symmetric(horizontal=16, vertical=12),
                    border_radius=10,
                    border=ft.Border.all(1, "#334155"),
                )
            )

        empty_state = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("📋", size=48),
                    ft.Text("Nenhum lançamento encontrado", size=16, color=self.text_secondary),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=40,
            alignment=ft.Alignment(0, 0),
        )

        return ft.Container(
            content=ft.Column(
                controls=[
                    # Header
                    ft.Row(
                        controls=[
                            ft.Text(
                                "💳 Lançamentos Financeiros",
                                size=26,
                                weight=ft.FontWeight.BOLD,
                                color=self.text_primary,
                            ),
                            ft.Container(expand=True),
                            ft.FilledButton(
                                content=ft.Text("🔄 Atualizar", size=13),
                                style=ft.ButtonStyle(bgcolor=self.primary_color),
                                on_click=lambda e: (
                                    self.page.clean(),
                                    self.build_ui(),
                                    self.page.update(),
                                ),
                                height=40,
                            ),
                        ],
                    ),
                    ft.Divider(height=10, color="#334155"),
                    # Estatísticas
                    stats_row,
                    ft.Divider(height=10, color="#334155"),
                    # Lista
                    ft.Column(
                        controls=items if items else [empty_state],
                        spacing=8,
                        scroll=ft.ScrollMode.AUTO,
                        expand=True,
                    ),
                ],
                spacing=15,
                expand=True,
            ),
            padding=20,
            expand=True,
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
        """Mostra detalhes completos do corretor em um dialog"""
        from datetime import date

        propostas = corretor.propostas
        total_bruto = sum(p.valor_bruto for p in propostas)
        comissao_perc = corretor.comissao_padrao
        total_comissao = total_bruto * (comissao_perc / 100)

        # Calcular lançamentos
        total_pago = 0.0
        total_pendente = 0.0
        hoje = date.today()

        for p in propostas:
            for l in p.lancamentos:
                if l.status_pago:
                    total_pago += l.valor_esperado
                else:
                    total_pendente += l.valor_esperado

        # Linhas de propostas
        proposta_rows = []
        for p in propostas:
            lancamentos_pendentes = sum(1 for l in p.lancamentos if not l.status_pago)
            proposta_rows.append(
                ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text(p.cliente_nome, size=13, weight=ft.FontWeight.BOLD, color=self.text_primary),
                            ft.Text(
                                f"Seguradora: {p.seguradora.nome}  |  Venda: {p.data_venda.strftime('%d/%m/%Y')}",
                                size=11, color=self.text_secondary,
                            ),
                        ], spacing=2, expand=True),
                        ft.Text(f"R$ {p.valor_bruto:,.2f}", size=13, color=self.text_primary),
                        ft.Container(
                            content=ft.Text(
                                f"{lancamentos_pendentes} pend.",
                                size=11,
                                color="#fca5a5" if lancamentos_pendentes > 0 else "#86efac",
                            ),
                            bgcolor="#450a0a" if lancamentos_pendentes > 0 else "#14532d",
                            padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                            border_radius=12,
                        ),
                    ], spacing=10),
                    bgcolor="#1e293b",
                    padding=10,
                    border_radius=8,
                    border=ft.Border.all(1, "#334155"),
                )
            )

        content = ft.Column(
            controls=[
                # Cabeçalho
                ft.Row([
                    ft.Column([
                        ft.Text(corretor.nome, size=20, weight=ft.FontWeight.BOLD, color=self.text_primary),
                        ft.Text(corretor.email or "Sem e-mail", size=13, color=self.text_secondary),
                        ft.Text(corretor.telefone or "Sem telefone", size=13, color=self.text_secondary),
                    ], spacing=3),
                    ft.Container(expand=True),
                    ft.Container(
                        content=ft.Text(
                            f"{comissao_perc}%",
                            size=22, weight=ft.FontWeight.BOLD, color=self.primary_color,
                        ),
                        bgcolor="#1e1b4b",
                        padding=ft.Padding.symmetric(horizontal=16, vertical=8),
                        border_radius=12,
                    ),
                ]),
                ft.Divider(color="#334155"),
                # Resumo financeiro
                ft.Row([
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Total Apólices", size=11, color=self.text_secondary),
                            ft.Text(f"R$ {total_bruto:,.2f}", size=16, weight=ft.FontWeight.BOLD, color=self.text_primary),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        bgcolor="#1e293b", padding=14, border_radius=8, expand=True,
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Comissão Total", size=11, color=self.text_secondary),
                            ft.Text(f"R$ {total_comissao:,.2f}", size=16, weight=ft.FontWeight.BOLD, color=self.primary_color),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        bgcolor="#1e293b", padding=14, border_radius=8, expand=True,
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Pago", size=11, color=self.text_secondary),
                            ft.Text(f"R$ {total_pago:,.2f}", size=16, weight=ft.FontWeight.BOLD, color=self.accent_color),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        bgcolor="#1e293b", padding=14, border_radius=8, expand=True,
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Pendente", size=11, color=self.text_secondary),
                            ft.Text(f"R$ {total_pendente:,.2f}", size=16, weight=ft.FontWeight.BOLD, color=self.error_color),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        bgcolor="#1e293b", padding=14, border_radius=8, expand=True,
                    ),
                ], spacing=10),
                ft.Divider(color="#334155"),
                ft.Text(f"Propostas ({len(propostas)})", size=15, weight=ft.FontWeight.BOLD, color=self.text_primary),
                ft.Column(
                    controls=proposta_rows if proposta_rows else [
                        ft.Text("Nenhuma proposta.", color=self.text_secondary, size=13)
                    ],
                    spacing=6,
                    scroll=ft.ScrollMode.AUTO,
                    height=200,
                ),
            ],
            spacing=12,
            width=620,
            tight=True,
        )

        dialog = ft.AlertDialog(
            title=ft.Text(f"👤 Detalhes - {corretor.nome}"),
            content=content,
            actions=[
                ft.FilledButton(
                    content=ft.Text("Fechar"),
                    on_click=lambda e: (setattr(dialog, 'open', False), self.page.update()),
                ),
            ],
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

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
                valor_total=lancamento.valor_esperado,
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

        def marcar_recebido(e, tx_id):
            from modulo_financeiro import TransacaoFinanceira
            from datetime import date as date_type
            try:
                tx = self.session.query(TransacaoFinanceira).get(tx_id)
                if tx:
                    tx.status = 'PAGO'
                    tx.data_pagamento = date_type.today()
                    self.session.commit()
                self.show_snackbar("✅ Recebimento registrado!", self.accent_color)
                self.page.clean()
                self.build_ui()
                self.page.update()
            except Exception as ex:
                self.show_snackbar(f"❌ Erro: {str(ex)}", self.error_color)

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
                        ], spacing=2, expand=True),
                        ft.Text(f"R$ {conta.valor:,.2f}", size=16, weight=ft.FontWeight.BOLD, color=self.accent_color),
                        ft.FilledButton(
                            content=ft.Text("✓ Recebido", size=12),
                            style=ft.ButtonStyle(bgcolor=self.accent_color),
                            on_click=lambda e, tid=conta.id: marcar_recebido(e, tid),
                        ),
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
            """Abre formulário para nova transação financeira"""
            from modulo_financeiro import TransacaoFinanceira, CategoriaFinanceira, ContaBancaria
            from datetime import date as date_type

            categorias = self.session.query(CategoriaFinanceira).all()
            contas = self.session.query(ContaBancaria).filter_by(ativa=True).all()

            desc_field = ft.TextField(label="Descrição", width=380)
            tipo_dropdown = ft.Dropdown(
                label="Tipo",
                width=160,
                options=[
                    ft.dropdown.Option("RECEITA", "📈 Receita"),
                    ft.dropdown.Option("DESPESA", "📉 Despesa"),
                ],
                value="RECEITA",
            )
            valor_field = ft.TextField(
                label="Valor (R$)", width=160, keyboard_type=ft.KeyboardType.NUMBER
            )
            data_field = ft.TextField(
                label="Data (DD/MM/AAAA)",
                value=date_type.today().strftime("%d/%m/%Y"),
                width=180,
            )
            venc_field = ft.TextField(
                label="Vencimento (opcional)",
                hint_text="DD/MM/AAAA",
                width=180,
            )
            obs_field = ft.TextField(label="Observações", multiline=True, max_lines=2, width=380)

            categoria_dropdown = ft.Dropdown(
                label="Categoria",
                width=200,
                options=[ft.dropdown.Option(str(c.id), c.nome) for c in categorias],
            )
            conta_dropdown = ft.Dropdown(
                label="Conta",
                width=200,
                options=[ft.dropdown.Option(str(c.id), c.nome) for c in contas],
            )

            def salvar(e):
                try:
                    if not desc_field.value or not valor_field.value:
                        self.show_snackbar("❌ Preencha descrição e valor!", self.error_color)
                        return

                    from datetime import datetime as dt
                    data_obj = dt.strptime(data_field.value, "%d/%m/%Y").date()
                    venc_obj = None
                    if venc_field.value:
                        venc_obj = dt.strptime(venc_field.value, "%d/%m/%Y").date()

                    transacao = TransacaoFinanceira(
                        descricao=desc_field.value,
                        tipo=tipo_dropdown.value,
                        valor=float(valor_field.value.replace(",", ".")),
                        data_transacao=data_obj,
                        data_vencimento=venc_obj,
                        status="PENDENTE",
                        categoria_id=int(categoria_dropdown.value) if categoria_dropdown.value else None,
                        conta_id=int(conta_dropdown.value) if conta_dropdown.value else None,
                        observacoes=obs_field.value or None,
                    )
                    self.session.add(transacao)
                    self.session.commit()
                    self.show_snackbar("✅ Transação registrada!", self.accent_color)
                    dialog.open = False
                    self.page.update()
                    self.page.clean()
                    self.build_ui()
                    self.page.update()
                except Exception as ex:
                    self.show_snackbar(f"❌ Erro: {str(ex)}", self.error_color)

            dialog = ft.AlertDialog(
                title=ft.Text("➕ Nova Transação Financeira"),
                content=ft.Column(
                    controls=[
                        ft.Row([tipo_dropdown, valor_field], spacing=10),
                        desc_field,
                        ft.Row([data_field, venc_field], spacing=10),
                        ft.Row([categoria_dropdown, conta_dropdown], spacing=10),
                        obs_field,
                    ],
                    tight=True,
                    spacing=10,
                    width=420,
                ),
                actions=[
                    ft.TextButton(
                        content=ft.Text("Cancelar"),
                        on_click=lambda e: (setattr(dialog, 'open', False), self.page.update()),
                    ),
                    ft.FilledButton(
                        content=ft.Text("✅ Salvar"),
                        on_click=salvar,
                        style=ft.ButtonStyle(bgcolor=self.accent_color),
                    ),
                ],
            )
            self.page.dialog = dialog
            dialog.open = True
            self.page.update()

        def gerenciar_categorias(e):
            """Abre dialog para gerenciar categorias financeiras"""
            from modulo_financeiro import CategoriaFinanceira

            categorias = self.session.query(CategoriaFinanceira).all()

            nome_field = ft.TextField(label="Nome da Categoria", width=220)
            tipo_cat = ft.Dropdown(
                label="Tipo",
                width=140,
                options=[
                    ft.dropdown.Option("RECEITA", "📈 Receita"),
                    ft.dropdown.Option("DESPESA", "📉 Despesa"),
                ],
                value="RECEITA",
            )

            lista_ref = ft.Column(spacing=5, scroll=ft.ScrollMode.AUTO, height=200)

            def refresh_lista():
                cats = self.session.query(CategoriaFinanceira).all()
                lista_ref.controls.clear()
                for cat in cats:
                    def del_cat(e, c=cat):
                        self.session.delete(c)
                        self.session.commit()
                        refresh_lista()
                        self.page.update()

                    lista_ref.controls.append(
                        ft.Row([
                            ft.Container(
                                content=ft.Text(
                                    "R" if cat.tipo == "RECEITA" else "D",
                                    size=11, color="#86efac" if cat.tipo == "RECEITA" else "#fca5a5",
                                ),
                                bgcolor="#14532d" if cat.tipo == "RECEITA" else "#450a0a",
                                padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                                border_radius=10,
                            ),
                            ft.Text(cat.nome, size=13, color=self.text_primary, expand=True),
                            ft.IconButton(
                                icon=ft.icons.DELETE_OUTLINE,
                                icon_color=self.error_color,
                                icon_size=18,
                                on_click=del_cat,
                            ),
                        ], spacing=8)
                    )
                self.page.update()

            def adicionar_cat(e):
                if not nome_field.value:
                    return
                nova = CategoriaFinanceira(nome=nome_field.value, tipo=tipo_cat.value)
                self.session.add(nova)
                self.session.commit()
                nome_field.value = ""
                refresh_lista()
                self.page.update()

            refresh_lista()

            dialog = ft.AlertDialog(
                title=ft.Text("🏷️ Gerenciar Categorias"),
                content=ft.Column([
                    ft.Row([nome_field, tipo_cat], spacing=8),
                    ft.FilledButton(
                        content=ft.Text("➕ Adicionar"),
                        style=ft.ButtonStyle(bgcolor=self.primary_color),
                        on_click=adicionar_cat,
                    ),
                    ft.Divider(color="#334155"),
                    lista_ref,
                ], tight=True, spacing=10, width=400),
                actions=[
                    ft.FilledButton(
                        content=ft.Text("Fechar"),
                        on_click=lambda e: (setattr(dialog, 'open', False), self.page.update()),
                    ),
                ],
            )
            self.page.dialog = dialog
            dialog.open = True
            self.page.update()

        def criar_meta(e):
            """Abre formulário para criar meta financeira"""
            from modulo_financeiro import Meta
            from datetime import datetime as dt

            nome_field = ft.TextField(label="Nome da Meta", width=300)
            tipo_dropdown = ft.Dropdown(
                label="Tipo",
                width=150,
                options=[
                    ft.dropdown.Option("RECEITA", "📈 Receita"),
                    ft.dropdown.Option("DESPESA", "📉 Despesa"),
                    ft.dropdown.Option("LUCRO", "💰 Lucro"),
                ],
                value="RECEITA",
            )
            valor_field = ft.TextField(
                label="Valor Meta (R$)", width=160, keyboard_type=ft.KeyboardType.NUMBER
            )
            periodo_dropdown = ft.Dropdown(
                label="Período",
                width=150,
                options=[
                    ft.dropdown.Option("MENSAL", "Mensal"),
                    ft.dropdown.Option("TRIMESTRAL", "Trimestral"),
                    ft.dropdown.Option("ANUAL", "Anual"),
                ],
                value="MENSAL",
            )
            ano_field = ft.TextField(
                label="Ano", value=str(dt.now().year), width=100, keyboard_type=ft.KeyboardType.NUMBER
            )
            mes_field = ft.TextField(
                label="Mês (1-12)", value=str(dt.now().month), width=100, keyboard_type=ft.KeyboardType.NUMBER
            )

            def salvar_meta(e):
                try:
                    if not nome_field.value or not valor_field.value:
                        self.show_snackbar("❌ Preencha nome e valor!", self.error_color)
                        return

                    meta = Meta(
                        nome=nome_field.value,
                        tipo=tipo_dropdown.value,
                        valor_meta=float(valor_field.value.replace(",", ".")),
                        periodo=periodo_dropdown.value,
                        mes=int(mes_field.value) if mes_field.value else None,
                        ano=int(ano_field.value),
                        ativa=True,
                    )
                    self.session.add(meta)
                    self.session.commit()
                    self.show_snackbar("✅ Meta criada com sucesso!", self.accent_color)
                    dialog.open = False
                    self.page.update()
                    self.page.clean()
                    self.build_ui()
                    self.page.update()
                except Exception as ex:
                    self.show_snackbar(f"❌ Erro: {str(ex)}", self.error_color)

            dialog = ft.AlertDialog(
                title=ft.Text("🎯 Criar Nova Meta Financeira"),
                content=ft.Column([
                    nome_field,
                    ft.Row([tipo_dropdown, valor_field], spacing=10),
                    ft.Row([periodo_dropdown, ano_field, mes_field], spacing=10),
                ], tight=True, spacing=10, width=380),
                actions=[
                    ft.TextButton(
                        content=ft.Text("Cancelar"),
                        on_click=lambda e: (setattr(dialog, 'open', False), self.page.update()),
                    ),
                    ft.FilledButton(
                        content=ft.Text("✅ Criar Meta"),
                        on_click=salvar_meta,
                        style=ft.ButtonStyle(bgcolor=self.accent_color),
                    ),
                ],
            )
            self.page.dialog = dialog
            dialog.open = True
            self.page.update()

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

        def editar_imposto(nome_imposto, valor_atual):
            """Abre dialog para editar alíquota"""
            valor_field = ft.TextField(
                label=f"Nova alíquota para {nome_imposto} (%)",
                value=str(valor_atual),
                width=260,
                keyboard_type=ft.KeyboardType.NUMBER,
            )

            def salvar(e):
                try:
                    novo_valor = float(valor_field.value.replace(",", "."))
                    if novo_valor < 0 or novo_valor > 100:
                        self.show_snackbar("❌ Valor deve ser entre 0 e 100!", self.error_color)
                        return
                    config.set_imposto(nome_imposto, novo_valor)
                    self.show_snackbar(f"✅ {nome_imposto} atualizado para {novo_valor}%", self.accent_color)
                    dialog.open = False
                    self.page.update()
                    self.page.clean()
                    self.build_ui()
                    self.page.update()
                except ValueError:
                    self.show_snackbar("❌ Valor inválido!", self.error_color)

            dialog = ft.AlertDialog(
                title=ft.Text(f"✏️ Editar {nome_imposto}"),
                content=ft.Column([
                    ft.Text(f"Alíquota atual: {valor_atual}%", size=14, color=self.text_secondary),
                    valor_field,
                ], tight=True, spacing=10),
                actions=[
                    ft.TextButton(
                        content=ft.Text("Cancelar"),
                        on_click=lambda e: (setattr(dialog, 'open', False), self.page.update()),
                    ),
                    ft.FilledButton(
                        content=ft.Text("✅ Salvar"),
                        on_click=salvar,
                        style=ft.ButtonStyle(bgcolor=self.accent_color),
                    ),
                ],
            )
            self.page.dialog = dialog
            dialog.open = True
            self.page.update()

        impostos_list = ft.Column(
            controls=[
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Text("%", size=18, color=self.primary_color),
                            bgcolor="#1e1b4b",
                            padding=10,
                            border_radius=8,
                            width=44,
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Column([
                            ft.Text(nome, size=15, weight=ft.FontWeight.BOLD, color=self.text_primary),
                            ft.Text(f"Alíquota: {valor}%", size=13, color=self.text_secondary),
                        ], spacing=2, expand=True),
                        ft.FilledButton(
                            content=ft.Text("✏️ Editar", size=13),
                            style=ft.ButtonStyle(bgcolor=self.primary_color),
                            on_click=lambda e, n=nome, v=valor: editar_imposto(n, v),
                            height=38,
                        ),
                    ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=self.surface_color,
                    padding=ft.Padding.symmetric(horizontal=16, vertical=12),
                    border_radius=10,
                    border=ft.Border.all(1, "#334155"),
                )
                for nome, valor in impostos.items()
            ],
            spacing=8,
        )

        total_impostos = sum(impostos.values())

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row([
                        ft.Text(
                            "⚙️ Configurações de Impostos",
                            size=26,
                            weight=ft.FontWeight.BOLD,
                            color=self.text_primary,
                        ),
                        ft.Container(expand=True),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Total de Impostos", size=11, color=self.text_secondary),
                                ft.Text(f"{total_impostos:.2f}%", size=20, weight=ft.FontWeight.BOLD, color=self.error_color),
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            bgcolor=self.surface_color,
                            padding=ft.Padding.symmetric(horizontal=20, vertical=10),
                            border_radius=10,
                            border=ft.Border.all(1, "#334155"),
                        ),
                    ]),
                    ft.Text(
                        "Clique em ✏️ Editar para alterar a alíquota de cada imposto.",
                        size=13,
                        color=self.text_secondary,
                        italic=True,
                    ),
                    ft.Divider(height=20, color="#334155"),
                    impostos_list,
                ],
                scroll=ft.ScrollMode.AUTO,
                spacing=12,
            ),
            padding=25,
        )

    async def importar_pdf(self, e):
        """Abre seletor de arquivo, mostra loading animado durante OCR e exibe dialog de revisão"""
        import asyncio, threading

        arquivos = await self.file_picker.pick_files(
            dialog_title="Selecionar Proposta PDF",
            allowed_extensions=["pdf"],
            allow_multiple=False,
        )

        if not arquivos:
            self.show_snackbar("Nenhum arquivo selecionado.", self.text_secondary)
            return

        file_path = arquivos[0].path
        file_name = arquivos[0].name

        # ── Loading dialog ─────────────────────────────────────────────────────
        status_text = ft.Text("📄 Lendo o arquivo...", size=13, color=self.text_secondary)
        etapa_text  = ft.Text("Etapa 1 de 4", size=11, color=self.text_secondary)
        progress    = ft.ProgressBar(
            width=420, value=0.0,
            color=self.primary_color, bgcolor="#334155",
        )

        loading_dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("🔍 Extraindo dados do PDF", size=15, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(file_name, size=12, color=self.text_secondary, italic=True),
                    ft.Container(height=18),
                    progress,
                    ft.Container(height=10),
                    status_text,
                    etapa_text,
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                width=460, height=170, padding=20,
            ),
        )
        self.page.dialog = loading_dlg
        loading_dlg.open = True
        self.page.update()

        # ── OCR em thread separada para não travar a UI ────────────────────────
        resultado = {'dados': None, 'erro': None}

        def run_ocr():
            try:
                from ocr_engine import OCREngine
                ocr = OCREngine()
                resultado['dados'] = ocr.extrair_dados_proposta(
                    ocr.extrair_texto_pdf(file_path)
                )
                ocr.fechar()
            except Exception as ex:
                resultado['erro'] = ex

        ocr_thread = threading.Thread(target=run_ocr, daemon=True)
        ocr_thread.start()

        # ── Animação de progresso enquanto OCR roda ────────────────────────────
        etapas = [
            (0.15, "📄 Lendo o arquivo PDF...",        "Etapa 1 de 4"),
            (0.40, "🔍 Extraindo texto das páginas...", "Etapa 2 de 4"),
            (0.70, "🧠 Identificando campos...",        "Etapa 3 de 4"),
            (0.90, "👥 Buscando dependentes...",        "Etapa 4 de 4"),
        ]
        idx = 0
        while ocr_thread.is_alive():
            val, msg, etapa = etapas[idx % len(etapas)]
            progress.value   = val
            status_text.value = msg
            etapa_text.value  = etapa
            self.page.update()
            idx += 1
            await asyncio.sleep(0.9)

        ocr_thread.join()

        # Barra completa
        progress.value    = 1.0
        status_text.value = "✅ Extração concluída!"
        etapa_text.value  = ""
        self.page.update()
        await asyncio.sleep(0.5)

        loading_dlg.open = False
        self.page.update()

        if resultado['erro']:
            self.show_snackbar(f"❌ Erro ao processar PDF: {resultado['erro']}", self.error_color)
            return

        self._abrir_tela_revisao_proposta(resultado['dados'], file_name)

    def _abrir_tela_revisao_proposta(self, dados: dict, file_name: str = ""):
        """Tela completa de revisão e validação dos dados extraídos do PDF de proposta"""
        from database import Corretor, Seguradora

        corretores = self.session.query(Corretor).all()
        seguradoras = self.session.query(Seguradora).all()

        def _voltar():
            self.page.clean()
            self.build_ui()
            self.page.update()

        # ── helper ────────────────────────────────────────────────────────────
        def _tf(label, valor, width, **kw):
            filled = bool(valor and str(valor).strip())
            return ft.TextField(
                label=label,
                value=str(valor).strip() if filled else "",
                width=width,
                border_color=self.accent_color if filled else None,
                focused_border_color=self.primary_color,
                bgcolor=self.surface_color,
                **kw,
            )

        def _pre_select(lista, nome_extraido, tolerancia=0.20):
            """Seleciona o item mais similar com até 'tolerancia' de diferença (padrão 20%)"""
            import difflib, unicodedata as _ud
            if not nome_extraido or not lista:
                return None
            def _norm(t):
                t2 = _ud.normalize('NFKD', t or "")
                t2 = "".join(c for c in t2 if not _ud.combining(c))
                import re as _re
                return _re.sub(r'\s+', ' ', t2).strip().lower()
            alvo = _norm(nome_extraido)
            melhor_id = None
            melhor_ratio = 0.0
            for item in lista:
                ratio = difflib.SequenceMatcher(None, alvo, _norm(item.nome)).ratio()
                if ratio > melhor_ratio:
                    melhor_ratio = ratio
                    melhor_id = str(item.id)
            return melhor_id if melhor_ratio >= (1.0 - tolerancia) else None

        # ── Campos editáveis ───────────────────────────────────────────────────
        f_nome  = _tf("Nome do Cliente *",       dados.get('cliente_nome'), 340)
        f_cpf   = _tf("CPF / CNPJ",              dados.get('cpf_cnpj'),     200)
        f_rg    = _tf("RG",                      dados.get('rg'),           180)
        f_nasc  = _tf("Data de Nascimento",
                      dados['data_nascimento'].strftime('%d/%m/%Y') if dados.get('data_nascimento') else "",
                      160, hint_text="dd/mm/aaaa")
        f_tel   = _tf("Telefone",                dados.get('telefone'),     185)
        f_email = _tf("E-mail",                  dados.get('email'),        290)
        f_plano = _tf("Tipo de Plano / Produto", dados.get('tipo_plano'),   380)
        f_valor = _tf("Valor do Contrato (R$) *",
                      f"{dados.get('valor_bruto', 0.0):.2f}".replace('.', ','),
                      170, keyboard_type=ft.KeyboardType.NUMBER)

        corretor_dd = ft.Dropdown(
            label="Corretor *", width=280,
            options=[ft.dropdown.Option(key=str(c.id), text=c.nome) for c in corretores],
            value=_pre_select(corretores, dados.get('corretor_nome')),
            bgcolor=self.surface_color,
        )
        seguradora_dd = ft.Dropdown(
            label="Seguradora *", width=280,
            options=[ft.dropdown.Option(key=str(s.id), text=s.nome) for s in seguradoras],
            value=_pre_select(seguradoras, dados.get('seguradora_nome')),
            bgcolor=self.surface_color,
        )

        # ── Dependentes ────────────────────────────────────────────────────────
        dep_controls    = []
        dep_fields_list = []

        def _build_dep_row(dep_dados=None, indice=0):
            d = dep_dados or {}
            nasc_val = d['data_nascimento'].strftime('%d/%m/%Y') if d.get('data_nascimento') else ""
            fd = {
                'nome':        ft.TextField(label="Nome", value=d.get('nome',''), width=240,
                                            bgcolor=self.surface_color,
                                            border_color=self.accent_color if d.get('nome') else None),
                'cpf':         ft.TextField(label="CPF",  value=d.get('cpf',''), width=170,
                                            bgcolor=self.surface_color,
                                            border_color=self.accent_color if d.get('cpf') else None),
                'rg':          ft.TextField(label="RG",   value=d.get('rg',''),  width=150,
                                            bgcolor=self.surface_color,
                                            border_color=self.accent_color if d.get('rg') else None),
                'nasc':        ft.TextField(label="Nascimento", value=nasc_val, width=140,
                                            hint_text="dd/mm/aaaa", bgcolor=self.surface_color,
                                            border_color=self.accent_color if nasc_val else None),
                'parentesco':  ft.TextField(label="Parentesco", value=d.get('parentesco',''), width=160,
                                            bgcolor=self.surface_color,
                                            border_color=self.accent_color if d.get('parentesco') else None),
                'sexo':        ft.Dropdown(
                                    label="Sexo", width=140,
                                    options=[
                                        ft.dropdown.Option("Masculino"),
                                        ft.dropdown.Option("Feminino"),
                                    ],
                                    value=d.get('sexo') if d.get('sexo') in ('Masculino', 'Feminino') else None,
                                    bgcolor=self.surface_color,
                               ),
                'estado_civil': ft.Dropdown(
                                    label="Estado Civil", width=180,
                                    options=[
                                        ft.dropdown.Option("Solteiro(a)"),
                                        ft.dropdown.Option("Casado(a)"),
                                        ft.dropdown.Option("Divorciado(a)"),
                                        ft.dropdown.Option("Viúvo(a)"),
                                        ft.dropdown.Option("União Estável"),
                                        ft.dropdown.Option("Separado(a)"),
                                    ],
                                    value=d.get('estado_civil') or None,
                                    bgcolor=self.surface_color,
                               ),
            }
            dep_fields_list.append(fd)
            return ft.Container(
                content=ft.Column([
                    ft.Text(f"Dependente {indice + 1}", size=12,
                            weight=ft.FontWeight.BOLD, color=self.primary_color),
                    ft.Row([fd['nome'], fd['cpf'], fd['rg']], spacing=8, wrap=True),
                    ft.Row([fd['nasc'], fd['parentesco'], fd['sexo'], fd['estado_civil']],
                           spacing=8, wrap=True),
                ], spacing=6),
                bgcolor="#0f1e33",
                padding=ft.Padding.symmetric(horizontal=14, vertical=10),
                border_radius=8,
                border=ft.Border.all(1, "#2d3f6e"),
            )

        for i, dep in enumerate(dados.get('dependentes', [])):
            dep_controls.append(_build_dep_row(dep, i))

        dep_col = ft.Column(controls=dep_controls, spacing=8)

        def adicionar_dependente(e):
            dep_controls.append(_build_dep_row(indice=len(dep_fields_list)))
            dep_col.controls = dep_controls[:]
            self.page.update()

        # ── Salvar ────────────────────────────────────────────────────────────
        def confirmar_salvar(e):
            from database import Proposta, Dependente
            from datetime import datetime as dt

            if not f_nome.value.strip():
                self.show_snackbar("❌ Nome do cliente é obrigatório!", self.error_color); return
            if not corretor_dd.value:
                self.show_snackbar("❌ Selecione o corretor!", self.error_color); return
            if not seguradora_dd.value:
                self.show_snackbar("❌ Selecione a seguradora!", self.error_color); return
            try:
                nasc_val = None
                if f_nasc.value.strip():
                    try: nasc_val = dt.strptime(f_nasc.value.strip(), '%d/%m/%Y').date()
                    except Exception: pass

                valor_num = 0.0
                try: valor_num = float(f_valor.value.strip().replace(',', '.'))
                except Exception: pass

                proposta = Proposta(
                    cliente_nome=f_nome.value.strip(),
                    cliente_cpf=f_cpf.value.strip() or None,
                    cliente_rg=f_rg.value.strip() or None,
                    cliente_data_nascimento=nasc_val,
                    cliente_telefone=f_tel.value.strip() or None,
                    cliente_email=f_email.value.strip() or None,
                    tipo_plano=f_plano.value.strip() or None,
                    valor_bruto=valor_num,
                    seguradora_id=int(seguradora_dd.value),
                    corretor_id=int(corretor_dd.value),
                    data_venda=dados.get('data_venda') or dt.now().date(),
                )
                self.session.add(proposta)
                self.session.commit()

                ndeps = 0
                for fd in dep_fields_list:
                    nome_dep = fd['nome'].value.strip()
                    if not nome_dep: continue
                    nasc_dep = None
                    if fd['nasc'].value.strip():
                        try: nasc_dep = dt.strptime(fd['nasc'].value.strip(), '%d/%m/%Y').date()
                        except Exception: pass
                    self.session.add(Dependente(
                        proposta_id=proposta.id, nome=nome_dep,
                        cpf=fd['cpf'].value.strip() or None,
                        rg=fd['rg'].value.strip() or None,
                        data_nascimento=nasc_dep,
                        parentesco=fd['parentesco'].value.strip() or None,
                        sexo=fd['sexo'].value or None,
                        estado_civil=fd['estado_civil'].value or None,
                    ))
                    ndeps += 1
                self.session.commit()

                from finance_engine import FinanceEngine
                FinanceEngine(session=self.session).gerar_lancamentos(proposta)

                msg = f"✅ Proposta #{proposta.id} — {proposta.cliente_nome} salva!"
                if ndeps: msg += f"  |  {ndeps} dependente(s)"
                self.page.clean()
                self.build_ui()
                self.page.update()
                self.show_snackbar(msg, self.accent_color)

            except Exception as ex:
                self.show_snackbar(f"❌ Erro ao salvar: {str(ex)}", self.error_color)

        # ══ PAINEL ESQUERDO — resumo extraído (somente leitura) ════════════════
        campos_ok  = sum(1 for v in [dados.get('cliente_nome'), dados.get('cpf_cnpj'),
                                     dados.get('rg'), dados.get('data_nascimento'),
                                     dados.get('telefone'), dados.get('email'),
                                     dados.get('tipo_plano'), dados.get('valor_bruto')] if v)
        ndeps_ext  = len(dados.get('dependentes', []))

        def _item_extraido(icone, label, valor, ok=True):
            cor = self.accent_color if (valor and ok) else "#ef4444"
            txt = str(valor) if valor else "Não encontrado"
            return ft.Row([
                ft.Icon(ft.Icons.CHECK_CIRCLE if (valor and ok) else ft.Icons.CANCEL,
                        color=cor, size=14),
                ft.Column([
                    ft.Text(label, size=10, color=self.text_secondary),
                    ft.Text(txt, size=12, color=self.text_primary,
                            weight=ft.FontWeight.W_500, no_wrap=False),
                ], spacing=0, expand=True),
            ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.START)

        nasc_str = dados['data_nascimento'].strftime('%d/%m/%Y') if dados.get('data_nascimento') else None

        deps_resumo = []
        for dep in dados.get('dependentes', []):
            deps_resumo.append(ft.Container(
                content=ft.Column([
                    ft.Text(dep.get('nome', ''), size=12, weight=ft.FontWeight.BOLD,
                            color=self.text_primary),
                    ft.Text(
                        f"Parentesco: {dep.get('parentesco') or '—'}  •  CPF: {dep.get('cpf') or '—'}",
                        size=11, color=self.text_secondary,
                    ),
                    ft.Text(
                        f"RG: {dep.get('rg') or '—'}  •  Nasc.: "
                        f"{dep['data_nascimento'].strftime('%d/%m/%Y') if dep.get('data_nascimento') else '—'}",
                        size=11, color=self.text_secondary,
                    ),
                    ft.Text(
                        f"Sexo: {dep.get('sexo') or '—'}  •  Est. Civil: {dep.get('estado_civil') or '—'}",
                        size=11, color=self.text_secondary,
                    ),
                ], spacing=2),
                bgcolor="#0f1e33",
                padding=ft.Padding.symmetric(horizontal=10, vertical=6),
                border_radius=6,
                border=ft.Border.all(1, "#2d3f6e"),
            ))

        painel_esq = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.DOCUMENT_SCANNER, color=self.accent_color, size=20),
                        ft.Text(" Dados Extraídos", size=14,
                                weight=ft.FontWeight.BOLD, color=self.text_primary),
                    ]),
                    bgcolor="#0d2818",
                    padding=ft.Padding.symmetric(horizontal=14, vertical=10),
                    border_radius=8,
                    border=ft.Border.all(1, self.accent_color + "50"),
                ),
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.AUTO_AWESOME, color=self.accent_color, size=14),
                        ft.Text(f"{campos_ok} de 8 campos identificados automaticamente",
                                size=11, color=self.accent_color),
                    ], spacing=6),
                    padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                ),
                ft.Divider(height=8, color="#334155"),
                ft.Text("Titular", size=11, weight=ft.FontWeight.BOLD,
                        color=self.text_secondary),
                _item_extraido("👤", "Nome",         dados.get('cliente_nome')),
                _item_extraido("📋", "CPF / CNPJ",   dados.get('cpf_cnpj')),
                _item_extraido("🪪", "RG",            dados.get('rg')),
                _item_extraido("🎂", "Nascimento",    nasc_str),
                _item_extraido("📞", "Telefone",      dados.get('telefone')),
                _item_extraido("✉️", "E-mail",        dados.get('email')),
                ft.Divider(height=8, color="#334155"),
                ft.Text("Contrato", size=11, weight=ft.FontWeight.BOLD,
                        color=self.text_secondary),
                _item_extraido("🏷️", "Plano",         dados.get('tipo_plano')),
                _item_extraido("💰", "Valor",
                               f"R$ {dados['valor_bruto']:,.2f}" if dados.get('valor_bruto') else None),
                _item_extraido("💼", "Corretor",      dados.get('corretor_nome')),
                _item_extraido("🏢", "Seguradora",    dados.get('seguradora_nome')),
                ft.Divider(height=8, color="#334155"),
                ft.Row([
                    ft.Icon(ft.Icons.PEOPLE, color=self.primary_color, size=14),
                    ft.Text(f"Dependentes ({ndeps_ext})", size=11,
                            weight=ft.FontWeight.BOLD, color=self.text_secondary),
                ], spacing=6),
                *(deps_resumo if deps_resumo else [
                    ft.Text("Nenhum dependente encontrado", size=11,
                            color=self.text_secondary, italic=True)
                ]),
            ], spacing=6, scroll=ft.ScrollMode.AUTO),
            bgcolor=self.surface_color,
            padding=16,
            border_radius=12,
            border=ft.Border.all(1, "#334155"),
            width=310,
            expand=False,
        )

        # ══ PAINEL DIREITO — formulário editável ═══════════════════════════════
        painel_dir = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.EDIT_NOTE, color=self.primary_color, size=20),
                        ft.Text(" Confirmar / Corrigir Informações", size=14,
                                weight=ft.FontWeight.BOLD, color=self.text_primary),
                    ]),
                    bgcolor="#0d1f3c",
                    padding=ft.Padding.symmetric(horizontal=14, vertical=10),
                    border_radius=8,
                    border=ft.Border.all(1, self.primary_color + "50"),
                ),
                ft.Text("Campos com borda verde foram preenchidos automaticamente pelo OCR.",
                        size=11, color=self.text_secondary, italic=True),
                ft.Divider(height=8, color="#334155"),

                ft.Text("👤 Dados do Titular", size=12,
                        weight=ft.FontWeight.BOLD, color=self.primary_color),
                ft.Row([f_nome], spacing=8),
                ft.Row([f_cpf, f_rg], spacing=8, wrap=True),
                ft.Row([f_nasc, f_tel, f_email], spacing=8, wrap=True),

                ft.Divider(height=8, color="#334155"),
                ft.Text("📋 Plano e Contrato", size=12,
                        weight=ft.FontWeight.BOLD, color=self.primary_color),
                ft.Row([f_plano], spacing=8),
                ft.Row([f_valor], spacing=8),
                ft.Row([corretor_dd, seguradora_dd], spacing=8, wrap=True),

                ft.Divider(height=8, color="#334155"),
                ft.Row([
                    ft.Text("👥 Dependentes", size=12,
                            weight=ft.FontWeight.BOLD, color=self.primary_color),
                    ft.TextButton(
                        content=ft.Text("+ Adicionar", size=11, color=self.accent_color),
                        on_click=adicionar_dependente,
                    ),
                ]),
                dep_col,
            ], spacing=8, scroll=ft.ScrollMode.AUTO),
            bgcolor=self.surface_color,
            padding=16,
            border_radius=12,
            border=ft.Border.all(1, "#334155"),
            expand=True,
        )

        # ══ BARRA DE TOPO ══════════════════════════════════════════════════════
        topo = ft.Container(
            content=ft.Row([
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    icon_color=self.text_primary,
                    tooltip="Voltar sem salvar",
                    on_click=lambda e: _voltar(),
                ),
                ft.Column([
                    ft.Text("Validação de Proposta Importada", size=16,
                            weight=ft.FontWeight.BOLD, color=self.text_primary),
                    ft.Text(f"Arquivo: {file_name}", size=11,
                            color=self.text_secondary, italic=True),
                ], spacing=1),
                ft.Container(expand=True),
                ft.OutlinedButton(
                    content=ft.Text("← Cancelar", color=self.error_color),
                    style=ft.ButtonStyle(side=ft.BorderSide(1, self.error_color)),
                    on_click=lambda e: _voltar(),
                ),
                ft.FilledButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.SAVE_ALT, size=16, color="white"),
                        ft.Text("  Confirmar e Salvar", color="white",
                                weight=ft.FontWeight.BOLD),
                    ]),
                    style=ft.ButtonStyle(bgcolor=self.accent_color, padding=18),
                    height=44,
                    on_click=confirmar_salvar,
                ),
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=self.surface_color,
            padding=ft.Padding.symmetric(horizontal=20, vertical=12),
            border=ft.Border(bottom=ft.BorderSide(1, "#334155")),
        )

        # ══ TELA COMPLETA ══════════════════════════════════════════════════════
        tela = ft.Container(
            content=ft.Column([
                topo,
                ft.Container(
                    content=ft.Row([
                        painel_esq,
                        ft.Container(width=16),
                        painel_dir,
                    ], vertical_alignment=ft.CrossAxisAlignment.START, expand=True),
                    expand=True,
                    padding=ft.Padding.symmetric(horizontal=20, vertical=16),
                ),
            ], spacing=0, expand=True),
            bgcolor=self.background_color,
            expand=True,
        )

        self.page.clean()
        self.page.add(tela)
        self.page.update()

    async def importar_comissoes(self, e):
        """Importa PDF de extrato/relatório de comissões com loading animado e dialog de revisão"""
        import asyncio, threading

        arquivos = await self.file_picker_com.pick_files(
            dialog_title="Selecionar Relatório de Comissões (PDF)",
            allowed_extensions=["pdf"],
            allow_multiple=False,
        )

        if not arquivos:
            self.show_snackbar("Nenhum arquivo selecionado.", self.text_secondary)
            return

        file_path = arquivos[0].path
        file_name = arquivos[0].name

        # ── Loading dialog ─────────────────────────────────────────────────────
        status_text = ft.Text("📄 Lendo o arquivo...", size=13, color=self.text_secondary)
        etapa_text  = ft.Text("Etapa 1 de 3", size=11, color=self.text_secondary)
        progress    = ft.ProgressBar(width=420, value=0.0, color="#7c3aed", bgcolor="#334155")

        loading_dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("💰 Extraindo Comissões do PDF", size=15, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(file_name, size=12, color=self.text_secondary, italic=True),
                    ft.Container(height=18),
                    progress,
                    ft.Container(height=10),
                    status_text,
                    etapa_text,
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                width=460, height=170, padding=20,
            ),
        )
        self.page.dialog = loading_dlg
        loading_dlg.open = True
        self.page.update()

        # ── Extração em thread ─────────────────────────────────────────────────
        resultado = {'dados': None, 'texto': None, 'formato': None, 'erro': None}

        def run_ocr():
            try:
                from ocr_engine import OCREngine
                ocr = OCREngine()
                texto = ocr.extrair_texto_pdf(file_path)
                resultado['texto'] = texto
                fmt = ocr.detectar_formato(texto)
                resultado['formato'] = fmt
                if fmt == 'ALLCARE':
                    resultado['dados'] = ocr.extrair_dados_allcare(texto)
                else:
                    resultado['dados'] = ocr.extrair_dados_comissao(texto)
                ocr.fechar()
            except Exception as ex:
                resultado['erro'] = ex

        ocr_thread = threading.Thread(target=run_ocr, daemon=True)
        ocr_thread.start()

        etapas = [
            (0.20, "📄 Lendo o relatório...",         "Etapa 1 de 3"),
            (0.55, "🔍 Identificando pagamentos...",   "Etapa 2 de 3"),
            (0.85, "💰 Calculando comissões...",        "Etapa 3 de 3"),
        ]
        idx = 0
        while ocr_thread.is_alive():
            val, msg, etapa = etapas[idx % len(etapas)]
            progress.value    = val
            status_text.value = msg
            etapa_text.value  = etapa
            self.page.update()
            idx += 1
            await asyncio.sleep(0.9)

        ocr_thread.join()
        progress.value    = 1.0
        status_text.value = "✅ Extração concluída!"
        etapa_text.value  = ""
        self.page.update()
        await asyncio.sleep(0.5)

        loading_dlg.open = False
        self.page.update()

        if resultado['erro']:
            self.show_snackbar(f"❌ Erro ao processar PDF: {resultado['erro']}", self.error_color)
            return

        if resultado.get('formato') == 'ALLCARE':
            self._abrir_tela_revisao_allcare(resultado['dados'], file_name)
        else:
            self._abrir_tela_revisao_comissoes(resultado['dados'], resultado['texto'], file_name)

    def _abrir_tela_revisao_allcare(self, dados: dict, file_name: str = ""):
        """Tela completa de revisão e importação de extrato Allcare Benefícios"""
        from database import Corretor, Lancamento as _Lanc, Proposta
        from modulo_financeiro import TransacaoFinanceira, ContaBancaria
        from datetime import datetime as dt

        COR_TEAL = "#0d9488"

        def _voltar():
            self.page.clean()
            self.build_ui()
            self.page.update()

        def _fmt_val(v):
            if v is None:
                return "—"
            try:
                return f"R$ {float(v):,.2f}"
            except Exception:
                return str(v)

        def _fmt_data(d):
            if not d:
                return "—"
            try:
                return d.strftime('%d/%m/%Y')
            except Exception:
                return str(d)

        # ── Checkboxes de seleção de itens ─────────────────────────────────────
        itens = dados.get('itens', [])
        checks = [ft.Checkbox(value=True, fill_color=COR_TEAL) for _ in itens]

        # ── Painel esquerdo — informações do extrato ───────────────────────────
        status_color = "#10b981" if dados.get('status_financeiro') == 'RECEBIDO' else "#f59e0b"
        status_label = dados.get('status_financeiro', 'PENDENTE')

        val_status = dados.get('validacao', {})
        val_cor = "#10b981" if val_status.get('status') == 'OK' else "#ef4444"
        val_txt = (f"✅ Soma OK — R$ {val_status.get('soma_comissoes', 0):,.2f}"
                   if val_status.get('status') == 'OK'
                   else f"⚠ Divergência R$ {val_status.get('divergencia', 0):,.2f}")

        def _info_row(label, valor, cor=None):
            return ft.Row([
                ft.Text(label, size=11, color=self.text_secondary, width=130),
                ft.Text(str(valor) if valor else "—", size=11,
                        color=cor or self.text_primary, weight=ft.FontWeight.W_500,
                        no_wrap=False, expand=True),
            ], spacing=4, vertical_alignment=ft.CrossAxisAlignment.START)

        painel_esq = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.RECEIPT_LONG, color=COR_TEAL, size=20),
                        ft.Text(" Extrato Allcare", size=14,
                                weight=ft.FontWeight.BOLD, color=self.text_primary),
                    ]),
                    bgcolor="#0d2e2e", padding=ft.Padding.symmetric(horizontal=14, vertical=10),
                    border_radius=8, border=ft.Border.all(1, COR_TEAL + "60"),
                ),
                ft.Divider(height=6, color="#334155"),
                ft.Text("Identificação", size=11, weight=ft.FontWeight.BOLD,
                        color=self.text_secondary),
                _info_row("Nº Extrato:", dados.get('numero_extrato')),
                _info_row("Corretora:", dados.get('corretora')),
                _info_row("CNPJ:", dados.get('cnpj_produtor')),
                _info_row("Produtor:", dados.get('produtor_nome')),
                _info_row("Período:",
                          f"{_fmt_data(dados.get('periodo_inicio'))} a "
                          f"{_fmt_data(dados.get('periodo_fim'))}"),
                _info_row("Nota Fiscal:", dados.get('nota_fiscal') or "—"),
                ft.Divider(height=6, color="#334155"),
                ft.Text("Financeiro", size=11, weight=ft.FontWeight.BOLD,
                        color=self.text_secondary),
                _info_row("Valor Apurado:", _fmt_val(dados.get('valor_apurado'))),
                _info_row(f"IRRF ({dados.get('aliquota_irrf', 0):.2f}%):",
                          f"– {_fmt_val(dados.get('valor_irrf'))}",
                          "#ef4444"),
                _info_row(f"ISS ({dados.get('aliquota_iss', 0):.2f}%):",
                          f"– {_fmt_val(dados.get('valor_iss'))}",
                          "#ef4444"),
                _info_row("Valor Líquido:", _fmt_val(dados.get('valor_liquido')),
                          COR_TEAL),
                ft.Divider(height=6, color="#334155"),
                ft.Text("Pagamento", size=11, weight=ft.FontWeight.BOLD,
                        color=self.text_secondary),
                _info_row("Banco:", dados.get('banco')),
                _info_row("Agência:", dados.get('agencia')),
                _info_row("Conta:", dados.get('conta')),
                _info_row("Data Prevista:", _fmt_data(dados.get('data_pagamento_previsto'))),
                ft.Container(
                    content=ft.Text(status_label, size=12, weight=ft.FontWeight.BOLD,
                                    color=status_color),
                    bgcolor=status_color + "20",
                    padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                    border_radius=20,
                    border=ft.Border.all(1, status_color + "60"),
                ),
                ft.Divider(height=6, color="#334155"),
                ft.Container(
                    content=ft.Text(val_txt, size=11, color=val_cor),
                    padding=ft.Padding.symmetric(horizontal=8, vertical=6),
                    bgcolor=val_cor + "15", border_radius=6,
                    border=ft.Border.all(1, val_cor + "40"),
                ),
            ], spacing=5, scroll=ft.ScrollMode.AUTO),
            bgcolor=self.surface_color, padding=16, border_radius=12,
            border=ft.Border.all(1, "#334155"), width=320, expand=False,
        )

        # ── Tabela de itens ────────────────────────────────────────────────────
        def _sel_all(e):
            for ch in checks:
                ch.value = e.control.value
            self.page.update()

        check_todos = ft.Checkbox(value=True, fill_color=COR_TEAL, on_change=_sel_all,
                                  tooltip="Selecionar tudo")

        cabecalho = ft.Container(
            content=ft.Row([
                ft.Container(check_todos, width=36),
                ft.Text("Contrato", size=11, weight=ft.FontWeight.BOLD,
                         color=self.text_secondary, width=90),
                ft.Text("Cliente", size=11, weight=ft.FontWeight.BOLD,
                         color=self.text_secondary, expand=True),
                ft.Text("Operadora", size=11, weight=ft.FontWeight.BOLD,
                         color=self.text_secondary, width=110),
                ft.Text("Produto", size=11, weight=ft.FontWeight.BOLD,
                         color=self.text_secondary, width=80),
                ft.Text("Ref.", size=11, weight=ft.FontWeight.BOLD,
                         color=self.text_secondary, width=60),
                ft.Text("Vidas", size=11, weight=ft.FontWeight.BOLD,
                         color=self.text_secondary, width=40, text_align=ft.TextAlign.CENTER),
                ft.Text("Fatura", size=11, weight=ft.FontWeight.BOLD,
                         color=self.text_secondary, width=80, text_align=ft.TextAlign.RIGHT),
                ft.Text("% Com.", size=11, weight=ft.FontWeight.BOLD,
                         color=self.text_secondary, width=55, text_align=ft.TextAlign.CENTER),
                ft.Text("Comissão", size=11, weight=ft.FontWeight.BOLD,
                         color=COR_TEAL, width=80, text_align=ft.TextAlign.RIGHT),
            ], spacing=6),
            bgcolor="#0d2e2e", padding=ft.Padding.symmetric(horizontal=12, vertical=8),
            border_radius=ft.BorderRadius(8, 8, 0, 0),
            border=ft.Border(bottom=ft.BorderSide(1, COR_TEAL + "40")),
        )

        linhas_itens = []
        for idx, item in enumerate(itens):
            ch = checks[idx]
            bg = self.surface_color if idx % 2 == 0 else "#182030"
            tipo_badge_cor = "#6366f1" if item.get('tipo_pessoa') == 'Pessoa Jurídica' else "#10b981"

            linha = ft.Container(
                content=ft.Row([
                    ft.Container(ch, width=36),
                    ft.Text(item.get('numero_contrato', '—'), size=11,
                             color=self.text_secondary, width=90),
                    ft.Column([
                        ft.Text(item.get('nome_cliente', '—'), size=11,
                                color=self.text_primary, weight=ft.FontWeight.W_500,
                                no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Container(
                            content=ft.Text(item.get('tipo_pessoa', '—'), size=9,
                                            color=tipo_badge_cor),
                            bgcolor=tipo_badge_cor + "20",
                            padding=ft.Padding.symmetric(horizontal=5, vertical=1),
                            border_radius=10,
                        ),
                    ], spacing=2, expand=True),
                    ft.Text((item.get('operadora') or '—')[:14], size=10,
                             color=self.text_secondary, width=110, no_wrap=True,
                             overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Text((item.get('produto') or '—')[:10], size=10,
                             color=self.text_secondary, width=80, no_wrap=True,
                             overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Text(item.get('referencia', '—'), size=10,
                             color=self.text_secondary, width=60),
                    ft.Text(str(item.get('vidas', '—')), size=11,
                             color=self.text_primary, width=40,
                             text_align=ft.TextAlign.CENTER),
                    ft.Text(f"R$ {item.get('valor_fatura', 0):,.2f}", size=11,
                             color=self.text_secondary, width=80,
                             text_align=ft.TextAlign.RIGHT),
                    ft.Text(f"{item.get('percentual_comissao', 0):.2f}%", size=11,
                             color=self.text_secondary, width=55,
                             text_align=ft.TextAlign.CENTER),
                    ft.Text(f"R$ {item.get('valor_comissao', 0):,.2f}", size=12,
                             color=COR_TEAL, weight=ft.FontWeight.BOLD, width=80,
                             text_align=ft.TextAlign.RIGHT),
                ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=bg, padding=ft.Padding.symmetric(horizontal=12, vertical=6),
                border=ft.Border(bottom=ft.BorderSide(1, "#2d3748")),
            )
            linhas_itens.append(linha)

        total_selecionado = ft.Text(
            f"Total: {_fmt_val(sum(i.get('valor_comissao', 0) for i in itens))}",
            size=13, weight=ft.FontWeight.BOLD, color=COR_TEAL,
        )

        painel_dir = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.TABLE_ROWS, color=COR_TEAL, size=20),
                        ft.Text(f" Itens de Comissão ({len(itens)})", size=14,
                                weight=ft.FontWeight.BOLD, color=self.text_primary),
                        ft.Container(expand=True),
                        total_selecionado,
                    ]),
                    bgcolor="#0d2e2e", padding=ft.Padding.symmetric(horizontal=14, vertical=10),
                    border_radius=8, border=ft.Border.all(1, COR_TEAL + "50"),
                ),
                ft.Text("Selecione os itens a importar como transações financeiras.",
                        size=11, color=self.text_secondary, italic=True),
                ft.Divider(height=4, color="#334155"),
                cabecalho,
                ft.Container(
                    content=ft.Column(linhas_itens, spacing=0, scroll=ft.ScrollMode.AUTO),
                    border=ft.Border.all(1, "#334155"),
                    border_radius=ft.BorderRadius(0, 0, 8, 8),
                    expand=True,
                ),
            ], spacing=8, expand=True),
            bgcolor=self.surface_color, padding=16, border_radius=12,
            border=ft.Border.all(1, "#334155"), expand=True,
        )

        # ── Salvar ─────────────────────────────────────────────────────────────
        def confirmar_salvar(e):
            itens_sel = [itens[i] for i, ch in enumerate(checks) if ch.value]
            if not itens_sel:
                self.show_snackbar("❌ Selecione pelo menos um item!", self.error_color)
                return
            try:
                conta = self.session.query(ContaBancaria).first()
                if not conta:
                    conta = ContaBancaria(nome="Conta Principal", banco="", agencia="",
                                         conta="", saldo_inicial=0.0, saldo_atual=0.0)
                    self.session.add(conta)
                    self.session.flush()

                hoje = dt.now().date()
                status_tx = ('PAGO'
                             if dados.get('status_financeiro') == 'RECEBIDO'
                             else 'PENDENTE')
                data_pgto = dados.get('data_pagamento_previsto') if status_tx == 'PAGO' else None

                n = 0
                for item in itens_sel:
                    obs = (
                        f"Extrato {dados.get('numero_extrato', '—')} | "
                        f"Operadora: {item.get('operadora', '—')} | "
                        f"Produto: {item.get('produto', '—')} | "
                        f"Ref: {item.get('referencia', '—')} | "
                        f"Fatura: {item.get('numero_fatura', '—')} | "
                        f"Parcela: {item.get('parcela', '—')} | "
                        f"Vidas: {item.get('vidas', '—')}"
                    )
                    rubrica_str = item.get('rubrica', '').strip()
                    tx = TransacaoFinanceira(
                        conta_id       = conta.id,
                        tipo           = 'RECEITA',
                        descricao      = (
                            f"{rubrica_str} — "
                            f"{item.get('nome_cliente', '')} "
                            f"(Contrato {item.get('numero_contrato', '')})"
                        ),
                        valor          = item.get('valor_comissao', 0.0),
                        data_transacao = item.get('data_operacao') or hoje,
                        data_vencimento= item.get('vencimento'),
                        data_pagamento = data_pgto,
                        status         = status_tx,
                        observacoes    = obs,
                    )
                    self.session.add(tx)
                    n += 1

                self.session.commit()
                total = sum(i.get('valor_comissao', 0) for i in itens_sel)
                self.page.clean()
                self.build_ui()
                self.page.update()
                self.show_snackbar(
                    f"✅ {n} transação(ões) importada(s) — Total: R$ {total:,.2f}",
                    self.accent_color,
                )
            except Exception as ex:
                self.show_snackbar(f"❌ Erro ao importar: {str(ex)}", self.error_color)

        # ── Barra de topo ──────────────────────────────────────────────────────
        topo = ft.Container(
            content=ft.Row([
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK, icon_color=self.text_primary,
                    tooltip="Voltar sem salvar", on_click=lambda e: _voltar(),
                ),
                ft.Column([
                    ft.Text(
                        f"Extrato Allcare — Nº {dados.get('numero_extrato', '—')}",
                        size=16, weight=ft.FontWeight.BOLD, color=self.text_primary,
                    ),
                    ft.Text(f"Arquivo: {file_name}", size=11,
                            color=self.text_secondary, italic=True),
                ], spacing=1),
                ft.Container(expand=True),
                ft.OutlinedButton(
                    content=ft.Text("← Cancelar", color=self.error_color),
                    style=ft.ButtonStyle(side=ft.BorderSide(1, self.error_color)),
                    on_click=lambda e: _voltar(),
                ),
                ft.FilledButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.SAVE_ALT, size=16, color="white"),
                        ft.Text("  Importar Selecionados", color="white",
                                weight=ft.FontWeight.BOLD),
                    ]),
                    style=ft.ButtonStyle(bgcolor=COR_TEAL, padding=18),
                    height=44,
                    on_click=confirmar_salvar,
                ),
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=self.surface_color,
            padding=ft.Padding.symmetric(horizontal=20, vertical=12),
            border=ft.Border(bottom=ft.BorderSide(1, "#334155")),
        )

        tela = ft.Container(
            content=ft.Column([
                topo,
                ft.Container(
                    content=ft.Row([
                        painel_esq,
                        ft.Container(width=16),
                        painel_dir,
                    ], vertical_alignment=ft.CrossAxisAlignment.START, expand=True),
                    expand=True,
                    padding=ft.Padding.symmetric(horizontal=20, vertical=16),
                ),
            ], spacing=0, expand=True),
            bgcolor=self.background_color, expand=True,
        )

        self.page.clean()
        self.page.add(tela)
        self.page.update()

    def _abrir_tela_revisao_comissoes(self, dados: dict, texto_bruto: str, file_name: str = ""):
        """Tela completa de revisão e validação dos dados extraídos do PDF de comissões"""
        from database import Corretor, Seguradora
        from datetime import datetime as dt

        corretores  = self.session.query(Corretor).all()
        seguradoras = self.session.query(Seguradora).all()

        COR_PURPLE = "#7c3aed"

        def _voltar():
            self.page.clean()
            self.build_ui()
            self.page.update()

        # ── helper ────────────────────────────────────────────────────────────
        def _tf(label, valor, width, **kw):
            filled = bool(valor and str(valor).strip())
            return ft.TextField(
                label=label,
                value=str(valor).strip() if filled else "",
                width=width,
                border_color=COR_PURPLE if filled else None,
                focused_border_color=self.primary_color,
                bgcolor=self.surface_color,
                **kw,
            )

        def _pre_select(lista, nome_extraido, tolerancia=0.20):
            """Seleciona o item mais similar com até 'tolerancia' de diferença (padrão 20%)"""
            import difflib, unicodedata as _ud
            if not nome_extraido or not lista:
                return None
            def _norm(t):
                t2 = _ud.normalize('NFKD', t or "")
                t2 = "".join(c for c in t2 if not _ud.combining(c))
                import re as _re
                return _re.sub(r'\s+', ' ', t2).strip().lower()
            alvo = _norm(nome_extraido)
            melhor_id = None
            melhor_ratio = 0.0
            for item in lista:
                ratio = difflib.SequenceMatcher(None, alvo, _norm(item.nome)).ratio()
                if ratio > melhor_ratio:
                    melhor_ratio = ratio
                    melhor_id = str(item.id)
            return melhor_id if melhor_ratio >= (1.0 - tolerancia) else None

        # ── Campos editáveis — pré-preencher com dados extraídos ───────────────
        # Usar o nome conforme banco se OCR encontrou match, senão o texto extraído
        nome_corretor_display  = dados.get('corretor_nome_banco') or dados.get('corretor_nome') or ""
        nome_seguradora_display = dados.get('seguradora_nome_banco') or dados.get('seguradora_nome') or ""
        # Pré-selecionar dropdowns usando corretor_id/seguradora_id já resolvidos pelo OCR
        corretor_pre_id  = str(dados['corretor_id'])  if dados.get('corretor_id')  else \
                           _pre_select(corretores,  dados.get('corretor_nome'))
        seguradora_pre_id = str(dados['seguradora_id']) if dados.get('seguradora_id') else \
                            _pre_select(seguradoras, dados.get('seguradora_nome'))

        f_corretor_nome  = _tf("Corretor (extraído)",   nome_corretor_display,   280)
        f_seguradora     = _tf("Seguradora (extraída)", nome_seguradora_display, 280)
        f_valor_bruto    = _tf("Valor Bruto (R$) *",
                               f"{dados.get('valor_bruto', 0.0):.2f}".replace('.', ','),
                               180, keyboard_type=ft.KeyboardType.NUMBER)
        f_valor_comissao = _tf("Valor da Comissão (R$)",
                               f"{dados.get('valor_comissao', 0.0):.2f}".replace('.', ',') if dados.get('valor_comissao') else "",
                               180, keyboard_type=ft.KeyboardType.NUMBER)
        f_comissao       = _tf("% Comissão",     dados.get('comissao') or "",     140)
        f_competencia    = _tf("Competência/Período", dados.get('competencia') or "", 200)
        f_susep          = _tf("SUSEP",          dados.get('susep') or "",         180)
        f_descricao      = _tf("Descrição",      dados.get('descricao') or "",     500,
                               multiline=True, min_lines=2, max_lines=3)

        corretor_dd = ft.Dropdown(
            label="Vincular ao Corretor *", width=300,
            options=[ft.dropdown.Option(key=str(c.id), text=c.nome) for c in corretores],
            value=corretor_pre_id,
            bgcolor=self.surface_color,
        )
        seguradora_dd = ft.Dropdown(
            label="Vincular à Seguradora", width=300,
            options=[ft.dropdown.Option(key=str(s.id), text=s.nome) for s in seguradoras],
            value=seguradora_pre_id,
            bgcolor=self.surface_color,
        )

        # ── Cruzamento: propostas do corretor identificado ─────────────────────
        corretor_id_match = dados.get('corretor_id')
        propostas_corretor = []
        if corretor_id_match:
            propostas_corretor = (
                self.session.query(Proposta)
                .filter(Proposta.corretor_id == corretor_id_match)
                .order_by(Proposta.data_venda.desc())
                .limit(20)
                .all()
            )

        proposta_ids_selecionadas = []  # IDs de propostas a marcar como comissão paga

        def _build_proposta_row(p):
            check = ft.Checkbox(value=False, fill_color=COR_PURPLE)

            def on_check(ev, pid=p.id):
                if ev.control.value:
                    if pid not in proposta_ids_selecionadas:
                        proposta_ids_selecionadas.append(pid)
                else:
                    if pid in proposta_ids_selecionadas:
                        proposta_ids_selecionadas.remove(pid)

            check.on_change = on_check
            seg_nome = p.seguradora.nome if p.seguradora else "—"
            total_pendente = sum(l.valor_esperado for l in p.lancamentos if not l.status_pago)
            return ft.Container(
                content=ft.Row([
                    check,
                    ft.Column([
                        ft.Text(p.cliente_nome, size=12, weight=ft.FontWeight.BOLD,
                                color=self.text_primary),
                        ft.Text(f"{seg_nome}  •  {p.data_venda.strftime('%d/%m/%Y') if p.data_venda else '—'}",
                                size=11, color=self.text_secondary),
                    ], spacing=1, expand=True),
                    ft.Text(f"R$ {p.valor_bruto:,.2f}", size=12, color=COR_PURPLE,
                            weight=ft.FontWeight.BOLD),
                    ft.Text(f"Pendente: R$ {total_pendente:,.2f}", size=11,
                            color="#f59e0b" if total_pendente > 0 else self.text_secondary),
                ], spacing=8),
                bgcolor="#1a0d2e",
                padding=ft.Padding.symmetric(horizontal=12, vertical=8),
                border_radius=6,
                border=ft.Border.all(1, COR_PURPLE + "30"),
            )

        painel_propostas = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.RECEIPT_LONG, color=COR_PURPLE, size=16),
                    ft.Text(
                        f" Propostas do Corretor ({len(propostas_corretor)})",
                        size=13, weight=ft.FontWeight.BOLD, color=self.text_primary,
                    ),
                    ft.Container(expand=True),
                    ft.Text("Marque para vincular comissão:", size=11, color=self.text_secondary),
                ]),
                ft.Divider(height=4, color="#334155"),
                *([_build_proposta_row(p) for p in propostas_corretor]
                  if propostas_corretor
                  else [ft.Text("Nenhuma proposta encontrada para este corretor.",
                                size=12, color=self.text_secondary, italic=True)]),
            ], spacing=6, scroll=ft.ScrollMode.AUTO),
            bgcolor=self.surface_color,
            padding=14, border_radius=10,
            border=ft.Border.all(1, COR_PURPLE + "50"),
            height=260,
        ) if propostas_corretor else ft.Container(
            content=ft.Text(
                "Nenhuma proposta encontrada para o corretor identificado.",
                size=12, color=self.text_secondary, italic=True,
            ),
            padding=12,
        )

        # ── Salvar / registrar comissão ────────────────────────────────────────
        def confirmar_salvar(e):
            if not corretor_dd.value:
                self.show_snackbar("❌ Selecione o corretor para vincular!", self.error_color)
                return
            try:
                from modulo_financeiro import TransacaoFinanceira, ContaBancaria

                conta = self.session.query(ContaBancaria).first()
                if not conta:
                    conta = ContaBancaria(nome="Conta Principal", banco="", saldo_inicial=0.0)
                    self.session.add(conta)
                    self.session.commit()

                valor_num = 0.0
                try:
                    valor_num = float(f_valor_bruto.value.strip().replace(',', '.'))
                except Exception:
                    pass

                corretor_obj = self.session.query(Corretor).get(int(corretor_dd.value))
                seg_nome = f_seguradora.value.strip() or (dados.get('seguradora_nome') or 'Seguradora')

                descricao_tx = (
                    f_descricao.value.strip()
                    or f"Comissão importada — {corretor_obj.nome if corretor_obj else 'Corretor'} | {seg_nome}"
                )

                tx = TransacaoFinanceira(
                    conta_id  = conta.id,
                    tipo      = 'RECEITA',
                    descricao = descricao_tx,
                    valor     = valor_num,
                    data      = dados.get('data_venda') or dt.now().date(),
                )
                self.session.add(tx)
                self.session.commit()

                # Marcar lancamentos das propostas selecionadas como pagos
                npago = 0
                for pid in proposta_ids_selecionadas:
                    from database import Lancamento as _Lanc
                    lans = self.session.query(_Lanc).filter(
                        _Lanc.proposta_id == pid,
                        _Lanc.status_pago == False,
                    ).all()
                    for lan in lans:
                        lan.status_pago = True
                        npago += 1
                if npago:
                    self.session.commit()

                msg = f"✅ Comissão de R$ {valor_num:,.2f} registrada para {corretor_obj.nome if corretor_obj else ''}!"
                if npago:
                    msg += f"  |  {npago} lançamento(s) marcado(s) como pago."
                self.page.clean()
                self.build_ui()
                self.page.update()
                self.show_snackbar(msg, self.accent_color)

            except Exception as ex:
                self.show_snackbar(f"❌ Erro ao registrar: {str(ex)}", self.error_color)

        # ══ PAINEL ESQUERDO — resumo extraído (somente leitura) ════════════════
        campos_ok = sum(1 for v in [
            dados.get('corretor_nome'), dados.get('seguradora_nome'),
            dados.get('valor_bruto'), dados.get('comissao'),
        ] if v)

        def _item_extraido(label, valor):
            cor = COR_PURPLE if valor else "#ef4444"
            txt = str(valor) if valor else "Não encontrado"
            return ft.Row([
                ft.Icon(ft.Icons.CHECK_CIRCLE if valor else ft.Icons.CANCEL,
                        color=cor, size=14),
                ft.Column([
                    ft.Text(label, size=10, color=self.text_secondary),
                    ft.Text(txt, size=12, color=self.text_primary,
                            weight=ft.FontWeight.W_500, no_wrap=False),
                ], spacing=0, expand=True),
            ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.START)

        # Trecho do texto extraído
        trecho = (texto_bruto or "")[:900].strip()
        preview_trecho = ft.Container(
            content=ft.Column([
                ft.Text("📄 Trecho do documento:", size=10,
                        weight=ft.FontWeight.BOLD, color=self.text_secondary),
                ft.Text(trecho or "(sem texto extraído)", size=10,
                        color=self.text_secondary, selectable=True, no_wrap=False),
            ], spacing=4, scroll=ft.ScrollMode.AUTO),
            bgcolor="#0a0f1e",
            padding=10,
            border_radius=8,
            border=ft.Border.all(1, "#334155"),
            height=200,
        )

        painel_esq = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.RECEIPT_LONG, color=COR_PURPLE, size=20),
                        ft.Text(" Dados Extraídos", size=14,
                                weight=ft.FontWeight.BOLD, color=self.text_primary),
                    ]),
                    bgcolor="#1a0d2e",
                    padding=ft.Padding.symmetric(horizontal=14, vertical=10),
                    border_radius=8,
                    border=ft.Border.all(1, COR_PURPLE + "50"),
                ),
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.AUTO_AWESOME, color=COR_PURPLE, size=14),
                        ft.Text(f"{campos_ok} de 4 campos identificados automaticamente",
                                size=11, color=COR_PURPLE),
                    ], spacing=6),
                    padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                ),
                ft.Divider(height=8, color="#334155"),
                ft.Text("Comissão", size=11, weight=ft.FontWeight.BOLD,
                        color=self.text_secondary),
                _item_extraido("💼 Corretor",
                               dados.get('corretor_nome_banco') or dados.get('corretor_nome')),
                _item_extraido("🏢 Seguradora",
                               dados.get('seguradora_nome_banco') or dados.get('seguradora_nome')),
                _item_extraido("💰 Valor Bruto",
                               f"R$ {dados['valor_bruto']:,.2f}" if dados.get('valor_bruto') else None),
                _item_extraido("💵 Val. Comissão",
                               f"R$ {dados['valor_comissao']:,.2f}" if dados.get('valor_comissao') else None),
                _item_extraido("📊 % Comissão",   dados.get('comissao')),
                _item_extraido("📅 Competência",  dados.get('competencia')),
                _item_extraido("🔖 SUSEP",        dados.get('susep')),
                ft.Divider(height=8, color="#334155"),
                preview_trecho,
            ], spacing=6, scroll=ft.ScrollMode.AUTO),
            bgcolor=self.surface_color,
            padding=16,
            border_radius=12,
            border=ft.Border.all(1, "#334155"),
            width=320,
            expand=False,
        )

        # ══ PAINEL DIREITO — formulário editável ═══════════════════════════════
        painel_dir = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.EDIT_NOTE, color=COR_PURPLE, size=20),
                        ft.Text(" Confirmar / Corrigir Dados da Comissão", size=14,
                                weight=ft.FontWeight.BOLD, color=self.text_primary),
                    ]),
                    bgcolor="#1a0d2e",
                    padding=ft.Padding.symmetric(horizontal=14, vertical=10),
                    border_radius=8,
                    border=ft.Border.all(1, COR_PURPLE + "50"),
                ),
                ft.Text("Campos com borda roxa foram preenchidos automaticamente pelo OCR.",
                        size=11, color=self.text_secondary, italic=True),
                ft.Divider(height=8, color="#334155"),

                ft.Text("💰 Dados da Comissão", size=12,
                        weight=ft.FontWeight.BOLD, color=COR_PURPLE),
                ft.Row([f_corretor_nome, f_seguradora], spacing=8, wrap=True),
                ft.Row([f_valor_bruto, f_valor_comissao, f_comissao], spacing=8, wrap=True),
                ft.Row([f_competencia, f_susep], spacing=8, wrap=True),
                ft.Row([f_descricao], spacing=8),

                ft.Divider(height=8, color="#334155"),
                ft.Text("🔗 Vincular ao Sistema", size=12,
                        weight=ft.FontWeight.BOLD, color=COR_PURPLE),
                ft.Row([corretor_dd, seguradora_dd], spacing=8, wrap=True),

                ft.Divider(height=8, color="#334155"),
                painel_propostas,

            ], spacing=8, scroll=ft.ScrollMode.AUTO),
            bgcolor=self.surface_color,
            padding=16,
            border_radius=12,
            border=ft.Border.all(1, "#334155"),
            expand=True,
        )

        # ══ BARRA DE TOPO ══════════════════════════════════════════════════════
        topo = ft.Container(
            content=ft.Row([
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    icon_color=self.text_primary,
                    tooltip="Voltar sem salvar",
                    on_click=lambda e: _voltar(),
                ),
                ft.Column([
                    ft.Text("Validação de Comissões Importadas", size=16,
                            weight=ft.FontWeight.BOLD, color=self.text_primary),
                    ft.Text(f"Arquivo: {file_name}", size=11,
                            color=self.text_secondary, italic=True),
                ], spacing=1),
                ft.Container(expand=True),
                ft.OutlinedButton(
                    content=ft.Text("← Cancelar", color=self.error_color),
                    style=ft.ButtonStyle(side=ft.BorderSide(1, self.error_color)),
                    on_click=lambda e: _voltar(),
                ),
                ft.FilledButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.SAVE_ALT, size=16, color="white"),
                        ft.Text("  Registrar Comissão", color="white",
                                weight=ft.FontWeight.BOLD),
                    ]),
                    style=ft.ButtonStyle(bgcolor=COR_PURPLE, padding=18),
                    height=44,
                    on_click=confirmar_salvar,
                ),
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=self.surface_color,
            padding=ft.Padding.symmetric(horizontal=20, vertical=12),
            border=ft.Border(bottom=ft.BorderSide(1, "#334155")),
        )

        # ══ TELA COMPLETA ══════════════════════════════════════════════════════
        tela = ft.Container(
            content=ft.Column([
                topo,
                ft.Container(
                    content=ft.Row([
                        painel_esq,
                        ft.Container(width=16),
                        painel_dir,
                    ], vertical_alignment=ft.CrossAxisAlignment.START, expand=True),
                    expand=True,
                    padding=ft.Padding.symmetric(horizontal=20, vertical=16),
                ),
            ], spacing=0, expand=True),
            bgcolor=self.background_color,
            expand=True,
        )

        self.page.clean()
        self.page.add(tela)
        self.page.update()

    def _importar_pdf_LEGADO(self, e):
        """Abre dialog para importar PDF — LEGADO (substituído por FilePicker)"""
        caminho_field = ft.TextField(
            label="Caminho do arquivo PDF",
            hint_text="Cole o caminho completo do arquivo aqui",
            width=500,
            multiline=False,
        )

        def processar_arquivo(e):
            caminho = caminho_field.value
            if not caminho:
                self.show_snackbar("❌ Informe o caminho do arquivo!", self.error_color)
                return
            dialog.open = False
            self.page.update()
            self.show_snackbar("⏳ Processando PDF...", self.primary_color)
            try:
                from ocr_engine import processar_pdf
                resultado = processar_pdf(caminho)
                if resultado['sucesso']:
                    self.show_snackbar(f"✅ {resultado['mensagem']}", self.accent_color)
                    self.atualizar_dashboard(None)
                else:
                    self.show_snackbar(f"❌ Erro: {resultado['mensagem']}", self.error_color)
            except Exception as ex:
                self.show_snackbar(f"❌ Erro ao processar: {str(ex)}", self.error_color)

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

    # ── Helpers de validação ──────────────────────────────────────────────────

    @staticmethod
    def _ok_cpf(valor: str) -> bool:
        import re
        return bool(re.sub(r'\D', '', valor or ''))  # basta ter dígitos

    @staticmethod
    def _ok_email(valor: str) -> bool:
        import re
        return bool(re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]{2,}$', valor or ''))

    @staticmethod
    def _ok_tel(valor: str) -> bool:
        import re
        return len(re.sub(r'\D', '', valor or '')) >= 8

    def _erro(self, campo, msg: str = "Campo obrigatório"):
        """Marca campo com borda vermelha e mensagem de erro"""
        campo.border_color = self.error_color
        campo.error_text = msg
        self.page.update()
        return False

    def _ok(self, campo):
        """Remove marcação de erro do campo"""
        campo.border_color = None
        campo.error_text = None
        return True

    def _validar(self, regras: list) -> bool:
        """
        Valida uma lista de regras: [(campo, condicao, msg), ...]
        Retorna True se tudo válido.
        """
        ok = True
        for item in regras:
            campo, condicao, msg = item
            if not condicao:
                self._erro(campo, msg)
                ok = False
            else:
                self._ok(campo)
        self.page.update()
        return ok


class VendedorApp:
    """Interface restrita para corretor/vendedor"""

    # Compartilha paleta com CorretoraApp
    primary_color    = "#6366f1"
    secondary_color  = "#8b5cf6"
    background_color = "#0f172a"
    surface_color    = "#1e293b"
    accent_color     = "#10b981"
    error_color      = "#ef4444"
    text_primary     = "#f8fafc"
    text_secondary   = "#94a3b8"

    def __init__(self, page: ft.Page, usuario_logado):
        self.page = page
        self.usuario_logado = usuario_logado
        self.corretor_id = usuario_logado.corretor_id  # filtra tudo por este ID

        self.page.title = f"Painel do Vendedor — {usuario_logado.nome_completo}"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 0
        self.page.window_width  = 1280
        self.page.window_height = 860

        engine = criar_banco()
        self.session = obter_sessao(engine)

        self.build_ui()

    # ── show_snackbar (igual à CorretoraApp) ──────────────────────────────────
    def show_snackbar(self, message, color):
        sb = ft.SnackBar(content=ft.Text(message, color=self.text_primary),
                         bgcolor=color, action="OK")
        self.page.snack_bar = sb
        sb.open = True
        self.page.update()

    def _reload(self):
        self.page.clean()
        self.build_ui()
        self.page.update()

    # ── Helpers validação (iguais a CorretoraApp) ─────────────────────────────
    @staticmethod
    def _ok_tel(v):
        import re; return len(re.sub(r'\D', '', v or '')) >= 8
    @staticmethod
    def _ok_email(v):
        import re; return bool(re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]{2,}$', v or ''))

    # ── Layout principal ──────────────────────────────────────────────────────
    def build_ui(self):
        self.page.add(ft.Container(
            content=ft.Column([self._build_header(), self._build_tabs()],
                              spacing=0, expand=True),
            bgcolor=self.background_color, expand=True,
        ))

    def _build_header(self):
        def logout(e):
            self.page.clean()
            from login_system import mostrar_tela_login
            mostrar_tela_login(self.page, lambda u: (
                self.page.clean().__class__ or True,
                VendedorApp(self.page, u) if u.tipo == 'corretor' else CorretoraApp(self.page, u)
            ))

        # Buscar nome do corretor vinculado
        corretor_nome = ""
        if self.corretor_id:
            c = self.session.query(Corretor).get(self.corretor_id)
            if c:
                corretor_nome = f" — {c.nome}"

        return ft.Container(
            content=ft.Row([
                ft.Text("🏷️", size=28),
                ft.Column([
                    ft.Text(f"Painel do Vendedor{corretor_nome}", size=18,
                            weight=ft.FontWeight.BOLD, color=self.text_primary),
                    ft.Text("Acesso restrito · Seus dados e comissões", size=12,
                            color=self.text_secondary),
                ], spacing=1),
                ft.Container(expand=True),
                ft.Column([
                    ft.Text(self.usuario_logado.nome_completo, size=13,
                            weight=ft.FontWeight.BOLD, color=self.text_primary),
                    ft.Text("👤 VENDEDOR", size=11, color="#6366f1"),
                ], spacing=1, horizontal_alignment=ft.CrossAxisAlignment.END),
                ft.Container(width=16),
                ft.OutlinedButton(content=ft.Text("🚪 Sair", size=13),
                                  style=ft.ButtonStyle(color=self.error_color),
                                  on_click=logout),
            ], alignment=ft.MainAxisAlignment.START),
            bgcolor=self.surface_color, padding=18,
            border=ft.Border.only(bottom=ft.BorderSide(1, "#334155")),
        )

    def _build_tabs(self):
        return ft.Container(
            content=ft.Column([
                ft.TabBar(tabs=[
                    ft.Tab(label="📊 Dashboard"),
                    ft.Tab(label="🎯 Meu CRM"),
                    ft.Tab(label="💳 Valor a Receber"),
                    ft.Tab(label="💰 Extrato de Comissões"),
                ]),
                ft.TabBarView(controls=[
                    self._build_dashboard_vendedor(),
                    self._build_crm_vendedor(),
                    self._build_valor_receber(),
                    self._build_extrato_comissoes(),
                ], expand=True),
            ], spacing=0, expand=True),
            expand=True,
        )

    # ── Dashboard ──────────────────────────────────────────────────────────────
    def _build_dashboard_vendedor(self):
        from database import Lead, Lancamento as _Lanc
        # KPIs filtrados por corretor
        propostas = (self.session.query(Proposta)
                     .filter(Proposta.corretor_id == self.corretor_id).all()
                     if self.corretor_id else [])
        lans_pendentes = []
        lans_pagos     = []
        for p in propostas:
            for l in p.lancamentos:
                (lans_pagos if l.status_pago else lans_pendentes).append(l)

        leads_ativos = (self.session.query(Lead)
                        .filter(Lead.corretor_id == self.corretor_id,
                                Lead.status.notin_(['GANHO','PERDIDO'])).count()
                        if self.corretor_id else 0)

        total_vendido = sum(p.valor_bruto for p in propostas)
        total_receber = sum(l.valor_esperado for l in lans_pendentes)
        total_recebido = sum(l.valor_esperado for l in lans_pagos)

        def _card(titulo, valor, cor, icone):
            return ft.Container(
                content=ft.Column([
                    ft.Icon(icone, color=cor, size=28),
                    ft.Text(valor, size=22, weight=ft.FontWeight.BOLD, color=cor),
                    ft.Text(titulo, size=12, color=self.text_secondary),
                ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=self.surface_color, padding=20, border_radius=12,
                border=ft.Border.all(1, cor + "40"), expand=True,
            )

        # Últimas propostas
        ultimas = propostas[:8]
        rows = []
        for p in ultimas:
            seg = p.seguradora.nome if p.seguradora else "—"
            pendente = sum(l.valor_esperado for l in p.lancamentos if not l.status_pago)
            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(p.cliente_nome, size=12)),
                ft.DataCell(ft.Text(seg, size=12)),
                ft.DataCell(ft.Text(p.data_venda.strftime('%d/%m/%Y') if p.data_venda else "—", size=12)),
                ft.DataCell(ft.Text(f"R$ {p.valor_bruto:,.2f}", size=12,
                                    color=self.primary_color, weight=ft.FontWeight.BOLD)),
                ft.DataCell(ft.Text(f"R$ {pendente:,.2f}", size=12,
                                    color="#f59e0b" if pendente > 0 else self.text_secondary)),
            ]))

        tabela = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Cliente", size=11, color=self.text_secondary)),
                ft.DataColumn(ft.Text("Seguradora", size=11, color=self.text_secondary)),
                ft.DataColumn(ft.Text("Data Venda", size=11, color=self.text_secondary)),
                ft.DataColumn(ft.Text("Valor Bruto", size=11, color=self.text_secondary)),
                ft.DataColumn(ft.Text("Pendente", size=11, color=self.text_secondary)),
            ],
            rows=rows,
            border=ft.border.all(1, "#334155"),
            border_radius=8,
            vertical_lines=ft.border.BorderSide(1, "#334155"),
            heading_row_color="#1e293b",
        ) if rows else ft.Text("Nenhuma proposta ainda.", color=self.text_secondary, italic=True)

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    _card("Propostas", str(len(propostas)), self.primary_color, ft.Icons.DESCRIPTION),
                    _card("Leads Ativos", str(leads_ativos), self.accent_color, ft.Icons.PEOPLE),
                    _card("Total Vendido", f"R$ {total_vendido:,.0f}", "#8b5cf6", ft.Icons.TRENDING_UP),
                    _card("A Receber", f"R$ {total_receber:,.0f}", "#f59e0b", ft.Icons.SAVINGS),
                    _card("Recebido", f"R$ {total_recebido:,.0f}", self.accent_color, ft.Icons.CHECK_CIRCLE),
                ], spacing=12),
                ft.Divider(height=20, color="#334155"),
                ft.Text("📄 Minhas Propostas Recentes", size=14,
                        weight=ft.FontWeight.BOLD, color=self.text_primary),
                ft.Container(content=tabela, padding=4),
            ], spacing=16, scroll=ft.ScrollMode.AUTO),
            padding=24, expand=True,
        )

    # ── CRM filtrado por corretor ──────────────────────────────────────────────
    def _build_crm_vendedor(self):
        from database import Lead, Interacao
        STATUS_COLORS = {
            'NOVO':'#3b82f6','CONTATO':'#8b5cf6','QUALIFICADO':'#f59e0b',
            'PROPOSTA':'#10b981','GANHO':'#22c55e','PERDIDO':'#ef4444',
        }
        filtro = [None]

        def _reload_crm():
            self.page.clean(); self.build_ui(); self.page.update()

        def _fechar(dlg):
            dlg.open = False; self.page.update()

        def _leads():
            q = self.session.query(Lead)
            if self.corretor_id:
                q = q.filter(Lead.corretor_id == self.corretor_id)
            if filtro[0]:
                q = q.filter(Lead.status == filtro[0])
            return q.order_by(Lead.data_criacao.desc()).all()

        def adicionar_lead(e):
            f_nome  = ft.TextField(label="Nome *", width=300, bgcolor=self.surface_color)
            f_tel   = ft.TextField(label="Telefone *", width=200, bgcolor=self.surface_color)
            f_email = ft.TextField(label="E-mail", width=260, bgcolor=self.surface_color)
            f_prod  = ft.TextField(label="Produto", width=280, bgcolor=self.surface_color)
            f_obs   = ft.TextField(label="Observações", width=460, multiline=True, min_lines=2,
                                   bgcolor=self.surface_color)
            f_origem = ft.Dropdown(label="Origem", width=200, bgcolor=self.surface_color,
                options=[ft.dropdown.Option(o) for o in
                         ["Google Ads","Facebook","Instagram","Indicação","Site","Telefone","WhatsApp","Outro"]])

            def salvar(e):
                if not f_nome.value.strip() or not self._ok_tel(f_tel.value):
                    self.show_snackbar("❌ Nome e telefone são obrigatórios!", self.error_color)
                    return
                try:
                    self.session.add(Lead(
                        nome=f_nome.value.strip(), telefone=f_tel.value.strip(),
                        email=f_email.value.strip() or None,
                        produto_interesse=f_prod.value.strip() or None,
                        origem=f_origem.value or None,
                        corretor_id=self.corretor_id, status='NOVO',
                        observacoes=f_obs.value.strip() or None,
                    ))
                    self.session.commit()
                    self.show_snackbar(f"✅ Lead {f_nome.value.strip()} adicionado!", self.accent_color)
                    _fechar(dlg); _reload_crm()
                except Exception as ex:
                    self.show_snackbar(f"❌ {ex}", self.error_color)

            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Row([ft.Icon(ft.Icons.PERSON_ADD_ALT, color=self.primary_color),
                               ft.Text("  Novo Lead", weight=ft.FontWeight.BOLD)]),
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([f_nome, f_tel], spacing=8, wrap=True),
                        ft.Row([f_email, f_origem], spacing=8, wrap=True),
                        f_prod, f_obs,
                    ], spacing=8, scroll=ft.ScrollMode.AUTO),
                    width=520, height=340,
                ),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda e: _fechar(dlg)),
                    ft.FilledButton("Salvar", on_click=salvar,
                                    style=ft.ButtonStyle(bgcolor=self.primary_color)),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            self.page.dialog = dlg; dlg.open = True; self.page.update()

        def registrar_contato(lead):
            f_tipo = ft.Dropdown(label="Tipo *", width=200, value="LIGAÇÃO",
                bgcolor=self.surface_color,
                options=[ft.dropdown.Option(t) for t in
                         ["LIGAÇÃO","WHATSAPP","EMAIL","REUNIÃO","PROPOSTA","OUTRO"]])
            f_desc    = ft.TextField(label="Descrição *", width=440,
                                     multiline=True, min_lines=3, bgcolor=self.surface_color)
            f_followup = ft.TextField(label="Follow-up (dd/mm/aaaa)", width=200,
                                      bgcolor=self.surface_color)
            f_status  = ft.Dropdown(label="Novo Status", width=200, value=lead.status,
                bgcolor=self.surface_color,
                options=[ft.dropdown.Option(s) for s in
                         ['NOVO','CONTATO','QUALIFICADO','PROPOSTA','GANHO','PERDIDO']])

            def salvar(e):
                if not f_desc.value.strip():
                    self.show_snackbar("❌ Descrição obrigatória!", self.error_color); return
                try:
                    followup = None
                    if f_followup.value.strip():
                        from datetime import datetime as _dt
                        followup = _dt.strptime(f_followup.value.strip(), '%d/%m/%Y')
                    uid = self.usuario_logado.id
                    self.session.add(Interacao(
                        lead_id=lead.id, usuario_id=uid, tipo=f_tipo.value,
                        descricao=f_desc.value.strip(), proximo_followup=followup,
                    ))
                    lead.data_ultima_interacao = datetime.now()
                    if f_status.value:
                        lead.status = f_status.value
                    self.session.commit()
                    self.show_snackbar("✅ Contato registrado!", self.accent_color)
                    _fechar(dlg); _reload_crm()
                except Exception as ex:
                    self.show_snackbar(f"❌ {ex}", self.error_color)

            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Row([ft.Icon(ft.Icons.CHAT, color=self.primary_color),
                               ft.Text(f"  Registrar Contato — {lead.nome}",
                                       weight=ft.FontWeight.BOLD)]),
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([f_tipo, f_followup, f_status], spacing=8, wrap=True),
                        f_desc,
                    ], spacing=8),
                    width=540, height=280,
                ),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda e: _fechar(dlg)),
                    ft.FilledButton("Salvar", on_click=salvar,
                                    style=ft.ButtonStyle(bgcolor=self.primary_color)),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            self.page.dialog = dlg; dlg.open = True; self.page.update()

        leads = _leads()

        def _card_lead(lead):
            cor = STATUS_COLORS.get(lead.status, '#6b7280')
            followup_alerta = ""
            if lead.data_ultima_interacao:
                dias = (datetime.now() - lead.data_ultima_interacao).days
                if dias > 3 and lead.status not in ('GANHO','PERDIDO'):
                    followup_alerta = f"⚠️ {dias}d sem contato"

            return ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Container(width=4, height=40, bgcolor=cor, border_radius=2),
                        ft.Column([
                            ft.Text(lead.nome, size=13, weight=ft.FontWeight.BOLD,
                                    color=self.text_primary),
                            ft.Text(lead.telefone, size=11, color=self.text_secondary),
                        ], spacing=1, expand=True),
                        ft.Container(
                            content=ft.Text(lead.status, size=10, color="white",
                                            weight=ft.FontWeight.BOLD),
                            bgcolor=cor, padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                            border_radius=20,
                        ),
                    ], spacing=8),
                    ft.Row([
                        ft.Text(lead.produto_interesse or "—", size=11, color=self.text_secondary,
                                expand=True),
                        ft.Text(followup_alerta, size=11, color="#f59e0b"),
                    ]) if (lead.produto_interesse or followup_alerta) else ft.Container(),
                    ft.Row([
                        ft.TextButton(
                            content=ft.Row([ft.Icon(ft.Icons.CHAT, size=14),
                                            ft.Text(" Registrar Contato", size=11)]),
                            style=ft.ButtonStyle(color=self.primary_color),
                            on_click=lambda e, l=lead: registrar_contato(l),
                        ),
                    ]),
                ], spacing=4),
                bgcolor=self.surface_color, padding=12, border_radius=10,
                border=ft.Border.all(1, "#334155"),
                margin=ft.Margin(0, 0, 0, 4),
            )

        filtro_row = ft.Row([
            ft.TextButton(
                content=ft.Text("Todos", size=12,
                                color=self.text_primary if not filtro[0] else self.text_secondary),
                on_click=lambda e: (filtro.__setitem__(0, None), _reload_crm()),
            ),
            *[ft.TextButton(
                content=ft.Text(s, size=12,
                                color=STATUS_COLORS[s] if filtro[0] == s else self.text_secondary),
                on_click=lambda e, st=s: (filtro.__setitem__(0, st), _reload_crm()),
            ) for s in ['NOVO','CONTATO','QUALIFICADO','PROPOSTA','GANHO','PERDIDO']],
            ft.Container(expand=True),
            ft.FilledButton(
                content=ft.Row([ft.Icon(ft.Icons.ADD, size=14, color="white"),
                                ft.Text(" Novo Lead", color="white")]),
                style=ft.ButtonStyle(bgcolor=self.primary_color),
                on_click=adicionar_lead,
            ),
        ], wrap=True)

        return ft.Container(
            content=ft.Column([
                filtro_row,
                ft.Divider(height=8, color="#334155"),
                ft.Column([_card_lead(l) for l in leads], spacing=4,
                          scroll=ft.ScrollMode.AUTO) if leads
                else ft.Text("Nenhum lead no momento.", color=self.text_secondary, italic=True),
            ], spacing=8, scroll=ft.ScrollMode.AUTO),
            padding=20, expand=True,
        )

    # ── Valor a Receber ────────────────────────────────────────────────────────
    def _build_valor_receber(self):
        propostas = (self.session.query(Proposta)
                     .filter(Proposta.corretor_id == self.corretor_id).all()
                     if self.corretor_id else [])

        rows = []
        total_pendente = 0.0
        for p in propostas:
            for lan in sorted(p.lancamentos, key=lambda x: x.data_vencimento):
                if not lan.status_pago:
                    total_pendente += lan.valor_esperado
                    venc = lan.data_vencimento
                    hoje = datetime.now().date()
                    atrasado = venc < hoje
                    rows.append(ft.DataRow(
                        color=ft.colors.with_opacity(0.04, "#ef4444") if atrasado else None,
                        cells=[
                            ft.DataCell(ft.Text(p.cliente_nome, size=12)),
                            ft.DataCell(ft.Text(
                                p.seguradora.nome if p.seguradora else "—", size=12)),
                            ft.DataCell(ft.Text(
                                venc.strftime('%d/%m/%Y'), size=12,
                                color=self.error_color if atrasado else self.text_primary)),
                            ft.DataCell(ft.Text(
                                f"R$ {lan.valor_esperado:,.2f}", size=12,
                                weight=ft.FontWeight.BOLD, color=self.primary_color)),
                            ft.DataCell(ft.Container(
                                content=ft.Text("ATRASADO" if atrasado else "PENDENTE", size=10),
                                bgcolor=self.error_color if atrasado else "#334155",
                                padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                                border_radius=20,
                            )),
                        ],
                    ))

        tabela = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Cliente", size=11, color=self.text_secondary)),
                ft.DataColumn(ft.Text("Seguradora", size=11, color=self.text_secondary)),
                ft.DataColumn(ft.Text("Vencimento", size=11, color=self.text_secondary)),
                ft.DataColumn(ft.Text("Valor", size=11, color=self.text_secondary)),
                ft.DataColumn(ft.Text("Status", size=11, color=self.text_secondary)),
            ],
            rows=rows or [ft.DataRow(cells=[
                ft.DataCell(ft.Text("Nenhum lançamento pendente", color=self.text_secondary)),
                ft.DataCell(ft.Text("")), ft.DataCell(ft.Text("")),
                ft.DataCell(ft.Text("")), ft.DataCell(ft.Text("")),
            ])],
            border=ft.border.all(1, "#334155"), border_radius=8,
            vertical_lines=ft.border.BorderSide(1, "#334155"),
            heading_row_color="#1e293b",
        )

        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.SAVINGS, color="#f59e0b", size=24),
                        ft.Column([
                            ft.Text("Total a Receber", size=13, color=self.text_secondary),
                            ft.Text(f"R$ {total_pendente:,.2f}", size=24,
                                    weight=ft.FontWeight.BOLD, color="#f59e0b"),
                        ], spacing=2),
                    ], spacing=16),
                    bgcolor=self.surface_color, padding=20, border_radius=10,
                    border=ft.Border.all(1, "#f59e0b40"),
                ),
                ft.Text("💳 Lançamentos Pendentes", size=14,
                        weight=ft.FontWeight.BOLD, color=self.text_primary),
                tabela,
            ], spacing=16, scroll=ft.ScrollMode.AUTO),
            padding=24, expand=True,
        )

    # ── Extrato de Comissões ───────────────────────────────────────────────────
    def _build_extrato_comissoes(self):
        from modulo_financeiro import TransacaoFinanceira
        from sqlalchemy import func

        # Buscar transações de comissão do corretor (por nome no campo descrição)
        corretor_obj = (self.session.query(Corretor).get(self.corretor_id)
                        if self.corretor_id else None)
        corretor_nome = corretor_obj.nome if corretor_obj else ""

        txs = []
        if corretor_nome:
            txs = (self.session.query(TransacaoFinanceira)
                   .filter(TransacaoFinanceira.tipo == 'RECEITA',
                           TransacaoFinanceira.descricao.ilike(f'%{corretor_nome}%'))
                   .order_by(TransacaoFinanceira.data.desc())
                   .all())

        # Propostas pagas (lançamentos status_pago=True)
        propostas = (self.session.query(Proposta)
                     .filter(Proposta.corretor_id == self.corretor_id).all()
                     if self.corretor_id else [])
        total_recebido_lans = sum(
            l.valor_esperado for p in propostas for l in p.lancamentos if l.status_pago
        )
        total_pendente_lans = sum(
            l.valor_esperado for p in propostas for l in p.lancamentos if not l.status_pago
        )

        rows_tx = []
        for tx in txs:
            rows_tx.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(tx.data.strftime('%d/%m/%Y') if tx.data else "—", size=12)),
                ft.DataCell(ft.Text(tx.descricao[:60], size=11, color=self.text_secondary)),
                ft.DataCell(ft.Text(f"R$ {tx.valor:,.2f}", size=12,
                                    weight=ft.FontWeight.BOLD, color=self.accent_color)),
            ]))

        tabela_tx = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Data", size=11, color=self.text_secondary)),
                ft.DataColumn(ft.Text("Descrição", size=11, color=self.text_secondary)),
                ft.DataColumn(ft.Text("Valor", size=11, color=self.text_secondary)),
            ],
            rows=rows_tx or [ft.DataRow(cells=[
                ft.DataCell(ft.Text("Nenhuma comissão registrada ainda.",
                                    color=self.text_secondary)),
                ft.DataCell(ft.Text("")), ft.DataCell(ft.Text("")),
            ])],
            border=ft.border.all(1, "#334155"), border_radius=8,
            vertical_lines=ft.border.BorderSide(1, "#334155"),
            heading_row_color="#1e293b",
        )

        def _kpi(titulo, valor, cor, icone):
            return ft.Container(
                content=ft.Column([
                    ft.Icon(icone, color=cor, size=24),
                    ft.Text(f"R$ {valor:,.2f}", size=20, weight=ft.FontWeight.BOLD, color=cor),
                    ft.Text(titulo, size=11, color=self.text_secondary),
                ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=self.surface_color, padding=18, border_radius=10,
                border=ft.Border.all(1, cor + "40"), expand=True,
            )

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    _kpi("Total Recebido (lançamentos)", total_recebido_lans,
                         self.accent_color, ft.Icons.CHECK_CIRCLE),
                    _kpi("Total Pendente", total_pendente_lans,
                         "#f59e0b", ft.Icons.SCHEDULE),
                    _kpi("Comissões Importadas", sum(t.valor for t in txs),
                         self.primary_color, ft.Icons.RECEIPT_LONG),
                ], spacing=12),
                ft.Divider(height=20, color="#334155"),
                ft.Text("💰 Histórico de Comissões Importadas", size=14,
                        weight=ft.FontWeight.BOLD, color=self.text_primary),
                tabela_tx,
            ], spacing=16, scroll=ft.ScrollMode.AUTO),
            padding=24, expand=True,
        )


def main(page: ft.Page):
    """Função principal"""
    page.title = "Sistema Financeiro - Corretora"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0

    usuario_logado = None

    def on_login_success(usuario):
        nonlocal usuario_logado
        usuario_logado = usuario
        page.clean()
        # Roteamento por tipo de usuário
        if usuario.tipo == 'corretor' and usuario.corretor_id:
            VendedorApp(page, usuario)
        else:
            CorretoraApp(page, usuario)
        page.update()

    from login_system import mostrar_tela_login
    mostrar_tela_login(page, on_login_success)


if __name__ == "__main__":
    ft.run(main)
