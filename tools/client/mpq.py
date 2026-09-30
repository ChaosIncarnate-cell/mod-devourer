"""MPQ archives in plain Python: read the 3.3.5a client's archives and write the Devourer's patch.

No StormLib needed. Reads format v1/v2 (everything a 3.3.5a client can load): encrypted hash/block tables,
encrypted files (incl. FIX_KEY), single-unit and sector files, zlib / bzip2 / PKWARE DCL compression.
Writes format v1 with zlib-compressed sectors and a (listfile).

    Archive(path).read("DBFilesClient\\Spell.dbc")  -> bytes or None
    Archive(path).names()                            -> names from the (listfile), if the archive has one
    write_archive(path, {"Interface\\...": bytes, ...})
"""
from __future__ import annotations

import bz2
import struct
import zlib
from pathlib import Path

# --- hashing and encryption ------------------------------------------------------------------------------
_CRYPT = [0] * 0x500


def _init_crypt():
    seed = 0x00100001
    for i1 in range(0x100):
        i2 = i1
        for _ in range(5):
            seed = (seed * 125 + 3) % 0x2AAAAB
            t1 = (seed & 0xFFFF) << 16
            seed = (seed * 125 + 3) % 0x2AAAAB
            t2 = seed & 0xFFFF
            _CRYPT[i2] = t1 | t2
            i2 += 0x100


_init_crypt()
HASH_OFFSET, HASH_A, HASH_B, HASH_KEY = 0, 1, 2, 3
M32 = 0xFFFFFFFF


def hash_string(name: str, kind: int) -> int:
    seed1, seed2 = 0x7FED7FED, 0xEEEEEEEE
    for ch in name.upper().replace("/", "\\").encode("latin-1"):
        seed1 = (_CRYPT[(kind << 8) + ch] ^ (seed1 + seed2)) & M32
        seed2 = (ch + seed1 + seed2 + (seed2 << 5) + 3) & M32
    return seed1


def _decrypt(data: bytes, key: int) -> bytes:
    n = len(data) // 4
    if not n:
        return data
    words = struct.unpack_from(f"<{n}I", data)
    out = []
    seed = 0xEEEEEEEE
    for v in words:
        seed = (seed + _CRYPT[0x400 + (key & 0xFF)]) & M32
        ch = v ^ ((key + seed) & M32)
        key = ((((~key) << 0x15) + 0x11111111) & M32) | (key >> 0x0B)
        seed = (ch + seed + (seed << 5) + 3) & M32
        out.append(ch)
    return struct.pack(f"<{n}I", *out) + data[n * 4:]


def _encrypt(data: bytes, key: int) -> bytes:
    n = len(data) // 4
    words = struct.unpack_from(f"<{n}I", data)
    out = []
    seed = 0xEEEEEEEE
    for v in words:
        seed = (seed + _CRYPT[0x400 + (key & 0xFF)]) & M32
        out.append(v ^ ((key + seed) & M32))
        key = ((((~key) << 0x15) + 0x11111111) & M32) | (key >> 0x0B)
        seed = (v + seed + (seed << 5) + 3) & M32
    return struct.pack(f"<{n}I", *out) + data[n * 4:]


# --- PKWARE DCL "explode" (tables from StormLib's pklib/explode.c, MIT licence, (c) Ladislav Zezula) --------
_LEN_BITS = [3, 2, 3, 3, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 7, 7]
_LEN_CODE = [0x05, 0x03, 0x01, 0x06, 0x0A, 0x02, 0x0C, 0x14, 0x04, 0x18, 0x08, 0x30, 0x10, 0x20, 0x40, 0x00]
_EX_LEN_BITS = [0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8]
_LEN_BASE = [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 14, 22, 38, 70, 134, 262]
_DIST_BITS = [2, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7,
              7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8]
