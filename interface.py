import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import sys
import warnings

# Suprimir warnings de glyphs de emojis não encontrados na fonte
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', message='.*Glyph.*missing from font.*')
warnings.filterwarnings('ignore', message='.*CHART.*')
warnings.filterwarnings('ignore', message='.*TREND.*')
warnings.filterwarnings('ignore', message='.*TROPHY.*')
warnings.filterwarnings('ignore', message='.*RULER.*')
warnings.filterwarnings('ignore', message='.*DejaVu.*')

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    import numpy as np
except ModuleNotFoundError as e:
    try:
        from tkinter import messagebox
        messagebox.showerror(
            "Dependência ausente",
            f"Módulo requerido não encontrado: {e.name}\n\nExecute no terminal:\n  pip install matplotlib numpy"
        )
    except Exception:
        print(f"Módulo requerido não encontrado: {e.name}. Execute: pip install matplotlib numpy")
    sys.exit(1)
from analise_avancada import AnaliseDados
from tratamento_dados import ProcessadorImagemBI, TratamentoDados, processar_entrada_usuario
from exportar_pdf import ExportadorPDF
import json


class InterfaceAnalise:
    def __init__(self, root):
        self.root = root
        self.root.title("ObservaBI - Análise Inteligente de Dados")
        
        # 🎯 RESPONSIVIDADE: Detectar resolução da tela
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calcular tamanho da janela (90% da altura, mantendo proporção 16:9)
        window_height = max(600, int(screen_height * 0.90))
        window_width = max(800, int(window_height * 1.6))
        
        # Limitar ao tamanho da tela
        window_width = min(window_width, screen_width - 100)
        window_height = min(window_height, screen_height - 100)
        
        # Calcular tamanho das fontes baseado na altura
        self.scale_factor = window_height / 800.0
        self.title_font_size = max(10, int(14 * self.scale_factor))
        self.subtitle_font_size = max(8, int(9 * self.scale_factor))
        self.label_font_size = max(7, int(8 * self.scale_factor))
        self.button_font_size = max(7, int(8 * self.scale_factor))
        
        self.root.geometry(f"{window_width}x{window_height}")
        self.root.configure(bg='#f0f0f0')
        
        self.labels = []
        self.values = []
        self.analise = None
        
        self.dados_periodo_anterior = []  # Para gráfico comparativo
        self.tempo_resolucao = []  # Para gráfico de dispersão
        self.informacoes_adicionais = []  # Para exibir na barra horizontal
        self.dados_temporais = {}  # Para gráfico de área (múltiplos períodos)
        self.usar_dados_avancados = False
        self.ordem_crescente = False  # Controle de ordenação da tabela
        self.mapa_indices = {}  # Mapeia posição da tabela para índice original
        
        self.configurar_estilo()
        
        self.criar_interface()
        
    def configurar_estilo(self):
        """Configura o estilo da interface com tamanhos responsivos"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 🎯 FONTES RESPONSIVAS
        style.configure('Title.TLabel', 
                       font=('Arial', self.title_font_size, 'bold'), 
                       background='#f0f0f0', foreground='#2c3e50')
        style.configure('Subtitle.TLabel', 
                       font=('Arial', self.subtitle_font_size, 'bold'),
                       background='#f0f0f0', foreground='#34495e')
        style.configure('Custom.TButton', 
                       font=('Arial', self.button_font_size, 'bold'),
                       padding=max(3, int(6 * self.scale_factor)))
        
    def criar_interface(self):
       
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        title_label = ttk.Label(main_frame, text="📊 ObservaBI", 
                               style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        self.criar_frame_entrada(main_frame)
        
        self.criar_frame_visualizacao(main_frame)
        
        self.criar_frame_controles(main_frame)
        
    def criar_frame_entrada(self, parent):
       
        frame_entrada = ttk.LabelFrame(parent, text="📝 Entrada de Dados", padding="10")
        frame_entrada.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        instrucoes = ttk.Label(frame_entrada, 
                              text="Adicione os dados para análise:",
                              style='Subtitle.TLabel')
        instrucoes.grid(row=0, column=0, columnspan=3, pady=(0, 10), sticky=tk.W)
        
        ttk.Label(frame_entrada, text="Categoria:", font=('Arial', self.label_font_size)).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entry_label = ttk.Entry(frame_entrada, width=20)
        self.entry_label.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        ttk.Label(frame_entrada, text="Valor Atual:", font=('Arial', self.label_font_size)).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.entry_value = ttk.Entry(frame_entrada, width=20)
        self.entry_value.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        self.frame_avancado = ttk.LabelFrame(frame_entrada, text="📊 Dados Avançados (Opcional)", padding="5")
        self.frame_avancado.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10, padx=5)
        self.frame_avancado.grid_remove()  # Esconder inicialmente
        
        ttk.Label(self.frame_avancado, text="Período Anterior:", font=('Arial', self.label_font_size)).grid(row=0, column=0, sticky=tk.W, pady=3)
        self.entry_periodo_anterior = ttk.Entry(self.frame_avancado, width=12)
        self.entry_periodo_anterior.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=3, padx=3)
        
        ttk.Label(self.frame_avancado, text="Tempo Resolução (h):", font=('Arial', self.label_font_size)).grid(row=1, column=0, sticky=tk.W, pady=3)
        self.entry_tempo_resolucao = ttk.Entry(self.frame_avancado, width=12)
        self.entry_tempo_resolucao.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=3, padx=3)
        
        ttk.Label(self.frame_avancado, text="Informações Adicionais:", font=('Arial', self.label_font_size)).grid(row=2, column=0, sticky=tk.W, pady=3)
        self.entry_informacoes_adicionais = ttk.Entry(self.frame_avancado, width=12)
        self.entry_informacoes_adicionais.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=3, padx=3)
        
        self.btn_toggle_avancado = ttk.Button(frame_entrada, text="▼ Mostrar Campos Avançados",
                                              command=self.toggle_campos_avancados,
                                              width=25)
        self.btn_toggle_avancado.grid(row=4, column=0, columnspan=3, pady=5)
        
        # 🎯 LAYOUT RESPONSIVO: 2x2 de botões em vez de 3 em linha
        btn_width = max(12, int(20 * self.scale_factor))
        
        btn_adicionar = ttk.Button(frame_entrada, text="➕ Adicionar", 
                                   command=self.adicionar_dado,
                                   style='Custom.TButton', width=btn_width-2)
        btn_adicionar.grid(row=5, column=0, pady=5, padx=2, sticky=(tk.W, tk.E))
        
        btn_sequencia = ttk.Button(frame_entrada, text="⚡ Rápida", 
                                   command=self.inserir_sequencia,
                                   style='Custom.TButton', width=btn_width-2)
        btn_sequencia.grid(row=5, column=1, pady=5, padx=2, sticky=(tk.W, tk.E))
        
        btn_editar = ttk.Button(frame_entrada, text="✏️ Editar", 
                                command=self.editar_dado,
                                style='Custom.TButton', width=btn_width-2)
        btn_editar.grid(row=5, column=2, pady=5, padx=2, sticky=(tk.W, tk.E))
        
        btn_remover = ttk.Button(frame_entrada, text="➖ Remover", 
                                command=self.remover_dado,
                                style='Custom.TButton', width=btn_width-2)
        btn_remover.grid(row=6, column=0, pady=5, padx=2, sticky=(tk.W, tk.E))
        
        btn_limpar = ttk.Button(frame_entrada, text="🗑️ Limpar", 
                               command=self.limpar_dados,
                               style='Custom.TButton', width=btn_width-2)
        btn_limpar.grid(row=6, column=1, columnspan=2, pady=5, padx=2, sticky=(tk.W, tk.E))
        
        ttk.Label(frame_entrada, text="Dados:", style='Subtitle.TLabel').grid(row=7, column=0, columnspan=2, 
                                              pady=(10, 5), sticky=tk.W)
        
        self.btn_ordenar = ttk.Button(frame_entrada, text="⬆️", 
                                     command=self.toggle_ordenacao,
                                     width=3)
        self.btn_ordenar.grid(row=7, column=2, sticky=tk.E, padx=2)
        
        # 🎯 TABELA RESPONSIVA com altura dinâmica
        columns = ('Categoria', 'Valor', 'Ant.', 'h', 'Info')
        tree_height = max(5, int(8 * self.scale_factor))
        self.tree = ttk.Treeview(frame_entrada, columns=columns, show='headings', height=tree_height)
        
        self.tree.heading('Categoria', text='Categoria')
        self.tree.heading('Valor', text='Valor')
        self.tree.heading('Ant.', text='Ant.')
        self.tree.heading('h', text='h')
        self.tree.heading('Info', text='Info')
        
        # 🎯 COLUNAS RESPONSIVAS (proporcionais)
        self.tree.column('Categoria', width=max(80, int(120 * self.scale_factor)))
        self.tree.column('Valor', width=max(50, int(60 * self.scale_factor)))
        self.tree.column('Ant.', width=max(50, int(60 * self.scale_factor)))
        self.tree.column('h', width=max(40, int(50 * self.scale_factor)))
        self.tree.column('Info', width=max(60, int(80 * self.scale_factor)))
        
        self.tree.grid(row=8, column=0, columnspan=3, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.tree.bind('<Double-Button-1>', lambda e: self.editar_dado())
        
        scrollbar = ttk.Scrollbar(frame_entrada, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=8, column=3, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        ttk.Separator(frame_entrada, orient='horizontal').grid(row=9, column=0, 
                                                               columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # 🎯 BOTÕES IMPORT/EXPORT com layout responsivo
        btn_width_small = max(8, int(14 * self.scale_factor))
        
        btn_carregar = ttk.Button(frame_entrada, text="📂 JSON", 
                                 command=self.carregar_dados,
                                 style='Custom.TButton', width=btn_width_small)
        btn_carregar.grid(row=10, column=0, pady=3, padx=2, sticky=(tk.W, tk.E))
        
        btn_salvar = ttk.Button(frame_entrada, text="💾 JSON", 
                               command=self.salvar_dados,
                               style='Custom.TButton', width=btn_width_small)
        btn_salvar.grid(row=10, column=1, pady=3, padx=2, sticky=(tk.W, tk.E))
        
        btn_exemplo = ttk.Button(frame_entrada, text="📋 Exemplo", 
                                command=self.carregar_exemplo,
                                style='Custom.TButton', width=btn_width_small)
        btn_exemplo.grid(row=10, column=2, pady=3, padx=2, sticky=(tk.W, tk.E))
        
        btn_imagem = ttk.Button(frame_entrada, text="🖼️ OCR", 
                               command=self.importar_imagem,
                               style='Custom.TButton', width=btn_width_small)
        btn_imagem.grid(row=11, column=0, pady=3, padx=2, sticky=(tk.W, tk.E))
        
        btn_texto = ttk.Button(frame_entrada, text="📝 Texto", 
                              command=self.colar_texto_bi,
                              style='Custom.TButton', width=btn_width_small)
        btn_texto.grid(row=11, column=1, pady=3, padx=2, sticky=(tk.W, tk.E))
        
        btn_ajuda = ttk.Button(frame_entrada, text="❓ Ajuda", 
                              command=self.mostrar_ajuda,
                              width=btn_width_small)
        btn_ajuda.grid(row=11, column=2, pady=3, padx=2, sticky=(tk.W, tk.E))
        
        frame_entrada.columnconfigure(1, weight=1)
        frame_entrada.rowconfigure(8, weight=1)  
        
    def criar_frame_visualizacao(self, parent):
     
        frame_viz = ttk.LabelFrame(parent, text="📈 Visualização", padding="10")
        frame_viz.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        frame_viz.columnconfigure(0, weight=1)
        frame_viz.rowconfigure(1, weight=1)
        
        frame_controles_viz = ttk.Frame(frame_viz)
        frame_controles_viz.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        btn_zoom_in = ttk.Button(frame_controles_viz, text="🔍+ Zoom In", 
                                command=self.zoom_in,
                                width=12)
        btn_zoom_in.pack(side=tk.LEFT, padx=2)
        
        btn_zoom_out = ttk.Button(frame_controles_viz, text="🔍− Zoom Out", 
                                 command=self.zoom_out,
                                 width=12)
        btn_zoom_out.pack(side=tk.LEFT, padx=2)
        
        btn_guia = ttk.Button(frame_controles_viz, text="📊 Guia de Gráficos", 
                             command=self.mostrar_guia_graficos,
                             width=18)
        btn_guia.pack(side=tk.LEFT, padx=2)
        
        self.canvas_container = tk.Canvas(frame_viz, bg='white')
        self.scrollbar_y = ttk.Scrollbar(frame_viz, orient=tk.VERTICAL, command=self.canvas_container.yview)
        self.scrollbar_x = ttk.Scrollbar(frame_viz, orient=tk.HORIZONTAL, command=self.canvas_container.xview)
        
        self.canvas_frame = ttk.Frame(self.canvas_container)
        
        self.canvas_container.configure(yscrollcommand=self.scrollbar_y.set, 
                                       xscrollcommand=self.scrollbar_x.set)
        
        self.canvas_container.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.scrollbar_y.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.scrollbar_x.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        self.canvas_window = self.canvas_container.create_window((0, 0), window=self.canvas_frame, anchor=tk.NW)
        
        self.canvas_frame.bind('<Configure>', self.on_frame_configure)
        self.canvas_container.bind('<Configure>', self.on_canvas_configure)
        
        self.label_placeholder = ttk.Label(self.canvas_frame, 
                                          text="Adicione dados e selecione um tipo de gráfico",
                                          font=('Arial', 12))
        self.label_placeholder.grid(row=0, column=0, padx=50, pady=50)
        
    def on_frame_configure(self, event=None):
        
        self.canvas_container.configure(scrollregion=self.canvas_container.bbox("all"))
    
    def on_canvas_configure(self, event):
       
        canvas_width = event.width
        self.canvas_container.itemconfig(self.canvas_window, width=canvas_width)
        
    def criar_frame_controles(self, parent):
       
        frame_controles = ttk.LabelFrame(parent, text="🎨 Controles de Visualização", padding="10")
        frame_controles.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Label(frame_controles, text="Tipo de Gráfico:", 
                 style='Subtitle.TLabel').grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        graficos = [
            ("📊 Barras V", "barras_vertical"),
            ("📊 Barras H", "barras_horizontal"),
            ("🥧 Pizza", "pizza"),
            ("📈 Pareto", "pareto"),
            ("📉 Linha", "linha"),
            ("📊 Área", "area"),
            ("🔄 Comp.", "comparativo"),
            ("🔵 Disp.", "dispersao"),
            ("📋 Dashboard", "dashboard")
        ]
        
        # 🎯 LAYOUT RESPONSIVO: botões em grid com melhor adaptação
        col = 1
        buttons_per_row = max(3, int(5 * self.scale_factor))  # Mais botões em linhas menores
        
        for i, (texto, tipo) in enumerate(graficos):
            row = i // buttons_per_row
            col_pos = (i % buttons_per_row) + 1
            
            btn = ttk.Button(frame_controles, text=texto, 
                           command=lambda t=tipo: self.gerar_grafico(t),
                           width=max(10, int(14 * self.scale_factor)))
            btn.grid(row=row, column=col_pos, padx=2, pady=3, sticky=(tk.W, tk.E))
            
        ttk.Separator(frame_controles, orient='horizontal').grid(
            row=row+1, column=0, columnspan=buttons_per_row+1, 
            sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(frame_controles, text="Exportar:", 
                 style='Subtitle.TLabel').grid(row=row+2, column=0, padx=5, pady=5, sticky=tk.W)
        
        btn_width_export = max(10, int(13 * self.scale_factor))
        
        btn_salvar_png = ttk.Button(frame_controles, text="💾 PNG", 
                                   command=self.salvar_grafico_png,
                                   style='Custom.TButton', width=btn_width_export)
        btn_salvar_png.grid(row=row+2, column=1, padx=2, pady=3, sticky=(tk.W, tk.E))
        
        btn_relatorio = ttk.Button(frame_controles, text="📄 Relatório", 
                                  command=self.gerar_relatorio,
                                  style='Custom.TButton', width=btn_width_export)
        btn_relatorio.grid(row=row+2, column=2, padx=2, pady=3, sticky=(tk.W, tk.E))
        
        btn_pdf = ttk.Button(frame_controles, text="📕 PDF", 
                            command=self.exportar_pdf_completo,
                            style='Custom.TButton', width=btn_width_export)
        btn_pdf.grid(row=row+2, column=3, padx=2, pady=3, sticky=(tk.W, tk.E))
        
        btn_todos = ttk.Button(frame_controles, text="🖼️ Todos", 
                              command=self.gerar_todos_graficos,
                              style='Custom.TButton', width=btn_width_export)
        btn_todos.grid(row=row+2, column=4, padx=2, pady=3, sticky=(tk.W, tk.E))
        
        # 🎯 Tornar o frame expansível
        frame_controles.columnconfigure(1, weight=1)
        frame_controles.columnconfigure(2, weight=1)
        frame_controles.columnconfigure(3, weight=1)
        frame_controles.columnconfigure(4, weight=1)
    
    def toggle_campos_avancados(self):
        """Mostra/oculta campos avançados"""
        if self.frame_avancado.winfo_viewable():
            self.frame_avancado.grid_remove()
            self.btn_toggle_avancado.config(text="▼ Mostrar Campos Avançados")
        else:
            self.frame_avancado.grid()
            self.btn_toggle_avancado.config(text="▲ Ocultar Campos Avançados")
    
    def toggle_ordenacao(self):
        """Alterna entre ordenação crescente e decrescente"""
        self.ordem_crescente = not self.ordem_crescente
        if self.ordem_crescente:
            self.btn_ordenar.config(text="⬇️ Decrescente")
        else:
            self.btn_ordenar.config(text="⬆️ Crescente")
        self.atualizar_tabela_dados()
    
    def atualizar_tabela_dados(self):
        """Atualiza a tabela com os dados ordenados"""
        # Limpar tabela e mapa
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.mapa_indices = {}
        
        # Criar lista de índices ordenados
        indices = list(range(len(self.labels)))
        if self.ordem_crescente:
            indices.sort(key=lambda i: self.values[i])  # Crescente
        else:
            indices.sort(key=lambda i: self.values[i], reverse=True)  # Decrescente
        
        # Reinserir dados ordenados
        for pos, idx in enumerate(indices):
            periodo_display = int(self.dados_periodo_anterior[idx]) if idx < len(self.dados_periodo_anterior) and self.dados_periodo_anterior[idx] else '-'
            tempo_display = f"{self.tempo_resolucao[idx]:.1f}" if idx < len(self.tempo_resolucao) and self.tempo_resolucao[idx] else '-'
            info_display = self.informacoes_adicionais[idx] if idx < len(self.informacoes_adicionais) and self.informacoes_adicionais[idx] else '-'
            
            item_id = self.tree.insert('', tk.END, values=(
                self.labels[idx],
                int(self.values[idx]),
                periodo_display,
                tempo_display,
                info_display
            ))
            # Mapear posição da tabela para índice original
            self.mapa_indices[item_id] = idx
        
    def toggle_campos_avancados(self):
        """Mostra/oculta campos avançados"""
        if self.frame_avancado.winfo_viewable():
            self.frame_avancado.grid_remove()
            self.btn_toggle_avancado.config(text="▼ Mostrar Campos Avançados")
        else:
            self.frame_avancado.grid()
            self.btn_toggle_avancado.config(text="▲ Ocultar Campos Avançados")
        
    def adicionar_dado(self):
        """Adiciona um novo dado à lista com dados opcionais"""
        label = self.entry_label.get().strip()
        value_str = self.entry_value.get().strip()
        
        if not label or not value_str:
            messagebox.showwarning("Atenção", "Preencha os campos obrigatórios!")
            return
        
        try:
            value = float(value_str)
            if value < 0:
                raise ValueError("Valor deve ser positivo")
        except ValueError as e:
            messagebox.showerror("Erro", "Valor deve ser um número positivo!")
            return
        
        self.labels.append(label)
        self.values.append(value)
        
        periodo_ant_str = self.entry_periodo_anterior.get().strip()
        tempo_res_str = self.entry_tempo_resolucao.get().strip()
        info_adicionais_str = self.entry_informacoes_adicionais.get().strip()
        
        if periodo_ant_str:
            try:
                periodo_ant = float(periodo_ant_str)
                if periodo_ant < 0:
                    raise ValueError()
                self.dados_periodo_anterior.append(periodo_ant)
            except ValueError:
                self.dados_periodo_anterior.append(None)
        else:
            self.dados_periodo_anterior.append(None)
        
        if tempo_res_str:
            try:
                tempo_res = float(tempo_res_str)
                if tempo_res < 0:
                    raise ValueError()
                self.tempo_resolucao.append(tempo_res)
            except ValueError:
                self.tempo_resolucao.append(None)
        else:
            self.tempo_resolucao.append(None)
        
        # Adicionar informações adicionais
        if info_adicionais_str:
            self.informacoes_adicionais.append(info_adicionais_str)
        else:
            self.informacoes_adicionais.append(None)
        
        if any(self.dados_periodo_anterior) or any(self.tempo_resolucao) or any(self.informacoes_adicionais):
            self.usar_dados_avancados = True
        
        self.entry_label.delete(0, tk.END)
        self.entry_value.delete(0, tk.END)
        self.entry_periodo_anterior.delete(0, tk.END)
        self.entry_tempo_resolucao.delete(0, tk.END)
        self.entry_informacoes_adicionais.delete(0, tk.END)
        self.entry_label.focus()
        
        self.atualizar_tabela_dados()
        self.atualizar_analise()
    
    def inserir_sequencia(self):
        """Abre janela para inserção rápida em sequência de múltiplos dados"""
        janela_seq = tk.Toplevel(self.root)
        janela_seq.title("⚡ Inserção Rápida em Sequência")
        janela_seq.geometry("800x600")
        janela_seq.transient(self.root)
        
        frame_principal = ttk.Frame(janela_seq, padding="15")
        frame_principal.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(frame_principal, text="Inserção Rápida em Sequência", 
                 font=('Arial', 14, 'bold')).pack(pady=(0, 10))
        ttk.Label(frame_principal, text="Use Tab para navegar. Enter para avançar ou adicionar item. Ctrl+Enter para adicionar de qualquer campo.", 
                 font=('Arial', 9), foreground='gray').pack(pady=(0, 15))
        
        # Frame de entrada
        frame_entrada = ttk.LabelFrame(frame_principal, text="Novos Dados", padding="10")
        frame_entrada.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(frame_entrada, text="Categoria:").grid(row=0, column=0, sticky=tk.W, pady=5)
        entry_label_seq = ttk.Entry(frame_entrada, width=40)
        entry_label_seq.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        ttk.Label(frame_entrada, text="Valor:").grid(row=1, column=0, sticky=tk.W, pady=5)
        entry_value_seq = ttk.Entry(frame_entrada, width=40)
        entry_value_seq.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        ttk.Label(frame_entrada, text="Período Anterior (opt):").grid(row=2, column=0, sticky=tk.W, pady=5)
        entry_periodo_seq = ttk.Entry(frame_entrada, width=40)
        entry_periodo_seq.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        ttk.Label(frame_entrada, text="Tempo (h) (opt):").grid(row=3, column=0, sticky=tk.W, pady=5)
        entry_tempo_seq = ttk.Entry(frame_entrada, width=40)
        entry_tempo_seq.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        ttk.Label(frame_entrada, text="Informações (opt):").grid(row=4, column=0, sticky=tk.W, pady=5)
        entry_info_seq = ttk.Entry(frame_entrada, width=40)
        entry_info_seq.grid(row=4, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        frame_entrada.columnconfigure(1, weight=1)
        
        # Frame para lista de itens adicionados
        frame_lista = ttk.LabelFrame(frame_principal, text="Itens a Adicionar", padding="10")
        frame_lista.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Treeview para mostrar itens que serão adicionados
        columns_seq = ('Categoria', 'Valor', 'Anterior', 'Tempo (h)', 'Informações')
        tree_seq = ttk.Treeview(frame_lista, columns=columns_seq, show='headings', height=10)
        tree_seq.heading('Categoria', text='Categoria')
        tree_seq.heading('Valor', text='Valor')
        tree_seq.heading('Anterior', text='Período Ant.')
        tree_seq.heading('Tempo (h)', text='Tempo (h)')
        tree_seq.heading('Informações', text='Informações')
        tree_seq.column('Categoria', width=200)
        tree_seq.column('Valor', width=80)
        tree_seq.column('Anterior', width=80)
        tree_seq.column('Tempo (h)', width=80)
        tree_seq.column('Informações', width=150)
        tree_seq.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        scrollbar_seq = ttk.Scrollbar(frame_lista, orient=tk.VERTICAL, command=tree_seq.yview)
        scrollbar_seq.pack(side=tk.LEFT, fill=tk.Y)
        tree_seq.configure(yscrollcommand=scrollbar_seq.set)
        
        # Lista temporária
        dados_temp = []
        
        def adicionar_item_temp():
            """Adiciona item à lista temporária"""
            label = entry_label_seq.get().strip()
            value_str = entry_value_seq.get().strip()
            
            if not label or not value_str:
                messagebox.showwarning("Atenção", "Preencha Categoria e Valor!")
                return
            
            try:
                value = float(value_str)
                if value < 0:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("Erro", "Valor deve ser um número positivo!")
                return
            
            periodo_str = entry_periodo_seq.get().strip()
            tempo_str = entry_tempo_seq.get().strip()
            info_str = entry_info_seq.get().strip()
            
            # Validar valores opcionais
            periodo = None
            tempo = None
            
            if periodo_str:
                try:
                    periodo = float(periodo_str)
                    if periodo < 0:
                        raise ValueError()
                except ValueError:
                    messagebox.showerror("Erro", "Período Anterior inválido!")
                    return
            
            if tempo_str:
                try:
                    tempo = float(tempo_str)
                    if tempo < 0:
                        raise ValueError()
                except ValueError:
                    messagebox.showerror("Erro", "Tempo de Resolução inválido!")
                    return
            
            # Adicionar aos dados temporários
            dados_temp.append({
                'label': label,
                'value': value,
                'periodo': periodo,
                'tempo': tempo,
                'info': info_str if info_str else None
            })
            
            # Atualizar treeview
            tree_seq.insert('', tk.END, values=(
                label,
                int(value) if value == int(value) else value,
                int(periodo) if periodo and periodo == int(periodo) else periodo if periodo else '',
                tempo if tempo else '',
                info_str
            ))
            
            # Limpar campos de entrada
            entry_label_seq.delete(0, tk.END)
            entry_value_seq.delete(0, tk.END)
            entry_periodo_seq.delete(0, tk.END)
            entry_tempo_seq.delete(0, tk.END)
            entry_info_seq.delete(0, tk.END)
            entry_label_seq.focus()
            
            # Atualizar contador
            atualizar_contador()
        
        def remover_selecionado():
            """Remove item selecionado da lista temporária"""
            selection = tree_seq.selection()
            if not selection:
                messagebox.showwarning("Atenção", "Selecione um item para remover!")
                return
            
            item_index = tree_seq.index(selection[0])
            tree_seq.delete(selection[0])
            del dados_temp[item_index]
            atualizar_contador()
        
        def atualizar_contador():
            """Atualiza o rótulo com quantidade de itens"""
            label_contador.config(text=f"Total de itens a adicionar: {len(dados_temp)}")
        
        def confirmar_adicao():
            """Adiciona todos os itens e fecha a janela"""
            if not dados_temp:
                messagebox.showwarning("Atenção", "Nenhum item para adicionar!")
                return
            
            # Adicionar todos os itens aos dados principais
            for item in dados_temp:
                self.labels.append(item['label'])
                self.values.append(item['value'])
                self.dados_periodo_anterior.append(item['periodo'])
                self.tempo_resolucao.append(item['tempo'])
                self.informacoes_adicionais.append(item['info'])
            
            # Verificar se há dados avançados
            if any(self.dados_periodo_anterior) or any(self.tempo_resolucao) or any(self.informacoes_adicionais):
                self.usar_dados_avancados = True
            
            self.atualizar_tabela_dados()
            self.atualizar_analise()
            
            messagebox.showinfo("Sucesso", f"{len(dados_temp)} item(ns) adicionado(s)!")
            janela_seq.destroy()
        
        # Frame de controles
        frame_botoesalt = ttk.Frame(frame_principal)
        frame_botoesalt.pack(fill=tk.X, pady=(0, 10))
        
        btn_adicionar_item = ttk.Button(frame_botoesalt, text="➕ Adicionar Item", 
                                        command=adicionar_item_temp,
                                        width=30)
        btn_adicionar_item.pack(side=tk.LEFT, padx=5)
        
        btn_remover_item = ttk.Button(frame_botoesalt, text="➖ Remover Selecionado", 
                                      command=remover_selecionado,
                                      width=30)
        btn_remover_item.pack(side=tk.LEFT, padx=5)
        
        # Label contador
        label_contador = ttk.Label(frame_principal, text="Total de itens a adicionar: 0", 
                                   font=('Arial', 10, 'bold'), foreground='#2c3e50')
        label_contador.pack(pady=(0, 10))
        
        # Frame de ações finais
        frame_botoes_finais = ttk.Frame(frame_principal)
        frame_botoes_finais.pack(fill=tk.X)
        
        btn_confirmar = ttk.Button(frame_botoes_finais, text="✅ Confirmar e Adicionar Tudo", 
                                   command=confirmar_adicao,
                                   width=35)
        btn_confirmar.pack(side=tk.LEFT, padx=5)
        
        btn_cancelar = ttk.Button(frame_botoes_finais, text="❌ Cancelar", 
                                 command=janela_seq.destroy,
                                 width=35)
        btn_cancelar.pack(side=tk.LEFT, padx=5)
        
        # Bind para Enter confirmar item em qualquer campo
        entry_label_seq.bind('<Return>', lambda e: entry_value_seq.focus())
        entry_value_seq.bind('<Return>', lambda e: adicionar_item_temp())
        entry_periodo_seq.bind('<Return>', lambda e: entry_tempo_seq.focus())
        entry_tempo_seq.bind('<Return>', lambda e: entry_info_seq.focus())
        entry_info_seq.bind('<Return>', lambda e: adicionar_item_temp())
        
        # Alternativamente, Ctrl+Enter em qualquer campo adiciona o item
        def adicionar_com_ctrl_enter(event):
            """Adiciona item quando Ctrl+Enter é pressionado"""
            adicionar_item_temp()
        
        entry_label_seq.bind('<Control-Return>', adicionar_com_ctrl_enter)
        entry_value_seq.bind('<Control-Return>', adicionar_com_ctrl_enter)
        entry_periodo_seq.bind('<Control-Return>', adicionar_com_ctrl_enter)
        entry_tempo_seq.bind('<Control-Return>', adicionar_com_ctrl_enter)
        entry_info_seq.bind('<Control-Return>', adicionar_com_ctrl_enter)
        
        entry_label_seq.focus()
        
    def editar_dado(self):
        """Edita o dado selecionado incluindo dados opcionais"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Atenção", "Selecione um item para editar!")
            return
        
        # Usar mapa para obter índice original
        item_id = selected[0]
        index = self.mapa_indices.get(item_id, self.tree.index(item_id))
        
        label_atual = self.labels[index]
        value_atual = self.values[index]
        periodo_ant_atual = self.dados_periodo_anterior[index] if index < len(self.dados_periodo_anterior) else None
        tempo_res_atual = self.tempo_resolucao[index] if index < len(self.tempo_resolucao) else None
        info_adicionais_atual = self.informacoes_adicionais[index] if index < len(self.informacoes_adicionais) else None
        
        janela_edit = tk.Toplevel(self.root)
        janela_edit.title("Editar Dado")
        janela_edit.geometry("500x400")
        janela_edit.transient(self.root)
        janela_edit.grab_set()
        
        frame = ttk.Frame(janela_edit, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Editar Dado", 
                 font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        ttk.Label(frame, text="Categoria:").grid(row=1, column=0, sticky=tk.W, pady=5)
        entry_label_edit = ttk.Entry(frame, width=30)
        entry_label_edit.insert(0, label_atual)
        entry_label_edit.grid(row=1, column=1, pady=5, padx=(10, 0), sticky=(tk.W, tk.E))
        entry_label_edit.focus()
        entry_label_edit.select_range(0, tk.END)
        
        ttk.Label(frame, text="Valor Atual:").grid(row=2, column=0, sticky=tk.W, pady=5)
        entry_value_edit = ttk.Entry(frame, width=30)
        entry_value_edit.insert(0, str(int(value_atual)))
        entry_value_edit.grid(row=2, column=1, pady=5, padx=(10, 0), sticky=(tk.W, tk.E))
        
        ttk.Label(frame, text="--- Dados Opcionais ---", 
                 font=('Arial', 9, 'italic'), foreground='gray').grid(row=3, column=0, columnspan=2, pady=(10, 5))
        
        ttk.Label(frame, text="Período Anterior:", font=('Arial', 8)).grid(row=4, column=0, sticky=tk.W, pady=5)
        entry_periodo_edit = ttk.Entry(frame, width=30)
        if periodo_ant_atual is not None:
            entry_periodo_edit.insert(0, str(int(periodo_ant_atual)))
        entry_periodo_edit.grid(row=4, column=1, pady=5, padx=(10, 0), sticky=(tk.W, tk.E))
        
        ttk.Label(frame, text="Tempo Resolução (h):", font=('Arial', 8)).grid(row=5, column=0, sticky=tk.W, pady=5)
        entry_tempo_edit = ttk.Entry(frame, width=30)
        if tempo_res_atual is not None:
            entry_tempo_edit.insert(0, str(tempo_res_atual))
        entry_tempo_edit.grid(row=5, column=1, pady=5, padx=(10, 0), sticky=(tk.W, tk.E))
        
        ttk.Label(frame, text="Informações Adicionais:", font=('Arial', 8)).grid(row=6, column=0, sticky=tk.W, pady=5)
        entry_info_edit = ttk.Entry(frame, width=30)
        if info_adicionais_atual is not None:
            entry_info_edit.insert(0, info_adicionais_atual)
        entry_info_edit.grid(row=6, column=1, pady=5, padx=(10, 0), sticky=(tk.W, tk.E))
        
        def salvar_edicao():
            novo_label = entry_label_edit.get().strip()
            novo_value_str = entry_value_edit.get().strip()
            
            if not novo_label or not novo_value_str:
                messagebox.showwarning("Atenção", "Preencha os campos obrigatórios!")
                return
            
            try:
                novo_value = float(novo_value_str)
                if novo_value < 0:
                    raise ValueError("Valor deve ser positivo")
            except ValueError:
                messagebox.showerror("Erro", "Valor deve ser um número positivo!")
                return
            
            self.labels[index] = novo_label
            self.values[index] = novo_value
            
            novo_periodo_str = entry_periodo_edit.get().strip()
            novo_tempo_str = entry_tempo_edit.get().strip()
            novo_info_str = entry_info_edit.get().strip()
            
            while len(self.dados_periodo_anterior) <= index:
                self.dados_periodo_anterior.append(None)
            while len(self.tempo_resolucao) <= index:
                self.tempo_resolucao.append(None)
            while len(self.informacoes_adicionais) <= index:
                self.informacoes_adicionais.append(None)
            
            if novo_periodo_str:
                try:
                    self.dados_periodo_anterior[index] = float(novo_periodo_str)
                except ValueError:
                    self.dados_periodo_anterior[index] = None
            else:
                self.dados_periodo_anterior[index] = None
            
            if novo_tempo_str:
                try:
                    self.tempo_resolucao[index] = float(novo_tempo_str)
                except ValueError:
                    self.tempo_resolucao[index] = None
            else:
                self.tempo_resolucao[index] = None
            
            if novo_info_str:
                self.informacoes_adicionais[index] = novo_info_str
            else:
                self.informacoes_adicionais[index] = None
            
            periodo_display = int(self.dados_periodo_anterior[index]) if self.dados_periodo_anterior[index] else '-'
            tempo_display = f"{self.tempo_resolucao[index]:.1f}" if self.tempo_resolucao[index] else '-'
            info_display = self.informacoes_adicionais[index] if self.informacoes_adicionais[index] else '-'
            
            self.tree.item(selected[0], values=(
                novo_label, 
                int(novo_value),
                periodo_display,
                tempo_display,
                info_display
            ))
            
            if any(self.dados_periodo_anterior) or any(self.tempo_resolucao) or any(self.informacoes_adicionais):
                self.usar_dados_avancados = True
            
            self.atualizar_analise()
            
            messagebox.showinfo("Sucesso", "Dado atualizado com sucesso!")
            janela_edit.destroy()
        
        frame_btn = ttk.Frame(frame)
        frame_btn.grid(row=7, column=0, columnspan=2, pady=(20, 0))
        
        btn_salvar = ttk.Button(frame_btn, text="✓ Salvar", 
                               command=salvar_edicao,
                               style='Custom.TButton')
        btn_salvar.pack(side=tk.LEFT, padx=5)
        
        btn_cancelar = ttk.Button(frame_btn, text="✗ Cancelar", 
                                 command=janela_edit.destroy,
                                 style='Custom.TButton')
        btn_cancelar.pack(side=tk.LEFT, padx=5)
        
        entry_value_edit.bind('<Return>', lambda e: salvar_edicao())
        
        frame.columnconfigure(1, weight=1)
        
    def remover_dado(self):
        """Remove o dado selecionado e seus dados opcionais"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Atenção", "Selecione um item para remover!")
            return
        
        # Usar mapa para obter índice original
        item_id = selected[0]
        index = self.mapa_indices.get(item_id, self.tree.index(item_id))
        
        del self.labels[index]
        del self.values[index]
        
        if index < len(self.dados_periodo_anterior):
            del self.dados_periodo_anterior[index]
        if index < len(self.tempo_resolucao):
            del self.tempo_resolucao[index]
        if index < len(self.informacoes_adicionais):
            del self.informacoes_adicionais[index]
        
        if self.dados_periodo_anterior or self.tempo_resolucao or self.informacoes_adicionais:
            self.usar_dados_avancados = any(self.dados_periodo_anterior) or any(self.tempo_resolucao) or any(self.informacoes_adicionais)
        else:
            self.usar_dados_avancados = False
        
        self.atualizar_tabela_dados()
        self.atualizar_analise()
        
    def limpar_dados(self):
        """Limpa todos os dados incluindo opcionais"""
        if not self.labels:
            return
        
        if messagebox.askyesno("Confirmar", "Deseja limpar todos os dados?"):
            self.labels = []
            self.values = []
            self.dados_periodo_anterior = []
            self.tempo_resolucao = []
            self.informacoes_adicionais = []
            self.dados_temporais = {}
            self.usar_dados_avancados = False
            self.ordem_crescente = False
            self.mapa_indices = {}
            
            self.tree.delete(*self.tree.get_children())
            self.analise = None
            self.btn_ordenar.config(text="⬆️ Crescente")
            
            for widget in self.canvas_frame.winfo_children():
                widget.destroy()
            self.label_placeholder = ttk.Label(self.canvas_frame, 
                                              text="Adicione dados e selecione um tipo de gráfico",
                                              font=('Arial', 12))
            self.label_placeholder.grid(row=0, column=0)
    
    def carregar_exemplo(self):
        """Carrega dados de exemplo com dados opcionais"""
        self.limpar_dados()
        
        exemplos = [
            ("Duplicidade de usuário", 124, 98, 4.5, "3100,3102,3103"),
            ("Conexão base de dados", 51, 45, 2.3, "3107"),
            ("Rotina EnviarNFSincrono", 41, 52, 3.1, "3106,3108"),
            ("Erro Confirmar NF", 36, 28, 5.2, "3105"),
            ("Consumo indevido", 32, 40, 1.8, "3104"),
            ("Rejeição Alíquota IBS", 23, 19, 3.7, "3109")
        ]
        
        for label, value, periodo_ant, tempo_res, info_adicionais in exemplos:
            self.labels.append(label)
            self.values.append(value)
            self.dados_periodo_anterior.append(periodo_ant)
            self.tempo_resolucao.append(tempo_res)
            self.informacoes_adicionais.append(info_adicionais)
        
        self.usar_dados_avancados = True
        self.atualizar_tabela_dados()
        self.atualizar_analise()
        messagebox.showinfo("Sucesso", "Dados de exemplo carregados com dados avançados!\n" +
                           "Agora você pode usar todos os gráficos incluindo comparativo e dispersão.")
        
    def carregar_dados(self):
        """Carrega dados de um arquivo JSON"""
        filename = filedialog.askopenfilename(
            title="Carregar Dados",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.limpar_dados()
            self.labels = data['labels']
            self.values = data['values']
            
            # Carregarpara compatibilidade com arquivos antigos
            self.dados_periodo_anterior = data.get('dados_periodo_anterior', [])
            self.tempo_resolucao = data.get('tempo_resolucao', [])
            self.informacoes_adicionais = data.get('informacoes_adicionais', [])
            
            # Garantir que as listas têm o mesmo tamanho
            while len(self.dados_periodo_anterior) < len(self.labels):
                self.dados_periodo_anterior.append(None)
            while len(self.tempo_resolucao) < len(self.labels):
                self.tempo_resolucao.append(None)
            while len(self.informacoes_adicionais) < len(self.labels):
                self.informacoes_adicionais.append(None)
            
            if any(self.dados_periodo_anterior) or any(self.tempo_resolucao) or any(self.informacoes_adicionais):
                self.usar_dados_avancados = True
            
            self.atualizar_tabela_dados()
            self.atualizar_analise()
            messagebox.showinfo("Sucesso", f"Dados carregados de {filename}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar arquivo: {str(e)}")
    
    def salvar_dados(self):
        """Salva dados em um arquivo JSON"""
        if not self.labels:
            messagebox.showwarning("Atenção", "Não há dados para salvar!")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Salvar Dados",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            data = {
                'labels': self.labels,
                'values': [int(v) for v in self.values],
                'dados_periodo_anterior': self.dados_periodo_anterior,
                'tempo_resolucao': self.tempo_resolucao,
                'informacoes_adicionais': self.informacoes_adicionais
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Sucesso", f"Dados salvos em {filename}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar arquivo: {str(e)}")
    
    def atualizar_analise(self):
        """Atualiza o objeto de análise com dados opcionais (ordenados conforme exibição)"""
        if len(self.labels) >= 2:
            # Obter índices ordenados conforme exibição na tabela
            indices = list(range(len(self.labels)))
            if self.ordem_crescente:
                indices.sort(key=lambda i: self.values[i])  # Crescente
            else:
                indices.sort(key=lambda i: self.values[i], reverse=True)  # Decrescente
            
            # Reordenar os dados na mesma sequência
            labels_ordenados = [self.labels[i] for i in indices]
            values_ordenados = [self.values[i] for i in indices]
            
            periodo_ant = None
            tempo_res = None
            info_adicionais = None
            
            if self.usar_dados_avancados:
                if self.dados_periodo_anterior and len(self.dados_periodo_anterior) == len(self.values):
                    periodo_ant = [self.dados_periodo_anterior[i] for i in indices]
                
                if self.tempo_resolucao and len(self.tempo_resolucao) == len(self.values):
                    tempo_res = [self.tempo_resolucao[i] for i in indices]
                
                if self.informacoes_adicionais and len(self.informacoes_adicionais) == len(self.values):
                    info_adicionais = [self.informacoes_adicionais[i] for i in indices]
            
            self.analise = AnaliseDados(
                labels_ordenados, 
                values_ordenados,
                periodo_anterior=periodo_ant,
                tempo_resolucao=tempo_res,
                informacoes_adicionais=info_adicionais
            )
        else:
            self.analise = None
    
    def gerar_grafico(self, tipo):
        """Gera o gráfico selecionado"""
        if not self.analise:
            messagebox.showwarning("Atenção", "Adicione pelo menos 2 dados para gerar gráficos!")
            return
        
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
        
        funcoes = {
            'barras_vertical': self.analise.grafico_barras_vertical,
            'barras_horizontal': self.analise.grafico_barras_horizontal,
            'pizza': self.analise.grafico_pizza,
            'pareto': self.analise.grafico_pareto,
            'linha': self.analise.grafico_linha_tendencia,
            'area': self.analise.grafico_area_empilhada,
            'comparativo': self.analise.grafico_comparativo_duplo,
            'dispersao': self.analise.grafico_dispersao_analise,
            'dashboard': self.analise.dashboard_completo
        }
        
        try:
            self.root.config(cursor="wait")
            self.root.update()
            
            fig = funcoes[tipo]()
            
            canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
            canvas.draw()
            
            from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
            
            toolbar_frame = ttk.Frame(self.canvas_frame)
            toolbar_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
            toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
            toolbar.update()
            
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            self.canvas_frame.columnconfigure(0, weight=1)
            self.canvas_frame.rowconfigure(1, weight=1)
            
            self.current_figure = fig
            self.current_canvas = canvas
            
            def on_scroll(event):
                if event.button == 'up':
                    self.zoom_in()
                elif event.button == 'down':
                    self.zoom_out()
            
            canvas.mpl_connect('scroll_event', on_scroll)
            
            self.canvas_frame.update_idletasks()
            self.on_frame_configure()
            
            self.canvas_container.yview_moveto(0)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar gráfico: {str(e)}")
        finally:
            self.root.config(cursor="")
    
    def salvar_grafico_png(self):
        """Salva o gráfico atual como PNG"""
        if not hasattr(self, 'current_figure'):
            messagebox.showwarning("Atenção", "Gere um gráfico primeiro!")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Salvar Gráfico",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.current_figure.savefig(filename, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Sucesso", f"Gráfico salvo em {filename}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar gráfico: {str(e)}")
    
    def gerar_relatorio(self):
        """Gera relatório estatístico em uma nova janela"""
        if not self.analise:
            messagebox.showwarning("Atenção", "Adicione dados primeiro!")
            return
        
        janela_relatorio = tk.Toplevel(self.root)
        janela_relatorio.title("Relatório Estatístico")
        janela_relatorio.geometry("600x500")
        
        text_widget = scrolledtext.ScrolledText(janela_relatorio, wrap=tk.WORD, 
                                               font=('Courier', 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        relatorio = self.gerar_texto_relatorio()
        text_widget.insert('1.0', relatorio)
        text_widget.config(state=tk.DISABLED)
        
        btn_fechar = ttk.Button(janela_relatorio, text="Fechar", 
                               command=janela_relatorio.destroy)
        btn_fechar.pack(pady=5)
    
    def gerar_texto_relatorio(self):
        """Gera o texto do relatório"""
        relatorio = "=" * 60 + "\n"
        relatorio += "RELATÓRIO ESTATÍSTICO COMPLETO\n"
        relatorio += "=" * 60 + "\n\n"
        
        relatorio += f"Total de Incidentes: {int(self.analise.total)}\n"
        relatorio += f"Média: {np.mean(self.analise.values):.2f}\n"
        relatorio += f"Mediana: {np.median(self.analise.values):.2f}\n"
        relatorio += f"Desvio Padrão: {np.std(self.analise.values):.2f}\n"
        relatorio += f"Variância: {np.var(self.analise.values):.2f}\n"
        relatorio += f"Mínimo: {int(np.min(self.analise.values))}\n"
        relatorio += f"Máximo: {int(np.max(self.analise.values))}\n"
        relatorio += f"Amplitude: {int(np.max(self.analise.values) - np.min(self.analise.values))}\n\n"
        
        relatorio += "-" * 60 + "\n"
        relatorio += "DISTRIBUIÇÃO POR CATEGORIA\n"
        relatorio += "-" * 60 + "\n"
        
        for i, label in enumerate(self.analise.labels):
            relatorio += f"{label:30} | {int(self.analise.values[i]):4} | {self.analise.percentages[i]:5.1f}%\n"
        
        relatorio += "\n" + "-" * 60 + "\n"
        relatorio += "TOP 3 CATEGORIAS\n"
        relatorio += "-" * 60 + "\n"
        
        top_indices = np.argsort(self.analise.values)[::-1][:3]
        for i, idx in enumerate(top_indices, 1):
            relatorio += f"{i}. {self.analise.labels[idx]:30} | {int(self.analise.values[idx])} itens\n"
        
        relatorio += "\n" + "=" * 60
        
        return relatorio
    
    def gerar_todos_graficos(self):
        """Gera e salva todos os tipos de gráficos"""
        if not self.analise:
            messagebox.showwarning("Atenção", "Adicione dados primeiro!")
            return
        
        pasta = filedialog.askdirectory(title="Selecione a pasta para salvar os gráficos")
        if not pasta:
            return
        
        graficos = [
            ("01_barras_vertical", self.analise.grafico_barras_vertical),
            ("02_barras_horizontal", self.analise.grafico_barras_horizontal),
            ("03_pizza", self.analise.grafico_pizza),
            ("04_pareto", self.analise.grafico_pareto),
            ("05_linha_tendencia", self.analise.grafico_linha_tendencia),
            ("06_area_empilhada", self.analise.grafico_area_empilhada),
            ("07_comparativo_duplo", self.analise.grafico_comparativo_duplo),
            ("08_dispersao", self.analise.grafico_dispersao_analise),
            ("09_dashboard", self.analise.dashboard_completo)
        ]
        
        sucesso = 0
        for nome, funcao in graficos:
            try:
                fig = funcao()
                fig.savefig(f'{pasta}/{nome}.png', dpi=300, bbox_inches='tight')
                plt.close(fig)
                sucesso += 1
            except Exception as e:
                print(f"Erro ao gerar {nome}: {e}")
        
        messagebox.showinfo("Concluído", 
                           f"{sucesso}/{len(graficos)} gráficos salvos em:\n{pasta}")
    
    def exportar_pdf_completo(self):
        """Exporta relatório completo em PDF"""
        if not self.analise:
            messagebox.showwarning("Atenção", "Adicione dados primeiro!")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Salvar Relatório PDF",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            self.root.config(cursor="wait")
            self.root.update()
            
            sucesso = ExportadorPDF.gerar_pdf_completo(
                self.labels, 
                self.values, 
                filename,
                self.analise
            )
            
            if sucesso:
                messagebox.showinfo("Sucesso", 
                    f"✓ Relatório PDF completo salvo em:\n{filename}\n\n" +
                    "O PDF inclui:\n" +
                    "• Estatísticas gerais\n" +
                    "• Tabela de distribuição\n" +
                    "• Dashboard completo\n" +
                    "• Análise TOP 5")
            else:
                messagebox.showerror("Erro", "Erro ao gerar PDF")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar PDF:\n{str(e)}")
        finally:
            self.root.config(cursor="")
    
    def importar_imagem(self):
        """Importa dados de uma imagem usando OCR"""
        from tratamento_dados import ProcessadorImagemBI
        
        instalado, mensagem = ProcessadorImagemBI.verificar_tesseract_instalado()
        
        if not instalado:
            resposta = messagebox.askquestion(
                "Tesseract-OCR não disponível",
                f"{mensagem}\n\n" +
                "❌ A importação de imagens requer Tesseract-OCR instalado.\n\n" +
                "✅ ALTERNATIVA FÁCIL: Use 'Colar Texto do BI'\n\n" +
                "Deseja ver instruções de instalação do Tesseract?",
                icon='warning'
            )
            
            if resposta == 'yes':
                self.mostrar_instrucoes_tesseract()
            
            if messagebox.askyesno("Usar alternativa?", 
                                  "Deseja usar 'Colar Texto do BI' ao invés?\n\n" +
                                  "É mais fácil e funciona sem instalação adicional!"):
                self.colar_texto_bi()
            return
        
        filename = filedialog.askopenfilename(
            title="Selecionar Imagem do BI",
            filetypes=[
                ("Imagens", "*.png *.jpg *.jpeg *.bmp *.gif"),
                ("PNG", "*.png"),
                ("JPEG", "*.jpg *.jpeg"),
                ("Todos", "*.*")
            ]
        )
        
        if not filename:
            return
        
        self.root.config(cursor="wait")
        self.root.update()
        
        try:
            resultado = ProcessadorImagemBI.processar_imagem_bi(filename)
            
            if 'erro' in resultado:
                msg = f"{resultado['erro']}\n\n{resultado['mensagem']}"
                if 'instrucoes' in resultado:
                    msg += "\n\n" + "\n".join(resultado['instrucoes'])
                messagebox.showerror("Erro", msg)
                
                if resultado.get('solucao_alternativa') == 'colar_texto':
                    if messagebox.askyesno("Alternativa", 
                                          "Deseja usar 'Colar Texto do BI' ao invés?"):
                        self.colar_texto_bi()
                        
            elif 'labels' in resultado and len(resultado['labels']) > 0:
                self.limpar_dados()
                
                self.labels = resultado['labels']
                self.values = resultado['values']
                
                for label, value in zip(self.labels, self.values):
                    self.tree.insert('', tk.END, values=(label, int(value)))
                
                self.atualizar_analise()
                
                msg = f"✓ Extraídos {len(self.labels)} itens da imagem!\n\n"
                if 'texto_bruto' in resultado:
                    msg += "Texto detectado:\n" + resultado['texto_bruto'][:200]
                
                messagebox.showinfo("Sucesso", msg)
            else:
                messagebox.showwarning("Atenção", 
                    "Não foi possível extrair dados da imagem.\n\n" +
                    "Dicas:\n" +
                    "- Certifique-se que a imagem tem boa qualidade\n" +
                    "- O texto deve estar legível\n" +
                    "- Tente usar a opção 'Colar Texto do BI'")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar imagem:\n{str(e)}")
        finally:
            self.root.config(cursor="")
    
    def colar_texto_bi(self):
        """Abre janela para colar texto copiado do BI"""
        janela = tk.Toplevel(self.root)
        janela.title("Colar Texto do BI")
        janela.geometry("600x500")
        
        instrucoes = ttk.Label(janela, 
            text="Cole aqui o texto copiado do seu BI\n" +
                 "Formatos aceitos:\n" +
                 "• Nome do serviço 123\n" +
                 "• Nome do serviço: 123\n" +
                 "• Nome do serviço | 123\n" +
                 "• 123 Nome do serviço",
            justify=tk.LEFT,
            font=('Arial', 9))
        instrucoes.pack(pady=10, padx=10)
        
        texto_widget = scrolledtext.ScrolledText(janela, wrap=tk.WORD, 
                                                 font=('Courier', 10),
                                                 height=20)
        texto_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        exemplo = """Duplicidade de usuário 124
Conexão base de dados 51
Rotina EnviarNFSincrono 41
Erro Confirmar NF 36
Consumo indevido 32
Rejeição Alíquota IBS 23"""
        texto_widget.insert('1.0', exemplo)
        texto_widget.tag_add("exemplo", "1.0", "end")
        texto_widget.tag_config("exemplo", foreground="gray")
        
        def processar_texto():
            texto = texto_widget.get('1.0', tk.END)
            
            if not texto.strip():
                messagebox.showwarning("Atenção", "Cole o texto primeiro!")
                return
            
            resultado = TratamentoDados.extrair_dados_texto_manual(texto)
            
            if 'labels' in resultado and len(resultado['labels']) > 0:
                self.limpar_dados()
                
                self.labels = resultado['labels']
                self.values = resultado['values']
                
                for label, value in zip(self.labels, self.values):
                    self.tree.insert('', tk.END, values=(label, int(value)))
                
                self.atualizar_analise()
                
                messagebox.showinfo("Sucesso", 
                    f"✓ Extraídos {len(self.labels)} itens do texto!")
                janela.destroy()
            else:
                messagebox.showwarning("Atenção", 
                    "Não foi possível extrair dados do texto.\n\n" +
                    "Verifique se o formato está correto.")
        
        frame_btn = ttk.Frame(janela)
        frame_btn.pack(pady=10)
        
        btn_processar = ttk.Button(frame_btn, text="✓ Processar Texto", 
                                   command=processar_texto)
        btn_processar.pack(side=tk.LEFT, padx=5)
        
        btn_cancelar = ttk.Button(frame_btn, text="✗ Cancelar", 
                                 command=janela.destroy)
        btn_cancelar.pack(side=tk.LEFT, padx=5)
    
    def importar_csv_excel(self):
        """Importa dados de arquivo CSV ou Excel"""
        filename = filedialog.askopenfilename(
            title="Selecionar Arquivo",
            filetypes=[
                ("CSV", "*.csv"),
                ("Excel", "*.xlsx *.xls"),
                ("Todos", "*.*")
            ]
        )
        
        if not filename:
            return
        
        try:
            if filename.lower().endswith('.csv'):
                resultado = TratamentoDados.extrair_dados_csv(filename)
            elif filename.lower().endswith(('.xlsx', '.xls')):
                resultado = TratamentoDados.extrair_dados_excel(filename)
            else:
                messagebox.showerror("Erro", "Formato de arquivo não suportado")
                return
            
            if 'erro' in resultado:
                messagebox.showerror("Erro", 
                    f"{resultado['erro']}\n\n{resultado['mensagem']}")
            elif 'labels' in resultado and len(resultado['labels']) > 0:
                self.limpar_dados()
                
                self.labels = resultado['labels']
                self.values = resultado['values']
                
                for label, value in zip(self.labels, self.values):
                    self.tree.insert('', tk.END, values=(label, int(value)))
                
                self.atualizar_analise()
                
                messagebox.showinfo("Sucesso", 
                    f"✓ Importados {len(self.labels)} itens do arquivo!")
            else:
                messagebox.showwarning("Atenção", 
                    "Não foi possível extrair dados do arquivo.")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao importar arquivo:\n{str(e)}")
    
    def mostrar_instrucoes_tesseract(self):
        """Mostra instruções detalhadas de instalação do Tesseract"""
        janela = tk.Toplevel(self.root)
        janela.title("Instalação do Tesseract-OCR")
        janela.geometry("700x600")
        
        text_widget = scrolledtext.ScrolledText(janela, wrap=tk.WORD, 
                                               font=('Courier', 9))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        instrucoes = """
═══════════════════════════════════════════════════════════════
📥 INSTALAÇÃO DO TESSERACT-OCR
═══════════════════════════════════════════════════════════════

⚠️  IMPORTANTE: O Tesseract é necessário APENAS para importar imagens.
    Para a maioria dos casos, use "Colar Texto do BI" que não precisa 
    de instalação adicional!

═══════════════════════════════════════════════════════════════
🪟 WINDOWS (Mais Fácil)
═══════════════════════════════════════════════════════════════

1. BAIXAR O INSTALADOR:
   Link: https://github.com/UB-Mannheim/tesseract/wiki
   
   Ou busque no Google: "tesseract windows download"
   
   Baixe: tesseract-ocr-w64-setup-v5.x.x.exe
          (versão mais recente)

2. INSTALAR:
   • Execute o arquivo baixado
   • Durante a instalação:
     ✓ IMPORTANTE: Marque "Add to PATH" (Adicionar ao PATH)
     ✓ Instale o idioma "Portuguese" (Português)
   • Clique em "Next" até finalizar

3. VERIFICAR INSTALAÇÃO:
   • Abra o Prompt de Comando (cmd)
   • Digite: tesseract --version
   • Se mostrar a versão, está instalado!

4. INSTALAR BIBLIOTECA PYTHON:
   • Abra o terminal
   • Digite: pip install pytesseract pillow
   • Aguarde a instalação

5. REINICIAR:
   • Feche este programa
   • Abra novamente
   • Agora "Importar de Imagem" funcionará!

═══════════════════════════════════════════════════════════════
🐧 LINUX (Ubuntu/Debian)
═══════════════════════════════════════════════════════════════

1. INSTALAR TESSERACT:
   sudo apt-get update
   sudo apt-get install tesseract-ocr
   sudo apt-get install tesseract-ocr-por

2. INSTALAR BIBLIOTECA PYTHON:
   pip install pytesseract pillow

═══════════════════════════════════════════════════════════════
🍎 MACOS
═══════════════════════════════════════════════════════════════

1. INSTALAR COM HOMEBREW:
   brew install tesseract
   brew install tesseract-lang

2. INSTALAR BIBLIOTECA PYTHON:
   pip install pytesseract pillow

═══════════════════════════════════════════════════════════════
✅ ALTERNATIVA RECOMENDADA (SEM INSTALAÇÃO)
═══════════════════════════════════════════════════════════════

USE "📝 COLAR TEXTO DO BI":

1. No seu BI/Dashboard, selecione os dados com o mouse
2. Copie com Ctrl+C
3. Clique em "📝 Colar Texto do BI" no programa
4. Cole com Ctrl+V
5. Clique em "Processar"

✓ Mais rápido
✓ Mais confiável
✓ Sem instalação adicional
✓ Funciona com qualquer BI

═══════════════════════════════════════════════════════════════
❓ PROBLEMAS?
═══════════════════════════════════════════════════════════════

• "Comando não encontrado": Tesseract não está no PATH
  Solução: Reinstale marcando "Add to PATH"

• "Erro ao processar": Imagem pode ter baixa qualidade
  Solução: Use "Colar Texto do BI"

• Outras dúvidas: Use sempre "Colar Texto do BI"!

═══════════════════════════════════════════════════════════════
        """
        
        text_widget.insert('1.0', instrucoes)
        text_widget.config(state=tk.DISABLED)
        
        frame_btn = ttk.Frame(janela)
        frame_btn.pack(pady=10)
        
        def abrir_link():
            import webbrowser
            webbrowser.open('https://github.com/UB-Mannheim/tesseract/wiki')
        
        btn_link = ttk.Button(frame_btn, text="🌐 Abrir Página de Download", 
                             command=abrir_link)
        btn_link.pack(side=tk.LEFT, padx=5)
        
        btn_fechar = ttk.Button(frame_btn, text="Fechar", 
                               command=janela.destroy)
        btn_fechar.pack(side=tk.LEFT, padx=5)
    
    def zoom_in(self):
        """Aplica zoom in no gráfico atual"""
        if not hasattr(self, 'current_figure'):
            messagebox.showwarning("Atenção", "Gere um gráfico primeiro!")
            return
        
        try:
            axes = self.current_figure.get_axes()
            for ax in axes:
                tem_pizza = any(hasattr(item, 'theta1') for item in ax.patches)
                
                if tem_pizza:
                    continue
                
                xlim = ax.get_xlim()
                ylim = ax.get_ylim()
                
                x_center = (xlim[0] + xlim[1]) / 2
                y_center = (ylim[0] + ylim[1]) / 2
                x_range = (xlim[1] - xlim[0]) * 0.4
                y_range = (ylim[1] - ylim[0]) * 0.4
                
                ax.set_xlim(x_center - x_range, x_center + x_range)
                ax.set_ylim(y_center - y_range, y_center + y_range)
            
            self.current_canvas.draw()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao aplicar zoom: {str(e)}")
    
    def zoom_out(self):
        """Aplica zoom out no gráfico atual"""
        if not hasattr(self, 'current_figure'):
            messagebox.showwarning("Atenção", "Gere um gráfico primeiro!")
            return
        
        try:
            axes = self.current_figure.get_axes()
            for ax in axes:
                tem_pizza = any(hasattr(item, 'theta1') for item in ax.patches)
                
                if tem_pizza:
                    continue
                
                xlim = ax.get_xlim()
                ylim = ax.get_ylim()
                
                x_center = (xlim[0] + xlim[1]) / 2
                y_center = (ylim[0] + ylim[1]) / 2
                x_range = (xlim[1] - xlim[0]) * 0.575
                y_range = (ylim[1] - ylim[0]) * 0.575
                
                ax.set_xlim(x_center - x_range, x_center + x_range)
                ax.set_ylim(y_center - y_range, y_center + y_range)
            
            self.current_canvas.draw()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao aplicar zoom: {str(e)}")
    
    def mostrar_guia_graficos(self):
        """Mostra guia completo sobre os tipos de gráficos"""
        janela = tk.Toplevel(self.root)
        janela.title("📊 Guia Completo de Gráficos")
        janela.geometry("900x700")
        
        text_widget = scrolledtext.ScrolledText(janela, wrap=tk.WORD, 
                                               font=('Courier', 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        guia_texto = """
═══════════════════════════════════════════════════════════════
📊 GUIA COMPLETO DE GRÁFICOS - QUANDO E COMO USAR
═══════════════════════════════════════════════════════════════

📊 1. GRÁFICO DE BARRAS VERTICAL
═══════════════════════════════════════════════════════════════

O QUE FAZ:
• Compara valores entre diferentes categorias
• Mostra a magnitude de cada categoria de forma vertical
• Ideal para comparações diretas entre itens

QUANDO USAR:
✓ Quando você tem até 10 categorias
✓ Para comparar quantidades absolutas
✓ Quando os nomes das categorias são curtos
✓ Para apresentações formais e relatórios

PARÂMETROS IMPORTANTES:
• Valores: Quantidades absolutas (números positivos)
• Ordenação: Automática por valor (maior para menor)
• Cores: Gradiente de azul (claro para escuro)

EXEMPLO DE USO:
"Quantos incidentes cada serviço teve neste mês?"
"Qual categoria teve mais problemas?"


📊 2. GRÁFICO DE BARRAS HORIZONTAL
═══════════════════════════════════════════════════════════════

O QUE FAZ:
• Similar ao vertical, mas com barras horizontais
• Melhor legibilidade para nomes longos
• Facilita comparação de muitos itens

QUANDO USAR:
✓ Quando os nomes das categorias são longos
✓ Para mais de 10 categorias
✓ Quando precisa de melhor legibilidade
✓ Para rankings e listas ordenadas

PARÂMETROS IMPORTANTES:
• Valores: Quantidades absolutas
• Ordenação: Do maior para o menor
• Labels: Podem ter até 50 caracteres sem cortar

EXEMPLO DE USO:
"Ranking de serviços com mais erros"
"Lista completa de incidentes por tipo"


🥧 3. GRÁFICO DE PIZZA
═══════════════════════════════════════════════════════════════

O QUE FAZ:
• Mostra proporções e porcentagens do total
• Visualiza a distribuição relativa entre categorias
• Destaca a participação de cada item no todo

QUANDO USAR:
✓ Para mostrar porcentagens e proporções
✓ Quando tem até 7 categorias
✓ Para visualizar a distribuição do todo
✓ Quando as proporções são significativas (>5%)

PARÂMETROS IMPORTANTES:
• Valores: Convertidos automaticamente em percentuais
• Total: Soma de todos os valores = 100%
• Destaque: Fatia maior é automaticamente destacada
• Percentuais: Mostrados em cada fatia se >3%

EXEMPLO DE USO:
"Qual percentual cada erro representa do total?"
"Distribuição proporcional dos incidentes"


📈 4. GRÁFICO DE PARETO (80/20)
═══════════════════════════════════════════════════════════════

O QUE FAZ:
• Identifica os "poucos vitais" vs "muitos triviais"
• Mostra barras (valores) + linha (acumulado %)
• Aplica o princípio 80/20 automaticamente

QUANDO USAR:
✓ Para priorização de problemas
✓ Identificar principais causas
✓ Análise de impacto e foco de esforços
✓ Decidir onde atuar primeiro

PARÂMETROS IMPORTANTES:
• Valores: Quantidades absolutas
• Ordenação: Sempre do maior para menor
• Linha acumulada: Mostra % acumulado até 100%
• Zona crítica: Destaque nos primeiros 80%

EXEMPLO DE USO:
"Quais 20% dos erros causam 80% dos problemas?"
"Onde devemos focar nossos esforços?"
"TOP 3 categorias que resolvem 80% dos casos"


📉 5. GRÁFICO DE LINHA/TENDÊNCIA
═══════════════════════════════════════════════════════════════

O QUE FAZ:
• Mostra evolução e tendências
• Conecta pontos para visualizar padrão
• Adiciona linha de tendência (regressão)

QUANDO USAR:
✓ Para visualizar evolução temporal
✓ Identificar tendências (crescimento/queda)
✓ Comparar progressão de valores
✓ Análise de séries temporais

PARÂMETROS IMPORTANTES:
• Ordem: Sequência importa (cronológica ou lógica)
• Tendência: Linha tracejada mostra direção
• Pontos: Marcados para cada categoria
• Inclinação: Positiva (subindo) ou negativa (caindo)

EXEMPLO DE USO:
"Os incidentes estão aumentando ou diminuindo?"
"Qual a tendência para os próximos meses?"


📊 6. GRÁFICO DE ÁREA EMPILHADA
═══════════════════════════════════════════════════════════════

O QUE FAZ:
• Mostra valores individuais E total acumulado
• Preenche área abaixo da linha
• Visualiza contribuição de cada categoria no tempo

QUANDO USAR:
✓ Para mostrar composição do total ao longo do tempo
✓ Visualizar volume total + partes
✓ Comparar contribuição relativa
✓ Análise de evolução conjunta

PARÂMETROS IMPORTANTES:
• Empilhamento: Cada área soma à anterior
• Total: Altura máxima = soma de todos
• Cores: Diferentes para cada categoria
• Transparência: Permite ver sobreposições

EXEMPLO DE USO:
"Como cada tipo de erro contribui para o total?"
"Evolução do volume total e suas partes"


📊 7. GRÁFICO COMPARATIVO DUPLO
═══════════════════════════════════════════════════════════════

O QUE FAZ:
• Compara valores reais vs proporções (%)
• Dois eixos Y: valores absolutos e percentuais
• Barra + linha no mesmo gráfico

QUANDO USAR:
✓ Para análise dupla: quantidade E proporção
✓ Comparar impacto absoluto vs relativo
✓ Entender contexto completo de cada categoria

PARÂMETROS IMPORTANTES:
• Eixo esquerdo: Valores absolutos (barras)
• Eixo direito: Percentuais (linha)
• Cores: Azul (barras) e vermelho (linha %)
• Dual: Leitura simultânea de dois aspectos

EXEMPLO DE USO:
"Este erro tem muito volume OU alto percentual?"
"Análise dupla: quantidade absoluta e participação %"


🔵 8. GRÁFICO DE DISPERSÃO COM ANÁLISE
═══════════════════════════════════════════════════════════════

O QUE FAZ:
• Analisa distribuição e outliers (pontos fora do padrão)
• Mostra pontos individuais + média + desvio padrão
• Identifica valores atípicos automaticamente

QUANDO USAR:
✓ Para identificar anomalias e outliers
✓ Visualizar distribuição dos dados
✓ Análise estatística visual
✓ Encontrar padrões e exceções

PARÂMETROS IMPORTANTES:
• Pontos: Cada categoria como um ponto
• Média: Linha horizontal verde
• Desvio: Área sombreada (±1σ)
• Outliers: Pontos fora da área sombreada (vermelhos)
• Estatísticas: Média, mediana, desvio no rodapé

EXEMPLO DE USO:
"Existem valores muito discrepantes?"
"Quais categorias fogem do padrão?"
"Identificar erros excepcionais vs normais"


📋 9. DASHBOARD COMPLETO
═══════════════════════════════════════════════════════════════

O QUE FAZ:
• Combina 6 visualizações diferentes em uma tela
• Visão 360° dos dados
• Análise multidimensional integrada

COMPONENTES:
1. Barras Vertical - Comparação básica
2. Pizza - Distribuição proporcional
3. Pareto - Priorização 80/20
4. Linha - Tendência e evolução
5. Área - Volume acumulado
6. Dispersão - Análise estatística

QUANDO USAR:
✓ Para apresentações executivas
✓ Visão geral completa dos dados
✓ Relatórios gerenciais
✓ Quando precisa de múltiplas perspectivas
✓ Para exportar análise completa

PARÂMETROS IMPORTANTES:
• Todos os parâmetros dos 6 gráficos combinados
• Layout: Grade 3x2 otimizada
• Cores: Coordenadas entre gráficos
• Espaçamento: Ajustado para legibilidade

EXEMPLO DE USO:
"Preciso de uma visão completa de tudo"
"Apresentação para gerência com todas as análises"


═══════════════════════════════════════════════════════════════
💡 DICAS DE ESCOLHA DO GRÁFICO CERTO
═══════════════════════════════════════════════════════════════

❓ QUAL GRÁFICO USAR QUANDO...

→ Quero COMPARAR valores entre categorias?
  Use: Barras Vertical ou Horizontal

→ Quero ver PROPORÇÕES e percentuais?
  Use: Pizza

→ Preciso PRIORIZAR onde atuar primeiro?
  Use: Pareto

→ Quero ver TENDÊNCIAS e evolução?
  Use: Linha/Tendência

→ Preciso mostrar VOLUME TOTAL + partes?
  Use: Área Empilhada

→ Quero análise DUPLA (quantidade e %)?
  Use: Comparativo Duplo

→ Preciso identificar OUTLIERS e anomalias?
  Use: Dispersão

→ Quero VISÃO COMPLETA de tudo?
  Use: Dashboard


═══════════════════════════════════════════════════════════════
🎯 RECURSOS INTERATIVOS
═══════════════════════════════════════════════════════════════

ZOOM:
• Roleta do mouse: UP = Zoom In, DOWN = Zoom Out
• Botões: 🔍+ Zoom In e 🔍− Zoom Out
• Gráfico de pizza: Não sofre zoom (mantém proporção)

NAVEGAÇÃO:
• Use a toolbar acima do gráfico
• Pan: Mover o gráfico arrastando
• Home: Voltar à visualização original
• Salvar: Exportar imagem do gráfico

EXPORTAÇÃO:
• PNG: Alta qualidade (300 DPI)
• PDF: Relatório completo com estatísticas
• Todos: Gera todos os 9 gráficos de uma vez


═══════════════════════════════════════════════════════════════
        """
        
        text_widget.insert('1.0', guia_texto)
        text_widget.config(state=tk.DISABLED)
        
        btn_fechar = ttk.Button(janela, text="Fechar", 
                               command=janela.destroy)
        btn_fechar.pack(pady=5)
    
    def mostrar_ajuda(self):
        """Mostra janela de ajuda"""
        janela = tk.Toplevel(self.root)
        janela.title("Ajuda - ObservaBI")
        janela.geometry("700x600")
        
        text_widget = scrolledtext.ScrolledText(janela, wrap=tk.WORD, 
                                               font=('Arial', 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ajuda_texto = """
📊 ObservaBI - ANÁLISE INTELIGENTE DE DADOS - GUIA DE USO

═══════════════════════════════════════════════════════════════

🔹 COMO ADICIONAR DADOS:

1. MANUALMENTE
   • Digite a categoria no campo "Categoria"
   • Digite o valor numérico no campo "Valor"
   • Clique em "➕ Adicionar"

2. IMPORTAR DE IMAGEM (OCR)
   • Tire screenshot do seu BI/Dashboard
   • Clique em "🖼️ Importar de Imagem (OCR)"
   • Selecione a imagem (PNG, JPG)
   • Sistema extrai automaticamente os dados

3. COLAR TEXTO DO BI
   • Copie os dados do BI (Ctrl+C)
   • Clique em "📝 Colar Texto do BI"
   • Cole o texto na janela
   • Formatos aceitos:
     ✓ Nome do serviço 123
     ✓ Nome do serviço: 123
     ✓ Nome do serviço | 123
     ✓ 123 Nome do serviço

4. IMPORTAR ARQUIVOS
   • CSV/Excel: Clique em "📄 Importar CSV/Excel"
   • JSON: Clique em "📂 Carregar Dados (JSON)"

═══════════════════════════════════════════════════════════════

🎨 TIPOS DE GRÁFICOS:

📊 Barras Vertical - Gráfico clássico vertical
📊 Barras Horizontal - Melhor para nomes longos
🥧 Pizza - Distribuição em porcentagens
📈 Pareto - Análise 80/20 (principais causas)
📉 Linha/Tendência - Visualiza tendências
📊 Área Empilhada - Evolução temporal
📊 Comparativo - Compara períodos
🔵 Dispersão - Correlação entre variáveis
📋 Dashboard - Visão completa com 6 gráficos

═══════════════════════════════════════════════════════════════

💾 EXPORTAR RESULTADOS:

• Salvar Gráfico Individual: Clique em "💾 Salvar como PNG"
• Gerar Todos: Clique em "🖼️ Gerar Todos os Gráficos"
• Relatório: Clique em "📄 Gerar Relatório"

═══════════════════════════════════════════════════════════════

🔧 DICAS E TRUQUES:

✓ Use o toolbar de navegação acima do gráfico para zoom e pan
✓ Clique com botão direito para salvar gráfico rapidamente
✓ Dashboard é melhor visualizado em tela cheia
✓ Para redimensionar: arraste as bordas da janela
✓ Use scrollbar se o gráfico for muito grande

═══════════════════════════════════════════════════════════════

⚙️ REQUISITOS PARA OCR:

Para usar importação de imagens, instale:
1. pip install pytesseract pillow
2. Tesseract-OCR: github.com/UB-Mannheim/tesseract/wiki

═══════════════════════════════════════════════════════════════

❓ PROBLEMAS COMUNS:

• Gráfico não aparece: Adicione pelo menos 2 dados
• OCR não funciona: Use "Colar Texto do BI" como alternativa
• Texto cortado: Redimensione a janela ou use zoom
• Dashboard muito pequeno: Use scrollbar ou maximize janela

═══════════════════════════════════════════════════════════════

Desenvolvido com ❤️ usando Python, Matplotlib e Tkinter
        """
        
        text_widget.insert('1.0', ajuda_texto)
        text_widget.config(state=tk.DISABLED)
        
        btn_fechar = ttk.Button(janela, text="Fechar", 
                               command=janela.destroy)
        btn_fechar.pack(pady=5)

def main():
    root = tk.Tk()
    app = InterfaceAnalise(root)
    root.mainloop()


if __name__ == "__main__":
    main()
