"""
Bot Integrator - Integração com Webhooks e APIs
Sistema de notificações automáticas via Clawdbot e recepção de leads
"""

import requests
import json
from datetime import datetime
from typing import Dict, Optional, List
from database import criar_banco, obter_sessao, Proposta, Lancamento, Corretor, Seguradora
from flask import Flask, request, jsonify
import threading
import os


class WebhookConfig:
    """Configuração de webhooks"""

    def __init__(self, config_path: str = "webhook_config.json"):
        """
        Inicializa configuração de webhooks

        Args:
            config_path: Caminho do arquivo de configuração
        """
        self.config_path = config_path
        self.config = self.carregar_configuracao()

    def carregar_configuracao(self) -> Dict:
        """Carrega configuração de webhooks"""
        default_config = {
            "webhooks": {
                "clawdbot_url": "https://api.clawdbot.com/webhook",
                "clawdbot_token": "seu_token_aqui",
                "backup_url": "https://backup.webhook.com/receive",
                "timeout": 10,
                "retry_attempts": 3
            },
            "templates": {
                "proposta_finalizada": {
                    "cliente": {
                        "titulo": "Proposta Aprovada! 🎉",
                        "mensagem": "Olá {cliente_nome}! Sua proposta #{proposta_id} foi aprovada. Valor: R$ {valor_bruto}. Em breve entraremos em contato!"
                    },
                    "corretor": {
                        "titulo": "Nova Venda Registrada! 💰",
                        "mensagem": "Parabéns {corretor_nome}! Venda de R$ {valor_bruto} para {cliente_nome}. Comissão estimada: R$ {comissao_liquida}"
                    }
                },
                "pagamento_baixado": {
                    "corretor": {
                        "titulo": "Pagamento Recebido! 💵",
                        "mensagem": "Olá {corretor_nome}! Pagamento de R$ {valor_pagamento} foi baixado. Proposta: #{proposta_id}"
                    }
                },
                "lead_recebido": {
                    "admin": {
                        "titulo": "Novo Lead! 🚀",
                        "mensagem": "Lead de {origem}: {cliente_nome} ({telefone}). Interesse: {produto}"
                    }
                }
            },
            "api_server": {
                "host": "0.0.0.0",
                "port": 5000,
                "debug": False
            }
        }

        # Tentar carregar do arquivo
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    custom_config = json.load(f)
                    return {**default_config, **custom_config}
            except Exception as e:
                print(f"Erro ao carregar config: {e}")

        # Salvar config padrão
        self.salvar_configuracao(default_config)
        return default_config

    def salvar_configuracao(self, config: Dict = None):
        """Salva configuração em arquivo"""
        if config is None:
            config = self.config

        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)


