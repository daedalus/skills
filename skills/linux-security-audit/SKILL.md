---
name: linux-security-audit
description: >
  Comprehensive Linux security auditing and hardening skill. Use this whenever
  the user wants to audit a Linux system, assess its security posture, harden a
  server or workstation, review running services/users/permissions, check for
  privilege escalation vectors, generate a security report, or understand
  specific security controls (PAM, sudoers, AppArmor, SELinux, SSH, sysctl,
  firewall, cron, SUID/SGID, world-writable paths, failed logins, kernel
  parameters, etc.). Trigger for phrases like: "audit my server", "harden this
  box", "security check", "is this system secure", "check for misconfigs",
  "review sudoers", "find SUID binaries", "check open ports", "who can SSH in",
  "CIS benchmark", "DISA STIG", "NIST 800-123", "check /etc/passwd", "review
  crontabs", "enumerate users", "find world-writable files", or any request to
  assess, report on, or remediate Linux system security. Also trigger when the
  user pastes command output (ps aux, ss -tlnp, ls -la /etc, etc.) and asks
  "is this OK?" or "what should I fix?".
---

# Linux Security Audit

A structured, adversarial-first approach to Linux security assessment and hardening.
Philosophy: assume breach posture. Every default is suspect. Prove safety, don't assume it.

---

## Audit Phases

Run phases in order for a full audit. For targeted questions, jump to the relevant section.

```
Phase 0 — Context gathering
Phase 1 — Identity & access control
Phase 2 — Network exposure
Phase 3 — File system & permissions
Phase 4 — Process & service posture
Phase 5 — Kernel & OS hardening
Phase 6 — Logging & monitoring
Phase 7 — Package & update hygiene
Phase 8 — Cryptographic posture
Phase 9 — Reporting & remediation
```

---

## Phase 0 — Context Gathering

Before auditing, establish scope:

```bash
# Distribution + kernel
uname -a
cat /etc/os-release
lsb_release -a 2>/dev/null

# Uptime + last boot (patching cadence signal)
uptime
who -b

# Virtualization (affects threat model)
systemd-detect-virt 2>/dev/null || virt-what 2>/dev/null

# What role does this system play?
hostname
cat /etc/hostname
```

**Threat model questions to ask the user:**
- Internet-facing or internal-only?
- Single-user workstation, multi-user server, or container host?
- Compliance target? (CIS, STIG, PCI-DSS, SOC 2, HIPAA)
- Known sensitive data? (keys, PII, source code, credentials)

---

## Phase 1 — Identity & Access Control

### Users and Groups

```bash
# All local accounts — look for unexpected UID 0 accounts
awk -F: '$3 == 0 {print "ROOT-UID:", $0}' /etc/passwd
awk -F: '$3 < 1000 && $7 !~ /nologin|false/ {print "SYSTEM+SHELL:", $0}' /etc/passwd

# Accounts with login shells (interactive accounts)
grep -v '/nologin\|/false\|/sync' /etc/passwd | cut -d: -f1,3,7

# Groups with elevated privilege
getent group sudo wheel adm staff docker lxd

# Password aging policy
chage -l <username>        # per-user
cat /etc/login.defs        # global defaults (PASS_MAX_DAYS, PASS_MIN_LEN, etc.)

# Shadow file — look for empty passwords or ! (locked) vs * (disabled)
sudo awk -F: '$2 == "" {print "NO PASSWORD:", $1}' /etc/shadow
sudo awk -F: '$2 !~ /^[\$!*]/ {print "CLEARTEXT?:", $1, $2}' /etc/shadow
```

**Red flags:**
- Multiple UID 0 accounts
- System accounts with real shells (`/bin/bash` instead of `/usr/sbin/nologin`)
- Accounts in `docker` group (equivalent to root on most systems)
- `lxd` group membership (trivial container escape to root)
- Empty passwords in shadow

### Sudo Configuration

```bash
sudo cat /etc/sudoers
sudo ls /etc/sudoers.d/
sudo visudo -c          # syntax check

# Find NOPASSWD grants (can execute as root without auth)
sudo grep -r NOPASSWD /etc/sudoers /etc/sudoers.d/ 2>/dev/null

# Find wildcard abuse — dangerous patterns:
# user ALL=(ALL) /usr/bin/vi         <- shell escape
# user ALL=(ALL) /usr/bin/find       <- -exec /bin/sh
# user ALL=(ALL) /usr/bin/python*    <- trivial bypass
# user ALL=(ALL) /bin/cp             <- overwrite /etc/passwd
```

