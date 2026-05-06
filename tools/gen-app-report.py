#!/usr/bin/env python3
"""
Genera reporte HTML de APP Maestro para el dashboard QA.
Lee todos los batch-*.log del día y produce reporte acumulativo.

Uso:
    python3 tools/gen-app-report.py <cliente_slug> <cliente_cap> <fecha> [--env staging|production]

Ejemplo:
    python3 tools/gen-app-report.py caren Caren 2026-05-06
    python3 tools/gen-app-report.py caren Caren 2026-05-06 --env staging
"""

import sys, re, json, os, glob
from datetime import datetime
from html import escape
from urllib.parse import quote
from pathlib import Path

# ── Args ──────────────────────────────────────────────────────
args = sys.argv[1:]
client_slug = args[0] if len(args) > 0 else ""
client_cap  = args[1] if len(args) > 1 else client_slug.capitalize()
date_str    = args[2] if len(args) > 2 else datetime.now().strftime("%Y-%m-%d")
environment = "staging"
if "--env" in args:
    idx = args.index("--env")
    environment = args[idx + 1] if idx + 1 < len(args) else "staging"

QA_ROOT     = Path(__file__).parent.parent
OUTPUT_DIR  = QA_ROOT / "QA" / client_cap / date_str
HTML_DIR    = QA_ROOT / "public" / "qa" / "app-reports"
MANIFEST    = QA_ROOT / "public" / "qa" / "manifest.json"
REPORT_FILE = f"{client_cap}-{date_str}.html"
REPORT_PATH = HTML_DIR / REPORT_FILE

# ── Leer sync data si existe ─────────────────────────────────
sync_data = None
sync_json_path = OUTPUT_DIR / "sync-data.json"
if sync_json_path.exists():
    try:
        sync_data = json.loads(sync_json_path.read_text())
    except Exception:
        pass

# ── Leer batch logs en orden ──────────────────────────────────
batch_logs = sorted(OUTPUT_DIR.glob("batch-*.log"))

if not batch_logs:
    print(f"❌ No hay batch logs en {OUTPUT_DIR}")
    sys.exit(1)

batches_done = []
flows = []

for log_path in batch_logs:
    batch_num = re.search(r"batch-(\d+)", log_path.name)
    batch_num = int(batch_num.group(1)) if batch_num else 0
    batches_done.append(batch_num)

    for line in log_path.read_text().splitlines():
        m = re.match(r'\[(Passed|Failed|Manual-Pass|Skipped)\]\s+(.+?)\s+\(([^)]*)\)(?:\s+\((.+)\))?', line.strip())
        if m:
            flows.append({
                'name':     m.group(2),
                'status':   m.group(1).lower().replace('-', '_'),
                'duration': m.group(3),
                'error':    m.group(4) or '',
                'batch':    batch_num,
            })

passed  = sum(1 for f in flows if f['status'] == 'passed')
manual  = sum(1 for f in flows if f['status'] == 'manual_pass')
failed  = sum(1 for f in flows if f['status'] == 'failed')
skipped = sum(1 for f in flows if f['status'] == 'skipped')
total   = len(flows)
effective = total - skipped
health  = round((passed + manual) / effective * 100) if effective > 0 else 0

health_color = '#10b981' if health >= 80 else '#f59e0b' if health >= 60 else '#ef4444'
verdict      = 'LISTO' if health == 100 and failed == 0 else 'CON OBSERVACIONES' if health >= 70 else 'BLOQUEADO'
verdict_cls  = 'listo' if health == 100 and failed == 0 else 'condiciones' if health >= 70 else 'bloqueado'

total_batches = 3  # convención: siempre 3 batches
is_partial = max(batches_done) < total_batches if batches_done else True
partial_note = f" · Batches completados: {'/'.join(str(b) for b in sorted(batches_done))}/{total_batches}" if is_partial else ""

