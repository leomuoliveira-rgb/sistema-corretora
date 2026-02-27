"""
Finance Engine - Motor de Cálculos Financeiros
Gera lançamentos automáticos com cálculo de impostos
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import Proposta, Lancamento, Seguradora, obter_sessao, criar_banco
from config_manager import ConfigManager
from typing import List, Tuple


class FinanceEngine:
    """Motor financeiro para cálculo de comissões e impostos"""

    def __init__(self, session: Session = None, database_url='sqlite:///corretora.db'):
        """
        Inicializa o motor financeiro

        Args:
            session: Sessão do SQLAlchemy (opcional)
            database_url: URL do banco de dados
        """
        if session is None:
            engine = criar_banco(database_url)
            self.session = obter_sessao(engine)
            self._own_session = True
        else:
            self.session = session
            self._own_session = False

        self.config_manager = ConfigManager(session=self.session)

    def calcular_impostos(self, valor_bruto: float) -> Tuple[float, dict]:
        """
        Calcula o valor líquido após descontar impostos

        Args:
            valor_bruto: Valor bruto da comissão

        Returns:
            Tuple[float, dict]: (valor_liquido, detalhamento_impostos)

        Exemplo:
            >>> engine = FinanceEngine()
            >>> liquido, detalhes = engine.calcular_impostos(1000.00)
            >>> print(f"Líquido: R$ {liquido:.2f}")
        """
        # Buscar alíquotas
        pis = self.config_manager.get_imposto('PIS')
        cofins = self.config_manager.get_imposto('COFINS')
        iss = self.config_manager.get_imposto('ISS')
        irpf = self.config_manager.get_imposto('IRPF')
        csll = self.config_manager.get_imposto('CSLL')

        # Calcular valores
        valor_pis = valor_bruto * (pis / 100)
        valor_cofins = valor_bruto * (cofins / 100)
        valor_iss = valor_bruto * (iss / 100)
        valor_irpf = valor_bruto * (irpf / 100)
        valor_csll = valor_bruto * (csll / 100)

        total_impostos = valor_pis + valor_cofins + valor_iss + valor_irpf + valor_csll
        valor_liquido = valor_bruto - total_impostos

        detalhes = {
            'valor_bruto': valor_bruto,
            'PIS': {'aliquota': pis, 'valor': valor_pis},
            'COFINS': {'aliquota': cofins, 'valor': valor_cofins},
            'ISS': {'aliquota': iss, 'valor': valor_iss},
            'IRPF': {'aliquota': irpf, 'valor': valor_irpf},
            'CSLL': {'aliquota': csll, 'valor': valor_csll},
            'total_impostos': total_impostos,
            'valor_liquido': valor_liquido
        }

        return valor_liquido, detalhes

    def parsear_regra_pagamento(self, regra: str) -> List[int]:
        """
        Converte regra de pagamento em lista de dias

        Args:
            regra: String com dias separados por "/" (ex: "7/30/60") ou número único

        Returns:
            List[int]: Lista de dias para pagamento

        Exemplo:
            >>> engine = FinanceEngine()
            >>> engine.parsear_regra_pagamento("7/30/60")
            [7, 30, 60]
            >>> engine.parsear_regra_pagamento("30")
            [30]
        """
        regra_str = str(regra).strip()

        if '/' in regra_str:
            # Formato: "7/30/60"
            dias = [int(d.strip()) for d in regra_str.split('/')]
        else:
            # Formato: "30" ou 30
            dias = [int(regra_str)]

        return sorted(dias)  # Ordenar por segurança

    def gerar_lancamentos(
        self,
        proposta: Proposta,
        calcular_comissao: bool = True,
        percentual_comissao: float = None
    ) -> List[Lancamento]:
        """
        Gera lançamentos automáticos para uma proposta

        Args:
            proposta: Objeto Proposta
            calcular_comissao: Se True, aplica % de comissão do corretor
            percentual_comissao: Percentual customizado (sobrescreve comissão do corretor)

        Returns:
            List[Lancamento]: Lista de lançamentos criados

        Exemplo:
            >>> engine = FinanceEngine()
            >>> proposta = session.query(Proposta).first()
            >>> lancamentos = engine.gerar_lancamentos(proposta)
            >>> print(f"{len(lancamentos)} lançamentos criados")
        """
        # Validar proposta
        if proposta.seguradora is None:
            raise ValueError("Proposta deve ter uma seguradora associada")

        if proposta.corretor is None:
            raise ValueError("Proposta deve ter um corretor associado")

        # Obter regra de pagamento
        regra = proposta.seguradora.regra_pagamento_dias
        dias_pagamento = self.parsear_regra_pagamento(regra)

        # Calcular valor base (comissão)
        if calcular_comissao:
            if percentual_comissao is None:
                percentual_comissao = proposta.corretor.comissao_padrao

            valor_comissao_bruto = proposta.valor_bruto * (percentual_comissao / 100)
        else:
            valor_comissao_bruto = proposta.valor_bruto

        # Calcular impostos
        valor_liquido, detalhes_impostos = self.calcular_impostos(valor_comissao_bruto)

        # Dividir valor líquido pelos lançamentos
        num_lancamentos = len(dias_pagamento)
        valor_por_lancamento = valor_liquido / num_lancamentos

        # Criar lançamentos
        lancamentos = []
        data_base = proposta.data_venda

        for i, dias in enumerate(dias_pagamento):
            data_vencimento = data_base + timedelta(days=dias)

            # Ajustar último lançamento para compensar arredondamentos
            if i == num_lancamentos - 1:
                valor_final = valor_liquido - (valor_por_lancamento * (num_lancamentos - 1))
            else:
                valor_final = valor_por_lancamento

            lancamento = Lancamento(
                proposta_id=proposta.id,
                data_vencimento=data_vencimento,
                valor_esperado=round(valor_final, 2),
                status_pago=False
            )

            lancamentos.append(lancamento)
            self.session.add(lancamento)

        # Commit no banco
        self.session.commit()

        return lancamentos

    def recalcular_lancamentos(self, proposta: Proposta) -> List[Lancamento]:
        """
        Remove lançamentos antigos e recalcula

        Args:
            proposta: Objeto Proposta

        Returns:
            List[Lancamento]: Novos lançamentos criados
        """
        # Remover lançamentos existentes não pagos
        self.session.query(Lancamento).filter(
            Lancamento.proposta_id == proposta.id,
            Lancamento.status_pago == False
        ).delete()

        self.session.commit()

        # Gerar novos lançamentos
        return self.gerar_lancamentos(proposta)

    def marcar_lancamento_pago(self, lancamento_id: int) -> bool:
        """
        Marca um lançamento como pago

        Args:
            lancamento_id: ID do lançamento

        Returns:
            bool: True se sucesso
        """
        try:
            lancamento = self.session.query(Lancamento).get(lancamento_id)

            if lancamento is None:
                return False

            lancamento.status_pago = True
            self.session.commit()
            return True

        except Exception as e:
            print(f"Erro ao marcar lançamento como pago: {e}")
            self.session.rollback()
            return False

    def obter_relatorio_proposta(self, proposta_id: int) -> dict:
        """
        Gera relatório completo de uma proposta

        Args:
            proposta_id: ID da proposta

        Returns:
            dict: Relatório com todos os dados calculados
        """
        proposta = self.session.query(Proposta).get(proposta_id)

        if proposta is None:
            return {'erro': 'Proposta não encontrada'}

        # Calcular comissão
        comissao_bruto = proposta.valor_bruto * (proposta.corretor.comissao_padrao / 100)
        liquido, impostos = self.calcular_impostos(comissao_bruto)

        # Lançamentos
        lancamentos = proposta.lancamentos
        total_pago = sum(l.valor_esperado for l in lancamentos if l.status_pago)
        total_pendente = sum(l.valor_esperado for l in lancamentos if not l.status_pago)

        relatorio = {
            'proposta_id': proposta.id,
            'cliente': proposta.cliente_nome,
            'seguradora': proposta.seguradora.nome,
            'corretor': proposta.corretor.nome,
            'data_venda': proposta.data_venda.strftime('%d/%m/%Y'),
            'valor_bruto_apolice': proposta.valor_bruto,
            'comissao_percentual': proposta.corretor.comissao_padrao,
            'comissao_bruto': comissao_bruto,
            'impostos': impostos,
            'comissao_liquido': liquido,
            'lancamentos': {
                'total': len(lancamentos),
                'pagos': sum(1 for l in lancamentos if l.status_pago),
                'pendentes': sum(1 for l in lancamentos if not l.status_pago),
                'valor_pago': total_pago,
                'valor_pendente': total_pendente
            }
        }

        return relatorio

    def fechar(self):
        """Fecha a sessão do banco de dados"""
        if self._own_session:
            self.session.close()

    def __enter__(self):
        """Suporte para context manager"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Fecha ao sair do context manager"""
        self.fechar()


