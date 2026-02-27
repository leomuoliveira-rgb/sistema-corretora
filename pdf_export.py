"""
Sistema de Exportação de Relatórios em PDF
Gera relatórios de repasses, propostas e extratos
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from datetime import datetime
import os


class PDFExporter:
    """Exportador de relatórios em PDF"""

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
            fontSize=16,
            textColor=colors.HexColor('#1e293b'),
            spaceAfter=12,
            fontName='Helvetica-Bold'
        ))

    def gerar_relatorio_repasse(self, corretor, dados, output_path=None):
        """
        Gera PDF de extrato de repasses de um corretor

        Args:
            corretor: Objeto Corretor
            dados: Dict com dados do repasse
            output_path: Caminho para salvar o PDF
        """
        if not output_path:
            filename = f"repasse_{corretor.nome.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
            output_path = os.path.join(os.getcwd(), filename)

        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []

        # Título
        title = Paragraph(f"<b>EXTRATO DE REPASSES</b>", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.3*inch))

        # Informações do Corretor
        info_data = [
            ['Corretor:', corretor.nome],
            ['Email:', corretor.email or 'N/A'],
            ['Telefone:', corretor.telefone or 'N/A'],
            ['Comissão Padrão:', f"{corretor.comissao_padrao}%"],
            ['Data de Emissão:', datetime.now().strftime('%d/%m/%Y %H:%M')],
        ]

        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e2e8f0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ]))

        story.append(info_table)
        story.append(Spacer(1, 0.5*inch))

        # Resumo Financeiro
        heading = Paragraph("<b>RESUMO FINANCEIRO</b>", self.styles['CustomHeading'])
        story.append(heading)
        story.append(Spacer(1, 0.2*inch))

        resumo_data = [
            ['Descrição', 'Valor'],
            ['Total Bruto de Vendas', f"R$ {dados.get('total_bruto', 0):,.2f}"],
            ['Total de Comissões Brutas', f"R$ {dados.get('total_comissao_bruta', 0):,.2f}"],
            ['Total de Impostos', f"R$ {dados.get('total_impostos', 0):,.2f}"],
            ['Total Líquido a Receber', f"R$ {dados.get('total_liquido', 0):,.2f}"],
        ]

        resumo_table = Table(resumo_data, colWidths=[4*inch, 2*inch])
        resumo_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6366f1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#10b981')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ]))

        story.append(resumo_table)
        story.append(Spacer(1, 0.3*inch))

        # Rodapé
        story.append(Spacer(1, 0.5*inch))
        footer = Paragraph(
            f"<i>Documento gerado automaticamente em {datetime.now().strftime('%d/%m/%Y às %H:%M')}</i>",
            self.styles['Normal']
        )
        story.append(footer)

        # Build PDF
        doc.build(story)

        return output_path

    def gerar_relatorio_propostas(self, propostas, output_path=None):
        """
        Gera PDF com listagem de propostas

        Args:
            propostas: Lista de objetos Proposta
            output_path: Caminho para salvar o PDF
        """
        if not output_path:
            filename = f"relatorio_propostas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            output_path = os.path.join(os.getcwd(), filename)

        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []

        # Título
        title = Paragraph("<b>RELATÓRIO DE PROPOSTAS</b>", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.3*inch))

        # Informações gerais
        info = Paragraph(
            f"<b>Total de Propostas:</b> {len(propostas)}<br/>"
            f"<b>Data de Emissão:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            self.styles['Normal']
        )
        story.append(info)
        story.append(Spacer(1, 0.3*inch))

        # Tabela de propostas
        data = [['ID', 'Cliente', 'Corretor', 'Valor', 'Data']]

        for p in propostas[:100]:  # Limitar a 100 propostas
            data.append([
                str(p.id),
                p.cliente_nome[:30],  # Limitar tamanho
                p.corretor.nome[:25],
                f"R$ {p.valor_bruto:,.2f}",
                p.data_venda.strftime('%d/%m/%Y'),
            ])

        propostas_table = Table(data, colWidths=[0.5*inch, 2*inch, 1.8*inch, 1.2*inch, 1*inch])
        propostas_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6366f1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ]))

        story.append(propostas_table)

        # Build PDF
        doc.build(story)

        return output_path


def exportar_repasse_corretor(corretor, dados):
    """
    Função auxiliar para exportar repasse de corretor

    Args:
        corretor: Objeto Corretor
        dados: Dict com dados financeiros

    Returns:
        str: Caminho do arquivo gerado
    """
    exporter = PDFExporter()
    return exporter.gerar_relatorio_repasse(corretor, dados)


def exportar_relatorio_propostas(propostas):
    """
    Função auxiliar para exportar relatório de propostas

    Args:
        propostas: Lista de objetos Proposta

    Returns:
        str: Caminho do arquivo gerado
    """
    exporter = PDFExporter()
    return exporter.gerar_relatorio_propostas(propostas)
