# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

from father_trace import TraceWriter


def main() -> int:
    parser = argparse.ArgumentParser(description="Run any local FATHER process with end-to-end trace capture")
    parser.add_argument("--stage", required=True)
    parser.add_argument("--stream", default=os.getenv("FATHER_STREAM_ID", "CONTROL"))
    parser.add_argument("--run-id", default=os.getenv("FATHER_RUN_ID"))
    parser.add_argument("--cwd", default=None)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    command = list(args.command)
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        raise SystemExit("No command supplied")

    trace = TraceWriter(run_id=args.run_id, stream_id=args.stream)
    env = os.environ.copy()
    env["FATHER_TRACE_ID"] = trace.trace_id
    if trace.run_id:
        env["FATHER_RUN_ID"] = trace.run_id
    env["FATHER_STREAM_ID"] = args.stream

    print(f"FATHER_TRACE_ID={trace.trace_id}")
    print(f"TRACE_FILE={trace.path}")

    started = time.perf_counter()
    span_id = None
    try:
        with trace.span(args.stage, event="PROCESS", attributes={"command": command, "cwd": args.cwd}) as sid:
            span_id = sid
            proc = subprocess.Popen(
                command,
                cwd=args.cwd or None,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
            )
            assert proc.stdout is not None
            seq = 0
            for line in proc.stdout:
                print(line, end="")
                seq += 1
                trace.emit(
                    stage=args.stage,
                    status="OK",
                    event="STDOUT",
                    span_id=sid,
                    attributes={"seq": seq, "line": line.rstrip("\r\n")[:4000]},
                )
            rc = proc.wait()
            if rc != 0:
                raise RuntimeError(f"Child process exited with code {rc}")
    except Exception as exc:
        elapsed = (time.perf_counter() - started) * 1000.0
        print(f"TRACE FAILURE: {type(exc).__name__}: {exc}", file=sys.stderr)
        print(f"TRACE_ID={trace.trace_id}", file=sys.stderr)
        print(f"TRACE_FILE={trace.path}", file=sys.stderr)
        return 1

    elapsed = (time.perf_counter() - started) * 1000.0
    trace.emit(stage=args.stage, status="OK", event="PROCESS_SUMMARY", span_id=span_id,
               elapsed_ms=elapsed, attributes={"exit_code": 0})
    print(f"TRACE_ID={trace.trace_id}")
    print(f"TRACE_FILE={trace.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
