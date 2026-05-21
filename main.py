#!/usr/bin/env python3
"""
🎯 ObservaBI - Ponto de Entrada Principal
Sistema de Análise Inteligente de Dados
"""

import sys
import argparse
from pathlib import Path


def run_interface():
    """Executa a interface gráfica Tkinter"""
    print("🚀 Iniciando Interface Gráfica...")
    try:
        from interface import InterfaceAnalise
        import tkinter as tk
        
        root = tk.Tk()
        app = InterfaceAnalise(root)
        root.mainloop()
    except ImportError as e:
        print(f"❌ Erro: {e}")
        print("Execute: pip install -r requirements.txt")
        sys.exit(1)


def run_analysis(labels_file=None):
    """Executa análise programática com dados de exemplo"""
    print("📊 Executando Análise Programática...")
    try:
        from analise_avancada import executar_analise_completa
        
        labels = [
            "Duplicidade de usuário",
            "Conexão base de dados",
            "Rotina EnviarNFSincrono",
            "Erro Confirmar NF",
            "Consumo indevido",
            "Rejeição Alíquota IBS"
        ]
        values = [124, 51, 41, 36, 32, 23]
        
        executar_analise_completa(labels, values)
        print("✓ Análise concluída!")
        print("Verifique os arquivos PNG gerados na pasta atual.")
    except ImportError as e:
        print(f"❌ Erro: {e}")
        print("Execute: pip install -r requirements.txt")
        sys.exit(1)


def main():
    """Função principal com CLI argumentos"""
    parser = argparse.ArgumentParser(
        description="🎯 ObservaBI - Análise Inteligente de Dados",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python main.py                    # Interface gráfica
  python main.py -c                 # Análise programática
  python main.py --help             # Mostrar ajuda
        """
    )
    
    parser.add_argument(
        '-c', '--cli',
        action='store_true',
        help='Executar análise programática (não-interativa)'
    )
    
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='ObservaBI v2.0'
    )
    
    args = parser.parse_args()
    
    if args.cli:
        run_analysis()
    else:
        run_interface()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Programa interrompido pelo usuário.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
