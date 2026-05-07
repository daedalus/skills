---
name: page-cache-lpe-mitigation
description: >
  Linux kernel local privilege escalation (LPE) incident response and runtime
  mitigation. Use whenever the user asks about CVE-2026-31431 ("Copy Fail"),
  "Dirty Frag" (xfrm-ESP + RxRPC page-cache write, no CVE yet), AF_ALG /
  algif_aead exploitation, xfrm ESP in-place decryption, rxkad/RxRPC pcbc
  write, bpf-lsm runtime kernel mitigations, eBPF-based socket
  visibility/enforcement, page-cache poisoning via in-place crypto, or the
  general pattern of no-reboot LPE containment on a large Linux fleet. Also
  trigger for: "how do I block AF_ALG without rebooting", "block esp4 esp6
  rxrpc modules", "bpf-lsm allowlist socket", "kernel module mitigation
  without rmmod", "fleet-wide eBPF socket tracing", "authencesn OOB write",
  "fcrypt brute-force userspace key", "skb_cow_data bypass", or any request
  to replicate Cloudflare's staged visibility-then-enforcement rollout
  methodology.  Covers the entire page-cache-poison LPE family: Dirty Pipe →
  Copy Fail → Dirty Frag.
source:
  - https://blog.cloudflare.com/copy-fail-linux-vulnerability-mitigation/
  - https://github.com/V4bel/dirtyfrag
  - https://www.openwall.com/lists/oss-security/2026/05/07/8
---

# Page-Cache LPE Mitigation Skill (Copy Fail + Dirty Frag)

Runtime containment of kernel LPE exploits in the page-cache-poison family,
using bpf-lsm allowlisting and eBPF fleet visibility.  Generalises to any
kernel module exploit where blunt `rmmod` would break production users.

---

## 1. Vulnerability Anatomy

### 1.1 CVE-2026-31431 — "Copy Fail"

