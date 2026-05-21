"""
Módulo de tratamento e extração de dados com suporte a OCR profissional.
- Type hints completos
- EasyOCR (mais preciso que Tesseract)
- Validação com Pydantic
- Limpeza e normalização de dados
"""

from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path
from dataclasses import dataclass
import re
import logging
import time
from io import BytesIO

import numpy as np

from models import ResultadoOCR, DadosAnalise

logger = logging.getLogger(__name__)


class OcrManager:
    """Gerenciador centralizado de OCR com suporte a múltiplos engines."""
    
    _reader = None  # Cache para reader EasyOCR
    
    @classmethod
    def get_reader(cls, idiomas: List[str] = ['pt']):
        """Lazy loading do EasyOCR reader."""
        if cls._reader is None:
            try:
                import easyocr
                logger.info("Inicializando EasyOCR...")
                cls._reader = easyocr.Reader(idiomas, gpu=False)
            except ImportError:
                logger.warning("EasyOCR não instalado. Use: pip install easyocr")
                cls._reader = False
        return cls._reader if cls._reader else None


class TratamentoDados:
    """Processador de dados com validação e limpeza."""
    
    # Padrões regex compilados (otimização)
    PADRAO_VALOR_LABEL = re.compile(r'^(.+?)\s+(\d+(?:\.\d+)?)\s*$')
    PADRAO_VALOR_SEPARADOR = re.compile(r'^(.+?)[\:\-]\s*(\d+(?:\.\d+)?)\s*$')
    PADRAO_NUMERO_INICIO = re.compile(r'^(\d+(?:\.\d+)?)\s+(.+)$')
    PADRAO_NUMERO = re.compile(r'\d+(?:\.\d+)?')
    
    @staticmethod
    def extrair_dados_ocr_easyocr(
        caminho_imagem: str | Path,
        confianca_minima: float = 0.3
    ) -> ResultadoOCR:
        """
        Extrai dados de imagem usando EasyOCR (superior ao Tesseract).
        
        Args:
            caminho_imagem: Caminho da imagem
            confianca_minima: Confiança mínima para aceitar texto
        
        Returns:
            ResultadoOCR com dados extraídos
        """
        start = time.time()
        
        try:
            reader = OcrManager.get_reader()
            
            if not reader:
                return ResultadoOCR(
                    sucesso=False,
                    tempo_processamento=time.time() - start,
                    mensagem="EasyOCR não disponível. Instale com: pip install easyocr"
                )
            
            caminho = Path(caminho_imagem)
            if not caminho.exists():
                raise FileNotFoundError(f"Imagem não encontrada: {caminho}")
            
            # OCR com EasyOCR
            logger.info(f"Processando imagem: {caminho.name}")
            resultados = reader.readtext(str(caminho), detail=1)
            
            # Filtrar por confiança e extrair texto
            textos = [texto for _, texto, confianca in resultados if confianca >= confianca_minima]
            texto_completo = '\n'.join(textos)
            
            # Processar texto
            dados = TratamentoDados.processar_texto_bi(texto_completo)
            
            tempo_proc = time.time() - start
            
            if dados['labels']:
                return ResultadoOCR(
                    sucesso=True,
                    labels=dados['labels'],
                    values=dados['values'],
                    confianca=np.mean([conf for _, _, conf in resultados]) if resultados else None,
                    tempo_processamento=tempo_proc,
                    mensagem=f"Extraído {len(dados['labels'])} itens com sucesso"
                )
            else:
                return ResultadoOCR(
                    sucesso=False,
                    tempo_processamento=tempo_proc,
                    mensagem="Nenhum padrão válido encontrado na imagem"
                )
            
        except Exception as e:
            logger.error(f"Erro ao processar OCR: {e}")
            return ResultadoOCR(
                sucesso=False,
                tempo_processamento=time.time() - start,
                mensagem=f"Erro ao processar imagem: {str(e)}"
            )
    
    @staticmethod
    def extrair_dados_ocr_tesseract(caminho_imagem: str | Path) -> ResultadoOCR:
        """
        Extrai dados usando Tesseract (fallback).
        
        Args:
            caminho_imagem: Caminho da imagem
        
        Returns:
            ResultadoOCR com dados extraídos
        """
        start = time.time()
        
        try:
            import pytesseract
            from PIL import Image
            
            caminho = Path(caminho_imagem)
            img = Image.open(str(caminho))
            
            texto = pytesseract.image_to_string(img, lang='por')
            dados = TratamentoDados.processar_texto_bi(texto)
            
            tempo_proc = time.time() - start
            
            if dados['labels']:
                return ResultadoOCR(
                    sucesso=True,
                    labels=dados['labels'],
                    values=dados['values'],
                    tempo_processamento=tempo_proc,
                    mensagem=f"Extraído {len(dados['labels'])} itens com Tesseract"
                )
            else:
                return ResultadoOCR(
                    sucesso=False,
                    tempo_processamento=tempo_proc,
                    mensagem="Nenhum padrão encontrado com Tesseract"
                )
            
        except ImportError:
            return ResultadoOCR(
                sucesso=False,
                tempo_processamento=time.time() - start,
                mensagem="Tesseract não instalado. Instale com: pip install pytesseract"
            )
        except Exception as e:
            logger.error(f"Erro com Tesseract: {e}")
            return ResultadoOCR(
                sucesso=False,
                tempo_processamento=time.time() - start,
                mensagem=f"Erro ao processar: {str(e)}"
            )
    
    @staticmethod
    def processar_texto_bi(texto: str) -> Dict[str, Any]:
        """
        Processa texto extraído identificando padrões de dados BI.
        
        Formatos suportados:
        - "Nome Serviço 123"
        - "Nome Serviço: 123"
        - "Nome Serviço - 123"
        - "123 Nome Serviço"
        - "Nome Serviço | 123"
        
        Args:
            texto: Texto bruto do OCR
        
        Returns:
            Dict com labels, values e total_itens
        """
        linhas = texto.strip().split('\n')
        labels: List[str] = []
        values: List[float] = []
        
        for linha in linhas:
            # Normalizar
            linha = linha.strip()
            if not linha:
                continue
            
            linha = TratamentoDados._normalizar_linha(linha)
            
            # Tentar padrões em ordem de probabilidade
            resultado = (
                TratamentoDados._tentar_padrao_valor_label(linha) or
                TratamentoDados._tentar_padrao_valor_separador(linha) or
                TratamentoDados._tentar_padrao_numero_inicio(linha) or
                TratamentoDados._tentar_padrao_generico(linha)
            )
            
            if resultado:
                label, valor = resultado
                if label not in labels:  # Evitar duplicatas
                    labels.append(label)
                    values.append(valor)
        
        return {
            'labels': labels,
            'values': values,
            'total_itens': len(labels)
        }
    
    @staticmethod
    def _normalizar_linha(linha: str) -> str:
        """Normaliza linha removendo caracteres especiais."""
        linha = linha.replace('[', '').replace(']', '')
        linha = linha.replace('|', ' ')
        linha = re.sub(r'\s+', ' ', linha)  # Múltiplos espaços
        return linha
    
    @staticmethod
    def _tentar_padrao_valor_label(linha: str) -> Optional[Tuple[str, float]]:
        """Padrão: "Texto 123" """
        match = TratamentoDados.PADRAO_VALOR_LABEL.search(linha)
        if match:
            label = match.group(1).strip()
            label = TratamentoDados._limpar_label(label)
            try:
                valor = float(match.group(2))
                if valor > 0 and len(label) > 2:
                    return label, valor
            except ValueError:
                pass
        return None
    
    @staticmethod
    def _tentar_padrao_valor_separador(linha: str) -> Optional[Tuple[str, float]]:
        """Padrão: "Texto: 123" ou "Texto - 123" """
        match = TratamentoDados.PADRAO_VALOR_SEPARADOR.search(linha)
        if match:
            label = match.group(1).strip()
            label = TratamentoDados._limpar_label(label)
            try:
                valor = float(match.group(2))
                if valor > 0 and len(label) > 2:
                    return label, valor
            except ValueError:
                pass
        return None
    
    @staticmethod
    def _tentar_padrao_numero_inicio(linha: str) -> Optional[Tuple[str, float]]:
        """Padrão: "123 Texto" """
        match = TratamentoDados.PADRAO_NUMERO_INICIO.search(linha)
        if match:
            try:
                valor = float(match.group(1))
                label = match.group(2).strip()
                label = TratamentoDados._limpar_label(label)
                if valor > 0 and len(label) > 2:
                    return label, valor
            except ValueError:
                pass
        return None
    
    @staticmethod
    def _tentar_padrao_generico(linha: str) -> Optional[Tuple[str, float]]:
        """Padrão genérico: extrai último número como valor."""
        numeros = TratamentoDados.PADRAO_NUMERO.findall(linha)
        if numeros and len(linha) > 5:
            try:
                valor = float(numeros[-1])
                label = re.sub(r'\d+(?:\.\d+)?\s*$', '', linha).strip()
                label = TratamentoDados._limpar_label(label)
                if valor > 0 and len(label) > 2:
                    return label, valor
            except ValueError:
                pass
        return None
    
    @staticmethod
    def _limpar_label(label: str) -> str:
        """Remove caracteres especiais de label."""
        label = re.sub(r'[^a-zA-ZÀ-ÿ0-9\s\-:().,\.\*]', '', label).strip()
        label = re.sub(r'\.{3,}', '...', label)  # Normalizar pontos
        return label
    
    @staticmethod
    def extrair_dados_texto_manual(texto: str) -> DadosAnalise:
        """
        Extrai dados de texto colado manualmente.
        
        Args:
            texto: Texto bruto
        
        Returns:
            DadosAnalise validado
        """
        dados = TratamentoDados.processar_texto_bi(texto)
        return DadosAnalise(
            labels=dados['labels'],
            values=dados['values']
        )
    
    @staticmethod
    def extrair_dados_csv(caminho_csv: str | Path) -> DadosAnalise:
        """
        Extrai dados de arquivo CSV com type hints.
        
        Args:
            caminho_csv: Caminho do arquivo CSV
        
        Returns:
            DadosAnalise validado
        """
        try:
            import csv
            
            caminho = Path(caminho_csv)
            labels: List[str] = []
            values: List[float] = []
            
            with open(caminho, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader, None)  # Skip header
                
                for row in reader:
                    if len(row) >= 2:
                        try:
                            label = str(row[0]).strip()
                            valor = float(row[1].strip())
                            if valor >= 0 and label:
                                labels.append(label)
                                values.append(valor)
                        except (ValueError, IndexError):
                            logger.warning(f"Linha inválida: {row}")
                            continue
            
            return DadosAnalise(labels=labels, values=values)
            
        except Exception as e:
            logger.error(f"Erro ao processar CSV: {e}")
            raise ValueError(f"Erro ao processar CSV: {str(e)}")
    
    @staticmethod
    def extrair_dados_excel(caminho_excel: str | Path) -> DadosAnalise:
        """
        Extrai dados de arquivo Excel.
        
        Args:
            caminho_excel: Caminho do arquivo Excel
        
        Returns:
            DadosAnalise validado
        """
        try:
            import pandas as pd
            
            caminho = Path(caminho_excel)
            df = pd.read_excel(caminho)
            
            labels = df.iloc[:, 0].astype(str).tolist()
            values = df.iloc[:, 1].astype(float).tolist()
            
            return DadosAnalise(labels=labels, values=values)
            
        except ImportError:
            raise ImportError("pandas não instalado. Use: pip install pandas openpyxl")
        except Exception as e:
            logger.error(f"Erro ao processar Excel: {e}")
            raise ValueError(f"Erro ao processar Excel: {str(e)}")
    
    @staticmethod
    def limpar_dados(
        labels: List[str],
        values: List[float],
        remover_nulos: bool = True,
        remover_negativos: bool = True
    ) -> Tuple[List[str], List[float]]:
        """
        Limpa dados removendo valores inválidos.
        
        Args:
            labels: Lista de labels
            values: Lista de valores
            remover_nulos: Remove valores nulos/zero
            remover_negativos: Remove valores negativos
        
        Returns:
            Tupla (labels_limpos, values_limpos)
        """
        labels_limpos = []
        values_limpos = []
        
        for label, valor in zip(labels, values):
            if remover_nulos and valor == 0:
                continue
            if remover_negativos and valor < 0:
                continue
            
            labels_limpos.append(label)
            values_limpos.append(valor)
        
        return labels_limpos, values_limpos


