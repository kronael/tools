#!/usr/bin/env python3
import importlib.util
import json
import os
import re
import sys

spec = importlib.util.spec_from_file_location(
    "toolchain", os.path.expanduser("~/.claude/hooks/lib/toolchain.py")
)
toolchain = importlib.util.module_from_spec(spec)
spec.loader.exec_module(toolchain)
get_redirect_command = toolchain.get_redirect_command

try:
    data = json.load(sys.stdin)
except (json.JSONDecodeError, EOFError, ValueError):
    sys.exit(0)

if not isinstance(data, dict):
    sys.exit(0)

if data.get("tool_name") != "Bash":
    sys.exit(0)

cmd = data.get("tool_input", {}).get("command", "")
if not isinstance(cmd, str):
    sys.exit(0)

cwd = data.get("cwd") or ""

# Escape hatch: prefix with ! to bypass redirect
if cmd.startswith("!"):
    sys.exit(0)

# Operation detectors (intent -> action)
DETECTORS = [
    # TEST: run whole test suite
    (r"^(npm|yarn|pnpm)\s+(test|run\s+test)\b", "test"),
    (r"^pytest\b", "test"),
    (r"^go\s+test\b", "test"),
    (r"^cargo\s+test\b", "test"),
    (r"^python\s+-m\s+pytest\b", "test"),
    (r"^uv\s+run\s+pytest\b", "test"),
    # BUILD: run complete build
    (r"^(npm|yarn|pnpm)\s+(build|run\s+build)\b", "build"),
    (r"^go\s+build\b", "build"),
    (r"^cargo\s+build\b", "build"),
    (r"^tsc\b", "build"),
    # LINT: run linter
    (r"^(npm|yarn|pnpm)\s+(lint|run\s+lint)\b", "lint"),
    (r"^cargo\s+clippy\b", "lint"),
    (r"^go\s+vet\b", "lint"),
    (r"^ruff\s+check\b", "lint"),
    # E2E: run e2e/integration tests
    (r"\be2e\b", "e2e"),
    (r"\bintegration\b", "e2e"),
    (r"\bplaywright\b", "e2e"),
    (r"\bcypress\b", "e2e"),
    # SMOKE: longer test suite
    (r"\bsmoke\b", "smoke"),
]

# Detect and redirect
for pattern, action in DETECTORS:
    if re.search(pattern, cmd, re.IGNORECASE):
        redirect = get_redirect_command(cwd, action)
        if redirect and redirect != cmd:
            print(
                json.dumps(
                    {
                        "ok": True,
                        "hookSpecificOutput": {
                            "hookEventName": "PreToolUse",
                            "permissionDecision": "allow",
                            "permissionDecisionReason": f"Redirected: {action}",
                            "updatedInput": {"command": redirect},
                        },
                    }
                )
            )
            sys.exit(0)
        break

sys.exit(0)
