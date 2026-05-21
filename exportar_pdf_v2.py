"""
Módulo de exportação de PDF com refatoração profissional.
- Type hints completos
- Context managers para recursos
- Otimização de memória
- Desacoplamento de lógica
"""

from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime
import logging

import numpy as np
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, PageBreak, Image, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus.tableofcontents import TableOfContents

from models import DadosAnalise, ResultadoExportacao

logger = logging.getLogger(__name__)


class ConfiguracaoPDF:
    """Configuração centralizada para PDFs."""
    
    # Dimensões
    PAGESIZE = landscape(A4)
    MARGIN_HORIZONTAL = 1.5 * cm
    MARGIN_VERTICAL_TOP = 2 * cm
    MARGIN_VERTICAL_BOTTOM = 1.5 * cm
    
    # Cores
    COR_TITULO = colors.HexColor('#2E86AB')
    COR_SUBTITULO = colors.HexColor('#1D3557')
    COR_HEADER_TABELA = colors.HexColor('#2E86AB')
    COR_HEADER_TEXTO = colors.whitesmoke
    COR_LINHA_ALTERNADA = colors.HexColor('#E8F4F8')
    
    # Fontes
    FONTE_TITULO = ('Helvetica-Bold', 24)
    FONTE_SUBTITULO = ('Helvetica-Bold', 16)
    FONTE_LABEL = ('Helvetica', 10)
    FONTE_PEQUENA = ('Helvetica', 8)


