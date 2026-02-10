#!/usr/bin/env python3
"""
Obsidian Publish Scraper com Playwright - Mente Lendaria
=========================================================
Usa Playwright para abrir o site, autenticar e extrair TODAS as notas
via API do Obsidian Publish (POST requests) de dentro do navegador.

INSTALACAO:
    pip install playwright
    playwright install chromium

EXECUCAO:
    python3 obsidian_scraper.py

    # Modo com interface grafica (recomendado para primeira vez):
    python3 obsidian_scraper.py --headed

    # Modo headless (automatico):
    python3 obsidian_scraper.py --headless
"""

import os
import sys
import json
import time
import re
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print('[ERRO] Playwright nao esta instalado.')
    print('Execute: pip install playwright && playwright install chromium')
    sys.exit(1)


# ============================================================
# CONFIGURACAO
# ============================================================
SITE_URL = "https://mentelendaria.com"
SITE_ID = "f431548d64f3cdad0278eb0b35aa11fe"
PASSWORD = "@88888888#"
PUBLISH_API = "https://publish-01.obsidian.md"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "notas")
# ============================================================


def sanitize_path(path):
    """Limpa caminho de arquivo mantendo estrutura de pastas."""
    while path.endswith('.md.md'):
        path = path[:-3]
    if not path.endswith('.md'):
        path += '.md'

    path = path.replace(':', ' -')
    path = path.replace('|', '-')
    path = path.replace('<', '').replace('>', '')
    path = path.replace('"', '').replace('\\', '/')
    path = path.replace('*', '')

    return path