# ── Tabla de flows ─────────────────────────────────────────────
rows = ''
current_batch = None
for f in flows:
    if f['batch'] != current_batch:
        current_batch = f['batch']
        batch_names = {1: "Batch 1 — Core", 2: "Batch 2 — Alcance", 3: "Batch 3 — Pendientes"}
        label = batch_names.get(current_batch, f"Batch {current_batch}")
        rows += f'<tr class="batch-header"><td colspan="3">{label}</td></tr>'

    s = f['status']
    if s == 'passed':      icon, badge_cls, label = '✅', 'pass', 'PASS'
    elif s == 'manual_pass': icon, badge_cls, label = '👤', 'manual', 'MANUAL'
    elif s == 'skipped':   icon, badge_cls, label = '⏭', 'skip', 'SKIP'
    else:                  icon, badge_cls, label = '❌', 'fail', 'FAIL'

    # Extraer assertion fallida desde directorio Maestro si existe
    maestro_dir = f['error'] if f['error'] and os.path.isdir(f['error']) else None
    failed_assertion = ''
    yaml_file = ''
    if maestro_dir:
        cmd_files = sorted(glob.glob(f'{maestro_dir}/commands-*.json'))
        if cmd_files:
            yaml_file = re.sub(r'^commands-\((.+)\)\.json$', r'\1', os.path.basename(cmd_files[0]))
            try:
                cmds = json.loads(open(cmd_files[0]).read())
                for cmd in cmds:
                    meta = cmd.get('metadata', {})
                    if meta.get('status') in ('FAILED', 'ERROR'):
                        failed_assertion = meta.get('error', {}).get('message', '')[:280]
                        break
            except Exception:
                pass

    err_html = f'<div class="flow-error">{escape(failed_assertion[:120])}</div>' if failed_assertion else ''
    linear_btn = ''
    if s == 'failed':
        domain = f'{client_slug}.solopide.me' if environment == 'staging' else f'{client_slug}.youorder.me'
        dashboard_url = f'https://yomcl.github.io/qa/qa/app-reports/{client_cap}-{date_str}.html'
        github_flow = f'https://github.com/YOMCL/qa/blob/main/tests/app/flows/{client_slug}/{yaml_file}' if yaml_file else ''
        desc_parts = [
            f'Cliente: {client_cap} | Ambiente: {environment} ({domain}) | Fecha: {date_str}',
            f'Flow: {f["name"]}',
        ]
        if yaml_file:
            desc_parts.append(f'Archivo: tests/app/flows/{client_slug}/{yaml_file}')
        if failed_assertion:
            desc_parts += ['', f'Assertion fallida: {failed_assertion}']
        desc_parts += [
            '',
            'Pasos para reproducir:',
            f'1. Login como vendedor en me.youorder.yomventas.debug ({environment}, {domain})',
            '2. Seguir el flujo hasta la pantalla descrita en la assertion',
            '3. Observar el comportamiento inesperado',
            '',
            f'Reporte QA: {dashboard_url}',
        ]
        if github_flow:
            desc_parts.append(f'Flow YAML: {github_flow}')
        lt = quote(f'APP {client_cap}: {f["name"]} — fallo QA ({date_str})')
        ld = quote('\n'.join(desc_parts))
        linear_btn = f'<a href="https://linear.app/yom-tech/new?title={lt}&description={ld}" target="_blank" class="linear-btn">🔗 Ticket</a>'

    rows += f"""
        <tr>
            <td><span class="flow-icon">{icon}</span> {escape(f['name'])}{err_html}</td>
            <td><span class="badge {badge_cls}">{label}</span>{linear_btn}</td>
            <td class="duration">{escape(f['duration'])}</td>
        </tr>"""

# ── Stats card ─────────────────────────────────────────────────
generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
partial_banner = ""
if is_partial:
    remaining = [b for b in range(1, total_batches + 1) if b not in batches_done]
    remaining_str = ', '.join(str(b) for b in remaining)
    partial_banner = f'''
    <div class="partial-banner">
        ⏳ Reporte parcial — faltan batch(es): {remaining_str} de {total_batches} · Se actualiza automáticamente al correr cada batch
    </div>'''

domain_all = f'{client_slug}.solopide.me' if environment == 'staging' else f'{client_slug}.youorder.me'
dashboard_url_all = f'https://yomcl.github.io/qa/qa/app-reports/{client_cap}-{date_str}.html'
failed_flows_list = '\n'.join(f'- {f["name"]}' for f in flows if f['status'] == 'failed')
lt_all = quote(f'APP {client_cap}: resumen QA Maestro — {verdict} ({passed+manual}/{total} flows, {date_str})')
ld_all = quote(
    f'Cliente: {client_cap} | Ambiente: {environment} ({domain_all}) | Fecha: {date_str}\n'
    f'Health: {health}/100 | Flows: {passed+manual}/{total} PASS · {failed} FAIL | Veredicto: {verdict}\n'
    + (f'\nFlows fallidos:\n{failed_flows_list}\n' if failed_flows_list else '\nTodos los flows pasaron.\n')
    + f'\nReporte completo: {dashboard_url_all}'
)

