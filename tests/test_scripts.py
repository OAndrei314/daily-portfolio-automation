import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch


def load(name):
    path = Path(__file__).resolve().parents[1] / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ScriptTests(unittest.TestCase):
    def test_expired_oauth_is_actionable_without_echoing_secret(self):
        result = load("diagnose_failure").classify("OAuth token has expired: SECRET")
        self.assertIn("renew CLAUDE_CODE_OAUTH_TOKEN", result)
        self.assertNotIn("SECRET", result)

    def test_report_filters_old_prs_and_other_automations(self):
        report = load("record_run")
        repos = '[{"nameWithOwner":"OAndrei314/new-lab","pushedAt":"2026-10-22T18:00:00Z"}]'
        pulls = [{"merged_at": "2026-10-21T18:00:00Z"},
                 {"merged_at": "2026-10-22T18:00:00Z", "title": "Implement lab",
                  "html_url": "https://github.com/OAndrei314/new-lab/pull/1", "merge_commit_sha": "abc"}]
        import base64
        for marker, expected in [("codex-daily-routine", 0), ("claude-actions-daily-routine", 1)]:
            with patch.object(report, "command", return_value=repos), patch.object(report, "api", side_effect=[
                pulls, {"content": base64.b64encode(f"Maintained by: {marker}".encode()).decode()}
            ]):
                self.assertEqual(len(report.published_prs("2026-10-22T17:00:00Z")), expected)


if __name__ == "__main__":
    unittest.main()
