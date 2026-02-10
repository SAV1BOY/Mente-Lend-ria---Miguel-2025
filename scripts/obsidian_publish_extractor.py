#!/usr/bin/env python3
"""
Obsidian Publish Extractor - Mente Lendaria
============================================
Extrai TODAS as notas do Obsidian Publish usando a API POST correta.

INSTALACAO:
    pip install requests

EXECUCAO:
    python3 obsidian_publish_extractor.py

Este script usa a API interna do Obsidian Publish que funciona com POST requests.
Os scripts anteriores falhavam porque usavam GET requests.
"""

import requests
import hashlib
import json
import os
import sys
import time
import re
from urllib.parse import unquote
from pathlib import Path


# ============================================================
# CONFIGURACAO - Edite aqui se necessario
# ============================================================
SITE_ID = "f431548d64f3cdad0278eb0b35aa11fe"
PASSWORD = "@88888888#"
PUBLISH_HOST = "publish-01.obsidian.md"
PUBLISH_URL = f"https://{PUBLISH_HOST}"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "notas")
# ============================================================


def sha256_hash(text):
    """Gera hash SHA256 de um texto."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def create_session():
    """Cria sessao HTTP com headers de navegador."""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'Content-Type': 'application/json',
        'Origin': 'https://mentelendaria.com',
        'Referer': 'https://mentelendaria.com/',
    })
    return session


def get_site_cache(session, site_id, password):
    """
    Obtem o cache do site (lista de todos os arquivos) via POST.

    A API do Obsidian Publish usa POST, nao GET.
    O password pode ser enviado em texto puro ou como SHA256.
    """
    url = f"{PUBLISH_URL}/cache/{site_id}"

    # Tentar com diferentes formatos de senha
    password_variants = [
        {"id": site_id, "password": sha256_hash(password)},
        {"id": site_id, "password": password},
        {"id": site_id},
    ]

    for i, payload in enumerate(password_variants):
        try:
            print(f"  Tentativa {i+1}/3: POST {url}")
            response = session.post(url, json=payload, timeout=30)

            if response.status_code == 200:
                data = response.json()
                if data:
                    print(f"  [OK] Cache obtido com sucesso!")
                    return data
                else:
                    print(f"  [AVISO] Resposta vazia")
            else:
                print(f"  [ERRO] Status {response.status_code}: {response.text[:200]}")

        except requests.exceptions.JSONDecodeError:
            print(f"  [AVISO] Resposta nao e JSON, tentando texto...")
            if response.status_code == 200:
                return {"raw": response.text}
        except Exception as e:
            print(f"  [ERRO] {e}")

    return None


def get_file_content(session, site_id, file_path, password, file_hash=None):
    """
    Obtem o conteudo de um arquivo especifico via POST.
    """
    url = f"{PUBLISH_URL}/access/{site_id}"

    payload = {
        "id": site_id,
        "path": file_path,
        "password": sha256_hash(password),
    }

    if file_hash:
        payload["hash"] = file_hash

    try:
        response = session.post(url, json=payload, timeout=30)

        if response.status_code == 200:
            return response.text

        # Tentar com senha em texto puro
        payload["password"] = password
        response = session.post(url, json=payload, timeout=30)

        if response.status_code == 200:
            return response.text

        # Tentar sem senha
        del payload["password"]
        response = session.post(url, json=payload, timeout=30)

        if response.status_code == 200:
            return response.text

        return None

    except Exception as e:
        print(f"    [ERRO] {e}")
        return None


def sanitize_path(path):
    """Limpa o caminho do arquivo mantendo a estrutura de pastas."""
    # Decodificar URL encoding
    path = unquote(path)

    # Remover .md duplicado
    if path.endswith('.md.md'):
        path = path[:-3]

    # Garantir extensao .md
    if not path.endswith('.md'):
        path = path + '.md'

    # Remover caracteres invalidos para filesystem
    # Manter: letras, numeros, espacos, acentos, /, -, _, ., (, ), emojis
    parts = path.split('/')
    clean_parts = []
    for part in parts:
        # Remover apenas caracteres realmente problematicos
        part = part.replace(':', ' -')
        part = part.replace('|', '-')
        part = part.replace('<', '')
        part = part.replace('>', '')
        part = part.replace('"', '')
        part = part.replace('\\', '')
        part = part.replace('*', '')
        part = part.strip()
        if part:
            clean_parts.append(part)

    return '/'.join(clean_parts)


def create_frontmatter(title, source_path, tags=None):
    """Cria frontmatter YAML para o arquivo Obsidian."""
    fm = f"""---