# ── Sync card ──────────────────────────────────────────────────
sync_card = ''
if sync_data:
    sync_ok    = sync_data.get('successful', False)
    sync_total = sync_data.get('totalSeconds', 0)
    sync_icon  = '✅' if sync_ok else '⚠️'
    sync_note  = '' if sync_ok else '<span style="color:#92400e;font-size:.82em;margin-left:8px">sub-syncs sin config marcados como failed (bug conocido)</span>'
    sync_rows  = ''
    for a in sync_data.get('actions', []):
        row_ok   = a.get('ok', False)
        row_icon = '✅' if row_ok else '❌'
        pct      = f"{a['seconds']/sync_total*100:.0f}%" if sync_total > 0 else ''
        sync_rows += f"<tr><td>{row_icon} {escape(a['type'])}</td><td style='text-align:right'>{a['docs']}</td><td style='text-align:right'>{a['requests']}</td><td style='text-align:right;color:#6b7280'>{a['seconds']}s</td><td style='text-align:right;color:#9ca3af;font-size:.8em'>{pct}</td></tr>"
    device = escape(sync_data.get('deviceModel', ''))
    ram    = escape(sync_data.get('freeRam', ''))
    sync_card = f"""
<div class="card">
  <div class="card-title">{sync_icon} Sync inicial — {sync_total:.1f}s total{sync_note}</div>
  <p style="font-size:.8em;color:#6b7280;margin-bottom:12px">{device} · RAM libre: {ram} · App {escape(sync_data.get('appVersion',''))}</p>
  <div class="table-wrap"><table>
    <thead><tr><th>Acción</th><th style="text-align:right">Docs</th><th style="text-align:right">Requests</th><th style="text-align:right">Tiempo</th><th style="text-align:right">%</th></tr></thead>
    <tbody>{sync_rows}</tbody>
  </table></div>
</div>"""

HTML_DIR.mkdir(parents=True, exist_ok=True)

