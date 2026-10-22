"""Save an auditable report of real PRs merged during this workflow run."""
from datetime import datetime, timezone
import base64
import json
import os
from pathlib import Path
import subprocess


def command(*args):
    return subprocess.check_output(args, text=True).strip()


def api(path):
    return json.loads(command("gh", "api", path))


def published_prs(started_at):
    repos = json.loads(command("gh", "repo", "list", "OAndrei314", "--limit", "100",
                               "--json", "nameWithOwner,pushedAt"))
    found = []
    for repo in repos:
        name = repo["nameWithOwner"]
        if name.endswith("/daily-portfolio-automation") or repo["pushedAt"] < started_at:
            continue
        pulls = api(f"repos/{name}/pulls?state=closed&sort=updated&direction=desc&per_page=30")
        merged = [p for p in pulls if p.get("merged_at") and p["merged_at"] >= started_at]
        if not merged:
            continue
        readme = api(f"repos/{name}/readme")
        text = base64.b64decode(readme["content"]).decode("utf-8")
        if "Maintained by: claude-actions-daily-routine" not in text:
            continue
        for pull in merged:
            found.append({"repository": name, "title": pull["title"],
                          "url": pull["html_url"], "merged_at": pull["merged_at"],
                          "merge_commit_sha": pull["merge_commit_sha"]})
    return sorted(found, key=lambda p: p["url"])


if __name__ == "__main__":
    run = api(f"repos/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{os.environ['GITHUB_RUN_ID']}")
    pulls = published_prs(run["run_started_at"])
    if not pulls:
        raise SystemExit("No merged project PR verified for this run; refusing to report success.")
    now = datetime.now(timezone.utc)
    relative = f"reports/{now:%Y-%m-%d}-{os.environ['GITHUB_RUN_ID']}.json"
    path = Path(relative)
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps({"workflow_run": run["html_url"], "published_prs": pulls}, indent=2) + "\n")
    command("git", "config", "user.name", "OAndrei314")
    command("git", "config", "user.email", "56999057+OAndrei314@users.noreply.github.com")
    command("git", "pull", "--ff-only", "origin", "main")
    command("git", "add", "--", relative)
    command("git", "commit", "-m", f"Record verified portfolio work {now:%Y-%m-%d}")
    command("git", "push", "origin", "HEAD:main")
    print(f"Recorded {len(pulls)} verified merged PR(s) in {relative}")
