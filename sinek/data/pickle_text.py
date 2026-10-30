"""Read Shiu et al.'s ``sez_neurons.pickle`` without unpickling.

The pickle holds a plain ``dict[str, list[int]]`` (custom neuron name ->
FlyWire root IDs).  Unpickling executes code, so instead we disassemble the
file with :mod:`pickletools` and parse the text.  Only the opcodes a plain
dict/list/int/str pickle produces are understood; anything else raises.
"""
from __future__ import annotations

import io
import pickletools
import re
from pathlib import Path

_UNSAFE = {"GLOBAL", "STACK_GLOBAL", "REDUCE", "BUILD", "INST", "OBJ", "NEWOBJ", "NEWOBJ_EX"}


def read_name_to_ids(path: str | Path) -> dict[str, list[int]]:
    """Parse ``{name: [root_id, ...]}`` from a pickle via text disassembly."""
    buf = io.StringIO()
    with open(path, "rb") as f:
        pickletools.dis(f, out=buf)
    out: dict[str, list[int]] = {}
    key: str | None = None
    for line in buf.getvalue().splitlines():
        m = re.match(r"\s*\d+:\s+\S+\s+([A-Z_0-9]+)(?:\s+(.*))?$", line)
        if not m:
            continue
        op, arg = m.group(1), (m.group(2) or "").strip()
        if op in _UNSAFE:
            raise ValueError(f"unexpected opcode {op} in {path}; refusing to parse")
        if op in {"SHORT_BINUNICODE", "BINUNICODE", "UNICODE"}:
            key = arg[1:-1] if arg.startswith(("'", '"')) else arg
            out.setdefault(key, [])
        elif op in {"LONG1", "LONG", "BININT", "BININT1", "BININT2", "INT", "LONG4"} and key is not None:
            out[key].append(int(arg.rstrip("L")))
    return out
