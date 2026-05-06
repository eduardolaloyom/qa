#!/usr/bin/env python3
"""
Extrae datos de sync de un logcat capturado durante un run Maestro.
Busca el POST a sync-use-info que la app YOM envía al final de cada syncAll.

Uso:
    python3 tools/parse-sync-logcat.py <logcat_file> <output_json>

Ejemplo:
    python3 tools/parse-sync-logcat.py /tmp/logcat-batch1.txt QA/Caren/2026-05-06/sync-data.json
"""

import sys, json, re
from pathlib import Path

logcat_path = sys.argv[1] if len(sys.argv) > 1 else ""
output_path = sys.argv[2] if len(sys.argv) > 2 else ""

if not logcat_path or not output_path:
    print("Uso: parse-sync-logcat.py <logcat> <output.json>")
    sys.exit(1)

text = Path(logcat_path).read_text(errors="replace")

# Buscar líneas que contengan el body del POST a sync-use-info
# OkHttp loguea: "--> POST https://.../sync-use-info" seguido del body JSON
syncs = []
lines = text.splitlines()

for i, line in enumerate(lines):
    if "sync-use-info" in line and "-->" in line:
        # La siguiente línea no vacía contiene el body JSON
        for j in range(i + 1, min(i + 5, len(lines))):
            candidate = lines[j].strip()
            # Extraer solo el JSON (después del prefijo de logcat)
            m = re.search(r'(\{.+\})\s*$', candidate)
            if m:
                try:
                    data = json.loads(m.group(1))
                    if data.get("actionType") == "syncAll":
                        syncs.append(data)
                except Exception:
                    pass
                break

if not syncs:
    print("⚠  No se encontró sync-use-info en el logcat")
    sys.exit(0)

# Tomar el último sync (el más reciente del run)
sync = syncs[-1]
childs = sync.get("syncChilds", [])

total_seconds = sum(c.get("syncTimeSeconds", 0) for c in childs)
successful    = sync.get("successful", False)

summary = {
    "capturedAt":    None,
    "totalSeconds":  round(total_seconds, 2),
    "successful":    successful,
    "appVersion":    sync.get("appVersion", ""),
    "deviceModel":   sync.get("deviceModel", ""),
    "freeRam":       sync.get("freeRam", ""),
    "freeRamPct":    sync.get("freeRamPercentage", ""),
    "actions": [
        {
            "type":     c.get("actionType"),
            "docs":     c.get("documentsCount", 0),
            "requests": c.get("requests", 0),
            "seconds":  round(c.get("syncTimeSeconds", 0), 3),
            "ok":       c.get("successful", False),
        }
        for c in childs
    ],
}

# Intentar extraer timestamp del logcat
m = re.search(r'^(\d{2}-\d{2} \d{2}:\d{2}:\d{2})', lines[0] if lines else "")
if m:
    summary["capturedAt"] = m.group(1)

Path(output_path).parent.mkdir(parents=True, exist_ok=True)
Path(output_path).write_text(json.dumps(summary, indent=2, ensure_ascii=False))

status = "✅" if successful else "⚠ (sub-syncs sin config)"
print(f"{status} Sync: {total_seconds:.1f}s · {len(childs)} acciones · {sum(1 for c in childs if not c.get('successful'))} fallidas")
print(f"→ {output_path}")