**Audit checklist:**
- [ ] No `ALL=(ALL) ALL` for non-admin users
- [ ] No `NOPASSWD` for sensitive binaries (interpreters, editors, cp, tar, find)
- [ ] `requiretty` enabled (prevents remote sudo via non-interactive shells)
- [ ] `env_reset` is set (prevents $PATH poisoning)
- [ ] Logs go to syslog: `Defaults logfile=/var/log/sudo.log` or via `syslog`

### SSH Access

```bash
sshd -T 2>/dev/null | grep -iE 'permit|auth|root|password|pubkey|port|allow|deny|max'
cat /etc/ssh/sshd_config
ls /etc/ssh/sshd_config.d/ 2>/dev/null

# Who has authorized_keys?
find /home /root -name authorized_keys 2>/dev/null -exec echo "=== {} ===" \; -exec cat {} \;

# Host keys — algorithm strength
ls -la /etc/ssh/ssh_host_*
ssh-keygen -l -f /etc/ssh/ssh_host_rsa_key.pub 2>/dev/null
```

**Required SSH hardening:**

```
# /etc/ssh/sshd_config minimums
PermitRootLogin no                  # or prohibit-password at minimum
PasswordAuthentication no           # keys only
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
X11Forwarding no
AllowAgentForwarding no
AllowTcpForwarding no               # unless needed
MaxAuthTries 3
LoginGraceTime 30
ClientAliveInterval 300
ClientAliveCountMax 2
Protocol 2                          # implicit in modern OpenSSH but worth verifying
KexAlgorithms curve25519-sha256,diffie-hellman-group16-sha512
Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.com
MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com
HostKeyAlgorithms ssh-ed25519,rsa-sha2-512,rsa-sha2-256
```

### PAM

```bash
ls /etc/pam.d/
cat /etc/pam.d/common-auth 2>/dev/null || cat /etc/pam.d/system-auth 2>/dev/null
cat /etc/security/pwquality.conf 2>/dev/null
cat /etc/security/faillock.conf 2>/dev/null

# Account lockout after failed attempts?
grep -r faillock /etc/pam.d/ 2>/dev/null
grep -r pam_tally /etc/pam.d/ 2>/dev/null
```

---

## Phase 2 — Network Exposure

### Listening Services

```bash
# All listening sockets with process info
ss -tlnp    # TCP
ss -ulnp    # UDP
ss -xlnp    # Unix sockets

# Older systems
netstat -tlnp 2>/dev/null

# Who's listening on 0.0.0.0 (all interfaces) vs 127.0.0.1 (loopback only)?
ss -tlnp | awk '/0.0.0.0/ {print "EXPOSED:", $0}'
```

**Audit each exposed service:**
- Is it expected? If no, disable immediately.
- Is it authenticated?
- Does it need to listen on all interfaces, or can it bind to 127.0.0.1?
- Is it TLS-encrypted for sensitive data?

### Firewall

```bash
# iptables/nftables
sudo iptables -L -n -v
sudo iptables -t nat -L -n -v
sudo nft list ruleset 2>/dev/null

# UFW (Ubuntu/Debian)
sudo ufw status verbose

# firewalld (RHEL/CentOS/Fedora)
sudo firewall-cmd --list-all
sudo firewall-cmd --list-services

# What's the default policy?
sudo iptables -L | grep -i policy
```

**Minimum firewall posture:**
- Default INPUT: DROP
- Default FORWARD: DROP
- Default OUTPUT: ACCEPT (or restrict if high-security)
- Explicitly allow: SSH (rate-limited), required services only
- Log dropped packets: `iptables -A INPUT -j LOG --log-prefix "DROP: "`

### Network Parameters (sysctl)

```bash
sysctl -a 2>/dev/null | grep -E 'ip_forward|rp_filter|accept_redirects|send_redirects|log_martians|tcp_syncookies|icmp|bootp'
```

**Hardened values:**

```
net.ipv4.ip_forward = 0               # unless router/VPN
net.ipv4.conf.all.rp_filter = 1       # anti-spoofing
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.conf.all.log_martians = 1
net.ipv4.tcp_syncookies = 1           # SYN flood protection
net.ipv6.conf.all.accept_redirects = 0
net.ipv6.conf.all.accept_source_route = 0
```

---

## Phase 3 — File System & Permissions

### SUID/SGID Binaries

```bash
# Find all SUID binaries (can run as owner, typically root)
find / -perm -4000 -type f 2>/dev/null | sort

# Find all SGID binaries
find / -perm -2000 -type f 2>/dev/null | sort

# Compare against known-good baseline
# Expected SUID: passwd, su, sudo, ping, newgrp, gpasswd, chfn, chsh, mount, umount
# Unexpected: interpreters (python, perl, ruby), editors (vim, nano), nc, nmap, bash, sh
```