class ExportadorPDF:
    """Exportador de relatórios em PDF com otimizações."""
    
    @contextmanager
    def _criar_documento(self, caminho: str | Path):
        """
        Context manager para criar documento ReportLab.
        Garante cleanup de recursos.
        """
        caminho = Path(caminho)
        caminho.parent.mkdir(parents=True, exist_ok=True)
        
        doc = SimpleDocTemplate(
            str(caminho),
            pagesize=ConfiguracaoPDF.PAGESIZE,
            rightMargin=ConfiguracaoPDF.MARGIN_HORIZONTAL,
            leftMargin=ConfiguracaoPDF.MARGIN_HORIZONTAL,
            topMargin=ConfiguracaoPDF.MARGIN_VERTICAL_TOP,
            bottomMargin=ConfiguracaoPDF.MARGIN_VERTICAL_BOTTOM
        )
        
        try:
            yield doc
        finally:
            logger.info(f"Documento finalizado: {caminho}")
    
    @staticmethod
    def _criar_estilos_customizados() -> Dict[str, ParagraphStyle]:
        """Cria estilos de parágrafo customizados."""
        styles = getSampleStyleSheet()
        
        custom_styles = {
            'titulo': ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=ConfiguracaoPDF.FONTE_TITULO[1],
                textColor=ConfiguracaoPDF.COR_TITULO,
                spaceAfter=30,
                alignment=TA_CENTER,
                fontName=ConfiguracaoPDF.FONTE_TITULO[0]
            ),
            'subtitulo': ParagraphStyle(
                'CustomSubTitle',
                parent=styles['Heading2'],
                fontSize=ConfiguracaoPDF.FONTE_SUBTITULO[1],
                textColor=ConfiguracaoPDF.COR_SUBTITULO,
                spaceAfter=12,
                spaceBefore=20,
                fontName=ConfiguracaoPDF.FONTE_SUBTITULO[0]
            ),
            'data': ParagraphStyle(
                'DataStyle',
                parent=styles['Normal'],
                fontSize=ConfiguracaoPDF.FONTE_PEQUENA[1],
                textColor=colors.grey,
                alignment=TA_CENTER
            ),
            'normal': ParagraphStyle(
                'Normal',
                parent=styles['Normal'],
                fontSize=ConfiguracaoPDF.FONTE_LABEL[1],
                fontName=ConfiguracaoPDF.FONTE_LABEL[0]
            )
        }
        
        return custom_styles
    
    def _gerar_secao_estatisticas(
        self,
        dados: DadosAnalise,
        estilos: Dict[str, ParagraphStyle]
    ) -> List[Any]:
        """
        Gera seção de estatísticas do PDF.
        
        Args:
            dados: Dados para análise
            estilos: Estilos de parágrafo
        
        Returns:
            Lista de elementos Platypus
        """
        elements = []
        
        elements.append(Paragraph("📈 ESTATÍSTICAS GERAIS", estilos['subtitulo']))
        
        # Calcular estatísticas (vetorizado)
        values = np.array(dados.values, dtype=np.float64)
        total = np.sum(values)
        
        stats_data = [
            ['Métrica', 'Valor'],
            ['Total de Incidentes', f'{int(total)}'],
            ['Quantidade de Itens', f'{len(valores)}'],
            ['Média', f'{np.mean(values):.2f}'],
            ['Mediana', f'{np.median(values):.2f}'],
            ['Desvio Padrão', f'{np.std(values):.2f}'],
            ['Variância', f'{np.var(values):.2f}'],
            ['Mínimo', f'{int(np.min(values))}'],
            ['Máximo', f'{int(np.max(values))}'],
            ['Amplitude', f'{int(np.max(values) - np.min(values))}'],
            ['Q1 (25%)', f'{np.percentile(values, 25):.2f}'],
            ['Q3 (75%)', f'{np.percentile(values, 75):.2f}'],
            ['IQR', f'{np.percentile(values, 75) - np.percentile(values, 25):.2f}'],
        ]
        
        table = Table(stats_data, colWidths=[3.5*cm, 3.5*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), ConfiguracaoPDF.COR_HEADER_TABELA),
            ('TEXTCOLOR', (0, 0), (-1, 0), ConfiguracaoPDF.COR_HEADER_TEXTO),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, ConfiguracaoPDF.COR_LINHA_ALTERNADA]),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.5*cm))
        
        return elements
    
    def _gerar_secao_dados(
        self,
        dados: DadosAnalise,
        estilos: Dict[str, ParagraphStyle]
    ) -> List[Any]:
        """
        Gera seção com tabela de dados.
        
        Args:
            dados: Dados para análise
            estilos: Estilos de parágrafo
        
        Returns:
            Lista de elementos Platypus
        """
        elements = []
        
        elements.append(Paragraph("📋 DADOS DETALHADOS", estilos['subtitulo']))
        
        # Calcular percentuais (vetorizado)
        values = np.array(dados.values, dtype=np.float64)
        total = np.sum(values)
        percentages = (values / total) * 100 if total > 0 else np.zeros_like(values)
        
        # Montar tabela com ranking
        table_data = [['#', 'Serviço', 'Quantidade', '%', 'Acum. %']]
        cumulative = 0
        
        # Ordenar por valor decrescente
        sorted_indices = np.argsort(values)[::-1]
        for rank, idx in enumerate(sorted_indices, 1):
            cumulative += percentages[idx]
            table_data.append([
                str(rank),
                dados.labels[idx],
                f'{int(values[idx])}',
                f'{percentages[idx]:.1f}%',
                f'{cumulative:.1f}%'
            ])
        
        table = Table(table_data, colWidths=[0.8*cm, 5.5*cm, 1.5*cm, 1.5*cm, 1.8*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), ConfiguracaoPDF.COR_HEADER_TABELA),
            ('TEXTCOLOR', (0, 0), (-1, 0), ConfiguracaoPDF.COR_HEADER_TEXTO),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, ConfiguracaoPDF.COR_LINHA_ALTERNADA]),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.5*cm))
        
        return elements
    
    def gerar_pdf_completo(
        self,
        dados: DadosAnalise,
        caminho_pdf: str | Path,
        figuras: Optional[Dict[str, str]] = None
    ) -> ResultadoExportacao:
        """
        Gera relatório PDF completo.
        
        Args:
            dados: Dados para análise
            caminho_pdf: Caminho de saída do PDF
            figuras: Dict com caminhos de figuras para incluir
        
        Returns:
            ResultadoExportacao com status
        """
        try:
            start_time = datetime.now()
            
            with self._criar_documento(caminho_pdf) as doc:
                elements = []
                estilos = self._criar_estilos_customizados()
                
                # Cabeçalho
                elements.append(
                    Paragraph("📊 RELATÓRIO COMPLETO DE ANÁLISE DE DADOS", estilos['titulo'])
                )
                elements.append(
                    Paragraph(
                        f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}",
                        estilos['data']
                    )
                )
                elements.append(Spacer(1, 1*cm))
                
                # Seções
                elements.extend(self._gerar_secao_estatisticas(dados, estilos))
                elements.append(PageBreak())
                elements.extend(self._gerar_secao_dados(dados, estilos))
                
                # Incluir figuras se fornecidas
                if figuras:
                    elements.append(PageBreak())
                    elements.append(Paragraph("📈 VISUALIZAÇÕES", estilos['subtitulo']))
                    
                    for nome, caminho_fig in figuras.items():
                        if Path(caminho_fig).exists():
                            try:
                                img = Image(caminho_fig, width=18*cm, height=10*cm)
                                elements.append(img)
                                elements.append(Spacer(1, 0.5*cm))
                            except Exception as e:
                                logger.warning(f"Erro ao incluir figura {nome}: {e}")
                
                # Build PDF
                doc.build(elements)
            
            tempo_exec = (datetime.now() - start_time).total_seconds()
            
            return ResultadoExportacao(
                sucesso=True,
                caminho=str(caminho_pdf),
                mensagem=f"PDF gerado com sucesso em {tempo_exec:.2f}s",
                tempo_geracao=tempo_exec
            )
            
        except Exception as e:
            logger.error(f"Erro ao gerar PDF: {e}")
            return ResultadoExportacao(
                sucesso=False,
                mensagem=f"Erro ao gerar PDF: {str(e)}"
            )
    
    @staticmethod
    def gerar_pdf_simples(
        labels: List[str],
        values: List[float],
        caminho_pdf: str | Path,
        titulo: str = "Relatório de Análise"
    ) -> ResultadoExportacao:
        """
        Gera PDF simples sem figuras.
        
        Args:
            labels: Lista de labels
            values: Lista de valores
            caminho_pdf: Caminho de saída
            titulo: Título do relatório
        
        Returns:
            ResultadoExportacao com status
        """
        dados = DadosAnalise(labels=labels, values=values)
        exportador = ExportadorPDF()
        return exportador.gerar_pdf_completo(dados, caminho_pdf)