title: "{title}"
source_path: "{source_path}"
date_imported: "{time.strftime('%Y-%m-%d %H:%M:%S')}"
vault: "Mente Lendaria - Segundo Cerebro do Alan"
"""
    if tags:
        fm += f"tags: {json.dumps(tags, ensure_ascii=False)}\n"
    fm += "---\n\n"
    return fm


def extract_title_from_content(content, file_path):
    """Extrai titulo do conteudo ou do caminho do arquivo."""
    # Tentar extrair do frontmatter existente
    if content.startswith('---'):
        end = content.find('---', 3)
        if end > 0:
            fm = content[3:end]
            for line in fm.split('\n'):
                if line.strip().startswith('title:'):
                    title = line.split(':', 1)[1].strip()
                    title = title.strip('"').strip("'")
                    if title:
                        return title

    # Tentar extrair do primeiro heading
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('# '):
            return line[2:].strip()

    # Usar nome do arquivo
    name = os.path.basename(file_path)
    if name.endswith('.md'):
        name = name[:-3]
    return name


def parse_cache_files(cache_data):
    """
    Extrai a lista de arquivos do cache do Obsidian Publish.

    O cache pode ter diferentes formatos dependendo da versao:
    - {"files": {"path.md": {"hash": "..."}}}
    - Lista direta de paths
    - {"cache": {"path.md": {"hash": "..."}}}
    """
    files = {}

    if not cache_data:
        return files

    if isinstance(cache_data, dict):
        # Formato: {"files": {...}} ou diretamente os arquivos
        file_dict = None

        if "files" in cache_data:
            file_dict = cache_data["files"]
        elif "cache" in cache_data:
            file_dict = cache_data["cache"]
        else:
            # Pode ser o dict direto de arquivos
            # Verificar se as chaves parecem paths de arquivo
            for key in cache_data:
                if key.endswith('.md') or '/' in key:
                    file_dict = cache_data
                    break

        if file_dict and isinstance(file_dict, dict):
            for path, info in file_dict.items():
                if path.endswith('.md'):
                    file_hash = None
                    if isinstance(info, dict):
                        file_hash = info.get('hash', info.get('h', None))
                    elif isinstance(info, str):
                        file_hash = info
                    files[path] = file_hash

    elif isinstance(cache_data, list):
        for item in cache_data:
            if isinstance(item, str):
                files[item] = None
            elif isinstance(item, dict):
                path = item.get('path', item.get('name', ''))
                file_hash = item.get('hash', item.get('h', None))
                if path:
                    files[path] = file_hash

    return files


def download_all_notes(session, site_id, password, files, output_dir):
    """Baixa todas as notas e salva na estrutura de pastas."""
    os.makedirs(output_dir, exist_ok=True)

    total = len(files)
    downloaded = 0
    failed = []
    skipped = []

    for i, (file_path, file_hash) in enumerate(files.items(), 1):
        # Limpar o caminho
        clean_path = sanitize_path(file_path)
        local_path = os.path.join(output_dir, clean_path)

        # Verificar se ja existe com conteudo
        if os.path.exists(local_path):
            existing_size = os.path.getsize(local_path)
            if existing_size > 100:  # Ja tem conteudo (nao so frontmatter vazio)
                skipped.append(file_path)
                print(f"  [{i}/{total}] [SKIP] {clean_path} (ja existe com conteudo)")
                continue

        print(f"  [{i}/{total}] Baixando: {file_path}")

        # Baixar conteudo
        content = get_file_content(session, site_id, file_path, password, file_hash)

        if content and len(content.strip()) > 0:
            # Extrair titulo
            title = extract_title_from_content(content, file_path)

            # Determinar tags baseado no caminho
            tags = []
            path_parts = file_path.split('/')
            if len(path_parts) > 1:
                tags = [p for p in path_parts[:-1] if p]

            # Verificar se conteudo ja tem frontmatter
            if content.strip().startswith('---'):
                # Manter frontmatter original, adicionar metadados extras
                final_content = content
            else:
                # Adicionar frontmatter
                frontmatter = create_frontmatter(title, file_path, tags)
                final_content = frontmatter + content

            # Criar diretorios
            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            # Salvar arquivo
            with open(local_path, 'w', encoding='utf-8') as f:
                f.write(final_content)

            downloaded += 1
            print(f"    [OK] Salvo: {clean_path}")
        else:
            failed.append(file_path)
            print(f"    [FALHOU] Sem conteudo para: {file_path}")

        # Rate limiting - ser gentil com o servidor
        time.sleep(0.3)

    return downloaded, failed, skipped


def create_vault_index(output_dir):
    """Cria um indice do vault para navegacao no Obsidian."""
    index_entries = []

    for root, dirs, files in os.walk(output_dir):
        for file in sorted(files):
            if file.endswith('.md') and file != '_INDEX.md' and file != '_INDEX.json':
                rel_path = os.path.relpath(os.path.join(root, file), output_dir)
                # Converter para link Obsidian
                link_path = rel_path.replace('.md', '').replace('\\', '/')
                index_entries.append(f"- [[{link_path}]]")

    index_content = """---
