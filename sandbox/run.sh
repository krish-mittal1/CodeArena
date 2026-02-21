#!/bin/bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Sandbox entrypoint — compile, run, report results
#
#  Expected env:
#    LANGUAGE   — "cpp" or "python"
#    TIME_LIMIT — seconds (default 5)
#
#  Expected files in /workspace:
#    code.cpp or code.py — user source code
#    input.txt           — test case input
#
#  Produces:
#    output.txt  — stdout from user program
#    error.txt   — stderr from user program
#    result.json — execution metadata (always written)
#
#  NOTE: We do NOT use `set -e` because the user program may
#  crash (non-zero exit) and we MUST still write result.json.
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LANGUAGE="${LANGUAGE:-cpp}"
TIME_LIMIT="${TIME_LIMIT:-5}"

cd /workspace

# ── Helper: write result JSON ─────────────────────────────
write_result() {
    local exit_code=$1
    local stage=$2
    local time_ms=$3
    local timed_out=${4:-false}
    local oom_killed=${5:-false}
    cat > result.json <<EOF
{
    "exit_code": ${exit_code},
    "stage": "${stage}",
    "time_ms": ${time_ms},
    "timed_out": ${timed_out},
    "oom_killed": ${oom_killed}
}
EOF
}

# ── Compile (C++ only) ────────────────────────────────────
if [ "$LANGUAGE" = "cpp" ]; then
    # Compile with stderr captured
    g++ -O2 -std=c++17 -o solution code.cpp 2> error.txt
    COMPILE_EXIT=$?

    if [ $COMPILE_EXIT -ne 0 ]; then
        # Compilation failed — write result and exit cleanly
        touch output.txt
        write_result $COMPILE_EXIT "compile" 0 false false
        exit 0
    fi

    # ── Run with timeout ──────────────────────────────────
    # Use --signal=TERM first, then --kill-after to force-kill.
    # Exit codes:
    #   124 = timeout killed the process (TLE)
    #   137 = SIGKILL (OOM kill by kernel, or kill-after)
    #   Other non-zero = runtime error in user program
    START_NS=$(date +%s%N)

    timeout --signal=TERM --kill-after=2s ${TIME_LIMIT}s ./solution < input.txt > output.txt 2> error.txt
    RUN_EXIT=$?

    END_NS=$(date +%s%N)
    ELAPSED_MS=$(( (END_NS - START_NS) / 1000000 ))

    if [ $RUN_EXIT -eq 124 ]; then
        # Killed by timeout command = TLE
        write_result $RUN_EXIT "run" $ELAPSED_MS true false
        exit 0
    elif [ $RUN_EXIT -eq 137 ]; then
        # SIGKILL — most likely OOM killed by cgroup/kernel
        write_result $RUN_EXIT "run" $ELAPSED_MS false true
        exit 0
    fi

    # Normal completion (exit 0 = success, other = runtime error)
    write_result $RUN_EXIT "run" $ELAPSED_MS false false

elif [ "$LANGUAGE" = "python" ]; then
    # Python: no compilation step
    touch error.txt
    START_NS=$(date +%s%N)

    timeout --signal=TERM --kill-after=2s ${TIME_LIMIT}s python3 code.py < input.txt > output.txt 2> error.txt
    RUN_EXIT=$?

    END_NS=$(date +%s%N)
    ELAPSED_MS=$(( (END_NS - START_NS) / 1000000 ))

    if [ $RUN_EXIT -eq 124 ]; then
        # Killed by timeout command = TLE
        write_result $RUN_EXIT "run" $ELAPSED_MS true false
        exit 0
    elif [ $RUN_EXIT -eq 137 ]; then
        # SIGKILL — most likely OOM killed by cgroup/kernel
        write_result $RUN_EXIT "run" $ELAPSED_MS false true
        exit 0
    fi

    # Normal completion
    write_result $RUN_EXIT "run" $ELAPSED_MS false false

else
    echo "Unsupported language: $LANGUAGE" > error.txt
    touch output.txt
    write_result 1 "compile" 0 false false
fi
