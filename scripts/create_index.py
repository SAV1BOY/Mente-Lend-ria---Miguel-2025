#!/usr/bin/env python3
"""
Create Index - Mente Lendária
Cria um índice de todas as notas importadas
"""

import os
import json
import re
from pathlib import Path

def extract_frontmatter(content):
    """Extrair metadados do frontmatter YAML"""
    frontmatter = {}

    # Regex para encontrar frontmatter
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)

    if match:
        yaml_content = match.group(1)
        for line in yaml_content.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()

    return frontmatter

def extract_title(content, filename):
    """Extrair título da nota"""
    # Tentar extrair do frontmatter
    frontmatter = extract_frontmatter(content)
    if 'title' in frontmatter:
        return frontmatter['title']

    # Tentar extrair do primeiro H1
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1)

    # Usar nome do arquivo
    return filename.replace('.md', '').replace('_', ' ')

def create_index(notes_dir='notas'):
    """Criar índice de todas as notas"""
    notes_path = Path(notes_dir)

    if not notes_path.exists():
        print(f"❌ Pasta '{notes_dir}' não encontrada!")
        return

    # Coletar informações de todas as notas
    notes = []

    for md_file in notes_path.glob('*.md'):
        if md_file.name.startswith('_'):
            continue  # Pular arquivos de índice

        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            frontmatter = extract_frontmatter(content)
            title = extract_title(content, md_file.name)

            # Contar palavras
            word_count = len(content.split())

            note_info = {
                'filename': md_file.name,
                'title': title,
                'source': frontmatter.get('source', ''),
                'date_imported': frontmatter.get('date_imported', ''),
                'tags': frontmatter.get('tags', ''),
                'word_count': word_count
            }

            notes.append(note_info)

        except Exception as e:
            print(f"⚠️ Erro ao processar {md_file.name}: {e}")

    # Ordenar por título
    notes.sort(key=lambda x: x['title'])

    # Salvar como JSON
    json_file = notes_path / '_INDEX.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(notes, f, indent=2, ensure_ascii=False)

    # Criar índice Markdown
    md_index = notes_path / '_INDEX.md'

    with open(md_index, 'w', encoding='utf-8') as f:
        f.write("# 📚 Índice de Notas - Mente Lendária\n\n")
        f.write(f"**Total de notas**: {len(notes)}\n\n")
        f.write("---\n\n")

        # Agrupar por letra
        current_letter = ''
        for note in notes:
            first_letter = note['title'][0].upper() if note['title'] else '#'

            if first_letter != current_letter:
                current_letter = first_letter
                f.write(f"\n## {current_letter}\n\n")

            f.write(f"- **[{note['title']}]({note['filename']})**\n")

            if note['source']:
                f.write(f"  - 🔗 Fonte: {note['source']}\n")

            f.write(f"  - 📊 {note['word_count']} palavras\n")

            if note['date_imported']:
                f.write(f"  - 📅 Importado em: {note['date_imported']}\n")

            f.write("\n")

    print(f"\n✅ Índice criado com sucesso!")
    print(f"📊 Total de notas: {len(notes)}")
    print(f"📁 Arquivos criados:")
    print(f"   - {json_file}")
    print(f"   - {md_index}")

if __name__ == "__main__":
    create_index()
