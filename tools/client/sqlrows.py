"""Reads the rows of `INSERT INTO ... (columns) VALUES (...), ...;` statements from the module's SQL files,
so the client patch is built from exactly the rows the server gets. Other statements are skipped.
"""
from __future__ import annotations

import re
from pathlib import Path


def _tokens(text: str):
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c.isspace():
            i += 1
        elif text.startswith("--", i) or c == "#":
            i = text.find("\n", i)
            i = n if i < 0 else i
        elif text.startswith("/*", i):
            i = text.index("*/", i) + 2
        elif c == "'":
            out = []
            i += 1
            while True:
                c = text[i]
                if c == "\\":
                    out.append({"n": "\n", "t": "\t", "r": "\r", "0": "\0"}.get(text[i + 1], text[i + 1]))
                    i += 2
                elif c == "'" and text.startswith("''", i):
                    out.append("'")
                    i += 2
                elif c == "'":
                    i += 1
                    break
                else:
                    out.append(c)
                    i += 1
            yield ("str", "".join(out))
        elif c == "`":
            j = text.index("`", i + 1)
            yield ("id", text[i + 1:j])
            i = j + 1
        elif c.isdigit() or (c in "-+." and i + 1 < n and (text[i + 1].isdigit() or text[i + 1] == ".")):
            m = re.compile(r"[-+]?(0[xX][0-9a-fA-F]+|(\d+\.?\d*|\.\d+)([eE][-+]?\d+)?)").match(text, i)
            yield ("num", m.group(0))
            i = m.end()
        elif c.isalpha() or c == "_":
            m = re.compile(r"\w+").match(text, i)
            yield ("word", m.group(0))
            i = m.end()
        else:
            yield ("sym", c)
            i += 1


def _value(tok):
    kind, v = tok
    if kind == "str":
        return v
    if kind == "num":
        if "x" in v.lower():
            return int(v, 16)
        return float(v) if any(ch in v for ch in ".eE") else int(v)
    if kind == "word" and v.upper() == "NULL":
        return None
    raise ValueError(f"unexpected value {v!r}")


def statements(text: str):
    stmt = []
    for tok in _tokens(text):
        if tok == ("sym", ";"):
            if stmt:
                yield stmt
            stmt = []
        else:
            stmt.append(tok)
    if stmt:
        yield stmt


def inserts(text: str):
    """Yields (table, columns, [row values ...]) for every INSERT/REPLACE ... VALUES statement."""
    for st in statements(text):
        words = [v.upper() for k, v in st[:4] if k == "word"]
        if not words or words[0] not in ("INSERT", "REPLACE"):
            continue
        i = next(j for j, t in enumerate(st) if t == ("word", "INTO") or t == ("word", "into")) + 1
        table = st[i][1]
        i += 1
        if st[i] != ("sym", "("):
            continue                                   # INSERT ... SELECT without a column list
        cols = []
        i += 1
        while st[i] != ("sym", ")"):
            if st[i][0] in ("id", "word"):
                cols.append(st[i][1])
            i += 1
        i += 1
        if i >= len(st) or st[i][0] != "word" or st[i][1].upper() != "VALUES":
            continue                                   # INSERT ... SELECT
        i += 1
        rows = []
        while i < len(st) and st[i] == ("sym", "("):
            i += 1
            row = []
            while st[i] != ("sym", ")"):
                if st[i] != ("sym", ","):
                    row.append(_value(st[i]))
                i += 1
            i += 1
            if len(row) != len(cols):
                raise ValueError(f"{table}: {len(row)} values for {len(cols)} columns")
            rows.append(row)
            if i < len(st) and st[i] == ("sym", ","):
                i += 1
        yield table, cols, rows


def table_rows(paths: list[Path], table: str) -> dict[int, dict]:
    """Every row inserted into `table` by these files, as {id: {column: value}}; a later insert of an id wins."""
    out: dict[int, dict] = {}
    for path in paths:
        for t, cols, rows in inserts(path.read_text(encoding="utf-8")):
            if t != table:
                continue
            for row in rows:
                d = dict(zip(cols, row))
                out[int(d[cols[0]])] = d
    return out


def column_values(paths: list[Path], table: str, column: str) -> set[int]:
    vals = set()
    for path in paths:
        for t, cols, rows in inserts(path.read_text(encoding="utf-8")):
            if t == table and column in cols:
                k = cols.index(column)
                vals |= {int(r[k]) for r in rows if r[k] is not None}
    return vals
