# Production C++ Execution Pipeline for Online Judges

When building a high-capacity online judge like Codeforces or LeetCode using Docker, C++ introduces a unique set of challenges compared to interpreted languages like Python.

Python runs inside a Virtual Machine (the interpreter) which gracefully handles memory limits (`MemoryError`), stack depth (`RecursivityError`), and input buffering internally. C++ is a raw binary interacting directly with the Linux kernel (cgroups), meaning runtime errors manifest as harsh kernel signals (Segmentation Faults, OOM Kills).

Here is a complete, robust, production-safe C++ execution pipeline for your `sandbox`.

---

## 1. Why Python Works but C++ Fails in Containers

1.  **Memory Management:** Python tracks memory internally. If Python hits Docker's `mem_limit`, Python's allocator usually fails first, catching the `MemoryError` and exiting cleanly. C++ requests pages directly from the OS. When C++ exceeds `mem_limit`, the Linux kernel's **OOM Killer** instantly sends a `SIGKILL` (Exit Code 137). You never get an error message; the process just vanishes.
2.  **Stack Size:** Python controls its own recursion depth (default 1000). C++ relies on the Linux OS stack limit (usually only **8MB**). Without increasing the stack limit, a deep DFS algorithm in C++ will hit the 8MB OS limit and crash with a **Segmentation Fault** (Exit Code 139), even if your Docker `mem_limit` is 256MB.
3.  **Input/Output Buffering:** C++ `std::cin` will block indefinitely waiting for EOF or a newline if the test case is malformed or lacks a trailing `\n`. Python's `input()` usually detects the end of the file/stream and raises `EOFError` quickly.
4.  **libc Compatibility:** If you compile C++ on Alpine Linux (`musl libc`) and run it elsewhere, or compile it with static flags incorrectly, it crashes immediately on execution (Exit Code 127/1). **Always build and run C++ in a Debian or Ubuntu base image.**

---

## 2. Docker Base Image (The Target Environment)

Use `debian:bookworm-slim` or `ubuntu:22.04`. Do **not** use Alpine for C++ competitive programming. 

### `sandbox/Dockerfile`
```dockerfile
FROM debian:bookworm-slim

# Install C++ runtime, Python, and required utilities
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    g++ \
    coreutils \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Create unprivileged sandbox user with fixed UID/GID
# This prevents the container from running as root and modifying system files.
RUN groupadd -r sandbox -g 1000 && \
    useradd -u 1000 -r -g sandbox -m -s /bin/bash sandbox

# Copy the execution script
COPY run.sh /usr/local/bin/run.sh
RUN chmod +x /usr/local/bin/run.sh

# The volume mount point
WORKDIR /workspace

# Drop root privileges permanently
USER sandbox:sandbox

# Set the entrypoint explicitly so the sandbox runner is always invoked
ENTRYPOINT ["/usr/local/bin/run.sh"]
```

---

## 3. The Execution Script (`run.sh`)

This script handles secure compilation, strict stack/memory boundaries, input piping, and accurate exit code extraction.

### `sandbox/run.sh`
```bash
#!/bin/bash
# Language runtime router and executor

LANGUAGE="${LANGUAGE:-cpp}"
TIME_LIMIT="${TIME_LIMIT:-2}"

# 1. Helper to format JSON response for your backend
write_result() {
    local exit_code=$1
    local stage=$2
    local time_ms=$3
    local timed_out=${4:-false}
    local oom_killed=${5:-false}
    
    cat > /workspace/result.json <<EOF
{
    "exit_code": ${exit_code},
    "stage": "${stage}",
    "time_ms": ${time_ms},
    "timed_out": ${timed_out},
    "oom_killed": ${oom_killed}
}
EOF
}

# 2. C++ Executor Pipeline
if [ "$LANGUAGE" = "cpp" ]; then
    
    # --- COMPILATION STAGE ---
    # -O2: Competitive programming standard optimization
    # -std=c++17: Language standard
    # -DONLINE_JUDGE: Allows users to write `#ifndef ONLINE_JUDGE` for local debugging
    # -fno-asm: Prevent inline assembly (Security)
    # -lm: Math library linkage
    g++ -O2 -std=c++17 -fno-asm -DONLINE_JUDGE -Wall -Wextra -Wno-unused-result -o solution code.cpp -lm 2> error.txt
    COMPILE_EXIT=$?

    if [ $COMPILE_EXIT -ne 0 ]; then
        touch output.txt
        write_result $COMPILE_EXIT "compile" 0 false false
        exit 0
    fi

    # --- EXECUTION STAGE ---
    
    # CRITICAL: Increase Stack Size Limit!
    # Linux defaults to 8MB. Deep recursion (DFS, Segment Trees) will segfault.
    # Ulimit sets the stack to 64MB (65536 kilobytes).
    ulimit -s 65536 

    # Ulimit virtual memory to 256MB. Acts as a soft backup to Docker's hard limit.
    ulimit -v $((256 * 1024))

    START_NS=$(date +%s%N)
    
    # RUN via timeout
    # --signal=SIGTERM: Politely ask to terminate on timeout
    # --kill-after=1s: Force SIGKILL if it hangs on I/O during termination
    timeout --signal=SIGTERM --kill-after=1s ${TIME_LIMIT}s ./solution < input.txt > output.txt 2>> error.txt
    RUN_EXIT=$?

    END_NS=$(date +%s%N)
    ELAPSED_MS=$(( (END_NS - START_NS) / 1000000 ))

    # --- VERDICT RESOLUTION ---
    if [ $RUN_EXIT -eq 124 ]; then
        # 124 represents SIGTERM sent by the 'timeout' command -> TLE
        write_result $RUN_EXIT "run" $ELAPSED_MS true false
    elif [ $RUN_EXIT -eq 137 ]; then
        # 137 represents SIGKILL. This happens in two scenarios:
        # A) 'timeout' sent SIGKILL via --kill-after -> TLE
        # B) Linux kernel OOM Killer destroyed the process -> MLE
        
        # We assume OOM by default. Your Python backend checking `container.attrs['State']['OOMKilled']` 
        # will provide the definitive answer and overwrite this if needed.
        write_result $RUN_EXIT "run" $ELAPSED_MS false true
    else
        # Normal completion (0) or Runtime Error (Segfault/Abort/FloatException)
        write_result $RUN_EXIT "run" $ELAPSED_MS false false
    fi

