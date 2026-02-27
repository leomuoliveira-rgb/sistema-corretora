"""
Gerenciador de Configurações - Sistema Financeiro de Corretora
Funções para gerenciar impostos e alíquotas via banco de dados
"""

from sqlalchemy.orm import Session
from database import Configuracao, criar_banco, obter_sessao


class ConfigManager:
    """Gerenciador de configurações do sistema"""

    def __init__(self, session: Session = None, database_url='sqlite:///corretora.db'):
        """
        Inicializa o gerenciador de configurações

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

    def get_imposto(self, nome: str) -> float:
        """
        Obtém o valor de um imposto/alíquota

        Args:
            nome: Nome da configuração (ex: 'ISS', 'IRPF', 'PIS', etc)

        Returns:
            float: Valor da alíquota (retorna 0.0 se não encontrado)

        Exemplo:
            >>> config = ConfigManager()
            >>> iss = config.get_imposto('ISS')
            >>> print(f"ISS: {iss}%")
        """
        config = self.session.query(Configuracao).filter_by(chave=nome).first()

        if config is None:
            return 0.0

        try:
            return float(config.valor)
        except ValueError:
            print(f"Aviso: Valor inválido para {nome}: {config.valor}")
            return 0.0

    def set_imposto(self, nome: str, valor: float) -> bool:
        """
        Define ou atualiza o valor de um imposto/alíquota

        Args:
            nome: Nome da configuração (ex: 'ISS', 'IRPF', 'PIS', etc)
            valor: Valor da alíquota (em percentual, ex: 5.0 para 5%)

        Returns:
            bool: True se sucesso, False se erro

        Exemplo:
            >>> config = ConfigManager()
            >>> config.set_imposto('ISS', 5.0)
            >>> config.set_imposto('IRPF', 15.0)
        """
        try:
            config = self.session.query(Configuracao).filter_by(chave=nome).first()

            if config is None:
                # Criar nova configuração
                config = Configuracao(chave=nome, valor=str(valor))
                self.session.add(config)
            else:
                # Atualizar configuração existente
                config.valor = str(valor)

            self.session.commit()
            return True

        except Exception as e:
            print(f"Erro ao salvar configuração {nome}: {e}")
            self.session.rollback()
            return False

    def listar_impostos(self) -> dict:
        """
        Lista todos os impostos/alíquotas cadastrados

        Returns:
            dict: Dicionário com nome e valor de cada imposto

        Exemplo:
            >>> config = ConfigManager()
            >>> impostos = config.listar_impostos()
            >>> for nome, valor in impostos.items():
            ...     print(f"{nome}: {valor}%")
        """
        configs = self.session.query(Configuracao).all()

        impostos = {}
        for config in configs:
            try:
                impostos[config.chave] = float(config.valor)
            except ValueError:
                impostos[config.chave] = config.valor

        return impostos

    def remover_imposto(self, nome: str) -> bool:
        """
        Remove um imposto/alíquota do sistema

        Args:
            nome: Nome da configuração a ser removida

        Returns:
            bool: True se removido, False se não encontrado ou erro
        """
        try:
            config = self.session.query(Configuracao).filter_by(chave=nome).first()

            if config is None:
                return False

            self.session.delete(config)
            self.session.commit()
            return True

        except Exception as e:
            print(f"Erro ao remover configuração {nome}: {e}")
            self.session.rollback()
            return False

    def inicializar_impostos_padrao(self):
        """
        Inicializa impostos padrão do sistema (executar apenas uma vez)
        """
        impostos_padrao = {
            'ISS': 5.0,           # Imposto sobre Serviços
            'IRPF': 15.0,         # Imposto de Renda Pessoa Física
            'PIS': 0.65,          # Programa de Integração Social
            'COFINS': 3.0,        # Contribuição para Financiamento da Seguridade Social
            'CSLL': 1.0,          # Contribuição Social sobre Lucro Líquido
        }

        for nome, valor in impostos_padrao.items():
            if self.get_imposto(nome) == 0.0:
                self.set_imposto(nome, valor)
                print(f"Imposto {nome} configurado: {valor}%")

    def fechar(self):
        """Fecha a sessão do banco de dados"""
        if self._own_session:
            self.session.close()

    def __enter__(self):
        """Suporte para context manager (with statement)"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Fecha a sessão ao sair do context manager"""
        self.fechar()


# Funções auxiliares para uso direto (sem instanciar a classe)
def get_imposto(nome: str, database_url='sqlite:///corretora.db') -> float:
    """
    Função auxiliar para obter imposto sem instanciar ConfigManager

    Args:
        nome: Nome do imposto
        database_url: URL do banco de dados

    Returns:
        float: Valor do imposto
    """
    with ConfigManager(database_url=database_url) as config:
        return config.get_imposto(nome)


def set_imposto(nome: str, valor: float, database_url='sqlite:///corretora.db') -> bool:
    """
    Função auxiliar para definir imposto sem instanciar ConfigManager

    Args:
        nome: Nome do imposto
        valor: Valor do imposto
        database_url: URL do banco de dados

    Returns:
        bool: True se sucesso
    """
    with ConfigManager(database_url=database_url) as config:
        return config.set_imposto(nome, valor)


if __name__ == '__main__':
    # Exemplo de uso
    print("=== Testando ConfigManager ===\n")

    # Criar gerenciador
    config = ConfigManager()

    # Inicializar impostos padrão
    print("Inicializando impostos padrão...")
    config.inicializar_impostos_padrao()

    print("\n--- Impostos cadastrados ---")
    impostos = config.listar_impostos()
    for nome, valor in impostos.items():
        print(f"{nome}: {valor}%")

    # Testar alteração
    print("\n--- Alterando ISS para 6.5% ---")
    config.set_imposto('ISS', 6.5)
    print(f"Novo valor ISS: {config.get_imposto('ISS')}%")

    # Adicionar novo imposto
    print("\n--- Adicionando novo imposto (IOF) ---")
    config.set_imposto('IOF', 0.38)
    print(f"IOF cadastrado: {config.get_imposto('IOF')}%")

    print("\n--- Lista atualizada ---")
    impostos = config.listar_impostos()
    for nome, valor in impostos.items():
        print(f"{nome}: {valor}%")

    config.fechar()
    print("\n✓ Testes concluídos com sucesso!")
