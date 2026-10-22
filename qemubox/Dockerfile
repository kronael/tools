FROM debian:forky AS dockbox

ENV TZ=UTC

ARG CLAUDE_CODE_VERSION=latest

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

RUN curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg \
      | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" \
       > /etc/apt/sources.list.d/google-cloud-sdk.list \
    && apt-get update && apt-get install -y --no-install-recommends google-cloud-cli \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN corepack enable && corepack prepare pnpm@latest --activate

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

RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
  mkdir -p /opt/dev-tools/uv/bin && \
  mv /root/.local/bin/uv /opt/dev-tools/uv/bin/ && \
  mv /root/.local/bin/uvx /opt/dev-tools/uv/bin/ 2>/dev/null || true

RUN for t in pre-commit bandit pip-audit semgrep; do uv tool install "$t"; done

RUN curl -fsSL https://get.sdkman.io | bash

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

RUN mkdir -p /etc/zsh && printf '%s\n' \
  '[ -r /usr/share/doc/fzf/examples/key-bindings.zsh ] && source /usr/share/doc/fzf/examples/key-bindings.zsh' \
  '[ -r /usr/share/doc/fzf/examples/completion.zsh ] && source /usr/share/doc/fzf/examples/completion.zsh' \
  'export HISTFILE="$HOME/.zsh_history"' \
  > /etc/zsh/zshrc

RUN printf '#!/bin/sh\n\
[ -f /tmp/host-claude.json ] && { jq "del(.installMethod,.autoUpdates,.autoUpdatesProtectedForNative) + {diffSidebarOpen:false}" /tmp/host-claude.json > "$HOME/.claude.json" 2>/dev/null || cp /tmp/host-claude.json "$HOME/.claude.json"; }\n\
[ -f "$HOME/.claude.json" ] || echo "{\"hasCompletedOnboarding\":true,\"diffSidebarOpen\":false}" > "$HOME/.claude.json"\n\
export NVM_DIR="/opt/dev-tools/nvm"\n\
unset NPM_CONFIG_PREFIX\n\
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"\n\
exec /opt/dev-tools/bun/bin/claude --dangerously-skip-permissions "$@"\n' \
  > /usr/local/bin/claude && chmod +x /usr/local/bin/claude

COPY dockbox/dockbox-init dockbox/dockbox-docker \
    dockbox/dockbox-codex-bridge /usr/local/bin/

RUN chmod -R a+rwX /opt/dev-tools /usr/local/share/npm-global /workspace /home/dockbox

ARG RIPWIRE_VERSION=0.6.5
ENV UV_PYTHON_INSTALL_DIR=/opt/dev-tools/uv/python \
    SERENA_HOME=/opt/dev-tools/serena
