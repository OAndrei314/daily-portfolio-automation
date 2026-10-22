# Restoration record: 2026-10-22

## Verified working

- The local daily task completed successfully after recovery (`LastTaskResult: 0`).
  It remains scheduled daily at 17:00 Europe/Berlin. Today's source-linked research
  batch covered eight repositories, with seven project-note pushes plus the digest.
- Fixed a publication-guard false positive on `500K context`. Compensation language
  remains blocked. The digest suite passes 30 tests; GitHub CI passes.
- Native command failures in the local runner now stop the run instead of allowing
  a failed test or git operation to be recorded as success.
- Both GitHub workflows in this repository are active. Scheduler tests pass on
  Python 3.10 and 3.12.
- Published [checkpoint-recovery-lab](https://github.com/OAndrei314/checkpoint-recovery-lab)
  and merged its [implementation PR](https://github.com/OAndrei314/checkpoint-recovery-lab/pull/1)
  after 21 offline tests and Python 3.10/3.12 CI passed. It includes a runnable CLI,
  failure-trace replay, and reproduced synthetic results.

## Cloud changes

The old scheduler had been disabled by GitHub repository inactivity. It is enabled
again, checks out this repository before invoking the agent, attempts work daily at
15:11 UTC, and no longer randomly skips work. New projects are requested explicitly
with `project_mode: new`, or by the automatic seven-day creation rule. Concurrent
sessions are serialized. The success step verifies merged PRs and records useful
publication reports here so work elsewhere does not leave this repository idle.

## Remaining credential action

The [cloud verification run](https://github.com/OAndrei314/daily-portfolio-automation/actions/runs/39825810915)
failed Claude authentication before doing implementation work. The diagnostic step
confirmed the authentication failure without exposing its transcript or token.
Cloud project generation is therefore **not yet verified working**.

On Windows, run `claude.cmd setup-token` in a terminal and sign in using the Claude
subscription account. Replace `CLAUDE_CODE_OAUTH_TOKEN` in this repository's Actions
secrets, then manually run `Daily Portfolio Contribution` to verify it. Keep the token
out of commits, issues, and chat. No repository or script change can supply that login.
