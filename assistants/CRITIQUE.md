# Critical Issues from Agent Review

## Priority 1: Fix Immediately (Incorrect/Dangerous)

### claude-template/README.md
- **Remove non-existent agents**: task-framework, logo-designer
- **Fix agent name**: doc-init → document
- **Add missing agents**: refine, visual
- **Update agent count**: 11 → 10 (verify actual count)

### local/rust.md
- **Fix interior mutability advice**: Complete rewrite of accessor section
- **Add async/await section**: Critical missing content
- **Add ownership/lifetime patterns**: Core Rust concepts missing

### local/typescript.md
- **Define "gst"**: Either explain or remove
- **Add type safety section**: strict mode, discriminated unions
- **Add async/error handling**: Critical for services

## Priority 2: Improve Quality (Misleading/Incomplete)

### usage-patterns/README.md
- **Move limitations to top**: Add warning that patterns lack validation
- **Fix Pattern 5**: Clarify maintains both unit+integration tests
- **Strengthen Pattern 2**: Add data redaction checklist
- **Remove meta-pattern claims**: Or mark as hypothesis

### global/CLAUDE.md
- **Remove vague rules**: "shorter is better", "Unix style"
- **Fix make contradiction**: Clarify dev vs prod usage
- **Move Go-specific**: testing.Short() → go.md
- **Add error handling section**: Exit codes, propagation

### local/python.md
- **Fix async example**: Explain WHY not when
- **Remove obvious**: Type hint syntax
- **Add real footguns**: Mutable defaults, GIL threading
- **Fix .get() example**: Clarify actual benefit

## Priority 3: Reduce Verbosity

### claude-template/README.md
- **Condense installation**: 4 sections → 1
- **Remove agent count**: "753 lines, 11 agents" detail

### global/CLAUDE.md
- **Remove killall section**: Obvious advice
- **Consolidate make rules**: Lines 43 + 93 duplicate

## Agent Critiques (Full Reports)

Stored in tmp/ for reference:
- tmp/critique_usage_patterns.txt
- tmp/critique_template_readme.txt
- tmp/critique_global_claude.txt
- tmp/critique_python.txt
- tmp/critique_rust.txt
- tmp/critique_typescript.txt
