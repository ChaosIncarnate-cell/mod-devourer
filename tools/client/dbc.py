"""WDBC files (3.3.5a): read, change rows, write back. Records are kept as bytes; only the rows the tool touches
are decoded, so everything else in the client's file stays byte for byte as it was.

Field layouts for the tables written from SQL are in dbc_layouts.json (AzerothCore's `*_dbc` column order).
"""
from __future__ import annotations

import json
import struct
from pathlib import Path

LAYOUTS = {k: v for k, v in json.loads((Path(__file__).with_name("dbc_layouts.json")).read_text()).items()
           if not k.startswith("_")}
BY_TABLE = {v["table"]: k for k, v in LAYOUTS.items()}
_CODE = {"int": "i", "uint": "I", "float": "f", "string": "I", "byte": "B"}


class Dbc:
    def __init__(self, data: bytes, name: str = "?"):
        magic, count, self.fields, self.size, strsize = struct.unpack_from("<4s4I", data)
        if magic != b"WDBC":
            raise ValueError(f"{name}: not a WDBC file")
        self.name = name
        body = 20 + count * self.size
        self.records = [bytes(data[20 + i * self.size:20 + (i + 1) * self.size]) for i in range(count)]
        self.strings = bytearray(data[body:body + strsize]) or bytearray(b"\0")
        self._interned: dict[str, int] = {}
        self.layout = None
        self.fmt = None

    # --- layout ------------------------------------------------------------------------------------------
    def use_layout(self, dbc_name: str) -> "Dbc":
        fields = LAYOUTS[dbc_name]["fields"]
        fmt = "<" + "".join(_CODE[t] for _, t in fields)
        if len(fields) != self.fields or struct.calcsize(fmt) != self.size:
            raise ValueError(f"{self.name}: {self.fields} fields / {self.size} bytes, expected {len(fields)} / "
                             f"{struct.calcsize(fmt)} (not a 3.3.5a 12340 table?)")
        self.layout, self.fmt = fields, fmt
        return self

    def columns(self) -> list[str]:
        return [n for n, _ in self.layout]

    def decode(self, rec: bytes) -> list:
        """Values in layout order; strings as str."""
        values = list(struct.unpack(self.fmt, rec))
        return [self.string(v) if t == "string" else v for v, (_, t) in zip(values, self.layout)]

    def encode(self, values: list) -> bytes:
        out = []
        for v, (name, t) in zip(values, self.layout):
            if t == "string":
                out.append(self.intern(v or ""))
            elif t == "float":
                out.append(float(v or 0))
            elif t == "uint":
                out.append(int(v or 0) & 0xFFFFFFFF)
            elif t == "byte":
                out.append(int(v or 0) & 0xFF)
            else:
                v = int(v or 0) & 0xFFFFFFFF
                out.append(v - (1 << 32) if v & 0x80000000 else v)
        return struct.pack(self.fmt, *out)

    # --- strings -----------------------------------------------------------------------------------------
    def string(self, offset: int) -> str:
        if offset <= 0 or offset >= len(self.strings):
            return ""
        end = self.strings.index(b"\0", offset)
        return self.strings[offset:end].decode("utf-8", "replace")

    def intern(self, text: str) -> int:
        if not text:
            return 0
        if text not in self._interned:
            self._interned[text] = len(self.strings)
            self.strings += text.encode("utf-8") + b"\0"
        return self._interned[text]

    # --- rows by id (first field) --------------------------------------------------------------------------
    @staticmethod
    def rid(rec: bytes) -> int:
        return struct.unpack_from("<I", rec)[0]

    def ids(self) -> set[int]:
        return {self.rid(r) for r in self.records}

    def find(self, rid: int) -> bytes | None:
        return next((r for r in self.records if self.rid(r) == rid), None)

    def put(self, rec: bytes):
        """Adds or replaces the record with this id, keeping the file sorted by id."""
        assert len(rec) == self.size
        rid = self.rid(rec)
        self.records = [r for r in self.records if self.rid(r) != rid] + [rec]
        self.records.sort(key=self.rid)

    def words(self, i: int) -> tuple[int, ...]:
        rec = self.records[i]
        return struct.unpack_from(f"<{len(rec) // 4}I", rec)

    def to_bytes(self) -> bytes:
        return (struct.pack("<4s4I", b"WDBC", len(self.records), self.fields, self.size, len(self.strings))
                + b"".join(self.records) + bytes(self.strings))
