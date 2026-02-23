# Command-Line Tools and Entrypoints

CLI tools, management utilities, and command-line entrypoints across projects.

## Projects

### hukotctl
**Location**: `/home/ondra/wk/morha/hukotctl`
**Purpose**: Automate Windows VPS orders on cloud.hukot.net
**Lang**: Python

**Installation**:
```bash
cd hukotctl
make link          # Link to ~/bin (requires ~/bin in PATH)
# OR
sudo make install  # Install globally to /usr/local/bin
```

**Verification**:
```bash
hukotctl --help
```

**Usage Examples**:
```bash
# Interactive (prompts for password)
hukotctl create \
  --username alice \
  --sku WIN-SERVER-2022 \
  --hostname myvps.example.com

# Non-interactive (batch automation)
hukotctl create \
  --username alice \
  --password "secret" \
  --sku WIN-SERVER-2022 \
  --hostname myvps.example.com \
  --yes
```

**Key Design**:
- Interactive password prompt (fallback if --password omitted)
- --yes flag for non-interactive mode (skips confirmation)
- Semantic arguments (--username, --sku, --hostname)
- Clear help messages

### winctl
**Location**: `/home/ondra/wk/morha/winctl`
**Purpose**: Setup Windows VPS and deploy clients
**Lang**: Bash + Python

**Architecture**:
- Provision phase: Prepare files, setup directories
- Distribute phase: SCP files to multiple VPS
- Deploy phase: Execute on Windows (via SSH)

**Commands**:
```bash
./winctl provision <identity> [branch]
./winctl distribute [identity] | [--all]
```

**Operations**:

**Provision**:
1. Prepare client files for identity
2. Setup ssh keys
3. Generate configuration
4. Create output directory for distribution

**Distribute**:
1. Read credentials from passd.gpg
2. SCP prepared files to VPS
3. Setup task scheduler startup script
4. Deploy MetaTrader 5 (optional)

**Key Components**:
- SSH key management (per-identity)
- Google Cloud integration (legacy/deprecated)
- Credential store: passd.gpg (encrypted)
- File preparation: generate_client_files.sh
- Startup task: startup_script.bat

### easyrsa3
**Location**: `/home/ondra/wk/morha/easyrsa3`
**Purpose**: Manage Certification Authority for PKI
**Lang**: Bash wrapper + easyrsa

**Installation**:
```bash
cd easyrsa3
make install  # Install wrapper to /usr/local/sbin/easyrsa
```

**Usage**:
```bash
# Initialize CA
easyrsa production init-pki
easyrsa production build-ca
# Without password protection:
easyrsa production --no-pass build-ca

# Create server certificate
easyrsa production --no-pass build-server-full <server-name>

# Create client certificate
easyrsa production --no-pass build-client-full <client-name>
```

**Key Concepts**:
- Wrapper delegates to easyrsa executable
- Environment-based paths (production, staging)
- Support for password-protected or no-pass CA
- Certificates stored in pki/ directory

**Deployment Flow**:
1. Build CA (one-time)
2. Issue certificates for servers
3. Issue certificates for clients
4. Distribute to endpoints

### solana-unstake-auction-bot
**Location**: `/home/ondra/wk/trading/solana-unstake-auction-bot`
**Purpose**: Solana auction taker CLI bot
**Lang**: Rust

**Invocation**:
```bash
./target/debug/main cfg/hel1/solana_unstake_bot.toml
```

**Configuration** (CLI arg = first parameter):
```
Priority (highest first):
1. CLI argument (REQUIRED)
2. /srv/key/env.toml (optional secrets)
3. UNSTAKE_* environment variables
```

**Example Config** (cfg/hel1/solana_unstake_bot.toml):
```toml
[atomic_swap]
marketplace = "..."
fee_collector = "..."
margins = {...}

[application]
max_concurrent_auctions = 10
buffer_size = 1000
health_check_interval_secs = 60

[solana]
rpc_url = "https://..."
websocket_url = "wss://..."

[wallet]
keypair_path = "~/.solana/id.json"

[logger]
level = "info"
format = "json"

[discord]
token = "..."
channel_id = "..."
daily_summary_hour = 8
```

**Configuration Validation**:
- URL format checking (http/https, ws/wss)
- Non-zero amounts required
- Price bounds (0 < price ≤ 1)
- File path existence checks

**Exit Codes**:
- 0: Success
- 1: Configuration error
- 2: Runtime error

**Logging Format**:
```
Nov 05 15:30:45.234 INFO message key=value key=value
Nov 05 15:30:46.123 ERROR failure reason="timeout"
```

**Key Patterns**:

**Startup**:
```
1. Parse CLI args (config path required)
2. Load TOML config
3. Apply /srv/key/env.toml overrides
4. Apply UNSTAKE_* env var overrides
5. Validate all config sections
6. Initialize async runtime (tokio)
7. Connect to gRPC + RPC
8. Start auction stream listener
```

**Graceful Shutdown**:
```
1. Receive SIGTERM/SIGINT
2. Stop accepting new auctions
3. Wait for in-flight bids (timeout 30s)
4. Close connections
5. Exit with status 0
```

**Error Handling**:
- Transient: Retry with exponential backoff
- Fatal: Log with error level, exit
- Recoverable: Log with warn level, continue

### grid-bot
**Location**: `/home/ondra/wk/trading/grid-bot`
**Purpose**: Grid trading strategy bot
**Lang**: Go + Python CLI

**Build**:
```bash
make build                # Compiles to ./main
```

**Operation via CLI** (Python):
```bash
PREFIX=. python3 cli.py start                 # Start all exchanges
PREFIX=. python3 cli.py start -e hyperliquid  # Specific exchange
PREFIX=. python3 cli.py start -e aevo -e apex # Multiple exchanges

PREFIX=. python3 cli.py stop                  # Stop all bots
killall main                                   # Alternative (less safe)
kill $(cat run/grid-bot/{exchange}.pid)       # Kill specific bot

PREFIX=. python3 cli.py report pnl            # Show profits
PREFIX=. python3 cli.py report pnl -n 5       # Last 5 runs per exchange
PREFIX=. python3 cli.py report pnl -e hyperliquid
```

**Configuration**:
```
Production: ../cfg/hel1/grid_bot_{exchange}.toml
Data: ${PREFIX:-/srv}/data/grid-bot/
Logs: ./log/
Runs tracking: ${PREFIX:-/srv}/data/grid-bot/runs.jl
```

**Configuration Format**:
```toml
[exchange]
name = "hyperliquid"
api_key = "..."
api_secret = "..."

[grid]
symbols = ["BTC", "ETH"]
spread_pct = 0.7
grid_levels = 5

[risk]
max_position_size = 10000
stop_loss_pct = -3.0
take_profit_pct = 7.0
```

**PID Management**:
```bash
# Write on startup
echo $! > ${PREFIX}/data/grid-bot/bot.pid

# Later, kill by reading PID
kill $(cat ${PREFIX}/data/grid-bot/bot.pid)

# Check status
ps -p <PID> -o pid,etime,cmd
```

**Key Patterns**:

**Single Goroutine Design**:
- One goroutine processes all state
- Direct state access (no locks)
- Deterministic order
- Message processing inline

**Data Model**:
- Positions, balance, trades
- Virtual fills with lifecycle
- Grid levels (anchored vs unanchored)

**Output Format**:
```
PnL report:
  pnl:       $99.54 (live)
  fees:      $55.21
  volume:    $110,418.23
  trades:    130
  whale:     $5,234.56 vol, 12 trades
```

## Shared CLI Patterns

### Argument Parsing

**Three-level hierarchy**:
1. CLI flags (highest precedence, -e exchange)
2. Environment variables (EXCHANGE=, PREFIX=)
3. Configuration files (lowest, config.toml)
4. Defaults (hardcoded, if nothing else provided)

**Conventions**:
- Short flags: `-h` (help), `-v` (verbose)
- Long flags: `--yes` (boolean), `--config FILE`
- Positional args: `<identity>` (required), `[branch]` (optional)
- Multiple values: `-e ex1 -e ex2` or `--hosts=h1,h2`

### Configuration Loading

**TOML Standard**:
```rust
// Load with validation
let config = Config::load_from_file(path)?;

// Three-level precedence
let final_config = merge(
    defaults,
    env_vars,
    toml_file,
    env_file_overrides
);
```

**Secrets Pattern**:
- Committed config: `cfg/config.toml` (no secrets)
- Local overrides: `/srv/key/env.toml` (secrets, not in git)
- Environment: `UNSTAKE_*` prefix for CLI override
- File paths: Expanded with `${PREFIX:-/srv}` var

### Output Formatting

**Log Messages**:
```
Lowercase: normal operational messages
error message with context
CRITICAL: error names only
Format: Unix timestamp + level + message
```

**Progress Output**:
```bash
# Simple, no fancy
Processing stake account...
✓ Matched with pool (use ✓✗ sparingly)
Done.
```

**Error Messages**:
```
Clear and actionable:
Error: Invalid configuration - expected http/https URL for rpc_url
  Got: "ftp://invalid"
  Fix: Use https:// instead

Exit code: 1 (non-zero)
```

