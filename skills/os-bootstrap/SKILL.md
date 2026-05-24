---
name: os-bootstrap
description: Bootstrap the creation of a POSIX-like operating system kernel from scratch. Use this skill whenever someone wants to build, start, or plan a kernel or OS — including requests like "help me write an OS", "I want to build a kernel", "start an operating system project", "implement POSIX syscalls", "build a process scheduler", "write a VFS layer", "implement memory management for my kernel", "create a bootable system", or any request involving kernel internals (interrupts, paging, scheduling, file systems, system calls). Also trigger when someone wants to extend an existing hobby OS with a new kernel subsystem. This skill covers both project scaffolding AND deep technical implementation guidance — use it for either or both.
---

# OS Bootstrap Skill

This skill guides Claude through bootstrapping a POSIX-like kernel from a blank slate to a working, structured codebase. It covers two intertwined concerns: **project scaffolding** (directory layout, build system, toolchain) and **technical implementation** (memory, processes, VFS, syscalls). Both matter — a kernel with great architecture but no build system never ships, and a kernel that compiles but crashes in the scheduler is equally useless.

The skill is language-agnostic. Adapt all examples to the user's chosen language. The concepts are universal; the syntax is not.

---

## Phase 0: Establish Intent

Before generating any code or structure, understand the user's situation:

- **Starting fresh or extending?** If they already have a partial kernel, ask to see the existing layout before proposing structure.
- **Target architecture?** x86-64 is the most documented; AArch64 is common for embedded/Pi work. This affects bootloader choice, paging structures, and interrupt handling.
- **Language?** Affects toolchain setup, linking strategy, and how to handle unsafe/low-level primitives.
- **POSIX depth?** "POSIX-like" spans a huge range — from "I want `fork`/`exec`/`wait`" to "I want to pass the POSIX test suite." Clarify early so you don't over- or under-engineer.
- **Bare metal or VM?** QEMU/KVM is strongly recommended for development iteration speed.

Don't ask all of these at once — read context, make reasonable assumptions, and call out what you've assumed.

---

## Phase 1: Project Scaffolding

### Directory Layout

A well-structured kernel is easier to reason about and extend. Propose this canonical layout, adapting names to the language's conventions:

```
kernel/
├── arch/               # Architecture-specific code
│   └── x86_64/         # (or aarch64/, riscv/, etc.)
│       ├── boot/       # Bootloader, entry point, GDT/IDT setup
│       ├── mm/         # Arch-specific paging (page tables, TLB)
│       └── irq/        # Interrupt/exception handlers, APIC
├── kernel/             # Core kernel subsystems
│   ├── sched/          # Process scheduler
│   ├── mm/             # Generic memory manager (VMM, heap allocator)
│   ├── proc/           # Process/thread lifecycle
│   └── sync/           # Spinlocks, mutexes, semaphores
├── fs/                 # Virtual File System + concrete filesystems
│   ├── vfs/            # VFS layer (inode, dentry, file ops abstractions)
│   ├── ramfs/          # In-memory filesystem (good first target)
│   └── ext2/           # (optional, later)
├── drivers/            # Device drivers
│   ├── tty/            # Terminal/serial
│   ├── block/          # Block device abstraction
│   └── pci/            # PCI bus (if needed)
├── syscall/            # Syscall dispatch table and implementations
├── include/            # Public kernel headers
│   ├── kernel/
│   ├── arch/
│   └── posix/          # POSIX type definitions (pid_t, off_t, etc.)
├── lib/                # Kernel-internal utility library (no libc)
│   ├── string.c        # memcpy, memset, strlen, etc.
│   ├── printf.c        # Kernel printf (for debugging)
│   └── list.h          # Intrusive linked list
├── tests/              # Unit tests (can run in userspace for most logic)
├── Makefile / build.rs / CMakeLists.txt
├── linker.ld           # Linker script
└── README.md
```

The `arch/` split is important: it makes porting to a second architecture mechanical rather than surgical. Anything that touches hardware registers, page table formats, or interrupt vectors belongs under `arch/`. Everything else should be architecture-agnostic.

### Build System

Provide a working build system skeleton tailored to the user's language. Key concerns regardless of language:

- **Cross-compilation**: The kernel is built for a target that may not match the host. Set up cross-compilation from day one, even if host == target today.
- **Kernel vs userspace flags**: No stdlib, no floating point (unless explicitly saved in context switches), no stack protector (or configure it manually), position-independent or not as needed.
- **Separate linking**: Kernel needs a custom linker script to place sections at the right physical/virtual addresses.
- **Debug builds**: Include a debug target that adds debug symbols and disables optimizations.

Provide a concrete `Makefile` or equivalent that:
1. Compiles kernel sources with the right flags
2. Links with the custom linker script
3. Produces a raw binary + ELF + an ISO (via GRUB/limine/other) for QEMU boot

### Toolchain and Boot

