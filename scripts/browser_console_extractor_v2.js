/**
 * MENTE LENDARIA - EXTRATOR v2 (CORRIGIDO)
 * ==========================================
 *
 * INSTRUCOES:
 * 1. Esteja logado em mentelendaria.com
 * 2. F12 > Console
 * 3. Cole este script e pressione Enter
 */

(async function extractV2() {
    console.log('================================================================');
    console.log('  MENTE LENDARIA - EXTRATOR DE NOTAS v2');
    console.log('================================================================');

    // PASSO 1: Descobrir Site ID e Password Hash corretos
    console.log('[1/4] Descobrindo configuracoes do site...');

    // Buscar em todos os storages
    let siteId = null;
    let passwordHash = null;

    // Procurar o site ID e password em localStorage
    for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        const val = localStorage.getItem(key);
        console.log(`  localStorage: ${key} = ${val ? val.substring(0, 60) : 'null'}...`);

        if (key.includes('publish-site-password')) {
            passwordHash = val;
            // Extrair site ID do nome da chave
            const match = key.match(/publish-site-password-(.+)/);
            if (match) siteId = match[1];
        }
        if (key.includes('site-id') || key.includes('siteId')) {
            siteId = val;
        }
    }

    // Procurar em sessionStorage
    for (let i = 0; i < sessionStorage.length; i++) {
        const key = sessionStorage.key(i);
        const val = sessionStorage.getItem(key);
        console.log(`  sessionStorage: ${key} = ${val ? val.substring(0, 60) : 'null'}...`);

        if (key.includes('publish-site-password')) {
            passwordHash = val;
            const match = key.match(/publish-site-password-(.+)/);
            if (match) siteId = match[1];
        }
    }

    // Procurar no HTML da pagina
    const scripts = document.querySelectorAll('script');
    scripts.forEach(s => {
        const text = s.textContent || s.innerText || '';
        // Procurar site ID no JavaScript
        const idMatch = text.match(/siteId['":\s]+['"]([a-f0-9]{32})['"]/);
        if (idMatch) {
            siteId = idMatch[1];
            console.log(`  Encontrado siteId no script: ${siteId}`);
        }
        const idMatch2 = text.match(/["']id["']\s*:\s*["']([a-f0-9]{32})["']/);
        if (idMatch2) {
            siteId = idMatch2[1];
            console.log(`  Encontrado id no script: ${siteId}`);
        }
    });

    // Procurar no meta tags
    document.querySelectorAll('meta').forEach(meta => {
        const name = meta.getAttribute('name') || meta.getAttribute('property') || '';
        const content = meta.getAttribute('content') || '';
        if (name.includes('site') || content.match(/^[a-f0-9]{32}$/)) {
            console.log(`  Meta: ${name} = ${content}`);
        }
    });

    // Procurar no window/app object
    if (window.publish) console.log('  window.publish encontrado:', Object.keys(window.publish));
    if (window.app) console.log('  window.app encontrado:', Object.keys(window.app));
    if (window.siteId) { siteId = window.siteId; console.log(`  window.siteId: ${siteId}`); }

    console.log(`\n  Site ID encontrado: ${siteId || 'NAO ENCONTRADO'}`);
    console.log(`  Password Hash encontrado: ${passwordHash || 'NAO ENCONTRADO'}`);

    // Se nao encontrou o hash, gerar a partir da senha
    if (!passwordHash) {
        console.log('  Gerando hash da senha @88888888#...');
        const encoder = new TextEncoder();
        const data = encoder.encode('@88888888#');
        const hashBuffer = await crypto.subtle.digest('SHA-256', data);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        passwordHash = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
        console.log(`  Hash gerado: ${passwordHash}`);
    }

    // PASSO 2: Testar diferentes Site IDs
    console.log('\n[2/4] Testando conexao com a API...');

    const possibleIds = [siteId, 'f431548d64f3cdad0278eb0b35aa11fe'].filter(Boolean);

    // Tambem tentar extrair de cookies
    const cookies = document.cookie.split(';').map(c => c.trim());
    cookies.forEach(c => {
        console.log(`  Cookie: ${c.substring(0, 80)}`);
    });

    let cacheData = null;
    let workingSiteId = null;

    for (const testId of possibleIds) {
        console.log(`\n  Testando Site ID: ${testId}`);

        // Tentar com hash
        try {
            const resp = await fetch(`https://publish-01.obsidian.md/cache/${testId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: testId, password: passwordHash })
            });
            console.log(`    POST /cache com hash: ${resp.status}`);
            if (resp.ok) {
                cacheData = await resp.json();
                workingSiteId = testId;
                break;
            }
        } catch(e) { console.log(`    Erro: ${e.message}`); }

        // Tentar com senha em texto puro
        try {
            const resp = await fetch(`https://publish-01.obsidian.md/cache/${testId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: testId, password: '@88888888#' })
            });
            console.log(`    POST /cache com senha pura: ${resp.status}`);
            if (resp.ok) {
                cacheData = await resp.json();
                workingSiteId = testId;
                break;
            }
        } catch(e) {}

        // Tentar sem senha
        try {
            const resp = await fetch(`https://publish-01.obsidian.md/cache/${testId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: testId })
            });
            console.log(`    POST /cache sem senha: ${resp.status}`);
            if (resp.ok) {
                cacheData = await resp.json();
                workingSiteId = testId;
                break;
            }
        } catch(e) {}
    }

    // PASSO 3: Se API nao funcionou, extrair via DOM (metodo garantido)
    if (!cacheData) {
        console.log('\n[!] API nao disponivel. Usando extracao via DOM (metodo garantido)...');
        return await extractViaDOMOnly();
    }

    // Se chegou aqui, a API funcionou
    console.log(`\n[OK] API funcionando com Site ID: ${workingSiteId}`);
    console.log(`  Chaves do cache: ${Object.keys(cacheData).join(', ')}`);

    const files = {};
    const fileSource = cacheData.files || cacheData.cache || cacheData;
    for (const [path, info] of Object.entries(fileSource)) {
        if (path.endsWith('.md')) {
            files[path] = typeof info === 'object' ? (info.hash || info.h || null) : info;
        }
    }

    console.log(`  Arquivos .md: ${Object.keys(files).length}`);

    // Baixar via API...
    const notes = {};
    let dl = 0, fail = 0;
    const total = Object.keys(files).length;

    for (const [fp, fh] of Object.entries(files)) {
        try {
            const payload = { id: workingSiteId, path: fp, password: passwordHash };
            if (fh) payload.hash = fh;
            const r = await fetch(`https://publish-01.obsidian.md/access/${workingSiteId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (r.ok) { notes[fp] = await r.text(); dl++; }
            else { fail++; }
            if (dl % 10 === 0) console.log(`  [${dl}/${total}] ${fp}`);
            await new Promise(r => setTimeout(r, 200));
        } catch(e) { fail++; }
    }

    downloadJSON(notes, dl, fail, 'api');
})();

// =====================================================
// METODO DOM: Extrai conteudo navegando pelas paginas
// =====================================================
async function extractViaDOMOnly() {
    console.log('\n[3/4] Coletando todos os links do site...');

    // Expandir TODAS as pastas colapsadas (multiplas vezes)
    for (let round = 0; round < 5; round++) {
        const collapsed = document.querySelectorAll('.tree-item.is-collapsed');
        if (collapsed.length === 0) break;
        console.log(`  Round ${round+1}: Expandindo ${collapsed.length} pastas...`);
        collapsed.forEach(item => {
            const clickTarget = item.querySelector('.tree-item-icon') ||
                               item.querySelector('.tree-item-self') ||
                               item.querySelector('.collapse-icon');
            if (clickTarget) clickTarget.click();
        });
        await new Promise(r => setTimeout(r, 1500));
    }

    // Coletar TODOS os links de notas
    const paths = new Set();

    // data-path e mais confiavel
    document.querySelectorAll('[data-path]').forEach(el => {
        const p = el.getAttribute('data-path');
        if (p) paths.add(p);
    });

    // tree-item-self com data-path
    document.querySelectorAll('.tree-item-self').forEach(el => {
        const p = el.getAttribute('data-path');
        if (p) paths.add(p);
    });

    // Links internos
    document.querySelectorAll('.internal-link, a.internal-link').forEach(el => {
        const href = el.getAttribute('href');
        if (href && !href.startsWith('http') && !href.startsWith('#')) {
            let p = decodeURIComponent(href.replace(/^\//, ''));
            if (!p.endsWith('.md')) p += '.md';
            paths.add(p);
        }
    });

    // Todos os hrefs internos
    document.querySelectorAll('a[href]').forEach(el => {
        const href = el.getAttribute('href');
        if (href && !href.startsWith('http') && !href.startsWith('#') && !href.startsWith('javascript')) {
            let p = decodeURIComponent(href.replace(/^\//, ''));
            if (!p.endsWith('.md')) p += '.md';
            if (p.length > 1 && p !== '.md') paths.add(p);
        }
    });

    const allPaths = Array.from(paths);
    console.log(`  Total de paths unicos: ${allPaths.length}`);

    // Agora, para cada nota, NAVEGAR ate ela e extrair o conteudo renderizado
    console.log('\n[4/4] Extraindo conteudo de cada nota...');
    console.log('  (Isso vai navegar pagina por pagina - aguarde...)');

    const notes = {};
    let downloaded = 0;
    let failed = 0;
    const total = allPaths.length;

    for (const filePath of allPaths) {
        try {
            // Construir URL
            let urlPath = filePath.replace(/\.md$/, '');
            const url = `${window.location.origin}/${encodeURI(urlPath)}`;

            // Navegar via fetch (pega o HTML renderizado)
            const response = await fetch(url, {
                credentials: 'include',
                headers: {
                    'Accept': 'text/html,application/xhtml+xml',
                }
            });

            if (response.ok) {
                const html = await response.text();

                // Extrair conteudo do HTML
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');

                // Pegar o conteudo principal
                const contentEl = doc.querySelector('.markdown-preview-view') ||
                                 doc.querySelector('.publish-article-view') ||
                                 doc.querySelector('article') ||
                                 doc.querySelector('.content') ||
                                 doc.querySelector('main');

                if (contentEl) {
                    // Converter HTML para texto/markdown basico
                    let content = htmlToMarkdown(contentEl);

                    if (content && content.trim().length > 10) {
                        notes[filePath] = content;
                        downloaded++;
                    } else {
                        failed++;
                    }
                } else {
                    // Tentar pegar o body inteiro
                    const body = doc.querySelector('body');
                    if (body) {
                        let content = htmlToMarkdown(body);
                        if (content && content.trim().length > 50) {
                            notes[filePath] = content;
                            downloaded++;
                        } else {
                            failed++;
                        }
                    } else {
                        failed++;
                    }
                }
            } else {
                failed++;
            }

            if (downloaded % 20 === 0 && downloaded > 0) {
                console.log(`  [${downloaded}/${total}] baixadas, ${failed} falhas - atual: ${filePath}`);
            }

            // Rate limiting gentil
            await new Promise(r => setTimeout(r, 100));

        } catch(e) {
            failed++;
        }
    }

    console.log(`\n  Download completo: ${downloaded} OK, ${failed} falhas`);
    downloadJSON(notes, downloaded, failed, 'dom');
}

// Converter HTML para Markdown basico
function htmlToMarkdown(element) {
    let md = '';

    function processNode(node) {
        if (node.nodeType === 3) { // Text node
            return node.textContent;
        }

        if (node.nodeType !== 1) return ''; // Not element

        const tag = node.tagName.toLowerCase();
        const children = Array.from(node.childNodes).map(processNode).join('');

        switch(tag) {
            case 'h1': return `\n# ${children.trim()}\n\n`;
            case 'h2': return `\n## ${children.trim()}\n\n`;
            case 'h3': return `\n### ${children.trim()}\n\n`;
            case 'h4': return `\n#### ${children.trim()}\n\n`;
            case 'h5': return `\n##### ${children.trim()}\n\n`;
            case 'h6': return `\n###### ${children.trim()}\n\n`;
            case 'p': return `\n${children.trim()}\n\n`;
            case 'br': return '\n';
            case 'strong': case 'b': return `**${children}**`;
            case 'em': case 'i': return `*${children}*`;
            case 'code': return `\`${children}\``;
            case 'pre': return `\n\`\`\`\n${children}\n\`\`\`\n\n`;
            case 'blockquote': return `\n> ${children.trim().replace(/\n/g, '\n> ')}\n\n`;
            case 'li': return `- ${children.trim()}\n`;
            case 'ul': case 'ol': return `\n${children}\n`;
            case 'a': {
                const href = node.getAttribute('href') || '';
                return `[${children}](${href})`;
            }
            case 'img': {
                const src = node.getAttribute('src') || '';
                const alt = node.getAttribute('alt') || '';
                return `![${alt}](${src})`;
            }
            case 'hr': return '\n---\n\n';
            case 'table': return `\n${children}\n`;
            case 'tr': return `|${children}|\n`;
            case 'th': case 'td': return ` ${children.trim()} |`;
            case 'div': case 'section': case 'article': case 'main':
                return children;
            case 'script': case 'style': case 'nav': case 'aside':
                return '';
            default: return children;
        }
    }

    md = processNode(element);
    // Limpar espacos extras
    md = md.replace(/\n{3,}/g, '\n\n').trim();
    return md;
}

// Baixar resultado como JSON
function downloadJSON(notes, downloaded, failed, method) {
    console.log('\n  Preparando arquivo para download...');

    const exportData = {
        metadata: {
            source: 'mentelendaria.com',
            export_date: new Date().toISOString(),
            total_notes: downloaded,
            failed: failed,
            method: method,
            vault_name: 'Mente Lendaria - Segundo Cerebro do Alan'
        },
        notes: notes
    };

    const jsonStr = JSON.stringify(exportData, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
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
    console.log(`  ${downloaded} notas extraidas (${failed} falhas)`);
    console.log(`  Metodo usado: ${method}`);
    console.log(`  Tamanho: ${(jsonStr.length / 1024 / 1024).toFixed(2)} MB`);
    console.log('  Arquivo JSON baixado automaticamente!');
    console.log('');
    console.log('  Proximo passo no terminal:');
    console.log('  python3 scripts/import_from_json.py <arquivo.json>');
    console.log('================================================================');
}
