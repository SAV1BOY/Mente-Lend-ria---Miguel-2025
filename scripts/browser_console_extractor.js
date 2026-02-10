/**
 * ================================================================
 * BROWSER CONSOLE EXTRACTOR - Mente Lendaria
 * ================================================================
 *
 * COMO USAR (METODO MAIS FACIL):
 *
 * 1. Abra https://mentelendaria.com no seu navegador
 * 2. Faca login com a senha: @88888888#
 * 3. Aguarde o site carregar completamente
 * 4. Pressione F12 para abrir as Ferramentas do Desenvolvedor
 * 5. Clique na aba "Console"
 * 6. Cole TODO o codigo abaixo e pressione Enter
 * 7. Aguarde a extracao terminar
 * 8. Um arquivo .json sera baixado automaticamente com todas as notas
 *
 * Depois, use o script Python 'import_from_json.py' para converter
 * o JSON em arquivos Markdown organizados.
 *
 * ================================================================
 */

(async function extractAllNotes() {
    console.log('================================================================');
    console.log('  MENTE LENDARIA - EXTRATOR DE NOTAS');
    console.log('  Extraindo todas as notas do Segundo Cerebro...');
    console.log('================================================================');

    // Configuracao
    const SITE_ID = 'f431548d64f3cdad0278eb0b35aa11fe';
    const API_BASE = 'https://publish-01.obsidian.md';

    // Obter password hash do cookie ou storage
    let passwordHash = '';

    // Tentar obter do localStorage
    const storedPassword = localStorage.getItem('publish-site-password-' + SITE_ID);
    if (storedPassword) {
        passwordHash = storedPassword;
        console.log('[OK] Password hash encontrado no localStorage');
    }

    // Tentar obter do sessionStorage
    if (!passwordHash) {
        const sessionPassword = sessionStorage.getItem('publish-site-password-' + SITE_ID);
        if (sessionPassword) {
            passwordHash = sessionPassword;
            console.log('[OK] Password hash encontrado no sessionStorage');
        }
    }

    // Fallback: gerar hash da senha conhecida
    if (!passwordHash) {
        console.log('[INFO] Gerando hash da senha...');
        const encoder = new TextEncoder();
        const data = encoder.encode('@88888888#');
        const hashBuffer = await crypto.subtle.digest('SHA-256', data);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        passwordHash = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
        console.log('[OK] Hash gerado');
    }

    console.log('[1/3] Obtendo lista de arquivos do vault...');

    // Passo 1: Obter cache com lista de todos os arquivos
    let cacheData = null;
    try {
        const cacheResponse = await fetch(`${API_BASE}/cache/${SITE_ID}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id: SITE_ID,
                password: passwordHash
            })
        });

        if (cacheResponse.ok) {
            cacheData = await cacheResponse.json();
            console.log('[OK] Cache obtido com sucesso!');
        } else {
            console.log('[ERRO] Status: ' + cacheResponse.status);

            // Tentar sem password
            const retry = await fetch(`${API_BASE}/cache/${SITE_ID}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: SITE_ID })
            });

            if (retry.ok) {
                cacheData = await retry.json();
                console.log('[OK] Cache obtido sem senha');
            }
        }
    } catch (e) {
        console.error('[ERRO] Falha ao obter cache:', e);
    }

    if (!cacheData) {
        console.error('[ERRO] Nao foi possivel obter a lista de arquivos.');
        console.log('Tentando metodo alternativo via DOM...');

        // Fallback: extrair links da sidebar
        return extractFromDOM();
    }

    // Extrair lista de arquivos .md do cache
    const files = {};

    // O cache pode ter diferentes formatos
    const fileSource = cacheData.files || cacheData.cache || cacheData;

    if (typeof fileSource === 'object') {
        for (const [path, info] of Object.entries(fileSource)) {
            if (path.endsWith('.md')) {
                files[path] = typeof info === 'object' ? (info.hash || info.h || null) : info;
            }
        }
    }

    const totalFiles = Object.keys(files).length;
    console.log(`[OK] ${totalFiles} arquivos encontrados no vault!`);

    if (totalFiles === 0) {
        console.log('[AVISO] Nenhum arquivo .md encontrado no cache.');
        console.log('Estrutura do cache:', JSON.stringify(Object.keys(cacheData)).substring(0, 200));
        return extractFromDOM();
    }

    // Passo 2: Baixar conteudo de cada arquivo
    console.log(`[2/3] Baixando ${totalFiles} notas...`);

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

            if (fileHash) {
                payload.hash = fileHash;
            }

            const response = await fetch(`${API_BASE}/access/${SITE_ID}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                const content = await response.text();
                notes[filePath] = content;
                downloaded++;

                if (downloaded % 10 === 0 || downloaded === totalFiles) {
                    console.log(`  [${downloaded}/${totalFiles}] ${filePath}`);
                }
            } else {
                console.warn(`  [FALHOU] ${filePath}: Status ${response.status}`);
                failed++;
            }

            // Rate limiting
            await new Promise(r => setTimeout(r, 200));

        } catch (e) {
            console.warn(`  [ERRO] ${filePath}: ${e.message}`);
            failed++;
        }
    }

    console.log(`[OK] Download completo: ${downloaded} OK, ${failed} falhas`);

    // Passo 3: Salvar como JSON
    console.log('[3/3] Preparando arquivo para download...');

    const exportData = {
        metadata: {
            source: 'mentelendaria.com',
            site_id: SITE_ID,
            export_date: new Date().toISOString(),
            total_notes: downloaded,
            failed: failed,
            vault_name: 'Mente Lendaria - Segundo Cerebro do Alan'
        },
        files: files,
        notes: notes
    };

    // Criar e baixar arquivo
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `mente-lendaria-vault-${new Date().toISOString().slice(0, 10)}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    console.log('================================================================');
    console.log('  EXTRACAO COMPLETA!');
    console.log(`  ${downloaded} notas extraidas`);
    console.log('  Arquivo JSON baixado automaticamente');
    console.log('');
    console.log('  Proximo passo:');
    console.log('  python3 scripts/import_from_json.py <arquivo.json>');
    console.log('================================================================');

    return exportData;
})();

