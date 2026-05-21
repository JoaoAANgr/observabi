# 🚀 Guia de Instalação - ObservaBI

## 📦 Requisitos

- Python 3.7 ou superior
- pip (gerenciador de pacotes)
- ~200MB de espaço em disco

## ⚡ Instalação Rápida (5 minutos)

### 1. Clone o Repositório
```bash
git clone https://github.com/seu-usuario/observabi.git
cd observabi
```

### 2. Crie Ambiente Virtual
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instale Dependências
```bash
pip install -r requirements.txt
```

### 4. Execute
```bash
python main.py
```

## 🔧 Instalação do Tesseract (Opcional - para OCR)

Se deseja usar OCR para extrair texto de imagens:

### Windows
1. Baixe o instalador: https://github.com/UB-Mannheim/tesseract/wiki
2. Execute o instalador padrão
3. A aplicação detectará automaticamente

### Linux (Ubuntu/Debian)
```bash
sudo apt-get install tesseract-ocr
```

### macOS
```bash
brew install tesseract
```

## ✅ Verificar Instalação

```bash
python -c "import tkinter; print('✓ Tkinter OK')"
python -c "import matplotlib; print('✓ Matplotlib OK')"
python -c "import numpy; print('✓ NumPy OK')"
```

## 🎯 Próximos Passos

1. Abra a aplicação: `python main.py`
2. Clique em "Carregar Dados de Exemplo"
3. Selecione um gráfico
4. Exporte em PNG ou PDF

## 📱 Usar Executável (sem Python)

Se você baixou o arquivo `ObservaBI.exe`:
1. Simplesmente execute: `ObservaBI.exe`
2. Nenhuma instalação necessária!
3. Interface funciona em qualquer Windows

## 🐛 Problemas Comuns

**"Python não é reconhecido como comando"**
- Adicione Python ao PATH durante instalação
- Ou use: `python -m pip install ...`

**"ModuleNotFoundError"**
- Ative o ambiente virtual: `.venv\Scripts\activate`
- Reinstale dependências: `pip install -r requirements.txt`

**"Tesseract não encontrado"**
- OCR é opcional, não é obrigatório
- Se precisar, siga instruções acima

## 📞 Suporte

Consulte README.md para mais informações.