**Removing unnecessary SUID:**
```bash
chmod u-s /usr/bin/suspicious_binary
```

### World-Writable Files and Directories

```bash
# World-writable files (not symlinks)
find / -xdev -type f -perm -0002 -not -path '/proc/*' -not -path '/sys/*' 2>/dev/null

# World-writable directories (common, but sticky bit required)
find / -xdev -type d -perm -0002 -not -sticky -not -path '/proc/*' 2>/dev/null

# Unowned files (orphaned after user deletion)
find / -xdev \( -nouser -o -nogroup \) 2>/dev/null
```

### Critical File Permissions

```bash
# Must be owned root, not world-readable
ls -la /etc/shadow /etc/gshadow /etc/sudoers
# Expected: -rw-r----- root shadow (640) or -rw------- root root (600)

ls -la /etc/passwd /etc/group
# Expected: -rw-r--r-- (644) — world-readable is correct, no write access

# SSH config and keys
ls -la /etc/ssh/sshd_config /etc/ssh/ssh_host_*
# Private keys: -rw------- root root (600)

# cron directories
ls -la /etc/cron* /var/spool/cron/ 2>/dev/null
```

### Cron Jobs — Backdoor Vector

```bash
# System cron
crontab -l                    # root's crontab
cat /etc/crontab
ls -la /etc/cron.d/ /etc/cron.daily/ /etc/cron.weekly/ /etc/cron.monthly/

# All user crontabs
for user in $(cut -d: -f1 /etc/passwd); do
  echo "=== $user ==="
  crontab -u "$user" -l 2>/dev/null
done

# At jobs
atq 2>/dev/null

# Systemd timers (modern cron replacement)
systemctl list-timers --all
```

**Red flags:**
- Cron running scripts from world-writable directories
- Cron running scripts not owned by root
- Scripts doing `curl | bash` or downloading from external URLs
- Unexpected user crontabs

---

## Phase 4 — Process & Service Posture

### Running Services

```bash
# All enabled/active services
systemctl list-units --type=service --state=active
systemctl list-unit-files --type=service --state=enabled

# Services running as root (expected vs unexpected)
ps aux | awk '$1 == "root" {print}' | grep -v '\[.*\]'   # exclude kernel threads

# Services with network sockets — who owns them?
ss -tlnp | grep -v '127.0.0.1\|::1'                      # exposed to network
```

**Common unnecessary services to disable:**
- `telnet`, `rsh`, `rlogin`, `rexec` — plaintext remote access
- `finger`, `rpcbind` (unless NFS required)
- `avahi-daemon` (mDNS — rarely needed on servers)
- `cups` (printing — server has no printers)
- `bluetooth` (server contexts)
- `nfs-server`, `smbd` unless explicitly needed

### Container/Namespace Security

```bash
# Docker socket — root equivalent
ls -la /var/run/docker.sock 2>/dev/null
docker ps 2>/dev/null

# Is AppArmor active?
sudo aa-status 2>/dev/null
apparmor_status 2>/dev/null

# Is SELinux enforcing?
getenforce 2>/dev/null
sestatus 2>/dev/null
```

---

## Phase 5 — Kernel & OS Hardening

### Kernel Parameters

```bash
sysctl -a 2>/dev/null | grep -E 'kernel\.(randomize|dmesg|perf|suid|core|kptr|yama)'
```

**Hardened sysctl values:**

```
# /etc/sysctl.d/99-hardening.conf

# ASLR
kernel.randomize_va_space = 2

# Restrict dmesg to root
kernel.dmesg_restrict = 1

# Restrict /proc/kallsyms
kernel.kptr_restrict = 2

# Disable ptrace for non-root (breaks some debuggers but hardens against LPE)
kernel.yama.ptrace_scope = 1         # or 2 for stricter

# Disable core dumps for SUID programs
fs.suid_dumpable = 0

# Hide kernel pointers in /proc
kernel.perf_event_paranoid = 3

# Prevent unprivileged BPF
kernel.unprivileged_bpf_disabled = 1

# Protect symlinks in world-writable dirs
fs.protected_symlinks = 1
fs.protected_hardlinks = 1
```

### Kernel Modules

