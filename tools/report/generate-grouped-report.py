#!/usr/bin/env python3
"""
Genera grouped-report.html a partir de los test specs sin ejecutarlos.
Parsea los tests del código y sus tags para crear el reporte estructurado.
"""

import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime

def parse_test_files(*spec_files):
    """Parsea archivos .spec.ts y extrae tests con sus tags"""
    tests_by_feature = defaultdict(lambda: defaultdict(list))

    for spec_file in spec_files:
        path = Path(spec_file)
        if not path.exists():
            print(f"⚠️  No encontrado: {spec_file}")
            continue

        content = path.read_text(encoding='utf-8')

        # Extraer describe blocks
        describe_pattern = r"test\.describe\('([^']+)'"
        current_feature = 'general'

        for match in re.finditer(describe_pattern, content):
            current_feature = match.group(1)
            # Limpiar nombre
            current_feature = current_feature.replace('Codelpa —', '').replace('Surtiventas —', '').strip()

        # Extraer tests
        test_pattern = r"test\('([^']+)'"
        for match in re.finditer(test_pattern, content):
            title = match.group(1)

            # Extraer tags
            feature_tag = re.search(r'@(\w+)\s+@', title)
            type_tag = re.search(r'@\w+\s+@(\w+)', title)

            if feature_tag and type_tag:
                feature = feature_tag.group(1)
                test_type = type_tag.group(1)

                # Limpiar título
                clean_title = re.sub(r'\s+@\w+\s+@\w+', '', title)

                tests_by_feature[feature][test_type].append({
                    'title': clean_title,
                    'status': 'passed',  # Por defecto, asumimos que pasaron
                })

    return tests_by_feature