class ClawdBot:
    """Cliente para envio de mensagens via Clawdbot"""

    def __init__(self, config: WebhookConfig = None):
        """
        Inicializa cliente Clawdbot

        Args:
            config: Configuração de webhooks
        """
        if config is None:
            config = WebhookConfig()

        self.config = config
        self.webhook_url = config.config['webhooks']['clawdbot_url']
        self.token = config.config['webhooks']['clawdbot_token']
        self.timeout = config.config['webhooks']['timeout']
        self.retry_attempts = config.config['webhooks']['retry_attempts']

    def enviar_webhook(self, payload: Dict) -> Dict:
        """
        Envia webhook para Clawdbot

        Args:
            payload: Dados a enviar

        Returns:
            dict: Resposta da API
        """
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }

        for tentativa in range(self.retry_attempts):
            try:
                response = requests.post(
                    self.webhook_url,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout
                )

                if response.status_code == 200:
                    return {
                        'sucesso': True,
                        'mensagem': 'Webhook enviado com sucesso',
                        'resposta': response.json()
                    }
                else:
                    print(f"Tentativa {tentativa + 1}: Status {response.status_code}")

            except requests.exceptions.RequestException as e:
                print(f"Tentativa {tentativa + 1} falhou: {e}")

        return {
            'sucesso': False,
            'mensagem': 'Falha ao enviar webhook após tentativas',
            'erro': str(e) if 'e' in locals() else 'Timeout'
        }

    def notificar_proposta_finalizada(self, proposta: Proposta) -> Dict:
        """
        Notifica cliente e corretor sobre proposta finalizada

        Args:
            proposta: Objeto Proposta

        Returns:
            dict: Resultado do envio
        """
        templates = self.config.config['templates']['proposta_finalizada']

        # Calcular comissão estimada
        from finance_engine import FinanceEngine
        engine = criar_banco()
        session = obter_sessao(engine)
        finance = FinanceEngine(session=session)

        comissao_bruta = proposta.valor_bruto * (proposta.corretor.comissao_padrao / 100)
        liquido, _ = finance.calcular_impostos(comissao_bruta)

        finance.fechar()
        session.close()

        # Payload para cliente
        payload_cliente = {
            'tipo': 'proposta_finalizada',
            'destinatario': 'cliente',
            'dados': {
                'titulo': templates['cliente']['titulo'],
                'mensagem': templates['cliente']['mensagem'].format(
                    cliente_nome=proposta.cliente_nome,
                    proposta_id=proposta.id,
                    valor_bruto=f"{proposta.valor_bruto:,.2f}"
                ),
                'proposta_id': proposta.id,
                'cliente_nome': proposta.cliente_nome,
                'valor': proposta.valor_bruto,
                'data': proposta.data_venda.isoformat(),
                'seguradora': proposta.seguradora.nome
            }
        }

        # Payload para corretor
        payload_corretor = {
            'tipo': 'proposta_finalizada',
            'destinatario': 'corretor',
            'dados': {
                'titulo': templates['corretor']['titulo'],
                'mensagem': templates['corretor']['mensagem'].format(
                    corretor_nome=proposta.corretor.nome,
                    valor_bruto=f"{proposta.valor_bruto:,.2f}",
                    cliente_nome=proposta.cliente_nome,
                    comissao_liquida=f"{liquido:,.2f}"
                ),
                'corretor_id': proposta.corretor_id,
                'corretor_nome': proposta.corretor.nome,
                'proposta_id': proposta.id,
                'valor': proposta.valor_bruto,
                'comissao': liquido
            }
        }

        # Enviar ambos
        resultado_cliente = self.enviar_webhook(payload_cliente)
        resultado_corretor = self.enviar_webhook(payload_corretor)

        return {
            'cliente': resultado_cliente,
            'corretor': resultado_corretor
        }

    def notificar_pagamento_baixado(self, lancamento: Lancamento) -> Dict:
        """
        Notifica corretor sobre pagamento baixado

        Args:
            lancamento: Objeto Lancamento

        Returns:
            dict: Resultado do envio
        """
        templates = self.config.config['templates']['pagamento_baixado']
        proposta = lancamento.proposta

        payload = {
            'tipo': 'pagamento_baixado',
            'destinatario': 'corretor',
            'dados': {
                'titulo': templates['corretor']['titulo'],
                'mensagem': templates['corretor']['mensagem'].format(
                    corretor_nome=proposta.corretor.nome,
                    valor_pagamento=f"{lancamento.valor_esperado:,.2f}",
                    proposta_id=proposta.id
                ),
                'lancamento_id': lancamento.id,
                'proposta_id': proposta.id,
                'corretor_id': proposta.corretor_id,
                'corretor_nome': proposta.corretor.nome,
                'valor': lancamento.valor_esperado,
                'data_pagamento': datetime.now().isoformat()
            }
        }

        return self.enviar_webhook(payload)

    def notificar_lead_recebido(self, lead_data: Dict) -> Dict:
        """
        Notifica admin sobre novo lead

        Args:
            lead_data: Dados do lead

        Returns:
            dict: Resultado do envio
        """
        templates = self.config.config['templates']['lead_recebido']

        payload = {
            'tipo': 'lead_recebido',
            'destinatario': 'admin',
            'dados': {
                'titulo': templates['admin']['titulo'],
                'mensagem': templates['admin']['mensagem'].format(
                    origem=lead_data.get('origem', 'Web'),
                    cliente_nome=lead_data.get('nome', 'N/A'),
                    telefone=lead_data.get('telefone', 'N/A'),
                    produto=lead_data.get('produto', 'N/A')
                ),
                'lead': lead_data,
                'timestamp': datetime.now().isoformat()
            }
        }

        return self.enviar_webhook(payload)


