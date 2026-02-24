"""
Sistema Avançado de Exportação de PDF com Cruzamento de Dados
Cruza automaticamente propostas, lançamentos e parcelas do corretor
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from datetime import datetime
import os
from database import criar_banco, obter_sessao, Proposta, Lancamento, Corretor
from sistema_parcelas import Parcela, GerenciadorParcelas


class PDFExporterAvancado:
    """Exportador avançado de relatórios em PDF com cruzamento automático"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.create_custom_styles()

    def create_custom_styles(self):
        """Cria estilos customizados"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#6366f1'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1e293b'),
            spaceAfter=10,
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='Alert',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#ef4444'),
            fontName='Helvetica-Bold'
        ))

    def gerar_relatorio_comissoes_completo(self, corretor_id: int, output_path=None):
        """
        Gera PDF completo com cruzamento automático de dados

        Args:
            corretor_id: ID do corretor
            output_path: Caminho para salvar o PDF

        Returns:
            str: Caminho do arquivo PDF gerado
        """
        print(f"[PDF] Gerando relatório completo para corretor {corretor_id}")

        # Conectar ao banco
        engine = criar_banco()
        session = obter_sessao(engine)

        # Buscar corretor
        corretor = session.query(Corretor).get(corretor_id)
        if not corretor:
            print(f"[PDF] Corretor {corretor_id} não encontrado")
            return None

        # Buscar todas as propostas do corretor
        propostas = session.query(Proposta).filter_by(corretor_id=corretor_id).all()

        # Buscar todos os lançamentos
        lancamentos = session.query(Lancamento).join(Proposta).filter(
            Proposta.corretor_id == corretor_id
        ).all()

        # Buscar todas as parcelas
        parcelas = session.query(Parcela).filter_by(corretor_id=corretor_id).all()

        print(f"[PDF] Encontradas: {len(propostas)} propostas, {len(lancamentos)} lançamentos, {len(parcelas)} parcelas")

        # Definir caminho do arquivo
        if not output_path:
            filename = f"comissoes_{corretor.nome.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            output_path = os.path.join(os.getcwd(), filename)

        # Criar documento
        doc = SimpleDocTemplate(output_path, pagesize=A4,
                              leftMargin=0.5*inch, rightMargin=0.5*inch,
                              topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []

        # ===== CABEÇALHO =====
        title = Paragraph("<b>RELATÓRIO COMPLETO DE COMISSÕES</b>", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.2*inch))

        # ===== INFORMAÇÕES DO CORRETOR =====
        info_data = [
            ['<b>Corretor:</b>', corretor.nome],
            ['<b>Email:</b>', corretor.email or 'N/A'],
            ['<b>Telefone:</b>', corretor.telefone or 'N/A'],
            ['<b>Comissão Padrão:</b>', f"{corretor.comissao_padrao}%"],
            ['<b>Data de Emissão:</b>', datetime.now().strftime('%d/%m/%Y às %H:%M')],
        ]

        info_table = Table(info_data, colWidths=[1.5*inch, 5*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))

        story.append(info_table)
        story.append(Spacer(1, 0.3*inch))

        # ===== RESUMO GERAL =====
        heading = Paragraph("<b>📊 RESUMO GERAL</b>", self.styles['CustomHeading'])
        story.append(heading)

        # Calcular totais
        total_bruto = sum(p.valor_bruto for p in propostas)
        total_comissao = sum(l.valor_esperado for l in lancamentos)
        total_liquido = sum(l.valor_esperado for l in lancamentos)  # Valor esperado já é líquido

        # Totais de parcelas
        parcelas_quitadas = [p for p in parcelas if p.status == 'QUITADA']
        parcelas_pendentes = [p for p in parcelas if p.status in ['PENDENTE', 'VENCIDA', 'NOTIFICADA']]
        parcelas_vencidas = [p for p in parcelas if p.status in ['VENCIDA', 'NOTIFICADA']]

        total_quitado = sum(p.valor for p in parcelas_quitadas)
        total_pendente = sum(p.valor for p in parcelas_pendentes)
        total_vencido = sum(p.valor for p in parcelas_vencidas)

        resumo_data = [
            ['<b>Descrição</b>', '<b>Valor</b>'],
            ['Total Bruto de Vendas', f"R$ {total_bruto:,.2f}"],
            ['Total de Comissões', f"R$ {total_comissao:,.2f}"],
            ['Total Líquido', f"R$ {total_liquido:,.2f}"],
            ['', ''],
            ['<b>Parcelas Quitadas</b>', f"R$ {total_quitado:,.2f}"],
            ['<b>Parcelas Pendentes</b>', f"R$ {total_pendente:,.2f}"],
            ['<b>Parcelas Vencidas</b>', f"<font color='red'>R$ {total_vencido:,.2f}</font>"],
        ]

        resumo_table = Table(resumo_data, colWidths=[4*inch, 2.5*inch])
        resumo_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6366f1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        story.append(resumo_table)
        story.append(Spacer(1, 0.3*inch))

        # ===== PROPOSTAS COM PARCELAS =====
        heading = Paragraph("<b>📄 PROPOSTAS E PARCELAS</b>", self.styles['CustomHeading'])
        story.append(heading)

        if not propostas:
            story.append(Paragraph("Nenhuma proposta encontrada.", self.styles['Normal']))
        else:
            for proposta in propostas:
                # Buscar parcelas desta proposta
                parcelas_proposta = [p for p in parcelas if p.proposta_id == proposta.id]

                # Dados da proposta
                proposta_data = [
                    ['<b>Cliente</b>', '<b>CPF</b>', '<b>Valor</b>', '<b>Data Venda</b>'],
                    [
                        proposta.cliente_nome,
                        proposta.cliente_cpf or 'N/A',
                        f"R$ {proposta.valor_bruto:,.2f}",
                        proposta.data_venda.strftime('%d/%m/%Y')
                    ]
                ]

                prop_table = Table(proposta_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
                prop_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#d1fae5')),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ]))

                story.append(prop_table)
                story.append(Spacer(1, 0.1*inch))

                # Tabela de parcelas
                if parcelas_proposta:
                    parcelas_data = [['<b>Parcela</b>', '<b>Vencimento</b>', '<b>Valor</b>', '<b>Status</b>', '<b>Quitação</b>']]

                    for parc in parcelas_proposta:
                        # Cor do status
                        if parc.status == 'QUITADA':
                            status_text = '<font color="green">QUITADA</font>'
                        elif parc.status in ['VENCIDA', 'NOTIFICADA']:
                            status_text = '<font color="red">VENCIDA</font>'
                        else:
                            status_text = 'PENDENTE'

                        quitacao = parc.data_quitacao.strftime('%d/%m/%Y') if parc.data_quitacao else '-'

                        parcelas_data.append([
                            f"{parc.numero_parcela}ª",
                            parc.data_vencimento.strftime('%d/%m/%Y'),
                            f"R$ {parc.valor:,.2f}",
                            status_text,
                            quitacao
                        ])

                    parc_table = Table(parcelas_data, colWidths=[0.8*inch, 1.2*inch, 1.3*inch, 1.2*inch, 1.2*inch])
                    parc_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e2e8f0')),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 8),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ]))

                    story.append(parc_table)
                else:
                    story.append(Paragraph("<i>Nenhuma parcela gerada para esta proposta.</i>", self.styles['Normal']))

                story.append(Spacer(1, 0.2*inch))

        # ===== ALERTAS DE VENCIMENTO =====
        if parcelas_vencidas:
            story.append(Spacer(1, 0.2*inch))
            heading = Paragraph("<b>⚠️ ALERTAS: PARCELAS VENCIDAS</b>", self.styles['CustomHeading'])
            story.append(heading)

            alert_data = [['<b>Cliente</b>', '<b>Parcela</b>', '<b>Vencimento</b>', '<b>Valor</b>', '<b>Dias Atraso</b>']]

            for parc in parcelas_vencidas:
                dias_atraso = (datetime.now().date() - parc.data_vencimento).days
                proposta = session.query(Proposta).get(parc.proposta_id)

                alert_data.append([
                    proposta.cliente_nome,
                    f"{parc.numero_parcela}ª",
                    parc.data_vencimento.strftime('%d/%m/%Y'),
                    f"R$ {parc.valor:,.2f}",
                    f"<font color='red'>{dias_atraso}</font>"
                ])

            alert_table = Table(alert_data, colWidths=[2*inch, 0.8*inch, 1.2*inch, 1.2*inch, 1.3*inch])
            alert_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ef4444')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))

            story.append(alert_table)

        # ===== RODAPÉ =====
        story.append(Spacer(1, 0.5*inch))
        footer = Paragraph(
            f"<i>Relatório gerado automaticamente em {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}</i><br/>"
            "<i>Sistema de Gestão de Corretora - Módulo de Comissões</i>",
            self.styles['Normal']
        )
        story.append(footer)

        # Construir PDF
        doc.build(story)
        session.close()

        print(f"[PDF] [OK] Relatorio gerado: {output_path}")
        return output_path


def exportar_comissoes_corretor(corretor_id: int, output_path=None):
    """
    Função auxiliar para exportar comissões de um corretor

    Args:
        corretor_id: ID do corretor
        output_path: Caminho para salvar (opcional)

    Returns:
        str: Caminho do arquivo gerado
    """
    exporter = PDFExporterAvancado()
    return exporter.gerar_relatorio_comissoes_completo(corretor_id, output_path)


if __name__ == "__main__":
    # Teste
    print("PDF Exporter Avançado carregado!")
