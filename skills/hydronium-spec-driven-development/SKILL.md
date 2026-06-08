---
name: hydronium-spec-driven-development
description: >
  Generate hardware-accurate, spec-cited embedded firmware (C/C++) for a target MCU and peripheral.
  Auto-downloads the relevant datasheet and reference manual, extracts register definitions and timing
  constraints, produces MISRA-compliant driver code with every magic number annotated to the source
  section, emits supporting files (config header, Makefile snippet, Doxygen doc block), and — when
  given error output or a symptom description — runs an agentic debug trace from symptom to root-cause
  register.

  Use this skill whenever the user asks to: write a driver, init a peripheral, configure a clock/PLL,
  set a baud rate, init DMA/IRQ, flash firmware, debug a hardware fault, or generate any MCU-specific
  register-level code. Also trigger for "why is my UART wrong", "SPI not responding", "I2C NAK",
  "wrong frequency", "GPIO not toggling", or any embedded symptom description. Prefer this skill even
  for short requests like "I2C driver for nRF52840" — hardware correctness requires the spec.
---

# Hydronium Spec-Driven Development

Generate hardware-accurate, spec-cited embedded firmware for any MCU/peripheral combination.
Every register value is derived from the target device's actual datasheet or reference manual —
never from training-data averages.

---

## Agent Modes

**Default: infer the mode and state it, then proceed.** Do not block on a question unless the
request is genuinely ambiguous between two modes that produce incompatible outputs (e.g. the user
describes both a new feature and a broken symptom with no clear primary intent). In that case ask
once. Otherwise: infer from context (symptom description → Debug; "write a driver" → Code; design
question → Plan; datasheet lookup → Ask), state the inference in one sentence, and continue.

| Mode      | Use for |
|-----------|---------|
| **Ask**   | Querying datasheets, pinouts, understanding RTOS mechanisms, reading existing code without modifying it |
| **Plan**  | System design before coding: memory mapping, DMA routing, driver architecture, API surface definition |
| **Debug** | Hard faults, stack overflows, live serial log analysis, root-cause tracing |
| **Code**  | Writing HAL implementations, sensor drivers, bit-banging routines, register-level init sequences |

Use **Ask mode for exploration** — reading files and answering architectural questions burns context;
doing it in Ask mode keeps the main Code/Debug session clean.

---

## Context & Mentions

Use `@`-mentions to explicitly anchor context to specific artifacts rather than relying on auto-discovery alone.

| Mention | Description | Example use |
|---------|-------------|-------------|
| `@file` | Attach a local file's contents | `"Add DMA support to @src/drivers/drv8316.c"` |
| `@terminal` | Attach recent terminal output | `"Fix the linker errors in @terminal"` |
| `@problems` | VS Code: import IntelliSense errors | `"Resolve missing headers in @problems"` |
| `@git-changes` | Attach uncommitted diffs | `"Write a commit message for @git-changes"` |
| `@commit-hash` | Analyse a specific commit | `"Did @a1b2c3d introduce this priority inversion?"` |

**Drag and drop** schematics or logic-analyser screenshots directly into the VS Code chat pane
(hold Shift for external images) for visual analysis.

**`hydron.md`**: a file at the project root (created by `/init`) that records project baseline
rules — target MCU, peripheral assignments, coding conventions. If present, read it first and treat
its values as ground truth for clock frequencies, HAL level, and conventions. **If any value in
`hydron.md` conflicts with a value derived from a fetched reference manual** (e.g. `hydron.md`
states a peripheral bus clock of 42 MHz but your clock-tree derivation from the live register dump
or RM yields a different result): do not silently prefer either value. Generate code using the
**RM-derived value** (the more recently fetched, authoritative source) and mark every affected
constant with an inline conflict annotation:

```c
UART1->BAUD_REG = 0x02D9U;  /* CONFLICT: hydron.md=PCLK@42MHz → 0x016D; RM derivation=PCLK@84MHz → 0x02D9. Verify before flashing. */
```

Emit a summary comment block at the top of every generated file listing all conflicts. Ask the
user to resolve the discrepancy before the next session.

---

## Session Management

