#!/usr/bin/env python3
"""
Comprehensive test suite for hooks system.
Tests all 12 crashes and 3 logic bugs fixed.
"""
import subprocess
import json
import sys
from pathlib import Path


class HooksTestSuite:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
        self.hooks_dir = Path.home() / ".claude" / "hooks"

    def test(self, name, script, input_data, expect_crash=False, expect_output=None):
        """Run a single test."""
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

            # Check crash expectation
            if expect_crash and not crashed:
                self.failed += 1
                self.tests.append(f"✗ {name} - Expected crash but didn't")
                return False

            if not expect_crash and crashed:
                self.failed += 1
                stderr = result.stderr.decode()[:100]
                self.tests.append(f"✗ {name} - Unexpected crash: {stderr}")
                return False

            # Check output expectation
            if expect_output and expect_output not in output:
                self.failed += 1
                self.tests.append(f"✗ {name} - Expected '{expect_output}' in output")
                return False

            if expect_output is None and output:
                # Unexpected output (should be silent)
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
        """Run all tests."""
        print("=" * 70)
        print("HOOKS SYSTEM TEST SUITE")
        print("=" * 70)

        print("\n[PRIORITY 1: System Breaking Crashes]")
        print("-" * 70)

        # 1. JSON Parsing - No Error Handling
        print("\nJSON Parsing Error Handling:")
        self.test("redirect.py - empty input", "redirect.py", "")
        self.test("redirect.py - bad JSON", "redirect.py", "{bad json}")
        self.test("redirect.py - array input", "redirect.py", "[]")
        self.test("nudge.py - empty input", "nudge.py", "")
        self.test("nudge.py - bad JSON", "nudge.py", "{incomplete")
        self.test("nudge.py - array input", "nudge.py", "[]")
        self.test("context.py - empty input", "context.py", "")
        self.test("context.py - bad JSON", "context.py", "{x:")
        self.test("context.py - array input", "context.py", "[]")
        self.test("learn.py - empty input", "learn.py", "")
        self.test("learn.py - bad JSON", "learn.py", "{incomplete json")

        # 2. Null Value Crashes
        print("\nNull Value & Type Error Handling:")
        self.test("nudge.py - null prompt", "nudge.py", json.dumps({"prompt": None}))
        self.test("nudge.py - dict prompt", "nudge.py", json.dumps({"prompt": {"bad": "type"}}))
        self.test(
            "redirect.py - dict command",
            "redirect.py",
            json.dumps({"tool_input": {"command": {"nested": "dict"}}}),
        )
        self.test(
            "redirect.py - null command",
            "redirect.py",
            json.dumps({"tool_input": {"command": None}}),
        )
        self.test("context.py - null prompt", "context.py", json.dumps({"prompt": None}))
        self.test(
            "context.py - dict prompt",
            "context.py",
            json.dumps({"prompt": {"nested": "dict"}}),
        )

        print("\n[PRIORITY 2: Logic Bugs]")
        print("-" * 70)

        # 3. context.py Substring Matching Bug
        print("\nWord Boundary Matching (no false positives):")
        self.test(
            "context.py - 'thecontinueword' should NOT inject",
            "context.py",
            json.dumps({"prompt": "thecontinueword"}),
            expect_output=None,
        )
        self.test(
            "context.py - 'recap_session' should NOT inject",
            "context.py",
            json.dumps({"prompt": "recap_session"}),
            expect_output=None,
        )

        # 4. nudge.py Keyword Priority Bug
        print("\nKeyword Priority (specific patterns before generic):")
        self.test(
            "nudge.py - 'fix styling' → /visual",
            "nudge.py",
            json.dumps({"prompt": "fix styling"}),
            expect_output="/visual",
        )
        self.test(
            "nudge.py - 'fix ui' → /visual",
            "nudge.py",
            json.dumps({"prompt": "fix ui"}),
            expect_output="/visual",
        )
        self.test(
            "nudge.py - 'improve code' → /improve",
            "nudge.py",
            json.dumps({"prompt": "improve code"}),
            expect_output="/improve",
        )

        # 5. context.py Negation Not Handled
        print("\nNegation Detection:")
        self.test(
            "context.py - 'dont continue' should NOT inject",
            "context.py",
            json.dumps({"prompt": "dont continue"}),
            expect_output=None,
        )
        self.test(
            "context.py - 'don't continue' should NOT inject",
            "context.py",
            json.dumps({"prompt": "don't continue"}),
            expect_output=None,
        )
        self.test(
            "context.py - 'never recap' should NOT inject",
            "context.py",
            json.dumps({"prompt": "never recap"}),
            expect_output=None,
        )

        print("\n[POSITIVE CASES: Normal Behavior]")
        print("-" * 70)

        print("\nContext.py - Should inject rules:")
        self.test(
            "context.py - 'continue' → inject rules",
            "context.py",
            json.dumps({"prompt": "continue"}),
            expect_output="systemMessage",
        )
        self.test(
            "context.py - 'recap' → inject rules",
            "context.py",
            json.dumps({"prompt": "recap"}),
            expect_output="systemMessage",
        )
        self.test(
            "context.py - 'where were we' → inject rules",
            "context.py",
            json.dumps({"prompt": "where were we"}),
            expect_output="systemMessage",
        )
        self.test(
            "context.py - 'what's next' → inject rules",
            "context.py",
            json.dumps({"prompt": "what's next"}),
            expect_output="systemMessage",
        )

        print("\nNudge.py - Should inject agent hints:")
        self.test(
            "nudge.py - 'commit' → /commit rules",
            "nudge.py",
            json.dumps({"prompt": "commit changes"}),
            expect_output="Commit rules",
        )
        self.test(
            "nudge.py - 'refactor' → /improve",
            "nudge.py",
            json.dumps({"prompt": "refactor this"}),
            expect_output="/improve",
        )
        self.test(
            "nudge.py - 'write docs' → /readme",
            "nudge.py",
            json.dumps({"prompt": "write docs"}),
            expect_output="/readme",
        )

        # Summary
        print("\n" + "=" * 70)
        print("TEST RESULTS")
        print("=" * 70)
        for test in self.tests:
            print(test)

        print("\n" + "=" * 70)
        total = self.passed + self.failed
        status = "✓ PASS" if self.failed == 0 else "✗ FAIL"
        print(f"{status}: {self.passed}/{total} tests passed")
        print("=" * 70)

        return self.failed == 0


if __name__ == "__main__":
    suite = HooksTestSuite()
    success = suite.run_all()
    sys.exit(0 if success else 1)