| Field       | Detail |
|-------------|--------|
| Subsystem   | `algif_aead` (kernel crypto API userspace socket family) |
| Root cause  | 2017 in-place scatterlist optimisation: `authencesn` wrapper performs a 4-byte OOB write past the output region during `recvmsg()` decryption |
| Primitive   | Controlled 4-byte STORE into any file's page cache (file, offset, value all attacker-controlled via `assoclen`, splice params, AAD bytes 4-7) |
| Target      | `/usr/bin/su` (setuid-root, always cached) — `.text` patch → shellcode executes as root |
| Upstream fix| [commit a664bf3d603d](https://github.com/torvalds/linux/commit/a664bf3d603d) — reverts the 2017 in-place optimisation |
| Requires    | Unprivileged `AF_ALG` socket access (default on most distros) |
| Since       | kernel 4.14 (commit 72548b093ee3, January 2017) |

#### Exploit flow (condensed)

```
1. open("/usr/bin/su", O_RDONLY) + read()  → populate page cache
2. AF_ALG socket → bind authencesn(hmac(sha256),cbc(aes)) → accept()
3. for each 4-byte shellcode chunk:
     sendmsg(AAD[4:8] = chunk)
     splice(su_fd → pipe → alg_fd, assoclen+cryptlen = target .text offset)
     recvmsg()  # returns -EBADMSG but OOB write already committed
4. execve("/usr/bin/su")  → injected shellcode runs as root
```

---

### 1.2 "Dirty Frag" — No CVE (embargo broken 2026-05-07)

Two independent vulnerabilities chained to cover each other's distribution gaps.

#### Path A — xfrm-ESP Page-Cache Write

| Field       | Detail |
|-------------|--------|
| Subsystem   | `net/xfrm`, `net/ipv4/esp4.c` / `net/ipv6/esp6.c` — IPsec ESP input path |
| Root cause  | Non-linear skb carrying a splice-pinned page-cache reference bypasses mandatory `skb_cow_data()` CoW check in `esp_input()`; ESP decryption runs in-place, performing a 4-byte STORE directly into the pinned page |
| Primitive   | Same 4-byte page-cache STORE as Copy Fail; same sink, different source |
| Requires    | Privilege to create unprivileged user namespaces (Ubuntu default; sometimes blocked by AppArmor on hardened Ubuntu configs) |
| Since       | kernel commit cac2661c53f3, January 2017 |
| Module      | `esp4`, `esp6` |

#### Path B — RxRPC Page-Cache Write

| Field       | Detail |
|-------------|--------|
| Subsystem   | `net/rxrpc`, `net/rxrpc/rxkad.c` — `rxkad_verify_packet_1()` |
| Root cause  | Without namespace privileges, 8-byte in-place `pcbc(fcrypt)` decrypt runs onto a splice-pinned page-cache reference; decryption key brute-forced entirely in userspace before the kernel write is triggered |
| Primitive   | 8-byte page-cache STORE; deterministic — full key search before kernel touch |
| Requires    | No namespace privileges; `rxrpc.ko` must be loaded (ships and auto-loads on Ubuntu; absent on most other distros by default) |
| Since       | June 2023 |
| Module      | `rxrpc` |

#### Why two paths?

| Condition                              | esp4/esp6 works? | rxrpc works? |
|----------------------------------------|:---:|:---:|
| Ubuntu (unnamespaced, rxrpc auto-loads)| ✗ (AppArmor may block ns) | ✓ |
| Ubuntu (namespaces allowed)            | ✓ | ✓ |
| RHEL / Fedora / CentOS / AlmaLinux    | ✓ | ✗ (rxrpc not shipped) |
| openSUSE Tumbleweed                   | ✓ | ✗ |
| Copy Fail mitigated (algif_aead gone)  | ✓ | ✓ |

Running both in sequence → root on Ubuntu 24.04.4, RHEL 10.1, CentOS Stream 10,
AlmaLinux 10, Fedora 44, openSUSE Tumbleweed (kernels up to 7.0.x).

#### Key property

Pure logic bug, no race window, no kernel panic on failure, first-attempt
success rate very high.  Unlike race-condition LPEs, failed attempts do not
destabilise the host.

#### Detection signatures

```
# Path A — look for:
IPsec ESP socket creation by non-infrastructure process
  + recvmsg on AF_PACKET / raw socket
  + unusual splice() call sequence

# Path B — look for:
socket(AF_RXRPC, ...) by non-AFS/kerberos binary
  + rapid loop of sendmsg() → userspace timing (brute-force key phase)
  + recvmsg() returning -EBADMSG in tight loop
```

---

## 2. Mitigation Decision Tree

```
Which vulnerability are you containing?
├─ Copy Fail only (CVE-2026-31431)
│   └─ → §3.1 / §3.3 (algif_aead)
├─ Dirty Frag only
│   └─ → §3.2 (esp4/esp6/rxrpc)
└─ Both (recommended — same bug class, complementary coverage)
    └─ Apply all mitigations below

For each target module:
  Is the module loaded?
  ├─ No  →  add modprobe blacklist, done.
  └─ Yes
     └─ Do production services use this socket family?
        ├─ Unknown  →  deploy eBPF visibility first (§4), then decide
        ├─ No  →  rmmod path (§3.x blunt)
        └─ Yes  →  bpf-lsm allowlist path (§3.x surgical)
```

---

## 3. Mitigation Recipes

### 3.1 Copy Fail — blunt: disable algif_aead

```bash
echo "install algif_aead /bin/false" > /etc/modprobe.d/disable-algif.conf
rmmod algif_aead 2>/dev/null || true
```

Verify:

```python
import socket
s = socket.socket(socket.AF_ALG, socket.SOCK_SEQPACKET, 0)
s.bind(("aead", "authencesn(hmac(sha256),cbc(aes))"))
# Expected mitigated: FileNotFoundError or PermissionError
```

---

### 3.2 Dirty Frag — blunt: disable esp4/esp6/rxrpc

```bash
printf 'install esp4 /bin/false\ninstall esp6 /bin/false\ninstall rxrpc /bin/false\n' \
    > /etc/modprobe.d/dirtyfrag.conf
rmmod esp4 esp6 rxrpc 2>/dev/null || true
```

Impact assessment before running:

```bash
# Who uses IPsec ESP?
ss -pan | grep -E 'XFRM|esp'
ip xfrm state        # active SA count — non-zero means IPsec in use
ip xfrm policy

# Who uses RxRPC?
lsof -n 2>/dev/null | grep rxrpc
ss -pan --xdp | grep rxrpc
```

If IPsec SAs are active (`ip xfrm state` non-empty), prefer the bpf-lsm path
(§3.4) or schedule a maintenance window.  `rxrpc` removal is almost always safe
outside AFS/Kerberos infrastructure.

---

### 3.3 Copy Fail — surgical: bpf-lsm allowlist for algif_aead

```c
// SPDX-License-Identifier: GPL-2.0
// af_alg_restrict.bpf.c
#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <linux/socket.h>

static const char *allowlist[] = {
    "/usr/bin/openssl",
    "/usr/sbin/kTLS-helper",
    // add verified AF_ALG users discovered in §4
};

SEC("lsm/socket_bind")
int BPF_PROG(restrict_af_alg_bind, struct socket *sock,
             struct sockaddr *address, int addrlen)
{
    if (sock->sk->__sk_common.skc_family != AF_ALG)
        return 0;

    char path[256] = {};
    bpf_d_path(&sock->file->f_path, path, sizeof(path));

    for (int i = 0; i < sizeof(allowlist)/sizeof(allowlist[0]); i++) {
        if (__builtin_memcmp(path, allowlist[i],
                             __builtin_strlen(allowlist[i])) == 0)
            return 0;
    }
    return -EPERM;
}

char LICENSE[] SEC("license") = "GPL";
```

---

### 3.4 Dirty Frag — surgical: bpf-lsm allowlist for XFRM + RxRPC

Block `socket_create` for `PF_KEY`/XFRM policy sockets and `AF_RXRPC` for all
non-allowlisted callers.  Does not interrupt existing IPsec SAs already
established (kernel-internal state); only prevents new exploit socket setup.

```c
// SPDX-License-Identifier: GPL-2.0
// dirtyfrag_restrict.bpf.c
#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <linux/socket.h>

#define AF_RXRPC  35
#define PF_KEY    15   // used by racoon, strongswan, etc.

// Populate from §4 visibility data
static const char *xfrm_allowlist[] = {
    "/usr/sbin/strongswan",
    "/usr/sbin/racoon",
    "/usr/lib/ipsec/charon",
    // add your IPsec daemons
};

static const char *rxrpc_allowlist[] = {
    "/usr/sbin/afsd",   // AFS cache manager
    // add your AFS/Kerberos infrastructure
};

static int comm_in_list(const char **list, int n)
{
    char path[256] = {};
    // Note: bpf_d_path requires a non-null file reference
    return 0; // placeholder; real impl uses bpf_get_current_comm or
              // bpf_d_path depending on hook availability
}

SEC("lsm/socket_create")
int BPF_PROG(restrict_dirtyfrag, int family, int type, int protocol, int kern)
{
    if (kern)
        return 0;

    char comm[16] = {};
    bpf_get_current_comm(comm, sizeof(comm));

    if (family == AF_RXRPC) {
        // Block unless comm is in rxrpc_allowlist
        for (int i = 0; i < sizeof(rxrpc_allowlist)/sizeof(rxrpc_allowlist[0]); i++) {
            if (__builtin_memcmp(comm, rxrpc_allowlist[i],
                                 __builtin_strlen(rxrpc_allowlist[i])) == 0)
                return 0;
        }
        return -EPERM;
    }

    // PF_KEY (AF_KEY) gates new XFRM SA/policy injection from userspace
    if (family == PF_KEY) {
        for (int i = 0; i < sizeof(xfrm_allowlist)/sizeof(xfrm_allowlist[0]); i++) {
            if (__builtin_memcmp(comm, xfrm_allowlist[i],
                                 __builtin_strlen(xfrm_allowlist[i])) == 0)
                return 0;
        }
        return -EPERM;
    }

    return 0;
}

char LICENSE[] SEC("license") = "GPL";
```

Build and load:

```bash
clang -O2 -target bpf -c dirtyfrag_restrict.bpf.c -o dirtyfrag_restrict.bpf.o
bpftool prog load dirtyfrag_restrict.bpf.o /sys/fs/bpf/dirtyfrag_restrict \
    type lsm
```

Verify RxRPC blocked:

```python
import socket, errno
try:
    s = socket.socket(35, socket.SOCK_SEQPACKET, 0)  # AF_RXRPC = 35
    print("NOT blocked — check BPF program load")
except PermissionError:
    print("Blocked OK")
```

---

## 4. eBPF Visibility — Who Uses These Socket Families?

Deploy via `prometheus-ebpf-exporter` before enforcement to enumerate all
legitimate users without kernel changes or reboots.

```yaml
# ebpf_exporter config — track AF_ALG, AF_RXRPC, PF_KEY socket() callers
programs:
  - name: lpe_socket_usage
    metrics:
      counters:
        - name: lpe_socket_calls_total
          help: Socket calls by vulnerable family per binary
          labels:
            - name: comm
              size: 16
              decoders:
                - name: string
            - name: family
              size: 4
              decoders:
                - name: static_map
                  static_map:
                    "15":  PF_KEY
                    "35":  AF_RXRPC
                    "38":  AF_ALG
    kprobes:
      __sys_socket:
        - action: syscall_entry
          # filter: family in {15, 35, 38}
```

Aggregate across fleet within hours.  Confirm allowlists are complete before
enabling enforcement gates.

---

## 5. Staged Rollout Protocol (Cloudflare Pattern)

**Visibility gate before enforcement gate** — applies identically to Dirty Frag.

```
Phase 1 — Visibility (no enforcement)
  └─ deploy ebpf_exporter config (§4) fleet-wide
  └─ aggregate metric for AF_ALG, AF_RXRPC, PF_KEY callers (hours, not days)
  └─ populate allowlists in §3.3 and §3.4

Phase 2 — Enforcement (separate gate)
  └─ deploy bpf-lsm programs (§3.3 + §3.4) or blunt rmmod (§3.1 + §3.2)
  └─ end-to-end canary verification:
       exploit attempt → EPERM ✓
       legit IPsec daemon → still establishes SAs ✓
       legit AFS service  → still functions ✓

Phase 3 — Kernel patch (reboot automation, normal pace)
  └─ await backport from upstream (no timeline — embargo broken, no patch yet)
  └─ internal CI builds patched kernel once available
  └─ staging validation
  └─ ERR pipeline: rolling reboot across fleet
```

The bpf-lsm covers the window between disclosure and patched kernel deployment
without requiring emergency reboots.  For Dirty Frag this window is indefinite
until distros ship patches.

---

## 6. Threat Hunting Checklist

For both Copy Fail and Dirty Frag (and the whole bug class), hunt **before**
assuming no impact.  The page-cache write leaves no direct kernel log — hunt
userspace side-effects.

```
□ Search centralized logs for exploit signatures (48h lookback minimum):
    - AF_ALG + authencesn bind + recvmsg(-EBADMSG) sequence
    - AF_RXRPC socket creation by non-AFS binary
    - Rapid splice() loops into crypto sockets by unprivileged process

□ Verify setuid binary integrity vs package manifest:
    find / -perm -4000 -exec sha256sum {} \; 2>/dev/null | \
        comm -23 <(sort) <(sort known-good.txt)
    # Page-cache poison does NOT modify on-disk bytes — hash mismatch means
    # the exploit ran AND the page was evicted+reloaded, which is rare;
    # no mismatch does NOT rule out exploitation.

□ Check for new cron entries, systemd units, authorized_keys modifications
□ Audit unusual outbound connections (unexpected IPs, ports, timing)
□ Look for new users/groups in /etc/passwd, /etc/shadow
□ Verify /proc/*/maps for injected shared libraries in long-lived processes
□ Pull access logs for affected systems → reconstruct sessions
```

**Note on hash verification**: Dirty Frag (and Copy Fail) corrupt only the
in-memory page cache, not the on-disk inode.  A `sha256sum` against the
filesystem will match even on a compromised host if the page was not yet evicted.
`sha256sum` is a weak signal for this bug class.  Prefer runtime behavioral
detection.

Principle: **assume compromise until forensically disproven**.

---

## 7. Behavioral Detection Notes

Do **not** rely on CVE-specific signatures.  This entire bug class fires on
behavioral patterns before CVE assignment:

- Anomalous process execution chains involving crypto socket families + setuid binary
- Short-lived unprivileged processes opening `AF_RXRPC` / `PF_KEY` / `AF_ALG`
- `recvmsg()` returning `EBADMSG` / `EINVAL` in tight loops from non-daemon processes
- Fleet-wide baseline deviation (not host-by-host thresholds)

Behavioral EDR with fleet-baseline telemetry provides coverage before PoC
publication.  CVE-specific rules are a fallback, not the primary layer.

---

## 8. Kernel Configuration Hardening (follow-up)

```bash
# Check which crypto / network modules are loaded
lsmod | grep -E 'alg|esp|rxrpc|xfrm'

# Blacklist all three families proactively if not needed
cat >> /etc/modprobe.d/hardening.conf <<'EOF'
# Copy Fail
install algif_aead /bin/false
install algif_skcipher /bin/false
install algif_hash /bin/false
install algif_rng /bin/false

# Dirty Frag
install esp4 /bin/false
install esp6 /bin/false
install rxrpc /bin/false
EOF

# Identify other unused modules in current config
diff <(lsmod | awk '{print $1}' | sort) \
     <(grep '=y\|=m' /boot/config-$(uname -r) | \
       sed 's/CONFIG_//;s/=.*//' | tr '[:upper:]' '[:lower:]' | sort)
```

Target: remove unused modules from the kernel build entirely, not just runtime
blacklisting.  `CONFIG_AF_ALG`, `CONFIG_INET_ESP`, `CONFIG_RXRPC` are all
optional.

---

## 9. References

**Copy Fail (CVE-2026-31431)**
- Cloudflare mitigation blog: https://blog.cloudflare.com/copy-fail-linux-vulnerability-mitigation/
- Original researcher disclosure: https://xint.io/blog/copy-fail-linux-distributions
- Copy Fail site + one-liner verifier: https://copy.fail/
- Upstream fix: https://github.com/torvalds/linux/commit/a664bf3d603d
- Cloudflare bpf-lsm prior art: https://blog.cloudflare.com/live-patch-security-vulnerabilities-with-ebpf-lsm/

**Dirty Frag (no CVE)**
- Researcher repo: https://github.com/V4bel/dirtyfrag
- oss-security disclosure: https://www.openwall.com/lists/oss-security/2026/05/07/8
- LWN coverage: https://lwn.net/Articles/1071719/

**Tooling**
- ebpf_exporter: https://github.com/cloudflare/ebpf_exporter