| Signal | Action |
|--------|--------|
| Corrected more than twice on the same point | Recommend `/new` — a fresh session with a sharper prompt beats accumulated corrections |
| Context filling up: more than ~15 tool calls made this session, or responses are visibly truncating, or the user reports sluggish replies | Recommend `/compact` to summarise history and free context |
| Switching to an unrelated task mid-session | Recommend `/new` — one session, one scope |
| User wants to try a different approach | `/fork` branches the session at the current message |

---

## Best Practices (from Hydronium docs)

These principles govern every session. Apply them before writing a single line of code.

**1. Pair every implementation with a verifiable check.**
Vague prompts produce code that compiles but silently misbehaves. Always include:
- The exact target board/MCU (e.g. `STM32F446RE`, `ESP32-S3`, `ATmega4809` — full part number, not just a family name)
- A concrete success criterion (register readback value, expected serial output, logic-analyser measurement)
- A build command to confirm compilation

**2. Explore → Plan → Code (for multi-file work).**
For anything spanning more than one file: first read and understand the existing code, then produce
a written plan listing every file to create/modify and the public API surface, then implement. Skip
the plan step only for trivial single-line changes.

**3. Prompt like a code review comment.**
Scope by filename. Reference existing driver patterns explicitly. Describe the symptom precisely.
The more specific the prompt, the less inference is required, and inference compounds error.

**4. Datasheets are the biggest accuracy multiplier.**
If the user has not provided a datasheet, fetch it (Step 2 below). If they have attached one (as a
PDF upload), prefer it over web-fetched versions — especially for errata sheets, which often
contradict the main datasheet on edge cases. Re-fetch if the user mentions a new revision.
**Verify datasheet revision against the actual board parts** — vendors ship multiple versions per
chip; the wrong revision misleads every register computation.

**5. Keep scope focused.**
Accuracy degrades as a session accumulates tool outputs and aborted attempts. Treat each driver as
its own focused task. If the user has been correcting the same point repeatedly, recommend starting
fresh with a sharper prompt.

**6. Stop early on wrong paths.**
If the derived register value or init sequence looks wrong, say so immediately with the correct
value and citation — do not continue generating code that will require a rework.

---

## Workflow

### Step 0: Mode Selection

Before any other step, identify the agent mode. Infer from context and state it in one sentence
before proceeding. Ask only when the request contains equal evidence for two incompatible modes
(e.g. simultaneously describes a new driver and an active fault with no clear primary intent).
Never silently default to Code mode.

### Step 1: Parse the Request

Extract:
- **MCU** — full part number required (e.g. `STM32F446RE`, `ESP32-S3`, `ATmega4809`, `nRF52840`,
  `RP2040`); ask if ambiguous. A family name alone (e.g. "STM32", "AVR") is never sufficient.
- **Peripheral** — full instance name where applicable (e.g. `UART1`, `I2C0`, `SPI2`, `TIM3`,
  `ADC1`; vendor naming varies)
- **Parameters** (baud rate, clock speed, DMA channel, interrupt priority, etc.)
- **HAL level**: bare-metal register access, vendor HAL/framework (e.g. STM32 HAL, ESP-IDF,
  Arduino, Zephyr drivers), or RTOS — **see HAL level notes below; each path has a completely
  different workflow**
- **Mode**: code generation, or debug trace (symptom → register)
- **Success criterion**: how will correctness be verified? (build command, register readback,
  logic-analyser check)

#### HAL Level Notes

- **Bare-metal register access**: follow this document's full workflow (divisor derivation, struct
  definitions, citation pattern, etc.).
- **Vendor HAL / framework** (e.g. STM32 HAL/CubeMX, ESP-IDF, Arduino, PSOC Creator, NXP SDK):
  do **not** use this document's raw register derivation steps. Instead: (a) generate the
  appropriate framework init call (e.g. `HAL_UART_Init()`, `uart_driver_install()`, `Serial.begin()`)
  with correct parameters derived from the datasheet; (b) cite the framework API reference, not the
  raw RM register section; (c) skip custom struct definitions — framework headers are assumed
  present and must not be duplicated.
- **RTOS (FreeRTOS, Zephyr, ThreadX, etc.)**: see the RTOS Drivers section. All register accesses
  that can be preempted require critical sections.

### Step 2: Fetch the Datasheet / Reference Manual

**Check for duplicate sources first.** If the user has uploaded a PDF *and* a fetched mirror
exists or is being fetched, use the user-uploaded PDF as the canonical source and discard the
fetched version. Do not attempt to merge two versions of the same document — a version conflict is
a hard stop: surface it and ask the user which revision to use.

