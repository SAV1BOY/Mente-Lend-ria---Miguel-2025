#!/usr/bin/env python3
"""
Import Vault Complete - Mente Lendaria
=======================================
Converte o JSON exportado pelo browser_console_extractor em um
vault Obsidian completo e organizado.

USO:
    python3 import_vault_complete.py <arquivo.json>
    python3 import_vault_complete.py <arquivo.json> <pasta_destino>

EXEMPLO:
    python3 scripts/import_vault_complete.py ~/Downloads/mente-lendaria-vault-2026-02-11.json
    python3 scripts/import_vault_complete.py ~/Downloads/mente-lendaria-vault-2026-02-11.json ~/MeuObsidian/MenteLendaria
"""

import json
import os
import sys
import time
import re
import shutil
from pathlib import Path
from collections import defaultdict


# ============================================================
# CONFIGURACAO
# ============================================================
VAULT_NAME = "Mente Lendaria - Segundo Cerebro do Alan"
EMPTY_THRESHOLD = 150  # bytes - arquivos menores sao considerados vazios
PLACEHOLDER_FILES = [
    '_EXPLORAR_ESTA_SEÇÃO.md',
    '_EXPLORAR_ESTA_SECAO.md',
    'EXEMPLO_NOTA.md',
]
# ============================================================


def sanitize_path(path):
    """Limpa caminho de arquivo preservando estrutura e caracteres PT-BR."""
    # Remover .md duplicado
    while path.endswith('.md.md'):
        path = path[:-3]

    # Garantir extensao .md
    if not path.endswith('.md'):
        path += '.md'

    # Substituir caracteres invalidos para filesystem
    replacements = {
        ':': ' -',
        '|': '-',
        '<': '',
        '>': '',
        '"': '',
        '\\': '/',
        '*': '',
        '\t': ' ',
        '\n': ' ',
        '\r': '',
    }
    for old, new in replacements.items():
        path = path.replace(old, new)

    # Remover ? mas preservar outros caracteres (emojis, acentos)
    path = path.replace('?', '')

    # Limpar espacos duplos
    while '  ' in path:
        path = path.replace('  ', ' ')

    # Limpar / duplas
    while '//' in path:
        path = path.replace('//', '/')

    # Remover espacos no inicio/fim de cada segmento
    parts = path.split('/')
    parts = [p.strip() for p in parts if p.strip()]
    path = '/'.join(parts)

    return path


def extract_title(content, file_path):
    """Extrai titulo do conteudo ou path."""
    if not content:
        return path_to_title(file_path)

    # Do frontmatter existente
    if content.strip().startswith('---'):
        end = content.find('---', 3)
        if end > 0:
            for line in content[3:end].split('\n'):
                stripped = line.strip()
                if stripped.lower().startswith('title:'):
                    title = stripped.split(':', 1)[1].strip()
                    return title.strip('"').strip("'")

    # Do primeiro heading H1
    for line in content.split('\n')[:20]:
        line = line.strip()
        if line.startswith('# ') and not line.startswith('## '):
            return line[2:].strip()

    return path_to_title(file_path)


def path_to_title(file_path):
    """Converte path de arquivo em titulo legivel."""
    name = os.path.basename(file_path)
    if name.endswith('.md'):
        name = name[:-3]
    return name


def create_frontmatter(title, source_path, tags=None):
    """Cria frontmatter YAML padrao."""
    # Escapar aspas no titulo
    safe_title = title.replace('"', '\\"')

    fm = '---\n'
    fm += f'title: "{safe_title}"\n'
    fm += f'source_path: "{source_path}"\n'
    fm += f'date_imported: "{time.strftime("%Y-%m-%d %H:%M:%S")}"\n'
    fm += f'vault: "{VAULT_NAME}"\n'
    if tags:
        fm += f'tags: {json.dumps(tags, ensure_ascii=False)}\n'
    fm += '---\n\n'
    return fm


def clean_old_files(output_dir):
    """Remove arquivos placeholder e shells vazios."""
    removed = 0

    if not os.path.exists(output_dir):
        return removed

    for root, dirs, files in os.walk(output_dir):
        for file in files:
            filepath = os.path.join(root, file)

            # Remover placeholders conhecidos
            if file in PLACEHOLDER_FILES:
                os.remove(filepath)
                removed += 1
                continue

            # Remover arquivos .md vazios ou quase vazios
            if file.endswith('.md') and not file.startswith('_'):
                try:
                    size = os.path.getsize(filepath)
                    if size < EMPTY_THRESHOLD:
                        os.remove(filepath)
                        removed += 1
                except OSError:
                    pass

    # Remover pastas vazias
    for root, dirs, files in os.walk(output_dir, topdown=False):
        for d in dirs:
            dirpath = os.path.join(root, d)
            try:
                if not os.listdir(dirpath):
                    os.rmdir(dirpath)
            except OSError:
                pass

    return removed


