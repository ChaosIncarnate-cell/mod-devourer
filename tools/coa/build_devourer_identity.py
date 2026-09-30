#!/usr/bin/env python3
"""Turns class slot 20 into the Devourer, from CoA's original files.

Nothing of the class that used to live in slot 20 (Son of Arugal / Bloodmage) survives: its specs, talent
trees, resource UI, colours and name are replaced. Only the class *number* stays, because 3.3.5 class masks
are 32 bits wide and all 32 numbers are taken.

    python build_devourer_identity.py --dbc <repack>/Data/dbc --patch-b <client>/Data/patch-B.MPQ \
                                      --icons <folder with Interface/...> --out <folder>

Reads only the originals and writes everything new under --out:
    out/server-dbc/*.dbc            replacements for the server's Data/dbc (same files the client uses)
    out/client/DBFilesClient/*.dbc  the same DBCs for the client patch
    out/client/Interface/...        Lua overrides + class icons
    out/patch-TZ.MPQ                the client patch, ready to copy to <client>/Data (needs StormLib)
Re-run it after a CoA update: the transforms are applied to the new originals.
"""
from __future__ import annotations

import argparse
import re
import shutil
import struct
import subprocess
import sys
from pathlib import Path

CLASS_ID = 20
OLD_TOKEN, NEW_TOKEN = "SONOFARUGAL", "DEVOURER"
OLD_KEY, NEW_KEY = "SonOfArugal", "Devourer"          # CharacterAdvancement class-type key
CLASS_NAME = "Devourer"
CLASS_COLOR = (0.72, 0.47, 0.18)                       # bronze of the emblem

# The three specs take over the old spec ids 25-27; id 99 (Packleader) is removed.
# ChrSpecs fields: 1 class, 2 spec token, 3 icon, 8-10 stats, 11 melee 12 ranged 13 caster 14 tank 15 healer
# 16 support, 17 difficulty, 18-23 power types, 24/25/27 showcase spells, 28 identity entry, 29 name, 46 text.
SPECS = {
    25: dict(token="GLUTTON", name="Glutton", icon="Ability_Druid_DemoralizingRoar",
             stats=("Agility", "Stamina", "None"), roles=(14,), difficulty="Normal",
             text="Devour to grow. Every meal makes you larger and tougher, and what you eat decides how. "
                  "Weak prey is swallowed whole, and its own powers burst out of you."),
    26: dict(token="SKINCHANGER", name="Skinchanger", icon="Spell_Shadow_Charm",
             stats=("Agility", "Intellect", "None"), roles=(11, 13), difficulty="Hard",
             text="Change shapes mid-fight. Every shape you leave behind lingers as a ghostly echo that keeps "
                  "fighting, so a fast shifter fights beside the ghosts of everything it has been."),
    27: dict(token="BROOD", name="Brood", icon="Spell_Shadow_SummonFelHunter",
             stats=("Intellect", "Stamina", "None"), roles=(13,), difficulty="Normal",
             text="Breed the shapes you have eaten. Your hatchlings fight and feed for you, and what they devour "
                  "flows back into their mother."),
}
REMOVED_SPECS = {99}
SHOWCASE_SPELLS = (9100001, 9100100, 0)                 # Devour, Sethrak Form (Devourer module)
# Every spec needs an identity entry in CharacterAdvancement: the client builds it at level 10 and asserts
# ("entry 0 not found") when a spec has none. entry id, passive spell (mod-devourer), icon.
IDENTITY = {
    25: (139001, 9100011, "Bottomless Appetite", "ability_druid_demoralizingroar"),
    26: (139002, 9100012, "Restless Skin", "spell_shadow_charm"),
    27: (139003, 9100013, "Mother of the Brood", "spell_shadow_summonfelhunter"),
}
IDENTITY_TEMPLATE = 4023                                 # a Monk identity passive: free, level 10

LOCALES = 16


