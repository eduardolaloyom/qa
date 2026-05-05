#!/usr/bin/env python3
"""
Genera tests/app/flows/{cliente}/04-features.yaml basándose en
los valores reales de qa-matrix-staging.json (o qa-matrix.json para prod).

Uso:
    python3 tools/gen-maestro-features.py caren
    python3 tools/gen-maestro-features.py caren --env production
    python3 tools/gen-maestro-features.py caren --dry-run

El script:
1. Lee qa-matrix-staging.json (o qa-matrix.json con --env production)
2. Extrae las variables de feature flags del cliente
3. Genera 04-features.yaml con assertNotVisible/assertVisible ESTRICTOS
   (sin optional: true) solo cuando la flag está OFF
4. Escribe el archivo en tests/app/flows/{cliente}/04-features.yaml
"""

import sys
import json
import argparse
from pathlib import Path

# ── Feature flags mapeados a assertions Maestro ──────────────────────────────
# Formato: flag_name → { "off_label": texto a verificar cuando OFF, "on_label": texto cuando ON }
FEATURE_MAP = {
    # enableCreateCommerce: false → no debe haber botón Crear Comercio
    "commerce.enableCreateCommerce": {
        "off_check": "assertNotVisible",
        "off_text": r".*[Cc]rear [Cc]omercio.*|.*[Nn]uevo [Cc]omercio.*|.*[Aa]gregar [Cc]omercio.*",
        "on_check": "assertVisible",
        "on_text": r".*[Cc]rear [Cc]omercio.*|Crear comercio",
        "context": "lista de comercios",
        "description": "Botón 'Crear Comercio'",
    },
    # hasMultiUnitEnabled: false → no debe haber selector UND/DIS en catálogo
    "hasMultiUnitEnabled": {
        "off_check": "assertNotVisible",
        "off_text": r".*DIS.*|.*[Dd]isplay.*",
        "on_check": "assertVisible",
        "on_text": r"DIS|UND",
        "context": "catálogo de productos",
        "description": "Selector DIS/UND (multi-unidad)",
    },
    # useNewPromotions: false → no debe haber badge PROMO ni % descuento
    "useNewPromotions": {
        "off_check": "assertNotVisible",
        "off_text": r".*PROMO.*|.*%.*[Dd]escuento.*",
        "on_check": None,  # cuando ON no hay assertion fácil, skip
        "context": "catálogo de productos",
        "description": "Badge de promociones (PROMO / % descuento)",
    },
    # enableSellerDiscount: false → no debe haber 'Descuento Vendedor' en carrito
    "enableSellerDiscount": {
        "off_check": "assertNotVisible",
        "off_text": r".*[Dd]escuento [Vv]endedor.*|.*[Aa]plicar [Dd]escuento.*",
        "on_check": "assertVisible",
        "on_text": r".*[Dd]escuento [Vv]endedor.*",
        "context": "carrito de compras",
        "description": "Opción 'Descuento Vendedor'",
    },
    # enablePayments: false → no debe haber módulo Pagos
    "enablePayments": {
        "off_check": "assertNotVisible",
        "off_text": r".*[Pp]agos?.*|.*[Pp]ayment.*",
        "on_check": None,
        "context": "menú principal",
        "description": "Módulo de Pagos",
    },
    # enablePaymentsCollection: false → no debe haber opción Cobros
    "enablePaymentsCollection": {
        "off_check": "assertNotVisible",
        "off_text": r".*[Cc]obras?.*|.*[Cc]ollection.*",
        "on_check": None,
        "context": "menú principal",
        "description": "Módulo de Cobros",
    },
    # loginButtons.facebook: false → no debe aparecer botón Facebook en login
    "loginButtons.facebook": {
        "off_check": "assertNotVisible",
        "off_text": r".*[Ff]acebook.*|.*FB.*",
        "on_check": "assertVisible",
        "on_text": r".*[Ff]acebook.*",
        "context": "pantalla de login",
        "description": "Botón login con Facebook",
    },
    # loginButtons.google: false → no debe aparecer botón Google en login
    "loginButtons.google": {
        "off_check": "assertNotVisible",
        "off_text": r".*[Gg]oogle.*",
        "on_check": "assertVisible",
        "on_text": r".*[Gg]oogle.*",
        "context": "pantalla de login",
        "description": "Botón login con Google",
    },
}


