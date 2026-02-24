FROM node:20

ARG TZ=UTC
ENV TZ="$TZ"

ARG CLAUDE_CODE_VERSION=latest

RUN apt-get update && apt-get install -y --no-install-recommends \
  less git procps sudo fzf zsh man-db unzip gnupg2 gh \
  iptables ipset iproute2 dnsutils aggregate \
  jq nano vim \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

ARG UID=1000
RUN userdel -rf node 2>/dev/null; \
  useradd -m -s /bin/zsh -u $UID claude && \
  mkdir -p /usr/local/share/npm-global && \
  chown -R claude:claude /usr/local/share

ENV DEVCONTAINER=true

RUN mkdir -p /workspace /home/claude/.claude && \
  chown -R claude:claude /workspace /home/claude/.claude

WORKDIR /workspace

ARG GIT_DELTA_VERSION=0.18.2
RUN ARCH=$(dpkg --print-architecture) && \
  wget "https://github.com/dandavison/delta/releases/download/${GIT_DELTA_VERSION}/git-delta_${GIT_DELTA_VERSION}_${ARCH}.deb" && \
  dpkg -i "git-delta_${GIT_DELTA_VERSION}_${ARCH}.deb" && \
  rm "git-delta_${GIT_DELTA_VERSION}_${ARCH}.deb"

RUN corepack enable && corepack prepare pnpm@latest --activate

USER claude

ENV NPM_CONFIG_PREFIX=/usr/local/share/npm-global \
    PATH="$PATH:/usr/local/share/npm-global/bin" \
    SHELL=/bin/zsh \
    EDITOR=nano \
    VISUAL=nano

ARG ZSH_IN_DOCKER_VERSION=1.2.0
RUN sh -c "$(wget -O- https://github.com/deluan/zsh-in-docker/releases/download/v${ZSH_IN_DOCKER_VERSION}/zsh-in-docker.sh)" -- \
  -p git \
  -p fzf \
  -a "source /usr/share/doc/fzf/examples/key-bindings.zsh" \
  -a "source /usr/share/doc/fzf/examples/completion.zsh" \
  -a "export HISTFILE=/home/claude/.zsh_history" \
  -x

ENV NVM_DIR="/home/claude/.nvm"
RUN curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash

RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/home/claude/.bun/bin:$PATH"

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \
  | sh -s -- -y
ENV PATH="/home/claude/.cargo/bin:$PATH"

RUN curl -sSL https://git.io/g-install | sh -s -- -y
ENV PATH="/home/claude/go/bin:/home/claude/.go/bin:$PATH" \
    GOPATH="/home/claude/go"

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/home/claude/.local/bin:$PATH"

RUN curl -fsSL https://get.sdkman.io | bash
ENV SDKMAN_DIR="/home/claude/.sdkman"

RUN bun install -g @anthropic-ai/claude-code@${CLAUDE_CODE_VERSION} \
  @openai/codex \
  @mariozechner/pi-coding-agent

# Wrapper: copy host .claude.json at startup, ensure onboarding
RUN mkdir -p /home/claude/.local/bin && \
  printf '#!/bin/sh\n\
[ -f /tmp/host-claude.json ] && cp /tmp/host-claude.json /home/claude/.claude.json\n\
[ -f /home/claude/.claude.json ] || echo "{\"hasCompletedOnboarding\":true}" > /home/claude/.claude.json\n\
exec /home/claude/.bun/bin/claude "$@"\n' \
  > /home/claude/.local/bin/claude && \
  chmod +x /home/claude/.local/bin/claude
ENV PATH="/home/claude/.local/bin:$PATH"
