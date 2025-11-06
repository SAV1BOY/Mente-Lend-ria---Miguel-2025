# 🧠 Mente Lendária - Miguel 2025

Repositório contendo todas as notas e anotações do **Segundo Cérebro do Alan** extraídas de [mentelendaria.com](https://mentelendaria.com/).

## 📚 Sobre

Este repositório foi criado para preservar e organizar o conteúdo educacional do site Mente Lendária, facilitando o acesso offline e a pesquisa de informações.

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

### `simple_scraper.py`
Script Python para extração automatizada de notas (quando possível).

```bash
python3 simple_scraper.py
```

### `obsidian_scraper.py`
Script mais robusto usando Playwright para sites com JavaScript.

```bash
python3 obsidian_scraper.py
```

## 📊 Estatísticas

- **Total de Notas**: Em atualização
- **Data da Extração**: 2025-11-06
- **Última Atualização**: 2025-11-06

---

**⚠️ Nota**: Este repositório foi criado para fins educacionais e de backup pessoal. Todo o conteúdo pertence aos seus autores originais.