**Priority order:**
1. **User-uploaded PDF** — if the user attached a datasheet, use it. Prefer it for errata sheets.
2. **Direct vendor URL** — construct from the part number and the Supported Platforms table (e.g.
   `<vendor_doc_base>/<family>/<partnumber>_rm.pdf`). The exact URL pattern varies by vendor; use
   the table below as a starting point and adapt as needed.
3. **web_fetch with headers** — many vendor servers 403 on bare curl; try `web_fetch` which sends
   browser-like headers.
4. **Search + mirror** — web_search for a university/mirror host, then web_fetch the PDF.
5. **ManualsLib** — scrape only as a last resort. **Treat ManualsLib page scrapes as unreliable.**
   ManualsLib returns navigation HTML that does not contain register text; verify that the scraped
   content includes actual register bit-field tables before using it. If verification fails, fall
   through to step 6.
6. **Refuse and ask** — if all fetch attempts fail (or return non-register HTML), say so
   explicitly and ask the user to upload the PDF. **Do not fall back to training-data guesses.**

Use `bash_tool` to store downloaded PDFs locally and extract relevant sections:

```bash
# 1. Fetch PDF (substitute actual URL for target MCU)
curl -L -o /tmp/<mcu>_rm.pdf "<vendor_rm_url>"

# 1a. Verify the file is actually a PDF (vendor portals sometimes return a 200 login/CAPTCHA page)
file /tmp/<mcu>_rm.pdf | grep -q "PDF" || { echo "FETCH_NOT_PDF — got HTML or redirect; fall through to Refuse and ask"; exit 1; }

# 2. Check pdftotext; if absent, auto-install pdfminer.six; if that fails, hard-stop
if command -v pdftotext >/dev/null 2>&1; then
  pdftotext /tmp/<mcu>_rm.pdf /tmp/<mcu>_rm.txt
else
  python3 -c "import pdfminer" 2>/dev/null || \
    pip install --break-system-packages --quiet pdfminer.six 2>/dev/null || \
    { echo "PDF_EXTRACT_UNAVAILABLE"; exit 1; }
  python3 - <<'PY'
import sys
try:
    import pdfminer.high_level as pm
    with open("/tmp/<mcu>_rm.pdf","rb") as f:
        text = pm.extract_text(f)
    open("/tmp/<mcu>_rm.txt","w").write(text)
    print("OK")
except Exception as e:
    print(f"EXTRACT_FAILED: {e}", file=sys.stderr)
    sys.exit(1)
PY
fi
# If exit code != 0 at any point: fall through to "Refuse and ask" (step 6).
# Do NOT guess register values from training data.

# 3. Extract peripheral section (adapt keywords to target peripheral)
grep -n "baud\|divisor\|prescaler\|clock\|peripheral_name" /tmp/<mcu>_rm.txt | head -100
```

Extract the exact section number (e.g. `§4.2.1` — whatever the target RM uses) covering:
- Peripheral register map
- Bit-field definitions
- Timing/clock formulas
- Initialization sequence

### Step 3: Determine the System Clock Tree

**Never assume a clock frequency.** Obtain the actual peripheral bus clock via **one** of the
following, in priority order:

1. **`hydron.md`** — if present and not conflicting (see hydron.md rules above), use its clock
   values directly.
2. **User-provided clock init source** — parse the clock configuration function (e.g.
   `SystemClock_Config()`, `clk_init()`, `board_init()`) to extract oscillator source, PLL
   multipliers, bus prescalers, and the resulting peripheral bus frequency. Show the arithmetic
   explicitly.
3. **Live register dump** — if the user has provided a register dump (any hex values for the
   clock control registers — GDB `x/wx` output, debugger memory view, or a paste of register
   values is sufficient), decode the vendor's PLL configuration and bus prescaler registers to
   derive actual frequencies. Register names vary by vendor (e.g. RCC_CFGR + RCC_PLLCFGR on
   STM32, CLK_CFGR on SAMD, CMU registers on EFM32 — consult the clock tree section of the RM
   for the correct register names on the target device).
4. **Reference manual clock tree section** — read the clock tree section of the RM for the
   reset-state defaults; use these only when none of the above is available, and label the result
   "reset-default assumption — verify against your actual init code."
