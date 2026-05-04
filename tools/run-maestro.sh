#!/bin/bash
# Corre todos los flows Maestro para un cliente y genera reporte en el dashboard QA
# Uso: ./tools/run-maestro.sh <cliente> [--skip-to <flow>] [--interactive]
# Ejemplos:
#   ./tools/run-maestro.sh prinorte
#   ./tools/run-maestro.sh prinorte --skip-to 04-filtros
#   ./tools/run-maestro.sh prinorte --interactive
#
# --skip-to: salta todos los flows hasta encontrar el nombre indicado
# --interactive: pregunta qué hacer cuando un flow falla (m=manual-pass, r=reintentar, s=skip)

set -euo pipefail

# ── Config ────────────────────────────────────────────────────
CLIENTE="${1:-}"
if [ -z "$CLIENTE" ]; then
    echo "Uso: ./tools/run-maestro.sh <cliente> [--skip-to <flow>] [--interactive] [--env staging|production]"
    echo "Ejemplo: ./tools/run-maestro.sh prinorte --env production"
    exit 1
fi

# Parsear flags opcionales (a partir del arg 2)
SKIP_TO=""
INTERACTIVE="0"
ENVIRONMENT="production"   # default: production (APP corre en dispositivo real)
i=2
while [ $i -le $# ]; do
    arg="${!i}"
    case "$arg" in
        --skip-to)
            i=$((i+1))
            SKIP_TO="${!i:-}"
            ;;
        --interactive)
            INTERACTIVE="1"
            ;;
        --env)
            i=$((i+1))
            ENVIRONMENT="${!i:-production}"
            ;;
    esac
    i=$((i+1))
done

DATE=$(date +%Y-%m-%d)
QA_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$QA_ROOT/tests/app/config/env.${CLIENTE}.yaml"
CONFIG_FILE="$QA_ROOT/tests/app/config/config.${CLIENTE}.yaml"
FLOWS_DIR="$QA_ROOT/tests/app/flows"
CLIENTE_CAP=$(python3 -c "print('${CLIENTE}'.capitalize())")
OUTPUT_DIR="$QA_ROOT/QA/${CLIENTE_CAP}/${DATE}"
HTML_DIR="$QA_ROOT/public/qa/app-reports"
MANIFEST_FILE="$QA_ROOT/public/qa/manifest.json"
REPORT_FILE="${CLIENTE}-${DATE}.html"
REPORT_PATH="$HTML_DIR/${REPORT_FILE}"
RAW_LOG="${OUTPUT_DIR}/maestro.log"

