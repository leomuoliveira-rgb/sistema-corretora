"""
Sistema de Controle de Parcelas e Notificações
Gerencia vencimentos, quitações e envio de emails automáticos
"""

from database import Base, criar_banco, obter_sessao, Lancamento, Proposta, Corretor
from sqlalchemy import Column, Integer, String, Float, Date, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict


class Parcela(Base):
    """Tabela de parcelas de comissões"""
    __tablename__ = 'parcelas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    lancamento_id = Column(Integer, ForeignKey('lancamentos.id'), nullable=False)
    proposta_id = Column(Integer, ForeignKey('propostas.id'), nullable=False)
    corretor_id = Column(Integer, ForeignKey('corretores.id'), nullable=False)

    numero_parcela = Column(Integer, nullable=False)  # 1, 2, 3...
    valor = Column(Float, nullable=False)

    data_vencimento = Column(Date, nullable=False)
    data_quitacao = Column(Date, nullable=True)

    status = Column(String(20), default='PENDENTE')  # PENDENTE, QUITADA, VENCIDA, NOTIFICADA

    email_enviado = Column(Boolean, default=False)
    data_email = Column(DateTime, nullable=True)

    observacoes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relacionamentos
    lancamento = relationship('Lancamento', back_populates='parcelas')
    proposta = relationship('Proposta')
    corretor = relationship('Corretor')

    def __repr__(self):
        return f"<Parcela(id={self.id}, num={self.numero_parcela}, valor={self.valor}, venc={self.data_vencimento})>"


# Adicionar relacionamento em Lancamento
Lancamento.parcelas = relationship('Parcela', back_populates='lancamento', cascade='all, delete-orphan')


class ConfiguracaoEmail(Base):
    """Configurações de email para notificações"""
    __tablename__ = 'config_email'

    id = Column(Integer, primary_key=True, autoincrement=True)

    smtp_server = Column(String(100), default='smtp.gmail.com')
    smtp_port = Column(Integer, default=587)

    email_remetente = Column(String(200), nullable=False)
    senha_remetente = Column(String(200), nullable=False)  # Usar senha de aplicativo

    ativo = Column(Boolean, default=True)

    assunto_padrao = Column(String(200), default='Alerta: Parcela de Comissão Vencida')

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<ConfigEmail(servidor={self.smtp_server}, email={self.email_remetente})>"


