# ELF Loading — Minimal Kernel Implementation Guide

## ELF File Structure

An ELF binary has three layers you care about:

```
ELF Header        (at offset 0)        — identifies format, architecture, entry point
Program Headers   (PT_LOAD segments)   — what to map and where
Section Headers   (optional for loader) — debugging/linking info, not needed to execute
```

For a kernel loader, you only need to parse program headers.

## ELF Header (64-bit)

```c
typedef struct {
    uint8_t  e_ident[16];   // Magic: \x7fELF, class, data encoding, version...
    uint16_t e_type;        // ET_EXEC (2) = executable, ET_DYN (3) = PIE
    uint16_t e_machine;     // EM_X86_64 (62), EM_AARCH64 (183)
    uint32_t e_version;     // EV_CURRENT (1)
    uint64_t e_entry;       // Virtual address of entry point
    uint64_t e_phoff;       // Offset of program header table
    uint64_t e_shoff;       // Offset of section header table (ignore for loading)
    uint32_t e_flags;       // Architecture-specific flags
    uint16_t e_ehsize;      // Size of this header (64 bytes for 64-bit)
    uint16_t e_phentsize;   // Size of one program header entry (56 bytes)
    uint16_t e_phnum;       // Number of program header entries
    uint16_t e_shentsize;   // Size of one section header entry
    uint16_t e_shnum;       // Number of section header entries
    uint16_t e_shstrndx;    // Index of section name string table
} Elf64_Ehdr;
```

Validate on load:
- `e_ident[0..3]` == `\x7fELF`
- `e_ident[4]` == 2 (ELFCLASS64)
- `e_ident[5]` == 1 (ELFDATA2LSB, little-endian) for x86-64/AArch64
- `e_machine` matches your architecture
- `e_type` == ET_EXEC or ET_DYN

## Program Header (64-bit)

```c
typedef struct {
    uint32_t p_type;    // Segment type
    uint32_t p_flags;   // Segment flags (PF_R=4, PF_W=2, PF_X=1)
    uint64_t p_offset;  // Offset of segment data in file
    uint64_t p_vaddr;   // Virtual address to map to
    uint64_t p_paddr;   // Physical address (ignore for userspace)
    uint64_t p_filesz;  // Bytes in file (may be less than p_memsz)
    uint64_t p_memsz;   // Bytes in memory (BSS padding: memsz > filesz)
    uint64_t p_align;   // Alignment (usually 0x1000 or 0x200000)
} Elf64_Phdr;
```

Segment types you need:
- `PT_LOAD` (1): Map this segment into memory. These are the only ones required for execution.
- `PT_INTERP` (3): Dynamic linker path. If present, the binary is dynamically linked — you need to load the interpreter too, or reject dynamic binaries.
- `PT_PHDR` (6): Location of program header table itself (optional, can ignore).
- `PT_TLS` (7): Thread-local storage template. Required for pthreads / libc TLS.

## Minimal ELF Loader — Step by Step

```
function load_elf(file_data, new_address_space):

1. Read and validate Elf64_Ehdr at offset 0

2. For each program header (e_phnum entries at offset e_phoff):
   a. Read Elf64_Phdr
   b. Skip if p_type != PT_LOAD
   c. Compute page-aligned mapping range:
        map_start = p_vaddr & ~(PAGE_SIZE-1)
        map_end   = (p_vaddr + p_memsz + PAGE_SIZE - 1) & ~(PAGE_SIZE-1)
   d. Allocate physical pages for [map_start, map_end)
   e. Map them into new_address_space
   f. Copy p_filesz bytes from file at p_offset to virtual address p_vaddr
   g. Zero-fill bytes from (p_vaddr + p_filesz) to (p_vaddr + p_memsz)
      (this covers the BSS segment — uninitialized data must be zeroed)
   h. Set page protection according to p_flags:
        PF_R → readable
        PF_W → writable
        PF_X → executable

3. Set up user stack:
   a. Allocate stack pages (typically 8 pages = 32KB initial stack)
   b. Map at a high user address, e.g. 0x0000_7FFF_FFFF_0000
   c. Push auxiliary vector, environment, argv, argc in System V ABI order
      (see "Initial Stack Layout" below)

4. Return e_entry as the address to jump to
```

