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

import sys, re, json, os, glob, urllib.request, urllib.error
from datetime import datetime
from html import escape
from urllib.parse import quote
from pathlib import Path

# Flags con manifestación visual en la APP — (sección, descripción legible)
FEATURE_DISPLAY = [
    ('loginButtons.facebook',             'Pantalla de login',            "Botón login con Facebook"),
    ('loginButtons.google',               'Pantalla de login',            "Botón login con Google"),
    ('commerce.enableCreateCommerce',     'Lista de comercios',           "Botón 'Crear Comercio'"),
    ('hasNoSaleFilter',                   'Lista de comercios',           "Filtro 'Sin venta' en lista de comercios"),
    ('inMaintenance',                     'Lista de comercios',           "Banner de mantenimiento en la app"),
    ('enablePayments',                    'Menú lateral (drawer)',        "Módulo Pagos en menú lateral"),
    ('enablePaymentsCollection',          'Menú lateral (drawer)',        "Módulo Cobros en menú lateral"),
    ('enableTask',                        'Menú lateral (drawer)',        "Módulo Tareas en menú lateral"),
    ('enableCreditNotes',                 'Menú lateral (drawer)',        "Módulo Notas de crédito en menú lateral"),
    ('enableInvoicesList',                'Menú lateral (drawer)',        "Módulo Facturas en menú lateral"),
    ('pendingDocuments',                  'Menú lateral (drawer)',        "Módulo Documentos pendientes en menú lateral"),
    ('pointsEnabled',                     'Menú lateral (drawer)',        "Módulo Puntos en menú lateral"),
    ('enableDialogNoSellReason',          'Menú lateral (drawer)',        "Opción 'Razón de no venta'"),
    ('hasMultiUnitEnabled',               'Catálogo',                     "Selector DIS/UND (multi-unidad)"),
    ('hasStockEnabled',                   'Catálogo',                     "Indicador de stock en productos"),
    ('enableDistributionCentersSelector', 'Catálogo',                     "Selector de centros de distribución"),
    ('enableSellerDiscount',              'Carrito / checkout',           "Descuento manual del vendedor"),
    ('enableCoupons',                     'Carrito / checkout',           "Cupones en carrito"),
    ('purchaseOrderEnabled',              'Carrito / checkout',           "Campo Orden de compra / Nº pedido"),
    ('enableAskDeliveryDate',             'Carrito / checkout',           "Selector de fecha de entrega"),
    ('taxes.showSummary',                 'Carrito / checkout',           "Resumen de impuestos/IVA"),
]

def get_features_from_matrix(client_slug, qa_root):
    """Lee feature flags desde qa-matrix-staging.json para el cliente dado."""
    matrix_path = qa_root / 'data' / 'qa-matrix-staging.json'
    if not matrix_path.exists():
        return []
    try:
        matrix = json.loads(matrix_path.read_text())
        clients_data = matrix.get('clients', {})
        client_key = next((k for k in clients_data if client_slug in k.lower()), None)
        if not client_key:
            return []
        variables = clients_data[client_key].get('variables', {})
    except Exception:
        return []
    items = []
    for flag, section, desc in FEATURE_DISPLAY:
        val = variables.get(flag, False)
        state = 'VISIBLE' if val else 'INVISIBLE'
        items.append({'section': section, 'desc': desc, 'state': state,
                      'config': f'{flag}: {str(val).lower()}', 'flag': flag})
    return items

def parse_yaml_checklist(yaml_filename, client_slug, qa_root):
    """Parsea comentarios '# Desc — VISIBLE/INVISIBLE (config)' de un flow YAML."""
    yaml_path = qa_root / 'tests' / 'app' / 'flows' / client_slug / yaml_filename
    if not yaml_path.exists():
        return []
    items = []
    section = ''
    for line in yaml_path.read_text().splitlines():
        line = line.strip()
        sec_m = re.match(r'#\s+──+\s+(.+?)\s+──+', line)
        if sec_m:
            section = sec_m.group(1).strip()
            continue
        chk_m = re.match(r'#\s+(.+?)\s+—\s+(VISIBLE|INVISIBLE)\s+\((.+?)\)', line)
        if chk_m:
            items.append({'section': section, 'desc': chk_m.group(1),
                          'state': chk_m.group(2), 'config': chk_m.group(3), 'flag': ''})
    return items

