/* Project-wide published revision and scoped completion indicator.
   Safe to reuse on static GitHub Pages sites; no credentials or external services. */
(function () {
  'use strict';
  const tag = document.currentScript;
  if (!tag || !tag.src || document.getElementById('project-progress-status')) return;
  const root = new URL('./', tag.src);
  const getText = async name => {
    if (!/^[a-zA-Z0-9_./-]+$/.test(name) || name.includes('..')) throw new Error('Invalid progress source');
    const response = await fetch(new URL(name, root), {cache: 'no-store'});
    if (!response.ok) throw new Error('Progress source unavailable');
    return response.text();
  };
  const field = (value, path) => path.split('.').reduce(
    (obj, key) => obj != null ? obj[key] : undefined, value);
  async function revisionFor(config) {
    const src = config.revisionSource;
    if (!src) return String(config.revision || 'Not recorded');
    try {
      const contents = await getText(src.file);
      let value;
      if (src.type === 'json') value = field(JSON.parse(contents), src.path);
      if (src.type === 'text') {
        const result = contents.match(new RegExp(src.pattern, src.flags || 'm'));
        value = result && result[1];
      }
      if (value == null || value === '') throw new Error('Missing revision');
      return String(src.prefix || '') + String(value) + String(src.suffix || '');
    } catch (_) {
      return String(config.revision || 'Not recorded') + ' (last recorded)';
    }
  }
  async function countFor(config) {
    const p = config.progress || {};
    let done = p.completed;
    let total = p.total;
    if (p.source) {
      try {
        const source = JSON.parse(await getText(p.source.file));
        const data = field(source, p.source.path);
        if (p.source.kind === 'array-length') done = data.length;
        if (p.source.kind === 'sum-fields') done = p.source.fields.reduce(
          (n, k) => n + Number(data[k]), 0);
        if (p.source.kind === 'value') done = Number(data);
        if (p.source.totalPath) total = Number(field(source, p.source.totalPath));
        else if (p.source.totalField) total = Number(data[p.source.totalField]);
      } catch (_) {
        // Retain the last independently verified counts in the small manifest.
      }
    }
    const valid = Number.isInteger(done) && Number.isInteger(total) &&
      total > 0 && done >= 0 && done <= total;
    return {done, total, percent: valid ? Math.round(100 * done / total) : null};
  }
  function make(tagName, className, value) {
    const e = document.createElement(tagName);
    if (className) e.className = className;
    if (value != null) e.textContent = String(value);
    return e;
  }
  async function mount() {
    if (document.getElementById('project-progress-status')) return;
    let config;
    try { config = JSON.parse(await getText('site-progress.json')); }
    catch (_) { return; }
    if (!config || config.schemaVersion !== 1) return;
    const [revision, count] = await Promise.all([
      revisionFor(config), countFor(config)
    ]);
    const style = document.createElement('style');
    style.textContent = `
#project-progress-status{position:fixed;bottom:12px;right:12px;z-index:2147483000;
  max-width:min(350px,calc(100vw - 24px));font:12px/1.4 system-ui,-apple-system,
  "Segoe UI",sans-serif;color:#f1f4f4;text-align:left;isolation:isolate}
#project-progress-status details{background:rgba(18,26,29,.96);border:1px solid #5c6b70;
  border-radius:11px;box-shadow:0 6px 22px #0005;overflow:hidden;backdrop-filter:blur(8px)}
#project-progress-status summary{display:flex;gap:10px;align-items:center;
  list-style:none;cursor:pointer;padding:8px 10px;white-space:normal;font-weight:650}
#project-progress-status summary::-webkit-details-marker{display:none}
#project-progress-status summary:focus-visible{outline:2px solid #d9c080;outline-offset:-2px}
#project-progress-status .p-revision{opacity:.85;font-variant-numeric:tabular-nums}
#project-progress-status .p-pct{border-left:1px solid #637074;padding-left:10px;
  color:#e5ce8d;font-variant-numeric:tabular-nums}
#project-progress-status .p-more{opacity:.7;margin-left:auto;font-size:10px}
#project-progress-status details[open] .p-more{transform:rotate(180deg)}
#project-progress-status .p-detail{padding:2px 12px 12px;border-top:1px solid #526168}
#project-progress-status .p-title{margin:9px 0 4px;font-weight:700}
#project-progress-status .p-detail p{margin:4px 0;color:#c4d0d0}
#project-progress-status progress{width:100%;height:7px;accent-color:#d8bf7f}
@media print{#project-progress-status{display:none!important}}
`;
    document.head.appendChild(style);
    const frame = make('aside');
    frame.id = 'project-progress-status';
    frame.setAttribute('aria-label', 'Project revision and scoped completion');
    const details = make('details');
    const summary = make('summary');
    summary.setAttribute('aria-label', 'Show project revision and progress basis');
    summary.append(make('span', 'p-revision', 'Rev ' + revision));
    summary.append(make('span', 'p-pct',
      count.percent === null ? 'Progress —' : String(count.percent) + '%'));
    summary.append(make('span', 'p-more', '▾'));
    details.append(summary);
    const body = make('div', 'p-detail');
    body.append(make('div', 'p-title', String(config.progress?.label || 'Tracked milestone')));
    if (count.percent !== null) {
      const bar = make('progress');
      bar.value = count.done; bar.max = count.total;
      bar.setAttribute('aria-label', String(config.progress?.label || 'Progress'));
      body.append(bar);
      body.append(make('p', '', count.done + ' of ' + count.total + ' tracked units complete'));
    } else body.append(make('p', '', 'No defensible completion denominator is recorded.'));
    if (config.progress?.basis) body.append(make('p', '', config.progress.basis));
    if (config.progress?.note) body.append(make('p', '', config.progress.note));
    if (config.asOf) body.append(make('p', '', 'Progress reviewed: ' + config.asOf));
    details.append(body); frame.append(details);
    document.body.appendChild(frame);
  }
  if (document.readyState === 'loading')
    document.addEventListener('DOMContentLoaded', mount, {once:true});
  else mount();
})();
