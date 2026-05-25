FROM node:lts

ARG TZ=UTC
ENV TZ="$TZ"

ARG CLAUDE_CODE_VERSION=latest

RUN apt-get update && apt-get install -y --no-install-recommends \
  less git procps sudo fzf zsh man-db unzip zip gnupg2 gh \
  iptables ipset iproute2 dnsutils aggregate \
  jq nano vim docker.io clang libclang-dev libudev-dev \
  bubblewrap socat gosu \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

# All tool homes live in /opt/dev-tools — world-readable so any runtime UID
# can use them. No /home/<user> dependencies anywhere.
ENV DEVCONTAINER=true \
    SHELL=/bin/zsh \
    EDITOR=nano \
    VISUAL=nano \
    NPM_CONFIG_PREFIX=/usr/local/share/npm-global \
    NVM_DIR=/opt/dev-tools/nvm \
    BUN_INSTALL=/opt/dev-tools/bun \
    CARGO_HOME=/opt/dev-tools/cargo \
    RUSTUP_HOME=/opt/dev-tools/rustup \
    G_HOME=/opt/dev-tools/g \
    GOPATH=/opt/dev-tools/go \
    SDKMAN_DIR=/opt/dev-tools/sdkman \
    PLAYWRIGHT_BROWSERS_PATH=/opt/playwright-browsers \
    PUPPETEER_CACHE_DIR=/opt/playwright-browsers/puppeteer \
    UV_TOOL_BIN_DIR=/opt/dev-tools/uv/bin \
    UV_TOOL_DIR=/opt/dev-tools/uv/tools \
    PATH=/opt/dev-tools/uv/bin:/opt/dev-tools/cargo/bin:/opt/dev-tools/bun/bin:/opt/dev-tools/g/bin:/opt/dev-tools/g/go/bin:/opt/dev-tools/go/bin:/usr/local/share/npm-global/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

RUN mkdir -p /opt/dev-tools/nvm /usr/local/share/npm-global /workspace /home/dockbox

WORKDIR /workspace

ARG GIT_DELTA_VERSION=0.19.2
RUN ARCH=$(dpkg --print-architecture) && \
  wget "https://github.com/dandavison/delta/releases/download/${GIT_DELTA_VERSION}/git-delta_${GIT_DELTA_VERSION}_${ARCH}.deb" && \
  dpkg -i "git-delta_${GIT_DELTA_VERSION}_${ARCH}.deb" && \
  rm "git-delta_${GIT_DELTA_VERSION}_${ARCH}.deb"

RUN corepack enable && corepack prepare pnpm@latest --activate

RUN npx -y playwright install --with-deps chromium && \
  chmod -R o+rx /opt/playwright-browsers

RUN curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.4/install.sh | bash && \
  unset NPM_CONFIG_PREFIX && . "$NVM_DIR/nvm.sh" && \
  nvm install node && nvm alias default node

RUN curl -fsSL https://bun.sh/install | bash

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \
  | sh -s -- -y && \
  /opt/dev-tools/cargo/bin/rustup component add rust-analyzer clippy rustfmt

RUN curl -sSL https://git.io/g-install | sh -s -- -y && \
  /opt/dev-tools/g/go/bin/go install golang.org/x/tools/gopls@latest

ARG NU_VERSION=0.112.2
RUN ARCH=$(uname -m) && \
  curl -fsSL "https://github.com/nushell/nushell/releases/download/${NU_VERSION}/nu-${NU_VERSION}-${ARCH}-unknown-linux-gnu.tar.gz" \
  | tar xz --strip-components=1 -C /opt/dev-tools/cargo/bin

# uv installer writes to $HOME/.local/bin by default; move into /opt
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
  mkdir -p /opt/dev-tools/uv/bin && \
  mv /root/.local/bin/uv /opt/dev-tools/uv/bin/ && \
  mv /root/.local/bin/uvx /opt/dev-tools/uv/bin/ 2>/dev/null || true

RUN uv tool install pre-commit

RUN curl -fsSL https://get.sdkman.io | bash

RUN npm install -g @anthropic-ai/claude-code@${CLAUDE_CODE_VERSION}

RUN bun install -g \
  @openai/codex \
  @mariozechner/pi-coding-agent \
  agent-browser \
  pyright \
  typescript typescript-language-server

RUN uv tool install git+https://github.com/kronael/ship

RUN bunx puppeteer browsers install chrome

# system-wide zshrc — every zsh user loads this
RUN mkdir -p /etc/zsh && printf '%s\n' \
  '[ -r /usr/share/doc/fzf/examples/key-bindings.zsh ] && source /usr/share/doc/fzf/examples/key-bindings.zsh' \
  '[ -r /usr/share/doc/fzf/examples/completion.zsh ] && source /usr/share/doc/fzf/examples/completion.zsh' \
  'export HISTFILE="$HOME/.zsh_history"' \
  > /etc/zsh/zshrc

# claude wrapper at /usr/local/bin (system-wide, $HOME-relative)
RUN printf '#!/bin/sh\n\
[ -f /tmp/host-claude.json ] && cp /tmp/host-claude.json "$HOME/.claude.json"\n\
[ -f "$HOME/.claude.json" ] || echo "{\"hasCompletedOnboarding\":true}" > "$HOME/.claude.json"\n\
export NVM_DIR="/opt/dev-tools/nvm"\n\
unset NPM_CONFIG_PREFIX\n\
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"\n\
exec /usr/local/share/npm-global/bin/claude --dangerously-skip-permissions "$@"\n' \
  > /usr/local/bin/claude && chmod +x /usr/local/bin/claude

# dockbox-init: register the runtime user in /etc/passwd, chown overmounts
# and $HOME (top-level only — nested bind mounts must not be touched), then
# gosu-drop to DOCKBOX_UID:DOCKBOX_GID before exec'ing the command.
RUN printf '#!/bin/sh\n\
USERNAME="${DOCKBOX_USER:-dockbox}"\n\
USER_UID="${DOCKBOX_UID:-1000}"\n\
USER_GID="${DOCKBOX_GID:-1000}"\n\
HOME_DIR="${HOME:-/home/dockbox}"\n\
if [ "$(id -u)" = "0" ]; then\n\
  getent passwd "$USER_UID" >/dev/null 2>&1 || \\\n\
    echo "${USERNAME}:x:${USER_UID}:${USER_GID}::${HOME_DIR}:/bin/zsh" >> /etc/passwd\n\
  getent group "$USER_GID" >/dev/null 2>&1 || \\\n\
    echo "${USERNAME}:x:${USER_GID}:" >> /etc/group\n\
  [ -d "$HOME_DIR" ] && chown "${USER_UID}:${USER_GID}" "$HOME_DIR"\n\
  if [ -n "$DOCKBOX_EPH_PATHS" ]; then\n\
    IFS=:\n\
    for p in $DOCKBOX_EPH_PATHS; do\n\
      [ -d "$p" ] && chown "${USER_UID}:${USER_GID}" "$p"\n\
    done\n\
    unset IFS\n\
  fi\n\
  exec gosu "${USER_UID}:${USER_GID}" "$@"\n\
fi\n\
exec "$@"\n' > /usr/local/bin/dockbox-init && chmod +x /usr/local/bin/dockbox-init

# World-readable + writable tooling so any runtime UID can use it
RUN chmod -R a+rwX /opt/dev-tools /usr/local/share/npm-global /workspace /home/dockbox