class GerenciadorParcelas:
    """Classe para gerenciar parcelas e notificações"""

    def __init__(self, session=None):
        if session is None:
            engine = criar_banco()
            self.session = obter_sessao(engine)
            self.own_session = True
        else:
            self.session = session
            self.own_session = False

    def fechar(self):
        """Fecha a sessão se foi criada aqui"""
        if self.own_session:
            self.session.close()

    def criar_parcelas_automaticas(self, lancamento_id: int, proposta_id: int, corretor_id: int,
                                   valor_total: float, data_primeira_quitacao: datetime.date):
        """
        Cria parcelas automáticas quando a primeira parcela é quitada

        Regra:
        - Parcela 1: 30 dias após quitação da proposta
        - Parcela 2: 60 dias após quitação da proposta
        - Parcela 3: 90 dias após quitação da proposta (se necessário)

        Args:
            lancamento_id: ID do lançamento
            proposta_id: ID da proposta
            corretor_id: ID do corretor
            valor_total: Valor total a ser dividido
            data_primeira_quitacao: Data da quitação da primeira parcela da proposta

        Returns:
            List[Parcela]: Lista de parcelas criadas
        """
        print(f"[PARCELAS] Criando parcelas automáticas para lançamento {lancamento_id}")

        # Verificar se já existem parcelas para este lançamento
        parcelas_existentes = self.session.query(Parcela).filter_by(lancamento_id=lancamento_id).all()
        if parcelas_existentes:
            print(f"[PARCELAS] Já existem {len(parcelas_existentes)} parcelas para este lançamento")
            return parcelas_existentes

        # Dividir valor em 3 parcelas
        valor_parcela = valor_total / 3
        parcelas = []

        for i in range(1, 4):
            dias_vencimento = i * 30  # 30, 60, 90 dias
            data_vencimento = data_primeira_quitacao + timedelta(days=dias_vencimento)

            parcela = Parcela(
                lancamento_id=lancamento_id,
                proposta_id=proposta_id,
                corretor_id=corretor_id,
                numero_parcela=i,
                valor=valor_parcela,
                data_vencimento=data_vencimento,
                status='PENDENTE'
            )

            self.session.add(parcela)
            parcelas.append(parcela)
            print(f"[PARCELAS] Criada parcela {i}/3: R$ {valor_parcela:.2f} - Venc: {data_vencimento}")

        self.session.commit()
        print(f"[PARCELAS] {len(parcelas)} parcelas criadas com sucesso!")

        return parcelas

    def quitar_parcela(self, parcela_id: int, data_quitacao: datetime.date = None):
        """
        Marca uma parcela como quitada

        Args:
            parcela_id: ID da parcela
            data_quitacao: Data da quitação (padrão: hoje)
        """
        parcela = self.session.query(Parcela).get(parcela_id)

        if not parcela:
            print(f"[ERRO] Parcela {parcela_id} não encontrada")
            return False

        if data_quitacao is None:
            data_quitacao = datetime.now().date()

        parcela.data_quitacao = data_quitacao
        parcela.status = 'QUITADA'
        parcela.updated_at = datetime.now()

        self.session.commit()
        print(f"[PARCELAS] Parcela {parcela_id} quitada em {data_quitacao}")

        return True

    def verificar_parcelas_vencidas(self) -> List[Parcela]:
        """
        Verifica todas as parcelas vencidas e não quitadas

        Returns:
            List[Parcela]: Lista de parcelas vencidas
        """
        hoje = datetime.now().date()

        parcelas_vencidas = self.session.query(Parcela).filter(
            Parcela.status == 'PENDENTE',
            Parcela.data_vencimento < hoje
        ).all()

        # Atualizar status para VENCIDA
        for parcela in parcelas_vencidas:
            if parcela.status == 'PENDENTE':
                parcela.status = 'VENCIDA'

        self.session.commit()

        print(f"[PARCELAS] {len(parcelas_vencidas)} parcelas vencidas encontradas")
        return parcelas_vencidas

    def enviar_email_vencimento(self, parcela_id: int) -> bool:
        """
        Envia email ao corretor sobre parcela vencida

        Args:
            parcela_id: ID da parcela

        Returns:
            bool: True se enviou com sucesso
        """
        parcela = self.session.query(Parcela).get(parcela_id)

        if not parcela:
            print(f"[EMAIL] Parcela {parcela_id} não encontrada")
            return False

        # Verificar se já enviou email
        if parcela.email_enviado:
            print(f"[EMAIL] Email já foi enviado para parcela {parcela_id}")
            return False

        # Buscar configuração de email
        config = self.session.query(ConfiguracaoEmail).filter_by(ativo=True).first()

        if not config:
            print("[EMAIL] Configuração de email não encontrada")
            return False

        # Preparar dados do email
        corretor = parcela.corretor
        proposta = parcela.proposta

        if not corretor.email:
            print(f"[EMAIL] Corretor {corretor.nome} não possui email cadastrado")
            return False

        # Montar corpo do email
        corpo_email = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #ef4444;">⚠️ Alerta: Parcela de Comissão Vencida</h2>

            <p>Olá <strong>{corretor.nome}</strong>,</p>

            <p>Informamos que você possui uma parcela de comissão vencida:</p>

            <div style="background-color: #f3f4f6; padding: 15px; border-radius: 5px; margin: 15px 0;">
                <p><strong>📄 Proposta:</strong> {proposta.cliente_nome}</p>
                <p><strong>💰 Valor:</strong> R$ {parcela.valor:,.2f}</p>
                <p><strong>📅 Data de Vencimento:</strong> {parcela.data_vencimento.strftime('%d/%m/%Y')}</p>
                <p><strong>🔢 Parcela:</strong> {parcela.numero_parcela}ª parcela</p>
                <p><strong>⏰ Dias em atraso:</strong> {(datetime.now().date() - parcela.data_vencimento).days} dias</p>
            </div>

            <p>Por favor, entre em contato com o financeiro para regularizar a situação.</p>

            <hr style="margin: 20px 0;">
            <p style="color: #6b7280; font-size: 12px;">
                Este é um email automático enviado pelo Sistema de Gestão de Corretora.
            </p>
        </body>
        </html>
        """

        try:
            # Criar mensagem
            msg = MIMEMultipart('alternative')
            msg['Subject'] = config.assunto_padrao
            msg['From'] = config.email_remetente
            msg['To'] = corretor.email

            # Anexar HTML
            html_part = MIMEText(corpo_email, 'html')
            msg.attach(html_part)

            # Conectar ao servidor SMTP
            print(f"[EMAIL] Conectando ao servidor {config.smtp_server}:{config.smtp_port}")
            server = smtplib.SMTP(config.smtp_server, config.smtp_port)
            server.starttls()
            server.login(config.email_remetente, config.senha_remetente)

            # Enviar email
            server.send_message(msg)
            server.quit()

            # Atualizar parcela
            parcela.email_enviado = True
            parcela.data_email = datetime.now()
            parcela.status = 'NOTIFICADA'
            self.session.commit()

            print(f"[EMAIL] ✅ Email enviado com sucesso para {corretor.email}")
            return True

        except Exception as e:
            print(f"[EMAIL] ❌ Erro ao enviar email: {e}")
            return False

    def notificar_parcelas_vencidas(self) -> Dict:
        """
        Verifica e notifica todas as parcelas vencidas

        Returns:
            Dict com estatísticas de envio
        """
        parcelas_vencidas = self.verificar_parcelas_vencidas()

        total = len(parcelas_vencidas)
        enviados = 0
        erros = 0

        for parcela in parcelas_vencidas:
            if self.enviar_email_vencimento(parcela.id):
                enviados += 1
            else:
                erros += 1

        resultado = {
            'total_vencidas': total,
            'emails_enviados': enviados,
            'emails_erros': erros
        }

        print(f"\n[NOTIFICAÇÃO] Resultado:")
        print(f"  - Total vencidas: {total}")
        print(f"  - Emails enviados: {enviados}")
        print(f"  - Erros: {erros}")

        return resultado

    def obter_relatorio_corretor(self, corretor_id: int) -> Dict:
        """
        Gera relatório completo de parcelas do corretor

        Args:
            corretor_id: ID do corretor

        Returns:
            Dict com dados do relatório
        """
        parcelas = self.session.query(Parcela).filter_by(corretor_id=corretor_id).all()

        total_pendente = sum(p.valor for p in parcelas if p.status in ['PENDENTE', 'VENCIDA', 'NOTIFICADA'])
        total_quitado = sum(p.valor for p in parcelas if p.status == 'QUITADA')
        total_vencido = sum(p.valor for p in parcelas if p.status in ['VENCIDA', 'NOTIFICADA'])

        num_pendentes = len([p for p in parcelas if p.status in ['PENDENTE', 'VENCIDA', 'NOTIFICADA']])
        num_quitadas = len([p for p in parcelas if p.status == 'QUITADA'])
        num_vencidas = len([p for p in parcelas if p.status in ['VENCIDA', 'NOTIFICADA']])

        return {
            'total_parcelas': len(parcelas),
            'valor_total_pendente': total_pendente,
            'valor_total_quitado': total_quitado,
            'valor_total_vencido': total_vencido,
            'num_pendentes': num_pendentes,
            'num_quitadas': num_quitadas,
            'num_vencidas': num_vencidas,
            'parcelas': parcelas
        }


def inicializar_sistema_parcelas():
    """Inicializa o sistema de parcelas criando as tabelas"""
    engine = criar_banco()
    Base.metadata.create_all(engine)
    print("[PARCELAS] Sistema de parcelas inicializado!")


if __name__ == "__main__":
    inicializar_sistema_parcelas()
