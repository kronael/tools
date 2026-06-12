# BUGS

Review queue. Log here, fix when prioritised — not on sight.

## dockbox: `-D` docker socket unusable after gosu drop

**Symptom:** testcontainers (and anything as the runtime user) inside
`dockbox -D` can't reach `/var/run/docker.sock` — "gid 1000 isn't in the
socket's group (964)".

**Root cause:** `dockbox` passes `--group-add $(stat -c %g docker.sock)`
(=964) to `docker run`, but that group lands on the **root init process
only**. `dockbox-init` creates the runtime user with `${USERNAME}:x:${USER_GID}:`
(gid 1000) and `exec gosu ${UID}:${GID}` — gosu's `initgroups` reads
`/etc/group`, finds the user in no group 964, and drops the supplementary
group. Socket is `srw-rw---- root docker` (mode 660), so the dropped user
is denied.

**Fix (Dockerfile `dockbox-init` heredoc, before the `gosu` exec):** add the
runtime user to each non-primary supplementary gid the container was started
with, so `initgroups` preserves it:
```sh
for g in $(id -G); do
  case "$g" in 0|"$USER_GID") continue ;; esac
  getent group "$g" >/dev/null 2>&1 || groupadd -g "$g" "hostgrp$g"
  usermod -aG "$g" "$USERNAME"
done
```
Requires `make image` rebuild + a testcontainers smoke test inside dockbox.

**NOT the fix:** `chmod 666 /var/run/docker.sock` on the host — world-writable
socket is root-equivalent for every process on the box, and unnecessary (host
ondra is already in `docker` group; the socket answers).
