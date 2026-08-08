# daily-portfolio-automation

Infrastructure, not a portfolio project: this repo hosts the GitHub Actions workflow that
runs a daily, autonomous Claude Code session against the rest of the
[OAndrei314](https://github.com/OAndrei314) portfolio.

## Why this exists, and why it's a separate repo

The daily job needs to touch many repos (clone, extend, occasionally create a new one) —
that doesn't belong inside any single portfolio project's own Actions tab, so it lives here
instead. This repo has no code of its own; it's the scheduler.

## How it works

- `.github/workflows/daily-routine.yml` runs on a daily `schedule:` cron trigger (plus
  `workflow_dispatch` for manual runs).
- A real jitter delay (0-3h, `sleep $(( RANDOM % 10800 ))`) runs as an explicit workflow
  step *before* Claude Code starts, so the actual commit/PR timestamp on the target repos
  varies day to day instead of landing at the same minute every time — this is a workflow
  step, not just an instruction in the prompt, so it can't be skipped by a bad interpretation.
- [`anthropics/claude-code-action@v1`](https://github.com/anthropics/claude-code-action)
  then runs a single, self-contained daily-task prompt (see the workflow file for the full
  text) that: scans live AI news for anything extraordinary, discovers the current state of
  the portfolio via `gh repo list`, picks the least-recently-touched repo it owns, either
  extends it with one genuine improvement or founds a brand-new project if that repo is
  honestly complete, verifies everything with real tests, and opens + merges a real PR.
- Cross-repo access (cloning/pushing/creating repos beyond this one) uses a GitHub PAT, not
  the default `GITHUB_TOKEN` — the built-in token is scoped only to the repo a workflow runs
  in, which isn't enough for a job that rotates across an entire account's repos.

## Ownership boundary

A second, independent automation (Codex-based, running locally via Windows Task Scheduler)
also contributes to this account, on a disjoint set of repos. Both sides check for and set a
`Maintained by: <agent>-daily-routine` marker line in each repo's README to stay out of each
other's way — see the workflow prompt for the exact rule.

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