_DIST_CODE = [0x03, 0x0D, 0x05, 0x19, 0x09, 0x11, 0x01, 0x3E, 0x1E, 0x2E, 0x0E, 0x36, 0x16, 0x26, 0x06, 0x3A,
              0x1A, 0x2A, 0x0A, 0x32, 0x12, 0x22, 0x42, 0x02, 0x7C, 0x3C, 0x5C, 0x1C, 0x6C, 0x2C, 0x4C, 0x0C,
              0x74, 0x34, 0x54, 0x14, 0x64, 0x24, 0x44, 0x04, 0x78, 0x38, 0x58, 0x18, 0x68, 0x28, 0x48, 0x08,
              0xF0, 0x70, 0xB0, 0x30, 0xD0, 0x50, 0x90, 0x10, 0xE0, 0x60, 0xA0, 0x20, 0xC0, 0x40, 0x80, 0x00]
_CH_BITS_ASC = bytes.fromhex(
    "0b0c0c0c0c0c0c0c0c08070c0c070c0c0c0c0c0c0c0c0c0c0c0c0d0c0c0c0c0c"
    "040a080c0a0c0a08070708090706070807060707070708070708080c0b07090b"
    "0c0607060605070808060b0906070606070b06060607090809090b080b090c08"
    "0c0506060605060606050b0705060505060a05050505080708080a0b0b0c0c0c"
    "0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d"
    "0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c"
    "0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c"
    "0d0c0d0d0d0c0d0d0d0c0d0d0d0d0c0d0d0d0c0c0c0d0d0d0d0d0d0d0d0d0d0d")
_CH_CODE_ASC = [
    0x0490, 0x0FE0, 0x07E0, 0x0BE0, 0x03E0, 0x0DE0, 0x05E0, 0x09E0, 0x01E0, 0x00B8, 0x0062, 0x0EE0, 0x06E0, 0x0022,
    0x0AE0, 0x02E0, 0x0CE0, 0x04E0, 0x08E0, 0x00E0, 0x0F60, 0x0760, 0x0B60, 0x0360, 0x0D60, 0x0560, 0x1240, 0x0960,
    0x0160, 0x0E60, 0x0660, 0x0A60, 0x000F, 0x0250, 0x0038, 0x0260, 0x0050, 0x0C60, 0x0390, 0x00D8, 0x0042, 0x0002,
    0x0058, 0x01B0, 0x007C, 0x0029, 0x003C, 0x0098, 0x005C, 0x0009, 0x001C, 0x006C, 0x002C, 0x004C, 0x0018, 0x000C,
    0x0074, 0x00E8, 0x0068, 0x0460, 0x0090, 0x0034, 0x00B0, 0x0710, 0x0860, 0x0031, 0x0054, 0x0011, 0x0021, 0x0017,
    0x0014, 0x00A8, 0x0028, 0x0001, 0x0310, 0x0130, 0x003E, 0x0064, 0x001E, 0x002E, 0x0024, 0x0510, 0x000E, 0x0036,
    0x0016, 0x0044, 0x0030, 0x00C8, 0x01D0, 0x00D0, 0x0110, 0x0048, 0x0610, 0x0150, 0x0060, 0x0088, 0x0FA0, 0x0007,
    0x0026, 0x0006, 0x003A, 0x001B, 0x001A, 0x002A, 0x000A, 0x000B, 0x0210, 0x0004, 0x0013, 0x0032, 0x0003, 0x001D,
    0x0012, 0x0190, 0x000D, 0x0015, 0x0005, 0x0019, 0x0008, 0x0078, 0x00F0, 0x0070, 0x0290, 0x0410, 0x0010, 0x07A0,
    0x0BA0, 0x03A0, 0x0240, 0x1C40, 0x0C40, 0x1440, 0x0440, 0x1840, 0x0840, 0x1040, 0x0040, 0x1F80, 0x0F80, 0x1780,
    0x0780, 0x1B80, 0x0B80, 0x1380, 0x0380, 0x1D80, 0x0D80, 0x1580, 0x0580, 0x1980, 0x0980, 0x1180, 0x0180, 0x1E80,
    0x0E80, 0x1680, 0x0680, 0x1A80, 0x0A80, 0x1280, 0x0280, 0x1C80, 0x0C80, 0x1480, 0x0480, 0x1880, 0x0880, 0x1080,
    0x0080, 0x1F00, 0x0F00, 0x1700, 0x0700, 0x1B00, 0x0B00, 0x1300, 0x0DA0, 0x05A0, 0x09A0, 0x01A0, 0x0EA0, 0x06A0,
    0x0AA0, 0x02A0, 0x0CA0, 0x04A0, 0x08A0, 0x00A0, 0x0F20, 0x0720, 0x0B20, 0x0320, 0x0D20, 0x0520, 0x0920, 0x0120,
    0x0E20, 0x0620, 0x0A20, 0x0220, 0x0C20, 0x0420, 0x0820, 0x0020, 0x0FC0, 0x07C0, 0x0BC0, 0x03C0, 0x0DC0, 0x05C0,
    0x09C0, 0x01C0, 0x0EC0, 0x06C0, 0x0AC0, 0x02C0, 0x0CC0, 0x04C0, 0x08C0, 0x00C0, 0x0F40, 0x0740, 0x0B40, 0x0340,
    0x0300, 0x0D40, 0x1D00, 0x0D00, 0x1500, 0x0540, 0x0500, 0x1900, 0x0900, 0x0940, 0x1100, 0x0100, 0x1E00, 0x0E00,
    0x0140, 0x1600, 0x0600, 0x1A00, 0x0E40, 0x0640, 0x0A40, 0x0A00, 0x1200, 0x0200, 0x1C00, 0x0C00, 0x1400, 0x0400,
    0x1800, 0x0800, 0x1000, 0x0000]


