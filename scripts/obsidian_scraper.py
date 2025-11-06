#!/usr/bin/env python3
"""
Obsidian Publish Private Scraper - Mente Lendária
Extrai conteúdo de site Obsidian Publish protegido por senha
"""

from playwright.sync_api import sync_playwright
import os
import time
import re
import json
from urllib.parse import urljoin, urlparse

class MenteLendariaScaper:
    def __init__(self, base_url, password, output_dir):
        self.base_url = base_url
        self.password = password
        self.output_dir = output_dir
        self.visited_urls = set()
        self.all_notes = {}

    def sanitize_filename(self, title):
        """Criar nome de arquivo válido"""
        # Remover caracteres inválidos
        filename = re.sub(r'[<>:"/\\|?*]', '', title)
        filename = filename.strip().replace(' ', '_').replace('/', '-')
        # Remover caracteres especiais mas manter acentos
        filename = re.sub(r'[^\w\s\-_áàâãéèêíïóôõöúçñÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑ]', '', filename)
        return filename[:100] if filename else 'Sem_titulo'

    def scrape_all_notes(self):
        """Scraping usando Playwright"""
        print("🚀 Iniciando scraper com Playwright...")

        with sync_playwright() as p:
            # Iniciar browser (headless para ambiente sem GUI)
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = context.new_page()

            try:
                # Navegar para o site
                print(f"🌐 Acessando: {self.base_url}")
                page.goto(self.base_url, wait_until='networkidle', timeout=30000)
                time.sleep(2)

                # Tentar fazer login se houver campo de senha
                print("🔐 Verificando autenticação...")

                # Método 1: Campo de senha visível
                password_input = page.locator('input[type="password"]')
                if password_input.count() > 0:
                    print("📝 Preenchendo senha...")
                    password_input.fill(self.password)

                    # Procurar botão de submit
                    submit_button = page.locator('button[type="submit"], button:has-text("Entrar"), button:has-text("Login"), input[type="submit"]').first
                    if submit_button.count() > 0:
                        submit_button.click()
                    else:
                        password_input.press('Enter')

                    page.wait_for_timeout(3000)
                    print("✅ Login realizado!")

                # Método 2: Prompt de senha do browser
                page.on("dialog", lambda dialog: dialog.accept(self.password))

                # Aguardar página carregar completamente
                page.wait_for_timeout(2000)

                # Coletar todos os links internos
                print("🔍 Mapeando todas as páginas...")
                all_links = page.evaluate('''() => {
                    const links = new Set();
                    document.querySelectorAll('a[href]').forEach(a => {
                        const href = a.href;
                        if (href && !href.startsWith('http') || href.includes('mentelendaria.com')) {
                            links.add(href);
                        }
                    });
                    return Array.from(links);
                }''')

                # Adicionar URL base se não tiver links
                if not all_links:
                    all_links = [self.base_url]

                # Também tentar pegar do navigation/sidebar
                nav_links = page.evaluate('''() => {
                    const links = new Set();
                    document.querySelectorAll('nav a, aside a, .sidebar a, .tree-item a').forEach(a => {
                        if (a.href) links.add(a.href);
                    });
                    return Array.from(links);
                }''')

                all_links.extend(nav_links)
                all_links = list(set(all_links))  # Remover duplicatas

                print(f"📚 Encontradas {len(all_links)} páginas para processar")

                # Criar diretório de saída
                os.makedirs(self.output_dir, exist_ok=True)

                # Processar cada link
                for i, link in enumerate(all_links, 1):
                    if link in self.visited_urls:
                        continue

                    self.visited_urls.add(link)
                    print(f"\n📥 [{i}/{len(all_links)}] Processando: {link}")

                    try:
                        # Navegar para a página
                        page.goto(link, wait_until='networkidle', timeout=15000)
                        page.wait_for_timeout(1000)

                        # Extrair título
                        title = page.title()
                        if not title or title == "":
                            title = page.evaluate('''() => {
                                const h1 = document.querySelector('h1');
                                return h1 ? h1.textContent : 'Sem Título';
                            }''')

                        print(f"   📄 Título: {title}")

                        # Extrair conteúdo principal
                        content = page.evaluate('''() => {
                            // Tentar diferentes seletores de conteúdo
                            const selectors = [
                                'article',
                                '.markdown-preview-view',
                                '.content',
                                'main',
                                '.note-content',
                                '.page-content',
                                '[data-content]'
                            ];

                            for (const selector of selectors) {
                                const element = document.querySelector(selector);
                                if (element) {
                                    return element.innerHTML;
                                }
                            }

                            // Fallback: pegar o body
                            return document.body.innerHTML;
                        }''')

                        # Extrair texto limpo também
                        text_content = page.evaluate('''() => {
                            const selectors = [
                                'article',
                                '.markdown-preview-view',
                                '.content',
                                'main'
                            ];

                            for (const selector of selectors) {
                                const element = document.querySelector(selector);
                                if (element) {
                                    return element.innerText;
                                }
                            }

                            return document.body.innerText;
                        }''')

                        # Salvar nota
                        filename = self.sanitize_filename(title)
                        if not filename.endswith('.md'):
                            filename += '.md'

                        filepath = os.path.join(self.output_dir, filename)

                        # Criar conteúdo Markdown com frontmatter
                        markdown_content = f"""---
title: {title}
source: {link}
date_imported: {time.strftime('%Y-%m-%d %H:%M:%S')}
---

# {title}

{text_content}

---

<details>
<summary>📎 Conteúdo HTML Original</summary>

{content}

</details>
"""

                        # Salvar arquivo
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(markdown_content)

                        self.all_notes[link] = filename
                        print(f"   ✅ Salvo: {filename}")

                        time.sleep(0.5)  # Rate limiting

                    except Exception as e:
                        print(f"   ❌ Erro ao processar página: {e}")
                        continue

                # Salvar índice de páginas
                index_file = os.path.join(self.output_dir, '_INDEX.json')
                with open(index_file, 'w', encoding='utf-8') as f:
                    json.dump(self.all_notes, f, indent=2, ensure_ascii=False)

                print(f"\n🎉 Scraping concluído! {len(self.all_notes)} notas extraídas")
                print(f"📁 Salvas em: {self.output_dir}")

            except Exception as e:
                print(f"\n❌ Erro geral: {e}")
                import traceback
                traceback.print_exc()
            finally:
                browser.close()

def main():
    # CONFIGURAÇÃO
    BASE_URL = "https://mentelendaria.com"
    PASSWORD = "@88888888#"
    OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "notas")

    print("""
╔═══════════════════════════════════════════════════╗
║   🧠 MENTE LENDÁRIA - SCRAPER DE NOTAS 🧠        ║
║   Extração de Segundo Cérebro do Alan            ║
╚═══════════════════════════════════════════════════╝
""")

    scraper = MenteLendariaScaper(BASE_URL, PASSWORD, OUTPUT_DIR)
    scraper.scrape_all_notes()

    print("\n✅ Processo concluído com sucesso!")

if __name__ == "__main__":
    main()