def render_checklist_html(items):
    if not items:
        return ''
    rows_html = ''
    cur_sec = None
    for it in items:
        if it['section'] != cur_sec:
            cur_sec = it['section']
            rows_html += f'<tr><td colspan="3" class="chk-section">{escape(cur_sec)}</td></tr>'
        is_bug = it.get('flag') in {'enableDistributionCentersSelector', 'enableAskDeliveryDate'} and it['state'] == 'VISIBLE'
        icon = '🔴' if is_bug else ('🟢' if it['state'] == 'VISIBLE' else '➖')
        rows_html += (f'<tr><td class="chk-icon">{icon}</td>'
                      f'<td class="chk-desc">{escape(it["desc"])}</td>'
                      f'<td class="chk-config">{escape(it["config"])}</td></tr>')
    return (f'<details class="chk-details"><summary>Ver checklist de features</summary>'
            f'<table class="chk-table"><thead><tr>'
            f'<th></th><th>Feature</th><th>Config</th></tr></thead>'
            f'<tbody>{rows_html}</tbody></table></details>')

def render_slack_html(text):
    """Convierte texto con formato Slack a HTML limpio para el dashboard."""
    lines = text.split('\n')
    parts = []
    for line in lines:
        if not line.strip():
            parts.append('<div style="height:6px"></div>')
            continue
        safe = escape(line)
        safe = re.sub(r'\*([^*]+)\*', r'<strong>\1</strong>', safe)
        safe = re.sub(r'_([^_]+)_', r'<em style="color:#6b7280">\1</em>', safe)
        if line.strip().startswith('•') or line.strip().startswith('  •'):
            parts.append(f'<div style="padding:1px 0 1px 14px;color:#374151">{safe}</div>')
        elif re.match(r'^\s*\*', line):
            parts.append(f'<div style="padding:3px 0;font-size:.9em">{safe}</div>')
        else:
            parts.append(f'<div style="padding:1px 0;font-size:.85em;color:#6b7280">{safe}</div>')
    return '\n'.join(parts)

def read_yaml_context(yaml_filename, client_slug, qa_root):
    """Lee comentarios de cabecera de un flow YAML para enriquecer tickets Linear."""
    yaml_path = qa_root / 'tests' / 'app' / 'flows' / client_slug / yaml_filename
    ctx = {'objetivo': '', 'config': '', 'alcance': '', 'bug': '', 'pasos': '', 'flow_name': ''}
    if not yaml_path.exists():
        return ctx
    for line in yaml_path.read_text().splitlines():
        line = line.strip()
        if line.startswith('name:') and not ctx['flow_name']:
            ctx['flow_name'] = line.replace('name:', '').strip().strip('"').strip("'")
        if line.startswith('# OBJETIVO:'):
            ctx['objetivo'] = line.replace('# OBJETIVO:', '').strip()
        elif line.startswith('# Config:'):
            ctx['config'] = line.replace('# Config:', '').strip()
        elif 'Alcance' in line and line.startswith('#'):
            if not ctx['alcance']:
                ctx['alcance'] = line.lstrip('# ').strip()
        elif line.startswith('# BUG CONOCIDO:'):
            ctx['bug'] = line.replace('# BUG CONOCIDO:', '').strip()
        elif line.startswith('# PASOS:'):
            ctx['pasos'] = line.replace('# PASOS:', '').strip()
    return ctx

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