class ExportadorExcel:
    """Exportador para Excel (futuro)."""
    
    @staticmethod
    def gerar_excel(
        dados: DadosAnalise,
        caminho_excel: str | Path
    ) -> ResultadoExportacao:
        """
        Gera planilha Excel.
        
        Args:
            dados: Dados para exportar
            caminho_excel: Caminho de saída
        
        Returns:
            ResultadoExportacao com status
        """
        try:
            import pandas as pd
            
            caminho = Path(caminho_excel)
            caminho.parent.mkdir(parents=True, exist_ok=True)
            
            # Criar DataFrame
            values = np.array(dados.values, dtype=np.float64)
            total = np.sum(values)
            percentages = (values / total) * 100 if total > 0 else np.zeros_like(values)
            
            df = pd.DataFrame({
                'Serviço': dados.labels,
                'Quantidade': values.astype(int),
                'Percentual (%)': percentages.round(2),
                'Acumulado (%)': np.cumsum(percentages).round(2)
            })
            
            # Salvar com estilo
            with pd.ExcelWriter(str(caminho), engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Dados')
                
                # Aplicar formatação básica
                worksheet = writer.sheets['Dados']
                for idx, col in enumerate(df.columns, 1):
                    worksheet.column_dimensions[chr(64 + idx)].width = 15
            
            return ResultadoExportacao(
                sucesso=True,
                caminho=str(caminho),
                mensagem="Excel gerado com sucesso"
            )
            
        except ImportError:
            return ResultadoExportacao(
                sucesso=False,
                mensagem="pandas/openpyxl não instalado. Use: pip install pandas openpyxl"
            )
        except Exception as e:
            logger.error(f"Erro ao gerar Excel: {e}")
            return ResultadoExportacao(
                sucesso=False,
                mensagem=f"Erro ao gerar Excel: {str(e)}"
            )
