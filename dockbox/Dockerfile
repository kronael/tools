FROM node:20

ARG TZ
ENV TZ="$TZ"

ARG CLAUDE_CODE_VERSION=latest

# Install basic development tools and iptables/ipset
RUN apt-get update && apt-get install -y --no-install-recommends \
  less \
  git \
  procps \
  sudo \
  fzf \
  zsh \
  man-db \
  unzip \
  gnupg2 \
  gh \
  iptables \
  ipset \
  iproute2 \
  dnsutils \
  aggregate \
  jq \
  nano \
  vim \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

# Create claude user with configurable uid to match host user
ARG UID=1000
RUN userdel -rf node 2>/dev/null; \
  useradd -m -s /bin/zsh -u $UID claude && \
  mkdir -p /usr/local/share/npm-global && \
  chown -R claude:claude /usr/local/share


# Set `DEVCONTAINER` environment variable to help with orientation
ENV DEVCONTAINER=true

# Create workspace and config directories and set permissions
RUN mkdir -p /workspace /home/claude/.claude && \
  chown -R claude:claude /workspace /home/claude/.claude

WORKDIR /workspace

ARG GIT_DELTA_VERSION=0.18.2
RUN ARCH=$(dpkg --print-architecture) && \
  wget "https://github.com/dandavison/delta/releases/download/${GIT_DELTA_VERSION}/git-delta_${GIT_DELTA_VERSION}_${ARCH}.deb" && \
  sudo dpkg -i "git-delta_${GIT_DELTA_VERSION}_${ARCH}.deb" && \
  rm "git-delta_${GIT_DELTA_VERSION}_${ARCH}.deb"

# Enable pnpm via corepack (needs root)
RUN corepack enable && corepack prepare pnpm@latest --activate

# Set up non-root user
USER claude

# Install global packages
ENV NPM_CONFIG_PREFIX=/usr/local/share/npm-global
ENV PATH=$PATH:/usr/local/share/npm-global/bin

# Set the default shell to zsh rather than sh
ENV SHELL=/bin/zsh

# Set the default editor and visual
ENV EDITOR=nano
ENV VISUAL=nano

# Default powerline10k theme
ARG ZSH_IN_DOCKER_VERSION=1.2.0
RUN sh -c "$(wget -O- https://github.com/deluan/zsh-in-docker/releases/download/v${ZSH_IN_DOCKER_VERSION}/zsh-in-docker.sh)" -- \
  -p git \
  -p fzf \
  -a "source /usr/share/doc/fzf/examples/key-bindings.zsh" \
  -a "source /usr/share/doc/fzf/examples/completion.zsh" \
  -a "export HISTFILE=/home/claude/.zsh_history" \
  -x

# Install nvm
ENV NVM_DIR="/home/claude/.nvm"
RUN curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash

# Install bun
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/home/claude/.bun/bin:$PATH"

# Install rustup
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/home/claude/.cargo/bin:$PATH"

# Install g (Go version manager)
RUN curl -sSL https://git.io/g-install | sh -s -- -y
ENV PATH="/home/claude/go/bin:/home/claude/.go/bin:$PATH"
ENV GOPATH="/home/claude/go"

# Install AI coding tools
RUN bun install -g @anthropic-ai/claude-code@${CLAUDE_CODE_VERSION} \
  @openai/codex \
  @mariozechner/pi-coding-agent

# Claude wrapper to init .claude.json at startup (if not mounted)
RUN mkdir -p /home/claude/.local/bin && \
  printf '#!/bin/sh\n[ -f /tmp/host-claude.json ] && cp /tmp/host-claude.json /home/claude/.claude.json\n[ -f /home/claude/.claude.json ] || echo "{\"hasCompletedOnboarding\":true}" > /home/claude/.claude.json\nexec /home/claude/.bun/bin/claude "$@"\n' > /home/claude/.local/bin/claude && \
  chmod +x /home/claude/.local/bin/claude
ENV PATH="/home/claude/.local/bin:$PATH"