# Funções auxiliares
def gerar_lancamentos(proposta: Proposta, session: Session = None) -> List[Lancamento]:
    """
    Função auxiliar para gerar lançamentos sem instanciar FinanceEngine

    Args:
        proposta: Objeto Proposta
        session: Sessão do SQLAlchemy

    Returns:
        List[Lancamento]: Lançamentos criados
    """
    with FinanceEngine(session=session) as engine:
        return engine.gerar_lancamentos(proposta)


if __name__ == '__main__':
    print("=== Teste do Finance Engine ===\n")

    # Criar sessão
    engine_db = criar_banco()
    session = obter_sessao(engine_db)

    # Inicializar configurações se necessário
    config = ConfigManager(session=session)
    if config.get_imposto('ISS') == 0.0:
        print("Inicializando impostos padrão...")
        config.inicializar_impostos_padrao()

    # Criar finance engine
    finance = FinanceEngine(session=session)

    # Buscar ou criar uma proposta de teste
    proposta = session.query(Proposta).first()

    if proposta:
        print(f"Testando com proposta existente: {proposta.cliente_nome}")
        print(f"Valor bruto: R$ {proposta.valor_bruto:.2f}")
        print(f"Seguradora: {proposta.seguradora.nome}")
        print(f"Regra de pagamento: {proposta.seguradora.regra_pagamento_dias} dias")
        print(f"Comissão corretor: {proposta.corretor.comissao_padrao}%\n")

        # Gerar lançamentos
        print("Gerando lançamentos...")
        lancamentos = finance.gerar_lancamentos(proposta)

        print(f"\n{len(lancamentos)} lançamentos criados:\n")
        for i, lanc in enumerate(lancamentos, 1):
            print(f"  {i}. Vencimento: {lanc.data_vencimento.strftime('%d/%m/%Y')}")
            print(f"     Valor: R$ {lanc.valor_esperado:.2f}")
            print(f"     Status: {'PAGO' if lanc.status_pago else 'PENDENTE'}\n")

        # Gerar relatório
        print("--- Relatório da Proposta ---")
        relatorio = finance.obter_relatorio_proposta(proposta.id)

        print(f"Cliente: {relatorio['cliente']}")
        print(f"Valor Apólice: R$ {relatorio['valor_bruto_apolice']:.2f}")
        print(f"Comissão Bruto: R$ {relatorio['comissao_bruto']:.2f}")
        print(f"Total Impostos: R$ {relatorio['impostos']['total_impostos']:.2f}")
        print(f"Comissão Líquido: R$ {relatorio['comissao_liquido']:.2f}")

    else:
        print("Nenhuma proposta encontrada no banco.")
        print("Execute test_database.py primeiro para criar dados de teste.")

    finance.fechar()
    print("\n[OK] Teste concluído!")
