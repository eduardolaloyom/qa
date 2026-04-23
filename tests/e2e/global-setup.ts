import { execSync } from 'child_process';
import clients from './fixtures/clients';

export default async function globalSetup() {
  // Validación de seguridad: detectar clientes apuntando a producción
  // Los tests que crean pedidos tienen guard de describe-level, pero este
  // aviso asegura que el operador sepa que está corriendo contra prod.
  const prodClients = Object.entries(clients)
    .filter(([, c]) => c.baseURL.includes('youorder.me'))
    .map(([k, c]) => `${k} → ${c.baseURL}`);

  if (prodClients.length > 0) {
    console.warn('\n⚠️  PRODUCCIÓN DETECTADA — los siguientes clientes apuntan a youorder.me:');
    prodClients.forEach(c => console.warn(`   ${c}`));
    console.warn('   Tests que crean pedidos (C2-11, C2-12, PM1-03) están BLOQUEADOS automáticamente.\n');
  }

  // Skip en CI — no hay browser que abrir
  if (process.env.CI) return;

  // webServer config handles server lifecycle.
  // Just open the dashboard in browser (best-effort, macOS only).
  try {
    execSync('open http://localhost:8080');
  } catch {}
}