def import_notes(data, output_dir):
    """Importa todas as notas do JSON para arquivos Markdown."""
    notes = data.get('notes', {})
    metadata = data.get('metadata', {})

    if not notes:
        print('[ERRO] Nenhuma nota encontrada no JSON.')
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    imported = 0
    skipped_empty = 0
    skipped_existing = 0
    stats_by_folder = defaultdict(int)

    total = len(notes)

    for file_path, content in notes.items():
        # Pular notas vazias
        if not content or not content.strip() or len(content.strip()) < 10:
            skipped_empty += 1
            continue

        # Limpar caminho
        clean_path = sanitize_path(file_path)
        local_path = os.path.join(output_dir, clean_path)

        # Proteger notas existentes com conteudo
        if os.path.exists(local_path):
            existing_size = os.path.getsize(local_path)
            if existing_size > EMPTY_THRESHOLD:
                skipped_existing += 1
                continue

        # Extrair titulo
        title = extract_title(content, file_path)

        # Tags baseadas no path
        path_parts = file_path.split('/')
        tags = [p.strip() for p in path_parts[:-1] if p.strip()]

        # Preparar conteudo final
        if content.strip().startswith('---'):
            final_content = content
        else:
            frontmatter = create_frontmatter(title, file_path, tags if tags else None)
            final_content = frontmatter + content

        # Criar diretorios
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        # Salvar
        with open(local_path, 'w', encoding='utf-8') as f:
            f.write(final_content)

        imported += 1

        # Estatisticas por pasta
        folder = path_parts[0] if len(path_parts) > 1 else '(raiz)'
        stats_by_folder[folder] += 1

        # Progresso
        if imported % 100 == 0 or imported == 1:
            print(f'  [{imported}] {clean_path}')

    return imported, skipped_empty, skipped_existing, stats_by_folder


def create_vault_index(output_dir):
    """Cria indice geral do vault com wikilinks."""
    sections = defaultdict(list)

    for root, dirs, files in os.walk(output_dir):
        for file in sorted(files):
            if file.endswith('.md') and not file.startswith('_'):
                rel_path = os.path.relpath(os.path.join(root, file), output_dir)
                link = rel_path.replace('.md', '').replace('\\', '/')

                # Agrupar por pasta de primeiro nivel
                parts = link.split('/')
                section = parts[0] if len(parts) > 1 else 'Raiz'
                sections[section].append(link)

    # Gerar conteudo do indice
    lines = [
        '---',
        f'title: "Indice Completo - {VAULT_NAME}"',
        f'date: "{time.strftime("%Y-%m-%d")}"',
        'type: index',
        '---',
        '',
        f'# {VAULT_NAME}',
        '',
        f'**Total: {sum(len(v) for v in sections.values())} notas**',
        '',
        '---',
        '',
    ]

    for section in sorted(sections.keys()):
        notes_list = sections[section]
        lines.append(f'## {section} ({len(notes_list)} notas)')
        lines.append('')
        for link in sorted(notes_list):
            display = link.split('/')[-1]
            lines.append(f'- [[{link}|{display}]]')
        lines.append('')

    index_content = '\n'.join(lines)

    with open(os.path.join(output_dir, '_INDEX.md'), 'w', encoding='utf-8') as f:
        f.write(index_content)

    return sum(len(v) for v in sections.values())