Recommend a bootloader based on architecture and language:
- **GRUB2 + Multiboot2**: Most documented, works well for x86-64 C/C++ kernels
- **Limine**: Modern, clean protocol, excellent for Rust (via `limine` crate) and C
- **U-Boot**: Common for AArch64/embedded
- **Custom**: Only recommend if the user explicitly wants the learning experience

Set up QEMU as the primary test target. Provide a `make run` or equivalent that boots the kernel in QEMU. Add a `make debug` target that starts QEMU with `-s -S` and launches GDB attached to it.

---

## Phase 2: Kernel Subsystems — Implementation Guidance

Work through subsystems in dependency order. Each subsystem depends on the ones above it.

### 2.1 Physical Memory Manager (PMM)

The PMM tracks which physical RAM pages are free. It needs to exist before anything else can allocate memory.

**Approach**: A bitmap or buddy allocator over the physical address space. The bitmap is simpler to implement first; a buddy allocator gives better performance and fragmentation characteristics.

Key tasks:
- Parse memory map from bootloader (Multiboot2 / Limine provides this)
- Mark kernel image pages and reserved regions as used
- Expose `pmm_alloc_page()` and `pmm_free_page()` (or equivalent)
- Track contiguous allocations for DMA if needed

**Common pitfall**: Off-by-one errors in bitmap indexing, especially around the boundary between available and reserved regions. Write unit tests for the bitmap manipulations in userspace first.

### 2.2 Virtual Memory Manager (VMM) and Paging

The VMM maps virtual addresses to physical pages using the architecture's page table format.

Key tasks:
- Set up initial page tables (map kernel at high address, e.g. `0xFFFFFFFF80000000` for x86-64 higher-half)
- Implement `vmm_map(vaddr, paddr, flags)` and `vmm_unmap(vaddr)`
- Handle page faults (map new physical pages on demand, or panic if the fault is invalid)
- Keep a per-process page table root (CR3 on x86-64, TTBR0/TTBR1 on AArch64)

**Design decision**: Higher-half kernel (kernel lives in the top half of virtual address space, userspace in the bottom) is the standard POSIX approach and worth doing right from the start. It avoids virtual address conflicts when switching address spaces.

### 2.3 Kernel Heap Allocator

Once paging works, implement `kmalloc`/`kfree` (or equivalents). This is a dynamic allocator for kernel-internal use.

Common choices:
- **Slab allocator**: High performance, low fragmentation for fixed-size objects. More complex to implement.
- **Simple linked-list allocator**: Easy to implement correctly, sufficient to unblock other work. Replace later.
- **Buddy allocator at this level too**: Works well if the PMM is already buddy-based.

Implement a simple version first to unblock process/VFS work, then optimize.

### 2.4 Interrupt Handling

Interrupts are the kernel's interface with hardware and the mechanism for syscalls.

Key tasks:
- Initialize the interrupt descriptor table (IDT on x86-64) or equivalent
- Set up a Programmable Interrupt Controller (PIC or APIC on x86; GIC on AArch64)
- Implement generic interrupt dispatch: save full register state, call handler, restore, return
- Set up a timer interrupt (PIT or HPET on x86; timer on AArch64) — this drives preemptive scheduling

**Critical**: The interrupt handler entry/exit must save and restore *all* registers correctly, including segment registers and flags. Get this wrong and the kernel will silently corrupt state. Write a test that fires an interrupt and verifies register state is preserved.

### 2.5 Process Model

Implement the POSIX process model: `fork`, `exec`, `wait`, `exit`.

Data structures:
```
Process Control Block (PCB):
  - pid, ppid
  - state: (running, ready, blocked, zombie)
  - address space (pointer to page table root)
  - open file table
  - saved register state (for context switching)
  - signal state
  - working directory
```

Implement in this order:
1. `fork()` — duplicate the calling process (copy address space or use copy-on-write)
2. `exec()` — replace the address space with a new program (load ELF)
3. `wait()`/`waitpid()` — parent blocks until child exits; child becomes a zombie until reaped
4. `exit()` — mark process as zombie, wake waiting parent

**Copy-on-write fork**: Implement basic copy fork first (simpler, correct). Add CoW later as an optimization — it matters a lot for performance but not for correctness.

**ELF loading**: Write a minimal ELF parser that loads PT_LOAD segments into the new process's address space, sets up a stack, and jumps to the entry point.

### 2.6 Scheduler

The scheduler decides which process runs next. Start simple; complexity can be added incrementally.

Recommended progression:
1. **Round-robin**: Maintain a run queue. On timer interrupt, preempt current process, append to tail of queue, pick from head.
2. **Priority scheduling**: Assign static priorities; always run highest-priority runnable process.
3. **CFS-like**: Weighted fair queueing based on virtual runtime. Implement only if needed.

Context switch implementation:
- Save current process's register state to its PCB
- Load next process's register state from its PCB
- Switch page tables (write new CR3 / TTBR0)
- Return to next process