# --- DBC ------------------------------------------------------------------------------------------------
class Dbc:
    def __init__(self, path: Path):
        d = path.read_bytes()
        magic, self.n, self.f, self.rs, ss = struct.unpack_from("<4s4I", d)
        assert magic == b"WDBC" and self.rs % 4 == 0, path
        self.dw = self.rs // 4                       # some tables pack byte fields: work in whole dwords
        self.rows = [list(struct.unpack_from(f"<{self.dw}I", d, 20 + i * self.rs)) for i in range(self.n)]
        self.strings = bytearray(d[20 + self.n * self.rs:20 + self.n * self.rs + ss])
        self.cache: dict[str, int] = {}

    def s(self, off: int) -> str | None:
        if off <= 0 or off >= len(self.strings) or self.strings[off - 1] != 0:
            return None
        return self.strings[off:self.strings.find(b"\0", off)].decode("utf-8", "replace")

    def add(self, text: str) -> int:
        if not text:
            return 0
        if text not in self.cache:
            self.cache[text] = len(self.strings)
            self.strings += text.encode("utf-8") + b"\0"
        return self.cache[text]

    def by_id(self, rid: int) -> list[int] | None:
        return next((r for r in self.rows if r[0] == rid), None)

    def save(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        body = b"".join(struct.pack(f"<{self.dw}I", *r) for r in self.rows)
        path.write_bytes(struct.pack("<4s4I", b"WDBC", len(self.rows), self.f, self.rs, len(self.strings))
                         + body + bytes(self.strings))


def set_locales(db: Dbc, row: list[int], first: int, text: str):
    """A localized string: 16 locale slots and a flags dword. enUS is filled, the rest point at it too."""
    off = db.add(text)
    for i in range(LOCALES):
        row[first + i] = off


def build_dbcs(src: Path, out_dirs: list[Path]) -> list[str]:
    report = []

    classes = Dbc(src / "ChrClasses.dbc")
    row = classes.by_id(CLASS_ID)
    for first in (4, 21, 38):                           # name, female name, neutral name
        set_locales(classes, row, first, CLASS_NAME)
    row[55] = classes.add(NEW_TOKEN)
    report.append(f"ChrClasses: class {CLASS_ID} is now '{CLASS_NAME}' ({NEW_TOKEN})")

    specs = Dbc(src / "ChrSpecs.dbc")
    specs.rows = [r for r in specs.rows if not (r[0] in REMOVED_SPECS and specs.s(r[1]) == OLD_TOKEN)]
    for sid, spec in SPECS.items():
        r = specs.by_id(sid)
        assert r and specs.s(r[1]) == OLD_TOKEN, f"spec {sid} is not the old class's"
        r[1] = specs.add(NEW_TOKEN)
        r[2] = specs.add(spec["token"])
        r[3] = specs.add(spec["icon"])
        for i, stat in enumerate(spec["stats"]):
            r[8 + i] = specs.add(stat)
        for field in range(11, 17):
            r[field] = 1 if field in spec["roles"] else 0
        r[17] = specs.add(spec["difficulty"])
        r[18] = specs.add("RAGE")                       # Hunger runs on the rage bar
        for field in range(19, 24):
            r[field] = specs.add("NONE")
        r[24], r[25], _ = SHOWCASE_SPELLS
        r[27] = IDENTITY[sid][1]                        # the spec's passive, shown in the spec chooser
        r[28] = IDENTITY[sid][0]                        # its identity entry in CharacterAdvancement
        r[29] = specs.add(spec["name"])
        set_locales(specs, r, 46, spec["text"])
    report.append(f"ChrSpecs: {', '.join(s['name'] for s in SPECS.values())}; Packleader removed")

    tabs = Dbc(src / "CharacterAdvancementTabTypes.dbc")
    next_id = max(r[0] for r in tabs.rows) + 1
    template = next(r for r in tabs.rows if tabs.s(r[1]) == "Blood")
    for spec in SPECS.values():
        if any(tabs.s(r[1]) == spec["name"] for r in tabs.rows):
            continue
        r = list(template)
        r[0] = next_id
        next_id += 1
        r[1] = r[2] = tabs.add(spec["name"])
        tabs.rows.append(r)
    report.append("CharacterAdvancementTabTypes: talent tabs for the three specs")

    types = Dbc(src / "CharacterAdvancementClassTypes.dbc")
    ctype = next(r for r in types.rows if r[2] == CLASS_ID)
    ctype[1] = types.add(NEW_KEY)
    ctype[6] = types.add(CLASS_NAME)
    type_id = ctype[0]

    adv = Dbc(src / "CharacterAdvancement.dbc")
    before = len(adv.rows)
    adv.rows = [r for r in adv.rows if r[32] != type_id]
    report.append(f"CharacterAdvancement: removed {before - len(adv.rows)} talents of the old class")
    template = adv.by_id(IDENTITY_TEMPLATE)
    assert template, "identity template entry missing"
    tab_by_name = {tabs.s(r[1]): r[0] for r in tabs.rows}
    for sid, (entry, spell, name, icon) in IDENTITY.items():
        r = list(template)
        r[0] = entry
        r[2] = r[3] = r[4] = 0                          # no prerequisites
        r[5] = spell
        for field in range(6, 10):
            r[field] = 0
        r[32] = type_id
        r[33] = tab_by_name[SPECS[sid]["name"]]
        r[47] = adv.add(name)
        r[64] = adv.add(icon)
        adv.rows = [x for x in adv.rows if x[0] != entry] + [r]
    report.append("CharacterAdvancement: an identity passive for each spec")

    for db, name in ((classes, "ChrClasses"), (specs, "ChrSpecs"), (tabs, "CharacterAdvancementTabTypes"),
                     (types, "CharacterAdvancementClassTypes"), (adv, "CharacterAdvancement")):
        for out in out_dirs:
            db.save(out / f"{name}.dbc")
    return report


# --- client Lua -----------------------------------------------------------------------------------------
def lua_block_end(text: str, start: int) -> int:
    """Index just past the '}' that closes the table opened at or after `start` (strings are ignored)."""
    i = text.index("{", start)
    depth = 0
    in_str = None
    while i < len(text):
        c = text[i]
        if in_str:
            if c == "\\":
                i += 2
                continue
            if c == in_str:
                in_str = None
        elif c in "\"'":
            in_str = c
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    raise ValueError("unbalanced table")


def drop_keyed_block(text: str, key: str) -> tuple[str, int]:
    """Removes every  ["key"] = { ... },  entry."""
    count = 0
    pattern = re.compile(r'\n([ \t]*)\["' + re.escape(key) + r'"\]\s*=\s*\{')
    while (m := pattern.search(text)):
        end = lua_block_end(text, m.start())
        if text[end:end + 1] == ",":
            end += 1
        text = text[:m.start()] + text[end:]
        count += 1
    return text, count


def rename(text: str) -> str:
    """Token and key renames; texture paths (\\SonOfArugal...) keep pointing at files that exist."""
    for old, new in ((OLD_TOKEN, NEW_TOKEN), (OLD_KEY, NEW_KEY), (OLD_TOKEN.lower(), NEW_TOKEN.lower())):
        text = re.sub(r"(?<!\\)" + old, new, text)
    return text.replace("CLASS_SON_OF_ARUGAL", "CLASS_DEVOURER")


def transform_lua(path: str, text: str) -> tuple[str, str]:
    name = path.split("\\")[-1]
    notes = []

    if name == "CoATalentNodeData.lua":
        text, n = drop_keyed_block(text, OLD_KEY)
        notes.append(f"old talent trees removed ({n} blocks)")
    elif name == "Ascension_WorgenResource.lua":
        # The old class's resource orb: retired, never loads again.
        text = re.sub(r'if class ~= "' + OLD_TOKEN + r'" then return end', "do return end -- retired with the old class", text)
        notes.append("old resource orb retired")
    elif name == "ClassResources.lua":
        m = re.search(r'\nelseif class == "' + OLD_TOKEN + r'" then\n', text)
        nxt = re.compile(r'\n(elseif class ==|else\n|end\n)').search(text, m.end())
        text = text[:m.start()] + text[nxt.start():]
        notes.append("old resource bar removed")
    elif name == "C_Player.lua":
        text = re.sub(r'elseif class == "' + OLD_TOKEN + r'" then\n(\s*)return C_CharacterAdvancement\.IsKnownID\(\d+\)',
                      r'elseif class == "' + NEW_TOKEN + r'" then\n\1return false -- identity passive not defined yet', text)
        notes.append("identity check neutral")
    elif name == "SharedConstants.lua":
        spec_table = "\n".join(f'\t\t["{s["token"]}"] = "{s["name"]}",' for s in SPECS.values())
        text = re.sub(r'(\["' + OLD_TOKEN + r'"\]\s*=\s*\{\n)(?:\t\t\["[A-Z]+"\][^\n]*\n)+',
                      lambda m: m.group(1) + spec_table + "\n", text, count=1)
        r, g, b = CLASS_COLOR
        text = re.sub(r'(\["' + OLD_TOKEN + r'"\]\s*=\s*)CreateColor\([^)]*\)', rf'\1CreateColor({r:.2f}, {g:.2f}, {b:.2f})', text)
        notes.append("spec names, class colour")
    elif name == "AtlasInfo.lua":
        spec_old = ["packleader", "fleshweaver", "ferocity", "blood"]
        spec_new = {"fleshweaver": "glutton", "blood": "skinchanger", "ferocity": "brood"}
        lines = []
        for line in text.split("\n"):
            low = line.lower()
            if f"-{OLD_TOKEN.lower()}-packleader" in low:
                continue
            for o, n in spec_new.items():
                line = line.replace(f"-{OLD_TOKEN.lower()}-{o}\"", f"-{OLD_TOKEN.lower()}-{n}\"")
            lines.append(line)
        text = "\n".join(lines)
        notes.append("atlas keys for class and specs (art still the old sheets)")

    text = rename(text)
    return text, "; ".join(notes) or "renamed"


def build_lua(patch_b: Path, out: Path, mpq_reader) -> list[str]:
    report = []
    archive = mpq_reader.open_archive(str(patch_b))
    for name, _ in mpq_reader.listing(archive):
        if not name.lower().endswith((".lua", ".xml")):
            continue
        raw = mpq_reader.read(archive, name)
        if not re.search(rb"SONOFARUGAL|SonOfArugal", raw, re.I):
            continue
        text = raw.decode("utf-8", "surrogateescape")
        new, note = transform_lua(name, text)
        leftover = [m for m in re.finditer(r"(?<!\\)(SONOFARUGAL|SonOfArugal|sonofarugal)", new)]
        assert not leftover, f"{name}: old class name left at {leftover[0].start()}"
        dest = out / name.replace("\\", "/")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(new.encode("utf-8", "surrogateescape"))
        if name.lower().endswith(".lua"):
            # WoW accepts a UTF-8 BOM, luac does not: check the text without it.
            body = new.encode("utf-8", "surrogateescape").removeprefix(b"\xef\xbb\xbf")
            check = subprocess.run(["luac5.1", "-p", "-"], input=body, capture_output=True)
            if check.returncode:
                raise SystemExit(f"Lua syntax error in {name}: {check.stderr.decode('latin1')}")
        report.append(f"{name}: {note}")
    return report


def build_mpq(files_root: Path, dest: Path, storm):
    import ctypes
    from ctypes import byref, c_void_p
    L = storm.L
    L.SFileCreateArchive.argtypes = [ctypes.c_char_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(c_void_p)]
    L.SFileAddFileEx.argtypes = [c_void_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
    L.SFileCloseArchive.argtypes = [c_void_p]
    files = [p for p in files_root.rglob("*") if p.is_file()]
    if dest.exists():
        dest.unlink()
    h = c_void_p()
    MPQ_CREATE_ARCHIVE_V2, MPQ_CREATE_LISTFILE, MPQ_CREATE_ATTRIBUTES = 0x01000000, 0x00100000, 0x00200000
    if not L.SFileCreateArchive(str(dest).encode(), MPQ_CREATE_ARCHIVE_V2 | MPQ_CREATE_LISTFILE | MPQ_CREATE_ATTRIBUTES,
                                max(64, len(files) * 2), byref(h)):
        raise SystemExit("cannot create MPQ")
    MPQ_FILE_COMPRESS, MPQ_FILE_REPLACEEXISTING, MPQ_COMPRESSION_ZLIB = 0x200, 0x80000000, 0x02
    for p in files:
        arc = str(p.relative_to(files_root)).replace("/", "\\")
        if not L.SFileAddFileEx(h, str(p).encode(), arc.encode(), MPQ_FILE_COMPRESS | MPQ_FILE_REPLACEEXISTING,
                                MPQ_COMPRESSION_ZLIB, MPQ_COMPRESSION_ZLIB):
            raise SystemExit(f"cannot add {arc}")
    L.SFileCloseArchive(h)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dbc", type=Path, required=True)
    ap.add_argument("--patch-b", type=Path, required=True)
    ap.add_argument("--icons", type=Path)
    ap.add_argument("--extra-client", type=Path, help="more client files to pack (e.g. the module's DBC patch)")
    ap.add_argument("--base-patch", type=Path,
                    help="an MPQ whose files the patch starts from (the package's patch-T: CoA's spells + the module's)")
    ap.add_argument("--patch-name", default="patch-TZ.MPQ",
                    help="patch-T.MPQ for this client: a separate archive loses to patch-T")
    ap.add_argument("--loose-interface", action="store_true",
                    help="write Interface files as loose files (out/interface) instead of packing them")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--mpq-tools", type=Path, default=Path(__file__).parent)
    a = ap.parse_args()
    sys.path.insert(0, str(a.mpq_tools))
    import mpq

    if a.out.exists():
        shutil.rmtree(a.out)
    client = a.out / "client"
    if a.base_patch:
        archive = mpq.open_archive(str(a.base_patch))
        for name, _ in mpq.listing(archive):
            if name.startswith("("):
                continue
            dest = client / name.replace("\\", "/")
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(mpq.read(archive, name))
    if a.extra_client:
        shutil.copytree(a.extra_client, client, dirs_exist_ok=True)
    report = build_dbcs(a.dbc, [a.out / "server-dbc", client / "DBFilesClient"])
    report += build_lua(a.patch_b, client, mpq)
    if a.icons:
        shutil.copytree(a.icons, client, dirs_exist_ok=True)
        report.append("class icons")
    if a.loose_interface:
        shutil.move(str(client / "Interface"), str(a.out / "interface" / "Interface"))
        report.append("interface files kept loose (out/interface)")
    build_mpq(client, a.out / a.patch_name, mpq)
    report.append(f"{a.patch_name} written")
    print("\n".join(" - " + r for r in report))


if __name__ == "__main__":
    main()
