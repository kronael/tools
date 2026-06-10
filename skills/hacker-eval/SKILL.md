---
name: hacker-eval
description: Use when evaluating a codebase or project from a security researcher / red-team perspective. Triggers on: "security review", "pentest this", "hacker evaluation", "is this safe to run", "attack surface", "can I trust this dependency", security audit before adopting open-source code.
---

# Hacker Eval

Security-first evaluation of a project. Goal: find what breaks before an attacker does.

## Scope

Attack surface · dependency chain · secret exposure · auth/authz gaps · injection vectors · supply chain · protocol safety · DoS vectors

## Execution

ALWAYS fan the checklist out via /fable background agents (Agent tool,
`model: "fable"`, `run_in_background: true`), NEVER more than 4:

1. Build & static analysis + dependency audit + supply chain (§1, §2, §8)
2. Secret scan + operational security (§3, §9)
3. Auth/authz + input validation & injection (§4, §5)
4. DoS vectors + protocol & transport (§6, §7)

Each agent reports findings only (file:line, severity, why). The main
context collects, dedupes, rates per the table below, records ALL findings
to `BUGS.md` without asking, and writes the verdict.

## Checklist

Flag every finding; do not fix — record to `BUGS.md`.

### 1. Build & Static Analysis

```sh
# Does it build at all?
make build 2>&1 | tee tmp/build.log

# Go
go vet ./... 2>&1
gofmt -l . 2>&1          # formatting = discipline signal

# Python
bandit -r . -ll 2>&1
semgrep --config=auto . 2>&1

# JS/TS
npx audit-ci --moderate 2>&1
```

**Flag:** build failures, vet errors, formatting violations in non-test code.

### 2. Dependency Audit

```sh
# Go
govulncheck ./...         # known CVEs in transitive deps
cat go.mod | grep -v "^//" | wc -l   # dep count (< 10 direct = good)

# JS
npm audit --audit-level=moderate
npx snyk test

# Python
pip-audit
safety check
```

**Flag:** any HIGH/CRITICAL CVE, deps with known abandoned maintainers, >50 transitive deps without justification.

### 3. Secret Scan

```sh
# Never-committed secrets
git log --all --oneline | head -20   # check for "remove secret" commits
trufflehog filesystem . --only-verified
gitleaks detect --source . -v

# Hardcoded strings
grep -r "password\|secret\|token\|api_key\|apikey\|AUTH\|Bearer" \
  --include="*.go" --include="*.py" --include="*.ts" \
  --exclude-dir=".git" -l
```

**Flag:** any token/key in source or git history.

### 4. Authentication & Authorization

- Is there auth on the HTTP server? If not: what's the blast radius if port is exposed?
- Does each endpoint validate caller identity before acting?
- Session IDs: server-generated (good) or client-supplied (session fixation risk)?
- Are admin/destructive endpoints protected differently from read endpoints?
- Unix socket permissions: who can connect?

**Flag:** no auth + non-loopback bind, client-controlled session IDs, missing endpoint-level authz.

### 5. Input Validation & Injection

```sh
# Find where user input hits shell/exec
grep -rn "exec\.\|os\.exec\|subprocess\|cmd\.Run\|Popen" \
  --include="*.go" --include="*.py" -n

# Find SQL construction
grep -rn "fmt.Sprintf.*SELECT\|string+.*WHERE\|query +" -n

# Find path traversal
grep -rn "filepath\.Join\|os\.Open\|ioutil\.Read" -n
```

**Check each callsite:**
- Is input sanitized before hitting exec/query/path?
- Are parameterized queries used (never string concat for SQL)?
- Path traversal: is `filepath.Clean` + prefix-check applied?
- Prompt injection: does user input flow directly into LLM prompts without a trust boundary?

### 6. DoS Vectors

- Request body size limit? (`http.MaxBytesReader` / `LimitReader`)
- Write timeout set? (`WriteTimeout: 0` = infinite = slow-loris risk on streaming)
- Max concurrent sessions / rate limiting?
- Memory unbounded growth? (e.g., in-memory session map with no cap)
- Scanner buffer caps? (bufio.Scanner default = 64KB; check for overrides)

### 7. Protocol & Transport

- TLS in use? (Required if not loopback-only)
- CORS headers present? (XSS pivot if browser-accessible)
- WebSocket origin check?
- Unix socket path: world-writable dir? (Use `/run/<app>/` not `/tmp/`)
- MCP: does the server expose dangerous tools (shell exec, fs write, permission bypass) without additional guard?

### 8. Supply Chain

- Is the project using a pinned lockfile (`go.sum`, `package-lock.json`, `Pipfile.lock`)?
- Are pre/post install scripts present in npm packages?
- CI: does it pull `@latest` / `HEAD` deps?
- Single maintainer? Abandoned project? (check last commit date, issue response time)
- Module path matches actual repo URL? (typosquatting)

### 9. Operational Security

- Log output: does it log request bodies, tokens, or secrets?
- Error messages: do they leak stack traces / internal paths to callers?
- Health endpoint: does it expose internal state (session count, system info) without auth?
- Crash behavior: does panic recovery exist? Does it expose stack traces?

## Risk Rating

| Finding | Severity |
|---------|----------|
| Secrets in git history | CRITICAL |
| RCE via injection | CRITICAL |
| Unauthed admin endpoints on non-loopback | HIGH |
| Known CVE in dep (exploitable path) | HIGH |
| No input size limits (DoS) | MEDIUM |
| Session fixation (client-controlled IDs) | MEDIUM |
| Prompt injection surface | MEDIUM |
| No TLS on non-loopback | MEDIUM |
| Abandoned dep, no CVE yet | LOW |
| gofmt/lint violations | INFO |

## Verdict Template

```
## Hacker Eval: <project> v<version>

**Verdict:** [USE / USE WITH MITIGATIONS / DO NOT USE]

**Deployment scope this is safe for:** [loopback-only / internal network / internet-facing]

### Critical
- ...

### High
- ...

### Medium
- ...

### Mitigations required before production use
1. ...
```

## What "safe enough" means

A tool rated **USE** means: known attack paths are absent or mitigated for the stated deployment scope. It does NOT mean zero bugs. All software has bugs; the question is blast radius.

**Loopback-only tools** with no auth are acceptable if the OS user boundary is the auth layer.
**Internet-facing tools** with no auth are never acceptable.
