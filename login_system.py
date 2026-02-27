"""
Sistema de Login e Autenticação
"""

import flet as ft
from database import criar_banco, obter_sessao, Usuario
from datetime import datetime


class LoginScreen:
    """Tela de Login do Sistema"""

    def __init__(self, page: ft.Page, on_login_success):
        self.page = page
        self.on_login_success = on_login_success

        # Cores
        self.primary_color = "#6366f1"
        self.background_color = "#0f172a"
        self.surface_color = "#1e293b"
        self.text_primary = "#f8fafc"
        self.text_secondary = "#94a3b8"
        self.error_color = "#ef4444"
        self.accent_color = "#10b981"

        # Banco
        engine = criar_banco()
        self.session = obter_sessao(engine)

        # Criar usuário admin padrão se não existir
        self.criar_usuario_admin_padrao()

    def criar_usuario_admin_padrao(self):
        """Cria usuário admin padrão: admin/admin123"""
        admin = self.session.query(Usuario).filter_by(username='admin').first()

        if not admin:
            admin = Usuario(
                username='admin',
                senha_hash=Usuario.criar_hash_senha('admin123'),
                nome_completo='Administrador',
                email='admin@corretora.com',
                tipo='admin',
                ativo=True
            )
            self.session.add(admin)
            self.session.commit()
            print("[LOGIN] Usuário admin criado: admin/admin123")

    def build(self):
        """Constrói a tela de login"""
        username_field = ft.TextField(
            label="👤 Usuário",
            width=300,
            bgcolor=self.surface_color,
            border_color=self.primary_color,
            color=self.text_primary,
        )

        senha_field = ft.TextField(
            label="🔒 Senha",
            password=True,
            can_reveal_password=True,
            width=300,
            bgcolor=self.surface_color,
            border_color=self.primary_color,
            color=self.text_primary,
        )

        error_text = ft.Text(
            "",
            color=self.error_color,
            size=14,
            visible=False,
        )

        def fazer_login(e):
            """Processa o login"""
            username = username_field.value
            senha = senha_field.value

            if not username or not senha:
                error_text.value = "Preencha usuário e senha"
                error_text.visible = True
                self.page.update()
                return

            # Buscar usuário
            usuario = self.session.query(Usuario).filter_by(username=username, ativo=True).first()

            if not usuario or not usuario.verificar_senha(senha):
                error_text.value = "Usuário ou senha incorretos"
                error_text.visible = True
                username_field.value = ""
                senha_field.value = ""
                self.page.update()
                return

            # Login bem-sucedido
            usuario.ultimo_acesso = datetime.now()
            self.session.commit()

            # Chamar callback de sucesso
            self.on_login_success(usuario)

        login_button = ft.FilledButton(
            content=ft.Text("Entrar", size=16, weight=ft.FontWeight.BOLD),
            width=300,
            height=50,
            style=ft.ButtonStyle(
                bgcolor=self.primary_color,
                color=self.text_primary,
            ),
            on_click=fazer_login,
        )

        return ft.Container(
            content=ft.Column(
                controls=[
                    # Logo/Título
                    ft.Container(
                        content=ft.Column([
                            ft.Text("🏢", size=64),
                            ft.Text(
                                "Sistema Financeiro",
                                size=32,
                                weight=ft.FontWeight.BOLD,
                                color=self.text_primary,
                            ),
                            ft.Text(
                                "Corretora de Seguros",
                                size=18,
                                color=self.text_secondary,
                            ),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                        padding=ft.padding.only(bottom=40),
                    ),

                    # Card de Login
                    ft.Container(
                        content=ft.Column([
                            ft.Text(
                                "Acessar Sistema",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=self.text_primary,
                            ),
                            ft.Container(height=20),
                            username_field,
                            ft.Container(height=10),
                            senha_field,
                            ft.Container(height=10),
                            error_text,
                            ft.Container(height=20),
                            login_button,
                            ft.Container(height=20),
                            ft.Text(
                                "Usuário padrão: admin / Senha: admin123",
                                size=12,
                                color=self.text_secondary,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        bgcolor=self.surface_color,
                        padding=40,
                        border_radius=15,
                        border=ft.Border.all(1, "#334155"),
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            bgcolor=self.background_color,
            expand=True,
            padding=20,
        )


def mostrar_tela_login(page: ft.Page, on_login_success):
    """Mostra a tela de login"""
    page.title = "Login - Sistema Financeiro"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.spacing = 0

    login_screen = LoginScreen(page, on_login_success)
    page.add(login_screen.build())
    page.update()