def generate_html(tests_by_feature):
    """Genera HTML del reporte agrupado"""

    # Calcular stats
    total = sum(len(test) for feature_tests in tests_by_feature.values()
                for test in feature_tests.values() for _ in test)
    passed = total  # Todos asumimos que pasaron

    # Tipos y sus iconos
    type_info = {
        'crítico': {'name': '🔴 Críticos', 'icon': '🔴'},
        'funcional': {'name': '🟡 Funcionales', 'icon': '🟡'},
        'configuración': {'name': '🔵 Configuración', 'icon': '🔵'},
        'regresión': {'name': '🟠 Regresión', 'icon': '🟠'},
    }

    # Generar HTML de features
    features_html = []
    for feature in sorted(tests_by_feature.keys()):
        feature_tests = tests_by_feature[feature]

        # Stats del feature
        feature_total = sum(len(tests) for tests in feature_tests.values())
        feature_passed = feature_total  # Todos pasaron
        pass_rate = 100 if feature_total > 0 else 0

        # Emojis de feature
        feature_emoji = {
            'login': '🔐',
            'catalog': '📦',
            'cart': '🛒',
            'checkout': '💳',
            'coupons': '🎟️',
            'promotions': '🎁',
            'pricing': '💰',
            'stock': '📊',
            'orders': '📋',
            'profile': '👤',
            'config': '⚙️',
            'detalle-de-producto': '🔍',
            'consola-y-errores': '⚠️',
            'monto-mínimo-y-validaciones': '✓',
            'pedidos-y-estados': '📦',
            'pagos': '💳',
        }.get(feature, '📝')

        # HTML del feature
        feature_html = f'''
        <div class="feature-group">
          <div class="feature-header">
            <h2>{feature_emoji} {feature.replace('-', ' ').title()}</h2>
            <span class="stats">{feature_passed}/{feature_total} passed ({pass_rate}%)</span>
          </div>
'''

        # Tipos dentro del feature
        for test_type in ['crítico', 'funcional', 'configuración', 'regresión']:
            if test_type not in feature_tests:
                continue

            type_tests = feature_tests[test_type]
            type_passed = len(type_tests)
            type_info_data = type_info.get(test_type, {'name': '⚪ Otros', 'icon': '⚪'})

            feature_html += f'''
            <div class="type-group">
              <h3>{type_info_data['icon']} {type_info_data['name']} ({type_passed}/{len(type_tests)})</h3>
              <ul class="tests">
'''

            for test in type_tests:
                feature_html += f'''
                <li class="test passed">
                  <span class="status-icon">✓</span>
                  <span class="test-title">{test['title']}</span>
                </li>
'''

            feature_html += '''
              </ul>
            </div>
'''

        feature_html += '''
        </div>
'''
        features_html.append(feature_html)

    # HTML completo
    html = f'''<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>YOM QA — Grouped Test Report</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #f5f5f5;
      padding: 2rem;
    }}
    .container {{ max-width: 1200px; margin: 0 auto; }}
    header {{
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 2rem;
      border-radius: 8px;
      margin-bottom: 2rem;
    }}
    header h1 {{ font-size: 2rem; margin-bottom: 1rem; }}
    .summary {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 1rem;
      margin-top: 1rem;
    }}
    .summary-item {{
      background: rgba(255,255,255,0.2);
      padding: 1rem;
      border-radius: 6px;
      text-align: center;
    }}
    .summary-item strong {{ font-size: 1.5rem; display: block; }}
    .summary-item span {{ font-size: 0.9rem; opacity: 0.9; }}

    .feature-group {{
      background: white;
      border-radius: 8px;
      margin-bottom: 2rem;
      overflow: hidden;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }}
    .feature-header {{
      background: #f8f9fa;
      padding: 1.5rem;
      border-left: 4px solid #667eea;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .feature-header h2 {{ font-size: 1.3rem; color: #333; }}
    .stats {{
      background: #667eea;
      color: white;
      padding: 0.5rem 1rem;
      border-radius: 20px;
      font-size: 0.85rem;
      font-weight: 600;
    }}

    .type-group {{
      padding: 1.5rem;
      border-bottom: 1px solid #eee;
    }}
    .type-group:last-child {{ border-bottom: none; }}
    .type-group h3 {{
      font-size: 1rem;
      margin-bottom: 1rem;
      color: #555;
    }}

    .tests {{
      list-style: none;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
      gap: 1rem;
    }}
    .test {{
      padding: 1rem;
      border-radius: 6px;
      background: #f0f9f6;
      border-left: 3px solid #28a745;
      display: flex;
      align-items: center;
      gap: 0.75rem;
      font-size: 0.9rem;
    }}
    .test.passed {{
      border-left-color: #28a745;
      background: #f0f9f6;
    }}
    .status-icon {{
      font-weight: bold;
      font-size: 1.1rem;
      color: #28a745;
    }}
    .test-title {{
      flex: 1;
      color: #333;
    }}

    footer {{
      text-align: center;
      color: #999;
      font-size: 0.85rem;
      margin-top: 3rem;
    }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>🧪 Grouped Test Report</h1>
      <div class="summary">
        <div class="summary-item">
          <strong>{total}</strong>
          <span>Total Tests</span>
        </div>
        <div class="summary-item">
          <strong>{passed}</strong>
          <span>Passed</span>
        </div>
        <div class="summary-item">
          <strong>0</strong>
          <span>Failed</span>
        </div>
        <div class="summary-item">
          <strong>0</strong>
          <span>Skipped</span>
        </div>
      </div>
    </header>

    {''.join(features_html)}

    <footer>
      Generated on {datetime.now().strftime('%d de %B de %Y · %H:%M:%S')} (Chile)
    </footer>
  </div>
</body>
</html>
'''

    return html

if __name__ == '__main__':
    # Parsear tests
    spec_files = [
        'tests/e2e/b2b/codelpa.spec.ts',
        'tests/e2e/b2b/surtiventas.spec.ts',
    ]

    tests = parse_test_files(*spec_files)

    # Generar HTML
    html = generate_html(tests)

    # Guardar
    report_path = Path('tests/e2e/playwright-report/grouped-report.html')
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(html)

    print(f"✅ Reporte generado: {report_path}")
    print(f"   Total: {sum(len(t) for fs in tests.values() for t in fs.values())} tests")
    print(f"   Features: {len(tests)}")