```bash
# Loaded modules
lsmod

# Uncommon/legacy modules that should be blacklisted on servers:
# cramfs, freevxfs, jffs2, hfs, hfsplus, squashfs, udf (filesystem rarely needed)
# dccp, sctp, rds, tipc (network protocols rarely needed)
cat /etc/modprobe.d/*.conf 2>/dev/null | grep blacklist

# USB storage — disable on servers
grep usb-storage /etc/modprobe.d/*.conf 2>/dev/null
```

**Blacklist template for servers:**
```
# /etc/modprobe.d/blacklist-rare.conf
blacklist dccp
blacklist sctp
blacklist rds
blacklist tipc
blacklist usb-storage
install usb-storage /bin/false
```

---

## Phase 6 — Logging & Monitoring

### Log Infrastructure

```bash
# Systemd journal
journalctl --disk-usage
journalctl -p err..emerg -n 50   # recent errors

# syslog
ls -la /var/log/
cat /etc/rsyslog.conf 2>/dev/null
cat /etc/syslog-ng/syslog-ng.conf 2>/dev/null

# Auditd
systemctl status auditd
auditctl -l 2>/dev/null        # active audit rules
ausearch -m avc 2>/dev/null | head -20   # SELinux denials

# Auth log — failed logins, sudo usage
grep -iE 'failed|invalid|refused|authentication failure' /var/log/auth.log 2>/dev/null | tail -30
grep -iE 'failed|invalid|refused|authentication failure' /var/log/secure 2>/dev/null | tail -30

# Last logins
last -n 20
lastb -n 20 2>/dev/null   # failed login attempts (requires root)
```

### Audit Rules (auditd)

Minimum audit rules for compliance:

```
# /etc/audit/rules.d/audit.rules

# Identity changes
-w /etc/passwd -p wa -k identity
-w /etc/shadow -p wa -k identity
-w /etc/group -p wa -k identity
-w /etc/sudoers -p wa -k sudoers
-w /etc/sudoers.d/ -p wa -k sudoers

# Privilege escalation
-a always,exit -F arch=b64 -S setuid -S setgid -F key=privilege_abuse
-w /bin/su -p x -k priv_esc
-w /usr/bin/sudo -p x -k priv_esc

# Network config changes
-w /etc/hosts -p wa -k network
-w /etc/network/ -p wa -k network

# SSH
-w /etc/ssh/sshd_config -p wa -k sshd

# Cron
-w /etc/crontab -p wa -k cron
-w /etc/cron.d/ -p wa -k cron
-w /var/spool/cron/ -p wa -k cron

# Module loading (LKM rootkits)
-w /sbin/insmod -p x -k modules
-w /sbin/rmmod -p x -k modules
-w /sbin/modprobe -p x -k modules
-a always,exit -F arch=b64 -S init_module -S delete_module -k modules
```

---

## Phase 7 — Package & Update Hygiene

```bash
# Debian/Ubuntu
apt list --upgradable 2>/dev/null
apt-get -s dist-upgrade 2>/dev/null | grep -i security
unattended-upgrades --dry-run 2>/dev/null

# RHEL/CentOS/Fedora
yum check-update 2>/dev/null
dnf updateinfo list security 2>/dev/null
yum-plugin-security 2>/dev/null

# Last package update
stat /var/cache/apt/pkgcache.bin 2>/dev/null    # Debian
rpm -qa --last 2>/dev/null | head -10            # RHEL

# Packages not from official repos (GPG unsigned or foreign repos)
apt-key list 2>/dev/null
dpkg --get-selections | wc -l

# Check for packages installed from .deb/.rpm files (bypassed repo GPG check)
apt list 2>/dev/null | grep 'installed,local'
```

---

## Phase 8 — Cryptographic Posture

```bash
# TLS certificates — expiry
for cert in /etc/ssl/certs/*.pem; do
  echo "$cert: $(openssl x509 -noout -enddate -in "$cert" 2>/dev/null)"
done

# Check weak keys (RSA < 2048, DSA keys)
for keyfile in /etc/ssl/private/*.key; do
  echo "$keyfile: $(openssl rsa -noout -text -in "$keyfile" 2>/dev/null | grep 'Key:')";
done

# SSH host key strength
for pub in /etc/ssh/ssh_host_*.pub; do
  ssh-keygen -l -f "$pub" 2>/dev/null
done

# GPG keys on system
gpg --list-keys 2>/dev/null
gpg --list-secret-keys 2>/dev/null

# /dev/random vs /dev/urandom (entropy)
cat /proc/sys/kernel/random/entropy_avail
```

**Weak algorithms to flag:**
- RSA keys < 2048 bits
- DSA keys (broken for k < 256 bits, deprecated)
- MD5 or SHA-1 certificate signatures
- SSLv3, TLSv1.0, TLSv1.1 in any service config
- DH groups < 2048 bits (Logjam)

