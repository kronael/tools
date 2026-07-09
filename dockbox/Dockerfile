FROM debian:forky

ARG TZ=UTC
ENV TZ="$TZ"

ARG CLAUDE_CODE_VERSION=2.1.199

# Base apt deps. gh isn't packaged in forky's apt — add GitHub CLI's
# official repo before installing it.
RUN apt-get update && apt-get install -y --no-install-recommends \
  wget curl ca-certificates gnupg2 \
  && mkdir -p -m 755 /etc/apt/keyrings \
  && wget -qO- https://cli.github.com/packages/githubcli-archive-keyring.gpg \
     | tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
  && chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
  && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
     > /etc/apt/sources.list.d/github-cli.list \
  && apt-get update && apt-get install -y --no-install-recommends \
  xz-utils make \
  less git procps sudo fzf zsh man-db unzip zip gh \
  iptables ipset iproute2 dnsutils aggregate \
  jq yq bc nano vim docker.io clang libclang-dev libudev-dev libssl-dev libpq-dev pkg-config \
  bubblewrap socat gosu libicu78 \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

# All tool homes live in /opt/dev-tools — world-readable so any runtime UID
# can use them. No /home/<user> dependencies anywhere. Node comes from nvm,
# not from a baked base image — respects per-project .nvmrc at runtime.
ENV DEVCONTAINER=true \
    SHELL=/bin/zsh \
    EDITOR=nano \
    VISUAL=nano \
    DISABLE_AUTOUPDATER=1 \
    CLAUDE_CODE_DISABLE_AUTOUPDATE=1 \
    NPM_CONFIG_PREFIX=/usr/local/share/npm-global \
    NVM_DIR=/opt/dev-tools/nvm \
    BUN_INSTALL=/opt/dev-tools/bun \
    CARGO_HOME=/opt/dev-tools/cargo \
    RUSTUP_HOME=/opt/dev-tools/rustup \
    GOROOT=/opt/dev-tools/goroot \
    GOPATH=/opt/dev-tools/go \
    SDKMAN_DIR=/opt/dev-tools/sdkman \
    PLAYWRIGHT_BROWSERS_PATH=/opt/playwright-browsers \
    PUPPETEER_CACHE_DIR=/opt/playwright-browsers/puppeteer \
    UV_TOOL_BIN_DIR=/opt/dev-tools/uv/bin \
    UV_TOOL_DIR=/opt/dev-tools/uv/tools \
    DOTNET_ROOT=/opt/dev-tools/dotnet \
    PATH=/usr/local/bin:/opt/dev-tools/uv/bin:/opt/dev-tools/cargo/bin:/opt/dev-tools/bun/bin:/opt/dev-tools/goroot/bin:/opt/dev-tools/go/bin:/opt/dev-tools/dotnet:/usr/local/share/npm-global/bin:/usr/local/sbin:/usr/sbin:/usr/bin:/sbin:/bin

RUN mkdir -p /opt/dev-tools/nvm /usr/local/share/npm-global /workspace /home/dockbox

WORKDIR /workspace

# Install nvm + default LTS node first so subsequent RUNs can use npm/npx/corepack.
# Symlink the default node's binaries to /usr/local/bin so they're on PATH
# without sourcing nvm.sh in every RUN. Runtime users can still `nvm use` per
# project (the wrapper sources nvm.sh, so .nvmrc / nvm install <ver> works).
RUN curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.4/install.sh | bash && \
    unset NPM_CONFIG_PREFIX && . "$NVM_DIR/nvm.sh" && \
    nvm install --lts && nvm alias default 'lts/*' && \
    NODE_BIN="$NVM_DIR/versions/node/$(nvm version default)/bin" && \
    for b in node npm npx corepack; do ln -sf "$NODE_BIN/$b" "/usr/local/bin/$b"; done

ARG GIT_DELTA_VERSION=0.19.2
RUN ARCH=$(dpkg --print-architecture) && \
  wget "https://github.com/dandavison/delta/releases/download/${GIT_DELTA_VERSION}/git-delta_${GIT_DELTA_VERSION}_${ARCH}.deb" && \
  dpkg -i "git-delta_${GIT_DELTA_VERSION}_${ARCH}.deb" && \
  rm "git-delta_${GIT_DELTA_VERSION}_${ARCH}.deb"

# gcloud CLI — needed for GCS operations (gcs_cached_download, gsutil, etc.)
RUN curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg \
      | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" \
       > /etc/apt/sources.list.d/google-cloud-sdk.list \
    && apt-get update && apt-get install -y --no-install-recommends google-cloud-cli \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN corepack enable && corepack prepare pnpm@latest --activate