/**
 * Metodo alternativo: extrair notas navegando pelo DOM
 * Usado quando a API do Obsidian Publish nao retorna o cache
 */
async function extractFromDOM() {
    console.log('[ALTERNATIVO] Extraindo notas via navegacao do DOM...');

    const SITE_ID = 'f431548d64f3cdad0278eb0b35aa11fe';
    const API_BASE = 'https://publish-01.obsidian.md';

    // Encontrar todos os links na sidebar
    const navLinks = document.querySelectorAll('.tree-item-self, .nav-file-title, a[data-path]');
    const allLinks = document.querySelectorAll('a[href]');

    console.log(`  Links na navegacao: ${navLinks.length}`);
    console.log(`  Links totais: ${allLinks.length}`);

    // Coletar todos os paths unicos
    const paths = new Set();

    // De data-path attributes
    navLinks.forEach(el => {
        const path = el.getAttribute('data-path') || el.dataset.path;
        if (path && path.endsWith('.md')) {
            paths.add(path);
        }
    });

    // De hrefs
    allLinks.forEach(el => {
        const href = el.getAttribute('href');
        if (href && !href.startsWith('http') && !href.startsWith('#')) {
            let path = href.replace(/^\//, '');
            if (!path.endsWith('.md')) path += '.md';
            paths.add(path);
        }
    });

    // Tambem expandir todas as pastas colapsadas
    console.log('  Expandindo pastas colapsadas...');
    const collapsedItems = document.querySelectorAll('.tree-item.is-collapsed .tree-item-icon, .collapse-icon.is-collapsed');
    collapsedItems.forEach(item => {
        item.click();
    });

    // Aguardar DOM atualizar
    await new Promise(r => setTimeout(r, 2000));

    // Recoletar apos expandir
    document.querySelectorAll('.tree-item-self, .nav-file-title, a[data-path]').forEach(el => {
        const path = el.getAttribute('data-path') || el.dataset.path;
        if (path && path.endsWith('.md')) {
            paths.add(path);
        }
    });

    console.log(`  Total de paths encontrados: ${paths.size}`);

    if (paths.size === 0) {
        console.log('[AVISO] Nenhum path encontrado no DOM.');
        console.log('  Tente expandir manualmente todas as pastas na sidebar');
        console.log('  e execute o script novamente.');
        return null;
    }

    // Obter password hash
    let passwordHash = '';
    const storedPassword = localStorage.getItem('publish-site-password-' + SITE_ID) ||
                          sessionStorage.getItem('publish-site-password-' + SITE_ID);

    if (storedPassword) {
        passwordHash = storedPassword;
    } else {
        const encoder = new TextEncoder();
        const data = encoder.encode('@88888888#');
        const hashBuffer = await crypto.subtle.digest('SHA-256', data);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        passwordHash = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    }

    // Baixar cada nota
    const notes = {};
    let downloaded = 0;
    let failed = 0;
    const total = paths.size;

    for (const filePath of paths) {
        try {
            const response = await fetch(`${API_BASE}/access/${SITE_ID}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    id: SITE_ID,
                    path: filePath,
                    password: passwordHash
                })
            });

            if (response.ok) {
                notes[filePath] = await response.text();
                downloaded++;
                if (downloaded % 5 === 0) {
                    console.log(`  [${downloaded}/${total}] ${filePath}`);
                }
            } else {
                failed++;
            }

            await new Promise(r => setTimeout(r, 300));
        } catch (e) {
            failed++;
        }
    }

    console.log(`[OK] ${downloaded} notas baixadas, ${failed} falhas`);

    // Exportar
    const exportData = {
        metadata: {
            source: 'mentelendaria.com',
            site_id: SITE_ID,
            export_date: new Date().toISOString(),
            total_notes: downloaded,
            method: 'dom_extraction'
        },
        notes: notes
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `mente-lendaria-vault-${new Date().toISOString().slice(0, 10)}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    console.log('  Arquivo JSON baixado!');
    return exportData;
}
