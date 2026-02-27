"""
OCR Engine - Extração de Dados de PDFs
Extrai informações de Propostas e Relatórios de Pagamento usando PDFplumber e Regex
"""

import re
import json
import unicodedata
import difflib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pdfplumber

from database import criar_banco, obter_sessao, Proposta, Seguradora, Corretor, Dependente
from finance_engine import FinanceEngine


class OCRConfig:
    """Configuração de padrões de extração"""

    def __init__(self, config_path: str = "ocr_config.json"):
        """
        Inicializa configurações de extração

        Args:
            config_path: Caminho para arquivo de configuração JSON
        """
        self.config_path = config_path
        self.patterns = self.carregar_configuracao()

    def carregar_configuracao(self) -> Dict:
        """Carrega configuração de padrões regex"""
        default_config = {
            "cliente": {
                "nome": [
                    r"(?:Cliente|Segurado|Nome do Titular|Titular)[:\s]+([A-ZÁÉÍÓÚÀÃÕÂÊÔÇ][A-Za-záéíóúàãõâêôç\s]+?)(?:\n|CPF|CNPJ|RG|Data)",
                    r"Nome do Cliente[:\s]+([^\n]+)",
                    r"Razão Social[:\s]+([^\n]+)"
                ],
                "cpf_cnpj": [
                    r"(?:CPF|CNPJ)[:\s]*(\d{3}\.?\d{3}\.?\d{3}-?\d{2})",
                    r"(?:CPF|CNPJ)[:\s]*(\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2})",
                    r"(\d{3}\.\d{3}\.\d{3}-\d{2})",
                    r"(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})"
                ],
                "rg": [
                    r"RG[:\s]*(\d{1,2}\.?\d{3}\.?\d{3}-?[\dXx]?)",
                    r"(?:Identidade|R\.G\.)[:\s]*([0-9.\-/Xx]+)",
                    r"RG\s+N[ºo°]?[:\s]*([0-9.\-/Xx]+)"
                ],
                "data_nascimento": [
                    r"(?:Data de Nascimento|Nascimento|Dt\.?\s*Nasc\.?)[:\s]*(\d{2}/\d{2}/\d{4})",
                    r"(?:Data de Nascimento|Nascimento)[:\s]*(\d{2}-\d{2}-\d{4})",
                    r"Nasc[.:]?\s*(\d{2}/\d{2}/\d{4})"
                ],
                "telefone": [
                    r"(?:Tel|Telefone|Celular|Fone|WhatsApp)[:\s]*(\(?0?\d{2}\)?\s?\d{4,5}[-\s]?\d{4})",
                    r"(\(?\d{2}\)?\s?\d{4,5}[-\s]?\d{4})"
                ],
                "email": [
                    r"(?:E-mail|Email|E\.mail)[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",
                    r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"
                ]
            },
            "seguradora": {
                "nome": [
                    r"(?:Seguradora|Operadora)[:\s]+([A-ZÁÉÍÓÚ][A-Za-záéíóúàãõâêôç\s]+?)(?:\n|Produto|Plano)",
                    r"(SulAm[eé]rica|Porto Seguro|Bradesco|Amil|Unimed|Tokio Marine|Allianz|Hapvida|NotreDame|Intermédica|MetLife|Zurich|Liberty)",
                    r"Cia[:\s]+([^\n]+)"
                ],
                "produto": [
                    r"(?:Produto|Plano Contratado|Plano|Modalidade|Tipo de Plano)[:\s]+([^\n]+)",
                    r"(?:Cobertura|Categoria)[:\s]+([^\n]+)",
                    r"(Amil|Bradesco Saúde|SulAmérica Saúde|Porto Seguro Auto|Unimed|Saúde Empresarial|Saúde Individual|Odontológico|Vida)"
                ]
            },
            "dependentes": {
                "bloco": [
                    r"(?:DEPENDENTES?|Dados do[s]? Dependentes?)([\s\S]{0,2000}?)(?:DADOS FINANCEIROS|VALORES|PAGAMENTO|CORRETOR|$)"
                ],
                "nome": [
                    r"(?:Nome|Dependente)[:\s]+([A-ZÁÉÍÓÚ][A-Za-záéíóúàãõâêôç\s]+?)(?:\n|CPF|RG|Data|Parentesco)",
                ],
                "cpf": [
                    r"CPF[:\s]*(\d{3}\.?\d{3}\.?\d{3}-?\d{2})",
                    r"(\d{3}\.\d{3}\.\d{3}-\d{2})"
                ],
                "rg": [
                    r"RG[:\s]*(\d{1,2}\.?\d{3}\.?\d{3}-?[\dXx]?)"
                ],
                "data_nascimento": [
                    r"(?:Data de Nascimento|Nascimento|Nasc\.?)[:\s]*(\d{2}/\d{2}/\d{4})"
                ],
                "parentesco": [
                    r"(?:Parentesco|Grau)[:\s]+([^\n]+)",
                    r"(Cônjuge|Filho\(a\)|Filho|Filha|Esposo\(a\)|Esposa|Esposo|Companheiro\(a\)|Mãe|Pai)"
                ],
                "sexo": [
                    r"(?:Sexo|G[êe]nero)[:\s]*(Masculino|Feminino|Masc\.?|Fem\.?|M\b|F\b)",
                    r"\b(Masculino|Feminino)\b"
                ],
                "estado_civil": [
                    r"(?:Estado Civil|Est\.?\s*Civil|E\.?\s*Civil)[:\s]*([^\n,]{3,30})",
                    r"\b(Solteiro[a]?|Casado[a]?|Divorciado[a]?|Vi[úu]vo[a]?|Uni[ãa]o Est[áa]vel|Separado[a]?)\b"
                ]
            },
            "valores": {
                "valor_bruto": [
                    r"(?:Valor Bruto|Valor Total|Prêmio Bruto)[:\s]*R?\$?\s?([0-9]{1,3}(?:\.[0-9]{3})*(?:,\d{2})?)",
                    r"Valor da Apólice[:\s]*R?\$?\s?([0-9]{1,3}(?:\.[0-9]{3})*(?:,\d{2})?)",
                    r"Total[:\s]*R?\$?\s?([0-9]{1,3}(?:\.[0-9]{3})*(?:,\d{2})?)"
                ],
                "valor_liquido": [
                    r"(?:Valor Líquido|Líquido|Valor a Receber)[:\s]*R?\$?\s?([0-9]{1,3}(?:\.[0-9]{3})*(?:,\d{2})?)",
                    r"A Receber[:\s]*R?\$?\s?([0-9]{1,3}(?:\.[0-9]{3})*(?:,\d{2})?)"
                ],
                "comissao": [
                    r"(?:Comissão|Comissao)[:\s]*R?\$?\s?([0-9]{1,3}(?:\.[0-9]{3})*(?:,\d{2})?)",
                    r"Comissão[:\s]*(\d{1,2}(?:,\d{1,2})?)\s?%"
                ]
            },
            "impostos": {
                "iss": [
                    r"ISS[:\s]*R?\$?\s?([0-9]{1,3}(?:\.[0-9]{3})*(?:,\d{2})?)"
                ],
                "irpf": [
                    r"(?:IRPF|IR)[:\s]*R?\$?\s?([0-9]{1,3}(?:\.[0-9]{3})*(?:,\d{2})?)"
                ],
                "pis": [
                    r"PIS[:\s]*R?\$?\s?([0-9]{1,3}(?:\.[0-9]{3})*(?:,\d{2})?)"
                ],
                "cofins": [
                    r"COFINS[:\s]*R?\$?\s?([0-9]{1,3}(?:\.[0-9]{3})*(?:,\d{2})?)"
                ],
                "total": [
                    r"(?:Total de Impostos|Impostos Total)[:\s]*R?\$?\s?([0-9]{1,3}(?:\.[0-9]{3})*(?:,\d{2})?)"
                ]
            },
            "corretor": {
                "nome": [
                    r"(?:Corretor|Vendedor|Consultor)[:\s]+([A-ZÁÉÍÓÚ][A-Za-záéíóúàãõâêôç\s]+?)(?:\n|CPF|Código)",
                    r"Corretor Responsável[:\s]+([^\n]+)"
                ],
                "codigo": [
                    r"(?:Código do Corretor|Cód\. Corretor)[:\s]*(\d+)"
                ]
            },
            "datas": {
                "data_venda": [
                    r"(?:Data da Venda|Data de Emissão|Emissão)[:\s]*(\d{2}/\d{2}/\d{4})",
                    r"(\d{2}/\d{2}/\d{4})"
                ],
                "vigencia_inicio": [
                    r"(?:Início de Vigência|Vigência)[:\s]*(\d{2}/\d{2}/\d{4})"
                ],
                "vigencia_fim": [
                    r"(?:Fim de Vigência|Término)[:\s]*(\d{2}/\d{2}/\d{4})"
                ]
            },
            "comissao_extrato": {
                "corretor": [
                    r"(?:Corretor|Vendedor|Consultor|Produtor)[:\s]+([A-ZÁÉÍÓÚ][A-Za-záéíóúàãõâêôç\s]+?)(?:\n|CPF|C[oó]d|SUSEP|$)",
                    r"(?:Nome do Corretor|Corretor Responsável)[:\s]*([^\n]+)"
                ],
                "seguradora": [
                    r"(?:Seguradora|Operadora|Cia)[:\s]+([^\n]+)",
                    r"(SulAm[eé]rica|Porto Seguro|Bradesco|Amil|Unimed|Tokio Marine|Allianz|Hapvida|NotreDame|Intermédica|MetLife|Zurich|Liberty)"
                ],
                "valor_total": [
                    r"(?:Total a Receber|Total de Comiss[ãa]o|Valor Total|Total Bruto)[:\s]*R?\$?\s?([0-9]{1,3}(?:\.[0-9]{3})*(?:,\d{2})?)",
                    r"(?:Valor Bruto|Prêmio Bruto)[:\s]*R?\$?\s?([0-9]{1,3}(?:\.[0-9]{3})*(?:,\d{2})?)"
                ],
                "percentual_comissao": [
                    r"(?:Comiss[ãa]o|Percentual)[:\s]*(\d{1,2}(?:[,.]\d{1,2})?)\s?%",
                    r"(\d{1,2}(?:[,.]\d{1,2})?)\s?%\s*(?:de comiss[ãa]o|comiss[ãa]o)"
                ],
                "valor_comissao": [
                    r"(?:Comiss[ãa]o|Valor da Comiss[ãa]o)[:\s]*R?\$?\s?([0-9]{1,3}(?:\.[0-9]{3})*(?:,\d{2})?)",
                    r"(?:A Receber|Líquido)[:\s]*R?\$?\s?([0-9]{1,3}(?:\.[0-9]{3})*(?:,\d{2})?)"
                ],
                "competencia": [
                    r"(?:Compet[êe]ncia|Per[íi]odo|M[êe]s Refer[êe]ncia)[:\s]*([^\n]+)",
                    r"(?:Ref\.?)[:\s]*(\d{2}/\d{4})"
                ],
                "susep": [
                    r"(?:SUSEP|C[oó]d\.?\s*SUSEP)[:\s]*(\d[\d.\-/]+)",
                ]
            },
            "tipo_documento": {
                "proposta": [
                    r"PROPOSTA",
                    r"PROPOSTA DE SEGURO",
                    r"ADESÃO",
                    r"CONTRATO"
                ],
                "relatorio": [
                    r"RELATÓRIO DE PAGAMENTO",
                    r"RELATORIO DE COMISSÃO",
                    r"EXTRATO DE PAGAMENTO",
                    r"DEMONSTRATIVO"
                ]
            }
        }

        # Tentar carregar do arquivo, se não existir, usar padrão
        if Path(self.config_path).exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    custom_config = json.load(f)
                    # Merge com default
                    return {**default_config, **custom_config}
            except Exception as e:
                print(f"Erro ao carregar config: {e}. Usando padrão.")

        return default_config

    def salvar_configuracao(self):
        """Salva configuração atual em arquivo JSON"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.patterns, f, indent=2, ensure_ascii=False)

    def adicionar_pattern(self, categoria: str, campo: str, pattern: str):
        """Adiciona novo padrão de extração"""
        if categoria not in self.patterns:
            self.patterns[categoria] = {}
        if campo not in self.patterns[categoria]:
            self.patterns[categoria][campo] = []
        self.patterns[categoria][campo].append(pattern)
        self.salvar_configuracao()


class OCREngine:
    """Motor de extração de dados de PDFs"""

    def __init__(self, config_path: str = "ocr_config.json"):
        """
        Inicializa o motor OCR

        Args:
            config_path: Caminho para arquivo de configuração
        """
        self.config = OCRConfig(config_path)
        engine = criar_banco()
        self.session = obter_sessao(engine)
        self.finance_engine = FinanceEngine(session=self.session)

    def extrair_texto_pdf(self, file_path: str) -> str:
        """
        Extrai todo o texto de um PDF

        Args:
            file_path: Caminho do arquivo PDF

        Returns:
            str: Texto completo do PDF
        """
        texto_completo = ""

        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    texto = page.extract_text()
                    if texto:
                        texto_completo += texto + "\n"
        except Exception as e:
            raise Exception(f"Erro ao extrair texto do PDF: {e}")

        return texto_completo

    def extrair_com_patterns(self, texto: str, patterns: List[str]) -> Optional[str]:
        """
        Tenta extrair informação usando lista de padrões regex

        Args:
            texto: Texto para buscar
            patterns: Lista de padrões regex

        Returns:
            str ou None: Primeiro match encontrado ou None
        """
        for pattern in patterns:
            match = re.search(pattern, texto, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(1).strip()
        return None

    def converter_valor_brasileiro(self, valor_str: str) -> float:
        """
        Converte valor em formato brasileiro para float

        Args:
            valor_str: String como "1.234,56" ou "1234,56"

        Returns:
            float: Valor convertido
        """
        if not valor_str:
            return 0.0

        # Remove R$, espaços
        valor_limpo = valor_str.replace('R$', '').replace(' ', '').strip()

        # Substitui vírgula por ponto e remove pontos de milhar
        if ',' in valor_limpo:
            # Se tem vírgula, é formato brasileiro
            valor_limpo = valor_limpo.replace('.', '').replace(',', '.')

        try:
            return float(valor_limpo)
        except ValueError:
            return 0.0

    def identificar_tipo_documento(self, texto: str) -> str:
        """
        Identifica se é PROPOSTA ou RELATÓRIO

        Args:
            texto: Texto do documento

        Returns:
            str: 'PROPOSTA' ou 'RELATORIO'
        """
        patterns_proposta = self.config.patterns['tipo_documento']['proposta']
        patterns_relatorio = self.config.patterns['tipo_documento']['relatorio']

        # Verificar nas primeiras 500 caracteres
        inicio_texto = texto[:500].upper()

        for pattern in patterns_proposta:
            if re.search(pattern, inicio_texto):
                return 'PROPOSTA'

        for pattern in patterns_relatorio:
            if re.search(pattern, inicio_texto):
                return 'RELATORIO'

        # Se não identificar, tentar por palavras-chave
        if 'COMISSÃO' in inicio_texto or 'PAGAMENTO' in inicio_texto:
            return 'RELATORIO'

        return 'PROPOSTA'  # Padrão

    @staticmethod
    def _normalizar(texto: str) -> str:
        """Remove acentos, converte para minúsculas e remove espaços extras"""
        txt = unicodedata.normalize('NFKD', texto or "")
        txt = "".join(c for c in txt if not unicodedata.combining(c))
        return re.sub(r'\s+', ' ', txt).strip().lower()

    def _match_fuzzy(self, nome_extraido: str, lista_nomes: List[str],
                     tolerancia: float = 0.20) -> Optional[int]:
        """
        Retorna o índice do nome mais parecido com nome_extraido.
        tolerancia=0.20 → aceita até 20% de diferença (80% de similaridade).
        Retorna None se nenhum superar o limiar.
        """
        if not nome_extraido:
            return None
        alvo = self._normalizar(nome_extraido)
        melhor_idx = None
        melhor_ratio = 0.0
        for i, nome in enumerate(lista_nomes):
            ratio = difflib.SequenceMatcher(None, alvo, self._normalizar(nome)).ratio()
            if ratio > melhor_ratio:
                melhor_ratio = ratio
                melhor_idx = i
        if melhor_ratio >= (1.0 - tolerancia):
            return melhor_idx
        return None

    def buscar_corretor_fuzzy(self, nome_extraido: str, tolerancia: float = 0.20):
        """
        Busca corretor no banco por similaridade de nome (tolerância de 20%).
        Retorna objeto Corretor ou None.
        """
        from database import Corretor
        corretores = self.session.query(Corretor).all()
        if not corretores or not nome_extraido:
            return None
        nomes = [c.nome for c in corretores]
        idx = self._match_fuzzy(nome_extraido, nomes, tolerancia)
        if idx is not None:
            return corretores[idx]
        return None

    def buscar_seguradora_fuzzy(self, nome_extraido: str, tolerancia: float = 0.20):
        """
        Busca seguradora no banco por similaridade de nome (tolerância de 20%).
        Retorna objeto Seguradora ou None.
        """
        from database import Seguradora
        seguradoras = self.session.query(Seguradora).all()
        if not seguradoras or not nome_extraido:
            return None
        nomes = [s.nome for s in seguradoras]
        idx = self._match_fuzzy(nome_extraido, nomes, tolerancia)
        if idx is not None:
            return seguradoras[idx]
        return None

    def extrair_dependentes(self, texto: str) -> List[Dict]:
        """
        Extrai dados de dependentes do texto do PDF.
        Tenta localizar um bloco de dependentes e parsear cada um.
        """
        dependentes = []
        patterns = self.config.patterns

        # Tentar localizar bloco dedicado a dependentes
        bloco_match = None
        for pat in patterns['dependentes']['bloco']:
            m = re.search(pat, texto, re.IGNORECASE | re.DOTALL)
            if m:
                bloco_match = m.group(1) if m.lastindex else m.group(0)
                break

        # Se não encontrou bloco, usar texto todo mas limitado
        bloco = bloco_match if bloco_match else ""

        if not bloco.strip():
            return dependentes

        # Dividir por linhas e tentar extrair entradas de dependentes
        # Cada dependente geralmente começa com "Nome:" ou é precedido por número
        # Estratégia: encontrar todos os nomes dentro do bloco
        nomes_matches = list(re.finditer(
            r"(?:Nome|Dependente\s*\d*)[:\s]+([A-ZÁÉÍÓÚ][A-Za-záéíóúàãõâêôç\s]{2,50})(?:\n|CPF|RG|$)",
            bloco, re.IGNORECASE
        ))

        if not nomes_matches:
            # Tentar padrão mais simples: linhas com nomes maiúsculos após "Dependente X"
            nomes_matches = list(re.finditer(
                r"Dependente\s*\d+[:\s]*([A-ZÁÉÍÓÚ][A-Za-záéíóúàãõâêôç\s]{2,50})",
                bloco, re.IGNORECASE
            ))

        for i, nome_m in enumerate(nomes_matches):
            nome = nome_m.group(1).strip()
            if not nome or len(nome) < 3:
                continue

            # Pegar contexto ao redor do nome (próximas 300 chars)
            inicio = nome_m.end()
            proximo = nomes_matches[i+1].start() if i+1 < len(nomes_matches) else inicio + 300
            contexto = bloco[inicio:min(proximo, inicio + 400)]

            dep = {
                'nome': nome, 'cpf': None, 'rg': None,
                'data_nascimento': None, 'parentesco': None,
                'sexo': None, 'estado_civil': None,
            }

            # Buscar CPF no contexto — com ou sem prefixo "CPF:"
            cpf_m = re.search(
                r"(?:CPF[:\s]*)?(\d{3}\.\d{3}\.\d{3}-\d{2})",
                contexto, re.IGNORECASE
            )
            if cpf_m:
                dep['cpf'] = cpf_m.group(1)

            rg_m = re.search(r"RG[:\s]*(\d[\d.\-/Xx]+)", contexto, re.IGNORECASE)
            if rg_m:
                dep['rg'] = rg_m.group(1)

            nasc_m = re.search(r"(?:Nasc|Nascimento)[.:\s]*(\d{2}/\d{2}/\d{4})", contexto, re.IGNORECASE)
            if nasc_m:
                try:
                    dep['data_nascimento'] = datetime.strptime(nasc_m.group(1), '%d/%m/%Y').date()
                except Exception:
                    pass

            par_m = re.search(
                r"(?:Parentesco|Grau)[:\s]*([^\n,]+)|"
                r"(Cônjuge|Filho[a]?|Filha|Esposo[a]?|Companheiro[a]?|Mãe|Pai)",
                contexto, re.IGNORECASE
            )
            if par_m:
                dep['parentesco'] = (par_m.group(1) or par_m.group(2) or "").strip()

            # Sexo
            for pat in self.config.patterns['dependentes']['sexo']:
                sm = re.search(pat, contexto, re.IGNORECASE)
                if sm:
                    raw = sm.group(1).strip()
                    # Normalizar
                    if raw.upper() in ('M', 'MASC', 'MASCULINO'):
                        dep['sexo'] = 'Masculino'
                    elif raw.upper() in ('F', 'FEM', 'FEMININO'):
                        dep['sexo'] = 'Feminino'
                    else:
                        dep['sexo'] = raw.capitalize()
                    break

            # Estado Civil
            for pat in self.config.patterns['dependentes']['estado_civil']:
                ecm = re.search(pat, contexto, re.IGNORECASE)
                if ecm:
                    dep['estado_civil'] = ecm.group(1).strip().capitalize()
                    break

            dependentes.append(dep)

        return dependentes

    def extrair_dados_proposta(self, texto: str) -> Dict:
        """
        Extrai dados de uma proposta de seguro

        Args:
            texto: Texto do PDF

        Returns:
            dict: Dados extraídos
        """
        dados = {
            'cliente_nome': None,
            'cpf_cnpj': None,
            'rg': None,
            'data_nascimento': None,
            'telefone': None,
            'email': None,
            'seguradora_nome': None,
            'produto': None,
            'tipo_plano': None,
            'valor_bruto': 0.0,
            'valor_liquido': 0.0,
            'comissao': None,
            'corretor_nome': None,
            'corretor_codigo': None,
            'data_venda': None,
            'dependentes': [],
            'impostos': {
                'iss': 0.0,
                'irpf': 0.0,
                'pis': 0.0,
                'cofins': 0.0,
                'total': 0.0
            }
        }

        patterns = self.config.patterns

        # Cliente — dados cadastrais
        dados['cliente_nome'] = self.extrair_com_patterns(texto, patterns['cliente']['nome'])
        dados['cpf_cnpj'] = self.extrair_com_patterns(texto, patterns['cliente']['cpf_cnpj'])
        dados['rg'] = self.extrair_com_patterns(texto, patterns['cliente']['rg'])
        dados['telefone'] = self.extrair_com_patterns(texto, patterns['cliente']['telefone'])
        dados['email'] = self.extrair_com_patterns(texto, patterns['cliente']['email'])

        # Data de nascimento
        nasc_str = self.extrair_com_patterns(texto, patterns['cliente']['data_nascimento'])
        if nasc_str:
            try:
                dados['data_nascimento'] = datetime.strptime(nasc_str, '%d/%m/%Y').date()
            except Exception:
                pass

        # Seguradora / Plano
        dados['seguradora_nome'] = self.extrair_com_patterns(texto, patterns['seguradora']['nome'])
        produto = self.extrair_com_patterns(texto, patterns['seguradora']['produto'])
        dados['produto'] = produto
        dados['tipo_plano'] = produto  # mesmo campo, alias

        # Valores
        valor_bruto_str = self.extrair_com_patterns(texto, patterns['valores']['valor_bruto'])
        dados['valor_bruto'] = self.converter_valor_brasileiro(valor_bruto_str)

        valor_liquido_str = self.extrair_com_patterns(texto, patterns['valores']['valor_liquido'])
        dados['valor_liquido'] = self.converter_valor_brasileiro(valor_liquido_str)

        dados['comissao'] = self.extrair_com_patterns(texto, patterns['valores']['comissao'])

        # Impostos
        iss_str = self.extrair_com_patterns(texto, patterns['impostos']['iss'])
        dados['impostos']['iss'] = self.converter_valor_brasileiro(iss_str)

        irpf_str = self.extrair_com_patterns(texto, patterns['impostos']['irpf'])
        dados['impostos']['irpf'] = self.converter_valor_brasileiro(irpf_str)

        pis_str = self.extrair_com_patterns(texto, patterns['impostos']['pis'])
        dados['impostos']['pis'] = self.converter_valor_brasileiro(pis_str)

        cofins_str = self.extrair_com_patterns(texto, patterns['impostos']['cofins'])
        dados['impostos']['cofins'] = self.converter_valor_brasileiro(cofins_str)

        total_imp_str = self.extrair_com_patterns(texto, patterns['impostos']['total'])
        dados['impostos']['total'] = self.converter_valor_brasileiro(total_imp_str)

        # Corretor
        dados['corretor_nome'] = self.extrair_com_patterns(texto, patterns['corretor']['nome'])
        dados['corretor_codigo'] = self.extrair_com_patterns(texto, patterns['corretor']['codigo'])

        # Datas
        data_venda_str = self.extrair_com_patterns(texto, patterns['datas']['data_venda'])
        if data_venda_str:
            try:
                dados['data_venda'] = datetime.strptime(data_venda_str, '%d/%m/%Y').date()
            except Exception:
                dados['data_venda'] = datetime.now().date()
        else:
            dados['data_venda'] = datetime.now().date()

        # Dependentes
        dados['dependentes'] = self.extrair_dependentes(texto)

        return dados

    def salvar_proposta_no_banco(self, dados: Dict) -> Tuple[bool, str]:
        """
        Salva proposta extraída no banco de dados

        Args:
            dados: Dicionário com dados da proposta

        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        """
        try:
            # Buscar seguradora com fuzzy matching
            seguradora = self.buscar_seguradora_fuzzy(dados.get('seguradora_nome'), tolerancia=0.20)
            if not seguradora and dados.get('seguradora_nome'):
                seguradora = Seguradora(
                    nome=dados['seguradora_nome'],
                    regra_pagamento_dias="30",
                    vitalicio_porcentagem=5.0
                )
                self.session.add(seguradora)
                self.session.commit()

            # Buscar corretor com fuzzy matching
            corretor = self.buscar_corretor_fuzzy(dados.get('corretor_nome'), tolerancia=0.20)
            if not corretor and dados.get('corretor_nome'):
                corretor = Corretor(
                    nome=dados['corretor_nome'],
                    comissao_padrao=10.0
                )
                self.session.add(corretor)
                self.session.commit()

            if not seguradora or not corretor:
                return False, "Seguradora ou Corretor não encontrados e não foi possível criar"

            # Criar proposta com todos os campos cadastrais
            proposta = Proposta(
                cliente_nome=dados['cliente_nome'] or "Cliente Desconhecido",
                cliente_cpf=dados.get('cpf_cnpj'),
                cliente_rg=dados.get('rg'),
                cliente_data_nascimento=dados.get('data_nascimento'),
                cliente_telefone=dados.get('telefone'),
                cliente_email=dados.get('email'),
                tipo_plano=dados.get('tipo_plano'),
                valor_bruto=dados['valor_bruto'],
                seguradora_id=seguradora.id,
                corretor_id=corretor.id,
                data_venda=dados['data_venda']
            )
            self.session.add(proposta)
            self.session.commit()

            # Salvar dependentes
            for dep_dados in dados.get('dependentes', []):
                dep = Dependente(
                    proposta_id=proposta.id,
                    nome=dep_dados['nome'],
                    cpf=dep_dados.get('cpf'),
                    rg=dep_dados.get('rg'),
                    data_nascimento=dep_dados.get('data_nascimento'),
                    parentesco=dep_dados.get('parentesco'),
                    sexo=dep_dados.get('sexo'),
                    estado_civil=dep_dados.get('estado_civil'),
                )
                self.session.add(dep)
            self.session.commit()

            # Gerar lançamentos automáticos
            self.finance_engine.gerar_lancamentos(proposta)

            ndeps = len(dados.get('dependentes', []))
            msg = f"Proposta #{proposta.id} salva com sucesso!"
            if ndeps:
                msg += f" ({ndeps} dependente(s) incluído(s))"
            return True, msg

        except Exception as e:
            self.session.rollback()
            return False, f"Erro ao salvar proposta: {e}"

    def extrair_dados_comissao(self, texto: str) -> Dict:
        """
        Extrai dados especializados de um extrato/relatório de comissões.
        Usa fuzzy matching (20% tolerância) para identificar corretor e seguradora.
        """
        patterns = self.config.patterns
        c_pat = patterns.get('comissao_extrato', {})

        dados = {
            'corretor_nome': None,
            'corretor_id': None,
            'seguradora_nome': None,
            'seguradora_id': None,
            'valor_bruto': 0.0,
            'comissao': None,
            'valor_comissao': 0.0,
            'competencia': None,
            'susep': None,
            'data_venda': None,
            'descricao': None,
        }

        # Extrair campos textuais
        dados['corretor_nome']  = self.extrair_com_patterns(texto, c_pat.get('corretor', []))
        dados['seguradora_nome'] = self.extrair_com_patterns(texto, c_pat.get('seguradora', []))
        dados['competencia']    = self.extrair_com_patterns(texto, c_pat.get('competencia', []))
        dados['susep']          = self.extrair_com_patterns(texto, c_pat.get('susep', []))

        # Percentual de comissão
        dados['comissao'] = self.extrair_com_patterns(texto, c_pat.get('percentual_comissao', []))

        # Valores
        v_total = self.extrair_com_patterns(texto, c_pat.get('valor_total', []))
        dados['valor_bruto'] = self.converter_valor_brasileiro(v_total)

        v_com = self.extrair_com_patterns(texto, c_pat.get('valor_comissao', []))
        dados['valor_comissao'] = self.converter_valor_brasileiro(v_com)

        # Se não extraiu valor bruto, tenta valor_bruto genérico
        if not dados['valor_bruto']:
            v_gen = self.extrair_com_patterns(texto, patterns['valores']['valor_bruto'])
            dados['valor_bruto'] = self.converter_valor_brasileiro(v_gen)

        # Data de referência
        data_str = self.extrair_com_patterns(texto, patterns['datas']['data_venda'])
        if data_str:
            try:
                dados['data_venda'] = datetime.strptime(data_str, '%d/%m/%Y').date()
            except Exception:
                dados['data_venda'] = datetime.now().date()
        else:
            dados['data_venda'] = datetime.now().date()

        # Fuzzy matching — corretor
        corretor_obj = self.buscar_corretor_fuzzy(dados['corretor_nome'])
        if corretor_obj:
            dados['corretor_id'] = corretor_obj.id
            dados['corretor_nome_banco'] = corretor_obj.nome  # nome conforme cadastro

        # Fuzzy matching — seguradora
        seg_obj = self.buscar_seguradora_fuzzy(dados['seguradora_nome'])
        if seg_obj:
            dados['seguradora_id'] = seg_obj.id
            dados['seguradora_nome_banco'] = seg_obj.nome

        # Descrição automática
        partes = []
        if dados['corretor_nome']:
            partes.append(f"Corretor: {dados.get('corretor_nome_banco') or dados['corretor_nome']}")
        if dados['seguradora_nome']:
            partes.append(f"Seg: {dados.get('seguradora_nome_banco') or dados['seguradora_nome']}")
        if dados['competencia']:
            partes.append(f"Ref: {dados['competencia']}")
        dados['descricao'] = " | ".join(partes) if partes else "Comissão importada via PDF"

        return dados

    def detectar_formato(self, texto: str) -> str:
        """Detecta o formato do extrato: 'ALLCARE', 'GENERICO', etc."""
        txt_upper = texto[:600].upper()
        if 'ALLCARE' in txt_upper and 'NUMERO EXTRATO' in txt_upper.replace('Ú','U').replace('É','E'):
            return 'ALLCARE'
        if 'ALLCARE' in txt_upper:
            return 'ALLCARE'
        return 'GENERICO'

    def extrair_dados_allcare(self, texto: str) -> Dict:
        """
        Parser especializado para extratos da Allcare Benefícios.
        Extrai cabeçalho, resumo financeiro, dados bancários e todos os itens de contrato.
        """
        # ── Helpers internos ──────────────────────────────────────────────────
        def _val(s):
            return self.converter_valor_brasileiro(s)

        def _data(s):
            if not s:
                return None
            s = s.strip()
            for fmt in ('%d/%m/%Y', '%Y-%m-%d'):
                try:
                    return datetime.strptime(s, fmt).date()
                except Exception:
                    pass
            return None

        def _tipo_pessoa(nome):
            pj_keywords = ('LTDA', ' ME ', ' SA ', ' S.A', ' S/A', ' EPP', ' EIRELI',
                           'COMERCIO', 'INDUSTRIA', 'SERVICOS', 'TRANSPORTES', 'LOGISTICA',
                           'MENTORIAS', 'FESTAS', 'AGENCIA', 'CONSTRUTORA', 'TEOMAQ')
            nome_up = nome.upper()
            for kw in pj_keywords:
                if kw in nome_up:
                    return 'Pessoa Jurídica'
            # Heurística: ≥3 palavras todas em caps = PJ
            partes = nome_up.split()
            if len(partes) >= 3 and all(p.isupper() for p in partes):
                # Mas pode ser nome completo de pessoa física
                # Se alguma palavra é substantivo típico de empresa → PJ
                pass
            return 'Pessoa Física'

        # ── Cabeçalho ─────────────────────────────────────────────────────────
        dados = {
            'formato': 'ALLCARE',
            'corretora': None,
            'cnpj_corretora': None,
            'filial': None,
            'produtor_codigo': None,
            'produtor_nome': None,
            'cnpj_produtor': None,
            'periodo_inicio': None,
            'periodo_fim': None,
            'numero_extrato': None,
            'nota_fiscal': None,
            # Quadro resumo
            'valor_apurado': 0.0,
            'valor_tx_implantacao': 0.0,
            'valor_estorno': 0.0,
            'valor_ajustes': 0.0,
            'valor_para_nf': 0.0,
            'aliquota_irrf': 0.0,
            'valor_irrf': 0.0,
            'aliquota_iss': 0.0,
            'valor_iss': 0.0,
            'valor_liquido': 0.0,
            # Pagamento
            'forma_pagamento': None,
            'banco': None,
            'agencia': None,
            'conta': None,
            'data_pagamento_previsto': None,
            'data_pagamento_efetivo': None,
            'status_financeiro': 'PENDENTE',
            # Itens
            'itens': [],
        }

        # Corretora + filial
        m = re.search(r'Corretora:\s*(.+?)(?:Filial Fiscal|CNPJ)', texto, re.IGNORECASE)
        if m:
            dados['corretora'] = m.group(1).strip()

        m = re.search(r'Filial(?:\s+Fiscal)?[:\s]+[^\-]+\-\s*([^\n]+?)(?:Filial:|Unidade:|$)', texto, re.IGNORECASE)
        if m:
            dados['filial'] = m.group(1).strip()

        # CNPJ da corretora (rodapé)
        m = re.search(r'Allcare[^\n]+CNPJ[:\s]*([\d./\-]+)', texto, re.IGNORECASE)
        if m:
            dados['cnpj_corretora'] = m.group(1).strip()

        # Produtor
        m = re.search(r'Produtor[:\s]*(\d+)\s*[-–]\s*([^\n]+?)(?:CNPJ|$)', texto, re.IGNORECASE)
        if m:
            dados['produtor_codigo'] = m.group(1).strip()
            dados['produtor_nome']   = m.group(2).strip()

        m = re.search(r'CNPJ[:\s]*([\d]{2}\.[\d]{3}\.[\d]{3}/[\d]{4}-[\d]{2})', texto)
        if m:
            dados['cnpj_produtor'] = m.group(1).strip()

        # Período
        m = re.search(r'Per[íi]odo de apura[çc][aã]o[:\s]*(\d{2}/\d{2}/\d{4})\s*at[ée]\s*(\d{2}/\d{2}/\d{4})',
                      texto, re.IGNORECASE)
        if m:
            dados['periodo_inicio'] = _data(m.group(1))
            dados['periodo_fim']    = _data(m.group(2))

        # Número extrato
        m = re.search(r'N[úu]mero extrato[:\s]*(\d+)', texto, re.IGNORECASE)
        if m:
            dados['numero_extrato'] = m.group(1).strip()

        # Nota fiscal
        m = re.search(r'Nota fiscal[:\s]*([^\n\s]+)', texto, re.IGNORECASE)
        if m:
            val = m.group(1).strip()
            dados['nota_fiscal'] = None if val in ('-', '', 'null') else val

        # ── Quadro financeiro ─────────────────────────────────────────────────
        def _extract_val(label):
            m = re.search(label + r'[:\s]*([\d.,]+)', texto, re.IGNORECASE)
            return _val(m.group(1)) if m else 0.0

        dados['valor_apurado']        = _extract_val(r'Valor Apurado')
        dados['valor_tx_implantacao'] = _extract_val(r'Valor Tx\. Implanta[çc][aã]o')
        dados['valor_estorno']        = _extract_val(r'Valor Estorno')
        dados['valor_ajustes']        = _extract_val(r'Valor Ajustes\b')
        dados['valor_para_nf']        = _extract_val(r'Valor para Emiss[aã]o de NF')
        dados['aliquota_irrf']        = _extract_val(r'Al[íi]quota IRRF')
        dados['valor_irrf']           = _extract_val(r'Valor IRRF')
        dados['aliquota_iss']         = _extract_val(r'Al[íi]quota ISS')
        dados['valor_iss']            = _extract_val(r'Valor ISS')

        m = re.search(r'Valor L[íi]quido a Receber\s+([\d.,]+)', texto, re.IGNORECASE)
        if m:
            dados['valor_liquido'] = _val(m.group(1))

        # ── Dados bancários ───────────────────────────────────────────────────
        m = re.search(r'Forma de pagamento[:\s]*([^\n]+?)Banco[:\s]*(\d+)', texto, re.IGNORECASE)
        if m:
            dados['forma_pagamento'] = m.group(1).strip()
            dados['banco']           = m.group(2).strip()

        m = re.search(r'Ag[êe]ncia[:\s]*([\d]+)', texto, re.IGNORECASE)
        if m:
            dados['agencia'] = m.group(1).strip()

        m = re.search(r'Conta[:\s]*([\d\-]+)', texto, re.IGNORECASE)
        if m:
            dados['conta'] = m.group(1).strip()

        m = re.search(r'Data pagamento previsto[:\s]*(\d{2}/\d{2}/\d{4})', texto, re.IGNORECASE)
        if m:
            dados['data_pagamento_previsto'] = _data(m.group(1))
            hoje = datetime.now().date()
            dados['status_financeiro'] = (
                'RECEBIDO' if dados['data_pagamento_previsto'] <= hoje else 'PENDENTE'
            )

        m = re.search(r'Data pagamento efetivo[:\s]*(\d{2}/\d{2}/\d{4})', texto, re.IGNORECASE)
        if m:
            dados['data_pagamento_efetivo'] = _data(m.group(1))

        # ── Itens de contrato ─────────────────────────────────────────────────
        # Divide por blocos "Contrato: XXXXX - NOME"
        blocos = re.split(
            r'(?=Contrato[:\s]+\d+\s*[-–])',
            texto,
            flags=re.IGNORECASE,
        )

        porte_atual = 'PME'  # default, atualizado quando encontrado

        for bloco in blocos:
            if not re.search(r'Contrato[:\s]+\d+', bloco, re.IGNORECASE):
                # Verificar se há linha de porte antes dos contratos
                mp = re.search(r'Porte do contrato[:\s]*(\w+)', bloco, re.IGNORECASE)
                if mp:
                    porte_atual = mp.group(1).strip().upper()
                continue

            # Porte do contrato (pode estar antes do bloco ou no início)
            mp = re.search(r'Porte do contrato[:\s]*(\w+)', bloco, re.IGNORECASE)
            if mp:
                porte_atual = mp.group(1).strip().upper()

            # Número e nome do contrato
            mc = re.search(r'Contrato[:\s]+(\d+)\s*[-–]\s*(.+?)(?:Operadora|$)',
                           bloco, re.IGNORECASE)
            if not mc:
                continue
            num_contrato  = mc.group(1).strip()
            nome_cliente  = mc.group(2).strip()

            # Operadora
            mo = re.search(r'Operadora[:\s]+([^\n]+?)(?:Data in[íi]cio|$)', bloco, re.IGNORECASE)
            operadora = mo.group(1).strip() if mo else None

            # Data início vigência
            mv = re.search(r'Data in[íi]cio vig[êe]ncia[:\s]*(\d{2}/\d{2}/\d{4})', bloco, re.IGNORECASE)
            data_vigencia = _data(mv.group(1)) if mv else None

            # Linhas de fatura — cada linha de item tem o padrão:
            # FATURA PROPOSTA PARCELA REFERENCIA VALOR_FATURA PRODUTO VIDAS VENCIMENTO DATA_OP FUNCAO RUBRICA % BASE COMISSAO
            # Usamos regex de captura linha a linha
            item_pattern = re.compile(
                r'(\d{8})\s+'               # fatura (8 dígitos)
                r'(\d{11,12})\s+'           # proposta/beneficiário
                r'(\d+)\s+'                 # parcela
                r'(\d{2}/\d{4})\s+'         # referência MM/AAAA
                r'([\d.,]+)'                # valor fatura
                r'(\w[^\d]+?)\s+'           # produto
                r'(\d+)\s+'                 # vidas
                r'(\d{2}/\d{2}/\d{4})\s+'  # vencimento
                r'(\d{2}/\d{2}/\d{4})\s+'  # data operação
                r'([^\s]+(?:\s+[^\s]+)?)\s+' # função venda
                r'(Comiss[aã]o|Vit[aá]l[íi]cio[^C]*Comiss[aã]o|Comiss[aã]o)\s+'
                r'([\d.,]+)\s+'             # percentual
                r'([\d.,]+)\s+'             # base cálculo
                r'([\d.,]+)',               # comissão
                re.IGNORECASE,
            )

            for item_m in item_pattern.finditer(bloco):
                produto_raw = item_m.group(6).strip()
                funcao_raw  = item_m.group(10).strip()
                rubrica_raw = item_m.group(11).strip()

                # Limpar produto (pode ter texto colado)
                produto = re.sub(r'\s+', ' ', produto_raw).strip()
                if len(produto) > 30:
                    produto = produto[:30].strip()

                dados['itens'].append({
                    'pagina':               None,   # preenchido abaixo
                    'porte_contrato':       porte_atual,
                    'numero_contrato':      num_contrato,
                    'nome_cliente':         nome_cliente,
                    'tipo_pessoa':          _tipo_pessoa(nome_cliente),
                    'operadora':            operadora,
                    'data_inicio_vigencia': data_vigencia,
                    'numero_fatura':        item_m.group(1),
                    'id_beneficiario':      item_m.group(2),
                    'parcela':              int(item_m.group(3)),
                    'referencia':           item_m.group(4),
                    'valor_fatura':         _val(item_m.group(5)),
                    'produto':              produto,
                    'vidas':                int(item_m.group(7)),
                    'vencimento':           _data(item_m.group(8)),
                    'data_operacao':        _data(item_m.group(9)),
                    'funcao_venda':         funcao_raw,
                    'rubrica':              rubrica_raw,
                    'percentual_comissao':  _val(item_m.group(12)),
                    'base_calculo':         _val(item_m.group(13)),
                    'valor_comissao':       _val(item_m.group(14)),
                })

        # Numeração de página simplificada (primeiros 3 → pg1, demais → pg2)
        for i, item in enumerate(dados['itens']):
            item['pagina'] = 1 if i < 3 else 2

        # Validação
        soma = round(sum(i['valor_comissao'] for i in dados['itens']), 2)
        dados['validacao'] = {
            'soma_comissoes':    soma,
            'valor_apurado':     dados['valor_apurado'],
            'divergencia':       round(abs(soma - dados['valor_apurado']), 2),
            'status':            'OK' if abs(soma - dados['valor_apurado']) < 0.02 else 'DIVERGENTE',
        }

        # Fuzzy matching produtor → corretor
        corretor_obj = self.buscar_corretor_fuzzy(dados.get('produtor_nome'), tolerancia=0.30)
        if corretor_obj:
            dados['corretor_id']          = corretor_obj.id
            dados['corretor_nome_banco']  = corretor_obj.nome

        return dados

    def processar_relatorio_pagamento(self, dados: Dict) -> Dict:
        """
        Processa relatório de pagamento (função para auditoria futura)

        Args:
            dados: Dados extraídos do relatório

        Returns:
            dict: Resultado do processamento
        """
        # Placeholder para função de auditoria
        return {
            'tipo': 'RELATORIO',
            'dados': dados,
            'status': 'AGUARDANDO_AUDITORIA',
            'mensagem': 'Relatório processado. Auditoria pendente.'
        }

    def processar_documento(self, file_path: str) -> Dict:
        """
        Função principal: processa documento PDF

        Args:
            file_path: Caminho do arquivo PDF

        Returns:
            dict: Resultado do processamento
        """
        resultado = {
            'sucesso': False,
            'tipo_documento': None,
            'dados_extraidos': {},
            'mensagem': '',
            'arquivo': file_path
        }

        try:
            # Extrair texto
            print(f"Extraindo texto de: {file_path}")
            texto = self.extrair_texto_pdf(file_path)

            if not texto or len(texto) < 50:
                resultado['mensagem'] = "PDF vazio ou com muito pouco texto"
                return resultado

            # Identificar tipo
            tipo = self.identificar_tipo_documento(texto)
            resultado['tipo_documento'] = tipo

            print(f"Tipo identificado: {tipo}")

            # Processar conforme tipo
            if tipo == 'PROPOSTA':
                dados = self.extrair_dados_proposta(texto)
                resultado['dados_extraidos'] = dados

                print(f"Dados extraídos: Cliente={dados['cliente_nome']}, Valor={dados['valor_bruto']}")

                # Salvar no banco
                sucesso, mensagem = self.salvar_proposta_no_banco(dados)
                resultado['sucesso'] = sucesso
                resultado['mensagem'] = mensagem

            elif tipo == 'RELATORIO':
                dados = self.extrair_dados_proposta(texto)  # Mesma função por enquanto
                resultado['dados_extraidos'] = dados

                # Enviar para auditoria (função futura)
                audit_result = self.processar_relatorio_pagamento(dados)
                resultado['sucesso'] = True
                resultado['mensagem'] = audit_result['mensagem']
                resultado['auditoria'] = audit_result

            return resultado

        except Exception as e:
            resultado['mensagem'] = f"Erro ao processar documento: {e}"
            return resultado

    def fechar(self):
        """Fecha conexão com banco"""
        self.session.close()


# Funções auxiliares
def processar_pdf(file_path: str) -> Dict:
    """
    Função auxiliar para processar PDF

    Args:
        file_path: Caminho do arquivo

    Returns:
        dict: Resultado do processamento
    """
    ocr = OCREngine()
    resultado = ocr.processar_documento(file_path)
    ocr.fechar()
    return resultado


if __name__ == '__main__':
    # Teste do OCR Engine
    print("=== Teste do OCR Engine ===\n")

    # Criar arquivo de configuração de exemplo
    config = OCRConfig()
    config.salvar_configuracao()
    print("[OK] Arquivo de configuração criado: ocr_config.json")

    # Exemplo de uso
    print("\nExemplo de uso:")
    print("  from ocr_engine import processar_pdf")
    print("  resultado = processar_pdf('proposta.pdf')")
    print("  print(resultado)")

    print("\nPadrões configurados:")
    print(f"  - Cliente: {len(config.patterns['cliente'])} campos")
    print(f"  - Seguradora: {len(config.patterns['seguradora'])} campos")
    print(f"  - Valores: {len(config.patterns['valores'])} campos")
    print(f"  - Impostos: {len(config.patterns['impostos'])} campos")
    print(f"  - Corretor: {len(config.patterns['corretor'])} campos")

    print("\n[OK] OCR Engine pronto para uso!")