## Initial Stack Layout (System V ABI)

The kernel must set up the initial stack before jumping to the entry point. The stack grows downward. Layout from high address to low:

```
[high address]
  strings/data for argv and envp (the actual bytes)
  NULL
  auxv[n].a_type = AT_NULL (end sentinel)
  auxv[n].a_val  = 0
  ...
  auxv[0].a_type
  auxv[0].a_val
  NULL                    (end of envp)
  envp[n-1] pointer
  ...
  envp[0] pointer
  NULL                    (end of argv)
  argv[argc-1] pointer
  ...
  argv[0] pointer
  argc                    (count, as uint64_t)
[RSP points here on entry]
[low address]
```

Auxiliary vector entries the libc needs:
```c
AT_PHDR   = 3   // Virtual address of program headers
AT_PHENT  = 4   // Size of one program header entry
AT_PHNUM  = 5   // Number of program headers
AT_PAGESZ = 6   // Page size (4096)
AT_BASE   = 7   // Base address of interpreter (0 if static)
AT_FLAGS  = 8   // Flags (0)
AT_ENTRY  = 9   // Entry point of main executable
AT_UID    = 11  // Real user ID
AT_EUID   = 12  // Effective user ID
AT_GID    = 13  // Real group ID
AT_EGID   = 14  // Effective group ID
AT_RANDOM = 25  // Pointer to 16 random bytes (for stack canary)
AT_NULL   = 0   // End of auxiliary vector
```

## Handling PIE (Position-Independent Executables)

ET_DYN binaries (PIE) can be loaded at any base address. Choose a base (e.g., `0x400000`) and add it to all `p_vaddr` values. Store the base so you can report it via `AT_BASE`.

Modern compilers produce PIE by default. Your loader should handle both ET_EXEC and ET_DYN.

## Rejecting Dynamic Binaries (Initial Simplification)

If `PT_INTERP` is present, the binary requires a dynamic linker. Two options:
1. **Reject**: Return `-ENOEXEC`. Tell the user to compile statically (`-static`). Reasonable for an early kernel.
2. **Support**: Load the interpreter ELF, map the main binary, set up `AT_BASE`, jump to interpreter entry point instead of main entry point. Complex but required to run typical Linux binaries.

For initial development, reject dynamic binaries and require static compilation. Musl with `-static` works well.

## Permissions Mapping

```
ELF p_flags → page table flags
PF_R (4) → present (always set)
PF_W (2) → writable
PF_X (1) → executable (clear NX bit)
PF_R|PF_W, no PF_X → data segment (present, writable, NX)
PF_R|PF_X, no PF_W → code segment (present, not writable, executable)
PF_R only           → read-only data (.rodata)
```

## Common Mistakes

- **Not zeroing BSS**: `p_memsz > p_filesz` for segments containing uninitialized data. The difference must be zeroed. If you copy `p_filesz` bytes and leave the rest from a previous page allocation, programs will see garbage in their `.bss` and global variables will have random values.
- **Mapping wrong size**: Map `p_memsz` (rounded to page size), copy `p_filesz` bytes. Don't map `p_filesz` — the BSS won't fit.
- **Ignoring alignment**: If `p_offset` and `p_vaddr` are not page-aligned together (they share the same offset within a page), you may need to map one page earlier and adjust.
- **Stack not 16-byte aligned at entry**: The ABI requires RSP to be 16-byte aligned at the point of the `call` to `main` — meaning RSP should be 16n-8 when the entry point is reached (because `call` pushes 8 bytes). Verify this or you'll get mysterious crashes in SSE code.
