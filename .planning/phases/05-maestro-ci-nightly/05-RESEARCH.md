# Phase 5: Maestro CI Nightly — Research

**Researched:** 2026-04-17
**Domain:** GitHub Actions, Android emulator CI, Maestro CLI, mobile E2E automation
**Confidence:** HIGH (core stack verified via official docs and marketplace listings)

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| REQ-07 | A GitHub Actions workflow must run the Prinorte Maestro APP flows automatically on a nightly schedule. Must produce artifacts (logs + HTML report) accessible from GitHub and notify on failure. No physical Android device required — must work with an emulator in CI. | android-emulator-runner@v2 on ubuntu-latest with KVM enables hardware-accelerated emulator; Maestro installs via curl; logs + HTML produced by run-maestro.sh pattern; failure notification via if: failure() + Slack webhook or GitHub issue. |
</phase_requirements>

---

## Summary

The workflow must replicate what `tools/run-maestro.sh` does locally: install Maestro CLI, load config vars (APP_PACKAGE, TEST_SELLER_EMAIL, TEST_SELLER_PASSWORD) from CI secrets, launch the prinorte-session.yaml against a running Android emulator, and produce a structured log + HTML report. The key CI-specific concerns are: (1) enabling hardware acceleration via KVM on ubuntu-latest, (2) installing the YOM Ventas APK before flows run, and (3) deciding how the APK reaches CI (download URL vs GitHub secret vs artifact).

The standard CI stack is `reactivecircus/android-emulator-runner@v2` on `ubuntu-latest` with KVM enabled via a udev rules step. This combination is hardware-accelerated, free on GitHub-hosted runners (as of April 2024 when GitHub enabled KVM for 2-vCPU runners), and 2-3x faster than macOS runners. Maestro version must be pinned at >= 1.40.0 (the MAESTRO_MIN_VERSION constant in run-maestro.sh) using the `MAESTRO_VERSION` env var before running the install curl command.

