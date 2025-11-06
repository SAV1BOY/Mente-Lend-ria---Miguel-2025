# 🧠 Mente Lendária - Miguel 2025

Repositório para backup e organização de todas as notas e anotações do **Segundo Cérebro do Alan** do site [mentelendaria.com](https://mentelendaria.com/).

## 📚 Sobre

Este repositório foi criado para preservar e organizar o conteúdo educacional do site Mente Lendária (Obsidian Publish), facilitando o acesso offline e a pesquisa de informações.

## ⚠️ Status Atual

**🚧 Estrutura criada - Aguardando extração de notas**

O site usa Obsidian Publish com proteção anti-bot, impedindo extração automatizada via servidor. As notas precisam ser extraídas manualmente ou via script local. Veja `COMO_EXTRAIR.md` para instruções completas.

## 📁 Estrutura

```
Mente-Lendária---Miguel-2025/
├── notas/              # Todas as notas extraídas em formato Markdown
├── scripts/            # Scripts de extração e organização
├── README.md           # Este arquivo
└── _INDEX.json         # Índice de todas as notas
```

## 🔧 Como usar

As notas estão em formato Markdown (`.md`) e podem ser:
- Lidas diretamente no GitHub
- Abertas em qualquer editor de texto
- Importadas para o Obsidian ou outros apps de notas
- Buscadas usando a função de pesquisa do GitHub

## 📝 Formato das Notas

Cada nota contém:
- **Frontmatter YAML** com metadados (título, fonte, data de importação)
- **Título principal**
- **Conteúdo** formatado em Markdown
- **Link da fonte original**

Exemplo:
```markdown
---
title: Título da Nota
source: https://mentelendaria.com/nota
date_imported: 2025-11-06
---

# Título da Nota

Conteúdo da nota aqui...
```

## 🔍 Pesquisar Notas

Use a busca do GitHub (`Ctrl/Cmd + K`) ou procure manualmente na pasta `notas/`.

## 📜 Licença e Créditos

- **Fonte Original**: [Mente Lendária](https://mentelendaria.com/)
- **Autor Original**: Alan (Segundo Cérebro do Alan)
- **Este Repositório**: Organizado por Miguel (2025)

---

## 🛠️ Scripts Disponíveis

### `scripts/local_scraper_selenium.py` ⭐ RECOMENDADO
Script para rodar **no seu computador local** (com interface gráfica):
```bash
pip install selenium webdriver-manager
python3 scripts/local_scraper_selenium.py
```

### `scripts/obsidian_api_scraper.py`
Tenta usar a API do Obsidian Publish (atualmente bloqueada):
```bash
python3 scripts/obsidian_api_scraper.py
```

### `scripts/create_index.py`
Cria índice de todas as notas importadas:
```bash
python3 scripts/create_index.py
```

## 📊 Estatísticas

- **Total de Notas Confirmadas**: ~22 (visíveis na navegação)
- **Total Estimado**: 100-200+ notas
- **Data de Setup**: 2025-11-06
- **Status**: Aguardando extração manual/local

## 🚀 Como Extrair as Notas

**Leia os guias completos:**
1. **`COMO_EXTRAIR.md`** - Guia passo a passo detalhado
2. **`LISTA_COMPLETA_NOTAS.md`** - Lista de todas as páginas conhecidas
3. **`scripts/manual_import_guide.md`** - Guia de importação manual

**Método mais rápido:**
- Use a extensão **MarkDownload** (veja `COMO_EXTRAIR.md`)
- OU rode `local_scraper_selenium.py` no seu computador

---

**⚠️ Nota**: Este repositório foi criado para fins educacionais e de backup pessoal. Todo o conteúdo pertence aos seus autores originais.
