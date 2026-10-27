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
  // Roadmap completion is earned only by individually accepted, evidenced gates.
  // A partial gate contributes zero until its explicit acceptance criteria are met.
  function roadmapFor(config) {
    const data = config.roadmap;
    if (!data || !Array.isArray(data.gates) || !data.gates.length) return null;
    const ids = new Set();
    let total = 0, done = 0;
    for (const gate of data.gates) {
      if (!gate || typeof gate.id !== 'string' || !/^[a-z0-9-]{2,64}$/.test(gate.id) ||
          ids.has(gate.id) || typeof gate.label !== 'string' ||
          !gate.label.trim() || !Number.isInteger(gate.weight) || gate.weight < 1 ||
          !['accepted','partial','planned'].includes(gate.status) ||
          typeof gate.evidence !== 'string' || !gate.evidence.trim()) return null;
      ids.add(gate.id);
      total += gate.weight;
      if (gate.status === 'accepted') done += gate.weight;
    }
    // A fixed approved delivery roadmap is 100 points. An invalid or unfinished
    // accounting definition must never appear as a valid percentage.
    if (total !== 100) return null;
    return {data, done, total, percent: done, gates: data.gates};
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
    const roadmap = roadmapFor(config);
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
#project-progress-status .p-secondary{margin-top:12px;border-top:1px solid #526168;padding-top:8px}
#project-progress-status .p-gates{max-height:184px;overflow-y:auto;margin:8px 0 0;padding:0;list-style:none}
#project-progress-status .p-gates li{display:flex;justify-content:space-between;gap:8px;padding:4px 0;border-bottom:1px dotted #526168;color:#dce4e4}
#project-progress-status .p-gates span:last-child{white-space:nowrap;opacity:.8;font-variant-numeric:tabular-nums}
#project-progress-status .p-gates .p-accepted span:last-child{color:#b4e1c1}
#project-progress-status .p-detail a{color:#e5ce8d}
#project-progress-status .p-detail a:focus-visible{outline:2px solid #d9c080}
@media print{#project-progress-status{display:none!important}}
`;
    document.head.appendChild(style);
    const frame = make('aside');
    frame.id = 'project-progress-status';
    frame.setAttribute('aria-label', 'Project revision and roadmap completion');
    const details = make('details');
    const summary = make('summary');
    summary.setAttribute('aria-label', 'Show project revision and progress basis');
    summary.append(make('span', 'p-revision', 'Rev ' + revision));
    summary.append(make('span', 'p-pct', roadmap ?
      'Roadmap ' + roadmap.percent + '%' :
      (config.roadmap ? 'Roadmap —' :
       (count.percent === null ? 'Progress —' : String(count.percent) + '%'))));
    summary.append(make('span', 'p-more', '▾'));
    details.append(summary);
    const body = make('div', 'p-detail');
    if (roadmap) {
      body.append(make('div', 'p-title', String(roadmap.data.label || 'Approved overall delivery roadmap')));
      const bar = make('progress');
      bar.value = roadmap.done; bar.max = roadmap.total;
      bar.setAttribute('aria-label', 'Accepted overall roadmap weight');
      body.append(bar);
      body.append(make('p', '', roadmap.done + ' of 100 weighted delivery points accepted'));
      if (roadmap.data.scope) body.append(make('p', '', roadmap.data.scope));
      const gates = make('ul', 'p-gates');
      gates.setAttribute('aria-label', 'Roadmap gates and acceptance status');
      for (const gate of roadmap.gates) {
        const item = make('li', 'p-' + gate.status);
        item.append(make('span', '', gate.label));
        item.append(make('span', '', gate.status + ' · ' + gate.weight + 'pt'));
        gates.append(item);
      }
      body.append(gates);
      if (roadmap.data.note) body.append(make('p', '', roadmap.data.note));
      if (roadmap.data.document && /^[a-zA-Z0-9_./-]+$/.test(roadmap.data.document) &&
          !roadmap.data.document.includes('..')) {
        const link = make('a', '', 'Read roadmap and acceptance evidence');
        link.href = new URL(roadmap.data.document, root).href;
        link.target = '_blank'; link.rel = 'noopener noreferrer';
        body.append(link);
      }
    } else if (config.roadmap) {
      body.append(make('p', '', 'Roadmap accounting is invalid; overall percentage withheld.'));
    }
    const phase = make('div', roadmap ? 'p-secondary' : '');
    phase.append(make('div', 'p-title', String(config.progress?.label || 'Tracked milestone')));
    if (count.percent !== null) {
      const bar = make('progress');
      bar.value = count.done; bar.max = count.total;
      bar.setAttribute('aria-label', String(config.progress?.label || 'Progress'));
      phase.append(bar);
      phase.append(make('p', '', count.done + ' of ' + count.total + ' tracked units complete'));
    } else phase.append(make('p', '', 'No defensible completion denominator is recorded.'));
    if (config.progress?.basis) phase.append(make('p', '', config.progress.basis));
    if (config.progress?.note) phase.append(make('p', '', config.progress.note));
    body.append(phase);
    if (config.asOf) body.append(make('p', '', 'Progress reviewed: ' + config.asOf));
    details.append(body); frame.append(details);
    document.body.appendChild(frame);
  }
  if (document.readyState === 'loading')
    document.addEventListener('DOMContentLoaded', mount, {once:true});
  else mount();
})();
