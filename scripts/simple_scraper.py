#!/usr/bin/env python3
"""
Simple Web Scraper - Mente Lendária
Extrai conteúdo usando requests + BeautifulSoup
"""

import requests
from bs4 import BeautifulSoup
import os
import time
import re
import json
from urllib.parse import urljoin, urlparse, unquote

class SimpleScaper:
    def __init__(self, base_url, password, output_dir):
        self.base_url = base_url
        self.password = password
        self.output_dir = output_dir
        self.session = requests.Session()
        self.visited_urls = set()
        self.all_notes = {}

        # Headers para parecer um navegador real
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
        })

    def sanitize_filename(self, title):
        """Criar nome de arquivo válido"""
        if not title:
            return 'Sem_titulo'
        # Remover caracteres inválidos
        filename = re.sub(r'[<>:"/\\|?*]', '', title)
        filename = filename.strip().replace(' ', '_').replace('/', '-')
        # Remover caracteres especiais mas manter acentos
        filename = re.sub(r'[^\w\s\-_áàâãéèêíïóôõöúçñÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑ]', '', filename)
        return filename[:100] if filename else 'Sem_titulo'

    def try_authentication(self, url):
        """Tentar diferentes métodos de autenticação"""
        print("🔐 Tentando autenticação...")

        # Método 1: Cookie simples
        self.session.cookies.set('password', self.password, domain=urlparse(url).netloc)

        # Método 2: Auth header
        self.session.headers['Authorization'] = f'Bearer {self.password}'

        # Método 3: Form POST
        try:
            response = self.session.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Procurar formulário de login
            form = soup.find('form')
            if form:
                action = form.get('action', '')
                method = form.get('method', 'post').lower()

                # Preparar dados do formulário
                form_data = {}
                for input_field in form.find_all('input'):
                    name = input_field.get('name')
                    value = input_field.get('value', '')
                    input_type = input_field.get('type', 'text')

                    if name:
                        if input_type == 'password':
                            form_data[name] = self.password
                        else:
                            form_data[name] = value

                # Submeter formulário
                if action:
                    post_url = urljoin(url, action)
                else:
                    post_url = url

                if method == 'post':
                    response = self.session.post(post_url, data=form_data)
                    print(f"   ✅ Formulário submetido: {response.status_code}")

        except Exception as e:
            print(f"   ⚠️ Erro na autenticação: {e}")

    def extract_links(self, soup, base_url):
        """Extrair todos os links internos"""
        links = set()

        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']

            # Converter para URL absoluta
            full_url = urljoin(base_url, href)

            # Apenas links do mesmo domínio
            if urlparse(full_url).netloc == urlparse(base_url).netloc:
                # Remover âncoras e query strings para simplificar
                clean_url = full_url.split('#')[0].split('?')[0]
                links.add(clean_url)

        return links

    def extract_content(self, url):
        """Extrair conteúdo de uma página"""
        try:
            response = self.session.get(url, timeout=15)

            if response.status_code != 200:
                print(f"   ⚠️ Status {response.status_code}")
                return None, None

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extrair título
            title = None
            if soup.find('title'):
                title = soup.find('title').get_text().strip()
            elif soup.find('h1'):
                title = soup.find('h1').get_text().strip()
            else:
                # Usar parte da URL como título
                path = urlparse(url).path
                title = unquote(path.split('/')[-1]).replace('-', ' ').replace('_', ' ').title()

            if not title:
                title = "Sem Título"

            # Procurar conteúdo principal
            content_element = None
            selectors = [
                'article',
                '.markdown-preview-view',
                '.content',
                'main',
                '.note-content',
                '.page-content',
                '[role="main"]',
                '#content'
            ]

            for selector in selectors:
                content_element = soup.select_one(selector)
                if content_element:
                    break

            if not content_element:
                # Fallback: pegar o body
                content_element = soup.body

            if not content_element:
                return title, "Conteúdo não encontrado"

            # Extrair texto formatado
            # Preservar estrutura de headings, listas, etc
            content_parts = []

            for element in content_element.descendants:
                if element.name == 'h1':
                    content_parts.append(f"\n# {element.get_text().strip()}\n")
                elif element.name == 'h2':
                    content_parts.append(f"\n## {element.get_text().strip()}\n")
                elif element.name == 'h3':
                    content_parts.append(f"\n### {element.get_text().strip()}\n")
                elif element.name == 'h4':
                    content_parts.append(f"\n#### {element.get_text().strip()}\n")
                elif element.name == 'p':
                    text = element.get_text().strip()
                    if text:
                        content_parts.append(f"\n{text}\n")
                elif element.name == 'li':
                    text = element.get_text().strip()
                    if text:
                        content_parts.append(f"- {text}\n")
                elif element.name == 'blockquote':
                    text = element.get_text().strip()
                    if text:
                        content_parts.append(f"\n> {text}\n")
                elif element.name == 'code':
                    text = element.get_text()
                    content_parts.append(f"`{text}`")
                elif element.name == 'pre':
                    text = element.get_text()
                    content_parts.append(f"\n```\n{text}\n```\n")

            # Se não conseguiu extrair nada estruturado, pegar texto simples
            if not content_parts:
                content_text = content_element.get_text(separator='\n', strip=True)
            else:
                content_text = ''.join(content_parts)

            return title, content_text

        except Exception as e:
            print(f"   ❌ Erro ao extrair conteúdo: {e}")
            return None, None

    def scrape_recursive(self, start_url, max_pages=200):
        """Fazer scraping recursivo"""
        to_visit = [start_url]
        pages_processed = 0

        print(f"🔍 Iniciando scraping de: {start_url}")

        # Tentar autenticação primeiro
        self.try_authentication(start_url)

        # Criar diretório de saída
        os.makedirs(self.output_dir, exist_ok=True)

        while to_visit and pages_processed < max_pages:
            url = to_visit.pop(0)

            if url in self.visited_urls:
                continue

            self.visited_urls.add(url)
            pages_processed += 1

            print(f"\n📥 [{pages_processed}] Processando: {url}")

            try:
                # Extrair conteúdo
                title, content = self.extract_content(url)

                if title and content:
                    print(f"   📄 Título: {title}")

                    # Salvar nota
                    filename = self.sanitize_filename(title)
                    if not filename.endswith('.md'):
                        filename += '.md'

                    filepath = os.path.join(self.output_dir, filename)

                    # Criar conteúdo Markdown com frontmatter
                    markdown_content = f"""---
title: {title}
source: {url}
date_imported: {time.strftime('%Y-%m-%d %H:%M:%S')}
---

# {title}

{content}
"""

                    # Salvar arquivo
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(markdown_content)

                    self.all_notes[url] = filename
                    print(f"   ✅ Salvo: {filename}")

                    # Buscar novos links nesta página
                    response = self.session.get(url)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    new_links = self.extract_links(soup, url)

                    for link in new_links:
                        if link not in self.visited_urls and link not in to_visit:
                            to_visit.append(link)

                    print(f"   🔗 Encontrados {len(new_links)} links novos")

                time.sleep(0.5)  # Rate limiting

            except Exception as e:
                print(f"   ❌ Erro: {e}")
                continue

        # Salvar índice
        index_file = os.path.join(self.output_dir, '_INDEX.json')
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(self.all_notes, f, indent=2, ensure_ascii=False)

        print(f"\n🎉 Scraping concluído! {len(self.all_notes)} notas extraídas")
        print(f"📁 Salvas em: {self.output_dir}")

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

    scraper = SimpleScaper(BASE_URL, PASSWORD, OUTPUT_DIR)
    scraper.scrape_recursive(BASE_URL, max_pages=500)

    print("\n✅ Processo concluído com sucesso!")
    print(f"📊 Total de notas: {len(scraper.all_notes)}")

if __name__ == "__main__":
    main()