class ProcessadorImagemBI:
    """Processador especializado em imagens de BI."""
    
    @staticmethod
    def processar_imagem_bi(
        caminho_imagem: str | Path,
        metodo_ocr: str = 'easyocr'
    ) -> ResultadoOCR:
        """
        Processa imagem de BI escolhendo o melhor método.
        
        Args:
            caminho_imagem: Caminho da imagem
            metodo_ocr: 'easyocr' (recomendado) ou 'tesseract'
        
        Returns:
            ResultadoOCR com dados extraídos
        """
        if metodo_ocr == 'easyocr':
            return TratamentoDados.extrair_dados_ocr_easyocr(caminho_imagem)
        else:
            return TratamentoDados.extrair_dados_ocr_tesseract(caminho_imagem)


def processar_entrada_usuario(entrada: str) -> DadosAnalise:
    """
    Processa entrada do usuário (texto, imagem ou arquivo).
    
    Args:
        entrada: String com dados ou caminho de arquivo
    
    Returns:
        DadosAnalise validado
    """
    entrada = entrada.strip()
    
    # Verificar se é caminho de arquivo
    if entrada.endswith(('.png', '.jpg', '.jpeg', '.bmp')):
        resultado = ProcessadorImagemBI.processar_imagem_bi(entrada)
        if resultado.sucesso:
            return DadosAnalise(labels=resultado.labels, values=resultado.values)
        else:
            raise ValueError(resultado.mensagem)
    
    elif entrada.endswith('.csv'):
        return TratamentoDados.extrair_dados_csv(entrada)
    
    elif entrada.endswith(('.xlsx', '.xls')):
        return TratamentoDados.extrair_dados_excel(entrada)
    
    else:
        # Assume texto manual
        return TratamentoDados.extrair_dados_texto_manual(entrada)
