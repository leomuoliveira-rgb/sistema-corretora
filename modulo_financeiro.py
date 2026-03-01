"""
Módulo Financeiro Avançado
Controle completo de fluxo de caixa, DRE, contas a pagar/receber
"""

from database import Base, criar_banco, obter_sessao
from sqlalchemy import Column, Integer, String, Float, Date, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from typing import Dict, List


# ============= NOVAS TABELAS FINANCEIRAS =============

class ContaBancaria(Base):
    """Contas bancárias da corretora"""
    __tablename__ = 'contas_bancarias'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(200), nullable=False)  # Ex: "Banco do Brasil CC 12345-6"
    banco = Column(String(100), nullable=False)
    agencia = Column(String(20), nullable=False)
    conta = Column(String(20), nullable=False)
    saldo_inicial = Column(Float, default=0.0)
    saldo_atual = Column(Float, default=0.0)
    ativa = Column(Boolean, default=True)

    # Relacionamentos
    transacoes = relationship('TransacaoFinanceira', back_populates='conta')

    def __repr__(self):
        return f"<ContaBancaria(nome='{self.nome}', saldo={self.saldo_atual})>"


class CategoriaFinanceira(Base):
    """Categorias para receitas e despesas"""
    __tablename__ = 'categorias_financeiras'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    tipo = Column(String(20), nullable=False)  # 'RECEITA' ou 'DESPESA'
    cor = Column(String(7), nullable=True)  # Hex color para gráficos
    descricao = Column(Text, nullable=True)

    # Relacionamentos
    transacoes = relationship('TransacaoFinanceira', back_populates='categoria')

    def __repr__(self):
        return f"<CategoriaFinanceira(nome='{self.nome}', tipo='{self.tipo}')>"


class TransacaoFinanceira(Base):
    """Registro de todas as transações financeiras"""
    __tablename__ = 'transacoes_financeiras'

    id = Column(Integer, primary_key=True, autoincrement=True)
    descricao = Column(String(255), nullable=False)
    tipo = Column(String(20), nullable=False)  # 'RECEITA' ou 'DESPESA'
    valor = Column(Float, nullable=False)
    data_transacao = Column(Date, nullable=False)
    data_vencimento = Column(Date, nullable=True)
    data_pagamento = Column(Date, nullable=True)
    status = Column(String(20), default='PENDENTE')  # PENDENTE, PAGO, CANCELADO
    categoria_id = Column(Integer, ForeignKey('categorias_financeiras.id'), nullable=True)
    conta_id = Column(Integer, ForeignKey('contas_bancarias.id'), nullable=True)
    proposta_id = Column(Integer, ForeignKey('propostas.id'), nullable=True)  # Se relacionado a proposta
    observacoes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    # Relacionamentos
    categoria = relationship('CategoriaFinanceira', back_populates='transacoes')
    conta = relationship('ContaBancaria', back_populates='transacoes')

    def __repr__(self):
        return f"<TransacaoFinanceira(descricao='{self.descricao}', valor={self.valor})>"


class Meta(Base):
    """Metas financeiras"""
    __tablename__ = 'metas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(200), nullable=False)
    tipo = Column(String(20), nullable=False)  # 'RECEITA', 'DESPESA', 'LUCRO'
    valor_meta = Column(Float, nullable=False)
    periodo = Column(String(20), nullable=False)  # 'MENSAL', 'TRIMESTRAL', 'ANUAL'
    mes = Column(Integer, nullable=True)
    ano = Column(Integer, nullable=False)
    ativa = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Meta(nome='{self.nome}', valor={self.valor_meta})>"


# ============= CLASSE DE CONTROLE FINANCEIRO =============

