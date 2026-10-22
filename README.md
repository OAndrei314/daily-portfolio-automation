# Daily portfolio automation

Runs substantive daily work across the OAndrei314 AI, ML, and hardware portfolio.
This repository contains scheduling infrastructure and verified publication reports.

## Schedule and new projects

The GitHub Actions workflow attempts work every day at **15:11 UTC** (17:11 CEST /
16:11 CET). It no longer randomly skips days. GitHub may delay scheduled starts.
A concurrency group prevents two portfolio sessions from modifying the same repos at once.

Each run discovers the live portfolio, reads current primary sources, and either implements
one tested improvement or creates a distinct new project. If this automation has not created
a project in the trailing seven days, the next successful run must create one. The active
project count is a preference; it cannot block that cadence or justify falsely marking a
project complete. New projects require implementation, offline tests, examples, and passing CI.

Use **Actions > Daily Portfolio Contribution > Run workflow > project_mode: new** to request
a new project immediately. `auto` follows the daily rotation and weekly creation rule.

The agent clones a project, implements and tests the change, opens a PR, waits for CI,
and merges only after checks pass. It must not publish filler or fabricate results.
The action starts from a checkout of this repository so its git configuration works.

## Publication verification and recovery

`scripts/record_run.py` independently verifies that the run merged a project PR and saves
its repository, title, URL, merge time, and commit in `reports/`. A run without verified
published work fails. These useful reports also keep this scheduler repository active;
previously GitHub disabled it after 60 days without repository activity even while its
workflow was contributing to other repositories.

On agent failure, `scripts/diagnose_failure.py` classifies authentication, model access,
usage, and billing errors without printing a transcript or credentials. Renew credentials
when required, then use a manual workflow run to verify recovery.

## Ownership

Cloud projects carry `Maintained by: claude-actions-daily-routine` and `Status: Active` or
`Status: Complete` in the README. The cloud routine excludes personal repositories and
projects maintained by the independent local Codex or legacy Claude routines. Completed
projects remain available. Never retire an unfinished project just to hit a project count.

The Windows task **OAndrei314 Codex Daily News Routine** remains a separate source-linked
research digest at 17:00 Europe/Berlin. It publishes notes to its own repositories and is
not an implementation agent. Its code lives in `ai-infra-optics-digest`.

## Required secrets

- `CLAUDE_CODE_OAUTH_TOKEN`: Claude subscription authentication, generated with `claude setup-token`.
- `GH_PAT`: cross-repository GitHub access with `repo` and `workflow` scopes.

Store these in GitHub Actions secrets. They are not repository files.

## Local weekly report

`local/weekly-report.ps1` produces a local HTML report of PRs merged across the account in
the trailing seven days. The Windows task `PortfolioWeeklyReport` runs Mondays at 08:00.
The report remains local under `Documents/github_projects/weekly-reports/latest.html`.

## Validation

Run `python -m unittest discover -s tests -v`. The tests cover credential-safe failure
diagnostics and verification of merged PRs within the current run and ownership boundary.

## License

MIT; see [LICENSE](LICENSE).