title: "Indice do Vault"
date_imported: "{date}"
---

# Mente Lendaria - Segundo Cerebro do Alan

## Todas as Notas

{entries}

---

Total: {total} notas
""".format(
        date=time.strftime('%Y-%m-%d %H:%M:%S'),
        entries='\n'.join(index_entries),
        total=len(index_entries)
    )

    index_path = os.path.join(output_dir, '_INDEX.md')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_content)

    print(f"\n  [OK] Indice criado: _INDEX.md ({len(index_entries)} notas)")


def create_json_index(output_dir):
    """Cria indice JSON para buscas programaticas."""
    index = {}

    for root, dirs, files in os.walk(output_dir):
        for file in sorted(files):
            if file.endswith('.md'):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, output_dir)

                # Ler primeiras linhas para extrair metadados
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read(500)

                    title = file[:-3]  # Remove .md
                    if content.startswith('---'):
                        end = content.find('---', 3)
                        if end > 0:
                            for line in content[3:end].split('\n'):
                                if line.strip().startswith('title:'):
                                    title = line.split(':', 1)[1].strip().strip('"').strip("'")
                                    break

                    index[rel_path] = {
                        "title": title,
                        "size": os.path.getsize(full_path),
                        "has_content": os.path.getsize(full_path) > 100,
                    }
                except:
                    pass

    index_path = os.path.join(output_dir, '_INDEX.json')
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

    print(f"  [OK] Indice JSON criado: _INDEX.json")


def print_banner():
    print("""
================================================================
   OBSIDIAN PUBLISH EXTRACTOR - Mente Lendaria
   Segundo Cerebro do Alan - Extracao Completa
================================================================
    """)


def print_summary(downloaded, failed, skipped, total):
    print(f"""
================================================================
   RESUMO DA EXTRACAO
================================================================
   Total de arquivos no vault:  {total}
   Baixados com sucesso:        {downloaded}
   Ja existentes (pulados):     {len(skipped)}
   Falharam:                    {len(failed)}
