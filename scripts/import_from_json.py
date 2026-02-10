#!/usr/bin/env python3
"""
Import from JSON - Mente Lendaria
==================================
Converte o arquivo JSON exportado pelo browser_console_extractor.js
em arquivos Markdown organizados na estrutura de pastas do Obsidian.

USO:
    python3 import_from_json.py mente-lendaria-vault-2026-02-10.json

O script vai:
1. Ler o JSON exportado pelo extrator do console
2. Criar a estrutura de pastas
3. Salvar cada nota como .md com frontmatter
4. Criar um indice geral (_INDEX.md)
"""

import json
import os
import sys
import time
import re
from pathlib import Path


def sanitize_path(path):
    """Limpa o caminho do arquivo."""
    # Remover .md duplicado
    while path.endswith('.md.md'):
        path = path[:-3]

    # Garantir extensao .md
    if not path.endswith('.md'):
        path = path + '.md'

    # Limpar caracteres problematicos
    path = path.replace(':', ' -')
    path = path.replace('|', '-')
    path = path.replace('<', '')
    path = path.replace('>', '')
    path = path.replace('"', '')
    path = path.replace('\\', '/')
    path = path.replace('*', '')
    path = path.replace('?', '')

    return path


def extract_title(content, file_path):
    """Extrai titulo do conteudo Markdown."""
    # Do frontmatter
    if content.startswith('---'):
        end = content.find('---', 3)
        if end > 0:
            for line in content[3:end].split('\n'):
                if line.strip().lower().startswith('title:'):
                    title = line.split(':', 1)[1].strip()
                    return title.strip('"').strip("'")

    # Do primeiro heading
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('# '):
            return line[2:].strip()

    # Do nome do arquivo
    name = os.path.basename(file_path)
    if name.endswith('.md'):
        name = name[:-3]
    return name


def create_frontmatter(title, source_path, tags=None):
    """Cria frontmatter YAML."""
    fm = '---\n'
    fm += f'title: "{title}"\n'
    fm += f'source_path: "{source_path}"\n'
    fm += f'date_imported: "{time.strftime("%Y-%m-%d %H:%M:%S")}"\n'
    fm += 'vault: "Mente Lendaria - Segundo Cerebro do Alan"\n'
    if tags:
        fm += f'tags: {json.dumps(tags, ensure_ascii=False)}\n'
    fm += '---\n\n'
    return fm


def import_vault(json_file, output_dir):
    """Importa notas do JSON para arquivos Markdown."""
    print(f'Lendo: {json_file}')

    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Extrair metadados
    metadata = data.get('metadata', {})
    notes = data.get('notes', {})

    print(f'Vault: {metadata.get("vault_name", "Mente Lendaria")}')
    print(f'Data de exportacao: {metadata.get("export_date", "N/A")}')
    print(f'Total de notas: {len(notes)}')
    print()

    if not notes:
        print('[ERRO] Nenhuma nota encontrada no JSON.')
        sys.exit(1)

    # Criar diretorio de saida
    os.makedirs(output_dir, exist_ok=True)

    imported = 0
    skipped = 0

    for file_path, content in notes.items():
        if not content or not content.strip():
            skipped += 1
            continue

        # Limpar caminho
        clean_path = sanitize_path(file_path)
        local_path = os.path.join(output_dir, clean_path)

        # Extrair titulo e tags
        title = extract_title(content, file_path)
        path_parts = file_path.split('/')
        tags = [p for p in path_parts[:-1] if p] if len(path_parts) > 1 else []

        # Preparar conteudo final
        if content.strip().startswith('---'):
            # Ja tem frontmatter, manter original
            final_content = content
        else:
            # Adicionar frontmatter
            frontmatter = create_frontmatter(title, file_path, tags)
            final_content = frontmatter + content

        # Criar diretorios necessarios
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        # Salvar arquivo
        with open(local_path, 'w', encoding='utf-8') as f:
            f.write(final_content)

        imported += 1
        print(f'  [{imported}] {clean_path}')

    # Criar indice
    create_index(output_dir)

    print()
    print('================================================================')
    print(f'  Importacao completa!')
    print(f'  Notas importadas: {imported}')
    print(f'  Notas vazias (puladas): {skipped}')
    print(f'  Pasta de saida: {output_dir}')
    print()
    print('  Proximos passos:')
    print('    1. Abra a pasta no Obsidian como vault')
    print('    2. git add notas/')
    print('    3. git commit -m "Add: notas do Mente Lendaria"')
    print('    4. git push')
    print('================================================================')


def create_index(output_dir):
    """Cria indice do vault."""
    entries = []

    for root, dirs, files in os.walk(output_dir):
        for file in sorted(files):
            if file.endswith('.md') and not file.startswith('_'):
                rel_path = os.path.relpath(os.path.join(root, file), output_dir)
                link = rel_path.replace('.md', '').replace('\\', '/')
                entries.append(f'- [[{link}]]')

    index = f"""---
title: "Indice do Vault - Mente Lendaria"
date: "{time.strftime('%Y-%m-%d')}"
---

# Mente Lendaria - Segundo Cerebro do Alan

## Indice de Notas

{chr(10).join(entries)}

---
Total: {len(entries)} notas
"""

    with open(os.path.join(output_dir, '_INDEX.md'), 'w', encoding='utf-8') as f:
        f.write(index)

    # Tambem criar JSON index
    json_index = {}
    for root, dirs, files in os.walk(output_dir):
        for file in sorted(files):
            if file.endswith('.md'):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, output_dir)
                json_index[rel_path] = {
                    'title': file[:-3],
                    'size': os.path.getsize(full_path),
                    'has_content': os.path.getsize(full_path) > 100,
                }

    with open(os.path.join(output_dir, '_INDEX.json'), 'w', encoding='utf-8') as f:
        json.dump(json_index, f, indent=2, ensure_ascii=False)

    print(f'  [INDEX] {len(entries)} notas indexadas')


def main():
    if len(sys.argv) < 2:
        print('Uso: python3 import_from_json.py <arquivo.json>')
        print()
        print('Primeiro, exporte as notas usando o script browser_console_extractor.js')
        print('no console do navegador (F12) enquanto estiver logado no site.')
        sys.exit(1)

    json_file = sys.argv[1]

    if not os.path.exists(json_file):
        print(f'[ERRO] Arquivo nao encontrado: {json_file}')
        sys.exit(1)

    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'notas')

    # Permitir especificar diretorio de saida
    if len(sys.argv) >= 3:
        output_dir = sys.argv[2]

    import_vault(json_file, output_dir)


if __name__ == '__main__':
    main()
