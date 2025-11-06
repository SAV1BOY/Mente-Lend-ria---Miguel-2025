# 📖 Instruções para Extração das Notas

## 🚨 Situação Atual

O site **mentelendaria.com** possui proteção contra scraping automatizado (erro 403 Forbidden), o que impede a extração automática das notas via scripts rodando em servidor.

## ✅ Soluções Disponíveis

### 🎯 Opção 1: Rodar Script Localmente (RECOMENDADO)

O script com Selenium roda no seu computador e usa um navegador real para acessar o site.

#### Passo a Passo:

1. **Instalar Python** (se não tiver):
   - Windows: https://www.python.org/downloads/
   - Mac: `brew install python3`
   - Linux: Já vem instalado

2. **Instalar dependências**:
```bash
pip install selenium webdriver-manager
```

3. **Executar o script**:
```bash
cd scripts
python3 local_scraper_selenium.py
```

4. **O navegador abrirá automaticamente** e fará:
   - Login no site
   - Mapeamento de todas as páginas
   - Download de cada nota
   - Salvamento na pasta `notas/`

5. **Criar índice**:
```bash
python3 create_index.py
```

---

### 🎯 Opção 2: MarkDownload (Manual mas Simples)

Se preferir método manual sem programar:

1. **Instale MarkDownload**:
   - [Chrome/Edge](https://chrome.google.com/webstore) - busque "MarkDownload"
   - [Firefox](https://addons.mozilla.org/firefox/addon/markdownload/)

2. **Configure** (veja detalhes em `scripts/manual_import_guide.md`)

3. **Para cada nota**:
   - Abra no navegador
   - Clique na extensão MarkDownload
   - Salve o arquivo .md na pasta `notas/`

4. **Depois organize**:
```bash
python3 scripts/create_index.py
```

---

### 🎯 Opção 3: Exportação Direta do Obsidian

Se você é o administrador do site:

1. Acesse o painel do Obsidian Publish
2. Procure opção "Export" ou "Download Vault"
3. Baixe o vault completo
4. Extraia na pasta `notas/`

---

## 📁 Estrutura do Repositório

```
Mente-Lendária---Miguel-2025/
├── notas/                          # Todas as notas em Markdown
│   ├── EXEMPLO_NOTA.md            # Template de formato
│   ├── _INDEX.md                  # Índice alfabético
│   └── _INDEX.json                # Índice em JSON
├── scripts/                        # Scripts de automação
│   ├── simple_scraper.py          # Scraper básico (requests)
│   ├── obsidian_scraper.py        # Scraper Playwright
│   ├── local_scraper_selenium.py  # 🌟 Script para rodar localmente
│   ├── create_index.py            # Cria índice das notas
│   └── manual_import_guide.md     # Guia detalhado
├── README.md                       # Documentação principal
├── INSTRUCOES.md                   # Este arquivo
└── .gitignore                      # Arquivos ignorados pelo Git

```

---

## 🔧 Próximos Passos

### Se escolheu Opção 1 (Selenium Local):

```bash
# 1. Instalar dependências
pip install selenium webdriver-manager

# 2. Executar scraper
python3 scripts/local_scraper_selenium.py

# 3. Criar índice
python3 scripts/create_index.py

# 4. Commit no Git
git add notas/
git commit -m "Add: Imported all notes from Mente Lendária"
git push
```

### Se escolheu Opção 2 (Manual):

1. Leia o guia completo: `scripts/manual_import_guide.md`
2. Instale MarkDownload
3. Extraia cada nota
4. Execute `python3 scripts/create_index.py`
5. Commit e push

### Se escolheu Opção 3 (Export):

```bash
# 1. Extrair vault baixado para pasta notas/
unzip vault.zip -d notas/

# 2. Criar índice
python3 scripts/create_index.py

# 3. Commit
git add notas/
git commit -m "Add: Imported notes from Obsidian export"
git push
```

---

## 📊 Verificação

Após importar as notas, verifique:

```bash
# Contar notas
ls -1 notas/*.md | wc -l

# Ver lista
ls notas/

# Verificar índice
cat notas/_INDEX.md
```

---

## 🆘 Problemas Comuns

### "ModuleNotFoundError: No module named 'selenium'"
**Solução**: `pip install selenium webdriver-manager`

### "403 Forbidden" ao rodar scripts
**Solução**: Use a Opção 1 (Selenium Local) ou Opção 2 (Manual)

### "No such file or directory: 'notas/'"
**Solução**: `mkdir notas`

### Navegador não abre no Selenium
**Solução**: Certifique-se que tem Chrome instalado

---

## 📞 Suporte

- Leia: `scripts/manual_import_guide.md` para guia detalhado
- Scripts inclusos têm comentários explicativos
- Exemplo de nota: `notas/EXEMPLO_NOTA.md`

---

## ⚠️ Importante

- **Backup**: Sempre faça backup antes de modificar
- **Encoding**: Use UTF-8 para todos os arquivos
- **Links**: Mantenha formato `[[Nome da Nota]]` para links internos
- **Commits**: Commit e push regularmente

---

**Boa sorte! 🚀**

Se precisar de ajuda, abra uma issue no GitHub.
