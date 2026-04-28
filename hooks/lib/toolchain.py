import os


def detect_package_manager(cwd: str) -> str:
    if os.path.exists(os.path.join(cwd, "pnpm-lock.yaml")):
        return "pnpm"
    if os.path.exists(os.path.join(cwd, "yarn.lock")):
        return "yarn"
    if os.path.exists(os.path.join(cwd, "package-lock.json")):
        return "npm"
    if os.path.exists(os.path.join(cwd, "package.json")):
        return "pnpm"  # default to pnpm
    return ""


def has_makefile(cwd: str) -> bool:
    return os.path.exists(os.path.join(cwd, "Makefile"))


def has_cargo(cwd: str) -> bool:
    return os.path.exists(os.path.join(cwd, "Cargo.toml"))


def has_go_mod(cwd: str) -> bool:
    return os.path.exists(os.path.join(cwd, "go.mod"))


def has_pyproject(cwd: str) -> bool:
    return os.path.exists(os.path.join(cwd, "pyproject.toml"))


def has_uv(cwd: str) -> bool:
    return os.path.exists(os.path.join(cwd, "uv.lock"))


# Action -> toolchain command mappings
MAKEFILE_COMMANDS = {
    "test": "make test",
    "build": "make build",
    "e2e": "make e2e",
    "smoke": "make smoke",
    "lint": "make lint",
}

CARGO_COMMANDS = {
    "test": "cargo test",
    "build": "cargo build",
    "e2e": "cargo test --test '*'",
    "lint": "cargo clippy",
}

GO_COMMANDS = {
    "test": "go test ./...",
    "build": "go build ./...",
    "e2e": "go test -tags=e2e ./...",
    "lint": "go vet ./...",
}


def get_npm_commands(pm: str) -> dict:
    return {
        "test": f"{pm} test",
        "build": f"{pm} run build",
        "e2e": f"{pm} run e2e",
        "smoke": f"{pm} run smoke",
        "lint": f"{pm} run lint",
    }


def get_python_commands(cwd: str) -> dict:
    runner = "uv run" if has_uv(cwd) else "python -m"
    return {
        "test": f"{runner} pytest",
        "e2e": f"{runner} pytest tests/",
        "smoke": f"{runner} pytest --smoke",
        "lint": f"{runner} ruff check .",
    }


def get_redirect_command(cwd: str, action: str) -> str:
    cwd = os.path.expanduser(cwd) if cwd else os.getcwd()

    # Priority 1: Makefile
    if has_makefile(cwd):
        cmd = MAKEFILE_COMMANDS.get(action)
        if cmd:
            # Verify make target exists
            makefile_path = os.path.join(cwd, "Makefile")
            try:
                with open(makefile_path) as f:
                    content = f.read()
                    target = action + ":"
                    if target in content or (".PHONY:" in content and action in content):
                        return cmd
            except OSError:
                pass

    # Priority 2: Cargo (Rust)
    if has_cargo(cwd):
        return CARGO_COMMANDS.get(action, "")

    # Priority 3: Go
    if has_go_mod(cwd):
        return GO_COMMANDS.get(action, "")

    # Priority 4: Node.js (npm/yarn/pnpm)
    pm = detect_package_manager(cwd)
    if pm:
        return get_npm_commands(pm).get(action, "")

    # Priority 5: Python
    if has_pyproject(cwd):
        return get_python_commands(cwd).get(action, "")

    return ""
