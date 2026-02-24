"""
Sistema Financeiro de Corretora - Modelos de Banco de Dados
SQLAlchemy models para gestão de propostas e comissões
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
import hashlib

Base = declarative_base()


# ============= AUTENTICAÇÃO =============

class Usuario(Base):
    """Tabela de usuários do sistema"""
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)  # Hash SHA256
    nome_completo = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False)
    tipo = Column(String(20), nullable=False)  # 'admin', 'corretor', 'corretora'
    ativo = Column(Boolean, default=True)
    corretor_id = Column(Integer, ForeignKey('corretores.id'), nullable=True)  # Se for corretor
    data_criacao = Column(DateTime, default=datetime.now)
    ultimo_acesso = Column(DateTime, nullable=True)

    # Relacionamento
    corretor = relationship('Corretor', foreign_keys=[corretor_id], backref='usuario')

    def __repr__(self):
        return f"<Usuario(username='{self.username}', tipo='{self.tipo}')>"

    def verificar_senha(self, senha):
        """Verifica se a senha está correta"""
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        return senha_hash == self.senha_hash

    @staticmethod
    def criar_hash_senha(senha):
        """Cria hash SHA256 da senha"""
        return hashlib.sha256(senha.encode()).hexdigest()


# ============= CRM =============

class Lead(Base):
    """Tabela de leads/prospects"""
    __tablename__ = 'leads'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(200), nullable=False)
    email = Column(String(200), nullable=True)
    telefone = Column(String(50), nullable=False)
    cpf_cnpj = Column(String(20), nullable=True)
    produto_interesse = Column(String(100), nullable=True)
    origem = Column(String(100), nullable=True)  # Google Ads, Facebook, Indicação, etc
    status = Column(String(50), default='NOVO')  # NOVO, CONTATO, QUALIFICADO, PROPOSTA, GANHO, PERDIDO
    corretor_id = Column(Integer, ForeignKey('corretores.id'), nullable=True)
    observacoes = Column(Text, nullable=True)
    data_criacao = Column(DateTime, default=datetime.now)
    data_ultima_interacao = Column(DateTime, nullable=True)

    # Relacionamentos
    corretor = relationship('Corretor', backref='leads')
    interacoes = relationship('Interacao', back_populates='lead', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Lead(nome='{self.nome}', status='{self.status}')>"


class Interacao(Base):
    """Histórico de interações com leads/clientes"""
    __tablename__ = 'interacoes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    lead_id = Column(Integer, ForeignKey('leads.id'), nullable=False)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    tipo = Column(String(50), nullable=False)  # LIGACAO, EMAIL, WHATSAPP, REUNIAO, PROPOSTA
    descricao = Column(Text, nullable=False)
    data_hora = Column(DateTime, default=datetime.now)
    proximo_followup = Column(DateTime, nullable=True)

    # Relacionamentos
    lead = relationship('Lead', back_populates='interacoes')
    usuario = relationship('Usuario', backref='interacoes')

    def __repr__(self):
        return f"<Interacao(tipo='{self.tipo}', lead_id={self.lead_id})>"


# ============= CONFIGURAÇÕES =============

class Configuracao(Base):
    """Tabela de configurações do sistema (impostos, alíquotas, etc)"""
    __tablename__ = 'configuracoes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    chave = Column(String(100), unique=True, nullable=False)
    valor = Column(String(255), nullable=False)

    def __repr__(self):
        return f"<Configuracao(chave='{self.chave}', valor='{self.valor}')>"


class Seguradora(Base):
    """Tabela de seguradoras"""
    __tablename__ = 'seguradoras'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(200), nullable=False)
    regra_pagamento_dias = Column(String(100), nullable=False)  # Dias para pagamento (ex: "7/30/60" ou "30")
    vitalicio_porcentagem = Column(Float, nullable=False)  # Percentual vitalício

    # Relacionamento
    propostas = relationship('Proposta', back_populates='seguradora')

    def __repr__(self):
        return f"<Seguradora(nome='{self.nome}')>"


class Corretor(Base):
    """Tabela de corretores"""
    __tablename__ = 'corretores'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(200), nullable=False)
    email = Column(String(200), nullable=True)  # E-mail do corretor
    telefone = Column(String(50), nullable=True)  # Telefone do corretor
    comissao_padrao = Column(Float, nullable=False)  # Percentual de comissão padrão

    # Relacionamento
    propostas = relationship('Proposta', back_populates='corretor')

    def __repr__(self):
        return f"<Corretor(nome='{self.nome}', comissao={self.comissao_padrao}%)>"


class Proposta(Base):
    """Tabela de propostas de seguro"""
    __tablename__ = 'propostas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    cliente_nome = Column(String(200), nullable=False)
    cliente_cpf = Column(String(20), nullable=True)  # CPF/CNPJ do cliente
    valor_bruto = Column(Float, nullable=False)
    seguradora_id = Column(Integer, ForeignKey('seguradoras.id'), nullable=False)
    corretor_id = Column(Integer, ForeignKey('corretores.id'), nullable=False)
    data_venda = Column(Date, nullable=False, default=datetime.now().date)

    # Relacionamentos
    seguradora = relationship('Seguradora', back_populates='propostas')
    corretor = relationship('Corretor', back_populates='propostas')
    lancamentos = relationship('Lancamento', back_populates='proposta', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Proposta(cliente='{self.cliente_nome}', valor={self.valor_bruto})>"


class Lancamento(Base):
    """Tabela de lançamentos financeiros (parcelas/pagamentos)"""
    __tablename__ = 'lancamentos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    proposta_id = Column(Integer, ForeignKey('propostas.id'), nullable=False)
    data_vencimento = Column(Date, nullable=False)
    valor_esperado = Column(Float, nullable=False)
    status_pago = Column(Boolean, default=False, nullable=False)

    # Relacionamento
    proposta = relationship('Proposta', back_populates='lancamentos')

    def __repr__(self):
        status = "PAGO" if self.status_pago else "PENDENTE"
        return f"<Lancamento(proposta_id={self.proposta_id}, valor={self.valor_esperado}, status={status})>"


# Funções utilitárias para inicialização do banco
def criar_banco(database_url='sqlite:///corretora.db'):
    """
    Cria o banco de dados e todas as tabelas

    Args:
        database_url: URL de conexão do banco (padrão: SQLite local)

    Returns:
        engine: Engine do SQLAlchemy
    """
    engine = create_engine(database_url, echo=False)
    Base.metadata.create_all(engine)

    # Aplicar migrações se necessário
    aplicar_migracoes(engine)

    return engine


def aplicar_migracoes(engine):
    """Aplica migrações ao banco de dados existente"""
    import sqlite3

    # Conectar diretamente ao SQLite para adicionar colunas
    try:
        # Extrair o caminho do banco da URL do engine
        db_path = str(engine.url).replace('sqlite:///', '')

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Verificar se as colunas email e telefone existem em corretores
        cursor.execute("PRAGMA table_info(corretores)")
        colunas = [col[1] for col in cursor.fetchall()]

        # Adicionar coluna email se não existir
        if 'email' not in colunas:
            cursor.execute("ALTER TABLE corretores ADD COLUMN email VARCHAR(200)")
            print("[MIGRAÇÃO] Coluna 'email' adicionada à tabela corretores")

        # Adicionar coluna telefone se não existir
        if 'telefone' not in colunas:
            cursor.execute("ALTER TABLE corretores ADD COLUMN telefone VARCHAR(50)")
            print("[MIGRAÇÃO] Coluna 'telefone' adicionada à tabela corretores")

        # Verificar se a coluna cliente_cpf existe em propostas
        cursor.execute("PRAGMA table_info(propostas)")
        colunas_propostas = [col[1] for col in cursor.fetchall()]

        # Adicionar coluna cliente_cpf se não existir
        if 'cliente_cpf' not in colunas_propostas:
            cursor.execute("ALTER TABLE propostas ADD COLUMN cliente_cpf VARCHAR(20)")
            print("[MIGRAÇÃO] Coluna 'cliente_cpf' adicionada à tabela propostas")

        conn.commit()
        conn.close()

    except Exception as e:
        print(f"[MIGRAÇÃO] Erro ao aplicar migrações: {e}")


def obter_sessao(engine):
    """
    Cria e retorna uma sessão do SQLAlchemy

    Args:
        engine: Engine do SQLAlchemy

    Returns:
        Session: Objeto de sessão do SQLAlchemy
    """
    Session = sessionmaker(bind=engine)
    return Session()


if __name__ == '__main__':
    # Exemplo de uso: criar banco de dados
    print("Criando banco de dados...")
    engine = criar_banco()
    print("Banco de dados criado com sucesso!")

    # Criar sessão de exemplo
    session = obter_sessao(engine)
    print("Sessão criada. Sistema pronto para uso!")
    session.close()