================================================================
""")

    if failed:
        print("  Arquivos que falharam:")
        for f in failed:
            print(f"    - {f}")
        print()


def main():
    print_banner()

    print(f"[1/4] Configuracao:")
    print(f"  Site ID:    {SITE_ID}")
    print(f"  Host:       {PUBLISH_HOST}")
    print(f"  Saida:      {OUTPUT_DIR}")
    print()

    # Criar sessao
    session = create_session()

    # Obter cache do site
    print("[2/4] Obtendo lista de arquivos do vault...")
    cache_data = get_site_cache(session, SITE_ID, PASSWORD)

    if cache_data is None:
        print()
        print("  [ERRO] Nao foi possivel obter o cache do site.")
        print("  Isso pode acontecer se:")
        print("    1. O site mudou de endereco ou foi removido")
        print("    2. A senha esta incorreta")
        print("    3. O firewall/proxy esta bloqueando a conexao")
        print()
        print("  Tentando com lista de arquivos conhecidos...")
        print()

        # Fallback: usar lista conhecida de arquivos
        files = get_known_files()
    else:
        # Extrair lista de arquivos do cache
        files = parse_cache_files(cache_data)

        if not files:
            print("  [AVISO] Cache obtido mas sem arquivos parseados.")
            print("  Formato do cache recebido:")
            if isinstance(cache_data, dict):
                print(f"    Chaves: {list(cache_data.keys())[:10]}")
            print()
            print("  Usando lista de arquivos conhecidos como fallback...")
            files = get_known_files()

    total = len(files)
    print(f"\n  Total de arquivos encontrados: {total}")
    print()

    if total == 0:
        print("  [ERRO] Nenhum arquivo encontrado. Verifique as configuracoes.")
        sys.exit(1)

    # Baixar todas as notas
    print(f"[3/4] Baixando {total} notas...")
    downloaded, failed, skipped = download_all_notes(
        session, SITE_ID, PASSWORD, files, OUTPUT_DIR
    )

    # Criar indices
    print("\n[4/4] Criando indices...")
    create_vault_index(OUTPUT_DIR)
    create_json_index(OUTPUT_DIR)

    # Resumo
    print_summary(downloaded, failed, skipped, total)

    print("  Proximos passos:")
    print("    1. Abra a pasta 'notas/' no Obsidian")
    print("    2. Verifique se as notas foram importadas corretamente")
    print("    3. Faca commit: git add notas/ && git commit -m 'Add notes'")
    print("    4. Push: git push")
    print()


def get_known_files():
    """
    Lista de arquivos conhecidos do vault como fallback.
    Extraida da navegacao do site em sessoes anteriores.
    """
    known = [
        "bem-vindo(a).md",
        # Anotacoes
        "Anotacoes/Guia dos Apodicticos.md",
        # Sobre Mim
        "Sobre Mim/Index.md",
        "Sobre Mim/Agora.md",
        "Sobre Mim/anos mais desesperadores da minha vida.md",
        "Sobre Mim/Como eu me tornei um otimista.md",
        "Sobre Mim/Entre Ausencias e Aparicoes O Que Aconteceu Comigo.md",
        "Sobre Mim/Essencia.md",
        "Sobre Mim/Eu do futuro.md",
        "Sobre Mim/Eu x  Eu publico.md",
        "Sobre Mim/Frases Alan.md",
        "Sobre Mim/Jornada e Historia.md",
        "Sobre Mim/Memorias Alan & Steven.md",
        "Sobre Mim/Minha Missao.md",
        "Sobre Mim/Projetos Atuais.md",
        "Sobre Mim/Quem e Alan Nicolas.md",
        "Sobre Mim/Visao de 2017 para 2022.md",
        # Conhecimento
        "Conhecimento/Index.md",
        "Conhecimento/README.md",
        # YouTube
        "Conhecimento/YouTube/Algoritmo do YouTube.md",
        "Conhecimento/YouTube/Codigo YouTube.md",
        "Conhecimento/YouTube/Dominando YouTube.md",
    ]
    return {f: None for f in known}


if __name__ == "__main__":
    main()
