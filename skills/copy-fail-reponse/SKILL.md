---
name: copy-fail-lpe-mitigation
description: >
  Linux kernel local privilege escalation (LPE) incident response and runtime
  mitigation. Use whenever the user asks about CVE-2026-31431 ("Copy Fail"),
  AF_ALG / algif_aead exploitation, bpf-lsm runtime kernel mitigations,
  eBPF-based socket visibility/enforcement, page-cache poisoning via in-place
  crypto, or the general pattern of no-reboot LPE containment on a large Linux
  fleet. Also trigger for: "how do I block AF_ALG without rebooting", "bpf-lsm
  allowlist socket", "kernel module mitigation without rmmod", "fleet-wide
  eBPF socket tracing", "authencesn OOB write", or any request to replicate
  Cloudflare's staged visibility-then-enforcement rollout methodology.
source: https://blog.cloudflare.com/copy-fail-linux-vulnerability-mitigation/
---

# Copy Fail — Linux LPE Mitigation Skill

Runtime containment of kernel LPE exploits targeting the `AF_ALG` subsystem,
using bpf-lsm allowlisting and eBPF fleet visibility.  Generalises to any
kernel module exploit where blunt `rmmod` would break production users.

---

## 1. Vulnerability Anatomy

**CVE-2026-31431** — "Copy Fail"