fi
```

---

## 4. Differentiating Errors in Python Backend

When your `sandbox.py` reads `result.json`, you must classify the `exit_code` exactly like Codeforces does:

| Error Type | Detection Logic | Exit Code | Reason / Description |
| :--- | :--- | :--- | :--- |
| **Compilation Error (CE)** | `stage == "compile"` and `exit_code != 0` | `!= 0` | Syntax error. Return the contents of `error.txt` to the user so they can fix their syntax. |
| **Time Limit Exceeded (TLE)** | `timed_out == True` or `exit_code == 124` | `124` | Infinite loop, or unoptimized O(N^2) algorithm logic. |
| **Memory Limit Exceeded (MLE)**| `oom_killed == True` (Docker API) | `137` | C++ allocated an array or vector exceeding 256MB. |
| **Runtime Error (RE) - SIGSEGV**| `stage == "run"`, `exit_code == 139` or `11` | `139` | **Segmentation Fault**. Usually out-of-bounds array access, null pointer dereference, or infinite recursion (Stack Overflow). |
| **Runtime Error (RE) - SIGABRT**| `stage == "run"`, `exit_code == 134` or `6` | `134` | **Abort**. Failed C++ assertions (e.g., `assert(x > 0)` or `std::vector::at()` out of bounds). |
| **Runtime Error (RE) - SIGFPE** | `stage == "run"`, `exit_code == 136` or `8` | `136` | **Floating Point Exception**. Divide by zero (`int x = a / 0;`). |
| **Runtime Error (RE) - General**| `stage == "run"`, `exit_code != 0` | `!= 0` | Unhandled exceptions or returning non-zero from `main()`. |

---

## 5. Security & Isolation in `sandbox.py`

When launching the container from Python, your `docker.containers.run()` must be heavily fortified:

```python
container = client.containers.run(
    image="codearena-sandbox",
    volumes={work_dir: {"bind": "/workspace", "mode": "rw"}}, # Only bind workspace
    environment={
        "LANGUAGE": "cpp",
        "TIME_LIMIT": str(time_limit_secs),
    },
    network_mode="none",              # PERFECT: Disables internet so malicious code can't botnet or download scripts.
    mem_limit="256m",                 # 256MB is the industry standard for C++ limits.
    memswap_limit="256m",             # IMPORTANT: Prevent them from using disk swap if RAM fills up.
    cpu_quota=100000,                 # Restrict to exactly 1 CPU core usage (100k ms / period).
    cpu_period=100000,
    pids_limit=64,                    # Prevent fork bombs (`while(1) fork();`). 64 is plenty for compiling/running.
    read_only=True,                   # Make the entire OS read-only except bound volumes!
    user="sandbox",                   # Non-root unprivileged user.
    cap_drop=["ALL"],                 # Drop all Linux capabilities (chown, setuid, net_admin).
    working_dir="/workspace",
    detach=True,
)
```

### Why your C++ failed earlier
1. Your `sandbox/Dockerfile` had `CMD ["bash"]`, meaning the `run.sh` script wasn't even attempting to compile/run the C++ code unless your backend passed `/run.sh` explicitly in the `command` argument to `client.containers.run()`.
2. Missing `\n` in Stdin hangs `std::cin`.
3. Not running `ulimit -s 65536` caused recursion algorithms to trigger Exit Code 139.

Rebuild your Sandbox using the Dockerfile and `run.sh` provided above, and your C++ submissions will be as stable as python.
