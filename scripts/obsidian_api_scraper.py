#!/usr/bin/env python3
"""
Obsidian Publish API Scraper - Mente Lendária
Usa a API do Obsidian Publish para extrair todas as notas
"""

import requests
import json
import os
import time
import re
from urllib.parse import unquote

class ObsidianPublishAPI:
    def __init__(self, site_uid, host, output_dir, password=None):
        self.site_uid = site_uid
        self.host = host
        self.base_url = f"https://{host}"
        self.output_dir = output_dir
        self.password = password
        self.session = requests.Session()

        # Headers para autenticação
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        })

        if password:
            self.session.cookies.set('password', password, domain=host)

    def get_cache(self):
        """Obter cache do site com lista de todas as notas"""
        cache_url = f"{self.base_url}/cache/{self.site_uid}"

        print(f"🔍 Buscando cache: {cache_url}")

        try:
            response = self.session.get(cache_url, timeout=15)

            if response.status_code == 200:
                try:
                    cache_data = response.json()
                    print(f"✅ Cache obtido com sucesso!")
                    return cache_data
                except json.JSONDecodeError:
                    print("⚠️ Resposta não é JSON, tentando texto")
                    return response.text
            else:
                print(f"❌ Erro ao obter cache: {response.status_code}")
                return None

        except Exception as e:
            print(f"❌ Erro na requisição: {e}")
            return None

    def get_page_content(self, file_path):
        """Obter conteúdo de uma página específica"""
        # URL da API de acesso
        access_url = f"{self.base_url}/access/{self.site_uid}/{file_path}"

        try:
            response = self.session.get(access_url, timeout=15)

            if response.status_code == 200:
                return response.text
            else:
                print(f"   ⚠️ Status {response.status_code} para {file_path}")
                return None

        except Exception as e:
            print(f"   ❌ Erro ao obter {file_path}: {e}")
            return None

    def sanitize_filename(self, path):
        """Criar nome de arquivo válido mantendo estrutura de pastas"""
        # Remover .md se já tiver
        if path.endswith('.md'):
            path = path[:-3]

        # URL decode
        path = unquote(path)

        # Substituir caracteres inválidos
        path = path.replace('?', '')
        path = path.replace(':', '-')
        path = path.replace('|', '-')

        return path

    def extract_all_notes(self, cache_data):
        """Extrair todas as notas baseado no cache"""

        # Usar sempre a lista extraída do HTML
        print("📋 Usando lista de arquivos extraída da navegação do site...")
        files_to_download = self.get_files_from_html_structure()

        print(f"\n📚 Total de páginas para processar: {len(files_to_download)}")

        # Criar diretório de saída
        os.makedirs(self.output_dir, exist_ok=True)

        downloaded = 0
        failed = []

        for i, file_path in enumerate(files_to_download, 1):
            # Garantir que tem .md
            if not file_path.endswith('.md'):
                file_path_md = file_path + '.md'
            else:
                file_path_md = file_path

            print(f"\n📥 [{i}/{len(files_to_download)}] {file_path}")

            # Obter conteúdo
            content = self.get_page_content(file_path_md)

            if content:
                # Criar caminho do arquivo local
                clean_path = self.sanitize_filename(file_path)
                local_path = os.path.join(self.output_dir, clean_path + '.md')

                # Criar diretórios se necessário
                os.makedirs(os.path.dirname(local_path), exist_ok=True)

                # Adicionar frontmatter
                frontmatter = f"""---
title: {clean_path.split('/')[-1].replace('_', ' ')}
source: https://mentelendaria.com/{file_path}
path: {file_path}
date_imported: {time.strftime('%Y-%m-%d %H:%M:%S')}
---

"""

                # Salvar arquivo
                with open(local_path, 'w', encoding='utf-8') as f:
                    f.write(frontmatter + content)

                downloaded += 1
                print(f"   ✅ Salvo: {local_path}")
            else:
                failed.append(file_path)
                print(f"   ❌ Falhou")

            # Rate limiting
            time.sleep(0.3)

        print(f"\n🎉 Scraping concluído!")
        print(f"✅ Baixadas: {downloaded}")
        print(f"❌ Falharam: {len(failed)}")

        if failed:
            print("\n⚠️ Arquivos que falharam:")
            for f in failed:
                print(f"  - {f}")

    def get_files_from_html_structure(self):
        """Lista de arquivos extraída da estrutura HTML"""
        return [
            "bem-vindo(a).md",
            # Anotações
            "Anotações/Guia dos Apodícticos.md",
            # Sobre Mim
            "Sobre Mim/📇 Index.md",
            "Sobre Mim/Agora.md",
            "Sobre Mim/anos mais desesperadores da minha vida.md",
            "Sobre Mim/Como eu me tornei um otimista.md",
            "Sobre Mim/Entre Ausências e Aparições O Que Aconteceu Comigo?.md",
            "Sobre Mim/Essência.md",
            "Sobre Mim/Eu do futuro.md",
            "Sobre Mim/Eu x  Eu público.md",
            "Sobre Mim/Frases Alan.md",
            "Sobre Mim/Jornada e História.md",
            "Sobre Mim/Memórias Alan & Steven.md",
            "Sobre Mim/Minha Missão.md",
            "Sobre Mim/Projetos Atuais.md",
            "Sobre Mim/Quem é Alan Nicolas.md",
            "Sobre Mim/Visão de 2017 para 2022.md",
            # Conhecimento
            "Conhecimento/📇 Index.md",
            "Conhecimento/README.md",
            # YouTube
            "Conhecimento/YouTube/Algoritmo do YouTube.md",
            "Conhecimento/YouTube/Código YouTube.md",
            "Conhecimento/YouTube/Dominando YouTube.md",
        ]

def main():
    # Configurações extraídas do HTML
    SITE_UID = "f431548d64f3cdad0278eb0b35aa11fe"
    HOST = "publish-01.obsidian.md"
    PASSWORD = "@88888888#"  # Se necessário
    OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "notas")

    print("""
╔═══════════════════════════════════════════════════╗
║   🧠 OBSIDIAN PUBLISH API SCRAPER 🧠             ║
║   Mente Lendária - Segundo Cérebro do Alan       ║
╚═══════════════════════════════════════════════════╝
""")

    scraper = ObsidianPublishAPI(SITE_UID, HOST, OUTPUT_DIR, PASSWORD)

    # Obter cache
    cache_data = scraper.get_cache()

    # Extrair todas as notas
    scraper.extract_all_notes(cache_data)

    print("\n✅ Processo concluído!")

if __name__ == "__main__":
    main()