5. **Hard stop** — if the clock value cannot be established by any of the four methods above,
   do not proceed. State that the clock frequency is unknown and ask the user to provide their
   clock init source or a live clock register dump before any register value can be computed.

Always state the source of the clock value and which bus or clock domain the peripheral sits on
(consult the clock tree section of the target RM — e.g. APB1/APB2/AHB on STM32, PCLK on AVR,
APB on ESP32, HFCLK on nRF) before computing any register value that depends on it.

### Step 4: Derive All Magic Numbers From Spec

**Never guess a register value.** For each computed value:

1. Quote the formula verbatim from the spec (e.g. *"BaudDiv = f_PCLK / (16 × BaudRate)"*, or
   whatever the target RM states)
2. State the clock source (from Step 3) and the peripheral bus frequency
3. **Check oversampling mode:** UART baud divisor formulas differ based on the oversampling
   setting. Before computing, locate the oversampling control in the target RM and identify its
   current value. Common patterns across vendors:
   - Some MCUs expose a configurable oversampling bit (e.g. STM32 CR1[OVER8], AVR UCSRnA[U2X])
     that selects between 8× and 16× sampling; the divisor formula and field widths change.
   - Others fix oversampling internally (e.g. ESP32 always 16×, nRF52 UARTE uses a fixed enum
     with no divisor at all).
   - For any unlisted vendor: read the baud rate register description; identify whether an
     oversampling factor appears in the formula and what controls it. State the mode explicitly
     before computing — never assume a default.
4. Show intermediate steps with full arithmetic
5. **Fractional tie-break rule:** when a fractional divisor rounds to exactly N.5, use
   **round-half-up** (ceiling). Show the rounded value, the resulting actual baud rate, and the
   error in ppm.
6. Produce the hex constant with a `// §X.Y.Z` citation inline

Example (generic 16× oversampling, f_PCLK=42 MHz, target=115200 baud):
```c
// f_PCLK = 42,000,000 Hz, BaudRate = 115200, oversampling = 16× (confirmed from RM §x.y)
// BaudDiv = 42_000_000 / (16 × 115200) = 22.7864...
// Mantissa = 22, Fraction = round(0.7864 × 16) = round(12.58) = 13  [round-half-up]
// Actual baud = 42_000_000 / (16 × 22.8125) = 114,942 bps  (−0.22% / −2200 ppm error)
UART1->BAUD_REG = (22U << 4) | 13U;  // 0x016D  §x.y.z <DocRef> Rev<N>
// NOTE: register name varies by vendor (BRR on STM32, UBRRnH:L on AVR, CLKDIV on ESP32, etc.)
```

### Step 5: Vendor Header Conflict Check

Before defining any register struct or peripheral base address:

```bash
# 1. Search project tree for vendor device headers
#    Adapt the glob to the target vendor (stm32*.h, sam*.h, nrf*.h, msp430*.h, etc.)
find . -name "*.h" | xargs grep -l "typedef.*_TypeDef\|_BASE_ADDR\|PERIPHERAL_BASE\|__VENDOR_CMSIS" \
  2>/dev/null | head -20

# 2. If nothing found in tree, check build system for external include paths
grep -rE "\-I\s*\S+|\binclude_directories\b|\btarget_include_directories\b" \
  Makefile CMakeLists.txt GNUmakefile build.ninja *.cmake 2>/dev/null | head -10
# Inspect those paths: ls <extracted_path>/*.h 2>/dev/null | head -20

# 3. If still nothing: ask the user explicitly
# "Does your project include a vendor device header (e.g. stm32f4xx.h, sam.h, nrf52840.h)?
#  If yes, provide the path. If no, confirm you want generated register structs."
```

- **If vendor device headers are found**: do **not** redefine peripheral structs, base addresses,
  or register types already declared in those headers. Use the vendor types directly. Duplicate
  definitions cause redefinition errors at compile time.
- **If no headers are found**: generate the minimal register structs needed, with a comment
  `/* generated — replace with vendor device header if available */`.

### Step 6: Generate Output Files

For **multi-file drivers** (e.g. driver + config + docs + Makefile), follow the Explore → Plan →
Code sequence: state the file list and API surface before writing any code. For single-file
requests, proceed directly.

Emit a complete file set:

#### `<peripheral>_driver.c` / `.h`
- Full init function with every register write cited
- Read/write helpers
- ISR stub (if IRQ mode requested) — **see ISR Name Verification below**
- **Memory barrier guidance** — after writes to peripheral control registers that affect
  subsequent instruction fetch or data access (e.g. enabling clocks, changing MPU/MMU regions,
  enabling caches), insert the appropriate barriers required by the target architecture:
  - **Cortex-M**: `__DSB()` after writes that must complete before the next peripheral access;
    `__ISB()` after changes that affect instruction fetch (e.g. cache enable)
  - **Other architectures**: consult the architecture reference manual for the equivalent
    fence/barrier instruction (e.g. `fence` on RISC-V, `dmb`/`dsb` on Cortex-A)
  - For routine peripheral init register writes (UART/SPI/I2C/TIM control registers) barriers are
    generally not required by the architecture; state explicitly when a barrier is inserted and
    why — do not insert them cargo-cult style
- MISRA C:2012 compliant (no implicit casts, explicit UL suffixes, no magic numbers without comment)

#### ISR Name Verification

ISR function names must match the vendor's vector table exactly. **Do not guess from memory.**
Before emitting any ISR stub:

```bash
# Locate the startup / vector file in the user's project
find . \( -name "startup_*.s" -o -name "startup_*.S" -o -name "startup_*.c" \
          -o -name "vectors.c" -o -name "vector_table.c" -o -name "isr_vector.s" \
       \) 2>/dev/null | head -5

# If found, grep for the peripheral's handler name (adapt to target peripheral)
grep -i "uart\|usart\|spi\|i2c\|tim\|adc" <found_startup_file> | head -20
```

ISR naming conventions vary by vendor and framework:
- **CMSIS (STM32, NXP, etc.)**: `<Peripheral>_IRQHandler` (e.g. `UART1_IRQHandler`)
- **Atmel/Microchip SAMD**: `<PERIPHERAL>_Handler` (e.g. `SERCOM0_Handler`)
- **AVR-GCC**: `ISR(<VECTOR_vect)` macro (e.g. `ISR(USART0_RX_vect)`)
- **Nordic nRF**: `nrfx_<peripheral>_irq_handler` or bare `UARTE0_UART0_IRQHandler`
- **RP2040**: handlers registered via `irq_set_exclusive_handler()` — no fixed name

If the startup file is not present, fetch the IRQ/vector table section from the RM and construct
the name using the vendor's documented convention. Cite the RM section.

**If search returns multiple candidates** (e.g. shared vectors where one entry covers multiple
peripheral instances): cross-reference the RM IRQ number table for the specific instance. If still
ambiguous, emit all plausible candidates as `TODO` stubs with the table citation and instruct the
user to confirm against their startup file.

If the name cannot be verified from any source, emit a `TODO` comment with the expected pattern
and instruct the user to verify.

#### `<peripheral>_config.h`
- All tunable parameters as `#define` with units in comments
- Clock assumptions documented, including oversampling mode for UART peripherals
- Guard against vendor header conflicts: wrap any `typedef` or base-address `#define` that may
  already exist in device headers with `#ifndef` guards, e.g.:
  ```c
  #ifndef UART1_BASE_ADDR
  #define UART1_BASE_ADDR  0x40011000UL
  #endif
  #ifndef UART1_TypeDef_DEFINED
  typedef struct { volatile uint32_t CR1; ... } UART1_TypeDef;
  #define UART1_TypeDef_DEFINED
  #endif
  ```
  A `#pragma once` / include guard on the file itself is not sufficient — it only prevents
  re-inclusion of *this* file, not conflicts with vendor headers included elsewhere.