RUN apt-get update && apt-get install -y --no-install-recommends \
    graphviz ffmpeg texlive-latex-base texlive-latex-recommended texlive-latex-extra dvisvgm \
    libcairo2-dev libpango1.0-dev \
  && apt-get clean && rm -f /var/lib/apt/lists/*_* \
  && uv tool install ast-grep-cli && rm -f /opt/dev-tools/uv/bin/sg \
  && uv tool install ruff \
  && UV_COMPILE_BYTECODE=1 uv tool install -p 3.13 serena-agent \
  && CC=clang UV_COMPILE_BYTECODE=1 uv tool install -p 3.13 manim \
  && serena init \
  && sed -i \
    -e 's|^web_dashboard: .*|web_dashboard: false|' \
    -e 's|^excluded_tools: .*|excluded_tools: [onboarding, list_memories, read_memory, write_memory, edit_memory, rename_memory, delete_memory]|' \
    -e 's|^project_serena_folder_location: .*|project_serena_folder_location: "/opt/dev-tools/serena/projects/$projectFolderName"|' \
    "$SERENA_HOME/serena_config.yml" \
  && grep -qx 'web_dashboard: false' "$SERENA_HOME/serena_config.yml" \
  && grep -q '^excluded_tools: \[onboarding' "$SERENA_HOME/serena_config.yml" \
  && grep -q '^project_serena_folder_location: "/opt/dev-tools/serena/projects/' "$SERENA_HOME/serena_config.yml" \
  && ARCH=$(dpkg --print-architecture) \
  && case "$ARCH" in amd64) RWARCH=x64 ;; arm64) RWARCH=arm64 ;; *) RWARCH=$ARCH ;; esac \
  && RW=ripwire-${RIPWIRE_VERSION}-linux-${RWARCH} \
  && cd /tmp && wget -q "https://github.com/redhat-et/ripwire/releases/download/v${RIPWIRE_VERSION}/${RW}.tar.gz" \
     "https://github.com/redhat-et/ripwire/releases/download/v${RIPWIRE_VERSION}/${RW}.tar.gz.sha256" \
  && sha256sum -c "${RW}.tar.gz.sha256" \
  && tar xzf "${RW}.tar.gz" "${RW}/ripwire" \
  && install -m 755 "${RW}/ripwire" /usr/local/bin/ripwire \
  && rm -f "${RW}.tar.gz" "${RW}.tar.gz.sha256" "${RW}/ripwire" && rmdir "${RW}" \
  && ripwire --version \
  && chmod -R a+rwX /opt/dev-tools/uv /opt/dev-tools/serena

COPY codex/AGENTS.md /opt/dockbox/codex-AGENTS.md

ARG AGENTS_CACHEBUST=0
RUN echo "agents cachebust: $AGENTS_CACHEBUST" \
  && bun install -g --trust @anthropic-ai/claude-code@${CLAUDE_CODE_VERSION} \
  && bun install -g @openai/codex \
  && chmod -R a+rwX /opt/dev-tools/bun

RUN apt-get update && apt-get install -y --no-install-recommends docker-cli gcc \
    && apt-get clean && rm -f /var/lib/apt/lists/*_*

RUN printf '%s\n' \
    'github.com ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOMqqnkVzrm0SdG6UOoqKLsabgH5C9okWi0dh2l9GKJl' \
    'github.com ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBEmKSENjQEezOmxkZMy7opKgwFB9nkt5YRrYMjNuG5N87uRgg6CLrbo5wAdT/y6v0mKV0U2w0WZ2YB/++Tpockg=' \
    >> /etc/ssh/ssh_known_hosts

FROM dockbox AS vm

RUN apt-get update && apt-get install -y --no-install-recommends \
    linux-image-amd64 initramfs-tools systemd-sysv udev dbus kmod \
    openssh-server systemd-timesyncd systemd-resolved e2fsprogs \
    && apt-get clean && rm -f /var/lib/apt/lists/*_* \
    && rm -f /usr/sbin/policy-rc.d /etc/apt/apt.conf.d/docker-* \
       /etc/dpkg/dpkg.cfg.d/docker-* /etc/ssh/ssh_host_* \
    && printf '%s\n' virtio_pci virtio_blk ext4 >> /etc/initramfs-tools/modules \
    && update-initramfs -u -k all \
    && systemctl disable docker.service containerd.service \
    && systemctl enable systemd-networkd systemd-resolved systemd-timesyncd ssh docker.socket \
    && systemctl mask ssh.socket \
    && truncate -s 0 /etc/machine-id \
    && rm -f /var/lib/dbus/machine-id \
    && ln -s /etc/machine-id /var/lib/dbus/machine-id

RUN for key in DEVCONTAINER SHELL EDITOR VISUAL DISABLE_AUTOUPDATER \
    CLAUDE_CODE_DISABLE_AUTOUPDATE NPM_CONFIG_PREFIX NVM_DIR BUN_INSTALL \
    CARGO_HOME RUSTUP_HOME GOROOT GOPATH SDKMAN_DIR PLAYWRIGHT_BROWSERS_PATH \
    PUPPETEER_CACHE_DIR UV_TOOL_BIN_DIR UV_TOOL_DIR UV_PYTHON_INSTALL_DIR SERENA_HOME \
    DOTNET_ROOT PATH; do \
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
    'groups="$groups $(getent group docker | cut -d: -f3):docker"' \
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
    'ssh-keygen -A' \
    'ln -sf /run/systemd/resolve/resolv.conf /etc/resolv.conf' \
    'resize2fs /dev/vda' \
    'touch /run/qemubox/ready' \
    'echo '"'"'qemubox: ready'"'"'' \
    > /usr/local/bin/qemubox-init && chmod 755 /usr/local/bin/qemubox-init
ENTRYPOINT ["/sbin/init"]
WORKDIR /
