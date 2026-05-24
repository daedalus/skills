# x86-64 Architecture Notes

## Boot Sequence

1. BIOS/UEFI hands off to bootloader (GRUB2/Limine)
2. Bootloader loads kernel ELF, sets up Multiboot2/Limine boot info
3. Bootloader jumps to kernel entry point in 64-bit long mode (Limine) or 32-bit protected mode (Multiboot2 — you must transition yourself)
4. Kernel initializes GDT, IDT, paging, then jumps to `kmain()`

**Limine is recommended**: it enters the kernel already in 64-bit long mode with a sane page table and passes a clean boot info struct. Saves significant early boot complexity.

## GDT (Global Descriptor Table)

The GDT defines memory segments. In 64-bit mode, segmentation is mostly vestigial, but the GDT still must be set up correctly for the CPL (privilege level) transitions.

Minimal GDT layout:
```
Index 0: Null descriptor (required)
Index 1: Kernel code segment  (base=0, limit=max, type=code, DPL=0, L=1)
Index 2: Kernel data segment  (base=0, limit=max, type=data, DPL=0)
Index 3: User code segment    (base=0, limit=max, type=code, DPL=3, L=1)
Index 4: User data segment    (base=0, limit=max, type=data, DPL=3)
Index 5: TSS descriptor       (64-bit TSS, 16 bytes wide)
```

The TSS (Task State Segment) is required: it holds RSP0 (the kernel stack pointer to load on privilege transition from ring 3 → ring 0).

## IDT (Interrupt Descriptor Table)

256 entries, one per interrupt/exception vector:
- 0–31: CPU exceptions (0=divide error, 6=invalid opcode, 14=page fault, etc.)
- 32–47: IRQs from PIC (timer=IRQ0=vector 32, keyboard=IRQ1=vector 33, etc.)
- 48–255: Available for software interrupts and APIC vectors

