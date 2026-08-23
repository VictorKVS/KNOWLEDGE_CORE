#!/usr/bin/env python3
"""Bounded Stream-2 acquisition profile for change-triggered runs.

Pushes should validate newly registered/changed official routes quickly instead of
re-spending the full scheduled-run timeout budget on every known slow endpoint.
The authoritative acquisition logic, immutable write path, manifests, counters and
proof gates remain in ``pdn_security_stack_acquire``; only transport retry budgets
are clamped here. Scheduled/manual maintenance runs continue to use the full profile.
"""
from __future__ import annotations

import pdn_security_stack_acquire as base

_ORIGINAL_FETCH = base.fetch_bytes


def bounded_fetch(url: str, timeout: int = 75, attempts: int = 3):
    return _ORIGINAL_FETCH(url, timeout=min(timeout, 25), attempts=1)


base.fetch_bytes = bounded_fetch

if __name__ == "__main__":
    raise SystemExit(base.main())
