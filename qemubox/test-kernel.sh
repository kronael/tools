#!/usr/bin/env bash

kernel_config_test() {
    local config="$1" line option count=0
    while IFS= read -r line
    do
        if [[ "$line" == '# CONFIG_'*' is not set' ]]
        then
            option=${line#'# '}
            option=${option%' is not set'}
            if grep -Eq "^$option=[ym]$" "$config"
            then
                echo "Unexpected kernel setting: $option" >&2
                return 1
            fi
        elif ! grep -Fxq -- "$line" "$config"
        then
            echo "Missing kernel setting: $line" >&2
            return 1
        fi
        count=$((count + 1))
    done <<'CONFIG'
CONFIG_64BIT=y
CONFIG_X86_64=y
CONFIG_SMP=y
# CONFIG_BASE_SMALL is not set
CONFIG_HYPERVISOR_GUEST=y
CONFIG_KVM_GUEST=y
CONFIG_ACPI=y
CONFIG_PCI=y
CONFIG_PCI_MSI=y
CONFIG_PCI_MMCONFIG=y
CONFIG_PCIEPORTBUS=y
CONFIG_VIRTIO=y
CONFIG_VIRTIO_PCI=y
CONFIG_VIRTIO_PCI_LEGACY=y
CONFIG_VIRTIO_BLK=y
CONFIG_VIRTIO_NET=y
CONFIG_VIRTIO_BALLOON=y
CONFIG_VIRTIO_MEM=y
CONFIG_MEMORY_HOTPLUG=y
CONFIG_MEMORY_BALLOON=y
CONFIG_PAGE_REPORTING=y
CONFIG_HW_RANDOM=y
CONFIG_HW_RANDOM_VIRTIO=y
CONFIG_FUSE_FS=y
CONFIG_VIRTIO_FS=y
# CONFIG_FUSE_DAX is not set
CONFIG_OVERLAY_FS=y
CONFIG_EXT4_FS=y
CONFIG_EXT4_FS_POSIX_ACL=y
CONFIG_EXT4_FS_SECURITY=y
# CONFIG_EXT4_DEBUG is not set
CONFIG_TMPFS=y
CONFIG_TMPFS_POSIX_ACL=y
CONFIG_TMPFS_XATTR=y
CONFIG_SHMEM=y
CONFIG_SWAP=y
# CONFIG_ZRAM is not set
# CONFIG_ZSWAP is not set
CONFIG_DEVTMPFS=y
CONFIG_DEVTMPFS_MOUNT=y
CONFIG_PROC_FS=y
CONFIG_SYSFS=y
CONFIG_UNIX98_PTYS=y
CONFIG_SERIAL_8250=y
CONFIG_SERIAL_8250_CONSOLE=y
CONFIG_BLK_DEV_INITRD=y
CONFIG_RD_GZIP=y
CONFIG_BINFMT_ELF=y
CONFIG_BINFMT_SCRIPT=y
CONFIG_UNIX=y
CONFIG_INET=y
CONFIG_IPV6=y
CONFIG_IP_PNP=y
# CONFIG_IP_PNP_DHCP is not set
# CONFIG_IP_PNP_BOOTP is not set
# CONFIG_IP_PNP_RARP is not set
CONFIG_INOTIFY_USER=y
CONFIG_NAMESPACES=y
CONFIG_NET_NS=y
CONFIG_PID_NS=y
CONFIG_IPC_NS=y
CONFIG_UTS_NS=y
CONFIG_USER_NS=y
CONFIG_CGROUPS=y
CONFIG_CGROUP_CPUACCT=y
CONFIG_CGROUP_DEVICE=y
CONFIG_CGROUP_FREEZER=y
CONFIG_CGROUP_SCHED=y
CONFIG_CGROUP_PIDS=y
CONFIG_CPUSETS=y
CONFIG_MEMCG=y
CONFIG_BLK_CGROUP=y
CONFIG_BLK_DEV_THROTTLING=y
CONFIG_FAIR_GROUP_SCHED=y
CONFIG_CFS_BANDWIDTH=y
CONFIG_BPF=y
CONFIG_BPF_SYSCALL=y
CONFIG_BPF_JIT=y
CONFIG_CGROUP_BPF=y
CONFIG_KEYS=y
CONFIG_SECCOMP=y
CONFIG_SECCOMP_FILTER=y
CONFIG_POSIX_MQUEUE=y
CONFIG_VETH=y
CONFIG_BRIDGE=y
CONFIG_BRIDGE_NETFILTER=y
CONFIG_NETFILTER=y
CONFIG_NETFILTER_ADVANCED=y
CONFIG_NF_CONNTRACK=y
CONFIG_NF_CONNTRACK_EVENTS=y
CONFIG_NF_NAT=y
CONFIG_NF_NAT_MASQUERADE=y
CONFIG_NF_TABLES=y
CONFIG_NF_TABLES_INET=y
CONFIG_NFT_CT=y
CONFIG_NFT_NAT=y
CONFIG_NFT_MASQ=y
CONFIG_NFT_REDIR=y
CONFIG_NFT_REJECT=y
CONFIG_NFT_FIB_IPV4=y
CONFIG_NFT_FIB_IPV6=y
CONFIG_NFT_FIB_INET=y
CONFIG_NFT_COMPAT=y
CONFIG_NETFILTER_XTABLES=y
CONFIG_NETFILTER_XT_MARK=y
CONFIG_NETFILTER_XT_NAT=y
CONFIG_NETFILTER_XT_TARGET_MASQUERADE=y
CONFIG_NETFILTER_XT_TARGET_REDIRECT=y
CONFIG_NETFILTER_XT_MATCH_ADDRTYPE=y
CONFIG_NETFILTER_XT_MATCH_CONNTRACK=y
CONFIG_NETFILTER_XT_MATCH_COMMENT=y
CONFIG_NETFILTER_XT_MATCH_MULTIPORT=y
CONFIG_NETFILTER_XT_MATCH_IPVS=y
CONFIG_IP_VS=y
CONFIG_IP_VS_NFCT=y
CONFIG_IP_VS_PROTO_TCP=y
CONFIG_IP_VS_PROTO_UDP=y
CONFIG_IP_VS_RR=y
CONFIG_IP_NF_IPTABLES=y
CONFIG_IP_NF_FILTER=y
CONFIG_IP_NF_MANGLE=y
CONFIG_IP_NF_RAW=y
CONFIG_IP_NF_NAT=y
CONFIG_IP_NF_TARGET_MASQUERADE=y
CONFIG_IP6_NF_IPTABLES=y
CONFIG_IP6_NF_FILTER=y
CONFIG_IP6_NF_MANGLE=y
CONFIG_IP6_NF_RAW=y
CONFIG_IP6_NF_NAT=y
CONFIG_IP6_NF_TARGET_MASQUERADE=y
# CONFIG_MODULES is not set
CONFIG
    if grep -qE '^CONFIG_[[:alnum:]_]+=m$' "$config"
    then
        echo 'Unexpected kernel module' >&2
        return 1
    fi
    printf 'kernel config: %s assertions passed\n' "$count"
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]
then
    set -Eeuo pipefail
    kernel_config_test "${1:?Expected the effective kernel config path}"
    exit
fi

kernel_checksum_test() {
    local dir="$fixture/kernel-checksums" file
    mkdir -p "$dir"
    awk '/^RUN printf / {sub(/^RUN /, ""); copy=1}
        copy {print}
        copy && /sha256sum -c -/ {exit}' "$here/Dockerfile.kernel" \
        > "$dir/checksums"
    (
        cd "$dir"
        export LINUX_SHA256=ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad
        export FIRECRACKER_SHA256="$LINUX_SHA256"
        printf abc > linux.tar.xz
        printf abc > firecracker.config
        bash -Eeuo pipefail checksums
        for file in linux.tar.xz firecracker.config
        do
            printf changed >> "$file"
            if bash -Eeuo pipefail checksums > mismatch.log 2>&1
            then
                exit 1
            fi
            grep -Fq "$file: FAILED" mismatch.log
            printf abc > "$file"
        done
    )
}
regression 'kernel source checksums reject changed input' kernel_checksum_test

kernel_initrd_test() (
    export QEMUBOX_TEST_INITRD_LOG="$fixture/kernel-initrd.log"
    busybox() {
        echo 'Absolute BusyBox path required' >&2
        return 64
    }
    printf '%s\n' '#!/bin/sh' \
        'printf "/bin/busybox %s\n" "$*" >> "$QEMUBOX_TEST_INITRD_LOG"' \
        > "$fixture/kernel-busybox"
    chmod +x "$fixture/kernel-busybox"
    sed "s|^/bin/busybox |\"$fixture/kernel-busybox\" |" \
        "$here/initrd-init" > "$fixture/kernel-initrd"
    mkdir() { :; }
    mount() {
        printf '%s\n' "$*" >> "$QEMUBOX_TEST_INITRD_LOG"
        if [[ -n "${QEMUBOX_TEST_MOUNT_ERROR:-}" && \
            "$*" == '-t virtiofs -o ro root /lower' ]]
        then
            return 42
        fi
    }
    exec() { printf '%s\n' "$*" >> "$QEMUBOX_TEST_INITRD_LOG"; }
    export -f busybox mkdir mount exec
    bash "$fixture/kernel-initrd"
    cat > "$fixture/kernel-initrd.want" <<'MOUNTS'
/bin/busybox --install -s /bin
-t devtmpfs devtmpfs /dev
-t proc proc /proc
-t sysfs sysfs /sys
-t virtiofs -o ro root /lower
-t ext4 -o discard /dev/vda /upper
-t overlay overlay -o lowerdir=/lower,upperdir=/upper/data,workdir=/upper/work /root
--move /upper /root/.qemubox
--move /lower /root/.qemubox/lower
--move /dev /root/dev
--move /proc /root/proc
--move /sys /root/sys
switch_root /root /usr/bin/tini -- /usr/local/bin/qemubox-init
MOUNTS
    diff -u "$fixture/kernel-initrd.want" "$QEMUBOX_TEST_INITRD_LOG"
    : > "$QEMUBOX_TEST_INITRD_LOG"
    if QEMUBOX_TEST_MOUNT_ERROR=1 bash "$fixture/kernel-initrd"
    then
        exit 1
    else
        [[ "$?" = 42 ]]
    fi
    ! grep -qE 'ext4|switch_root' "$QEMUBOX_TEST_INITRD_LOG"
)
regression 'initrd retains backing mounts and stops on a root mount error' \
    kernel_initrd_test
