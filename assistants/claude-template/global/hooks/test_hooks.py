#!/usr/bin/env python3
"""Smoke tests for hooks system.

Tests JSON parse guards, null/type guards, word-boundary matching,
keyword routing, and negation handling for the hooks that ship with
this template: nudge.py, local.py, learn.py, stop.py.
"""
import json
import subprocess
import sys
from pathlib import Path


class HooksTestSuite:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
        self.hooks_dir = Path.home() / ".claude" / "hooks"

    def test(self, name, script, input_data, expect_crash=False, expect_output=None):
        script_path = self.hooks_dir / script
        try:
            result = subprocess.run(
                ["python3", str(script_path)],
                input=input_data.encode() if input_data else b"",
                capture_output=True,
                timeout=2,
            )
            crashed = result.returncode != 0
            output = result.stdout.decode()

            if expect_crash and not crashed:
                self.failed += 1
                self.tests.append(f"✗ {name} - Expected crash but didn't")
                return False

            if not expect_crash and crashed:
                self.failed += 1
                stderr = result.stderr.decode()[:100]
                self.tests.append(f"✗ {name} - Unexpected crash: {stderr}")
                return False

            if expect_output and expect_output not in output:
                self.failed += 1
                self.tests.append(f"✗ {name} - Expected '{expect_output}' in output")
                return False

            if expect_output is None and output:
                self.failed += 1
                self.tests.append(f"✗ {name} - Unexpected output: {output[:50]}")
                return False

            self.passed += 1
            self.tests.append(f"✓ {name}")
            return True

        except subprocess.TimeoutExpired:
            self.failed += 1
            self.tests.append(f"✗ {name} - Timeout")
            return False
        except Exception as e:
            self.failed += 1
            self.tests.append(f"✗ {name} - Error: {e}")
            return False

    def run_all(self):
        print("=" * 70)
        print("HOOKS SYSTEM TEST SUITE")
        print("=" * 70)

        print("\n[JSON Parse Guards]")
        print("-" * 70)
        self.test("nudge.py - empty input", "nudge.py", "")
        self.test("nudge.py - bad JSON", "nudge.py", "{incomplete")
        self.test("nudge.py - array input", "nudge.py", "[]")
        self.test("local.py - empty input", "local.py", "")
        self.test("local.py - bad JSON", "local.py", "{x:")
        self.test("local.py - array input", "local.py", "[]")
        self.test("learn.py - empty input", "learn.py", "")
        self.test("learn.py - bad JSON", "learn.py", "{incomplete json")
        self.test("stop.py - empty input", "stop.py", "")
        self.test("stop.py - bad JSON", "stop.py", "{bad")

        print("\n[Null & Type Guards]")
        print("-" * 70)
        self.test("nudge.py - null prompt", "nudge.py", json.dumps({"prompt": None}))
        self.test(
            "nudge.py - dict prompt",
            "nudge.py",
            json.dumps({"prompt": {"bad": "type"}}),
        )
        self.test(
            "local.py - dict prompt",
            "local.py",
            json.dumps({"prompt": {"nested": "dict"}}),
        )

        print("\n[local.py Word Boundaries]")
        print("-" * 70)
        self.test(
            "local.py - 'thecontinueword' does NOT inject",
            "local.py",
            json.dumps({"prompt": "thecontinueword"}),
            expect_output=None,
        )
        self.test(
            "local.py - 'recap_session' does NOT inject",
            "local.py",
            json.dumps({"prompt": "recap_session"}),
            expect_output=None,
        )

        print("\n[nudge.py Keyword Routing]")
        print("-" * 70)
        self.test(
            "nudge.py - 'improve code' → @improve",
            "nudge.py",
            json.dumps({"prompt": "improve code"}),
            expect_output="@improve",
        )
        self.test(
            "nudge.py - 'visual' → @visual",
            "nudge.py",
            json.dumps({"prompt": "visual"}),
            expect_output="@visual",
        )
        self.test(
            "nudge.py - 'ship' → /ship",
            "nudge.py",
            json.dumps({"prompt": "ship it"}),
            expect_output="/ship",
        )
        self.test(
            "nudge.py - 'diary' → /diary",
            "nudge.py",
            json.dumps({"prompt": "diary"}),
            expect_output="/diary",
        )
        self.test(
            "nudge.py - 'commit' → Commit rules",
            "nudge.py",
            json.dumps({"prompt": "commit changes"}),
            expect_output="Commit rules",
        )
        self.test(
            "nudge.py - 'readme' → @readme",
            "nudge.py",
            json.dumps({"prompt": "write readme"}),
            expect_output="@readme",
        )

        print("\n[local.py Negation Handling]")
        print("-" * 70)
        self.test(
            "local.py - 'dont continue' does NOT inject",
            "local.py",
            json.dumps({"prompt": "dont continue"}),
            expect_output=None,
        )
        self.test(
            "local.py - 'never recap' does NOT inject",
            "local.py",
            json.dumps({"prompt": "never recap"}),
            expect_output=None,
        )

        print("\n[local.py Positive Cases]")
        print("-" * 70)
        self.test(
            "local.py - 'continue' → inject rules",
            "local.py",
            json.dumps({"prompt": "continue with implementation"}),
            expect_output="systemMessage",
        )
        self.test(
            "local.py - 'where were we' → inject rules",
            "local.py",
            json.dumps({"prompt": "where were we"}),
            expect_output="systemMessage",
        )

        print("\n" + "=" * 70)
        print("TEST RESULTS")
        print("=" * 70)
        for t in self.tests:
            print(t)

        print("\n" + "=" * 70)
        total = self.passed + self.failed
        status = "✓ PASS" if self.failed == 0 else "✗ FAIL"
        print(f"{status}: {self.passed}/{total} tests passed")
        print("=" * 70)

        return self.failed == 0


if __name__ == "__main__":
    suite = HooksTestSuite()
    sys.exit(0 if suite.run_all() else 1)