def _prefix_table(codes, bits) -> dict[tuple[int, int], int]:
    """Codes are read least significant bit first: (bit count, value of those bits) -> symbol."""
    return {(b, c & ((1 << b) - 1)): sym for sym, (c, b) in enumerate(zip(codes, bits))}


_LEN_TABLE = _prefix_table(_LEN_CODE, _LEN_BITS)
_DIST_TABLE = _prefix_table(_DIST_CODE, _DIST_BITS)
_ASC_TABLE = _prefix_table(_CH_CODE_ASC, _CH_BITS_ASC)


class _Bits:
    def __init__(self, data: bytes, pos: int):
        self.data, self.bit = data, pos * 8

    def read(self, n: int) -> int:
        v = 0
        for i in range(n):
            byte = self.bit >> 3
            if byte >= len(self.data):
                raise EOFError
            v |= ((self.data[byte] >> (self.bit & 7)) & 1) << i
            self.bit += 1
        return v

    def symbol(self, table: dict, max_bits: int = 16) -> int:
        v = 0
        for n in range(1, max_bits + 1):
            v |= self.read(1) << (n - 1)
            if (n, v) in table:
                return table[(n, v)]
        raise ValueError("PKWARE: bad code")


def explode(data: bytes) -> bytes:
    if len(data) < 3:
        raise ValueError("PKWARE: too short")
    ctype, dict_bits = data[0], data[1]
    if ctype not in (0, 1) or not 4 <= dict_bits <= 6:
        raise ValueError("PKWARE: bad header")
    bits = _Bits(data, 2)
    out = bytearray()
    try:
        while True:
            if bits.read(1) == 0:
                out.append(bits.read(8) if ctype == 0 else bits.symbol(_ASC_TABLE))
                continue
            code = bits.symbol(_LEN_TABLE)
            length = _LEN_BASE[code] + (bits.read(_EX_LEN_BITS[code]) if _EX_LEN_BITS[code] else 0)
            if length == 0x205:                       # end of stream
                break
            length += 2
            d = bits.symbol(_DIST_TABLE)
            dist = ((d << 2) | bits.read(2)) if length == 2 else ((d << dict_bits) | bits.read(dict_bits))
            start = len(out) - dist - 1
            if start < 0:
                raise ValueError("PKWARE: distance out of range")
            for i in range(length):                   # may overlap the bytes being written
                out.append(out[start + i])
    except EOFError:
        pass
    return bytes(out)