The critical blocker is the APK. Maestro requires a real APK installed on the emulator — there is no dry-run or syntax-only mode (a `maestro validate` command was requested in issue #1783 in 2024 but not confirmed as shipped). The recommended path: store the APK download URL or the APK file itself as a GitHub Actions secret or artifact. For a YOM-internal app, the most practical CI approach is to store the APK URL as a secret (`APK_URL`) and download it with `curl` at workflow start. If no URL is available, the workflow must gate on APK availability and fall back to YAML linting only.

**Primary recommendation:** Use ubuntu-latest + KVM + reactivecircus/android-emulator-runner@v2 (API 29, x86_64) + Maestro 1.40.0 pinned + APK downloaded from a signed S3/GCS URL stored as `APK_URL` secret. Notification via `if: failure()` step posting to Slack via `slackapi/slack-github-action`.

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| reactivecircus/android-emulator-runner | v2 (latest v2.37.0) | Spin up hardware-accelerated Android emulator in CI | Official GitHub Marketplace action; only stable solution for emulator-in-CI on ubuntu-latest |
| actions/checkout | v4 | Check out repo | Standard; required for flow YAML files |
| actions/upload-artifact | v4 | Upload maestro.log + HTML report | Standard GitHub artifact upload |
| Maestro CLI | 1.40.0 (pinned) | Run flow YAML files against Android app | The project's declared minimum version (run-maestro.sh MAESTRO_MIN_VERSION) |
| slackapi/slack-github-action | v1.27.0 | Post failure notification to Slack | Simple, maintained, uses incoming webhook — no extra dependencies |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| actions/setup-java | v4 | Install Java 17 (Maestro requirement) | Required — Maestro CLI needs Java 17+ |
| KVM udev rules (inline run step) | N/A | Enable hardware acceleration on ubuntu-latest | Mandatory before android-emulator-runner; one-liner udev rules step |
| yamllint | system pip | Validate flow YAML syntax | Only if APK is unavailable — fallback lint-only mode |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| ubuntu-latest + KVM | macos-latest | macOS is 2-3x slower and ~10x more expensive on GitHub-hosted runners |
| reactivecircus/android-emulator-runner | budtmo/docker-android | Docker approach works but adds complexity; emulator-runner is the ecosystem standard |
| Maestro CLI self-hosted | Maestro Cloud (SaaS) | Cloud requires paid API key; self-hosted is free and keeps secrets local |
| slackapi/slack-github-action | GitHub issue via gh CLI | Slack is more immediate; GitHub issue creates noise in the issue tracker |

**Installation (in workflow YAML):**

```yaml
# Java 17 (Maestro requirement)
- uses: actions/setup-java@v4
  with:
    distribution: temurin
    java-version: '17'

# Maestro CLI pinned to min version
- name: Install Maestro CLI
  run: |
    export MAESTRO_VERSION=1.40.0
    curl -fsSL "https://get.maestro.mobile.dev" | bash
    echo "$HOME/.maestro/bin" >> $GITHUB_PATH
```

---

## Architecture Patterns

### Workflow File Location

```
.github/workflows/
├── deploy-qa-dashboard.yml    # EXISTING — dashboard deploy on public/ push
└── app-maestro.yml            # NEW — nightly Maestro CI
```

### Pattern 1: Two-Job Strategy (lint-always, emulator-when-apk-available)

**What:** Split into two jobs. Job 1 always runs and validates flow YAML syntax with yamllint. Job 2 runs the full emulator suite only if the APK secret is set.

**When to use:** When APK availability is conditional (still sourcing a download URL).

**Example:**

```yaml
jobs:
  validate-flows:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install yamllint && yamllint tests/app/flows/

  run-on-emulator:
    runs-on: ubuntu-latest
    needs: validate-flows
    if: ${{ secrets.APK_URL != '' }}
    steps:
      # ... emulator + maestro steps
```

### Pattern 2: Single-Job with APK Download (preferred when APK URL is available)

**What:** One job that downloads the APK, boots the emulator, installs the APK, and runs flows. This matches how run-maestro.sh works locally.

**When to use:** Once `APK_URL` secret is populated.

```yaml
name: Maestro Nightly — Prinorte APP

on:
  schedule:
    - cron: '0 6 * * *'   # 06:00 UTC = 03:00 CLT (quiet hours)
  workflow_dispatch:

jobs:
  maestro:
    runs-on: ubuntu-latest
    timeout-minutes: 45

    steps:
      - uses: actions/checkout@v4

      - name: Enable KVM
        run: |
          echo 'KERNEL=="kvm", GROUP="kvm", MODE="0666", OPTIONS+="static_node=kvm"' | sudo tee /etc/udev/rules.d/99-kvm4all.rules
          sudo udevadm control --reload-rules
          sudo udevadm trigger --name-match=kvm

      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: '17'

      - name: Install Maestro CLI 1.40.0
        run: |
          export MAESTRO_VERSION=1.40.0
          curl -fsSL "https://get.maestro.mobile.dev" | bash
          echo "$HOME/.maestro/bin" >> $GITHUB_PATH

      - name: Download APK
        run: |
          curl -fsSL "${{ secrets.APK_URL }}" -o app.apk

      - name: Run Maestro on Emulator
        uses: reactivecircus/android-emulator-runner@v2
        with:
          api-level: 29
          target: default
          arch: x86_64
          profile: pixel_2
          emulator-options: -no-window -gpu swiftshader_indirect -noaudio -no-boot-anim -no-snapshot
          disable-animations: true
          script: |
            adb install -r app.apk
            mkdir -p QA/Prinorte/$(date +%Y-%m-%d)
            maestro test \
              --env APP_PACKAGE="${{ secrets.APP_PACKAGE }}" \
              --env TEST_SELLER_EMAIL="${{ secrets.TEST_SELLER_EMAIL }}" \
              --env TEST_SELLER_PASSWORD="${{ secrets.TEST_SELLER_PASSWORD }}" \
              tests/app/flows/prinorte-session.yaml \
              2>&1 | tee QA/Prinorte/$(date +%Y-%m-%d)/maestro.log

      - name: Generate HTML report
        if: always()
        run: |
          python3 tools/run-maestro.sh --ci-report-only 2>/dev/null || \
          python3 - <<'EOF'
          # Inline report generation from maestro.log
          # (see Code Examples section for full script)
          EOF

      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: maestro-report-${{ github.run_id }}
          path: |
            QA/Prinorte/*/maestro.log
            public/app-reports/prinorte-*.html
          retention-days: 30

      - name: Notify Slack on failure
        if: failure()
        uses: slackapi/slack-github-action@v1.27.0
        with:
          payload: |
            {
              "text": "Maestro CI fallido — Prinorte APP\nRun: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_MAESTRO_WEBHOOK }}
          SLACK_WEBHOOK_TYPE: INCOMING_WEBHOOK
```

### Anti-Patterns to Avoid

- **Hardcoding credentials in workflow YAML:** All secrets (APK_URL, TEST_SELLER_EMAIL, TEST_SELLER_PASSWORD, APP_PACKAGE, SLACK_MAESTRO_WEBHOOK) must come from GitHub Actions secrets — never inline.
- **Running on macos-latest:** It's 10x more expensive with no benefit for this use case since KVM is now available on ubuntu-latest.
- **Omitting the KVM step:** Without the udev rules step, the emulator will run in software mode on ubuntu-latest and be unbearably slow (10+ min boot).
- **Missing `if: always()` on upload-artifact:** If the Maestro run fails, artifacts are skipped without this flag — defeating the purpose of CI artifact collection.
- **Not pinning Maestro version:** `curl ... | bash` without `MAESTRO_VERSION` installs latest, which may break flows when Maestro releases breaking changes.
- **Using api-level > 29 without checking app compatibility:** Higher API levels boot slower in CI and may require `google_apis` target, which is an x86 (not x86_64) image. API 29 / x86_64 is the sweet spot for speed and stability.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Android emulator in CI | Custom Docker/QEMU setup | reactivecircus/android-emulator-runner@v2 | Handles SDK install, AVD creation, boot wait, hardware acceleration — 500+ lines of complex logic |
| Slack notifications | curl to Slack API | slackapi/slack-github-action | Handles authentication, payload formatting, retry logic |
| Artifact upload | Custom S3/upload script | actions/upload-artifact@v4 | Built into GitHub, free, UI-integrated |
| HTML report generation | New reporter | Reuse run-maestro.sh Python inline block (lines 283-481) | The report generator already exists and produces the correct format for the dashboard |

**Key insight:** The hardest problem in this phase is not the CI plumbing — it's sourcing the APK. Every other component has a battle-tested solution. Don't invest time in emulator setup gymnastics; invest time in solving the APK distribution question first.

---

## Common Pitfalls

### Pitfall 1: APK Not Available in CI
**What goes wrong:** Workflow boots the emulator, then `adb install` fails with "file not found" or a private URL returns 403.
**Why it happens:** The YOM Ventas APK (me.youorder.yomventas) is not publicly distributed. There is no public download URL.
**How to avoid:** Decide on APK strategy before writing the workflow. Options: (a) pre-upload APK as a GitHub Actions artifact from a build pipeline and download via `gh` CLI, (b) store APK as a base64-encoded GitHub secret (max 48KB — too large for APKs), (c) store a signed S3/GCS download URL as a secret, (d) trigger this workflow only after a build workflow that uploads the APK as an artifact.
**Warning signs:** Workflow succeeds on validate-flows job but never actually tests the app.

### Pitfall 2: KVM Not Enabled — Emulator Boot Timeout
**What goes wrong:** Emulator runner times out waiting for device to boot (default 600 seconds).
**Why it happens:** Without the KVM udev rules step, ubuntu-latest falls back to software emulation which is 10-20x slower.
**How to avoid:** Always include the KVM enablement step before `reactivecircus/android-emulator-runner`. Verify by checking runner logs for "HAXM" or "KVM" acceleration messages.
**Warning signs:** Boot takes more than 5 minutes; you see "emulator: WARNING: Host does not support KVM" in logs.

### Pitfall 3: Maestro Cannot Find Flow Files
**What goes wrong:** `maestro test tests/app/flows/prinorte-session.yaml` fails because `runFlow: helpers/sync.yaml` resolves relative to the wrong directory.
**Why it happens:** Maestro resolves `runFlow` paths relative to the flow file's directory. If you run from a different working directory, helper paths break.
**How to avoid:** Either `cd tests/app/flows && maestro test prinorte-session.yaml` (changes cwd) or pass absolute paths consistently. The existing `run-maestro.sh` handles this implicitly — replicate the same cwd logic.
**Warning signs:** Error "Flow file not found: helpers/login.yaml" even though the file exists.

### Pitfall 4: Config Vars Not Injected
**What goes wrong:** Maestro uses `${APP_PACKAGE}` syntax in flow YAML. If `--env` flags are not passed, flows fail with "unresolved variable" or silently use empty strings causing unexpected app behavior.
**Why it happens:** `config.prinorte.yaml` (the local config file) cannot be committed to git because it contains credentials. CI must replicate this by passing the same 3 vars as `--env` flags.
**How to avoid:** Map config.prinorte.yaml env section to GitHub Actions secrets: APP_PACKAGE → `secrets.APP_PACKAGE`, TEST_SELLER_EMAIL → `secrets.TEST_SELLER_EMAIL`, TEST_SELLER_PASSWORD → `secrets.TEST_SELLER_PASSWORD`. Do NOT commit config.prinorte.yaml.
**Warning signs:** "NUNCA commitear este archivo" comment in config.prinorte.yaml — this is the signal.

### Pitfall 5: Session Flow Max Attempts = 1
**What goes wrong:** A single flaky step fails the entire session run with no retry.
**Why it happens:** run-maestro.sh sets `max_attempts = 1` for session flows (vs 3 for individual flows) because `clearState + launchApp` restart is expensive.
**How to avoid:** This is intentional behavior. CI should not fight this — instead, set `workflow_dispatch` trigger so nightly runs can be manually re-triggered if there's a one-off failure. Consider wrapping the session runner in a shell loop with max 2 attempts at the workflow level.
**Warning signs:** Single unexplained failures that pass on re-run.

### Pitfall 6: Google Password Manager Popup
**What goes wrong:** The Google Password Manager popup (`login.yaml` handles this) may appear differently on emulators vs. physical devices. The `optional: true` pattern in login.yaml is already defensive, but emulator-specific system apps may still interfere.
**Why it happens:** Emulator API 29+ includes Google services that trigger password manager dialogs on first login.
**How to avoid:** Use `target: default` (not `google_apis`) to avoid Google Play Services overhead, OR use a factory-reset emulator snapshot with `-no-snapshot` flag to ensure clean state.
**Warning signs:** Flow hangs at "Esperar pantalla principal" after login with no error.

---

## Code Examples

### Maestro --env flag injection (replaces config.prinorte.yaml in CI)

```bash
# Source: config.prinorte.yaml env section analysis
maestro test \
  --env APP_PACKAGE="me.youorder.yomventas" \
  --env TEST_SELLER_EMAIL="${TEST_SELLER_EMAIL}" \
  --env TEST_SELLER_PASSWORD="${TEST_SELLER_PASSWORD}" \
  tests/app/flows/prinorte-session.yaml
```

### KVM enablement (required before android-emulator-runner)

```yaml
# Source: ReactiveCircus/android-emulator-runner official docs
- name: Enable KVM
  run: |
    echo 'KERNEL=="kvm", GROUP="kvm", MODE="0666", OPTIONS+="static_node=kvm"' | sudo tee /etc/udev/rules.d/99-kvm4all.rules
    sudo udevadm control --reload-rules
    sudo udevadm trigger --name-match=kvm
```

### Maestro pinned install

```bash
# Source: Maestro official install docs — MAESTRO_VERSION env var supported
export MAESTRO_VERSION=1.40.0
curl -fsSL "https://get.maestro.mobile.dev" | bash
echo "$HOME/.maestro/bin" >> $GITHUB_PATH
```

### Nightly schedule + manual trigger

```yaml
# Source: GitHub Actions docs — schedule cron syntax
on:
  schedule:
    - cron: '0 6 * * *'   # 06:00 UTC daily = 03:00 CLT (off-hours)
  workflow_dispatch:        # manual re-trigger
```

### Upload artifacts with always()

```yaml
# Source: actions/upload-artifact@v4 docs
- uses: actions/upload-artifact@v4
  if: always()
  with:
    name: maestro-report-${{ github.run_id }}
    path: |
      QA/Prinorte/*/maestro.log
      public/app-reports/prinorte-*.html
    retention-days: 30
```

### Slack notification on failure

```yaml
# Source: slackapi/slack-github-action@v1.27.0 docs
- name: Notify Slack on failure
  if: failure()
  uses: slackapi/slack-github-action@v1.27.0
  with:
    payload: |
      {
        "text": "Maestro CI failed — Prinorte APP flows\nSee: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_MAESTRO_WEBHOOK }}
    SLACK_WEBHOOK_TYPE: INCOMING_WEBHOOK
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| macOS runners for Android emulator | ubuntu-latest + KVM | April 2024 (GitHub enabled KVM for 2-vCPU linux runners) | 2-3x faster, cheaper, no macOS premium |
| x86 arch emulators | x86_64 | 2023+ | Better compatibility with modern Android APIs |
| Maestro Cloud (paid) for CI | Self-hosted emulator + OSS Maestro | Ongoing | Free, no API key, secrets stay local |
| Separate notification workflows | `if: failure()` inline step | GitHub Actions v2+ | Simpler, no workflow_run event complexity |

**Deprecated/outdated:**
- `macos-12` runner for Android emulator: Still works but is expensive and slower. The 2024 KVM announcement made ubuntu-latest the recommended choice.
- Hardcoded Maestro versions above 1.40.0 without checking compatibility with flow YAML — Maestro has had breaking syntax changes between minor versions.

---

## Open Questions

1. **APK distribution strategy — BLOCKER**
   - What we know: `me.youorder.yomventas` APK must be installed before flows run. config.prinorte.yaml confirms the package name. The app is not publicly distributed.
   - What's unclear: Is there an existing internal download URL (S3, Firebase App Distribution, etc.)? Is there a build pipeline that produces APK artifacts? Can a pre-built APK be committed to a private GitHub release?
   - Recommendation: Planner should define this as Wave 0 discovery. If no URL exists, the first task should be: establish APK distribution mechanism (upload to GitHub release, or S3 pre-signed URL as secret). The workflow can be written with `APK_URL` secret as a placeholder — emulator job runs only if `secrets.APK_URL != ''`.

2. **Slack webhook availability**
   - What we know: The existing Slack workspace is used for engineering coordination (per CLAUDE.md).
   - What's unclear: Does a `#qa-alerts` channel or incoming webhook exist? Who can create it?
   - Recommendation: If no Slack webhook is available, fall back to creating a GitHub issue via `gh issue create` on failure — this requires no additional secrets.

3. **prinorte/12-precios-fotos.yaml exists but is NOT in prinorte-session.yaml**
   - What we know: `tests/app/flows/prinorte/` has 12 flows (01-12) but `prinorte-session.yaml` only includes flows 01-11.
   - What's unclear: Is flow 12 intentionally excluded? Should CI run the same session as local (excluding 12) or a different set?
   - Recommendation: CI should run exactly `prinorte-session.yaml` as-is — do not second-guess what the session file includes.

---

## Validation Architecture

Note: `workflow.nyquist_validation` is not set in `.planning/config.json` — treating as enabled.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Maestro CLI 1.40.0 |
| Config file | `tests/app/config/config.prinorte.yaml` (local) / GitHub Secrets (CI) |
| Quick run command | `maestro test tests/app/flows/prinorte-session.yaml --env APP_PACKAGE=... --env TEST_SELLER_EMAIL=... --env TEST_SELLER_PASSWORD=...` |
| Full suite command | Same — prinorte-session.yaml is the full suite orchestrator |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REQ-07 | Nightly workflow triggers on cron schedule | smoke | Trigger via `workflow_dispatch` and verify run completes | ❌ Wave 0 — create `.github/workflows/app-maestro.yml` |
| REQ-07 | Artifacts (log + HTML) uploaded after run | integration | Check `actions/upload-artifact` step produces `maestro-report-*` artifact | ❌ Wave 0 — workflow creation |
| REQ-07 | Failure notification sent on non-zero exit | integration | Force failure (bad credentials), verify Slack message received | ❌ Wave 0 — workflow creation |
| REQ-07 | Works on emulator (no physical device) | integration | ubuntu-latest runner with KVM confirms no device attached | ❌ Wave 0 — workflow creation |

### Sampling Rate

- **Per task commit:** Validate YAML syntax — `yamllint .github/workflows/app-maestro.yml`
- **Per wave merge:** Manual `workflow_dispatch` trigger and verify run completes or APK-gate is correctly skipped
- **Phase gate:** Full nightly run producing artifact + Slack notification before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `.github/workflows/app-maestro.yml` — the workflow file to create (REQ-07)
- [ ] GitHub Actions secrets: `APK_URL`, `APP_PACKAGE`, `TEST_SELLER_EMAIL`, `TEST_SELLER_PASSWORD`, `SLACK_MAESTRO_WEBHOOK` — must be set in repo settings
- [ ] APK distribution decision — required before emulator job can actually run (see Open Questions #1)

---

## Sources

### Primary (HIGH confidence)
- [ReactiveCircus/android-emulator-runner GitHub Marketplace](https://github.com/marketplace/actions/android-emulator-runner) — KVM setup, inputs, API level recommendations, ubuntu-latest support
- [GitHub Changelog: Hardware accelerated Android virtualization](https://github.blog/changelog/2024-04-02-github-actions-hardware-accelerated-android-virtualization-now-available/) — Confirmed ubuntu-latest 2-vCPU KVM support since April 2024
- [Maestro CLI install docs](https://docs.maestro.dev/maestro-cli/how-to-install-maestro-cli) — Install command, MAESTRO_VERSION env var, Java 17 requirement
- `tools/run-maestro.sh` (local file) — MAESTRO_MIN_VERSION=1.40.0, config.yaml --env injection logic, HTML report generation Python
- `tests/app/config/config.prinorte.yaml` (local file) — Exact 3 env vars needed: APP_PACKAGE, TEST_SELLER_EMAIL, TEST_SELLER_PASSWORD
- `tests/app/flows/prinorte-session.yaml` (local file) — Session structure: 11 sub-flows, clearState+launchApp, helpers/login.yaml and helpers/sync.yaml dependencies
- `.github/workflows/deploy-qa-dashboard.yml` (local file) — Existing workflow pattern: actions/checkout@v4, peaceiris/actions-gh-pages@v3, ubuntu-latest

### Secondary (MEDIUM confidence)
- [slackapi/slack-github-action v1.27.0](https://github.com/marketplace/actions/notify-slack-action) — Slack failure notification pattern; verified as maintained action
- [retyui/Using-GitHub-Actions-to-run-your-Maestro-Flows](https://github.com/retyui/Using-GitHub-Actions-to-run-your-Maestro-Flows) — Community reference confirming ubuntu approach; notes macos is more stable but slower/expensive
- [Medium: Built a Visual Android UI Test Pipeline with Maestro](https://medium.com/@carlosjimz87/built-a-visual-android-ui-test-pipeline-with-maestro-664cc1d6f8bd) — Docker-android alternative pattern; confirmed APK install via adb pattern

### Tertiary (LOW confidence)
- [GitHub Issue #1783: maestro validate dry-run](https://github.com/mobile-dev-inc/Maestro/issues/1783) — Confirms no native dry-run/syntax-only mode as of July 2024; feature requested but not confirmed shipped

---

## Metadata

**Confidence breakdown:**
- Standard stack (emulator runner, KVM, Maestro install): HIGH — verified via official GitHub Marketplace listing and Maestro install docs
- Architecture (workflow structure, secret injection): HIGH — based on existing local script analysis + official action patterns
- APK blocker identification: HIGH — confirmed by config.prinorte.yaml inspection (credentials present, "NUNCA commitear" warning)
- Pitfalls: MEDIUM — KVM and cwd pitfalls verified; session max_attempts=1 verified from run-maestro.sh source; popup handling is LOW (emulator behavior is environment-specific)
- Notification (Slack): MEDIUM — slackapi/slack-github-action is the standard approach; webhook availability in this org is unknown

**Research date:** 2026-04-17
**Valid until:** 2026-05-17 (stable ecosystem; KVM support and Maestro install API are unlikely to change)