def load_matrix(env: str) -> dict:
    root = Path(__file__).parent.parent
    if env == "production":
        matrix_file = root / "data" / "qa-matrix.json"
    else:
        matrix_file = root / "data" / "qa-matrix-staging.json"

    if not matrix_file.exists():
        print(f"❌ Archivo no encontrado: {matrix_file}", file=sys.stderr)
        sys.exit(1)

    with open(matrix_file) as f:
        data = json.load(f)

    return data.get("clients", {})


def find_client(clients, slug, env):
    """Encuentra el cliente por slug, intentando variantes con sufijo -staging."""
    suffix = "-staging" if env == "staging" else ""
    candidates = [slug + suffix, slug]
    for key in candidates:
        if key in clients:
            return key, clients[key]
    # Búsqueda parcial
    for key, val in clients.items():
        if key.startswith(slug):
            return key, val
    return None, None


def get_var(variables: dict, flag: str):
    """Obtiene el valor de una variable (soporta dot notation)."""
    val = variables.get(flag)
    if val is None:
        return None
    return bool(val)


def gen_assertion(check: str, text: str, description: str) -> str:
    """Genera un bloque YAML de assertion."""
    lines = [
        f"# {description}",
        f"- {check}:",
        f'    text: "{text}"',
    ]
    return "\n".join(lines)


