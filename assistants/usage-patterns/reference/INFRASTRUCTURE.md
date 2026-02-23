# Infrastructure and Operations Patterns

Infrastructure automation, deployment systems, operational tools.

## Projects

### ansible
**Location**: `/home/ondra/wk/morha/ansible`
**Purpose**: IT automation for all production servers
**Lang**: Ansible (YAML)

**Architecture**:
- Single playbook: `playbooks.yml` (all servers)
- Roles: common + specialized (docker-service, nginx, grafana, rsyslog)
- Hosts: defined in `hosts` file

**Role Structure**:
```
common/               # Shared: UTC, SSH, users, postfix, zsh/bash
docker-service/      # Generic docker service (deployable)
nginx/               # Reverse proxy for grafana + reports
grafana/             # Grafana monitoring setup
rsyslog/             # Centralized logging (production)
```

**Usage**:
```bash
# Deploy to all servers
ansible-playbook playbooks.yml -i hosts -u <username>

# Specific subset
ansible-playbook playbooks.yml -i hosts -u <username> -l <server-subset>

# Specific tag
ansible-playbook playbooks.yml -i hosts -u <username> -t <tag-name>
```

**Key Components**:

**common**:
- UTC timezone
- SSH key management for users
- sshd_config hardening
- Shell defaults (zsh, bash)
- Postfix MTA (email capability)
- ansible-local helper (faster local runs)

**docker-service**:
- Generic Docker service deployable
- Service startup/stop via deploy
- Volume management
- Network configuration

**nginx**:
- Reverse proxy
- Routes to grafana
- Routes to reports
- TLS termination (assumed)

**grafana**:
- Prometheus datasource
- Default dashboards
- User management
- API token generation

**rsyslog**:
- Centralized log collection
- Forwarding to log aggregation
- Per-service filtering
- Retention policies

**Wisdom**:
- Single playbook forces common patterns
- Roles enable reuse and composition
- Per-server customization via group_vars
- Infrastructure as code (version control)

### ops-infra (Marinade)
**Location**: `/home/ondra/wk/mnde/ops-infra`
**Purpose**: Git-ops source for Marinade infrastructure
**Lang**: Terraform / Kubernetes / Ansible (mixed)

**Structure**:
```
docs/
├── infra.md           # Detailed infrastructure overview
├── learn.md           # Learning resources
└── utility.md         # Useful scripts and commands
```

**Key Concept**:
- Git-ops: Infrastructure defined in git
- Changes via pull requests
- Automated deployment (synced from git)
- Version history and rollback capability

**Typical Components**:
- Kubernetes cluster configuration
- Database infrastructure (PostgreSQL, etc.)
- Monitoring (Prometheus, Grafana)
- Secret management
- Network policies
- Storage configuration

### solana-unstake-liquidation-bot
**Location**: `/home/ondra/wk/trading/solana-unstake-liquidation-bot`
**Purpose**: Solana stake account liquidation system (arbitrage routing)
**Lang**: Rust

**Architecture** (4-crate workspace):

