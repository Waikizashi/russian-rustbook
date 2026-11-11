/* Rebuild mdBook's existing index with Unicode-aware token trimming.
 * Uses only Node's standard library and mdBook's bundled elasticlunr, whose
 * license is retained. Nothing is fetched or indexed in the reader's browser.
 */
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '..');
const patch = fs.readFileSync(path.join(root, 'assets/search-ru.js'), 'utf8');
const checks = [];
for (const folder of ['book', 'book/extras/bits-bytes']) {
    const dir = path.join(root, folder);
    const files = fs.readdirSync(dir);
    const engineFile = files.find(f => /^elasticlunr-.*\.js$/.test(f));
    const indexFile = files.find(f => /^searchindex-.*\.js$/.test(f));
    if (!engineFile || !indexFile) throw Error(`Missing mdBook search assets: ${folder}`);
    const engineText = fs.readFileSync(path.join(dir, engineFile), 'utf8');
    const engineScope = {module: {exports: {}}, exports: {}, console};
    vm.createContext(engineScope);
    vm.runInContext(engineText + '\n' + patch, engineScope);
    const engine = engineScope.module.exports;
    const scope = {window: {search: {}}};
    vm.createContext(scope);
    vm.runInContext(fs.readFileSync(path.join(dir, indexFile), 'utf8'), scope);
    const cfg = scope.window.search;
    const index = engine(function () {
        this.setRef(cfg.index.ref);
        for (const field of cfg.index.fields) this.addField(field);
        this.pipeline.reset();
        this.pipeline.add(engine.ruTrimmer, engine.stopWordFilter, engine.stemmer);
    });
    for (const doc of Object.values(cfg.index.documentStore.docs)) index.addDoc(doc);
    cfg.index = index.toJSON();
    const reloaded = engine.Index.load(cfg.index);
    for (const query of (folder === 'book' ? ['владение', 'заимствование', 'Rust'] : ['байты', 'парсер', 'Rust'])) {
        const results = reloaded.search(query, cfg.search_options);
        if (!results.length) throw Error(`Search regression: ${folder}: ${query}`);
        checks.push({book: folder, query, results: results.length});
    }
    const serialize = value => JSON.stringify(value).replace(/</g, '\\u003c').replace(/\u2028/g, '\\u2028').replace(/\u2029/g, '\\u2029');
    const indexText = 'window.search = Object.assign(window.search, ' + serialize(cfg) + ');\n';
    const vendorText = engineText.includes("registerFunction(engine.ruTrimmer") ? engineText : engineText + '\n' + patch;
    const hashed = (prefix, text) => prefix + crypto.createHash('sha256').update(text).digest('hex').slice(0, 8) + '.js';
    const newEngine = hashed('elasticlunr-ru-', vendorText);
    const newIndex = hashed('searchindex-', indexText);
    fs.writeFileSync(path.join(dir, newEngine), vendorText);
    fs.writeFileSync(path.join(dir, newIndex), indexText);
    for (const file of files.filter(f => f.endsWith('.html'))) {
        let html = fs.readFileSync(path.join(dir, file), 'utf8');
        html = html.replaceAll(engineFile, newEngine).replaceAll(indexFile, newIndex);
        fs.writeFileSync(path.join(dir, file), html);
    }
    if (engineFile !== newEngine) fs.unlinkSync(path.join(dir, engineFile));
    if (indexFile !== newIndex) fs.unlinkSync(path.join(dir, indexFile));
}
fs.mkdirSync(path.join(root, 'dist'), {recursive: true});
fs.writeFileSync(path.join(root, 'dist/search-verification.json'), JSON.stringify(checks, null, 2) + '\n');
console.log('Unicode search:', checks);