---

## Phase 9 — Reporting & Remediation

### Severity Classification

| Level    | Criteria                                         | Example                               |
|----------|--------------------------------------------------|---------------------------------------|
| CRITICAL | Direct path to root without auth                 | UID 0 duplicate, NOPASSWD sudo ALL    |
| HIGH     | Privilege escalation with minimal effort         | World-writable cron script, lxd group |
| MEDIUM   | Exposure increases attack surface                | Unnecessary service, PasswordAuth SSH |
| LOW      | Defense-in-depth gap                             | Missing audit rule, sysctl not set    |
| INFO     | Non-security hygiene                             | Old packages, verbose login banners   |

### Report Template

```markdown
# Linux Security Audit — [hostname] — [date]

**Auditor:** [name]
**Scope:** [what was tested]
**Compliance Target:** [CIS Level 1/2, STIG, etc.]

## Executive Summary
[2-3 sentences: overall posture, critical count, recommendation]

## Critical Findings
### CRIT-001: [title]
- **Description:** [what it is]
- **Evidence:** [command + output]
- **Impact:** [what an attacker can do]
- **Fix:** [specific remediation command or config]

## High Findings
...

## Remediation Checklist
- [ ] CRIT-001: Revoke unauthorized UID 0 account
- [ ] HIGH-001: Remove user X from docker group
...

## Positive Controls Observed
[What's already done right — builds credibility]
```

### Quick-Win Hardening Script Template

```bash
#!/bin/bash
# Hardening quick wins — review before running, this is not idempotent magic

set -euo pipefail

# 1. SSH hardening
sed -i 's/^#*PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/^#*X11Forwarding.*/X11Forwarding no/' /etc/ssh/sshd_config
systemctl reload ssh 2>/dev/null || systemctl reload sshd

# 2. Kernel hardening
cat > /etc/sysctl.d/99-hardening.conf << 'EOF'
kernel.randomize_va_space = 2
kernel.dmesg_restrict = 1
kernel.kptr_restrict = 2
kernel.yama.ptrace_scope = 1
fs.suid_dumpable = 0
fs.protected_symlinks = 1
fs.protected_hardlinks = 1
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.all.log_martians = 1
net.ipv4.tcp_syncookies = 1
EOF
sysctl --system

# 3. Disable unused network protocols
cat > /etc/modprobe.d/blacklist-rare.conf << 'EOF'
blacklist dccp
blacklist sctp
blacklist rds
blacklist tipc
install dccp /bin/false
install sctp /bin/false
EOF

echo "Done. Verify SSH login BEFORE closing this session."
```

---

## Compliance Mapping

| Check                        | CIS L1 | CIS L2 | STIG   |
|------------------------------|--------|--------|--------|
| PermitRootLogin no           | ✓      | ✓      | ✓      |
| PasswordAuthentication no    | ✓      | ✓      | ✓      |
| No UID 0 duplicates          | ✓      | ✓      | ✓      |
| ASLR enabled (= 2)           | ✓      | ✓      | ✓      |
| auditd installed + running   |        | ✓      | ✓      |
| No NOPASSWD sudo             | ✓      | ✓      | ✓      |
| Firewall active (default DROP)|       | ✓      | ✓      |
| No empty passwords           | ✓      | ✓      | ✓      |
| USB storage blacklisted      |        | ✓      | ✓      |
| dmesg_restrict = 1           |        | ✓      | ✓      |

For CIS Benchmark details → see `references/cis-controls.md`
For STIG details → see `references/stig-checklist.md`

---

## Quick Reference: Common Attack Vectors → Audit Check

| Attack Vector                  | What to Check                                      |
|--------------------------------|----------------------------------------------------|
| Sudo misconfiguration LPE      | `NOPASSWD`, interpreter-based sudo rules           |
| Docker group escape            | `getent group docker`                              |
| World-writable cron LPE        | Cron scripts in writable dirs                      |
| SSH brute force                | `PasswordAuthentication`, `MaxAuthTries`, fail2ban  |
| Credential theft from shadow   | `/etc/shadow` permissions, PAM hashing strength    |
| Kernel module rootkit          | Signed module enforcement, auditd module rules     |
| Weak TLS on service            | Protocol + cipher audit per service                |
| SUID abuse                     | Non-standard SUID binaries                         |
| Log tampering                  | `/var/log` permissions, remote syslog              |
| Lateral movement via SSH keys  | All `authorized_keys` files on system              |
