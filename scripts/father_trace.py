# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import os
import socket
import sqlite3
import threading
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_TRACE_ROOT = Path(r"G:\1\FATHER_KNOWLEDGE\traces")
DEFAULT_DB = Path(r"G:\1\FATHER_KNOWLEDGE\db\father_knowledge.db")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4()}"


class TraceWriter:
    def __init__(self, trace_id: str | None = None, run_id: str | None = None,
                 stream_id: str | None = None, worker_id: str | None = None,
                 trace_root: str | Path | None = None, db_path: str | Path | None = None):
        self.trace_id = trace_id or os.getenv("FATHER_TRACE_ID") or new_id("TRACE")
        self.run_id = run_id or os.getenv("FATHER_RUN_ID")
        self.stream_id = stream_id or os.getenv("FATHER_STREAM_ID")
        self.worker_id = worker_id or os.getenv("FATHER_WORKER_ID") or f"{socket.gethostname()}:{os.getpid()}:{threading.get_ident()}"
        self.trace_root = Path(trace_root or os.getenv("FATHER_TRACE_ROOT") or DEFAULT_TRACE_ROOT)
        self.db_path = Path(db_path or os.getenv("FATHER_KNOWLEDGE_DB") or DEFAULT_DB)
        self.trace_root.mkdir(parents=True, exist_ok=True)
        self.path = self.trace_root / f"{self.trace_id}.jsonl"
        self._lock = threading.Lock()
        self._local = threading.local()

    def _parent(self) -> str | None:
        stack = getattr(self._local, "span_stack", None)
        return stack[-1] if stack else None

    def _append_stack(self, span_id: str) -> None:
        stack = list(getattr(self._local, "span_stack", []))
        stack.append(span_id)
        self._local.span_stack = stack

    def _pop_stack(self, span_id: str) -> None:
        stack = list(getattr(self._local, "span_stack", []))
        if stack and stack[-1] == span_id:
            stack.pop()
        elif span_id in stack:
            stack.remove(span_id)
        self._local.span_stack = stack

    def emit(self, *, stage: str, status: str, event: str | None = None,
             span_id: str | None = None, parent_span_id: str | None = None,
             entity_type: str | None = None, entity_id: str | None = None,
             source_sha256: str | None = None, fragment_sha256: str | None = None,
             model: str | None = None, prompt_profile: str | None = None,
             elapsed_ms: float | None = None, error_type: str | None = None,
             error_message: str | None = None, attributes: dict[str, Any] | None = None) -> dict[str, Any]:
        record = {
            "event_id": new_id("EVT"),
            "trace_id": self.trace_id,
            "span_id": span_id or new_id("SPAN"),
            "parent_span_id": parent_span_id if parent_span_id is not None else self._parent(),
            "run_id": self.run_id,
            "stream_id": self.stream_id,
            "worker_id": self.worker_id,
            "timestamp": utc_now(),
            "stage": stage,
            "event": event,
            "status": status,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "source_sha256": source_sha256,
            "fragment_sha256": fragment_sha256,
            "model": model,
            "prompt_profile": prompt_profile,
            "elapsed_ms": elapsed_ms,
            "error_type": error_type,
            "error_message": error_message,
            "attributes": attributes or {},
        }
        line = json.dumps(record, ensure_ascii=False, separators=(",", ":"))
        with self._lock:
            with self.path.open("a", encoding="utf-8") as f:
                f.write(line + "\n")
            self._write_db(record)
        return record

    def _write_db(self, record: dict[str, Any]) -> None:
        if not self.db_path.exists():
            return
        try:
            conn = sqlite3.connect(self.db_path, timeout=2)
            try:
                conn.execute(
                    """INSERT OR IGNORE INTO trace_events(
                       event_id,trace_id,span_id,parent_span_id,run_id,stream_id,worker_id,timestamp,stage,event,status,
                       entity_type,entity_id,source_sha256,fragment_sha256,model,prompt_profile,elapsed_ms,error_type,error_message,attributes_json)
                       VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        record["event_id"], record["trace_id"], record["span_id"], record["parent_span_id"],
                        record["run_id"], record["stream_id"], record["worker_id"], record["timestamp"],
                        record["stage"], record["event"], record["status"], record["entity_type"], record["entity_id"],
                        record["source_sha256"], record["fragment_sha256"], record["model"], record["prompt_profile"],
                        record["elapsed_ms"], record["error_type"], record["error_message"],
                        json.dumps(record["attributes"], ensure_ascii=False, separators=(",", ":")),
                    ),
                )
                conn.commit()
            finally:
                conn.close()
        except Exception:
            # Trace persistence must not hide the original business error.
            pass

    def link_entity(self, entity_type: str, entity_id: str, span_id: str,
                    relation: str = "CREATED_BY", metadata: dict[str, Any] | None = None) -> None:
        if not self.db_path.exists():
            return
        try:
            conn = sqlite3.connect(self.db_path, timeout=2)
            try:
                conn.execute(
                    """INSERT OR IGNORE INTO entity_trace_links(entity_type,entity_id,trace_id,span_id,relation,linked_at,metadata_json)
                       VALUES(?,?,?,?,?,?,?)""",
                    (entity_type, entity_id, self.trace_id, span_id, relation, utc_now(),
                     json.dumps(metadata or {}, ensure_ascii=False, separators=(",", ":"))),
                )
                conn.commit()
            finally:
                conn.close()
        except Exception:
            pass

    @contextmanager
    def span(self, stage: str, *, event: str | None = None, entity_type: str | None = None,
             entity_id: str | None = None, source_sha256: str | None = None,
             fragment_sha256: str | None = None, model: str | None = None,
             prompt_profile: str | None = None, attributes: dict[str, Any] | None = None):
        span_id = new_id("SPAN")
        parent = self._parent()
        started = time.perf_counter()
        self.emit(stage=stage, status="START", event=event, span_id=span_id, parent_span_id=parent,
                  entity_type=entity_type, entity_id=entity_id, source_sha256=source_sha256,
                  fragment_sha256=fragment_sha256, model=model, prompt_profile=prompt_profile,
                  attributes=attributes)
        self._append_stack(span_id)
        try:
            yield span_id
        except Exception as exc:
            self.emit(stage=stage, status="ERROR", event=event, span_id=span_id, parent_span_id=parent,
                      entity_type=entity_type, entity_id=entity_id, source_sha256=source_sha256,
                      fragment_sha256=fragment_sha256, model=model, prompt_profile=prompt_profile,
                      elapsed_ms=(time.perf_counter() - started) * 1000.0,
                      error_type=type(exc).__name__, error_message=str(exc), attributes=attributes)
            raise
        else:
            self.emit(stage=stage, status="OK", event=event, span_id=span_id, parent_span_id=parent,
                      entity_type=entity_type, entity_id=entity_id, source_sha256=source_sha256,
                      fragment_sha256=fragment_sha256, model=model, prompt_profile=prompt_profile,
                      elapsed_ms=(time.perf_counter() - started) * 1000.0, attributes=attributes)
        finally:
            self._pop_stack(span_id)
