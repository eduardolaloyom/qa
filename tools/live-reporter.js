// @ts-check
const fs = require('fs');
const path = require('path');

const OUTPUT = path.join(__dirname, '../public/live.json');

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
  }

  onBegin(config, suite) {
    this.state.total = suite.allTests().length;
    this._save();
  }

  onTestBegin(test) {
    this.state.currentTest = test.title;
    this._save();
  }

  onTestEnd(test, result) {
    const status = result.status; // 'passed'|'failed'|'skipped'|'timedOut'
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
  }

  _save() {
    try {
      fs.writeFileSync(OUTPUT, JSON.stringify(this.state, null, 2));
    } catch (e) { /* ignore */ }
  }
}

module.exports = LiveReporter;