def main():
    # Verificar argumentos
    headed = '--headed' in sys.argv or '--head' in sys.argv
    headless = '--headless' in sys.argv

    # Default: headed (mais confiavel para autenticacao)
    if not headless:
        headed = True

    print('================================================================')
    print('  OBSIDIAN PUBLISH SCRAPER - Mente Lendaria')
    print('  Usando Playwright para extracao completa')
    print(f'  Modo: {"Com interface" if headed else "Headless"}')
    print('================================================================')
    print()

    with sync_playwright() as p:
        # Iniciar navegador
        print('[1/5] Iniciando navegador...')
        browser = p.chromium.launch(headless=not headed)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            viewport={'width': 1280, 'height': 800}
        )
        page = context.new_page()

        try:
            # Acessar o site
            print(f'[2/5] Acessando {SITE_URL}...')
            page.goto(SITE_URL, wait_until='networkidle', timeout=30000)
            page.wait_for_timeout(2000)

            # Autenticar
            print('[3/5] Autenticando...')
            password_input = page.locator('input[type="password"]')

            if password_input.count() > 0:
                password_input.fill(PASSWORD)
                page.wait_for_timeout(500)

                # Tentar clicar no botao de submit
                submit = page.locator('button[type="submit"], button:has-text("Enter"), button:has-text("Submit"), button:has-text("Entrar")')
                if submit.count() > 0:
                    submit.first.click()
                else:
                    password_input.press('Enter')

                page.wait_for_timeout(5000)
                print('  [OK] Senha submetida')
            else:
                print('  [INFO] Nenhum campo de senha encontrado - talvez ja autenticado')

            # Aguardar o site carregar completamente
            page.wait_for_timeout(3000)

            # Usar a API do Obsidian Publish de dentro do navegador
            print('[4/5] Extraindo notas via API do Obsidian Publish...')

            # Executar JavaScript no contexto do navegador para:
            # 1. Obter cache (lista de todos os arquivos)
            # 2. Baixar cada arquivo
            result = page.evaluate('''async () => {
                const SITE_ID = "''' + SITE_ID + '''";
                const API_BASE = "''' + PUBLISH_API + '''";

                // Obter password hash
                let passwordHash = '';
                const stored = localStorage.getItem('publish-site-password-' + SITE_ID) ||
                               sessionStorage.getItem('publish-site-password-' + SITE_ID);

                if (stored) {
                    passwordHash = stored;
                } else {
                    // Gerar hash da senha
                    const encoder = new TextEncoder();
                    const data = encoder.encode("''' + PASSWORD + '''");
                    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
                    const hashArray = Array.from(new Uint8Array(hashBuffer));
                    passwordHash = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
                }

                // 1. Obter cache
                let cacheData = null;
                try {
                    const resp = await fetch(`${API_BASE}/cache/${SITE_ID}`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ id: SITE_ID, password: passwordHash })
                    });

                    if (resp.ok) {
                        cacheData = await resp.json();
                    } else {
                        // Tentar sem senha
                        const retry = await fetch(`${API_BASE}/cache/${SITE_ID}`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ id: SITE_ID })
                        });
                        if (retry.ok) {
                            cacheData = await retry.json();
                        }
                    }
                } catch (e) {
                    return { error: 'cache_failed', message: e.message };
                }

                if (!cacheData) {
                    return { error: 'no_cache', message: 'Falha ao obter cache' };
                }

                // Extrair lista de arquivos .md
                const fileSource = cacheData.files || cacheData.cache || cacheData;
                const files = {};

                for (const [path, info] of Object.entries(fileSource)) {
                    if (path.endsWith('.md')) {
                        files[path] = typeof info === 'object' ? (info.hash || info.h || null) : info;
                    }
                }

                const totalFiles = Object.keys(files).length;

                if (totalFiles === 0) {
                    return {
                        error: 'no_files',
                        message: 'Nenhum arquivo .md encontrado',
                        cache_keys: Object.keys(cacheData).slice(0, 10)
                    };
                }

                // 2. Baixar cada arquivo
                const notes = {};
                let downloaded = 0;
                let failed = 0;

                for (const [filePath, fileHash] of Object.entries(files)) {
                    try {
                        const payload = {
                            id: SITE_ID,
                            path: filePath,
                            password: passwordHash
                        };

                        if (fileHash) payload.hash = fileHash;

                        const resp = await fetch(`${API_BASE}/access/${SITE_ID}`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(payload)
                        });

                        if (resp.ok) {
                            notes[filePath] = await resp.text();
                            downloaded++;
                        } else {
                            failed++;
                        }

                        // Rate limiting
                        await new Promise(r => setTimeout(r, 150));
                    } catch (e) {
                        failed++;
                    }
                }

                return {
                    success: true,
                    total: totalFiles,
                    downloaded: downloaded,
                    failed: failed,
                    files: files,
                    notes: notes
                };
            }''')

            # Processar resultado
            if not result:
                print('  [ERRO] Nenhum resultado retornado do JavaScript')
                return fallback_dom_extraction(page)

            if 'error' in result:
                print(f'  [ERRO] {result.get("message", "Erro desconhecido")}')
                if 'cache_keys' in result:
                    print(f'  Cache keys: {result["cache_keys"]}')
                print('  Tentando extracao alternativa via DOM...')
                return fallback_dom_extraction(page)

            total = result.get('total', 0)
            downloaded = result.get('downloaded', 0)
            failed = result.get('failed', 0)
            notes = result.get('notes', {})

            print(f'  [OK] {downloaded} de {total} notas baixadas ({failed} falhas)')

            # 5. Salvar arquivos
            print(f'[5/5] Salvando {len(notes)} notas em {OUTPUT_DIR}...')
            os.makedirs(OUTPUT_DIR, exist_ok=True)

            saved = 0
            for file_path, content in notes.items():
                if not content or not content.strip():
                    continue

                clean_path = sanitize_path(file_path)
                local_path = os.path.join(OUTPUT_DIR, clean_path)

                os.makedirs(os.path.dirname(local_path), exist_ok=True)

                # Adicionar frontmatter se nao tiver
                if not content.strip().startswith('---'):
                    title = os.path.basename(file_path).replace('.md', '')
                    tags = [p for p in file_path.split('/')[:-1] if p]
                    frontmatter = f'---\ntitle: "{title}"\nsource_path: "{file_path}"\ndate_imported: "{time.strftime("%Y-%m-%d %H:%M:%S")}"\n'
                    if tags:
                        frontmatter += f'tags: {json.dumps(tags, ensure_ascii=False)}\n'
                    frontmatter += '---\n\n'
                    content = frontmatter + content

                with open(local_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                saved += 1

            # Salvar JSON completo como backup
            export_data = {
                'metadata': {
                    'source': SITE_URL,
                    'site_id': SITE_ID,
                    'export_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'total_notes': saved,
                },
                'notes': notes
            }

            backup_path = os.path.join(OUTPUT_DIR, '_export_backup.json')
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            # Criar indice
            create_index(OUTPUT_DIR)

            print()
            print('================================================================')
            print(f'  EXTRACAO COMPLETA!')
            print(f'  Notas salvas: {saved}')
            print(f'  Pasta: {OUTPUT_DIR}')
            print(f'  Backup JSON: _export_backup.json')
            print('================================================================')

        except Exception as e:
            print(f'[ERRO] {e}')
            import traceback
            traceback.print_exc()
        finally:
            browser.close()


def fallback_dom_extraction(page):
    """Extracao alternativa via navegacao do DOM."""
    print('  Extraindo links da sidebar...')

    # Expandir todas as pastas colapsadas
    page.evaluate('''() => {
        document.querySelectorAll('.tree-item.is-collapsed').forEach(item => {
            const icon = item.querySelector('.tree-item-icon, .collapse-icon');
            if (icon) icon.click();
        });
    }''')

    page.wait_for_timeout(2000)

    # Coletar todos os links
    links = page.evaluate('''() => {
        const paths = new Set();
        document.querySelectorAll('[data-path]').forEach(el => {
            const p = el.getAttribute('data-path');
            if (p) paths.add(p);
        });
        document.querySelectorAll('.tree-item-self').forEach(el => {
            const p = el.getAttribute('data-path');
            if (p) paths.add(p);
        });
        document.querySelectorAll('a[href]').forEach(el => {
            const href = el.getAttribute('href');
            if (href && !href.startsWith('http') && !href.startsWith('#')) {
                let p = href.replace(/^\\//, '');
                if (!p.endsWith('.md')) p += '.md';
                paths.add(p);
            }
        });
        return Array.from(paths);
    }''')

    print(f'  Encontrados {len(links)} links')

    if not links:
        print('  [AVISO] Nenhum link encontrado. Tente em modo --headed')
        return

    # Navegar para cada pagina e extrair conteudo
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    saved = 0

    for i, link in enumerate(links, 1):
        url = f'{SITE_URL}/{link}' if not link.startswith('http') else link
        print(f'  [{i}/{len(links)}] {link}')

        try:
            page.goto(url, wait_until='networkidle', timeout=15000)
            page.wait_for_timeout(1000)

            content = page.evaluate('''() => {
                const el = document.querySelector('.markdown-preview-view') ||
                          document.querySelector('article') ||
                          document.querySelector('.content') ||
                          document.querySelector('main');
                return el ? el.innerText : document.body.innerText;
            }''')

            title = page.evaluate('''() => {
                const h1 = document.querySelector('h1');
                return h1 ? h1.textContent : document.title;
            }''')

            if content and content.strip():
                clean_path = sanitize_path(link if link.endswith('.md') else link + '.md')
                local_path = os.path.join(OUTPUT_DIR, clean_path)
                os.makedirs(os.path.dirname(local_path), exist_ok=True)

                md = f'---\ntitle: "{title}"\nsource: "{url}"\ndate_imported: "{time.strftime("%Y-%m-%d %H:%M:%S")}"\n---\n\n'
                md += f'# {title}\n\n{content}\n'

                with open(local_path, 'w', encoding='utf-8') as f:
                    f.write(md)

                saved += 1
        except Exception as e:
            print(f'    [ERRO] {e}')

        page.wait_for_timeout(500)

    create_index(OUTPUT_DIR)

    print(f'\n  [OK] {saved} notas salvas via DOM extraction')


def create_index(output_dir):
    """Cria indice Obsidian."""
    entries = []
    for root, dirs, files in os.walk(output_dir):
        for f in sorted(files):
            if f.endswith('.md') and not f.startswith('_'):
                rel = os.path.relpath(os.path.join(root, f), output_dir)
                link = rel.replace('.md', '').replace('\\', '/')
                entries.append(f'- [[{link}]]')

    idx = f'---\ntitle: "Indice do Vault"\ndate: "{time.strftime("%Y-%m-%d")}"\n---\n\n'
    idx += '# Mente Lendaria - Segundo Cerebro do Alan\n\n'
    idx += '\n'.join(entries)
    idx += f'\n\n---\nTotal: {len(entries)} notas\n'

    with open(os.path.join(output_dir, '_INDEX.md'), 'w', encoding='utf-8') as f:
        f.write(idx)

    # JSON index
    jidx = {}
    for root, dirs, files in os.walk(output_dir):
        for f in sorted(files):
            if f.endswith('.md'):
                fp = os.path.join(root, f)
                rel = os.path.relpath(fp, output_dir)
                jidx[rel] = {'title': f[:-3], 'size': os.path.getsize(fp)}

    with open(os.path.join(output_dir, '_INDEX.json'), 'w', encoding='utf-8') as f:
        json.dump(jidx, f, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    main()
