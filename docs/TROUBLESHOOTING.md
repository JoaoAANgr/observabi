# 🔧 Troubleshooting - Solução de Problemas

## 🎯 Problemas Comuns

### ❌ Problema: "ModuleNotFoundError: No module named 'tkinter'"

**Causa:** Tkinter não está instalado (raro em Windows)

**Solução:**
```bash
# Windows - Reinstale Python com Tkinter
# Rode o instalador Python novamente e marque "tcl/tk and IDLE"

# Linux
sudo apt-get install python3-tk

# Mac
brew install python-tk
```

---

### ❌ Problema: "ModuleNotFoundError: No module named 'matplotlib'"

**Causa:** Dependências não foram instaladas

**Solução:**
```bash
# Certifique-se que o ambiente virtual está ativo
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Reinstale todas as dependências
pip install -r requirements.txt
```

---

### ❌ Problema: Interface muito pequena ou muito grande

**Causa:** Escala não está correta para sua resolução

**Solução 1 - Deixar adaptar automaticamente:**
- Basta usar normalmente, a interface se adapta!

**Solução 2 - Ajustar manualmente:**

Edite `interface.py` linha 47:

```python
# Para interface mais COMPACTA (abrir o zoom):
window_height = max(600, int(screen_height * 0.85))

# Para interface mais AMPLA (reduzir zoom):
window_height = max(600, int(screen_height * 0.95))
```

---

### ❌ Problema: Aplicação não inicia / Erro ao executar `python main.py`

**Causa:** Múltiplas possibilidades

**Solução:**

1. Verifique Python:
```bash
python --version  # Deve ser 3.7+
```

2. Ative ambiente virtual:
```bash
.venv\Scripts\activate
```

3. Reinstale tudo:
```bash
pip install -r requirements.txt --force-reinstall
```

4. Teste importações:
```bash
python -c "import tkinter; print('OK')"
python -c "import matplotlib; print('OK')"
python -c "import numpy; print('OK')"
```

5. Se ainda não funcionar, execute em modo debug:
```bash
python -u main.py
```

---

### ❌ Problema: Erro ao exportar PDF

**Causa:** Dados não foram carregados ou gráfico não foi gerado

**Solução:**

1. Carregue dados primeiro:
   - Clique em "Carregar Dados de Exemplo"

2. Gere um gráfico:
   - Selecione um tipo de gráfico

3. Então exporte:
   - Clique em "Exportar PDF"

---

### ❌ Problema: Tesseract não encontrado (OCR)

**Causa:** Tesseract não foi instalado corretamente

**Solução:**

1. **OCR é opcional** - funciona sem ele!

2. Se quiser usar:

**Windows:**
- Baixe: https://github.com/UB-Mannheim/tesseract/wiki
- Execute o instalador padrão
- Reinicie a aplicação

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

**Mac:**
```bash
brew install tesseract
```

---

### ❌ Problema: Pasta "dist" ou "build" criada e arquivos ficando grandes

**Causa:** Compilação anterior deixou arquivos temporários

**Solução:**

```bash
# Limpe arquivos temporários
rmdir /s build dist __pycache__  # Windows
rm -rf build dist __pycache__     # Linux/Mac

# Recrie o executável se necessário
```

---

### ❌ Problema: Gráfico não aparece / Branco em branco

**Causa:** Matplotlib não renderizou corretamente

**Solução:**

```bash
# Atualize matplotlib
pip install --upgrade matplotlib

# Reinicie a aplicação
```

---

### ❌ Problema: "Encoding errors" ao carregar arquivos

**Causa:** Arquivo em encoding diferente (ex: UTF-8 vs ANSI)

**Solução:**

```python
# No seu código, especifique encoding:
with open('arquivo.txt', encoding='utf-8') as f:
    dados = f.read()
```

---

### ❌ Problema: Janela congela ao gerar gráfico

**Causa:** Gráfico muito grande ou máquina lenta

**Solução:**

1. Dados menores (< 100 itens)
2. Aguarde alguns segundos
3. Se persistir, aumente RAM ou libere espaço

---

### ❌ Problema: "Port already in use" se tiver servidor

**Causa:** Porta já está em uso por outro processo

**Solução:**

Não aplicável a esta aplicação (GUI não usa portas)

---

### ❌ Problema: Arquivo requirements.txt não instala

**Causa:** Versão de Python muito antiga ou versões incompatíveis

**Solução:**

```bash
# Atualize pip primeiro
pip install --upgrade pip

# Instale dependências novamente
pip install -r requirements.txt

# Se ainda não funcionar, instale manualmente
pip install matplotlib numpy pandas reportlab openpyxl pillow pytesseract
```

---

## 📞 Se Nada Funcionar

1. **Reinstale Python 3.9+** (versão mais recente)
2. **Crie novo ambiente virtual:**
   ```bash
   rmdir /s .venv  # Remove antigo
   python -m venv .venv
   .venv\Scripts\activate
   ```
3. **Instale do zero:**
   ```bash
   pip install -r requirements.txt
   python main.py
   ```

---

## 🆘 Reportar um Bug

Se encontrou um erro:

1. Anote o mensagem de erro completa
2. Anote sua versão de Python: `python --version`
3. Anote seu sistema: Windows/Linux/Mac
4. Abra uma Issue no GitHub com:
   - Título descritivo
   - Passos para reproduzir
   - Mensagem de erro
   - Seu ambiente

---

## ✅ Dicas de Performance

### Para máquina lenta:
1. Feche outros programas
2. Use dados menores
3. Gere gráficos um por um (não dashboard)
4. Exporte em PNG (mais rápido que PDF)

### Para tela pequena:
1. Redimensione a janela
2. Ou edite `interface.py` linha 47 para `0.85`
3. Remova itens não essenciais

### Para usar menos memória:
1. Não mantenha muitos gráficos abertos
2. Feche a aplicação entre análises grandes
3. Use modo CLI: `python main.py -c`

---

**Última atualização:** Maio 2026
