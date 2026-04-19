// @ts-check
const fs = require('fs');
const path = require('path');
const https = require('https');

const OUTPUT = path.join(__dirname, '../public/live.json');
const TMP_OUTPUT = OUTPUT + '.tmp';
const GITHUB_REPO = 'eduardolaloyom/qa';
const GITHUB_FILE = 'public/live.json';
const PUSH_INTERVAL_MS = 10_000; // push a GitHub cada 10s máximo

class LiveReporter {
  constructor() {
    this.state = {
      running: true,
      startTime: new Date().toISOString(),
      total: 0,
      passed: 0,
      failed: 0,
      skipped: 0,
      currentTest: null,
      recentTests: [],   // last 20
    };
    this._ghSha = null;       // SHA del archivo en GitHub (cache)
    this._lastPush = 0;       // timestamp del último push a GitHub
    this._pushPending = false; // evitar pushes concurrentes
  }

  onBegin(config, suite) {
    // Replace state entirely — clears counters, recentTests, and endTime from any
    // prior run that might otherwise bleed into this run's live.json snapshot.
    // Fixes PIPE-02: stale total/passed/failed/skipped between runs.
    this.state = {
      running: true,
      startTime: new Date().toISOString(),
      total: suite.allTests().length,
      passed: 0,
      failed: 0,
      skipped: 0,
      currentTest: null,
      recentTests: [],
    };
    this._save();
  }

  onTestBegin(test) {
    this.state.currentTest = test.title;
    this._save();
  }

  onTestEnd(test, result) {
    const status = result.status;
    if (status === 'passed') this.state.passed++;
    else if (status === 'failed' || status === 'timedOut') this.state.failed++;
    else if (status === 'skipped') this.state.skipped++;

    this.state.recentTests.unshift({
      title: test.title,
      status: status === 'timedOut' ? 'failed' : status,
      duration: result.duration,
    });
    if (this.state.recentTests.length > 20) this.state.recentTests.pop();
    this.state.currentTest = null;
    this._save();
  }

  onEnd(result) {
    this.state.running = false;
    this.state.endTime = new Date().toISOString();
    this.state.currentTest = null;
    this._save();
    // Push final siempre, sin respetar el intervalo
    this._pushToGitHub(true);
  }

  _save() {
    try {
      fs.writeFileSync(TMP_OUTPUT, JSON.stringify(this.state, null, 2));
      fs.renameSync(TMP_OUTPUT, OUTPUT);
    } catch (e) { /* ignore */ }
    this._pushToGitHub(false);
  }

  // ── GitHub API push ────────────────────────────────────────────────────────
  _pushToGitHub(force = false) {
    const token = process.env.GITHUB_TOKEN;
    if (!token) return;

    const now = Date.now();
    if (!force && (now - this._lastPush < PUSH_INTERVAL_MS)) return;
    if (this._pushPending) return;

    this._lastPush = now;
    this._pushPending = true;

    const content = Buffer.from(JSON.stringify(this.state, null, 2)).toString('base64');

    const doUpdate = (sha) => {
      const body = JSON.stringify({
        message: 'live: update test status',
        content,
        ...(sha ? { sha } : {}),
      });

      const req = https.request({
        hostname: 'api.github.com',
        path: `/repos/${GITHUB_REPO}/contents/${GITHUB_FILE}`,
        method: 'PUT',
        headers: {
          'Authorization': `token ${token}`,
          'User-Agent': 'yom-qa-live-reporter',
          'Accept': 'application/vnd.github.v3+json',
          'Content-Type': 'application/json',
          'Content-Length': Buffer.byteLength(body),
        },
      }, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          try {
            const json = JSON.parse(data);
            this._ghSha = json?.content?.sha || sha;
          } catch {}
          this._pushPending = false;
        });
      });
      req.on('error', () => { this._pushPending = false; });
      req.write(body);
      req.end();
    };

    // Si ya tenemos el SHA, hacer PUT directo
    if (this._ghSha) {
      doUpdate(this._ghSha);
      return;
    }

    // Si no, hacer GET primero para obtener el SHA
    const getReq = https.request({
      hostname: 'api.github.com',
      path: `/repos/${GITHUB_REPO}/contents/${GITHUB_FILE}`,
      method: 'GET',
      headers: {
        'Authorization': `token ${token}`,
        'User-Agent': 'yom-qa-live-reporter',
        'Accept': 'application/vnd.github.v3+json',
      },
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          this._ghSha = json?.sha || null;
        } catch {}
        doUpdate(this._ghSha);
      });
    });
    getReq.on('error', () => {
      doUpdate(null);
    });
    getReq.end();
  }
}

module.exports = LiveReporter;