# ── Leer JSONBIN_KEY ──────────────────────────────────────────
jsonbin_key = os.environ.get('JSONBIN_KEY', '')
if not jsonbin_key:
    _env_path = QA_ROOT / '.env'
    if _env_path.exists():
        for _line in _env_path.read_text().splitlines():
            if _line.startswith('JSONBIN_KEY='):
                jsonbin_key = _line.split('=', 1)[1].strip().strip('"').strip("'")
                break

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

total_batches = 3  # convención: siempre 3 batches
is_partial = max(batches_done) < total_batches if batches_done else True
partial_note = f" · Batches completados: {'/'.join(str(b) for b in sorted(batches_done))}/{total_batches}" if is_partial else ""

# ── Leer fixes.json si existe ─────────────────────────────────
fixes = {}
fixes_path = OUTPUT_DIR / "fixes.json"
if fixes_path.exists():
    try:
        fixes = json.loads(fixes_path.read_text())
    except Exception:
        pass

fixed_count = sum(1 for f in flows if f['status'] == 'failed' and fixes.get(f['name']))
real_failed = failed - fixed_count
health  = round((passed + manual + fixed_count) / effective * 100) if effective > 0 else 0

health_color = '#00A76F' if health >= 80 else '#FFAB00' if health >= 60 else '#FF5630'
verdict      = 'LISTO' if health == 100 and real_failed == 0 else 'CON OBSERVACIONES' if health >= 70 else 'BLOQUEADO'
verdict_cls  = 'listo' if health == 100 and real_failed == 0 else 'condiciones' if health >= 70 else 'bloqueado'

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
    # f['name'] es el yaml filename (ej: "02-pedido.yaml") — usar para lookup en fixes
    is_fixed = (s == 'failed') and bool(fixes.get(f['name']))
    if s == 'passed':        icon, badge_cls, label = '✅', 'pass', 'PASS'
    elif s == 'manual_pass': icon, badge_cls, label = '👤', 'manual', 'MANUAL'
    elif s == 'skipped':     icon, badge_cls, label = '⏭', 'skip', 'SKIP'
    elif is_fixed:           icon, badge_cls, label = '🔧', 'fixed-fail', 'FIXED'
    else:                    icon, badge_cls, label = '❌', 'fail', 'FAIL'

    # Extraer assertion fallida desde directorio Maestro si existe
    maestro_dir = f['error'] if f['error'] and os.path.isdir(f['error']) else None
    failed_assertion = ''
    yaml_file = f['name']  # fallback al nombre del flow
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
    fix_note = f'<div class="flow-error" style="color:#854d0e">{escape(fixes.get(f["name"], ""))}</div>' if is_fixed else ''
    if s == 'failed' and not is_fixed:
        domain = f'{client_slug}.solopide.me' if environment == 'staging' else f'{client_slug}.youorder.me'
        dashboard_url = f'https://yomcl.github.io/qa/qa/app-reports/{client_cap}-{date_str}.html'
        github_flow = f'https://github.com/YOMCL/qa/blob/main/tests/app/flows/{client_slug}/{yaml_file}' if yaml_file else ''
        ctx = read_yaml_context(yaml_file, client_slug, QA_ROOT) if yaml_file else {}
        desc_parts = [
            f'Cliente: {client_cap} | Ambiente: {environment} ({domain}) | Fecha: {date_str}',
        ]
        if ctx.get('objetivo'):
            desc_parts += ['', f'Descripción: {ctx["objetivo"]}']
        if ctx.get('config'):
            desc_parts.append(f'Configuración: {ctx["config"]}')
        if ctx.get('alcance'):
            desc_parts.append(f'Alcance: {ctx["alcance"]}')
        if yaml_file:
            desc_parts.append(f'Archivo: tests/app/flows/{client_slug}/{yaml_file}')
        if failed_assertion:
            # Derivar expected vs actual desde el mensaje de assertion
            if 'is visible' in failed_assertion and 'not visible' not in failed_assertion:
                assertion_text = re.sub(r'Assertion is false: ', '', failed_assertion).replace(' is visible', '')
                desc_parts += ['', f'Comportamiento esperado: elemento visible → {assertion_text}',
                               f'Comportamiento actual: el elemento NO aparece en pantalla']
            elif 'is not visible' in failed_assertion:
                assertion_text = re.sub(r'Assertion is false: ', '', failed_assertion).replace(' is not visible', '')
                desc_parts += ['', f'Comportamiento esperado: elemento oculto → {assertion_text}',
                               f'Comportamiento actual: el elemento SÍ aparece en pantalla (no debería)']
            else:
                desc_parts += ['', f'Assertion fallida: {failed_assertion}']
        if ctx.get('bug'):
            desc_parts += ['', f'Contexto adicional: {ctx["bug"]}']
        desc_parts += ['', 'Pasos para reproducir:']
        if ctx.get('pasos'):
            for step in ctx['pasos'].split(' | '):
                desc_parts.append(f'  {step.strip()}')
        else:
            desc_parts += [
                f'  1. Login como vendedor en me.youorder.yomventas.debug ({environment}, {domain})',
                f'  2. Navegar según el flow: {yaml_file or f["name"]}',
                '  3. Reproducir la condición descrita en "Comportamiento actual"',
            ]
        desc_parts += ['', f'Reporte QA: {dashboard_url}']
        if github_flow:
            desc_parts.append(f'Flow YAML: {github_flow}')
        lt = quote(f'APP {client_cap}: {f["name"]} — fallo QA ({date_str})')
        ld = quote('\n'.join(desc_parts))
        linear_btn = f'<a href="https://linear.app/yom-tech/new?title={lt}&description={ld}" target="_blank" class="linear-btn">🔗 Ticket</a>'

    checklist_html = ''
    if yaml_file:
        if yaml_file == '04-features.yaml':
            chk_items = get_features_from_matrix(client_slug, QA_ROOT)
        else:
            chk_items = parse_yaml_checklist(yaml_file, client_slug, QA_ROOT)
        if chk_items:
            checklist_html = render_checklist_html(chk_items)
    rows += f"""
        <tr>
            <td><span class="flow-icon">{icon}</span> {escape(f['name'])}{err_html}{fix_note}{checklist_html}</td>
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

# ── Slack deliverable ─────────────────────────────────────────
def flow_label(yaml_name, client_slug, qa_root):
    """Devuelve nombre legible del flow: strip 'CLIENTE: NN — ' prefix y sufijos técnicos."""
    ctx = read_yaml_context(yaml_name, client_slug, qa_root)
    name = ctx.get('flow_name') or yaml_name
    # strip "CAREN: 12 — " or "CAREN: 05b — " style prefix
    name = re.sub(r'^[A-Z][A-Z\s]+:\s*\d+[a-z]?\s*[—-]\s*', '', name).strip()
    # strip "(enableXxx)" or "(CLIENTE-QA-NNN)" style suffixes
    name = re.sub(r'\s*\([^\)]{3,40}\)', '', name).strip()
    return name

pass_flows   = [f for f in flows if f['status'] in ('passed', 'manual_pass')]
fail_real    = [f for f in flows if f['status'] == 'failed' and not fixes.get(f['name'])]
fail_fixed   = [f for f in flows if f['status'] == 'failed' and fixes.get(f['name'])]
ok_flows     = pass_flows + fail_fixed  # fixed = probado físicamente, funciona bien

# ── Crear/leer JSONBin para resolutions ──────────────────────
jsonbin_id_path = OUTPUT_DIR / "jsonbin-id.txt"
jsonbin_bin_id = ''
if jsonbin_id_path.exists():
    jsonbin_bin_id = jsonbin_id_path.read_text().strip()
elif fail_real and jsonbin_key:
    initial = {fl['name']: {'resolved': False, 'comment': ''} for fl in fail_real}
    try:
        req = urllib.request.Request(
            'https://api.jsonbin.io/v3/b',
            data=json.dumps(initial).encode('utf-8'),
            method='POST'
        )
        req.add_header('Content-Type', 'application/json')
        req.add_header('X-Master-Key', jsonbin_key)
        req.add_header('X-Bin-Name', f'QA-{client_cap}-{date_str}')
        req.add_header('X-Bin-Private', 'false')
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            jsonbin_bin_id = result['metadata']['id']
            jsonbin_id_path.write_text(jsonbin_bin_id)
            print(f'✅ JSONBin creado: {jsonbin_bin_id}')
    except Exception as e:
        print(f'⚠️ JSONBin create failed: {e}')

# ── Textos para Slack (separados para interactividad) ─────────
STAGING_BUGS = {'enableDistributionCentersSelector', 'enableAskDeliveryDate'}

ok_labels   = [flow_label(f['name'], client_slug, QA_ROOT) for f in ok_flows]
fail_labels = [flow_label(f['name'], client_slug, QA_ROOT) for f in fail_real]

# Texto estático: header + funciona bien
header_lines = [f'📱 *{environment.upper()} ({domain_all})*', '']
if ok_flows:
    header_lines += [f'*Lo que funciona ✅ ({len(ok_flows)})*']
    header_lines += [f'  • {l}' for l in ok_labels]

# Texto estático: sync + features + link (va después de los fails)
footer_lines = []
if sync_data:
    sync_total = sync_data.get('totalSeconds', 0)
    sync_ok_icon = '✅' if sync_data.get('successful', False) else '⚠️'
    footer_lines += ['', f'*Sync inicial:* {sync_total:.1f}s {sync_ok_icon}']

chk_items = get_features_from_matrix(client_slug, QA_ROOT)
# Filtrar sección login (no relevante para el equipo)
chk_items = [it for it in chk_items if it['section'] != 'Pantalla de login']
if chk_items:
    footer_lines += ['', f'*Features configuradas en {client_cap}:*']
    cur_sec = None
    for it in chk_items:
        if it['section'] != cur_sec:
            cur_sec = it['section']
            footer_lines.append(f'_{cur_sec}_')
        is_bug = it.get('flag') in STAGING_BUGS and it['state'] == 'VISIBLE'
        icon_s = '🔴' if is_bug else ('🟢' if it['state'] == 'VISIBLE' else '➖')
        bug_note = ' (configurado ON — no funciona en staging)' if is_bug else ''
        footer_lines.append(f'  {icon_s} {it["desc"]}{bug_note}')
footer_lines += ['', f'*Reporte completo:* {dashboard_url_all}']

header_text = '\n'.join(header_lines)
footer_text = '\n'.join(footer_lines)

# HTML checkboxes para fallas
fail_checks_html = ''
for i, (label, fl) in enumerate(zip(fail_labels, fail_real)):
    fid = f'fail-{i}'
    fail_checks_html += (
        f'<div id="row-{fid}" style="padding:6px 0;border-bottom:1px solid #f3f4f6">'
        f'<label style="display:flex;align-items:center;gap:8px;cursor:pointer;font-size:.88em">'
        f'<input type="checkbox" id="{fid}" data-yaml="{escape(fl["name"])}" '
        f'onchange="toggleFail(\'{fid}\')" style="width:15px;height:15px;cursor:pointer">'
        f'<span id="txt-{fid}">❌ {escape(label)}</span></label>'
        f'<input type="text" id="cmt-{fid}" data-yaml="{escape(fl["name"])}" placeholder="Comentario..." '
        f'oninput="updateComment(\'{fid}\')" '
        f'style="margin-top:4px;margin-left:23px;width:calc(100% - 23px);padding:4px 8px;'
        f'font-size:.82em;border:1px solid #e5e7eb;border-radius:5px;color:#374151;background:#f9fafb">'
        f'</div>\n'
    )

fail_items_js = json.dumps(fail_labels)
fail_yamls_js = json.dumps([fl['name'] for fl in fail_real])

slack_card = f"""
<div class="card" id="slack-card">
  <div class="card-title">📋 Reporte
    <span id="save-status" style="float:right;font-size:.78em;font-weight:400;color:#6b7280;margin-top:3px;margin-left:8px"></span>
    <button onclick="copySlack()" style="float:right;margin-top:-4px;padding:5px 14px;background:#4f6ef7;color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:.82em;font-weight:600">📋 Copiar</button>
  </div>
  <div style="background:#f8f9fb;border:1px solid #e5e7eb;border-radius:8px;padding:12px 14px;margin-bottom:12px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif">{render_slack_html(header_text)}</div>
  <div style="margin-bottom:8px">
    <div style="font-size:.82em;font-weight:700;color:#991b1b;margin-bottom:6px">❌ Lo que no funciona — marca lo que se resuelva:</div>
    {fail_checks_html}
  </div>
  <div id="slack-footer" style="background:#f8f9fb;border:1px solid #e5e7eb;border-radius:8px;padding:12px 14px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif">{render_slack_html(footer_text)}</div>