class ControleFinanceiro:
    """Classe para gerenciar todas as operações financeiras"""

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

    # ====== FLUXO DE CAIXA ======

    def obter_fluxo_caixa(self, data_inicio: datetime, data_fim: datetime) -> Dict:
        """
        Obtém fluxo de caixa detalhado entre duas datas

        Returns:
            Dict com receitas, despesas e saldo
        """
        from sqlalchemy.orm import joinedload as _jl
        transacoes = self.session.query(TransacaoFinanceira).filter(
            TransacaoFinanceira.data_transacao >= data_inicio,
            TransacaoFinanceira.data_transacao <= data_fim,
            TransacaoFinanceira.status == 'PAGO'
        ).options(_jl(TransacaoFinanceira.categoria)).all()

        total_receitas = sum(t.valor for t in transacoes if t.tipo == 'RECEITA')
        total_despesas = sum(t.valor for t in transacoes if t.tipo == 'DESPESA')
        saldo = total_receitas - total_despesas

        # Agrupar por categoria
        receitas_por_categoria = {}
        despesas_por_categoria = {}

        for t in transacoes:
            if t.categoria:
                categoria_nome = t.categoria.nome
                if t.tipo == 'RECEITA':
                    receitas_por_categoria[categoria_nome] = receitas_por_categoria.get(categoria_nome, 0) + t.valor
                else:
                    despesas_por_categoria[categoria_nome] = despesas_por_categoria.get(categoria_nome, 0) + t.valor

        return {
            'total_receitas': total_receitas,
            'total_despesas': total_despesas,
            'saldo': saldo,
            'receitas_por_categoria': receitas_por_categoria,
            'despesas_por_categoria': despesas_por_categoria,
            'periodo': {
                'inicio': data_inicio.strftime('%d/%m/%Y'),
                'fim': data_fim.strftime('%d/%m/%Y')
            }
        }

    def obter_contas_receber(self, vencidas=False) -> List:
        """
        Obtém contas a receber (receitas pendentes)

        Args:
            vencidas: Se True, retorna apenas vencidas
        """
        query = self.session.query(TransacaoFinanceira).filter(
            TransacaoFinanceira.tipo == 'RECEITA',
            TransacaoFinanceira.status == 'PENDENTE'
        )

        if vencidas:
            query = query.filter(TransacaoFinanceira.data_vencimento < datetime.now().date())

        return query.order_by(TransacaoFinanceira.data_vencimento).all()

    def obter_contas_pagar(self, vencidas=False) -> List:
        """
        Obtém contas a pagar (despesas pendentes)

        Args:
            vencidas: Se True, retorna apenas vencidas
        """
        query = self.session.query(TransacaoFinanceira).filter(
            TransacaoFinanceira.tipo == 'DESPESA',
            TransacaoFinanceira.status == 'PENDENTE'
        )

        if vencidas:
            query = query.filter(TransacaoFinanceira.data_vencimento < datetime.now().date())

        return query.order_by(TransacaoFinanceira.data_vencimento).all()

    # ====== DRE (Demonstração do Resultado do Exercício) ======

    def gerar_dre(self, mes: int, ano: int) -> Dict:
        """
        Gera DRE para um mês específico

        Args:
            mes: Mês (1-12)
            ano: Ano (ex: 2026)

        Returns:
            Dict com DRE completo
        """
        # Período do mês
        from calendar import monthrange
        ultimo_dia = monthrange(ano, mes)[1]
        data_inicio = datetime(ano, mes, 1)
        data_fim = datetime(ano, mes, ultimo_dia)

        # Obter fluxo de caixa
        fluxo = self.obter_fluxo_caixa(data_inicio, data_fim)

        # DRE estruturado
        dre = {
            'periodo': f"{mes:02d}/{ano}",
            'receita_bruta': fluxo['total_receitas'],
            'custos_operacionais': fluxo['total_despesas'],
            'lucro_operacional': fluxo['saldo'],
            'margem_lucro': (fluxo['saldo'] / fluxo['total_receitas'] * 100) if fluxo['total_receitas'] > 0 else 0,
            'detalhes': {
                'receitas': fluxo['receitas_por_categoria'],
                'despesas': fluxo['despesas_por_categoria']
            }
        }

        return dre

    # ====== METAS ======

    def obter_progresso_meta(self, meta_id: int) -> Dict:
        """
        Calcula progresso de uma meta

        Args:
            meta_id: ID da meta

        Returns:
            Dict com progresso da meta
        """
        meta = self.session.query(Meta).get(meta_id)

        if not meta:
            return {'erro': 'Meta não encontrada'}

        # Determinar período
        if meta.periodo == 'MENSAL':
            data_inicio = datetime(meta.ano, meta.mes, 1)
            from calendar import monthrange
            ultimo_dia = monthrange(meta.ano, meta.mes)[1]
            data_fim = datetime(meta.ano, meta.mes, ultimo_dia)
        elif meta.periodo == 'ANUAL':
            data_inicio = datetime(meta.ano, 1, 1)
            data_fim = datetime(meta.ano, 12, 31)

        # Obter realizado
        fluxo = self.obter_fluxo_caixa(data_inicio, data_fim)

        if meta.tipo == 'RECEITA':
            valor_realizado = fluxo['total_receitas']
        elif meta.tipo == 'DESPESA':
            valor_realizado = fluxo['total_despesas']
        elif meta.tipo == 'LUCRO':
            valor_realizado = fluxo['saldo']

        percentual = (valor_realizado / meta.valor_meta * 100) if meta.valor_meta > 0 else 0

        return {
            'meta': meta,
            'valor_meta': meta.valor_meta,
            'valor_realizado': valor_realizado,
            'percentual': percentual,
            'falta': meta.valor_meta - valor_realizado,
            'status': 'ATINGIDA' if percentual >= 100 else 'EM_PROGRESSO'
        }

    # ====== UTILITIES ======

    def criar_categorias_padrao(self):
        """Cria categorias padrão se não existirem"""
        categorias_receita = [
            ('Comissões', 'RECEITA', '#10b981'),
            ('Vitalícios', 'RECEITA', '#22c55e'),
            ('Outros Recebimentos', 'RECEITA', '#6366f1'),
        ]

        categorias_despesa = [
            ('Salários', 'DESPESA', '#ef4444'),
            ('Impostos', 'DESPESA', '#f59e0b'),
            ('Aluguel', 'DESPESA', '#ec4899'),
            ('Marketing', 'DESPESA', '#8b5cf6'),
            ('Infraestrutura', 'DESPESA', '#06b6d4'),
            ('Outros Custos', 'DESPESA', '#64748b'),
        ]

        for nome, tipo, cor in categorias_receita + categorias_despesa:
            existe = self.session.query(CategoriaFinanceira).filter_by(nome=nome).first()
            if not existe:
                cat = CategoriaFinanceira(nome=nome, tipo=tipo, cor=cor)
                self.session.add(cat)

        self.session.commit()


def inicializar_modulo_financeiro():
    """Inicializa o módulo financeiro criando as tabelas"""
    engine = criar_banco()
    Base.metadata.create_all(engine)

    session = obter_sessao(engine)
    controle = ControleFinanceiro(session)
    controle.criar_categorias_padrao()
    controle.fechar()

    print("[FINANCEIRO] Módulo inicializado com sucesso!")
