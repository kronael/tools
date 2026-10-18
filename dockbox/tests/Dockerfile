FROM debian:forky

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash ca-certificates curl git gosu iproute2 iptables jq procps \
    util-linux docker.io docker-cli && apt-get clean \
    && rm -f /var/lib/apt/lists/*_*
COPY dockbox/dockbox-init dockbox/dockbox-docker \
    dockbox/dockbox-codex-bridge /usr/local/bin/
COPY codex/AGENTS.md /opt/dockbox/codex-AGENTS.md
RUN mkdir -p /home/dockbox /workspace /etc/sudoers.d
WORKDIR /workspace
ENTRYPOINT ["/usr/local/bin/dockbox-init"]
CMD ["sleep", "infinity"]