| Field       | Detail |
|-------------|--------|
| Subsystem   | `algif_aead` (kernel crypto API userspace socket family) |
| Root cause  | 2017 in-place scatterlist optimisation: `authencesn` wrapper performs a 4-byte OOB write past the output region during `recvmsg()` decryption |
| Primitive   | Controlled 4-byte write into any file's page cache (file, offset, value all attacker-controlled via `assoclen`, splice params, AAD bytes 4-7) |
| Target      | `/usr/bin/su` (setuid-root, always cached) — `.text` patch → shellcode executes as root |
| Upstream fix| [commit a664bf3d603d](https://github.com/torvalds/linux/commit/a664bf3d603d) — reverts the 2017 in-place optimisation |
| Requires    | Unprivileged `AF_ALG` socket access (default on most distros) |

### Exploit flow (condensed)

```
1. open("/usr/bin/su", O_RDONLY) + read()  → populate page cache
2. AF_ALG socket → bind authencesn(hmac(sha256),cbc(aes)) → accept()
3. for each 4-byte shellcode chunk:
     sendmsg(AAD[4:8] = chunk)
     splice(su_fd → pipe → alg_fd, assoclen+cryptlen = target .text offset)
     recvmsg()  # returns -EBADMSG but OOB write already committed
4. execve("/usr/bin/su")  → injected shellcode runs as root
```

### Detection signature

Kernel logs emit a distinctive trace when the exploit runs.
Hunt pattern (centralized syslog / auditd / eBPF):

```
AF_ALG bind(authencesn(hmac(sha256),cbc(aes))) by non-allowlisted binary
followed by recvmsg returning -EBADMSG
```

---

## 2. Mitigation Decision Tree

```
Is algif_aead loaded?
├─ No  →  add modprobe blacklist (see §3.1), done.
└─ Yes
   └─ Do any production services use AF_ALG?
      ├─ Unknown  →  deploy eBPF visibility first (§3.2), then decide
      ├─ No known users  →  rmmod path (§3.1)
      └─ Yes (known users exist)  →  bpf-lsm allowlist path (§3.3)
```

**Cloudflare chose bpf-lsm** because one internal service legitimately used
`AF_ALG`; blunt `rmmod` would have broken it.

---

## 3. Mitigation Recipes

### 3.1 Blunt: disable the module (no legit users)

```bash
# Prevent future loads
echo "install algif_aead /bin/false" > /etc/modprobe.d/disable-algif.conf

# Unload if currently loaded (safe only if nothing is using it)
rmmod algif_aead 2>/dev/null || true
```

Verify:

```python
python3 -c '
import socket
s = socket.socket(socket.AF_ALG, socket.SOCK_SEQPACKET, 0)
s.bind(("aead","authencesn(hmac(sha256),cbc(aes))"))
'
# Expected on mitigated host: FileNotFoundError or PermissionError
```

### 3.2 eBPF visibility: who is using AF_ALG?

Deploy via `prometheus-ebpf-exporter` **before** enforcement to enumerate all
legitimate `AF_ALG` users across the fleet without kernel changes or reboots.

```yaml
# ebpf_exporter config snippet — track AF_ALG socket() callers by binary path
programs:
  - name: af_alg_usage
    metrics:
      counters:
        - name: af_alg_socket_calls_total
          help: AF_ALG socket() calls per binary
          labels:
            - name: comm
              size: 16
              decoders:
                - name: string
    kprobes:
      __sys_socket:
        - action: syscall_entry
          # filter: domain == AF_ALG (38)
```

Aggregate across fleet within hours.  Confirm exactly which binaries appear.
Gate enforcement on this confirmation.

### 3.3 Surgical: bpf-lsm allowlist (legit users exist)

Block `socket_bind` for all callers **not** on the allowlist.  No module
removal, no service disruption.

```c
// SPDX-License-Identifier: GPL-2.0
#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <linux/socket.h>

// Populate with absolute paths of known-legit AF_ALG users
static const char *allowlist[] = {
    "/usr/bin/openssl",
    "/usr/sbin/kTLS-helper",
    // add your binaries here
};

SEC("lsm/socket_bind")
int BPF_PROG(restrict_af_alg_bind, struct socket *sock,
             struct sockaddr *address, int addrlen)
{
    // Only intercept AF_ALG
    if (sock->sk->__sk_common.skc_family != AF_ALG)
        return 0;

    char comm[256] = {};
    bpf_d_path(&sock->file->f_path, comm, sizeof(comm));

    for (int i = 0; i < sizeof(allowlist)/sizeof(allowlist[0]); i++) {
        if (__builtin_memcmp(comm, allowlist[i],
                             __builtin_strlen(allowlist[i])) == 0)
            return 0; // allow
    }

    return -EPERM; // deny
}

char LICENSE[] SEC("license") = "GPL";
```

Build and load:

```bash
clang -O2 -target bpf -c af_alg_restrict.bpf.c -o af_alg_restrict.bpf.o
bpftool prog load af_alg_restrict.bpf.o /sys/fs/bpf/af_alg_restrict \
    type lsm
```

Verify on any host:

```python
python3 -c '
import socket
s = socket.socket(socket.AF_ALG, socket.SOCK_SEQPACKET, 0)
s.bind(("aead","authencesn(hmac(sha256),cbc(aes))"))
'
# Expected: PermissionError: [Errno 1] Operation not permitted
```

---

## 4. Staged Rollout Protocol (Cloudflare Pattern)

This is the key operational insight: **visibility gate before enforcement gate**.

```
Phase 1 — Visibility (salt/puppet gated, no enforcement)
  └─ deploy ebpf_exporter AF_ALG config fleet-wide
  └─ wait for metric aggregation (hours, not days)
  └─ confirm allow-list is complete

Phase 2 — Enforcement (separate gate)
  └─ deploy bpf-lsm program
  └─ end-to-end verify on a canary node:
       exploit attempt → PermissionError ✓
       legit service   → still works     ✓

Phase 3 — Kernel patch (reboot automation, normal pace)
  └─ backport merged into LTS line
  └─ internal CI builds patched kernel
  └─ staging validation
  └─ ERR pipeline: rolling reboot across fleet (~4 week cycle)
  └─ machines that already rebooted → manual reboot to pick up patch
```

The bpf-lsm covers the window between disclosure and patched kernel deployment
without requiring emergency reboots.

---

## 5. Threat Hunting Checklist

For critical LPE CVEs, hunt **before** assuming no impact:

```
□ Search centralized logs for exploit kernel signature (48h lookback)
□ Pull access logs for affected systems → reconstruct sessions
□ Verify setuid binary integrity: sha256sum vs package manifest
    find / -perm -4000 -exec sha256sum {} \; | diff - known-good.txt
□ Check for new cron entries, systemd units, authorized_keys modifications
□ Audit unusual outbound connections (unexpected IPs, ports)
□ Look for new users/groups in /etc/passwd, /etc/shadow
□ Verify /proc/*/maps for injected shared libraries in long-lived processes
```

Principle: **assume compromise until forensically disproven**.

---

## 6. Behavioral Detection Notes

Do **not** rely on CVE-specific signatures.  Cloudflare's detection fired
within minutes on behavioral patterns alone:

- Anomalous process execution chains involving AF_ALG + setuid binary
- Fleet-wide baseline deviation (not host-by-host thresholds)
- No signature update, no rule change, no human intervention required

Implication: behavioral EDR with fleet-baseline telemetry provides coverage
before PoC publication.  CVE-specific rules are a fallback, not the primary
layer.

---

## 7. Kernel Configuration Hardening (follow-up)

Post-incident audit items:

```bash
# Check which crypto modules are loaded
lsmod | grep alg

# Identify unused kernel modules in current config
diff <(lsmod | awk '{print $1}' | sort) \
     <(grep '=y\|=m' /boot/config-$(uname -r) | \
       sed 's/CONFIG_//;s/=.*//' | tr '[:upper:]' '[:lower:]' | sort)

# Blacklist unused AF_ALG families proactively
cat >> /etc/modprobe.d/hardening.conf <<'EOF'
# Disable AF_ALG if not needed
install algif_aead /bin/false
install algif_skcipher /bin/false
install algif_hash /bin/false
install algif_rng /bin/false
EOF
```

Target: reduce kernel attack surface by auditing and removing unused modules
from the build entirely (not just runtime blacklisting).

---

## 8. References

- Cloudflare blog: https://blog.cloudflare.com/copy-fail-linux-vulnerability-mitigation/
- Original researcher disclosure: https://xint.io/blog/copy-fail-linux-distributions
- Copy Fail site + one-liner verifier: https://copy.fail/
- Upstream fix: https://github.com/torvalds/linux/commit/a664bf3d603d
- Cloudflare bpf-lsm prior art: https://blog.cloudflare.com/live-patch-security-vulnerabilities-with-ebpf-lsm/
- ebpf_exporter: https://github.com/cloudflare/ebpf_exporter