Each IDT entry points to an interrupt stub. The stubs must:
1. (For exceptions that don't push an error code) push a dummy 0 on the stack
2. Push the vector number
3. Jump to a common handler
4. Common handler: save all registers (pushes rax, rbx, rcx, rdx, rsi, rdi, rbp, r8–r15)
5. Call C handler with pointer to saved register frame
6. Restore all registers, iretq

**Page fault specifics**: Vector 14. Error code on stack encodes: present bit, write/read, user/supervisor, instruction fetch. Faulting address in CR2.

## Paging (4-level, PML4)

x86-64 uses a 4-level page table:
```
CR3 → PML4 (512 entries) → PDPT (512 entries) → PD (512 entries) → PT (512 entries) → Physical Page
```
Each level indexes 9 bits of the virtual address. Final 12 bits = page offset.

Virtual address breakdown (48-bit canonical):
```
[63:48] Sign extension (must match bit 47)
[47:39] PML4 index  (9 bits)
[38:30] PDPT index  (9 bits)
[29:21] PD index    (9 bits)
[20:12] PT index    (9 bits)
[11:0]  Page offset (12 bits)
```

Higher-half kernel mapping: Map kernel at `0xFFFFFFFF80000000`. Identity-map the first 4GB (or just the kernel's physical range) during early boot. Switch to the final page table layout after the VMM is initialized.

Page table entry flags (low 12 bits):
```
Bit 0: Present
Bit 1: Writable
Bit 2: User-accessible (set for userspace pages)
Bit 3: Write-through
Bit 4: Cache disable
Bit 5: Accessed (set by CPU)
Bit 6: Dirty (set by CPU on write)
Bit 7: Huge page (2MB at PD level, 1GB at PDPT level)
Bit 8: Global (don't flush from TLB on CR3 write; use for kernel pages)
Bit 63: No-execute (NX bit; requires EFER.NXE=1)
```

TLB invalidation: After modifying a page table entry, invalidate the TLB entry with `invlpg [vaddr]`. After switching CR3, the entire TLB is flushed (except Global pages).

## Interrupts and APIC

**Disable the legacy PIC first** (mask all IRQs: `outb(0xFF, 0xA1); outb(0xFF, 0x21)`), then initialize the Local APIC.

Local APIC (per-core):
- MMIO at `0xFEE00000` (or RDMSR IA32_APIC_BASE)
- Enable with APIC_BASE MSR bit 11
- Spurious interrupt vector register: set bit 8 to enable, bits 0-7 = spurious vector (typically 0xFF)
- Timer: divide register + initial count → fires LVT timer vector periodically

I/O APIC (for routing device interrupts):
- MMIO base from MADT table in ACPI
- Redirection table entries map IRQ lines to Local APIC vectors

**For a simple start**: Use HPET or PIT for the timer (simpler than APIC timer), keep PIC enabled with remapped vectors (IRQ0=0x20, IRQ1=0x21, ...).

## Syscall / Sysret ABI

**`syscall` instruction** (fast, preferred):
- Requires: `EFER.SCE = 1`, `STAR` MSR (sets CS/SS for kernel and user), `LSTAR` MSR (points to kernel handler), `SFMASK` MSR (flags to clear on syscall)
- On `syscall`: RIP → RCX, RFLAGS → R11, load LSTAR into RIP, load kernel CS/SS from STAR, clear SFMASK bits from RFLAGS
- On `sysret`: RCX → RIP, R11 → RFLAGS, load user CS/SS from STAR

Linux x86-64 syscall calling convention:
```
RAX = syscall number
Arguments: RDI, RSI, RDX, R10, R8, R9
Return value: RAX (negative errno on error)
Clobbered by kernel: RCX, R11
```

Setup MSRs:
```c
wrmsr(IA32_EFER, rdmsr(IA32_EFER) | 1);  // SCE bit
wrmsr(IA32_STAR, ((uint64_t)USER_CS_SELECTOR << 48) | ((uint64_t)KERNEL_CS_SELECTOR << 32));
wrmsr(IA32_LSTAR, (uint64_t)syscall_entry);
wrmsr(IA32_SFMASK, RFLAGS_IF);  // Disable interrupts on syscall entry
```

**Stack discipline**: On `syscall`, the kernel is still on the user stack (RSP unchanged). The handler must immediately switch to the kernel stack (load from TSS.RSP0 or a per-CPU variable) before doing anything else.

## Context Switch Mechanics

On a timer interrupt (or voluntary yield), the kernel saves the interrupted process's register state and loads another's.

What to save per-process:
```
General purpose: RAX, RBX, RCX, RDX, RSI, RDI, RBP, RSP, R8–R15
Instruction pointer: RIP (from interrupt frame)
Flags: RFLAGS (from interrupt frame)
Segment registers: CS, SS (from interrupt frame; DS/ES/FS/GS if used)
CR3 (page table root) — load new process's CR3 on switch
FS.base / GS.base MSRs — for TLS
FPU/SSE state — save/restore with FXSAVE/FXRSTOR or XSAVE/XRSTOR
```

FPU state is expensive to save — use lazy FPU switching: only save/restore on context switch if the process has used FPU instructions (track with the TS bit in CR0).

## Useful MSRs

```
IA32_EFER        = 0xC0000080  // Extended feature enable (NX, SCE, LME)
IA32_STAR        = 0xC0000081  // Syscall CS/SS selectors
IA32_LSTAR       = 0xC0000082  // Syscall entry point (64-bit)
IA32_SFMASK      = 0xC0000084  // Syscall RFLAGS mask
IA32_FS_BASE     = 0xC0000100  // FS segment base (TLS)
IA32_GS_BASE     = 0xC0000101  // GS segment base (per-CPU data)
IA32_KERNEL_GS_BASE = 0xC0000102 // Kernel GS base (swapgs target)
IA32_APIC_BASE   = 0x0000001B  // Local APIC base address
```

## Useful CPUID Checks

Before using features:
```c
// Check NX support: CPUID.80000001H:EDX bit 20
// Check XSAVE:     CPUID.01H:ECX bit 26
// Check FSGSBASE:  CPUID.07H:EBX bit 0 (enables RDFSBASE etc.)
```

## Common Early-Boot Pitfalls

- **Stack alignment**: x86-64 ABI requires 16-byte stack alignment at `CALL` instruction. The kernel entry point's stack is set by the bootloader — verify or re-align before calling C code.
- **Red zone**: The System V x86-64 ABI has a 128-byte "red zone" below RSP that signal handlers may not use. Kernel interrupt handlers must either use `-mno-red-zone` or skip past it by subtracting 128 before using the stack.
- **Canonical addresses**: Pointers with bits 48–63 not equal to bit 47 cause a #GP fault. This catches many NULL dereference and pointer corruption bugs.
- **Floating point**: Disabled by default in the kernel. Set CR0.EM=0, CR0.MP=1, CR4.OSFXSR=1, CR4.OSXMMEXCPT=1 before using SSE. Or just don't use FP in the kernel.