### Installation Methods

**Pattern 1: make link**
```bash
make link  # Symlink to ~/bin (requires PATH setup)
```

**Pattern 2: make install**
```bash
sudo make install  # Copy to /usr/local/bin
```

**Pattern 3: Global install**
```bash
PREFIX=/usr/local ./install.sh
```

**Pattern 4: Development**
```bash
cargo run --manifest-path ./Cargo.toml -- <args>
go run main.go <args>
python3 -m main <args>
```

### Process Control

**PID File Pattern**:
```bash
# On startup
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    kill $OLD_PID 2>/dev/null  # Kill previous
fi
echo $$ > "$PID_FILE"

# On shutdown
trap 'rm -f "$PID_FILE"' EXIT
```

**Graceful Shutdown**:
```bash
# Handle signals
signal_handler() {
    log "Received signal, shutting down..."
    kill_subprocesses
    cleanup_resources
    exit 0
}
trap signal_handler SIGTERM SIGINT

# Wait for completion
wait_for_completion 30s  # 30 second timeout
```

**Status Checking**:
```bash
if ps -p $(cat $PID_FILE) > /dev/null; then
    echo "Running"
else
    echo "Not running"
fi
```

### Error Handling

**Exit Codes**:
- 0: Success
- 1: Configuration/argument error
- 2: Runtime error (retryable)
- 3: Fatal error (don't retry)
- 130: Interrupted (Ctrl+C)

**Error Reporting**:
```
Stderr for errors:
  Error: <description> >&2

Stdout for normal output:
  Processing...
  Done.

Exit code signals severity
```

### Help and Documentation

**Help Format** (--help):
```
Usage: grid-bot [OPTIONS] [COMMAND]

Commands:
  start    Start the bot
  stop     Stop the bot
  report   Generate reports
  help     Show this help

Options:
  -c, --config FILE     Configuration file
  -e, --exchange NAME   Filter by exchange
  -v, --verbose         Enable verbose logging
  -h, --help            Show this help
```

**Examples in Help**:
```bash
$ hukotctl create --help

Examples:
  # Interactive (prompts for password)
  $ hukotctl create --username alice --sku WIN-SERVER-2022

  # Non-interactive (batch automation)
  $ hukotctl create --username alice --password secret --yes
```

### Testing CLI

**Integration Testing**:
```bash
# Test with real config
./target/debug/main cfg/test/config.toml

# Test with env overrides
RUST_LOG=debug ./target/debug/main cfg/test/config.toml

# Test dry-run mode
./target/debug/main cfg/test/config.toml --dry-run
```

**Fixture Data**:
- Keep test configs in `cfg/test/`
- Never use production configs in tests
- Use temporary directories for data outputs

## CLI Development Checklist

When building new CLI tools:

1. **Argument Parsing**:
   - [ ] Help message (-h, --help)
   - [ ] Version flag (-v, --version)
   - [ ] Verbose flag (-v, --verbose)
   - [ ] Configuration file argument
   - [ ] Example usage in help

2. **Configuration**:
   - [ ] TOML schema with comments
   - [ ] Environment variable overrides
   - [ ] Secrets isolation (not in git)
   - [ ] Path expansion (${PREFIX})
   - [ ] Validation on load

3. **Output**:
   - [ ] Structured logging (key=value)
   - [ ] Different log levels (error/warn/info/debug)
   - [ ] Progress indicators (when appropriate)
   - [ ] Clean error messages
   - [ ] Proper exit codes

4. **Installation**:
   - [ ] make install target (if applicable)
   - [ ] make link target (for development)
   - [ ] Symlink or copy to standard location
   - [ ] README with installation steps

5. **Process Management**:
   - [ ] Graceful shutdown (SIGTERM/SIGINT)
   - [ ] PID file tracking
   - [ ] Cleanup on exit
   - [ ] Resource limits

6. **Testing**:
   - [ ] Test with various configs
   - [ ] Test error conditions
   - [ ] Integration tests with real operations
   - [ ] Dry-run mode available

## Common Pitfalls

**Don't**:
- Hardcode paths (use ${PREFIX})
- Ignore signals (handle SIGTERM)
- Write secrets to logs
- Use killall (kill by PID)
- Skip input validation
- Assume file existence

**Do**:
- Validate all inputs
- Log structured, parseable output
- Handle errors gracefully
- Provide clear help messages
- Test with real data
- Document environment variables

## See Also

- BUILDERS.md - Build tools and packaging
- INFRASTRUCTURE.md - Infrastructure operations
- Global CLAUDE.md - Development principles