html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>APP QA — {escape(client_cap)} — {date_str}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f8f9fb;padding:0 0 40px}}
.container{{max-width:1100px;margin:0 auto;padding:0 24px}}
.site-header{{background:#fff;border-bottom:1px solid #e2e5e9;padding:14px 24px;margin-bottom:24px;display:flex;align-items:center;gap:16px}}
.back-link{{color:#4f6ef7;text-decoration:none;font-size:.88em;font-weight:600}}
.site-header h1{{font-size:1.25em;font-weight:700;color:#1a1d23}}
.site-header p{{font-size:.85em;color:#64748b}}
.partial-banner{{background:#fef3c7;border:1px solid #fbbf24;border-radius:8px;padding:10px 16px;font-size:.85em;color:#92400e;margin-bottom:16px;font-weight:500}}
.card{{background:#fff;border-radius:12px;padding:24px;margin-bottom:16px;box-shadow:0 1px 3px rgba(0,0,0,.06),0 4px 12px rgba(0,0,0,.06)}}
.card-title{{font-size:1em;font-weight:700;color:#111827;margin-bottom:16px;padding-bottom:10px;border-bottom:1.5px solid #e5e7eb}}
.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(100px,1fr));gap:10px;margin-bottom:20px}}
.stat{{padding:14px;border-radius:10px;text-align:center;color:#fff}}
.stat.blue{{background:linear-gradient(135deg,#4f6ef7,#3b5bdb)}}
.stat.green{{background:linear-gradient(135deg,#10b981,#059669)}}
.stat.red{{background:linear-gradient(135deg,#ef4444,#dc2626)}}
.stat.amber{{background:linear-gradient(135deg,#f59e0b,#d97706)}}
.stat.gray{{background:linear-gradient(135deg,#9ca3af,#6b7280)}}
.stat-value{{font-size:1.6em;font-weight:800;line-height:1}}
.stat-label{{font-size:.68em;opacity:.9;font-weight:600;margin-top:4px}}
.verdict-badge{{display:inline-block;padding:6px 18px;border-radius:99px;font-weight:700;font-size:.9em;margin-bottom:14px}}
.verdict-listo{{background:#d1fae5;color:#065f46}}
.verdict-condiciones{{background:#fef3c7;color:#92400e}}
.verdict-bloqueado{{background:#fee2e2;color:#991b1b}}
.health-meta{{display:flex;justify-content:space-between;font-size:.82em;color:#6b7280;font-weight:600;margin-bottom:5px}}
.health-meta strong{{color:#111827}}
.health-track{{height:10px;background:#f3f4f6;border-radius:99px;overflow:hidden}}
.health-fill{{height:100%;border-radius:99px;background:{health_color}}}
.linear-btn{{display:inline-block;margin-left:6px;padding:2px 8px;background:#4f6ef7;color:#fff;border-radius:5px;font-size:.72em;font-weight:600;text-decoration:none;vertical-align:middle}}
.table-wrap{{overflow-x:auto;-webkit-overflow-scrolling:touch}}
table{{width:100%;border-collapse:collapse;table-layout:fixed}}
th{{background:#f9fafb;text-align:left;padding:10px 14px;font-size:.78em;color:#6b7280;font-weight:700;text-transform:uppercase;letter-spacing:.04em;border-bottom:1.5px solid #e5e7eb;white-space:nowrap}}
td{{padding:10px 14px;border-bottom:1px solid #f3f4f6;font-size:.88em;vertical-align:top;word-break:break-word;overflow-wrap:anywhere}}
tr:last-child td{{border-bottom:none}}
tr.batch-header td{{background:#f1f5f9;color:#475569;font-size:.78em;font-weight:700;text-transform:uppercase;letter-spacing:.05em;padding:7px 14px;border-bottom:1.5px solid #e2e8f0}}
.badge{{padding:2px 10px;border-radius:99px;font-size:.75em;font-weight:700}}
.badge.pass{{background:#d1fae5;color:#065f46}}
.badge.manual{{background:#dbeafe;color:#1e40af}}
.badge.skip{{background:#f3f4f6;color:#6b7280}}
.badge.fail{{background:#fee2e2;color:#991b1b}}
.flow-error{{font-size:.8em;color:#9ca3af;margin-top:3px;font-style:italic}}
.flow-icon{{margin-right:4px}}
.duration{{color:#9ca3af;white-space:nowrap}}
footer{{color:#9ca3af;font-size:.82em;text-align:center;margin-top:24px}}
</style>
</head>
<body>
<div class="site-header">
  <a href="../" class="back-link">← Dashboard</a>
  <div>
    <h1>📱 APP QA — {escape(client_cap)}</h1>
    <p>Maestro · {date_str} · {environment}{partial_note}</p>
  </div>
</div>
<div class="container">
{partial_banner}
<div class="card">
  <div class="card-title">Resumen</div>
  <span class="verdict-badge verdict-{verdict_cls}">{verdict}</span>
  <a href="https://linear.app/yom-tech/new?title={lt_all}&description={ld_all}" target="_blank" class="linear-btn" style="font-size:.85em;padding:6px 14px;margin-left:10px;">🔗 Crear ticket</a>
  <div class="stats" style="margin-top:16px">
    <div class="stat blue"><div class="stat-value">{total}</div><div class="stat-label">Flows</div></div>
    <div class="stat green"><div class="stat-value">{passed}</div><div class="stat-label">PASS</div></div>
    <div class="stat red"><div class="stat-value">{failed}</div><div class="stat-label">FAIL</div></div>
    <div class="stat gray"><div class="stat-value">{skipped}</div><div class="stat-label">SKIP</div></div>
    <div class="stat amber"><div class="stat-value">{health}%</div><div class="stat-label">Health</div></div>
  </div>
  <div>
    <div class="health-meta"><span>Health score</span><strong>{health}%</strong></div>
    <div class="health-track"><div class="health-fill" style="width:{health}%"></div></div>
  </div>
</div>
{sync_card}
<div class="card">
  <div class="card-title">Flows por batch</div>
  <div class="table-wrap"><table>
    <thead><tr><th style="width:65%">Flow</th><th style="width:20%">Estado</th><th style="width:15%">Duración</th></tr></thead>
    <tbody>{rows}</tbody>
  </table></div>
</div>
<footer>Generado {generated_at} · Batches completados: {sorted(batches_done)} de {total_batches}</footer>
</div>
</body>
</html>"""

REPORT_PATH.write_text(html)

# ── Actualizar manifest ────────────────────────────────────────
manifest = {'reports': []}
if MANIFEST.exists():
    try:
        manifest = json.loads(MANIFEST.read_text())
    except Exception:
        pass

manifest['reports'] = [
    r for r in manifest.get('reports', [])
    if not (r.get('client_slug') == client_slug and r.get('date') == date_str and r.get('platform') == 'app')
]
manifest['reports'].insert(0, {
    'client':       client_cap,
    'client_slug':  client_slug,
    'date':         date_str,
    'file':         f'app-reports/{REPORT_FILE}',
    'platform':     'app',
    'environment':  environment,
    'passed':       passed,
    'failed':       failed,
    'skipped':      skipped,
    'total':        total,
    'health':       health,
    'verdict':      verdict,
    'partial':      is_partial,
    'batches_done': sorted(batches_done),
})

MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))

status = "⏳ parcial" if is_partial else "✅ completo"
print(f"{status} · {passed}✅ {failed}❌ {skipped}⏭ · {health}% · {verdict}")
print(f"→ public/qa/app-reports/{REPORT_FILE}")
