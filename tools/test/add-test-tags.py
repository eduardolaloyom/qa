#!/usr/bin/env python3
"""
Script para agregar tags @feature y @type a los tests de Playwright
Usage: python3 add-test-tags.py <archivo.spec.ts>
"""

import sys
import re
from pathlib import Path

# Mapeo de palabras clave a tipos de test
TYPE_KEYWORDS = {
    'fallido': 'crítico',
    'error': 'crítico',
    'bloquea': 'crítico',
    'imposible': 'crítico',
    'roto': 'crítico',
    'no funciona': 'crítico',
    '500': 'crítico',
    'null': 'crítico',
    'exitoso': 'funcional',
    'muestra': 'funcional',
    'carga': 'funcional',
    'visible': 'funcional',
    'puede': 'funcional',
    'valida': 'funcional',
    'persistente': 'configuración',
    'config': 'configuración',
    'sin': 'configuración',
    'disabled': 'configuración',
    'readonly': 'configuración',
}

# Mapeo de describe blocks a features
FEATURE_MAP = {
    'Login': 'login',
    'Catálogo': 'catalog',
    'Carrito': 'cart',
    'Checkout': 'checkout',
    'Cupones': 'coupons',
    'Promociones': 'promotions',
    'Precios': 'pricing',
    'Stock': 'stock',
    'Órdenes': 'orders',
    'Perfil': 'profile',
    'Variables sin cobertura': 'config',
}

def detect_type(title: str) -> str:
    """Detecta el tipo de test basado en palabras clave en el título"""
    title_lower = title.lower()

    # Crítico si tiene palabras clave de error
    for keyword in ['fallido', 'error', 'bloquea', 'imposible', 'roto', '500', 'null']:
        if keyword in title_lower:
            return 'crítico'

    # Configuración si tienen estas palabras
    for keyword in ['persistente', 'config', 'disabled', 'readonly', 'editable', 'locked']:
        if keyword in title_lower:
            return 'configuración'

    # Por defecto funcional
    return 'funcional'

def detect_feature(describe_block: str) -> str:
    """Detecta la feature basada en el nombre del describe block"""
    for key, value in FEATURE_MAP.items():
        if key.lower() in describe_block.lower():
            return value
    # Extrae palabras de describe como feature
    words = describe_block.replace('Codelpa —', '').replace('Surtiventas —', '').strip().lower()
    return words.replace(' ', '-') if words else 'general'

def process_file(filepath: str):
    """Procesa un archivo .spec.ts y agrega tags a los tests"""
    path = Path(filepath)
    if not path.exists():
        print(f"❌ Archivo no encontrado: {filepath}")
        return False

    content = path.read_text(encoding='utf-8')
    lines = content.split('\n')

    current_feature = 'general'
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Detectar describe blocks
        describe_match = re.search(r"test\.describe\('([^']+)'", line)
        if describe_match:
            current_feature = detect_feature(describe_match.group(1))

        # Detectar tests
        test_match = re.search(r"test\('([^']+)'", line)
        if test_match:
            title = test_match.group(1)
            test_type = detect_type(title)

            # Crear tags
            tags = f"@{current_feature} @{test_type}"

            # Insertar tags en el título si no existen ya
            if '@' not in title:
                new_line = line.replace(f"test('{title}'", f"test('{title} {tags}'")
                result.append(new_line)
                print(f"✓ {title} → {tags}")
            else:
                result.append(line)
        else:
            result.append(line)

        i += 1

    # Guardar archivo actualizado
    path.write_text('\n'.join(result), encoding='utf-8')
    print(f"\n✅ Archivo actualizado: {filepath}")
    return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python3 add-test-tags.py <archivo.spec.ts> [archivo2.spec.ts ...]")
        sys.exit(1)

    for filepath in sys.argv[1:]:
        process_file(filepath)
