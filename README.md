# Mente Lendaria - Segundo Cerebro do Alan | Obsidian Vault

Repositorio para backup e organizacao de todas as notas do **Segundo Cerebro do Alan** do site [mentelendaria.com](https://mentelendaria.com/).

## Sobre

Este repositorio preserva o conteudo educacional do Mente Lendaria (Obsidian Publish) para acesso offline no **Obsidian**. O vault contem notas sobre IA, empreendedorismo, desenvolvimento pessoal, filosofia, saude, neurociencia e mais.

## Status

**Estrutura criada - Notas aguardando extracao**

O site usa Obsidian Publish com protecao anti-bot. A extracao deve ser feita localmente no seu computador.

## Como Extrair as Notas (3 Metodos)

### Metodo 1: Console do Navegador (MAIS FACIL)

1. Abra https://mentelendaria.com no navegador
2. Faca login com a senha: `@88888888#`
3. Pressione **F12** > aba **Console**
4. Cole o conteudo de `scripts/browser_console_extractor.js` e pressione Enter
5. Um arquivo JSON sera baixado automaticamente
6. Execute para converter em Markdown:

```bash
python3 scripts/import_from_json.py <arquivo-baixado>.json
```

### Metodo 2: Playwright (AUTOMATICO)

```bash
pip install playwright
playwright install chromium
python3 scripts/obsidian_scraper.py --headed
```

O script vai:
- Abrir o navegador automaticamente
- Fazer login no site
- Usar a API POST do Obsidian Publish para obter TODAS as notas
- Salvar tudo na pasta `notas/`

### Metodo 3: API Direta (Python puro)

```bash
pip install requests
python3 scripts/obsidian_publish_extractor.py
```

Usa a API do Obsidian Publish diretamente via POST requests. Funciona sem navegador, mas pode ser bloqueado dependendo da rede.

### Metodo 4: MarkDownload (Manual)

Veja `COMO_EXTRAIR.md` para instrucoes detalhadas usando a extensao MarkDownload no navegador.

## Apos Extrair

```bash
# Verificar as notas
ls -R notas/

# Commit
git add notas/
git commit -m "Add: notas do Mente Lendaria"
git push
```

Para usar no Obsidian: abra a pasta `notas/` como vault no Obsidian.

## Estrutura

```
notas/                  # Vault do Obsidian com todas as notas
  Sobre Mim/            # Notas pessoais do Alan
  Conhecimento/         # Base de conhecimento
    YouTube/            # Notas sobre YouTube
    Desenvolvimento Pessoal/
    Empreendedorismo/
    Filosofia/
    IA e Tecnologia/
    Saude e Neurociencia/
  IA/                   # Inteligencia Artificial
  MOCs/                 # Maps of Content
  Cursos/               # Notas de cursos
  Vida Lendaria/        # Programa Vida Lendaria
  Recursos/             # Ferramentas e recursos

scripts/                # Scripts de extracao
  browser_console_extractor.js  # Metodo 1: Console do navegador
  import_from_json.py           # Importa JSON do console extractor
  obsidian_scraper.py           # Metodo 2: Playwright automatico
  obsidian_publish_extractor.py # Metodo 3: API direta
  create_index.py               # Gera indice das notas
```

## Scripts

| Script | Metodo | Requisitos | Dificuldade |
|--------|--------|------------|-------------|
| `browser_console_extractor.js` | Console F12 | Navegador | Facil |
| `import_from_json.py` | Pos-extracao | Python 3 | Facil |
| `obsidian_scraper.py` | Playwright | Python + Playwright | Medio |
| `obsidian_publish_extractor.py` | API POST | Python + requests | Medio |
| `create_index.py` | Utilitario | Python 3 | Facil |

## Informacoes Tecnicas

- **Site ID (Obsidian Publish)**: `f431548d64f3cdad0278eb0b35aa11fe`
- **API**: `https://publish-01.obsidian.md`
- **Autenticacao**: Password `@88888888#` (SHA256 hash para API)
- **Total estimado**: 100-200+ notas (22 confirmadas visiveis)

## Creditos

- **Conteudo original**: Alan Nicolas - [Mente Lendaria](https://mentelendaria.com/)
- **Repositorio**: Miguel (2025)
- Repositorio criado para fins educacionais e backup pessoal.