# ── Validaciones ──────────────────────────────────────────────
if [ ! -f "$ENV_FILE" ] && [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Config file no encontrado"
    echo "   Esperado: tests/app/config/env.${CLIENTE}.yaml"
    echo "   o:        tests/app/config/config.${CLIENTE}.yaml"
    exit 1
fi

SESSION_FILE="$FLOWS_DIR/${CLIENTE}-session.yaml"
if [ -f "$SESSION_FILE" ]; then
    FLOW_COUNT=1
    FLOW_DESC="session"
else
    FLOW_COUNT=$(ls "$FLOWS_DIR"/${CLIENTE}-[0-9]*.yaml 2>/dev/null | wc -l | tr -d ' ')
    FLOW_DESC="flows individuales"
fi
if [ "$FLOW_COUNT" -eq 0 ]; then
    echo "❌ No hay flows para: $CLIENTE"
    echo "   Esperado: tests/app/flows/${CLIENTE}-session.yaml"
    exit 1
fi

# ── Maestro version check ─────────────────────────────────────
MAESTRO_MIN_VERSION="1.40.0"
if command -v maestro &>/dev/null; then
    MAESTRO_VERSION=$(maestro --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1 || echo "0.0.0")
    if [ "$(printf '%s\n' "$MAESTRO_MIN_VERSION" "$MAESTRO_VERSION" | sort -V | head -1)" != "$MAESTRO_MIN_VERSION" ]; then
        echo "⚠️  Maestro $MAESTRO_VERSION < mínimo requerido $MAESTRO_MIN_VERSION — actualizar con: brew upgrade maestro"
        exit 1
    fi
else
    echo "❌ Maestro no encontrado — instalar con: brew install maestro"
    exit 1
fi

# ── Setup Java/ADB ────────────────────────────────────────────
JAVA_PREFIX=$(brew --prefix openjdk@17 2>/dev/null || true)
[ -n "$JAVA_PREFIX" ] && export JAVA_HOME="$JAVA_PREFIX" && export PATH="$JAVA_HOME/bin:$PATH"
export PATH="$HOME/Library/Android/sdk/platform-tools:$PATH"

mkdir -p "$OUTPUT_DIR" "$HTML_DIR"

echo "📱 Maestro QA — ${CLIENTE_CAP} — ${DATE}"
echo "   ${FLOW_COUNT} ${FLOW_DESC} encontrado(s)"
[ -n "$SKIP_TO" ] && echo "   ⏭ Saltando hasta: ${SKIP_TO}"
[ "$INTERACTIVE" = "1" ] && echo "   👤 Modo interactivo activo"
echo ""

# ── Verificar dispositivo ─────────────────────────────────────
if ! adb devices 2>/dev/null | grep -q "device$"; then
    echo "❌ No hay dispositivo Android conectado"
    echo "   Conecta el celu con USB debugging activado"
    exit 1
fi

# ── Correr flows ──────────────────────────────────────────────
echo "▶ Iniciando flows (máx 3 intentos automáticos + opción manual)..."
python3 - "$ENV_FILE" "$FLOWS_DIR" "$CLIENTE" "$RAW_LOG" "$CONFIG_FILE" "$INTERACTIVE" "$SKIP_TO" <<'PYEOF'
import sys, yaml, subprocess, os, glob, re, select

env_file    = sys.argv[1]
flows_dir   = sys.argv[2]
cliente     = sys.argv[3]
log_file    = sys.argv[4]
config_file = sys.argv[5]
interactive = len(sys.argv) > 6 and sys.argv[6] == '1'
skip_to     = sys.argv[7] if len(sys.argv) > 7 else ''

# ── Construir comando base ────────────────────────────────────
# Si existe config.{cliente}.yaml → leer su sección env: (solo vars usadas en los flows)
# Si no → inyectar todas las vars de env.{cliente}.yaml como --env (modo legacy)
base_cmd = ['maestro', 'test']
if os.path.exists(config_file):
    with open(config_file) as f:
        config_data = yaml.safe_load(f) or {}
    env_vars = config_data.get('env', {})
    print(f"  ⚙  Config: {os.path.basename(config_file)} ({len(env_vars)} vars)")
else:
    with open(env_file) as f:
        env_vars = yaml.safe_load(f) or {}
    print(f"  ⚙  Env: {os.path.basename(env_file)} ({len(env_vars)} vars)")

for k, v in env_vars.items():
    if v is not None and str(k).strip():
        base_cmd.extend(['--env', f'{k}={v}'])

# ── TTY para modo interactivo ─────────────────────────────────
tty = None
if interactive:
    try:
        tty = open('/dev/tty', 'r')
    except Exception:
        print("  ⚠  No se pudo abrir /dev/tty — modo interactivo desactivado")
        interactive = False

# ── Lista de flows ────────────────────────────────────────────
session = os.path.join(flows_dir, f'{cliente}-session.yaml')
flows = [session] if os.path.exists(session) else sorted(
    glob.glob(os.path.join(flows_dir, f'{cliente}-[0-9]*.yaml'))
)

log_lines = []
skipping = bool(skip_to)

for flow_path in flows:
    # Nombre legible desde campo name: del YAML
    flow_name = os.path.splitext(os.path.basename(flow_path))[0]
    try:
        with open(flow_path) as f:
            flow_yaml = yaml.safe_load(f)
            if isinstance(flow_yaml, dict) and flow_yaml.get('name'):
                flow_name = flow_yaml['name']
    except Exception:
        pass

    # Lógica --skip-to
    if skipping:
        if skip_to in os.path.basename(flow_path):
            skipping = False
        else:
            print(f"  ⏭  Saltando: {flow_name}")
            log_lines.append(f'[Skipped] {flow_name} (-)')
            continue

    print(f"\n{'─'*50}")
    print(f"▶ {flow_name}")

    passed = False
    last_output = ''
    last_error = 'Error desconocido'

    # Reintentos: 1 para session flows (clearState+launchApp hace que reiniciar sea muy costoso)
    # 3 para flows individuales (flakiness de UI tolerable)
    is_session = cliente + '-session' in os.path.basename(flow_path)
    max_attempts = 1 if is_session else 3

    for attempt in range(1, max_attempts + 1):
        proc = subprocess.Popen(
            base_cmd + [flow_path],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        output_lines = []
        for line in proc.stdout:
            print(line, end='', flush=True)
            output_lines.append(line)
        proc.wait()
        last_output = ''.join(output_lines)

        if proc.returncode == 0:
            passed = True
            break
        else:
            non_empty = [l for l in last_output.splitlines() if l.strip()]
            last_error = ' | '.join(non_empty[-3:]) if non_empty else 'Error desconocido'
            if attempt < max_attempts:
                print(f"  ↺ Intento {attempt}/{max_attempts} fallido — reintentando...")
            else:
                print(f"  ✗ {max_attempts} intento(s) fallido(s)")

    # ── Intervención humana ───────────────────────────────────
    manual = False
    if not passed and interactive and tty:
        flow_short = flow_name[:30]
        print(f"\n╔{'═'*48}╗")
        print(f"║  Flow FALLÓ: {flow_short:<36}║")
        print(f"║  Revisa el device. ¿Funciona visualmente?  ║")
        print(f"║  [m] Manual-Pass   [r] Reintentar   [s] Skip║")
        print(f"╚{'═'*48}╝")
        print("Respuesta (30s → auto-skip): ", end='', flush=True)

        rlist, _, _ = select.select([tty], [], [], 30)
        if rlist:
            choice = tty.readline().strip().lower()[:1]
        else:
            choice = 's'
            print('s (timeout)')

        if choice == 'm':
            manual = True
            print(f"  👤 Marcado como MANUAL-PASS")
        elif choice == 'r':
            print(f"  ↺ Reintento manual...")
            proc = subprocess.Popen(
                base_cmd + [flow_path],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
            )
            output_lines = []
            for line in proc.stdout:
                print(line, end='', flush=True)
                output_lines.append(line)
            proc.wait()
            last_output = ''.join(output_lines)
            if proc.returncode == 0:
                passed = True
                print(f"  ✅ Reintento exitoso")
            else:
                print(f"  ✗ Reintento manual también falló — marcando FAILED")
        else:
            print(f"  ⏭ Skip — marcando FAILED")

    # ── Extraer duración del output ───────────────────────────
    dur_match = re.search(r'(\d+s \d+ms|\d+\.\d+s|\d+ms)', last_output)
    duration = dur_match.group(1) if dur_match else '?'

    if passed:
        log_lines.append(f'[Passed] {flow_name} ({duration})')
    elif manual:
        log_lines.append(f'[Manual-Pass] {flow_name} ({duration})')
    else:
        error_clean = last_error.replace('\n', ' ').replace('\r', '')[:120]
        log_lines.append(f'[Failed] {flow_name} ({duration}) ({error_clean})')

if tty:
    tty.close()

combined_log = '\n'.join(log_lines)
print(f"\n{'─'*50}")
print(combined_log)
with open(log_file, 'w') as f:
    f.write(combined_log + '\n')
PYEOF

echo ""

# ── Generar reporte HTML + actualizar manifest ────────────────
python3 - "$CLIENTE_CAP" "$CLIENTE" "$DATE" "$RAW_LOG" "$REPORT_PATH" "$MANIFEST_FILE" "$REPORT_FILE" "$ENVIRONMENT" <<'PYEOF'
import sys, re, json, os
from datetime import datetime
from html import escape
from urllib.parse import quote

client_cap    = sys.argv[1]
client_slug   = sys.argv[2]
date_str      = sys.argv[3]
log_file      = sys.argv[4]
report_path   = sys.argv[5]
manifest_file = sys.argv[6]
report_file   = sys.argv[7]
environment   = sys.argv[8] if len(sys.argv) > 8 else 'production'

# ── Parsear log ───────────────────────────────────────────────
with open(log_file) as f:
    lines = f.read().splitlines()

flows = []
for line in lines:
    m = re.match(r'\[(Passed|Failed|Manual-Pass|Skipped)\]\s+(.+?)\s+\(([^)]*)\)(?:\s+\((.+)\))?', line.strip())
    if m:
        flows.append({
            'name':     m.group(2),
            'status':   m.group(1).lower().replace('-', '_'),
            'duration': m.group(3),
            'error':    m.group(4) or '',
        })

passed      = sum(1 for f in flows if f['status'] == 'passed')
manual      = sum(1 for f in flows if f['status'] == 'manual_pass')
failed      = sum(1 for f in flows if f['status'] == 'failed')
skipped     = sum(1 for f in flows if f['status'] == 'skipped')
total       = len(flows)
effective   = total - skipped
health      = round((passed + manual) / effective * 100) if effective > 0 else 0

health_color = '#10b981' if health >= 80 else '#f59e0b' if health >= 60 else '#ef4444'
verdict      = 'LISTO' if health == 100 else 'CON OBSERVACIONES' if health >= 70 else 'BLOQUEADO'
verdict_cls  = 'listo' if health == 100 else 'condiciones' if health >= 70 else 'bloqueado'

# ── Filas de la tabla ─────────────────────────────────────────
rows = ''
for f in flows:
    s = f['status']
    if s == 'passed':
        icon, badge_cls, label = '✅', 'pass', 'PASSED'
    elif s == 'manual_pass':
        icon, badge_cls, label = '👤', 'manual', 'MANUAL-PASS'
    elif s == 'skipped':
        icon, badge_cls, label = '⏭', 'skip', 'SKIPPED'
    else:
        icon, badge_cls, label = '❌', 'fail', 'FAILED'
    err_html = f'<div class="flow-error">{escape(f["error"])}</div>' if f['error'] else ''
    row_linear = ''
    if s == 'failed':
        flt = quote(f'fix(app): {client_cap} — {f["name"]} ({date_str})')
        fld_parts = [f'## Flow fallido — APP Maestro\n\nCliente: {client_cap}  |  Fecha: {date_str}']
        fld_parts.append(f'Flow: {f["name"]}')
        if f['error']:
            fld_parts.append(f'Error: {f["error"]}')
        fld_parts.append('\n---\n_Generado automáticamente por QA Dashboard — YOM APP_')
        fld = quote('\n'.join(fld_parts))
        row_linear = f'<a href="https://linear.app/yom-tech/new?title={flt}&description={fld}" target="_blank" style="display:inline-block;margin-top:4px;padding:2px 8px;background:#4f6ef7;color:white;border-radius:5px;font-size:0.72em;font-weight:600;text-decoration:none;">🔗 Ticket</a>'
    rows += f"""
        <tr>
            <td><span class="flow-icon">{icon}</span> {escape(f['name'])}{err_html}</td>
            <td><span class="badge {badge_cls}">{label}</span>{row_linear}</td>
            <td class="duration">{escape(f['duration'])}</td>
        </tr>"""

# ── Estadísticas adicionales ──────────────────────────────────
manual_note = f' <span style="color:#6b7280;font-size:0.8em">(incl. {manual} manual)</span>' if manual else ''
skip_note   = f' <span style="color:#6b7280;font-size:0.8em">({skipped} saltados)</span>' if skipped else ''
generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

# ── Linear ticket link (always shown) ────────────────────────────────────
lt = quote(f'fix(app): {client_cap} — {verdict} ({passed+manual}/{total} flows, {date_str})')
ld = quote(f'## APP QA — Maestro\n\nCliente: {client_cap}  |  Fecha: {date_str}\nHealth: {health}/100  |  Flows: {passed+manual}/{total}  |  Veredicto: {verdict}\n\n## Acción requerida\n\nRevisar reporte Maestro de {date_str} para cliente {client_cap}.\n\n---\n_Generado automáticamente por QA Dashboard — YOM APP_')
linear_btn = f'<a href="https://linear.app/yom-tech/new?title={lt}&description={ld}" target="_blank" style="display:inline-block;margin-top:12px;padding:7px 16px;background:#4f6ef7;color:white;border-radius:8px;text-decoration:none;font-size:0.85em;font-weight:600;">🔗 Crear ticket en Linear</a>'

# ── HTML ──────────────────────────────────────────────────────
html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>APP QA — {escape(client_cap)} — {date_str}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f8f9fb;
            min-height: 100vh; padding: 0 0 40px;
        }}
        .container {{ max-width: 1100px; margin: 0 auto; padding: 0 24px; }}
        .site-header {{ background: #ffffff; border-bottom: 1px solid #e2e5e9; padding: 14px 24px; margin-bottom: 28px; display: flex; align-items: center; gap: 16px; }}
        .back-link {{ color: #4f6ef7; text-decoration: none; font-size: 0.88em; font-weight: 600; }}
        .back-link:hover {{ text-decoration: underline; }}
        .site-header h1 {{ font-size: 1.25em; font-weight: 700; color: #1a1d23; margin: 0; }}
        .site-header p {{ font-size: 0.85em; color: #64748b; margin: 0; }}
        .card {{ background: white; border-radius: 12px; padding: 24px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 4px 12px rgba(0,0,0,0.06); }}
        .card-title {{ font-size: 1em; font-weight: 700; color: #111827; margin-bottom: 16px; padding-bottom: 10px; border-bottom: 1.5px solid #e5e7eb; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(110px, 1fr)); gap: 10px; margin-bottom: 20px; }}
        .stat {{ background: linear-gradient(135deg, #4f6ef7, #3b5bdb); color: white; padding: 14px; border-radius: 10px; text-align: center; }}
        .stat.green  {{ background: linear-gradient(135deg, #10b981, #059669); }}
        .stat.red    {{ background: linear-gradient(135deg, #ef4444, #dc2626); }}
        .stat.amber  {{ background: linear-gradient(135deg, #f59e0b, #d97706); }}
        .stat.blue   {{ background: linear-gradient(135deg, #3b82f6, #2563eb); }}
        .stat.gray   {{ background: linear-gradient(135deg, #9ca3af, #6b7280); }}
        .stat-value {{ font-size: 1.6em; font-weight: 800; line-height: 1; }}
        .stat-label {{ font-size: 0.68em; opacity: 0.9; font-weight: 600; margin-top: 4px; }}
        .verdict-badge {{ display: inline-block; padding: 6px 18px; border-radius: 99px; font-weight: 700; font-size: 0.9em; margin-bottom: 18px; }}
        .verdict-listo      {{ background: #d1fae5; color: #065f46; }}
        .verdict-condiciones {{ background: #fef3c7; color: #92400e; }}
        .verdict-bloqueado  {{ background: #fee2e2; color: #991b1b; }}
        .health-bar {{ margin-bottom: 8px; }}
        .health-meta {{ display: flex; justify-content: space-between; font-size: 0.82em; color: #6b7280; font-weight: 600; margin-bottom: 5px; }}
        .health-meta strong {{ color: #111827; }}
        .health-track {{ height: 10px; background: #f3f4f6; border-radius: 99px; overflow: hidden; }}
        .health-fill {{ height: 100%; border-radius: 99px; background: {health_color}; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th {{ background: #f9fafb; text-align: left; padding: 10px 14px; font-size: 0.78em; color: #6b7280; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; border-bottom: 1.5px solid #e5e7eb; }}
        td {{ padding: 10px 14px; border-bottom: 1px solid #f3f4f6; font-size: 0.88em; vertical-align: top; }}
        tr:last-child td {{ border-bottom: none; }}
        .badge {{ padding: 2px 10px; border-radius: 99px; font-size: 0.75em; font-weight: 700; }}
        .badge.pass   {{ background: #d1fae5; color: #065f46; }}
        .badge.manual {{ background: #dbeafe; color: #1e40af; }}
        .badge.warn   {{ background: #fef3c7; color: #92400e; }}
        .badge.skip   {{ background: #f3f4f6; color: #6b7280; }}
        .badge.fail   {{ background: #fee2e2; color: #991b1b; }}
        .flow-error {{ font-size: 0.8em; color: #9ca3af; margin-top: 3px; font-style: italic; }}
        .duration {{ color: #9ca3af; white-space: nowrap; }}
        footer {{ color: #9ca3af; font-size: 0.82em; text-align: center; margin-top: 24px; }}
    </style>
</head>
<body>
<div class="site-header">
    <a href="../" class="back-link">← Dashboard principal</a>
    <div>
        <h1>📱 APP QA — {escape(client_cap)}</h1>
        <p>Maestro flows · {date_str}</p>
    </div>
</div>
<div class="container">

    <div class="card">
        <div class="card-title">Resumen</div>
        <span class="verdict-badge verdict-{verdict_cls}">{verdict}</span>
        {linear_btn}
        <div class="stats">
            <div class="stat"><div class="stat-value">{total}</div><div class="stat-label">Total flows</div></div>
            <div class="stat green"><div class="stat-value">{passed}</div><div class="stat-label">Auto-Pass</div></div>
            <div class="stat blue"><div class="stat-value">{manual}</div><div class="stat-label">Manual-Pass</div></div>
            <div class="stat red"><div class="stat-value">{failed}</div><div class="stat-label">Failed</div></div>
            <div class="stat amber"><div class="stat-value">{health}%</div><div class="stat-label">Health{'' if not skipped else f' ({skipped} skip)'}</div></div>
        </div>
        <div class="health-bar">
            <div class="health-meta">
                <span>Health score{manual_note}{skip_note}</span>
                <strong>{health}%</strong>
            </div>
            <div class="health-track"><div class="health-fill" style="width:{health}%"></div></div>
        </div>
    </div>

    <div class="card">
        <div class="card-title">Detalle por flow</div>
        <table>
            <thead><tr><th>Flow</th><th>Estado</th><th>Duración</th></tr></thead>
            <tbody>{rows}</tbody>
        </table>
    </div>

    <footer>Generado {generated_at} · Maestro + YOM QA · 👤 Manual-Pass = tester confirmó visualmente</footer>
</div>
<script>
(function(){{
  const h1 = document.querySelector('h1');
  const client = h1 ? h1.textContent.replace('📱 APP QA — ','') : '';
  const pEl = document.querySelector('.site-header p, header p');
  const parts = pEl ? pEl.textContent.split('·') : [];
  const date = parts[parts.length-1]?.trim() || '';
  function makeBtn(lt, ld){{
    const a = document.createElement('a');
    a.href = 'https://linear.app/yom-tech/new?title='+encodeURIComponent(lt)+'&description='+encodeURIComponent(ld);
    a.target = '_blank';
    a.style.cssText = 'display:inline-block;margin-left:8px;margin-top:3px;padding:2px 9px;background:#4f6ef7;color:white;border-radius:5px;font-size:.72em;font-weight:600;text-decoration:none;vertical-align:middle;';
    a.textContent = '🔗 Ticket';
    return a;
  }}
  // Badge fail/warn cells (MongoDB BUG CONFIG, PASS+WARN, etc.)
  document.querySelectorAll('.badge.fail, .badge.warn').forEach(function(b){{
    if (b.closest('a')) return;
    const txt = b.textContent.trim();
    const cell = b.parentNode;
    if (cell.querySelector('a[href*="linear"]')) return;
    const lt = 'fix(app): '+client+' — '+txt.slice(0,80)+' ('+date+')';
    const ld = '## Hallazgo APP\n\nCliente: '+client+'  |  Fecha: '+date+'\nHallazgo: '+txt+'\nContexto: '+cell.closest('tr')?.cells[0]?.textContent.trim().slice(0,120)+'\n\n---\n_Generado desde QA Dashboard — YOM APP_';
    cell.appendChild(makeBtn(lt, ld));
  }});
  // P2/P3 hallazgo rows
  document.querySelectorAll('.p2, .p3').forEach(function(p){{
    const row = p.closest('tr');
    if (!row) return;
    const descCell = row.cells[1];
    if (!descCell || descCell.querySelector('a[href*="linear"]')) return;
    const title = descCell.querySelector('strong')?.textContent || descCell.textContent.trim().slice(0,80);
    const lt = 'fix(app): '+client+' — '+title.slice(0,80)+' ('+date+')';
    const ld = '## Hallazgo APP\n\nCliente: '+client+'  |  Fecha: '+date+'\nPrioridad: '+p.textContent+'\nDescripción: '+descCell.textContent.trim().slice(0,300)+'\n\n---\n_Generado desde QA Dashboard — YOM APP_';
    descCell.appendChild(makeBtn(lt, ld));
  }});
}})();
</script>
</body>
</html>"""

with open(report_path, 'w') as f:
    f.write(html)

# ── Actualizar manifest ───────────────────────────────────────
manifest = {'reports': []}
if os.path.exists(manifest_file):
    try:
        with open(manifest_file) as f:
            manifest = json.load(f)
    except Exception:
        pass

manifest['reports'] = [
    r for r in manifest.get('reports', [])
    if not (r.get('client_slug') == client_slug and r.get('date') == date_str)
]
# ── Leer sync metrics del QA matrix (si existe) ──────────────
sync_warnings = []
qa_root = os.path.dirname(os.path.dirname(os.path.abspath(manifest_file)))
matrix_candidates = [
    os.path.join(qa_root, 'data', f'qa-matrix-staging-{client_slug}.json'),
    os.path.join(qa_root, 'data', f'qa-matrix-staging.json'),
    os.path.join(qa_root, 'data', 'qa-matrix.json'),
]
for matrix_path in matrix_candidates:
    if os.path.exists(matrix_path):
        try:
            with open(matrix_path) as f:
                matrix = json.load(f)
            # Find client by slug (try exact key first, then partial match)
            clients = matrix.get('clients', {})
            client_data = clients.get(client_slug) or clients.get(f'{client_slug}-staging')
            if not client_data:
                for k, v in clients.items():
                    if client_slug in k:
                        client_data = v
                        break
            if client_data:
                sync_metrics = client_data.get('syncMetrics', [])
                sync_warnings = [m for m in sync_metrics if m.get('slow') or not m.get('successful')]
        except Exception:
            pass
        break

manifest['reports'].append({
    'client':        client_cap,
    'client_slug':   client_slug,
    'date':          date_str,
    'file':          f'app-reports/{report_file}',
    'platform':      'app',
    'environment':   environment,
    'passed':        passed,
    'manual':        manual,
    'failed':        failed,
    'skipped':       skipped,
    'total':         total,
    'health':        health,
    'verdict':       verdict,
    'syncWarnings':  sync_warnings,
})
manifest['reports'].sort(key=lambda x: x['date'], reverse=True)

with open(manifest_file, 'w') as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

print(f"✅  Reporte: public/qa/app-reports/{report_file}")
print(f"📊  {passed}✅ {manual}👤 {failed}❌ {skipped}⏭ · Health {health}% · {verdict}")
PYEOF

echo ""
echo "🌐 Dashboard: abre public/qa/index.html"
