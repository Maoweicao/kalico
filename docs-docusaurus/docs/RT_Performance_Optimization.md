# Real-Time Performance Optimization

Kalico's host-side motion pipeline has been optimized with three layers of
real-time improvements. This document describes the architecture, what has been
changed, and how to configure a PREEMPT_RT kernel for maximum benefit.

## Architecture

The motion timing pipeline in Kalico runs as follows:

```
G-code (Python, ~ms per command)
  -> Look-ahead + junction deviation (Python, ~us)
  -> trapq_append (C) â€?trapezoidal velocity queue
  -> itersolve (C) â€?secant-method iterative step-time solver
  -> stepcompress (C) â€?step pulse compression/queuing
  -> serialqueue (C, background thread) â€?scheduled serial/CAN TX to MCU
  -> UART/CAN hardware
```

All performance-critical C code is compiled at runtime into `c_helper.so` via CFFI.
The timing-critical bottleneck is the **serialqueue background thread** which must
respond to hardware and timer events within microseconds to prevent MCU buffer
underruns.

## Changes Made

### 1. poll() â†?epoll + timerfd (`pollreactor.c`)

**Problem:** The original `pollreactor` used `poll()` with millisecond-level timeout
resolution (minimum 1ms). Timer callbacks were checked *after* `poll()` returned,
introducing unavoidable scheduling jitter.

**Solution:** On Linux (`#ifdef __linux__`), the event loop now uses:
- `epoll_create1` / `epoll_wait` â€?O(1) event-driven dispatch
- `timerfd_create` / `timerfd_settime` â€?nanosecond-level timer precision
  - Each timer callback gets its own `timerfd` file descriptor
  - `epoll_wait` wakes directly when the timerfd expires
  - No manual timeout calculation or polling needed

**Fallback:** Non-Linux platforms (macOS, BSD) retain the original `poll()`
implementation for compatibility.

| Metric | Before (`poll()`) | After (`epoll`+`timerfd`) |
|--------|-------------------|---------------------------|
| Timer resolution | 1 ms | 1 ns |
| FD dispatch | O(n) scan | O(1) event-driven |
| Hot-loop cost | 1000 wakeups/sec (min) | 0 when idle |

### 2. Real-Time Thread Scheduling (`serialqueue.c`)

**Problem:** The serial background thread ran at the default `SCHED_OTHER`
scheduling class, competing equally with Python threads, filesystem flushes,
network I/O, and other system tasks. On a busy system this could delay serial
data by tens of milliseconds.

**Solution:** After thread creation, the background thread is promoted to
`SCHED_FIFO` priority:

```c
struct sched_param sp;
sp.sched_priority = 1;
pthread_setschedparam(sq->tid, SCHED_FIFO, &sp);
```

- On a **PREEMPT_RT** kernel, this schedules the serial thread above all
  `SCHED_OTHER` tasks, ensuring timely execution.
- On a **standard** Linux kernel, `pthread_setschedparam` silently ignores
  this request (or requires `CAP_SYS_NICE`), safely falling back to
  `SCHED_OTHER`.

### 3. Priority-Inheritance Mutexes (`serialqueue.c`)

**Problem:** The Python main thread and the C serial thread share mutexes
(`sq->lock`, `sq->fast_reader_dispatch_lock`). When Python holds a mutex and the
high-priority serial thread blocks on it, the serial thread's priority can be
inverted â€?the Python thread runs at low priority, preventing the mutex from being
released quickly.

**Solution:** Mutexes are initialized with `PTHREAD_PRIO_INHERIT`:

```c
pthread_mutexattr_t mutex_attr;
pthread_mutexattr_init(&mutex_attr);
pthread_mutexattr_setprotocol(&mutex_attr, PTHREAD_PRIO_INHERIT);
pthread_mutex_init(&sq->lock, &mutex_attr);
```

- On a **PREEMPT_RT** kernel, the Python thread temporarily inherits the serial
  thread's high priority while holding the lock, eliminating priority inversion.
- On a **standard** kernel, `PTHREAD_PRIO_INHERIT` is a safe no-op.

## PREEMPT_RT Kernel Configuration

For the full benefit of these optimizations, install a PREEMPT_RT-patched kernel
on your host (typically a Raspberry Pi).

### Kernel command-line parameters

Add to `/boot/cmdline.txt` (Raspberry Pi) or `/etc/default/grub`
(`GRUB_CMDLINE_LINUX`):

```
isolcpus=3 nohz_full=3 rcu_nocbs=3 irqaffinity=0-2
```

| Parameter | Purpose |
|-----------|---------|
| `isolcpus=3` | Isolate CPU core 3 from general kernel scheduling |
| `nohz_full=3` | Disable the scheduler tick on core 3 when idle or single-task |
| `rcu_nocbs=3` | Offload RCU callbacks from core 3 |
| `irqaffinity=0-2` | Route all hardware interrupts to cores 0-2 |

### Pinning Klipper to the isolated core

In your Klipper service unit (e.g. `/etc/systemd/system/klipper.service`):

```ini
[Service]
CPUAffinity=3
```

### Kernel compile options

Essential PREEMPT_RT configuration when building a custom kernel:

```
CONFIG_PREEMPT_RT_FULL=y
CONFIG_HZ=1000
CONFIG_HIGH_RES_TIMERS=y
CONFIG_CPU_ISOLATION=y
CONFIG_NO_HZ_FULL=y
```

## Expected Improvements

| Metric | Stock kernel | + epoll/timerfd | + SCHED_FIFO | + PREEMPT_RT |
|--------|-------------|-----------------|--------------|--------------|
| Timer wake-up precision | ~1 ms | ~10 us | ~10 us | ~5 us |
| Timer wake-up jitter | +/- 5 ms | +/- 100 us | +/- 50 us | +/- 10 us |
| Serial thread preempt latency | 0-50 ms | 0-50 ms | 0-5 ms | < 100 us |
| Mutex priority inversion | possible | possible | reduced | eliminated |
| MCU buffer underrun risk | moderate | low | very low | near zero |

## Compatibility

- **Linux (Raspberry Pi OS, Armbian, etc.):** Full epoll/timerfd + RT support.
- **macOS / BSD:** Falls back to the original `poll()` implementation.
  SCHED_FIFO and PI mutex are no-ops.
- **Windows:** Not supported as a Klipper host.

## Code Changes Summary

| File | Change |
|------|--------|
| `klippy/chelper/pollreactor.c` | Linux path: epoll + timerfd. Non-Linux: original poll() |
| `klippy/chelper/serialqueue.c` | `#include <sched.h>`, PI mutex init, SCHED_FIFO thread |
| `klippy/chelper/pollreactor.h` | No API changes (fully compatible) |
| `klippy/chelper/__init__.py` | No changes needed |

## References

- [Linux PREEMPT_RT Wiki](https://wiki.linuxfoundation.org/realtime/)
- [timerfd_create(2) man page](https://man7.org/linux/man-pages/man2/timerfd_create.2.html)
- [epoll(7) man page](https://man7.org/linux/man-pages/man7/epoll.7.html)
- Klipper/Kalico serialqueue architecture: `klippy/chelper/serialqueue.c`
