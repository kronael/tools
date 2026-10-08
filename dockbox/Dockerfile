FROM debian:forky AS dockbox

ENV TZ=UTC

ARG CLAUDE_CODE_VERSION=latest

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
  qemu-system-x86 qemu-utils cloud-image-utils openssh-client \
  jq yq bc nano vim docker.io clang mold libclang-dev libudev-dev libssl-dev libpq-dev postgresql-client pkg-config protobuf-compiler \
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
RUN curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.7/install.sh | bash && \
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

ARG NU_VERSION=0.115.0
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

RUN bun install -g \
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
# host's native-install keys so the container's bun claude doesn't warn about a
# ~/.local/bin/claude that only exists on the host, and pins diffSidebarOpen so
# the diff tab stays closed (it is global config in ~/.claude.json, not a
# settings.json key, so it cannot be shipped in settings-recommended.json).
RUN printf '#!/bin/sh\n\
[ -f /tmp/host-claude.json ] && { jq "del(.installMethod,.autoUpdates,.autoUpdatesProtectedForNative) + {diffSidebarOpen:false}" /tmp/host-claude.json > "$HOME/.claude.json" 2>/dev/null || cp /tmp/host-claude.json "$HOME/.claude.json"; }\n\
[ -f "$HOME/.claude.json" ] || echo "{\"hasCompletedOnboarding\":true,\"diffSidebarOpen\":false}" > "$HOME/.claude.json"\n\
export NVM_DIR="/opt/dev-tools/nvm"\n\
unset NPM_CONFIG_PREFIX\n\
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"\n\
exec /opt/dev-tools/bun/bin/claude --dangerously-skip-permissions "$@"\n' \
  > /usr/local/bin/claude && chmod +x /usr/local/bin/claude

# dockbox-codex-bridge: expose the installed Claude bundle to Codex for the
# runtime user's $HOME. Codex scans ~/.agents/skills, linked to the ~/.claude
# bundle, and loads global guidance from ~/.codex/AGENTS.md, which gets the
# Kronael block telling it to read ~/.claude/CLAUDE.md. ~/.codex is the host's
# directory mounted rw, so a real file or any other link there is left alone;
# only a link to the wisdom file is replaced, removed first so the copy cannot
# write through it. Idempotent and a no-op until the bundle is installed into
# $HOME, so it is safe on every start. The skills link is RELATIVE so it
# resolves under whichever home reads it.
RUN printf '%s\n' \
  '#!/bin/sh' \
  'set -eu' \
  '[ -d "$HOME/.claude/skills" ] || exit 0' \
  'mkdir -p "$HOME/.agents"' \
  '[ -e "$HOME/.agents/skills" ] || ln -s ../.claude/skills "$HOME/.agents/skills"' \
  '[ -f "$HOME/.claude/CLAUDE.md" ] || exit 0' \
  'if [ -L "$HOME/.codex/AGENTS.md" ]; then' \
  '  case "$(readlink "$HOME/.codex/AGENTS.md")" in' \
  '    */.claude/CLAUDE.md) ;;' \
  '    *) exit 0 ;;' \
  '  esac' \
  'elif [ -e "$HOME/.codex/AGENTS.md" ]; then' \
  '  exit 0' \
  'fi' \
  'mkdir -p "$HOME/.codex"' \
  'rm -f "$HOME/.codex/AGENTS.md"' \
  'cp /opt/dockbox/codex-AGENTS.md "$HOME/.codex/AGENTS.md"' \
  > /usr/local/bin/dockbox-codex-bridge && chmod +x /usr/local/bin/dockbox-codex-bridge

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
  gosu "$USERNAME" env HOME="$HOME_DIR" /usr/local/bin/dockbox-codex-bridge || true\n\
  exec gosu "$USERNAME" "$@"\n\
fi\n\
[ "$#" -eq 0 ] && set -- /bin/zsh\n\
/usr/local/bin/dockbox-codex-bridge || true\n\
exec "$@"\n' > /usr/local/bin/dockbox-init && chmod +x /usr/local/bin/dockbox-init

# World-readable + writable tooling so any runtime UID can use it
RUN chmod -R a+rwX /opt/dev-tools /usr/local/share/npm-global /workspace /home/dockbox