</div>
<script>
var _binId={json.dumps(jsonbin_bin_id)};
var _binKey={json.dumps(jsonbin_key)};
var _resolutions={{}};
var _failYamls={fail_yamls_js};
var _failLabels={fail_items_js};
var _headerText={json.dumps(header_text)};
var _footerText={json.dumps(footer_text)};
var _saveTimer=null;
async function loadResolutions(){{
  if(!_binId)return;
  try{{
    var res=await fetch('https://api.jsonbin.io/v3/b/'+_binId+'/latest',
      {{headers:{{'X-Master-Key':_binKey}}}});
    if(!res.ok)return;
    var data=await res.json();
    _resolutions=data.record||{{}};
    applyResolutions();
  }}catch(e){{}}
}}
function applyResolutions(){{
  _failYamls.forEach(function(yaml,i){{
    var fid='fail-'+i;
    var r=_resolutions[yaml]||{{resolved:false,comment:''}};
    var cb=document.getElementById(fid);
    var cmt=document.getElementById('cmt-'+fid);
    if(cb)cb.checked=r.resolved;
    if(cmt)cmt.value=r.comment||'';
    applyStyle(fid,r.resolved);
  }});
}}
function applyStyle(fid,checked){{
  var span=document.getElementById('txt-'+fid);
  var row=document.getElementById('row-'+fid);
  if(!span)return;
  if(checked){{
    span.style.textDecoration='line-through';span.style.color='#10b981';
    span.textContent='✅ '+span.textContent.replace(/^[✅❌]\s*/,'');
    if(row)row.style.opacity='0.6';
  }}else{{
    span.style.textDecoration='';span.style.color='';
    span.textContent='❌ '+span.textContent.replace(/^[✅❌]\s*/,'');
    if(row)row.style.opacity='1';
  }}
}}
function toggleFail(fid){{
  var yaml=document.getElementById(fid).dataset.yaml;
  var checked=document.getElementById(fid).checked;
  if(!_resolutions[yaml])_resolutions[yaml]={{resolved:false,comment:''}};
  _resolutions[yaml].resolved=checked;
  applyStyle(fid,checked);
  scheduleSave();
}}
function updateComment(fid){{
  var el=document.getElementById('cmt-'+fid);
  if(!_resolutions[el.dataset.yaml])_resolutions[el.dataset.yaml]={{resolved:false,comment:''}};
  _resolutions[el.dataset.yaml].comment=el.value;
  scheduleSave();
}}
function scheduleSave(){{
  clearTimeout(_saveTimer);
  setSaveStatus('⏳ Guardando...');
  _saveTimer=setTimeout(saveResolutions,800);
}}
async function saveResolutions(){{
  if(!_binId)return;
  try{{
    var res=await fetch('https://api.jsonbin.io/v3/b/'+_binId,
      {{method:'PUT',headers:{{'X-Master-Key':_binKey,'Content-Type':'application/json','X-Bin-Versioning':'false'}},
        body:JSON.stringify(_resolutions)}});
    if(res.ok){{
      setSaveStatus('✅ Guardado');
      setTimeout(function(){{setSaveStatus('');}},2000);
    }}else{{setSaveStatus('⚠️ Error al guardar');}}
  }}catch(e){{setSaveStatus('⚠️ Sin conexión');}}
}}
function setSaveStatus(msg){{var el=document.getElementById('save-status');if(el)el.textContent=msg;}}
function copySlack(){{
  var pending=_failLabels.filter(function(l,i){{return !(_resolutions[_failYamls[i]]&&_resolutions[_failYamls[i]].resolved);}});
  var lines=[_headerText,''];
  if(pending.length){{lines.push('*Lo que no funciona ❌ ('+pending.length+')*');pending.forEach(function(l){{lines.push('  • '+l);}});}}
  lines.push(_footerText);
  var text=lines.join('\\n');
  navigator.clipboard.writeText(text).then(function(){{
    var b=document.querySelector('#slack-card button');
    b.textContent='✅ Copiado';setTimeout(function(){{b.textContent='📋 Copiar';}},2000);
  }});
}}
window.addEventListener('DOMContentLoaded',loadResolutions);
</script>"""

HTML_DIR.mkdir(parents=True, exist_ok=True)

html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>APP QA — {escape(client_cap)} — {date_str}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow:wght@700;800&family=Lato:wght@400;700&display=swap" rel="stylesheet">
<style>
:root{{--green:#00A76F;--green-lt:#C8FAD6;--green-dk:#007867;--amber:#FFAB00;--amber-lt:#FFF5CC;--red:#FF5630;--red-lt:#FFE9D5;--bg:#F4F6F8;--surface:#fff;--border:#E0E5EA;--text:#161C24;--dim:#637381;--faint:#919EAB}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Lato',sans-serif;background:var(--bg);padding:0 0 40px;color:var(--text)}}
h1,h2,.card-title,.stat-label,.stat-value{{font-family:'Barlow',sans-serif}}
.container{{max-width:1100px;margin:0 auto;padding:0 24px}}
.site-header{{background:var(--surface);border-bottom:1px solid var(--border);padding:14px 24px;margin-bottom:24px;display:flex;align-items:center;gap:16px}}
.back-link{{color:var(--green);text-decoration:none;font-size:.88em;font-weight:700}}
.back-link:hover{{text-decoration:underline}}
.site-header h1{{font-size:1.2em;font-weight:700;color:var(--text)}}
.site-header p{{font-size:.85em;color:var(--dim)}}
.partial-banner{{background:var(--amber-lt);border:1px solid var(--amber);border-radius:8px;padding:10px 16px;font-size:.85em;color:#7A4100;margin-bottom:16px;font-weight:500}}
.card{{background:var(--surface);border-radius:14px;padding:24px;margin-bottom:16px;box-shadow:0 1px 2px rgba(0,0,0,.05),0 4px 14px rgba(0,0,0,.07)}}
.card-title{{font-size:1em;font-weight:700;color:var(--text);margin-bottom:16px;padding-bottom:10px;border-bottom:1.5px solid var(--border)}}
.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(100px,1fr));gap:10px;margin-bottom:20px}}
.stat{{padding:14px;border-radius:10px;text-align:center;color:#fff}}
.stat.blue{{background:linear-gradient(135deg,var(--green),var(--green-dk))}}
.stat.green{{background:linear-gradient(135deg,var(--green),var(--green-dk))}}
.stat.red{{background:linear-gradient(135deg,var(--red),#B71D18)}}
.stat.amber{{background:linear-gradient(135deg,var(--amber),#B76E00)}}
.stat.gray{{background:linear-gradient(135deg,#919EAB,#637381)}}
.stat-value{{font-size:1.6em;font-weight:800;line-height:1}}
.stat-label{{font-size:.68em;opacity:.9;font-weight:700;margin-top:4px}}
.verdict-badge{{display:inline-block;padding:6px 18px;border-radius:99px;font-weight:700;font-size:.9em;margin-bottom:14px;font-family:'Barlow',sans-serif}}
.verdict-listo{{background:var(--green-lt);color:var(--green-dk)}}
.verdict-condiciones{{background:var(--amber-lt);color:#7A4100}}
.verdict-bloqueado{{background:var(--red-lt);color:#7A0916}}
.health-meta{{display:flex;justify-content:space-between;font-size:.82em;color:var(--dim);font-weight:600;margin-bottom:5px}}
.health-meta strong{{color:var(--text)}}
.health-track{{height:10px;background:var(--bg);border-radius:99px;overflow:hidden}}
.health-fill{{height:100%;border-radius:99px;background:{health_color}}}
.linear-btn{{display:inline-block;margin-left:6px;padding:2px 8px;background:var(--green);color:#fff;border-radius:5px;font-size:.72em;font-weight:700;text-decoration:none;vertical-align:middle}}
.table-wrap{{overflow-x:auto;-webkit-overflow-scrolling:touch}}
table{{width:100%;border-collapse:collapse;table-layout:fixed}}
th{{background:var(--bg);text-align:left;padding:10px 14px;font-size:.75em;color:var(--dim);font-weight:700;text-transform:uppercase;letter-spacing:.05em;border-bottom:1.5px solid var(--border);white-space:nowrap;font-family:'Barlow',sans-serif}}
td{{padding:10px 14px;border-bottom:1px solid var(--border);font-size:.88em;vertical-align:top;word-break:break-word;overflow-wrap:anywhere}}
tr:last-child td{{border-bottom:none}}
tr:hover td{{background:#FAFBFC}}
tr.batch-header td{{background:#EEF2F6;color:var(--dim);font-size:.75em;font-weight:700;text-transform:uppercase;letter-spacing:.05em;padding:7px 14px;border-bottom:1.5px solid var(--border);font-family:'Barlow',sans-serif}}
.badge{{padding:2px 10px;border-radius:99px;font-size:.75em;font-weight:700}}
.badge.pass{{background:var(--green-lt);color:var(--green-dk)}}
.badge.manual{{background:#EFD6FF;color:#5119B7}}
.badge.skip{{background:var(--bg);color:var(--dim)}}
.badge.fail{{background:var(--red-lt);color:#7A0916}}
.badge.fixed{{background:#CAFDF5;color:#006C9C;margin-right:4px}}
.badge.fixed-fail{{background:var(--amber-lt);color:#7A4100}}
.flow-error{{font-size:.8em;color:var(--faint);margin-top:3px;font-style:italic}}
.flow-icon{{margin-right:4px}}
.chk-details{{margin-top:6px;font-size:.8em}}
.chk-details summary{{cursor:pointer;color:var(--green);font-weight:700}}
.chk-table{{width:100%;margin-top:6px;border-collapse:collapse}}
.chk-table td,.chk-table th{{padding:3px 8px;border-bottom:1px solid var(--border);font-size:.8em}}
.chk-section{{background:var(--bg);color:var(--dim);font-weight:700;padding:5px 8px}}
.chk-icon{{width:24px;text-align:center}}
.chk-config{{color:var(--faint);font-style:italic}}
.duration{{color:var(--faint);white-space:nowrap}}
footer{{color:var(--faint);font-size:.82em;text-align:center;margin-top:24px}}
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
    <div class="stat red"><div class="stat-value">{real_failed}</div><div class="stat-label">FAIL</div></div>
    <div class="stat" style="background:linear-gradient(135deg,#ca8a04,#a16207)"><div class="stat-value">{fixed_count}</div><div class="stat-label">FIXED</div></div>
    <div class="stat amber"><div class="stat-value">{health}%</div><div class="stat-label">Health</div></div>
  </div>
  <div>
    <div class="health-meta"><span>Health score</span><strong>{health}%</strong></div>
    <div class="health-track"><div class="health-fill" style="width:{health}%"></div></div>
  </div>
</div>
{slack_card}
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