**arb/** - Core routing engine
- Graph-based pathfinding (Dijkstra)
- Nodes: Assets (Mint or StakeAccount)
- Edges: Conversion strategies (SPL, Sanctum, Jupiter, unstake.it)
- Highest price = lowest cost (minimizes losses)
- Multi-hop routes supported

**jito/** - Jito bundle integration
- Transaction batching (5 tx max per bundle)
- Fallback to standard RPC
- Tip amount configuration
- Dry-run mode support

**quote-server/** - gRPC server
- Dry-run routing queries
- Price curve caching (Lagrange interpolation)
- 10-minute TTL cache
- ~300ms cold, ~1ms warm requests

**workflow/** - Production daemon
- WebSocket subscriptions for stake accounts
- Polling fallback (10 minute interval)
- State machine: Uninitialized→Initialized→Activating→Active→Deactivating→Inactive
- Transaction submission via TxSender (channel-based batching)

**Configuration**:
```rust
struct Config {
    solana: SolanaConfig,         // RPC URLs, WebSocket, Jito
    wallet: WalletConfig,         // Keypair path (PREFIX expansion)
    spl: Option<SplConfig>,
    sanctum: Option<SanctumConfig>,
    jup: Option<JupConfig>,
    unstake_poc: Option<UnstakePOCConfig>,
    workflow: WorkflowConfig,
}
```

**Key Patterns**:

**Path expansion**:
```
Keypair path auto-prefixed: $PREFIX/{path}
Default PREFIX: /srv
Override: PREFIX=/custom/path
```

**Two-stage transaction signing**:
1. Strategies return `TxDetails` (Ready or Unprepared)
2. `TransactionBuilder` finalizes with blockhash + signatures

**Logging**:
```
Format: Unix timestamp + structured key=value
Levels: error, warn, info, debug
RUST_LOG env filtering
~30-50 lines/min typical (info level)
```

**Production vs Dry-run**:
```bash
# Dry-run (default)
cargo run -p workflow -- cfg/config.toml

# Production (sends real transactions)
cargo run -p workflow -- cfg/config.toml --production
```

**Wisdom**:
- Workspace structure: One project per crate
- Config validation on load (fail fast)
- Semaphore for concurrency limits (RPC protection)
- Cache with TTL (interpolation for efficiency)
- Separate binary from library (arb vs quote-server)

## Shared Infrastructure Patterns

### Configuration Management

**Three-level hierarchy**:
1. TOML config file (required or first CLI arg)
2. `/srv/key/env.toml` (optional overrides)
3. Environment variables (lowest precedence)

**Validation**:
- On-load checking via `validator` crate
- URL format validation (http/https, ws/wss)
- Range checking (min/max values)
- Non-empty string requirements

### Logging and Monitoring

**Structured Logging**:
```
Format: Mon DD HH:MM:SS.fff [LEVEL] message key=value key=value
Example: Nov 05 15:30:45.234 INFO Liquidating stake key=account value=balance
```

**Log Levels**:
- error: Failures only (~13 locations)
- warn: Recoverable issues (~12 locations)
- info: Normal operations (~75 locations) - RECOMMENDED for production
- debug: Internal algorithm details (~6 locations)

**Environment Control**:
```bash
RUST_LOG=info                    # Production (30-50 lines/min)
RUST_LOG=debug                   # Development (verbose)
RUST_LOG=error                   # Quiet (errors/warnings only)
RUST_LOG=module::path=debug,info # Selective (one module debug, rest info)
```

**Monitoring Integration**:
- Prometheus metrics endpoint
- Counter increments on events
- Gauge for current state (balance, position)
- Histogram for operation duration

### Data Storage

**Directory Structure**:
```
${PREFIX:-/srv}/data/
├── <project_name>/
│   ├── config.toml
│   ├── state.json          # Optional state snapshot
│   └── runs.jl             # JSONL log of runs
```

**Temporary Data**:
- Development: `./tmp/` (project root)
- Production: `/srv/tmp/` or `/tmp/project/`
- Log files: `./log/` for development
- Never use global `/tmp/` for state

### Service Management

**Process Tracking**:
- PID files in `/srv/data/<project>/`
- Write PID on startup
- Kill by reading PID file (never killall)
- Prevents accidentally killing wrong process

**Example**:
```bash
echo $! > ${PREFIX}/data/grid-bot/bot.pid
# Later:
kill $(cat ${PREFIX}/data/grid-bot/bot.pid)
```

**Graceful Shutdown**:
- Handle SIGTERM (15 seconds to finish)
- Handle SIGINT (Ctrl+C)
- Close connections cleanly
- Flush pending state

### Error Handling

**Error Hierarchy** (solana-unstake example):
```
TakerError
├── ApplicationError (business logic)
├── InfrastructureError (external services)
│   ├── GrpcError
│   └── SolanaError
└── DomainError (model validation)
```

**Retry Strategy**:
- Exponential backoff for transient errors
- Base delay: 100ms, Max retries: 5
- Backoff sequence: 100ms, 200ms, 400ms, 800ms, 1600ms
- Only retry transient errors (connection, timeout, unavailable)

### Secrets Management

**Pattern 1: TOML Overrides**:
```
Base config: cfg/config.toml (committed)
Secrets: /srv/key/env.toml (NOT committed)
Override precedence: env.toml > env vars > config.toml
```

**Pattern 2: Environment Variables**:
```bash
export POSTGRES_URL=postgresql://...
export RPC_URL=https://...
```

**Pattern 3: File Paths**:
```
Keypairs: ~/.config/solana/id.json (with chmod 600)
Certificates: /etc/pki/tls/certs/ (owned by service user)
```

## Infrastructure Deployment Checklist

When setting up new infrastructure:

1. **Configuration**:
   - [ ] TOML schema with validation
   - [ ] Environment variable overrides
   - [ ] Secrets isolation (not in git)
   - [ ] Path expansion for ${PREFIX}

2. **Logging**:
   - [ ] Structured format (Unix time, key=value)
   - [ ] Multiple log levels (error/warn/info/debug)
   - [ ] RUST_LOG filtering capability
   - [ ] Rotation policy (time or size based)

3. **Monitoring**:
   - [ ] Prometheus metrics
   - [ ] Health check endpoint
   - [ ] Error counter integration
   - [ ] Alerting rules

4. **Storage**:
   - [ ] ${PREFIX}/data/<project>/ directory
   - [ ] State persistence strategy
   - [ ] Cleanup/retention policies
   - [ ] Backup procedures

5. **Security**:
   - [ ] Minimal permissions (service user)
   - [ ] Secrets not in logs
   - [ ] TLS for network services
   - [ ] Audit logging for sensitive operations

6. **Operations**:
   - [ ] Graceful shutdown handling
   - [ ] PID file management
   - [ ] Restart policies (systemd)
   - [ ] Resource limits

## Operational Patterns

### Single Goroutine (Go) Pattern
Used in grid-bot:
- One main goroutine processes state
- Direct state access (no locks)
- No copy overhead
- Deterministic order
- Fails fast on conflicts

**Anti-pattern: Window-based calculations**
```rust
// WRONG
window = [last_100_values]
ewma = calculate(window)

// CORRECT
ewma_new = alpha * value + (1 - alpha) * ewma_old
```

### Async/Await (Rust) Pattern
Used in solana-unstake-bot:
- tokio runtime for async I/O
- Semaphore for concurrency control
- tokio::spawn for parallel tasks
- Arc<Self> for spawned tasks needing self
- Manual Clone impl when needed

### Database Integration

**Migrations**:
- Version control SQL files
- Atomic deployments
- Rollback strategy
- Test on staging first

**Connections**:
- Connection pooling (async-aware)
- Never manually call .close() on async context managers
- Trust context managers for cleanup
- Protocol errors indicate connection state corruption

## See Also

- BUILDERS.md - Build tools and Docker patterns
- CLI.md - Command-line tool patterns
- Global CLAUDE.md - Development principles