# --- reading -----------------------------------------------------------------------------------------------
F_IMPLODE, F_COMPRESS, F_ENCRYPTED, F_FIX_KEY = 0x100, 0x200, 0x10000, 0x20000
F_SINGLE_UNIT, F_DELETE_MARKER, F_SECTOR_CRC, F_EXISTS = 0x1000000, 0x2000000, 0x4000000, 0x80000000
C_ZLIB, C_PKWARE, C_BZIP2 = 0x02, 0x08, 0x10


def _decompress(data: bytes) -> bytes:
    mask, data = data[0], data[1:]
    if mask & ~(C_ZLIB | C_PKWARE | C_BZIP2):
        raise ValueError(f"unsupported MPQ compression 0x{mask:02X}")
    if mask & C_BZIP2:
        data = bz2.decompress(data)
    if mask & C_PKWARE:
        data = explode(data)
    if mask & C_ZLIB:
        data = zlib.decompress(data)
    return data


class Archive:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.f = open(self.path, "rb")
        self.base = self._find_header()
        f = self.f
        f.seek(self.base)
        (_, header_size, _, version, shift, hash_pos, block_pos, hash_count,
         block_count) = struct.unpack("<4sIIHHIIII", f.read(32))
        self.sector = 512 << shift
        hi_block_pos = hash_hi = block_hi = 0
        if version >= 1 and header_size >= 44:
            hi_block_pos, hash_hi, block_hi = struct.unpack("<QHH", f.read(12))
        self.hash = self._table(hash_pos | (hash_hi << 32), hash_count, "(hash table)")
        self.block = self._table(block_pos | (block_hi << 32), block_count, "(block table)")
        self.block_hi = [0] * block_count
        if hi_block_pos:
            f.seek(self.base + hi_block_pos)
            self.block_hi = list(struct.unpack(f"<{block_count}H", f.read(block_count * 2)))
        self.hash_mask = hash_count - 1

    def _find_header(self) -> int:
        f = self.f
        pos = 0
        size = self.path.stat().st_size
        while pos < size:
            f.seek(pos)
            magic = f.read(4)
            if magic == b"MPQ\x1a":
                return pos
            if magic == b"MPQ\x1b":
                _, header_offset = struct.unpack("<II", f.read(8))
                f.seek(pos + header_offset)
                if f.read(4) == b"MPQ\x1a":
                    return pos + header_offset
            pos += 512
        raise ValueError(f"{self.path}: not an MPQ archive")

    def _table(self, pos: int, count: int, key_name: str) -> list[tuple[int, int, int, int]]:
        self.f.seek(self.base + pos)
        raw = _decrypt(self.f.read(count * 16), hash_string(key_name, HASH_KEY))
        return [struct.unpack_from("<4I", raw, i * 16) for i in range(len(raw) // 16)]

    def close(self):
        self.f.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def _find(self, name: str) -> int | None:
        if not self.hash:
            return None
        start = hash_string(name, HASH_OFFSET) & self.hash_mask
        a, b = hash_string(name, HASH_A), hash_string(name, HASH_B)
        found = None
        i = start
        while True:
            h = self.hash[i]
            block = h[3]
            if block == 0xFFFFFFFF:
                break
            if h[0] == a and h[1] == b and block < len(self.block):
                locale = h[2] & 0xFFFF
                if locale == 0:
                    return block
                if found is None:
                    found = block
            i = (i + 1) & self.hash_mask
            if i == start:
                break
        return found

    def has(self, name: str) -> bool:
        block = self._find(name)
        return block is not None and self.block[block][3] & F_EXISTS and not self.block[block][3] & F_DELETE_MARKER

    def read(self, name: str) -> bytes | None:
        block = self._find(name)
        if block is None:
            return None
        pos, csize, size, flags = self.block[block]
        if not flags & F_EXISTS or flags & F_DELETE_MARKER:
            return None
        if size == 0:
            return b""
        offset = self.base + (pos | (self.block_hi[block] << 32))
        self.f.seek(offset)
        raw = self.f.read(csize)
        key = 0
        if flags & F_ENCRYPTED:
            key = hash_string(name.replace("/", "\\").split("\\")[-1], HASH_KEY)
            if flags & F_FIX_KEY:
                key = ((key + pos) ^ size) & M32
        if flags & F_SINGLE_UNIT:
            if flags & F_ENCRYPTED:
                raw = _decrypt(raw, key)
            if csize < size:
                raw = explode(raw) if flags & F_IMPLODE else _decompress(raw) if flags & F_COMPRESS else raw
            return raw[:size]
        count = (size + self.sector - 1) // self.sector
        compressed = flags & (F_COMPRESS | F_IMPLODE)
        if compressed:
            n = count + 1 + (1 if flags & F_SECTOR_CRC else 0)
            table = raw[:n * 4]
            if flags & F_ENCRYPTED:
                table = _decrypt(table, (key - 1) & M32)
            offsets = struct.unpack(f"<{n}I", table)[:count + 1]
        else:
            offsets = [min(i * self.sector, csize) for i in range(count + 1)]
        out = bytearray()
        for i in range(count):
            chunk = raw[offsets[i]:offsets[i + 1]]
            if flags & F_ENCRYPTED:
                chunk = _decrypt(chunk, (key + i) & M32)
            want = min(self.sector, size - i * self.sector)
            if compressed and len(chunk) < want:
                chunk = explode(chunk) if flags & F_IMPLODE else _decompress(chunk)
            out += chunk
        return bytes(out[:size])

    def names(self) -> list[str]:
        data = self.read("(listfile)")
        if not data:
            return []
        text = data.decode("latin-1").replace("\r", "\n").replace(";", "\n")
        return [n.strip() for n in text.split("\n") if n.strip() and self.has(n.strip())]


# --- writing -----------------------------------------------------------------------------------------------
def write_archive(path: str | Path, files: dict[str, bytes], sector_shift: int = 3):
    """A v1 archive: every file zlib-compressed in sectors (stored as is when that is not smaller)."""
    names = sorted(files, key=str.lower)
    listfile = "\r\n".join(names).encode("latin-1") + b"\r\n"
    entries = [(n.replace("/", "\\"), files[n]) for n in names] + [("(listfile)", listfile)]
    sector = 512 << sector_shift
    hash_count = 16
    while hash_count < len(entries) * 2:
        hash_count *= 2

    body = bytearray()
    blocks = []
    offset = 32
    for name, data in entries:
        count = max(1, (len(data) + sector - 1) // sector)
        chunks = []
        for i in range(count):
            part = data[i * sector:(i + 1) * sector]
            packed = b"\x02" + zlib.compress(part, 9)
            chunks.append(packed if len(packed) < len(part) else part)
        table_size = (count + 1) * 4
        offsets = [table_size]
        for c in chunks:
            offsets.append(offsets[-1] + len(c))
        blob = struct.pack(f"<{count + 1}I", *offsets) + b"".join(chunks)
        blocks.append((offset + len(body), len(blob), len(data), F_EXISTS | F_COMPRESS))
        body += blob

    hash_table = [(M32, M32, M32, M32)] * hash_count      # empty slot: every field 0xFFFFFFFF
    for index, (name, _) in enumerate(entries):
        i = hash_string(name, HASH_OFFSET) & (hash_count - 1)
        while hash_table[i][3] != M32:
            i = (i + 1) & (hash_count - 1)
        hash_table[i] = (hash_string(name, HASH_A), hash_string(name, HASH_B), 0, index)   # locale 0, platform 0
    hash_raw = b"".join(struct.pack("<4I", *h) for h in hash_table)
    block_raw = b"".join(struct.pack("<4I", *b) for b in blocks)
    hash_pos = 32 + len(body)
    block_pos = hash_pos + len(hash_raw)
    total = block_pos + len(block_raw)
    header = struct.pack("<4sIIHHIIII", b"MPQ\x1a", 32, total, 0, sector_shift, hash_pos, block_pos,
                         hash_count, len(blocks))
    Path(path).write_bytes(header + bytes(body)
                           + _encrypt(hash_raw, hash_string("(hash table)", HASH_KEY))
                           + _encrypt(block_raw, hash_string("(block table)", HASH_KEY)))