# Kronael block for dockbox-codex-bridge, read only at container start. Below
# the big chmod so editing the block keeps that layer cached.
COPY codex/AGENTS.md /opt/dockbox/codex-AGENTS.md

# claude + codex CLIs last, in a cache-busted layer, so every `make image`
# refreshes them to latest without re-running the heavier layers above. The
# Makefile passes a fresh AGENTS_CACHEBUST each build to defeat the layer cache;
# pin by building with --build-arg CLAUDE_CODE_VERSION=<v>. chmod only the bun
# install tree so the big chmod above stays cached. Both CLIs install via bun
# (--trust runs claude-code's postinstall so its bundled ripgrep is fetched).
ARG AGENTS_CACHEBUST=0
RUN echo "agents cachebust: $AGENTS_CACHEBUST" \
  && bun install -g --trust @anthropic-ai/claude-code@${CLAUDE_CODE_VERSION} \
  && bun install -g @openai/codex \
  && chmod -R a+rwX /opt/dev-tools/bun

# gcc sits in this late layer, which every build reruns anyway: psycopg2 and
# other sdists call x86_64-linux-gnu-gcc, which clang does not provide.
RUN apt-get update && apt-get install -y --no-install-recommends docker-cli gcc \
    && apt-get clean && rm -f /var/lib/apt/lists/*_*

FROM dockbox AS vm

RUN apt-get update && apt-get install -y --no-install-recommends \
    linux-image-amd64 initramfs-tools systemd-sysv udev dbus kmod \
    openssh-server systemd-timesyncd systemd-resolved e2fsprogs \
    && apt-get clean && rm -f /var/lib/apt/lists/*_* \
    && rm -f /usr/sbin/policy-rc.d /etc/apt/apt.conf.d/docker-* \
       /etc/dpkg/dpkg.cfg.d/docker-* /etc/ssh/ssh_host_* \
    && printf '%s\n' virtio_pci virtio_blk ext4 >> /etc/initramfs-tools/modules \
    && update-initramfs -u -k all \
    && systemctl disable docker.service containerd.service docker.socket \
    && systemctl enable systemd-networkd systemd-resolved systemd-timesyncd ssh \
    && systemctl mask ssh.socket \
    && truncate -s 0 /etc/machine-id \
    && rm -f /var/lib/dbus/machine-id \
    && ln -s /etc/machine-id /var/lib/dbus/machine-id

RUN for key in DEVCONTAINER SHELL EDITOR VISUAL DISABLE_AUTOUPDATER \
    CLAUDE_CODE_DISABLE_AUTOUPDATE NPM_CONFIG_PREFIX NVM_DIR BUN_INSTALL \
    CARGO_HOME RUSTUP_HOME GOROOT GOPATH SDKMAN_DIR PLAYWRIGHT_BROWSERS_PATH \
    PUPPETEER_CACHE_DIR UV_TOOL_BIN_DIR UV_TOOL_DIR DOTNET_ROOT PATH; do \
      value="$(printenv "$key")"; \
      printf '%s="%s"\n' "$key" "$value" >> /etc/environment; \
      printf 'export %s="%s"\n' "$key" "$value" >> /etc/profile.d/dev-tools.sh; \
    done \
    && echo '. /etc/profile.d/dev-tools.sh' >> /etc/zsh/zshenv

RUN mkdir -p /etc/systemd/network /etc/systemd/system/ssh.service.d \
    && printf '%s\n' '[Match]' 'Name=en* eth*' '[Network]' 'DHCP=yes' \
       > /etc/systemd/network/20-qemubox.network \
    && printf '%s\n' '[Unit]' 'Requires=qemubox-init.service' \
       'After=qemubox-init.service' > /etc/systemd/system/ssh.service.d/qemubox.conf \
    && printf '%s\n' 'PasswordAuthentication no' 'KbdInteractiveAuthentication no' \
       'PermitRootLogin no' 'StreamLocalBindUnlink yes' > /etc/ssh/sshd_config.d/qemubox.conf \
    && printf '%s\n' '[Unit]' 'After=local-fs.target' 'Before=ssh.service' \
       '[Service]' 'Type=oneshot' 'ExecStart=/usr/local/bin/qemubox-init' \
       'StandardOutput=journal+console' 'StandardError=journal+console' \
       'RemainAfterExit=yes' '[Install]' 'WantedBy=multi-user.target' \
       > /etc/systemd/system/qemubox-init.service \
    && systemctl enable qemubox-init.service

RUN printf '%s\n' \
    '#!/usr/bin/env bash' \
    'set -Eeuo pipefail' \
    'trap '"'"'echo "qemubox-init: failed at line $LINENO" >&2'"'"' ERR' \
    '' \
    'printf '"'"'127.0.0.1 localhost\n::1 localhost\n127.0.1.1 %s\n'"'"' "$(cat /proc/sys/kernel/hostname)" > /etc/hosts' \
    'mkdir -p /run/qemubox/config' \
    'modprobe -a 9p 9pnet_virtio' \
    'mount -t 9p -o trans=virtio,version=9p2000.L,ro qbxcfg /run/qemubox/config' \
    '{' \
    '    read -r username' \
    '    read -r user_uid' \
    '    read -r user_gid' \
    '    IFS= read -r home_dir' \
    '    read -r groups' \
    '    IFS= read -r zone' \
    '} < /run/qemubox/config/identity' \
    '[[ "$username" =~ ^[A-Za-z0-9_-]+$ && "$user_uid" =~ ^[0-9]+$ &&' \
    '    "$user_gid" =~ ^[0-9]+$ && "$home_dir" = /* && "$home_dir" != *:* ]]' \
    '[[ "$user_uid" != 0 ]]' \
    '[[ "$zone" != /* && "$zone" != *..* && -f "/usr/share/zoneinfo/$zone" ]]' \
    'ln -sf "/usr/share/zoneinfo/$zone" /etc/localtime' \
    '' \
    'passwd_entry="$username:x:$user_uid:$user_gid::$home_dir:/bin/bash"' \
    'if entry=$(getent passwd "$user_uid")' \
    then \
    '    [[ "$entry" = "$passwd_entry" ]]' \
    else \
    '    if getent passwd "$username" >/dev/null' \
    '    then' \
    '        echo "qemubox-init: conflicting user $username" >&2' \
    '        exit 1' \
    '    fi' \
    '    echo "$passwd_entry" >> /etc/passwd' \
    fi \
    'if ! getent shadow "$username" >/dev/null' \
    then \
    '    echo "$username:!:19000:0:99999:7:::" >> /etc/shadow' \
    fi \
    'for group in $groups' \
    do \
    '    gid=${group%%:*}' \
    '    gname=${group#*:}' \
    '    [[ "$gid" =~ ^[0-9]+$ ]]' \
    '    [[ "$gname" =~ ^[A-Za-z0-9_-]+$ ]] || gname="hostgrp$gid"' \
    '    if entry=$(getent group "$gid")' \
    '    then' \
    '        gname=${entry%%:*}' \
    '        members=${entry##*:}' \
    '    else' \
    '        members=""' \
    '        getent group "$gname" >/dev/null && gname="hostgrp$gid"' \
    '    fi' \
    '    case ",$members," in' \
    '        *",$username,"*) ;;' \
    '        *) members="${members:+$members,}$username" ;;' \
    '    esac' \
    '    sed -i "/^$gname:/d" /etc/group' \
    '    printf "%s:x:%s:%s\\n" "$gname" "$gid" "$members" >> /etc/group' \
    done \
    'getent group "$user_gid" >/dev/null' \
    'echo "$username ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/qemubox' \
    'chmod 0440 /etc/sudoers.d/qemubox' \
    'visudo -cf /etc/sudoers.d/qemubox' \
    'mkdir -p "$home_dir/.ssh"' \
    'chown "$user_uid:$user_gid" "$home_dir" "$home_dir/.ssh"' \
    'chmod 700 "$home_dir/.ssh"' \
    'install -m 600 -o "$user_uid" -g "$user_gid" \' \
    '    /run/qemubox/config/authorized_keys "$home_dir/.ssh/authorized_keys"' \
    'rm -f /etc/ssh/ssh_host_*' \
    'ssh-keygen -A' \
    'ln -sf /run/systemd/resolve/resolv.conf /etc/resolv.conf' \
    'resize2fs /dev/vda' \
    'touch /run/qemubox/ready' \
    'echo '"'"'qemubox: ready'"'"'' \
    > /usr/local/bin/qemubox-init && chmod 755 /usr/local/bin/qemubox-init
ENTRYPOINT ["/sbin/init"]
WORKDIR /