class LeadReceiver:
    """Receptor de leads do Portal de Vendas Web"""

    def __init__(self):
        """Inicializa receptor de leads"""
        self.app = Flask(__name__)
        self.config = WebhookConfig()
        self.clawdbot = ClawdBot(self.config)
        self.session = obter_sessao(criar_banco())

        # Registrar rotas
        self.setup_routes()

    def setup_routes(self):
        """Configura rotas da API"""

        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            return jsonify({
                'status': 'online',
                'timestamp': datetime.now().isoformat(),
                'service': 'Lead Receiver API'
            })

        @self.app.route('/api/lead', methods=['POST'])
        def receber_lead():
            """
            Endpoint para receber leads do Portal de Vendas Web

            Payload esperado:
            {
                "nome": "João Silva",
                "email": "joao@email.com",
                "telefone": "(11) 98765-4321",
                "cpf": "123.456.789-01",
                "produto": "Seguro Saúde",
                "origem": "Google Ads",
                "utm_source": "google",
                "utm_campaign": "campanha_2026",
                "mensagem": "Gostaria de um orçamento"
            }
            """
            try:
                data = request.get_json()

                # Validar dados obrigatórios
                campos_obrigatorios = ['nome', 'telefone']
                for campo in campos_obrigatorios:
                    if campo not in data:
                        return jsonify({
                            'sucesso': False,
                            'erro': f'Campo obrigatório ausente: {campo}'
                        }), 400

                # Processar lead
                resultado = self.processar_lead(data)

                if resultado['sucesso']:
                    # Notificar via Clawdbot
                    self.clawdbot.notificar_lead_recebido(data)

                    return jsonify({
                        'sucesso': True,
                        'mensagem': 'Lead recebido com sucesso',
                        'lead_id': resultado.get('lead_id'),
                        'timestamp': datetime.now().isoformat()
                    }), 201
                else:
                    return jsonify({
                        'sucesso': False,
                        'erro': resultado['erro']
                    }), 500

            except Exception as e:
                return jsonify({
                    'sucesso': False,
                    'erro': str(e)
                }), 500

        @self.app.route('/api/webhook/test', methods=['POST'])
        def test_webhook():
            """Endpoint de teste de webhook"""
            data = request.get_json()

            payload = {
                'tipo': 'teste',
                'destinatario': 'admin',
                'dados': {
                    'titulo': 'Teste de Webhook',
                    'mensagem': 'Este é um teste de webhook do Bot Integrator',
                    'timestamp': datetime.now().isoformat(),
                    'dados_teste': data
                }
            }

            resultado = self.clawdbot.enviar_webhook(payload)

            return jsonify(resultado)

    def processar_lead(self, data: Dict) -> Dict:
        """
        Processa lead recebido

        Args:
            data: Dados do lead

        Returns:
            dict: Resultado do processamento
        """
        try:
            # Aqui você pode:
            # 1. Salvar lead em tabela específica
            # 2. Criar uma proposta em análise
            # 3. Enviar para fila de processamento
            # 4. Atribuir a um corretor

            # Por enquanto, apenas log
            print(f"Lead recebido: {data['nome']} - {data['telefone']}")

            # Poderia criar uma proposta em estado "PENDENTE"
            # ou salvar em uma tabela "leads" separada

            return {
                'sucesso': True,
                'lead_id': f"LEAD-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'mensagem': 'Lead processado com sucesso'
            }

        except Exception as e:
            return {
                'sucesso': False,
                'erro': str(e)
            }

    def iniciar_servidor(self):
        """Inicia servidor API"""
        config = self.config.config['api_server']
        print(f"\n🚀 Lead Receiver API iniciando...")
        print(f"   URL: http://{config['host']}:{config['port']}")
        print(f"   Endpoints:")
        print(f"   - GET  /health")
        print(f"   - POST /api/lead")
        print(f"   - POST /api/webhook/test")
        print()

        self.app.run(
            host=config['host'],
            port=config['port'],
            debug=config['debug']
        )


# Funções auxiliares para integração fácil
def notificar_proposta(proposta_id: int) -> Dict:
    """
    Notifica sobre proposta finalizada

    Args:
        proposta_id: ID da proposta

    Returns:
        dict: Resultado das notificações
    """
    engine = criar_banco()
    session = obter_sessao(engine)

    proposta = session.query(Proposta).get(proposta_id)

    if not proposta:
        session.close()
        return {'sucesso': False, 'erro': 'Proposta não encontrada'}

    bot = ClawdBot()
    resultado = bot.notificar_proposta_finalizada(proposta)

    session.close()
    return resultado


def notificar_pagamento(lancamento_id: int) -> Dict:
    """
    Notifica sobre pagamento baixado

    Args:
        lancamento_id: ID do lançamento

    Returns:
        dict: Resultado da notificação
    """
    engine = criar_banco()
    session = obter_sessao(engine)

    lancamento = session.query(Lancamento).get(lancamento_id)

    if not lancamento:
        session.close()
        return {'sucesso': False, 'erro': 'Lançamento não encontrado'}

    bot = ClawdBot()
    resultado = bot.notificar_pagamento_baixado(lancamento)

    session.close()
    return resultado


def iniciar_api_leads():
    """Inicia servidor de recepção de leads"""
    receiver = LeadReceiver()
    receiver.iniciar_servidor()


if __name__ == '__main__':
    print("=== Bot Integrator ===\n")

    # Criar configuração
    config = WebhookConfig()
    config.salvar_configuracao()
    print("[OK] Configuração criada: webhook_config.json\n")

    print("Opções de uso:")
    print("\n1. Notificar proposta:")
    print("   from bot_integrator import notificar_proposta")
    print("   resultado = notificar_proposta(proposta_id=1)")

    print("\n2. Notificar pagamento:")
    print("   from bot_integrator import notificar_pagamento")
    print("   resultado = notificar_pagamento(lancamento_id=1)")

    print("\n3. Iniciar API de recepção de leads:")
    print("   from bot_integrator import iniciar_api_leads")
    print("   iniciar_api_leads()")

    print("\n4. Iniciar servidor agora:")
    print("   py bot_integrator.py --server")

    print("\n[OK] Bot Integrator pronto!\n")

    # Se executado com --server, iniciar API
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--server':
        iniciar_api_leads()
