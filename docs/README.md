# 📊 ObservaBI v2.0 - Documentação Completa

## 🎯 Sobre o Projeto

ObservaBI é um sistema moderno de análise de dados com interface gráfica responsiva, oferecendo **9 tipos de visualizações profissionais** e relatórios estatísticos avançados.

**Versão:** 2.0  
**Última atualização:** Maio 2026  
**Status:** ✅ Completo e pronto para produção

---

## 📋 Índice

1. [Instalação](#-instalação)
2. [Como Usar](#-como-usar)
3. [Funcionalidades](#-funcionalidades)
4. [Estrutura do Projeto](#-estrutura-do-projeto)
5. [Responsividade](#-responsividade)
6. [Gráficos Disponíveis](#-gráficos-disponíveis)
7. [Solução de Problemas](#-solução-de-problemas)

---

## 🔧 Instalação

### Pré-requisitos
- Python 3.7+
- pip ou conda

### Passo 1: Clonar Repositório
```bash
git clone https://github.com/seu-usuario/observabi.git
cd observabi
```

### Passo 2: Criar Ambiente Virtual
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### Passo 3: Instalar Dependências
```bash
pip install -r requirements.txt
```

### Passo 4 (Opcional): Instalar Tesseract para OCR
```bash
# Windows: Baixe em https://github.com/UB-Mannheim/tesseract/wiki
# Linux: sudo apt-get install tesseract-ocr
# Mac: brew install tesseract
```

---

## 🚀 Como Usar

### Iniciar a Aplicação
```bash
python main.py
```

### Modos de Uso

#### 1. Interface Gráfica (Recomendado)
```bash
python main.py
```
- Adicione dados manualmente
- Ou carregue dados de exemplo
- Selecione tipo de gráfico
- Exporte em PNG/PDF

#### 2. Modo CLI (Programático)
```bash
python main.py -c
```
- Executa análise com dados de exemplo
- Gera todos os 9 gráficos
- Salva em PNG 300 DPI

---

## ✨ Funcionalidades

### Análise de Dados
- ✅ Entrada manual de dados
- ✅ Importação de dados de exemplo
- ✅ Análise estatística completa
- ✅ Relatórios com estatísticas descritivas

### Visualizações (9 Tipos)
1. **Barras Vertical** - Comparação horizontal
2. **Barras Horizontal** - Comparação com labels longos
3. **Pizza** - Proporções e percentuais
4. **Pareto** - Regra 80/20
5. **Linha de Tendência** - Evolução temporal
6. **Área Empilhada** - Composição ao longo do tempo
7. **Comparativo Duplo** - Antes/Depois
8. **Dispersão/Análise** - Correlações
9. **Dashboard Completo** - Todos os 9 gráficos

### Exportação
- ✅ PNG (300 DPI - alta qualidade)
- ✅ PDF (relatório completo)
- ✅ Visualização em tempo real

### Interface
- ✅ 100% responsiva (adapta a qualquer tela)
- ✅ Suporte a 800x600 até 2560x1440
- ✅ Escalamento automático de fontes e layouts
- ✅ Intuitiva e fácil de usar

---

## 📁 Estrutura do Projeto

```
observabi/
├── main.py                      # Ponto de entrada unificado
├── interface.py                 # Interface gráfica responsiva
├── analise_avancada.py         # Engine de análise (9 gráficos)
├── tratamento_dados.py         # Processamento de dados
├── exportar_pdf.py             # Exportação em PDF
├── config.py                   # Configurações centralizadas
├── requirements.txt            # Dependências Python
├── .gitignore                  # Arquivo do Git
├── docs/                       # Documentação completa
│   ├── README.md              # Esta documentação
│   ├── INSTALACAO.md          # Guia de instalação detalhada
│   ├── RESPONSIVIDADE.md      # Documentação de responsividade
│   ├── ARQUITETURA.md         # Estrutura técnica
│   ├── CHANGELOG.md           # Histórico de versões
│   └── TROUBLESHOOTING.md     # Solução de problemas
├── dist/                       # Executável compilado
│   └── ObservaBI.exe          # Arquivo executável Windows
└── .venv/                      # Ambiente virtual
```

---

## 📱 Responsividade

### Como Funciona

A interface **detecta automaticamente** a resolução da sua tela e adapta:

- **Tamanho da janela** (até 90% da altura disponível)
- **Tamanho das fontes** (proporcionais)
- **Layout dos botões** (grid responsivo)
- **Dimensões das tabelas** (altura/colunas dinâmicas)

### Telas Suportadas

| Resolução | Notebook | Status |
|-----------|----------|--------|
| 1366x768 | 13" Pequeno | ✅ Perfeito |
| 1536x864 | 14-15" Médio | ✅ Perfeito |
| 1920x1080 | 15-17" Grande | ✅ Ótimo |
| 2560x1440 | 27" Desktop | ✅ Excelente |
| 800x600 | Antigos | ⚠️ Scrolls |

### Scale Factor

```
scale_factor = altura_janela / 800.0

Seu notebook (1536x864):
  scale_factor = 0.95
  Tudo será 95% do tamanho original
  Resultado: PERFEITO NA TELA ✓
```

---

## 📊 Gráficos Disponíveis

### 1. Barras Vertical
- Compara valores lado a lado
- Ideal para rankings
- Cores escalonadas

### 2. Barras Horizontal
- Labels longos ficam legíveis
- Melhor para textos grandes
- Ordenação automática

### 3. Pizza
- Proporções e percentuais
- Cores diferentes para cada fatia
- Percentuais na legenda

### 4. Pareto
- Regra 80/20 visual
- Combina barras + linha
- Identifica prioridades

### 5. Linha de Tendência
- Evolução temporal
- Conexão de pontos
- Perfeito para séries

### 6. Área Empilhada
- Composição ao longo do tempo
- Cores empilhadas
- Proporcionalidade mantida

### 7. Comparativo Duplo
- Antes vs Depois
- Período anterior vs atual
- Análise de mudanças

### 8. Dispersão/Análise
- Correlações entre variáveis
- Tempo de resolução vs complexidade
- Detecta padrões

### 9. Dashboard Completo
- Todos os 9 gráficos em 1 página
- Visão 360º dos dados
- Pronto para impressão

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Versão | Uso |
|-----------|--------|-----|
| Python | 3.7+ | Linguagem base |
| Tkinter | Built-in | Interface gráfica |
| Matplotlib | 3.5+ | Criação de gráficos |
| NumPy | 1.21+ | Cálculos numéricos |
| Pandas | 1.3+ | Processamento de dados |
| ReportLab | 3.6+ | Geração de PDF |
| Pillow | 8.0+ | Processamento de imagens |
| Pytesseract | 0.3+ | OCR (opcional) |

---

## 📝 Dependências

Ver arquivo `requirements.txt`:
```
matplotlib>=3.5.0
numpy>=1.21.0
pandas>=1.3.0
reportlab>=3.6.0
openpyxl>=3.6.0
Pillow>=8.0.0
pytesseract>=0.3.10
```

---

## 🐛 Solução de Problemas

### Problema: "ModuleNotFoundError: No module named 'matplotlib'"
**Solução:** Instale as dependências
```bash
pip install -r requirements.txt
```

### Problema: Interface muito pequena/grande
**Solução:** A interface se adapta automaticamente. Se precisar ajustar:

Edite `interface.py` linha 47:
```python
# Mais compacto:
window_height = max(600, int(screen_height * 0.85))

# Mais amplo:
window_height = max(600, int(screen_height * 0.95))
```

### Problema: Tesseract não encontrado (OCR)
**Solução:** OCR é opcional. Para usar:
```bash
# Windows: Baixe em https://github.com/UB-Mannheim/tesseract/wiki
# Linux: sudo apt-get install tesseract-ocr
# Mac: brew install tesseract
```

### Problema: Exportação PDF vazia
**Solução:** 
1. Carregue dados primeiro
2. Gere um gráfico
3. Tente exportar novamente

### Problema: Aplicação não inicia
**Solução:**
```bash
# Verifique se o ambiente está ativo:
.venv\Scripts\activate

# Reinstale dependências:
pip install -r requirements.txt --force-reinstall
```

---

## 📞 Suporte

- 📧 Email: seu-email@email.com
- 🐛 Issues: GitHub Issues
- 💬 Discussões: GitHub Discussions

---

## 📄 Licença

MIT License - Veja LICENSE para detalhes

---

## 👤 Desenvolvedor

Criado com ❤️ em 2026

---

## 🔄 Histórico de Versões

### v2.0 (Maio 2026)
- ✅ Interface 100% responsiva
- ✅ Consolidação de arquivos
- ✅ 9 tipos de gráficos
- ✅ Documentação completa
- ✅ Executável compilado
- ✅ Pronto para GitHub

### v1.0 (Inicial)
- Versão base com funcionalidades essenciais

---

**Última atualização:** Maio 2026  
**Versão:** 2.0  
**Status:** ✅ Pronto para produção