# Chromium runtime deps installed manually — playwright --with-deps uses a
# hardcoded list that predates Debian forky's t64 rename and missing font pkgs.
RUN apt-get update && apt-get install -y --no-install-recommends \
  libnspr4 libnss3 libglib2.0-0 libdbus-1-3 libdrm2 \
  libatk1.0-0t64 libatk-bridge2.0-0 libcups2t64 \
  libxkbcommon0 libatspi2.0-0 \
  libx11-6 libxcomposite1 libxdamage1 libxext6 libxfixes3 libxrandr2 \
  libgbm1 libpango-1.0-0 libcairo2 libasound2t64 \
  libfontconfig1 libfreetype6 \
  fonts-liberation fonts-freefont-ttf \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN npx -y playwright install chromium && \
  chmod -R o+rx /opt/playwright-browsers

RUN curl -fsSL https://bun.sh/install | bash

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \
  | sh -s -- -y && \
  /opt/dev-tools/cargo/bin/rustup component add rust-analyzer clippy rustfmt

RUN curl -sSL https://git.io/g-install | sh -s -- -y && \
  /opt/dev-tools/goroot/bin/go install golang.org/x/tools/gopls@latest && \
  /opt/dev-tools/goroot/bin/go install golang.org/x/vuln/cmd/govulncheck@latest

COPY udfix/ /tmp/udfix/
RUN make -C /tmp/udfix install PREFIX=/usr/local/bin && rm -rf /tmp/udfix

ARG NU_VERSION=0.112.2
RUN ARCH=$(uname -m) && \
  curl -fsSL "https://github.com/nushell/nushell/releases/download/${NU_VERSION}/nu-${NU_VERSION}-${ARCH}-unknown-linux-gnu.tar.gz" \
  | tar xz --strip-components=1 -C /opt/dev-tools/cargo/bin

# uv installer writes to $HOME/.local/bin by default; move into /opt
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
  mkdir -p /opt/dev-tools/uv/bin && \
  mv /root/.local/bin/uv /opt/dev-tools/uv/bin/ && \
  mv /root/.local/bin/uvx /opt/dev-tools/uv/bin/ 2>/dev/null || true

RUN for t in pre-commit bandit pip-audit semgrep; do uv tool install "$t"; done

RUN curl -fsSL https://get.sdkman.io | bash

# .NET SDK (LTS) — installed under /opt/dev-tools, in PATH so `dotnet` works
# inside dockbox without per-project overrides.
RUN curl -fsSL https://dot.net/v1/dotnet-install.sh \
  | bash -s -- --install-dir /opt/dev-tools/dotnet --channel LTS

RUN npm install -g @anthropic-ai/claude-code@${CLAUDE_CODE_VERSION}

RUN bun install -g \
  @openai/codex \
  @mariozechner/pi-coding-agent \
  agent-browser \
  pyright \
  typescript typescript-language-server

RUN uv tool install git+https://github.com/kronael/ship

ARG GITLEAKS_VERSION=8.30.1
RUN ARCH=$(dpkg --print-architecture) && \
  case "$ARCH" in amd64) GLARCH=x64 ;; arm64) GLARCH=arm64 ;; *) GLARCH=$ARCH ;; esac && \
  wget -qO /tmp/gitleaks.tgz "https://github.com/gitleaks/gitleaks/releases/download/v${GITLEAKS_VERSION}/gitleaks_${GITLEAKS_VERSION}_linux_${GLARCH}.tar.gz" \
  && tar xzf /tmp/gitleaks.tgz -C /usr/local/bin gitleaks && rm /tmp/gitleaks.tgz

RUN curl -sSfL https://raw.githubusercontent.com/trufflesecurity/trufflehog/main/scripts/install.sh \
  | sh -s -- -b /usr/local/bin

RUN bunx puppeteer browsers install chrome

# system-wide zshrc — every zsh user loads this
RUN mkdir -p /etc/zsh && printf '%s\n' \
  '[ -r /usr/share/doc/fzf/examples/key-bindings.zsh ] && source /usr/share/doc/fzf/examples/key-bindings.zsh' \
  '[ -r /usr/share/doc/fzf/examples/completion.zsh ] && source /usr/share/doc/fzf/examples/completion.zsh' \
  'export HISTFILE="$HOME/.zsh_history"' \
  > /etc/zsh/zshrc

# claude wrapper at /usr/local/bin. Sources nvm.sh so per-project .nvmrc is
# honored; falls back to the symlinked default node otherwise. jq strips the
# host's native-install keys so the container's npm claude doesn't warn about a
# ~/.local/bin/claude that only exists on the host.
RUN printf '#!/bin/sh\n\
[ -f /tmp/host-claude.json ] && { jq "del(.installMethod,.autoUpdates,.autoUpdatesProtectedForNative)" /tmp/host-claude.json > "$HOME/.claude.json" 2>/dev/null || cp /tmp/host-claude.json "$HOME/.claude.json"; }\n\
[ -f "$HOME/.claude.json" ] || echo "{\"hasCompletedOnboarding\":true}" > "$HOME/.claude.json"\n\
export NVM_DIR="/opt/dev-tools/nvm"\n\
unset NPM_CONFIG_PREFIX\n\
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"\n\
exec /usr/local/share/npm-global/bin/claude --dangerously-skip-permissions "$@"\n' \
  > /usr/local/bin/claude && chmod +x /usr/local/bin/claude