#### `<peripheral>_docs.md`
- Doxygen-style function documentation
- Register map summary for the configured peripheral
- Verification checklist (what to probe on a logic analyser / serial console)
- **Build command** to confirm compilation (from best practice #1)

#### `Makefile.snippet` (if bare-metal)
- Compiler flags, linker script hint, flash command

### Step 7: Citation Block

At the end of every generated `.c` file, emit a `CITATIONS` block:

```c
/*
 * CITATIONS
 * ---------
 * [1] <DocRef> §<section>  — <peripheral> baud rate / divisor register
 * [2] <DocRef> §<section>  — <peripheral> control register / mode bits
 * [3] <DocRef> §<section>  — clock tree / peripheral bus prescaler
 * Clock source: hydron.md | clock init function | register dump | RM reset default
 * Oversampling: <mode and value, e.g. "16× fixed" or "OVER8=0 (CR1[15]=0)">
 * Source: <full URL of fetched document>
 */
```

---

## Agentic Debug Mode

Trigger when the user provides: error output, wrong behavior description, register dump, fault
address, or a symptom like "returns 0xFFFF after ~30s" or "CS timing issue".

**First, classify the failure pattern:**

- **Deterministic** (fails every time, same way): proceed to the standard Debug Trace Protocol below.
- **Intermittent** (fails sometimes, under load, after N operations): do **not** start with the
  clock tree. Start with fault handler analysis — see Intermittent Fault Protocol below.
- **Unknown**: ask the user "Does this fail every time, or only sometimes?" before proceeding.

**Prompt the user to scope the symptom** if not already scoped:
- Which file / function exhibits the problem?
- What is the expected vs. observed value?
- How long does it take to manifest (immediate vs. after N operations)?

### Fault Exception Triage

On architectures with hardware fault classification (Cortex-M, RISC-V with trap CSRs, etc.), an
unhandled fault exception is the most common "something is broken" symptom. If the user reports a
hard fault, system lockup, or reset loop, **decode the fault status before anything else**.

#### Cortex-M (HardFault / UsageFault / BusFault)

**Fault decode protocol:**

```c
// Add to startup or fault handler to decode SCB fault registers
void HardFault_Handler(void) {
    volatile uint32_t CFSR  = SCB->CFSR;   // Combined fault status
    volatile uint32_t HFSR  = SCB->HFSR;   // Hard fault status
    volatile uint32_t MMFAR = SCB->MMFAR;  // MemManage fault address (if MMARVALID)
    volatile uint32_t BFAR  = SCB->BFAR;   // Bus fault address (if BFARVALID)
    (void)CFSR; (void)HFSR; (void)MMFAR; (void)BFAR;
    __BKPT(0); // Halt in debugger; inspect the above variables
}
```

| Register | Field | Meaning |
|----------|-------|---------|
| CFSR[7:0] | MMFSR | MemManage fault (MPU violation, null deref) |
| CFSR[15:8] | BFSR | Bus fault (BFARVALID+BFAR = faulting address) |
| CFSR[31:16] | UFSR | UsageFault (UNDEFINSTR, INVSTATE, DIVBYZERO, UNALIGNED) |
| HFSR[30] | FORCED | Escalated from configurable fault |
| HFSR[1] | VECTBL | Vector table read fault |

Ask the user to read out `CFSR`, `HFSR`, `MMFAR`, `BFAR` from the debugger (or add the stub
above) before proceeding with any other debug step.

#### Other architectures

- **AVR**: check MCUSR for reset cause (WDRF/BORF/EXTRF/PORF); enable watchdog reset detection.
- **RISC-V**: read `mcause` and `mtval` CSRs; `mcause` encodes exception code, `mtval` holds the
  faulting address or instruction.
- **ESP32 (Xtensa)**: decode the panic output in the serial log (`Guru Meditation Error`); the
  register dump includes EPC1–EPC4 and EXCCAUSE.
- **For any unlisted architecture**: consult the architecture reference for the fault status
  register equivalent and decode it before proceeding.

### Intermittent Fault Protocol

For failures that are non-deterministic, load-dependent, or timing-sensitive:

```
SYMPTOM → FAULT CLASS → STACK/HEAP CHECK → DMA COHERENCY → RACE CONDITION → ROOT CAUSE
```

1. **Enable fault handlers first** — add the fault decode stub for your architecture; intermittent
   faults often escalate to a catchable exception eventually.
2. **Check stack usage** — determine if the MCU has a stack overflow detector (Cortex-M7 MSPLIM,
   FreeRTOS stack watermark, AVR stack canary). Compare the current stack pointer to the linker
   script stack limit at the fault site.
3. **DMA coherency** — if DMA is involved: on architectures with data caches (Cortex-M7, Cortex-A,
   RISC-V with D-cache), verify cache invalidation before CPU reads of DMA-written buffers and
   cache clean before DMA reads of CPU-written buffers. On cache-less MCUs this step is N/A.
4. **Race condition** — if shared data is accessed from ISR and main context, check for missing
   critical section guards (architecture disable-IRQ or RTOS primitive).
5. **Heap fragmentation** — if `malloc` or an RTOS heap allocator is used, add heap usage logging.

### Standard Debug Trace Protocol (Deterministic Failures)

```
SYMPTOM  →  SUBSYSTEM  →  CLOCK TREE  →  REGISTER  →  ROOT CAUSE  →  PATCH
```

**Steps:**

1. **Classify symptom** — which peripheral/subsystem is implicated?
2. **Check clock tree** — is the peripheral clock enabled? Correct prescaler? (Use Step 3 clock
   derivation methodology — do not assume a frequency.)
3. **Check init sequence** — verify order of operations against spec (e.g. the peripheral enable
   bit must be set after the baud rate divisor register is written — verify the exact required
   order in the RM's initialization procedure subsection)
4. **Identify the register** — compute the expected value, compare to what the user set
5. **Root cause** — one sentence: what is wrong and why
6. **Patch** — minimal diff, with corrected value cited to spec section

**Example trace (vendor-neutral):**

```
SYMPTOM:   UART output is garbage at 115200 baud
SUBSYSTEM: UART1
CLOCK:     Peripheral bus = 84 MHz (derived from clock init function; PLL × 4, bus /2)
SAMPLING:  16× oversampling (confirmed from control register; no 8× mode on this device)
REGISTER:  Expected divisor = 84_000_000 / (16 × 115200) = 45.57
           Mantissa = 45, Fraction = round(0.57 × 16) = 9 → BaudReg = 0x02D9
           Actual value in register: 0x016D  (matches 42 MHz, not 84 MHz)
ROOT CAUSE: Peripheral bus clock assumed 42 MHz; actual post-PLL frequency is 84 MHz
PATCH:     UART1->BAUD_REG = 0x02D9U;  // §<x.y.z>, bus=84MHz, 16× oversampling
           // (substitute vendor baud register name — see RM register map)
```

Always re-cite the corrected value to the spec section.

---

## RTOS Drivers

When HAL level is RTOS, use the RTOS-appropriate primitives for every synchronization operation.
The examples below use **FreeRTOS** naming; substitute the equivalent for your RTOS (see table).

| Operation | FreeRTOS | Zephyr | ThreadX |
|-----------|----------|--------|---------|
| Enter critical section | `portENTER_CRITICAL()` | `irq_lock()` | `tx_interrupt_control(TX_INT_DISABLE)` |
| Exit critical section | `portEXIT_CRITICAL()` | `irq_unlock(key)` | `tx_interrupt_control(TX_INT_ENABLE)` |
| Mutex acquire/release | `xSemaphoreTake` / `xSemaphoreGive` | `k_mutex_lock` / `k_mutex_unlock` | `tx_mutex_get` / `tx_mutex_put` |
| Signal from ISR | `xTaskNotifyGiveFromISR` | `k_sem_give` | `tx_semaphore_put` |
| Block until signal | `ulTaskNotifyTake` | `k_sem_take` | `tx_semaphore_get` |
| Queue send from ISR | `xQueueSendFromISR` | `k_msgq_put` | `tx_queue_send` |

- **ISR ↔ task data sharing**: use the critical section primitive for your RTOS — never bare
  architecture disable-IRQ inside RTOS task context unless the RTOS explicitly permits it.
- **Blocking sends/receives**: use queue/message-passing APIs rather than spin-waiting on status
  registers from task context.
- **Peripheral send task-safety**: wrap transmit functions with a mutex to prevent interleaved
  output from multiple tasks.
- **DMA completion**: for single-consumer wakeup, prefer the lightest signal primitive (task
  notification in FreeRTOS, semaphore in Zephyr/ThreadX); use a counting semaphore or event
  flags for multi-consumer scenarios.
- **Stack size**: budget ≥512 bytes of extra stack per driver task beyond its measured watermark.
- **Framework-native drivers** (Zephyr device model, ThreadX USBX/FileX, etc.): use the
  framework's driver API and cite framework docs rather than raw register writes.

---

## Multi-Peripheral Interaction

When the request involves shared resources across multiple peripherals:

- **Shared DMA channels/streams**: verify the requested DMA channel is not already claimed by
  another peripheral. Consult the target RM's DMA request mapping table (section name varies by
  vendor: "DMA request mapping", "DMAC triggers", "PRS channels", etc.). State the assignment
  explicitly and flag any conflict.
- **GPIO alternate function remapping**: check that mapping a GPIO AF for one peripheral does not
  shadow another peripheral's required pin. Use the AF/pinmux table from the datasheet pinout
  section.
- **Bus sharing (SPI, I2C)**: the driver must arbitrate access per transaction (CS gating for SPI,
  bus ownership for I2C multi-master); verify no concurrent access from multiple drivers.
- **Peripheral clock gating interaction**: enabling or disabling a peripheral's clock gate affects
  all peripherals sharing that gate or bus clock domain; document which gates are touched.
- **Clock domain crossings**: if a signal path crosses between peripherals on different clock
  domains (e.g. a UART RX line feeding a timer input capture running from a different clock
  source), note the crossing. Signals crossing clock domain boundaries may require synchronization
  logic; at minimum, document that the two clocks differ and flag any timing assumptions that
  depend on their ratio.
- Handle these interactions explicitly in the Plan step before generating any code.

---

## Supported Platforms (priority fetch targets)

| MCU family | Vendor doc | Notes |
|-----------|-----------|-------|
| STM32F0/F1/F2/F3/F4/F7/H7/G0/G4/L0/L4/WB | st.com RM + DS | RM number varies per family |
| ESP32 / ESP32-S2/S3/C3/C6/H2 | espressif.com TRM | separate datasheet + TRM; use ESP-IDF API for HAL-level requests |
| ATmega328P / ATmega2560 / ATtiny | microchip.com | combined datasheet |
| MSP430 / MSPM0 | ti.com | SLAU + SLAS docs |
| nRF52840 / nRF5340 / nRF9160 | infocenter.nordicsemi.com | Product Spec PDF |
| RP2040 / RP2350 | datasheets.raspberrypi.com | |
| Teensy 4.x | IMXRT1060 (NXP) RM from nxp.com | |

For unlisted parts: web_search `"<exact part number>" "reference manual" OR "technical reference" filetype:pdf`
and fetch the first authoritative result.

---

## Quality Rules

- **No assumed clocks.** Always derive from the system clock tree (Step 3); state the derivation source. If the clock cannot be established by any method, hard-stop and ask.
- **No copy-paste register values** from training data — always recompute from spec formulas.
- **Every `->` register write** gets an inline `// §X.Y.Z` citation.
- **All constants** use explicit type suffixes (`U`, `UL`, `ULL`).
- **Init order** must match the spec's "initialization procedure" subsection exactly.
- **ISR names** must be verified against the startup file or RM vector table — not guessed from
  memory. If grep returns multiple candidates, cross-reference the IRQ number table. See ISR Name
  Verification in Step 6.
- **Oversampling mode must be explicit for all vendors.** Locate the oversampling control in the
  target RM, state its value, and use the vendor-correct divisor formula. Never silently assume
  any oversampling factor or default.
- **Fractional tie-break**: use round-half-up; always show the resulting baud error in ppm.
- **Vendor header check before structs**: search project tree *and* build system include flags
  before generating register type definitions; if neither yields a result, ask the user explicitly.
- **Memory barriers**: insert architecture-appropriate barriers only where required; explain why.
- **Fault decode first**: on any fault/lockup/reset-loop symptom, decode the architecture's fault
  status registers before clock tree or register init investigation.
- **Classify before tracing**: ask "intermittent or deterministic?" before running the debug protocol.
- **Mode selection before coding**: infer and state the mode; ask only when genuinely ambiguous
  between two incompatible modes. Never silently default to Code mode.
- **hydron.md conflicts produce annotated output, not a hard block**: use RM-derived values, mark
  every affected constant with a CONFLICT annotation, emit a summary block, ask for resolution.
- **ManualsLib is unreliable**: verify scraped content contains register tables; fall through to
  user upload if it doesn't.
- **PDF extraction fallback chain**: pdftotext → pdfminer.six (auto-install) → refuse and ask.
  Never guess register values if extraction fails.
- **Always name the exact board/MCU.** Missing part number → ask before generating.
- **Attach errata.** If the user mentions unexpected silicon behavior, check whether an errata
  sheet exists for the part (separate fetch from main RM/DS).
- **Stop on wrong path.** If the derived value or sequence looks inconsistent, stop and correct
  immediately — do not generate more code that will need rework.
- **If PDF fetch fails**, say so explicitly and ask the user to upload the datasheet — do not fall
  back to training-data guesses.
