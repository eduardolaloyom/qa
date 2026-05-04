import { execSync } from 'child_process';
import { readFileSync, unlinkSync, existsSync } from 'fs';
import { join } from 'path';

const PID_FILE = join(__dirname, '../../.http-server.pid');

export default async function globalTeardown() {
  // Belt-and-suspenders: kill anything holding port 8080
  // (webServer config handles this normally; this is the fallback)
  try {
    execSync('lsof -ti:8080 | xargs kill -9 2>/dev/null || true', { shell: '/bin/bash' });
  } catch {}
  // Clean up stale PID file if it somehow exists
  try { unlinkSync(PID_FILE); } catch {}

  // Publicar resultados al dashboard
  const root = join(__dirname, '../..');
  try {
    execSync('python3 tools/publish-results.py', { cwd: root, stdio: 'inherit' });
  } catch (e) {
    console.error('⚠️  publish-results.py falló:', e);
  }

  // Git commit + push (skip en CI — lo hace el workflow)
  if (process.env.CI) return;
  try {
    const date = new Date().toISOString().split('T')[0];
    execSync(
      `git diff --quiet public/qa/ && git diff --cached --quiet public/qa/ || ` +
      `(git add public/qa/ && git commit -m "chore: publish playwright results ${date}" && ` +
      `(git push || (git pull --rebase && git push)))`,
      { cwd: root, shell: '/bin/bash', stdio: 'inherit' }
    );
  } catch (e) {
    console.error('⚠️  git push falló:', e);
  }

  // Hint de triage si hay fallos
  try {
    const historyFile = join(root, 'public', 'qa', 'history', `${new Date().toISOString().split('T')[0]}.json`);
    if (existsSync(historyFile)) {
      const run = JSON.parse(readFileSync(historyFile, 'utf8'));
      const failed = run.failed || 0;
      const flaky = (run.failure_groups || []).filter((g: any) => g.category === 'flaky').reduce((acc: number, g: any) => acc + g.count, 0);
      if (failed > 0) {
        console.log(`\n${'─'.repeat(60)}`);
        console.log(`⚠️  ${failed} test(s) fallaron — corre /triage-playwright para analizar`);
        if (flaky > 0) console.log(`   + ${flaky} flaky (pasaron en retry)`);
        console.log(`${'─'.repeat(60)}\n`);
      }
    }
  } catch {}
}
