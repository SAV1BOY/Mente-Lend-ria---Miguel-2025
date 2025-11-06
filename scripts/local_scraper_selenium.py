#!/usr/bin/env python3
"""
Local Selenium Scraper - Mente Lendária
Para rodar localmente no computador do usuário (com interface gráfica)

INSTALAÇÃO:
pip install selenium webdriver-manager

EXECUÇÃO:
python3 local_scraper_selenium.py
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import json
import re

class SeleniumScraper:
    def __init__(self, base_url, password, output_dir):
        self.base_url = base_url
        self.password = password
        self.output_dir = output_dir
        self.visited_urls = set()
        self.all_notes = {}

        # Configurar Chrome
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        options.add_argument('--disable-blink-features=AutomationControlled')

        # Iniciar driver
        print("🚀 Iniciando Chrome...")
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )

    def sanitize_filename(self, title):
        """Criar nome de arquivo válido"""
        if not title:
            return 'Sem_titulo'
        filename = re.sub(r'[<>:"/\\|?*]', '', title)
        filename = filename.strip().replace(' ', '_').replace('/', '-')
        filename = re.sub(r'[^\w\s\-_áàâãéèêíïóôõöúçñÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑ]', '', filename)
        return filename[:100] if filename else 'Sem_titulo'

    def login(self):
        """Fazer login no site"""
        print(f"🌐 Acessando: {self.base_url}")
        self.driver.get(self.base_url)
        time.sleep(3)

        try:
            # Procurar campo de senha
            password_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="password"]'))
            )

            print("🔐 Preenchendo senha...")
            password_field.send_keys(self.password)

            # Procurar botão de submit
            submit_buttons = self.driver.find_elements(By.CSS_SELECTOR,
                'button[type="submit"], button:contains("Entrar"), input[type="submit"]')

            if submit_buttons:
                submit_buttons[0].click()
            else:
                password_field.submit()

            time.sleep(5)
            print("✅ Login realizado!")

        except Exception as e:
            print(f"⚠️ Não foi necessário fazer login ou erro: {e}")

    def extract_all_links(self):
        """Extrair todos os links do site"""
        print("🔍 Mapeando todas as páginas...")

        links = set()

        # JavaScript para pegar todos os links
        js_script = """
        const links = new Set();
        document.querySelectorAll('a[href]').forEach(a => {
            const href = a.href;
            if (href && (href.includes('mentelendaria.com') || !href.startsWith('http'))) {
                links.add(href);
            }
        });
        return Array.from(links);
        """

        page_links = self.driver.execute_script(js_script)

        for link in page_links:
            if link not in links:
                links.add(link)

        # Também tentar no navigation/sidebar
        try:
            nav_elements = self.driver.find_elements(By.CSS_SELECTOR,
                'nav a, aside a, .sidebar a, .tree-item a, .nav-link')

            for element in nav_elements:
                href = element.get_attribute('href')
                if href:
                    links.add(href)
        except Exception as e:
            print(f"⚠️ Erro ao extrair links de navegação: {e}")

        print(f"📚 Encontradas {len(links)} páginas")
        return list(links)

    def extract_note_content(self, url):
        """Extrair conteúdo de uma nota"""
        try:
            self.driver.get(url)
            time.sleep(2)

            # Extrair título
            title = self.driver.title

            try:
                h1 = self.driver.find_element(By.TAG_NAME, 'h1')
                title = h1.text
            except:
                pass

            if not title:
                title = "Sem Título"

            # Extrair conteúdo
            selectors = [
                'article',
                '.markdown-preview-view',
                '.content',
                'main',
                '.note-content',
                '.page-content'
            ]

            content_element = None
            for selector in selectors:
                try:
                    content_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if content_element:
                        break
                except:
                    continue

            if not content_element:
                content_element = self.driver.find_element(By.TAG_NAME, 'body')

            # Pegar texto formatado
            content_text = content_element.text

            # Pegar HTML também
            content_html = content_element.get_attribute('innerHTML')

            return title, content_text, content_html

        except Exception as e:
            print(f"   ❌ Erro ao extrair conteúdo: {e}")
            return None, None, None

    def scrape_all(self):
        """Fazer scraping de todas as páginas"""
        os.makedirs(self.output_dir, exist_ok=True)

        # Login
        self.login()

        # Pegar todos os links
        all_links = self.extract_all_links()

        if not all_links:
            print("❌ Nenhum link encontrado!")
            return

        # Processar cada link
        for i, url in enumerate(all_links, 1):
            if url in self.visited_urls:
                continue

            self.visited_urls.add(url)
            print(f"\n📥 [{i}/{len(all_links)}] Processando: {url}")

            try:
                title, content_text, content_html = self.extract_note_content(url)

                if title and content_text:
                    print(f"   📄 Título: {title}")

                    # Salvar nota
                    filename = self.sanitize_filename(title)
                    if not filename.endswith('.md'):
                        filename += '.md'

                    filepath = os.path.join(self.output_dir, filename)

                    # Criar conteúdo Markdown
                    markdown_content = f"""---
title: {title}
source: {url}
date_imported: {time.strftime('%Y-%m-%d %H:%M:%S')}
---

# {title}

{content_text}

---

<details>
<summary>📎 HTML Original</summary>

{content_html}

</details>
"""

                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(markdown_content)

                    self.all_notes[url] = filename
                    print(f"   ✅ Salvo: {filename}")

                time.sleep(1)  # Rate limiting

            except Exception as e:
                print(f"   ❌ Erro: {e}")
                continue

        # Salvar índice
        index_file = os.path.join(self.output_dir, '_INDEX.json')
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(self.all_notes, f, indent=2, ensure_ascii=False)

        print(f"\n🎉 Scraping concluído! {len(self.all_notes)} notas extraídas")

    def close(self):
        """Fechar navegador"""
        self.driver.quit()

def main():
    BASE_URL = "https://mentelendaria.com"
    PASSWORD = "@88888888#"
    OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "notas")

    print("""
╔═══════════════════════════════════════════════════╗
║   🧠 SCRAPER LOCAL COM SELENIUM 🧠               ║
║   Mente Lendária - Segundo Cérebro do Alan       ║
╚═══════════════════════════════════════════════════╝
""")

    scraper = SeleniumScraper(BASE_URL, PASSWORD, OUTPUT_DIR)

    try:
        scraper.scrape_all()
    finally:
        scraper.close()

    print("\n✅ Processo concluído!")

if __name__ == "__main__":
    main()