def create_folder_mocs(output_dir):
    """Cria Map of Content (MOC) para cada pasta."""
    mocs_created = 0

    for root, dirs, files in os.walk(output_dir):
        md_files = [f for f in files if f.endswith('.md') and not f.startswith('_')]

        if not md_files or root == output_dir:
            continue

        folder_name = os.path.basename(root)
        rel_root = os.path.relpath(root, output_dir)

        lines = [
            '---',
            f'title: "MOC - {folder_name}"',
            f'date: "{time.strftime("%Y-%m-%d")}"',
            'type: moc',
            f'tags: ["moc", "{folder_name.lower()}"]',
            '---',
            '',
            f'# {folder_name}',
            '',
            f'> Map of Content - {len(md_files)} notas nesta secao',
            '',
            '---',
            '',
        ]

        # Subpastas
        if dirs:
            lines.append('## Subpastas')
            lines.append('')
            for d in sorted(dirs):
                sub_rel = os.path.relpath(os.path.join(root, d), output_dir)
                moc_path = f'{sub_rel}/_MOC'
                lines.append(f'- [[{moc_path.replace(chr(92), "/")}|{d}]]')
            lines.append('')

        # Notas
        lines.append('## Notas')
        lines.append('')
        for f in sorted(md_files):
            link = os.path.relpath(os.path.join(root, f), output_dir)
            link = link.replace('.md', '').replace('\\', '/')
            display = f.replace('.md', '')
            lines.append(f'- [[{link}|{display}]]')

        lines.append('')

        moc_path = os.path.join(root, '_MOC.md')
        with open(moc_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        mocs_created += 1

    return mocs_created


def create_json_index(output_dir):
    """Cria indice JSON para buscas programaticas."""
    index = {}

    for root, dirs, files in os.walk(output_dir):
        for file in sorted(files):
            if file.endswith('.md'):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, output_dir).replace('\\', '/')

                size = os.path.getsize(full_path)
                title = file[:-3]

                # Tentar extrair titulo do frontmatter
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        head = f.read(500)
                    if head.startswith('---'):
                        end = head.find('---', 3)
                        if end > 0:
                            for line in head[3:end].split('\n'):
                                if line.strip().lower().startswith('title:'):
                                    title = line.split(':', 1)[1].strip().strip('"').strip("'")
                                    break
                except:
                    pass

                index[rel_path] = {
                    'title': title,
                    'size': size,
                    'has_content': size > EMPTY_THRESHOLD,
                    'folder': os.path.dirname(rel_path) or '(raiz)',
                }

    with open(os.path.join(output_dir, '_INDEX.json'), 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

    return len(index)


def print_banner():
    print()
    print('================================================================')
    print(f'  IMPORT VAULT COMPLETE - {VAULT_NAME}')
    print('================================================================')
    print()


def print_summary(imported, skipped_empty, skipped_existing, stats, indexed, mocs, cleaned):
    print()
    print('================================================================')
    print('  IMPORTACAO COMPLETA')
    print('================================================================')
    print(f'  Notas importadas:        {imported}')
    print(f'  Notas vazias (puladas):  {skipped_empty}')
    print(f'  Ja existentes (puladas): {skipped_existing}')
    print(f'  Arquivos antigos limpos: {cleaned}')
    print(f'  Notas indexadas:         {indexed}')
    print(f'  MOCs criados:            {mocs}')
    print()
    print('  Notas por secao:')
    for folder, count in sorted(stats.items(), key=lambda x: -x[1]):
        print(f'    {folder}: {count}')
    print()
    print('  Proximos passos:')
    print('    1. Abra a pasta de saida no Obsidian como vault')
    print('    2. git add notas/')
    print('    3. git commit -m "Add: notas do Mente Lendaria"')
    print('    4. git push')
    print('================================================================')
    print()


def main():
    print_banner()

    # Validar argumentos
    if len(sys.argv) < 2:
        print('USO:')
        print('  python3 import_vault_complete.py <arquivo.json>')
        print('  python3 import_vault_complete.py <arquivo.json> <pasta_destino>')
        print()
        print('EXEMPLO:')
        print('  python3 scripts/import_vault_complete.py ~/Downloads/mente-lendaria-vault.json')
        sys.exit(1)

    json_file = sys.argv[1]
    if not os.path.exists(json_file):
        print(f'[ERRO] Arquivo nao encontrado: {json_file}')
        sys.exit(1)

    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'notas')
    if len(sys.argv) >= 3:
        output_dir = sys.argv[2]

    output_dir = os.path.abspath(output_dir)

    # [1/5] Ler JSON
    print(f'[1/5] Lendo JSON: {json_file}')
    file_size = os.path.getsize(json_file) / (1024 * 1024)
    print(f'  Tamanho: {file_size:.2f} MB')

    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    metadata = data.get('metadata', {})
    notes = data.get('notes', {})
    print(f'  Notas no JSON: {len(notes)}')
    print(f'  Metodo: {metadata.get("method", "N/A")}')
    print(f'  Data: {metadata.get("export_date", "N/A")}')

    # [2/5] Limpar arquivos antigos
    print(f'\n[2/5] Limpando arquivos antigos em: {output_dir}')
    cleaned = clean_old_files(output_dir)
    print(f'  Removidos: {cleaned} arquivos vazios/placeholder')

    # [3/5] Importar notas
    print(f'\n[3/5] Importando {len(notes)} notas...')
    imported, skipped_empty, skipped_existing, stats = import_notes(data, output_dir)
    print(f'  Importadas: {imported}')

    # [4/5] Criar indices
    print(f'\n[4/5] Criando indices...')
    indexed = create_vault_index(output_dir)
    print(f'  Index geral: {indexed} notas')
    json_count = create_json_index(output_dir)
    print(f'  Index JSON: {json_count} entradas')

    # [5/5] Criar MOCs
    print(f'\n[5/5] Criando Maps of Content...')
    mocs = create_folder_mocs(output_dir)
    print(f'  MOCs criados: {mocs}')

    # Resumo
    print_summary(imported, skipped_empty, skipped_existing, stats, indexed, mocs, cleaned)


if __name__ == '__main__':
    main()
