# 📖 Guia de Importação Manual - Mente Lendária

Este guia explica como extrair manualmente as notas do site Mente Lendária quando o scraping automatizado não funciona devido a proteções contra bots.

## 🎯 Método 1: Usando MarkDownload (RECOMENDADO)

### Passo 1: Instalar a Extensão

**Chrome/Edge:**
1. Acesse: https://chrome.google.com/webstore
2. Busque por "MarkDownload"
3. Clique em "Adicionar ao Chrome/Edge"

**Firefox:**
1. Acesse: https://addons.mozilla.org/firefox/addon/markdownload/
2. Clique em "Adicionar ao Firefox"

### Passo 2: Configurar a Extensão

1. Clique no ícone da extensão (MarkDownload) na barra de ferramentas
2. Vá em configurações
3. Configure:
   - **Format**: Obsidian ou GitHub Flavored Markdown
   - **Include YAML frontmatter**: ✅ Habilitado
   - **Convert links**: ✅ Para formato [[WikiLinks]]
   - **Template**: Use o template abaixo

```yaml
---
title: {title}
source: {baseURI}
date_imported: {date:YYYY-MM-DD}
---

# {title}

{content}
```

### Passo 3: Extrair as Notas

1. Acesse https://mentelendaria.com
2. Faça login com a senha: `@88888888#`
3. Navegue até "Acessar o Segundo Cérebro do Alan"
4. Para cada nota:
   - Abra a nota
   - Clique no ícone do MarkDownload
   - Salve o arquivo `.md` na pasta `notas/`
5. Repita para todas as notas

### Passo 4: Organizar no Repositório

```bash
# Copiar arquivos para o repositório
cp /caminho/dos/downloads/*.md notas/

# Ou se estiver no Windows
# Arraste os arquivos para a pasta notas/
```

---

## 🎯 Método 2: Web Clipper do Obsidian

Se você já usa Obsidian:

### Passo 1: Instalar Web Clipper
1. Acesse: https://obsidian.md/clipper
2. Instale a extensão para seu navegador

### Passo 2: Configurar
1. Configure para salvar no seu vault
2. Use o template:

```markdown
---
title: {{title}}
url: {{url}}
date: {{date}}
---

# {{title}}

{{content}}

---
*Fonte: {{url}}*
```

### Passo 3: Clipar as Notas
1. Acesse cada nota no site
2. Clique no Web Clipper
3. Salve no seu vault
4. Depois copie para este repositório

---

## 🎯 Método 3: Copiar e Colar Manual

Se não quiser instalar extensões:

### Para cada nota:

1. **Abra a nota no site**
2. **Selecione todo o conteúdo** (Ctrl+A / Cmd+A)
3. **Copie** (Ctrl+C / Cmd+C)
4. **Crie um novo arquivo** `.md` na pasta `notas/`
5. **Cole o conteúdo**
6. **Adicione o frontmatter** no topo:

```markdown
---
title: Título da Nota
source: URL_da_nota
date_imported: 2025-11-06
---

[conteúdo copiado aqui]
```

---

## 🎯 Método 4: Screenshot e OCR (Backup)

Se nada mais funcionar:

1. Tire screenshots de cada nota
2. Use OCR para extrair texto:
   - Google Lens
   - Adobe Acrobat
   - Online OCR tools
3. Salve como `.md`

---

## 📝 Depois de Extrair

### Validar os Arquivos

```bash
# Contar quantas notas você extraiu
ls -1 notas/*.md | wc -l

# Ver lista de notas
ls notas/
```

### Criar Índice

Execute o script de índice:

```bash
python3 scripts/create_index.py
```

### Commit no Git

```bash
git add notas/
git commit -m "Add: Imported notes from Mente Lendária"
git push
```

---

## ⚠️ Dicas Importantes

1. **Nomes de Arquivo**: Use nomes descritivos sem caracteres especiais
2. **Encoding**: Salve sempre em UTF-8
3. **Links**: Tente manter links internos no formato `[[Nota]]`
4. **Imagens**: Se houver imagens, salve-as em `notas/assets/`

---

## 📊 Template de Nota Padrão

Use este template para cada nota:

```markdown
---
title: Título da Nota
source: https://mentelendaria.com/caminho
author: Alan
date_imported: 2025-11-06
tags: [tag1, tag2, tag3]
---

# Título da Nota

## Seção 1

Conteúdo aqui...

## Seção 2

Mais conteúdo...

---

**Fonte**: [Mente Lendária](https://mentelendaria.com)
```

---

## 🆘 Precisa de Ajuda?

Se encontrar problemas:
1. Verifique se está logado no site
2. Tente outro navegador
3. Limpe o cache
4. Use modo anônimo + faça login novamente

---

**Boa sorte na extração! 🚀**
