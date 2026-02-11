# Prompt Completo para Claude Code
## Metodologias: HRM + CoT + ToT + Taxonomia de Bloom

---

## COMO USAR

Copie o prompt da secao "PROMPT" abaixo e cole no Claude Code (terminal).
Substitua `<CAMINHO_DO_JSON>` pelo caminho real do arquivo JSON baixado.

---

## PROMPT

```
Voce e um engenheiro de software especializado em automacao, gestao de conhecimento e Obsidian.
Preciso que execute uma tarefa complexa com precisao cirurgica seguindo um raciocinio estruturado.

═══════════════════════════════════════════════════════════════
CONTEXTO (HRM - Hierarchical Role Method)
═══════════════════════════════════════════════════════════════

PAPEL PRIMARIO: Engenheiro de Automacao de Vaults Obsidian
PAPEL SECUNDARIO: Especialista em ETL (Extract-Transform-Load) de dados educacionais
PAPEL TERCIARIO: Consultor de organizacao de conhecimento pessoal (PKM)

SITUACAO:
- Tenho um repositorio Git em: /caminho/para/Mente-Lend-ria---Miguel-2025
- Extraí 1584 notas do site mentelendaria.com (Obsidian Publish do Alan Nicolas)
- As notas foram salvas em um arquivo JSON: <CAMINHO_DO_JSON>
- O JSON contem a estrutura: {"metadata": {...}, "notes": {"path/arquivo.md": "conteudo markdown", ...}}
- Preciso converter esse JSON em um vault Obsidian completo e organizado

RESTRICOES:
- Nao alterar o conteudo original das notas
- Preservar a estrutura de pastas do vault original
- Manter links internos no formato [[wikilink]]
- Gerar frontmatter YAML para notas que nao tem
- Nao sobrescrever arquivos que ja tenham conteudo

═══════════════════════════════════════════════════════════════
CADEIA DE PENSAMENTO (CoT - Chain of Thought)
═══════════════════════════════════════════════════════════════

Raciocine passo a passo antes de executar:

PASSO 1 - ANALISAR: Leia o arquivo JSON e entenda a estrutura
  → Quantas notas existem?
  → Quais sao as pastas principais?
  → O conteudo ja tem frontmatter ou e markdown puro?

PASSO 2 - PREPARAR: Limpar o estado atual
  → Remover arquivos placeholder vazios (_EXPLORAR_ESTA_SECAO.md)
  → Preservar notas que ja tem conteudo real
  → Criar estrutura de pastas necessaria

PASSO 3 - TRANSFORMAR: Converter cada nota
  → Para cada nota no JSON:
    - Sanitizar o caminho do arquivo (caracteres especiais, emojis)
    - Extrair titulo do conteudo ou do path
    - Adicionar frontmatter YAML se nao existir
    - Gerar tags baseadas na hierarquia de pastas
    - Salvar como arquivo .md na pasta correta

PASSO 4 - INDEXAR: Criar navegacao
  → _INDEX.md com wikilinks agrupados por secao
  → _INDEX.json para buscas programaticas
  → _MOC.md em cada pasta (Map of Content)

PASSO 5 - VERIFICAR: Validar resultado
  → Contar arquivos criados
  → Verificar que o vault abre no Obsidian
  → Mostrar estatisticas por secao

═══════════════════════════════════════════════════════════════
ARVORE DE DECISAO (ToT - Tree of Thought)
═══════════════════════════════════════════════════════════════

DECISAO 1: Como executar?
  ├─ Opcao A: Rodar o script existente → python3 scripts/import_vault_complete.py <JSON>
  ├─ Opcao B: Implementar inline se o script nao existir
  └─ ESCOLHA: Opcao A (script ja existe e esta testado)

DECISAO 2: Onde salvar?
  ├─ Opcao A: Na pasta notas/ do repositorio (padrao)
  ├─ Opcao B: Em pasta customizada do Obsidian do usuario
  └─ ESCOLHA: Opcao A primeiro, depois copiar se necessario

DECISAO 3: O que fazer com arquivos existentes?
  ├─ Opcao A: Sobrescrever tudo
  ├─ Opcao B: Preservar existentes com conteudo
  └─ ESCOLHA: Opcao B (nao perder trabalho anterior)

DECISAO 4: Apos importar?
  ├─ Opcao A: Commit e push automatico
  ├─ Opcao B: Apenas mostrar instrucoes
  └─ ESCOLHA: Perguntar ao usuario

═══════════════════════════════════════════════════════════════
NIVEIS DE BLOOM (Taxonomia Cognitiva)
═══════════════════════════════════════════════════════════════

NIVEL 1 - LEMBRAR: Identifique o arquivo JSON e o diretorio de destino
NIVEL 2 - COMPREENDER: Entenda a estrutura do JSON (metadata + notes)
NIVEL 3 - APLICAR: Execute o script de importacao com os parametros corretos
NIVEL 4 - ANALISAR: Verifique o resultado - quantas notas, estrutura de pastas, erros
NIVEL 5 - AVALIAR: Compare com o esperado (1584 notas, ~13.94 MB de conteudo)
NIVEL 6 - CRIAR: Gere os indices, MOCs e commit final

═══════════════════════════════════════════════════════════════
COMANDOS PARA EXECUTAR
═══════════════════════════════════════════════════════════════

Execute EXATAMENTE nesta ordem:

1. Navegue ate o repositorio:
   cd /caminho/para/Mente-Lend-ria---Miguel-2025

2. Execute o script de importacao:
   python3 scripts/import_vault_complete.py "<CAMINHO_DO_JSON>"

3. Verifique o resultado:
   find notas/ -name "*.md" | wc -l

4. Se tudo estiver correto, faca o commit:
   git add notas/
   git commit -m "Add: 1584 notas completas do Segundo Cerebro do Alan - Mente Lendaria"
   git push

5. Mostre o resumo final com:
   - Total de notas importadas
   - Distribuicao por pasta/secao
   - Tamanho total do vault
   - Instrucoes para abrir no Obsidian

═══════════════════════════════════════════════════════════════
FORMATO DE SAIDA ESPERADO
═══════════════════════════════════════════════════════════════

Ao final, me mostre:
1. Quantas notas foram importadas com sucesso
2. Quantas falharam ou foram puladas e por que
3. Lista das secoes/pastas com contagem de notas
4. Tamanho total do vault em MB
5. Comando git para commit
6. Como abrir no Obsidian
```

---

## VERSAO SIMPLIFICADA (so o comando)

Se voce so quer executar rapidamente sem o prompt completo:

```bash
cd /caminho/para/Mente-Lend-ria---Miguel-2025
python3 scripts/import_vault_complete.py ~/Downloads/"mente-lendaria-vault- Completo (8 falhas).json"
git add notas/
git commit -m "Add: notas completas do Segundo Cerebro - Mente Lendaria"
git push
```

---

## NOTAS SOBRE AS METODOLOGIAS

### HRM (Hierarchical Role Method)
Define papeis hierarquicos para o agente, estabelecendo contexto, expertise e restricoes claras.

### CoT (Chain of Thought)
Forca raciocinio sequencial explicito, evitando saltos logicos e garantindo que cada passo depende do anterior.

### ToT (Tree of Thought)
Apresenta decisoes como arvore de opcoes com justificativas, permitindo que o agente escolha o melhor caminho.

### Taxonomia de Bloom
Estrutura a tarefa em 6 niveis cognitivos crescentes: Lembrar → Compreender → Aplicar → Analisar → Avaliar → Criar.
