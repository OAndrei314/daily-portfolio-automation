# daily-portfolio-automation

Infrastructure, not a portfolio project: this repo hosts the GitHub Actions workflow that
runs a daily, autonomous Claude Code session against the rest of the
[OAndrei314](https://github.com/OAndrei314) portfolio.

## Why this exists, and why it's a separate repo

The daily job needs to touch many repos (clone, extend, occasionally create a new one) —
that doesn't belong inside any single portfolio project's own Actions tab, so it lives here
instead. This repo has no code of its own; it's the scheduler.

## How it works

- `.github/workflows/daily-routine.yml` fires on 6 `schedule:` cron triggers spanning
  15:00-01:00 UTC (~17:00-03:00 CEST) — plus `workflow_dispatch` for manual/verification runs,
  which skip all the randomization below and run immediately.
- Each of the 6 trigger points independently rolls dice on whether it actually does anything
  (a real workflow step, not just a prompt instruction, so it can't be skipped by a bad
  interpretation). It uses live GitHub search as shared state across the day's triggers — no
  database needed: if nothing has landed yet today, this slot has a ~27% chance of being the
  one that fires (solving for `1-(1-p)^6 = 0.85` across 6 slots); if something already landed
  today, it has a smaller ~8% chance of producing a rare second push. Net effect: pushes land
  on ~85% of days (comfortably ≥5 days/week in expectation) at a randomized point in the
  window, and occasionally twice in one day — without ever needing a single job to sleep for
  hours (each slot's intra-slot jitter tops out at 100 minutes, well under GitHub's ~6h job
  timeout).
- [`anthropics/claude-code-action@v1`](https://github.com/anthropics/claude-code-action)
  then runs a single, self-contained daily-task prompt (see the workflow file for the full
  text) that: finds the single hottest thing happening in AI right now, discovers the current
  state of the portfolio via `gh repo list`, picks the least-recently-touched repo it owns
  that isn't marked done, either extends it with one genuine improvement or founds a
  brand-new project if that repo is honestly complete, verifies everything with real tests,
  and opens + merges a real PR.
- Cross-repo access (cloning/pushing/creating repos beyond this one) uses a GitHub PAT, not
  the default `GITHUB_TOKEN` — the built-in token is scoped only to the repo a workflow runs
  in, which isn't enough for a job that rotates across an entire account's repos. The same PAT
  is also passed as the action's own `github_token` input, which sidesteps the need to install
  the official Claude GitHub App.

## Ownership boundary and the Status signal

A second, independent automation (Codex-based, running locally via Windows Task Scheduler)
also contributes to this account, on a disjoint set of repos. Both sides check for and set a
`Maintained by: <agent>-daily-routine` marker line in each repo's README to stay out of each
other's way — see the workflow prompt for the exact rule.

Each repo this automation owns also carries a `Status: Active` / `Status: Complete` marker
next to that line — a persistent, explicit "is this project still being extended" signal, so
the daily run doesn't have to re-derive completeness from scratch by re-reading a whole
codebase every time. The rotation target is a **6-8 Active-project band**, not a fixed count:
below 6, a genuinely-done repo gets flipped to `Status: Complete` (with an honest one-paragraph
justification) and a new project is founded to replace it; at 8, existing projects keep getting
extended instead. Completed repos stay in the account permanently as a real track record — they
just stop being rotation targets.

## Weekly local report

`local/weekly-report.ps1` is a separate, deliberately non-agentic piece: a deterministic script
(no LLM call, so it's instant and free) that pulls every PR merged across the whole
`OAndrei314` account in the trailing 7 days via `gh search prs` and renders it to a local HTML
file. It exists because the cloud workflow above runs on a GitHub-hosted runner, which has no
access to this machine's disk — genuinely local output needs something that actually runs
locally. It's registered as a weekly Windows Scheduled Task (`PortfolioWeeklyReport`, Mondays
08:00) and writes to `~/Documents/github_projects/weekly-reports/latest.html` (plus a dated
copy per run) — open that file directly in a browser, no server involved.

## Required repo secrets

- `CLAUDE_CODE_OAUTH_TOKEN` — authenticates via an existing Claude Pro/Max subscription
  instead of pay-per-token API billing. Generate it locally with `claude setup-token`
  (requires an active subscription and its own browser login) and paste the resulting token
  in as the secret value.
- `GH_PAT` — a GitHub personal access token (classic, `repo` + `workflow` scopes) so the
  workflow can reach repos beyond this one.

Neither secret is stored anywhere in this repo's history — add them directly via
**Settings → Secrets and variables → Actions** on GitHub.

## License

MIT — see [LICENSE](LICENSE).