**Invariant to maintain**: The scheduler must be re-entrant (or protected by a lock) because it can be called from interrupt context. Be explicit about when interrupts are enabled vs disabled.

### 2.7 Syscall Interface

Syscalls are the boundary between userspace and kernel. POSIX defines the interface; you choose the mechanism.

Mechanism:
- **x86-64**: `syscall`/`sysret` instructions (faster) or `int 0x80` (legacy, simpler to start with)
- **AArch64**: `svc #0` instruction

Dispatch table:
```
syscall_table[] = {
  [SYS_read]   = sys_read,
  [SYS_write]  = sys_write,
  [SYS_open]   = sys_open,
  [SYS_close]  = sys_close,
  [SYS_fork]   = sys_fork,
  [SYS_exec]   = sys_execve,
  [SYS_exit]   = sys_exit,
  [SYS_wait]   = sys_waitpid,
  [SYS_getpid] = sys_getpid,
  ...
}
```

Implement syscalls in this priority order (each unlocks the next):
1. `write` → enables any output from userspace
2. `exit` → enables programs that terminate cleanly
3. `fork` + `exec` + `wait` → enables a shell launching programs
4. `open`/`read`/`close` → enables file I/O (requires VFS)
5. `mmap`/`brk` → enables userspace heap (required by most libc implementations)

### 2.8 Virtual File System (VFS)

The VFS is an abstraction layer that lets the kernel treat all filesystems uniformly.

Core abstractions:
```
inode      — a file or directory (metadata: size, permissions, type)
dentry     — a name-to-inode binding (the directory entry)
file       — an open file handle (inode + offset + flags)
superblock — a mounted filesystem instance
```

Operations interfaces (implement these as vtables / trait objects / function pointer structs):
```
inode_ops:  lookup, create, mkdir, unlink, link, rename
file_ops:   read, write, seek, ioctl, mmap
```

Implementation order:
1. **ramfs**: An in-memory filesystem. Simple to implement, no disk I/O. Sufficient to boot a userspace and run programs.
2. **devfs** or **procfs**: Pseudo-filesystems for device nodes and process info. Needed for a POSIX environment.
3. **ext2**: A real on-disk filesystem. Implement read-only first, then write support.

Mount table: Track mounted filesystems with (mount point, superblock) pairs. `open()` resolves a path by walking dentries, crossing mount points as needed.

### 2.9 Signals

Signals are asynchronous notifications delivered to processes. Required for a POSIX environment.

Minimal implementation:
- Signal mask per process (`sigprocmask`)
- Pending signal set per process
- Default actions: terminate, ignore, or stop
- `kill(pid, sig)` syscall to send a signal
- Signal delivery on return from kernel (check pending signals on every syscall/interrupt return)
- `sigaction` for custom handlers (requires careful user/kernel stack manipulation)

### 2.10 POSIX Thread Support (pthreads)

Threads share an address space but have separate register state and stacks.

Key additions:
- Thread IDs (distinct from PIDs)
- Per-thread stacks (allocated in the shared address space)
- `clone()` syscall (Linux-style) or `rfork()` — the primitive behind both `fork` and `pthread_create`
- Thread-local storage (TLS) setup

---

## Phase 3: Making It Useful

Once the core subsystems are in place, getting a userspace running validates everything:

1. **Port a minimal libc**: musl is the best choice — small, correct, and auditable. Newlib is an alternative for embedded targets. Porting requires implementing the syscalls musl expects.
2. **Boot a shell**: A simple shell (`sh`) exercises fork/exec/wait/open/read/write end to end. Getting `/bin/sh` to run is a meaningful milestone.
3. **Add a device driver**: A serial driver (UART) is the simplest. A keyboard + VGA text driver enables interactive use.

---

## Cross-Cutting Concerns

These apply throughout, not just to one phase:

**Debugging**: Set up serial output early (before interrupts, before memory management). A `kprintf` to UART is the kernel's `printf` debugging. Add a kernel panic handler that dumps registers and halts.

**Locking**: Decide early on a locking strategy. Start with a big kernel lock (BKL) if needed to make things correct before making them concurrent. Spinlocks for interrupt-safe sections; mutexes for blocking waits.

**Testing**: Unit-test subsystems in userspace where possible (memory allocators, ELF parser, VFS path resolution). Boot tests in QEMU validate integration.

**Documentation**: Write a short `ARCHITECTURE.md` as you go. Future-you (and contributors) need to understand invariants: "what must be true when entering the scheduler?", "who owns this lock?".

---

## Reference Files

- `references/posix-syscalls.md` — Priority-ordered POSIX syscall list with descriptions and dependencies
- `references/x86_64-notes.md` — x86-64 specific: GDT/IDT setup, paging structures, syscall/sysret ABI
- `references/aarch64-notes.md` — AArch64 specific: exception levels, MMU, SVC ABI
- `references/elf-loading.md` — ELF format walkthrough and minimal loader implementation guide

Read the relevant reference files when working on the corresponding subsystem.