def generate_yaml(client_key: str, client_data: dict) -> str:
    variables = client_data.get("variables", {})
    name = client_data.get("name", client_key)
    domain = client_data.get("domain", "")

    assertions = []
    skipped = []

    for flag, spec in FEATURE_MAP.items():
        val = get_var(variables, flag)
        if val is None:
            skipped.append(f"  # {flag}: no encontrada en matrix")
            continue

        if not val:  # flag es FALSE/OFF
            check = spec.get("off_check")
            text = spec.get("off_text")
            desc = spec["description"]
            ctx = spec["context"]
            if check and text:
                assertions.append(
                    (ctx, flag, False, gen_assertion(check, text, f"{desc} — debe ser INVISIBLE ({flag}: false)"))
                )
        else:  # flag es TRUE/ON
            check = spec.get("on_check")
            text = spec.get("on_text")
            desc = spec["description"]
            ctx = spec["context"]
            if check and text:
                assertions.append(
                    (ctx, flag, True, gen_assertion(check, text, f"{desc} — debe ser VISIBLE ({flag}: true)"))
                )

    # Agrupar por contexto
    contexts_order = [
        "pantalla de login",
        "lista de comercios",
        "catálogo de productos",
        "carrito de compras",
        "menú principal",
    ]

    by_context = {}
    for ctx, flag, val, block in assertions:
        by_context.setdefault(ctx, []).append(block)

    lines = [
        f"appId: ${{APP_PACKAGE}}",
        f'name: "Verificación features ON/OFF — {name}"',
        f"# GENERADO AUTOMÁTICAMENTE por tools/gen-maestro-features.py",
        f"# Fuente: {domain} (variables MongoDB reales)",
        f"# Regenerar: python3 tools/gen-maestro-features.py <cliente>",
        "---",
        "",
    ]

    # Contextos que requieren navegación previa
    has_login_checks = "pantalla de login" in by_context
    has_catalog_checks = any(c in by_context for c in ["catálogo de productos", "carrito de compras"])
    has_list_checks = "lista de comercios" in by_context

    if has_login_checks:
        lines += [
            "# ── Login screen checks (antes de iniciar sesión) ────────────────",
            "- launchApp:",
            "    clearState: true",
            "- waitForAnimationToEnd",
            "",
        ]
        for block in by_context.get("pantalla de login", []):
            lines.append(block)
            lines.append("")

    lines += [
        "# ── Startup: llegar a lista de comercios ─────────────────────────",
        "- runFlow: helpers-startup.yaml",
        "",
    ]

    if has_list_checks:
        lines += [
            "# ── Lista de comercios ───────────────────────────────────────────",
        ]
        for block in by_context.get("lista de comercios", []):
            lines.append(block)
            lines.append("")

    if has_catalog_checks:
        lines += [
            "# ── Entrar a comercio disponible ─────────────────────────────────",
            "- runFlow: helpers-filtro-disponible.yaml",
            "- tapOn:",
            "    text: r'.*\\d{7,}.*'",
            "    index: 0",
            "    optional: true",
            "- extendedWaitUntil:",
            "    visible:",
            '      text: "Continuar|.*[Hh]acer [Pp]edido.*|.*[Cc]at[aá]logo.*"',
            "    timeout: 15000",
            "- tapOn:",
            '    text: "Continuar"',
            "    optional: true",
            "- waitForAnimationToEnd",
            "- tapOn:",
            '    text: ".*[Hh]acer [Pp]edido.*|.*[Cc]at[aá]logo.*|.*[Pp]roductos.*"',
            "    optional: true",
            "- extendedWaitUntil:",
            "    visible:",
            '      text: ".*[Aa]gregar.*|.*[Cc]at[aá]logo.*|.*[Pp]roducto.*"',
            "    timeout: 20000",
            "",
            "# ── Catálogo: checks de features ─────────────────────────────────",
        ]
        for block in by_context.get("catálogo de productos", []):
            lines.append(block)
            lines.append("")

        if "carrito de compras" in by_context:
            lines += [
                "# ── Agregar producto al carrito ──────────────────────────────────",
                "- tapOn:",
                '    text: ".*[Aa]gregar.*"',
                "    index: 0",
                "    optional: true",
                "- waitForAnimationToEnd",
                "",
                "# ── Carrito: checks de features ──────────────────────────────────",
            ]
            for block in by_context.get("carrito de compras", []):
                lines.append(block)
                lines.append("")

    lines += [
        "# ── Volver a lista ───────────────────────────────────────────────",
        "- runFlow: helpers-volver-lista.yaml",
    ]

    if skipped:
        lines += [
            "",
            "# ── Variables no encontradas en matrix (sin assertion) ───────────",
        ]
        lines.extend(skipped)

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Genera 04-features.yaml desde qa-matrix")
    parser.add_argument("cliente", help="Slug del cliente (ej: caren, prinorte)")
    parser.add_argument("--env", choices=["staging", "production"], default="staging")
    parser.add_argument("--dry-run", action="store_true", help="Mostrar YAML sin escribir archivo")
    args = parser.parse_args()

    clients = load_matrix(args.env)
    client_key, client_data = find_client(clients, args.cliente, args.env)

    if not client_data:
        print(f"❌ Cliente '{args.cliente}' no encontrado en matrix ({args.env})", file=sys.stderr)
        print(f"   Clientes disponibles: {', '.join(sorted(clients.keys()))}", file=sys.stderr)
        sys.exit(1)

    print(f"✅ Cliente: {client_key} — {client_data.get('name', '')}")
    print(f"   Dominio: {client_data.get('domain', '')}")

    yaml_content = generate_yaml(client_key, client_data)

    if args.dry_run:
        print("\n" + "─" * 60)
        print(yaml_content)
        return

    root = Path(__file__).parent.parent
    out_path = root / "tests" / "app" / "flows" / args.cliente / "04-features.yaml"

    if not out_path.parent.exists():
        print(f"❌ Directorio no existe: {out_path.parent}", file=sys.stderr)
        print(f"   ¿El cliente tiene flows? Verifica: tests/app/flows/{args.cliente}/", file=sys.stderr)
        sys.exit(1)

    out_path.write_text(yaml_content)
    print(f"✅ Generado: {out_path.relative_to(root)}")

    # Mostrar resumen de assertions generadas
    variables = client_data.get("variables", {})
    print("\n   Assertions generadas:")
    for flag, spec in FEATURE_MAP.items():
        val = get_var(variables, flag)
        if val is None:
            print(f"   ⚠  {flag}: no encontrada")
        elif not val:
            check = spec.get("off_check", "—")
            print(f"   ✓  {flag}: OFF → {check}")
        else:
            check = spec.get("on_check")
            if check:
                print(f"   ✓  {flag}: ON → {check}")
            else:
                print(f"   –  {flag}: ON (sin assertion para ON)")


if __name__ == "__main__":
    main()