# dockbox-init: register the runtime user in /etc/passwd, chown overmounts
# and $HOME (top-level only — nested bind mounts must not be touched), then
# gosu-drop to DOCKBOX_UID:DOCKBOX_GID before exec'ing the command.
# Before the drop it adds the runtime user to every --group-add supplementary
# gid (e.g. the docker socket's group from `dockbox -D`): gosu re-runs
# initgroups from /etc/group, so a `docker run --group-add` alone is lost on
# the drop unless the user is also a member in the container's /etc/group.
# Sanitizes DOCKBOX_USER (only [A-Za-z0-9_-] allowed) so a malicious value
# can't inject extra fields into /etc/passwd. Defaults CMD to /bin/zsh when
# none is provided so `gosu` doesn't error on empty args. chown failures
# print a warning instead of being silent.
RUN printf '#!/bin/sh\n\
set -eu\n\
USERNAME="${DOCKBOX_USER:-dockbox}"\n\
case "$USERNAME" in *[!A-Za-z0-9_-]*|"") USERNAME=dockbox ;; esac\n\
USER_UID="${DOCKBOX_UID:-1000}"\n\
case "$USER_UID" in ""|*[!0-9]*) USER_UID=1000 ;; esac\n\
USER_GID="${DOCKBOX_GID:-1000}"\n\
case "$USER_GID" in ""|*[!0-9]*) USER_GID=1000 ;; esac\n\
HOME_DIR="${HOME:-/home/dockbox}"\n\
if [ "$(id -u)" = "0" ]; then\n\
  getent passwd "$USER_UID" >/dev/null 2>&1 || \\\n\
    echo "${USERNAME}:x:${USER_UID}:${USER_GID}::${HOME_DIR}:/bin/zsh" >> /etc/passwd\n\
  getent group "$USER_GID" >/dev/null 2>&1 || \\\n\
    echo "${USERNAME}:x:${USER_GID}:" >> /etc/group\n\
  getent shadow "$USERNAME" >/dev/null 2>&1 || \\\n\
    echo "${USERNAME}:!:19000:0:99999:7:::" >> /etc/shadow\n\
  if [ "${DOCKBOX_SUDO:-}" = "1" ]; then\n\
    echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/dockbox-${USERNAME}\n\
    chmod 0440 /etc/sudoers.d/dockbox-${USERNAME}\n\
  fi\n\
  [ -d "$HOME_DIR" ] && \\\n\
    { chown "${USER_UID}:${USER_GID}" "$HOME_DIR" || echo "dockbox-init: chown $HOME_DIR failed" >&2; }\n\
  if [ -n "${DOCKBOX_EPH_PATHS:-}" ]; then\n\
    IFS=:\n\
    for p in $DOCKBOX_EPH_PATHS; do\n\
      [ -d "$p" ] && \\\n\
        { chown "${USER_UID}:${USER_GID}" "$p" || echo "dockbox-init: chown $p failed" >&2; }\n\
    done\n\
    unset IFS\n\
  fi\n\
  for g in $(id -G); do\n\
    case "$g" in 0|"$USER_GID") continue ;; esac\n\
    gname="$(getent group "$g" | cut -d: -f1)"\n\
    gmem="$(getent group "$g" | cut -d: -f4)"\n\
    [ -z "$gname" ] && gname="hostgrp$g"\n\
    case ",$gmem," in *",$USERNAME,"*) continue ;; esac\n\
    [ -n "$gmem" ] && gmem="$gmem,$USERNAME" || gmem="$USERNAME"\n\
    sed -i "/^$gname:/d" /etc/group\n\
    echo "$gname:x:$g:$gmem" >> /etc/group\n\
  done\n\
  mkdir -p /run/dockbox/sess && touch /run/dockbox/ready\n\
  [ "$#" -eq 0 ] && set -- /bin/zsh\n\
  exec gosu "$USERNAME" "$@"\n\
fi\n\
[ "$#" -eq 0 ] && set -- /bin/zsh\n\
exec "$@"\n' > /usr/local/bin/dockbox-init && chmod +x /usr/local/bin/dockbox-init

# World-readable + writable tooling so any runtime UID can use it
RUN chmod -R a+rwX /opt/dev-tools /usr/local/share/npm-global /workspace /home/dockbox
