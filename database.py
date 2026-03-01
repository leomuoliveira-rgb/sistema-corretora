"""
Sistema Financeiro de Corretora - Modelos de Banco de Dados
SQLAlchemy models para gestão de propostas e comissões
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Boolean, ForeignKey, DateTime, Text, event
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
    cliente_cpf = Column(String(20), nullable=True)
    cliente_rg = Column(String(30), nullable=True)
    cliente_data_nascimento = Column(Date, nullable=True)
    cliente_telefone = Column(String(50), nullable=True)
    cliente_email = Column(String(200), nullable=True)
    tipo_plano = Column(String(200), nullable=True)
    valor_bruto = Column(Float, nullable=False)
    seguradora_id = Column(Integer, ForeignKey('seguradoras.id'), nullable=False)
    corretor_id = Column(Integer, ForeignKey('corretores.id'), nullable=False)
    data_venda = Column(Date, nullable=False, default=datetime.now().date)

    # Relacionamentos
    seguradora = relationship('Seguradora', back_populates='propostas')
    corretor = relationship('Corretor', back_populates='propostas')
    lancamentos = relationship('Lancamento', back_populates='proposta', cascade='all, delete-orphan')
    dependentes = relationship('Dependente', back_populates='proposta', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Proposta(cliente='{self.cliente_nome}', valor={self.valor_bruto})>"


class Dependente(Base):
    """Dependentes vinculados a uma proposta"""
    __tablename__ = 'dependentes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    proposta_id = Column(Integer, ForeignKey('propostas.id'), nullable=False)
    nome = Column(String(200), nullable=False)
    cpf = Column(String(20), nullable=True)
    rg = Column(String(30), nullable=True)
    data_nascimento = Column(Date, nullable=True)
    parentesco = Column(String(50), nullable=True)  # Cônjuge, Filho(a), etc.
    sexo = Column(String(20), nullable=True)         # Masculino, Feminino
    estado_civil = Column(String(50), nullable=True) # Solteiro, Casado, etc.
    telefone = Column(String(50), nullable=True)
    email = Column(String(200), nullable=True)

    # Relacionamento
    proposta = relationship('Proposta', back_populates='dependentes')

    def __repr__(self):
        return f"<Dependente(nome='{self.nome}', proposta_id={self.proposta_id})>"


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
    # Importar todos os módulos com modelos para registrá-los no Base
    try:
        import modulo_financeiro  # noqa - registra ContaBancaria, CategoriaFinanceira, TransacaoFinanceira, Meta
    except Exception:
        pass
    try:
        import sistema_parcelas  # noqa - registra parcelas e config_email
    except Exception:
        pass

    engine = create_engine(
        database_url,
        echo=False,
        connect_args={"check_same_thread": False},
    )

    # Otimizações SQLite: WAL mode + cache generoso + synchronous normal
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragmas(dbapi_conn, _record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA cache_size=-16000")  # ~16 MB de cache
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.close()

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

        # Novas colunas de dados cadastrais do cliente
        if 'cliente_rg' not in colunas_propostas:
            cursor.execute("ALTER TABLE propostas ADD COLUMN cliente_rg VARCHAR(30)")
            print("[MIGRAÇÃO] Coluna 'cliente_rg' adicionada à tabela propostas")

        if 'cliente_data_nascimento' not in colunas_propostas:
            cursor.execute("ALTER TABLE propostas ADD COLUMN cliente_data_nascimento DATE")
            print("[MIGRAÇÃO] Coluna 'cliente_data_nascimento' adicionada à tabela propostas")

        if 'cliente_telefone' not in colunas_propostas:
            cursor.execute("ALTER TABLE propostas ADD COLUMN cliente_telefone VARCHAR(50)")
            print("[MIGRAÇÃO] Coluna 'cliente_telefone' adicionada à tabela propostas")

        if 'cliente_email' not in colunas_propostas:
            cursor.execute("ALTER TABLE propostas ADD COLUMN cliente_email VARCHAR(200)")
            print("[MIGRAÇÃO] Coluna 'cliente_email' adicionada à tabela propostas")

        if 'tipo_plano' not in colunas_propostas:
            cursor.execute("ALTER TABLE propostas ADD COLUMN tipo_plano VARCHAR(200)")
            print("[MIGRAÇÃO] Coluna 'tipo_plano' adicionada à tabela propostas")

        # Verificar colunas em dependentes
        cursor.execute("PRAGMA table_info(dependentes)")
        colunas_dep = [col[1] for col in cursor.fetchall()]

        if 'sexo' not in colunas_dep:
            cursor.execute("ALTER TABLE dependentes ADD COLUMN sexo VARCHAR(20)")
            print("[MIGRAÇÃO] Coluna 'sexo' adicionada à tabela dependentes")

        if 'estado_civil' not in colunas_dep:
            cursor.execute("ALTER TABLE dependentes ADD COLUMN estado_civil VARCHAR(50)")
            print("[MIGRAÇÃO] Coluna 'estado_civil' adicionada à tabela dependentes")

        # ── Índices de performance ──────────────────────────────────────────
        # Criados com IF NOT EXISTS — seguros para rodar múltiplas vezes
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_lanc_status    ON lancamentos(status_pago)",
            "CREATE INDEX IF NOT EXISTS idx_lanc_venc      ON lancamentos(data_vencimento)",
            "CREATE INDEX IF NOT EXISTS idx_lanc_proposta  ON lancamentos(proposta_id)",
            "CREATE INDEX IF NOT EXISTS idx_prop_corretor  ON propostas(corretor_id)",
            "CREATE INDEX IF NOT EXISTS idx_prop_venda     ON propostas(data_venda)",
            "CREATE INDEX IF NOT EXISTS idx_lead_status    ON leads(status)",
            "CREATE INDEX IF NOT EXISTS idx_lead_corretor  ON leads(corretor_id)",
            "CREATE INDEX IF NOT EXISTS idx_inter_lead     ON interacoes(lead_id)",
            "CREATE INDEX IF NOT EXISTS idx_parc_status    ON parcelas(status)",
            "CREATE INDEX IF NOT EXISTS idx_tx_status      ON transacoes_financeiras(status)",
            "CREATE INDEX IF NOT EXISTS idx_tx_tipo        ON transacoes_financeiras(tipo)",
        ]
        for sql in indexes:
            try:
                cursor.execute(sql)
            except Exception:
                pass

        conn.commit()
        conn.close()

    except Exception as e:
        print(f"[MIGRAÇÃO] Erro ao aplicar migrações: {e}")


def obter_sessao(engine):
    """
    Cria e retorna uma sessão do SQLAlchemy.
    expire_on_commit=False: objetos salvos continuam acessíveis sem re-query.
    """
    Session = sessionmaker(bind=engine, expire_on_commit=False)
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
