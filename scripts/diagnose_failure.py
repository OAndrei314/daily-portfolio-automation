"""Classify an agent failure without publishing its transcript or credentials."""
import json
import os
from pathlib import Path
import re


def classify(text):
    patterns = (
        (r"oauth.{0,50}expir|token.{0,30}expir", "Claude OAuth token expired; renew CLAUDE_CODE_OAUTH_TOKEN."),
        (r"invalid.{0,30}(token|api.key)|authentication|not logged in|unauthorized|401", "Claude authentication failed; check CLAUDE_CODE_OAUTH_TOKEN."),
        (r"credit balance|billing|subscription", "Claude billing or subscription access failed."),
        (r"rate.limit|usage.limit|limit.reached|429", "Claude usage limit reached."),
        (r"model.{0,80}(not found|not exist|not available|access)|404", "Configured Claude model is unavailable to this account."),
    )
    for pattern, message in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return message
    return "Claude failed before publishing. Inspect the private execution output; no transcript was exposed."


if __name__ == "__main__":
    data = json.loads(Path(os.environ["EXECUTION_FILE"]).read_text())
    # Result/error messages describe the failure; tool transcripts can mention unrelated errors.
    messages = data if isinstance(data, list) else [data]
    errors = [m for m in messages if isinstance(m, dict) and (m.get("is_error") or m.get("type") == "error")]
    print("::error::" + classify(json.dumps(errors or messages[-1:])))
