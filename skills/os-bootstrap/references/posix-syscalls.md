# POSIX Syscall Reference — Priority Ordered

Syscalls are listed in implementation priority order. Each tier unlocks the next.

## Tier 1 — Minimal Kernel Proof of Life
| Syscall       | Number (x86-64) | Description |
|---------------|-----------------|-------------|
| `write`       | 1               | Write bytes to a file descriptor |
| `exit`        | 60              | Terminate process |
| `exit_group`  | 231             | Terminate all threads in process |

These three let you prove your syscall dispatch, userspace stack, and kernel-to-user return work.

## Tier 2 — Process Model
| Syscall       | Number (x86-64) | Description |
|---------------|-----------------|-------------|
| `fork`        | 57              | Duplicate calling process |
| `execve`      | 59              | Replace process image with new program |
| `waitpid`     | 61              | Wait for child process state change |
| `getpid`      | 39              | Return calling process PID |
| `getppid`     | 110             | Return parent PID |

## Tier 3 — File I/O (requires VFS)
| Syscall       | Number (x86-64) | Description |
|---------------|-----------------|-------------|
| `open`        | 2               | Open a file, return fd |
| `read`        | 0               | Read bytes from fd |
| `close`       | 3               | Close fd |
| `lseek`       | 8               | Reposition file offset |
| `stat`        | 4               | Get file metadata |
| `fstat`       | 5               | Get file metadata by fd |
| `dup`         | 32              | Duplicate fd |
| `dup2`        | 33              | Duplicate fd to specific number |
| `pipe`        | 22              | Create pipe (anonymous fd pair) |

## Tier 4 — Userspace Heap (required by most libc)
| Syscall       | Number (x86-64) | Description |
|---------------|-----------------|-------------|
| `brk`         | 12              | Set program break (heap end) |
| `mmap`        | 9               | Map memory or file |
| `munmap`      | 11              | Unmap memory |
| `mprotect`    | 10              | Change memory protection |

## Tier 5 — Signals
| Syscall       | Number (x86-64) | Description |
|---------------|-----------------|-------------|
| `kill`        | 62              | Send signal to process |
| `sigaction`   | 13              | Install signal handler |
| `sigprocmask` | 14              | Block/unblock signals |
| `sigreturn`   | 15              | Return from signal handler |
| `pause`       | 34              | Sleep until signal |
| `alarm`       | 37              | Schedule SIGALRM |

## Tier 6 — Terminal and I/O Control
| Syscall       | Number (x86-64) | Description |
|---------------|-----------------|-------------|
| `ioctl`       | 16              | Device-specific control |
| `fcntl`       | 72              | File control (flags, locks) |
| `select`      | 23              | Synchronous I/O multiplexing |
| `poll`        | 7               | Poll file descriptors |

## Tier 7 — Directory and Filesystem
| Syscall       | Number (x86-64) | Description |
|---------------|-----------------|-------------|
| `getcwd`      | 79              | Get current working directory |
| `chdir`       | 80              | Change working directory |
| `mkdir`       | 83              | Create directory |
| `rmdir`       | 84              | Remove directory |
| `unlink`      | 87              | Remove file |
| `rename`      | 82              | Rename file |
| `link`        | 86              | Create hard link |
| `symlink`     | 88              | Create symbolic link |
| `readlink`    | 89              | Read symbolic link |
| `getdents64`  | 217             | Read directory entries |

## Tier 8 — Threads (pthreads)
| Syscall       | Number (x86-64) | Description |
|---------------|-----------------|-------------|
| `clone`       | 56              | Create thread or process (flags control sharing) |
| `set_tid_address` | 218         | Set pointer to thread ID |
| `futex`       | 202             | Fast userspace mutex primitive |
| `gettid`      | 186             | Get thread ID |

## Tier 9 — Time
| Syscall       | Number (x86-64) | Description |
|---------------|-----------------|-------------|
| `gettimeofday`| 96              | Get wall clock time |
| `clock_gettime` | 228           | Get time by clock ID |
| `nanosleep`   | 35              | Sleep for nanoseconds |
| `times`       | 100             | Get process CPU times |

## Errno Values
Implement these errno values from the start — musl and other libc implementations depend on exact values:

```c
#define EPERM    1   /* Operation not permitted */
#define ENOENT   2   /* No such file or directory */
#define ESRCH    3   /* No such process */
#define EINTR    4   /* Interrupted system call */
#define EIO      5   /* I/O error */
#define ENXIO    6   /* No such device or address */
#define EBADF    9   /* Bad file number */
#define ECHILD  10   /* No child processes */
#define EAGAIN  11   /* Try again */
#define ENOMEM  12   /* Out of memory */
#define EACCES  13   /* Permission denied */
#define EFAULT  14   /* Bad address */
#define EBUSY   16   /* Device or resource busy */
#define EEXIST  17   /* File exists */
#define ENODEV  19   /* No such device */
#define ENOTDIR 20   /* Not a directory */
#define EISDIR  21   /* Is a directory */
#define EINVAL  22   /* Invalid argument */
#define ENFILE  23   /* File table overflow */
#define EMFILE  24   /* Too many open files */
#define ENOSPC  28   /* No space left on device */
#define EROFS   30   /* Read-only file system */
#define EPIPE   32   /* Broken pipe */
#define ENOSYS  38   /* Function not implemented */
#define ENOTEMPTY 39 /* Directory not empty */
```
