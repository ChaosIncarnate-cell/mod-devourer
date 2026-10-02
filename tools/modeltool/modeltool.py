#!/usr/bin/env python3
r"""modeltool: look into WotLK (3.3.5a) creature models, see which animation is used for what, re-link animations,
bring models in from other sources, and put the changed files into the client.

    python modeltool.py find  <text>                      creatures / models by name or path
    python modeltool.py anims <model>                     the model's animations, and what plays for each emote
    python modeltool.py link  <model> <anim[,anim...]> <to>  make <anim> play the model's <to-anim> (e.g. EmoteRoar ->
                                                          BattleRoar): adds an alias sequence, as Blizzard does
    python modeltool.py rename <model> <seq#> <anim>      give sequence number <seq#> another animation id
    python modeltool.py reset <model>                     throw away your changes to a model (deletes it from work\)
    python modeltool.py import <model> [--from SOURCE]    copy a model (+ skins, .anim files, textures) into work\
    python modeltool.py work                              what is in work\ (changed / imported files)
    python modeltool.py pack                              put work\ into the client (into patch-Z.MPQ)

<model> is a display id (e.g. 20025), c:<creature entry> (e.g. c:18464), or a model path (Creature\Frog\Frog.m2).
<anim> is a name from AnimationData.dbc (Roar, Attack1H, EmoteTalk ...) or its number.

Sources, lowest priority first: the client's archives in load order (WOW HD CLIENT), then every --from (an MPQ, a
Data folder of MPQs, or a folder of loose files), then work\ (your changed files always win).

Changes never touch the client directly: link/rename/import write into work\<model path>; `pack` merges work\ into
the client's Data\patch-Z.MPQ (the top patch, so it beats the HD patches; a backup is kept). The Devourer's client
patch tool rebuilds patch-Z from scratch: run `pack` again after it.
"""
from __future__ import annotations

import argparse
import os
import datetime
import shutil
import struct
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
# Z:\ChromaticawBots: first parent folder that holds the game client (env CHROMATICAW_ROOT overrides)
ROOT = Path(os.environ.get("CHROMATICAW_ROOT") or next(
    (p for p in HERE.parents if (p / "WOW HD CLIENT").is_dir()), Path(r"Z:\ChromaticawBots")))
CLIENT_TOOLS = HERE.parent / "client"                        # mod-devourer/tools/client
sys.path.insert(0, str(CLIENT_TOOLS))

import mpq                                                   # noqa: E402
from build_client_patch import Folder, Layers, MpqSource, client_archives, coa_layers, detect_locale  # noqa: E402
from dbc import Dbc                                          # noqa: E402

CLIENT = ROOT / "WOW HD CLIENT"
WORK = HERE / "work"
STAGING = HERE / "staging"
PATCH = "patch-Z.MPQ"
MYSQL = ROOT / "mysql" / "bin" / "mysql.exe"

SEQ_SIZE = 64
F_IN_MODEL, F_ALIAS = 0x20, 0x40                         # sequence flags: 0x20 stored in the .m2, 0x40 alias
OFS_SEQUENCES, OFS_LOOKUP, OFS_TEXTURES = 0x1C, 0x24, 0x50
OFS_GLOBALS, OFS_EVENTS = 0x14, 0x100
# Blocks holding animated tracks: (header offset, record size, track offsets in a record or None = search the record).
# Each track has one timestamp/value list per sequence; a new sequence needs one more (empty) list in each.
TRACK_BLOCKS = [
    (0x2C, 88, (16, 36, 56)),                            # bones: translation, rotation, scale
    (0x48, 40, (0, 20)),                                 # colours: colour, alpha
    (0x58, 20, (0,)),                                    # texture weights
    (0x60, 60, (0, 20, 40)),                             # texture transforms
    (0xF0, 40, (20,)),                                   # attachments: animate attached
    (0x108, 156, (16, 36, 56, 76, 96, 116, 136)),       # lights
    (0x110, 100, (16, 48, 80)),                          # cameras: position, target, roll
    (0x120, 176, None),                                  # ribbon emitters
    (0x128, 476, None),                                  # particle emitters
]


# --- sources -------------------------------------------------------------------------------------------------------
def layers(extra: list[str]) -> Layers:
    data = CLIENT / "Data"
    loc = detect_locale(data)
    archives, _ = client_archives(data, loc)
    sources = [MpqSource(a) for a in archives]
    others = coa_layers([Path(p) for p in extra]).sources if extra else []
    work = []
    if STAGING.is_dir():                                 # converted, not imported yet (only for looking at)
        work.append(Folder(STAGING))
        work[-1].label = "staging"
    if WORK.is_dir():
        work.append(Folder(WORK))
        work[-1].label = "work"
    src = Layers(sources + others + work)
    src.client = Layers(sources + work)                 # the tables (DBC) always come from our client
    return src


def raw_dbc(src: Layers, name: str) -> Dbc:
    data = getattr(src, "client", src).read(f"DBFilesClient\\{name}")
    if not data:
        sys.exit(f"{name} not found in the client")
    return Dbc(data, name)


def row(d: Dbc, rec: bytes) -> tuple:
    return struct.unpack_from(f"<{d.fields}I", rec)


class Anims:
    """AnimationData.dbc names and fallbacks, Emotes.dbc + EmotesText.dbc (slash command -> animation)."""

    def __init__(self, src: Layers):
        d = raw_dbc(src, "AnimationData.dbc")
        self.name, self.fallback = {}, {}
        for rec in d.records:
            r = row(d, rec)
            self.name[r[0]] = d.string(r[1])
            self.fallback[r[0]] = r[5]                       # ID, Name, WeaponFlags, BodyFlags, Flags, Fallback
        self.by_name = {n.lower(): i for i, n in self.name.items()}
        e = raw_dbc(src, "Emotes.dbc")
        emote_anim = {row(e, rec)[0]: row(e, rec)[2] for rec in e.records}   # ID, SlashCommand, AnimID
        t = raw_dbc(src, "EmotesText.dbc")
        self.commands = []                                   # (command, anim id)
        for rec in t.records:
            r = row(t, rec)
            anim = emote_anim.get(r[2], 0)                   # ID, Name, EmoteID
            if anim:
                self.commands.append((t.string(r[1]).lower(), anim))

    def id(self, text: str) -> int:
        if text.isdigit():
            return int(text)
        if text.lower() in self.by_name:
            return self.by_name[text.lower()]
        close = [n for n in self.name.values() if text.lower() in n.lower()]
        sys.exit(f"unknown animation '{text}'" + (f"; did you mean: {', '.join(close[:12])}" if close else ""))

    def label(self, anim: int) -> str:
        return f"{self.name.get(anim, '?')} ({anim})"


# --- the model -----------------------------------------------------------------------------------------------------
class Model:
    def __init__(self, path: str, data: bytes):
        if data[:4] != b"MD20":
            sys.exit(f"{path}: not an M2 model")
        if struct.unpack_from("<I", data, 4)[0] != 264:
            sys.exit(f"{path}: version {struct.unpack_from('<I', data, 4)[0]}, only WotLK (264) models are supported")
        self.path, self.b = path, bytearray(data)

    def arr(self, ofs: int) -> tuple[int, int]:
        return struct.unpack_from("<2I", self.b, ofs)

    def sequences(self) -> list[dict]:
        n, o = self.arr(OFS_SEQUENCES)
        out = []
        for i in range(n):
            anim, var, dur, speed, flags = struct.unpack_from("<2HIfI", self.b, o + i * SEQ_SIZE)
            nxt, alias = struct.unpack_from("<hH", self.b, o + i * SEQ_SIZE + 60)
            out.append(dict(i=i, anim=anim, var=var, dur=dur, speed=speed, flags=flags, next=nxt, alias=alias))
        return out

    def lookup(self) -> list[int]:
        n, o = self.arr(OFS_LOOKUP)
        return list(struct.unpack_from(f"<{n}h", self.b, o)) if n else []

    def find(self, anim: int) -> int | None:
        """The sequence the client finds for `anim`: the lookup is a hash table (slot = id % size, then the next
        slots), and the client checks each candidate's id; an alias leads on to the sequence it stands for."""
        table, seqs = self.lookup(), self.sequences()
        idx = None
        if not table:
            idx = next((s["i"] for s in seqs if s["anim"] == anim and s["var"] == 0), None)
        else:
            for k in range(len(table)):
                cand = table[(anim + k) % len(table)]
                if cand < 0:
                    break
                if seqs[cand]["anim"] == anim:
                    idx = cand
                    break
        seen = set()
        while idx is not None and seqs[idx]["flags"] & F_ALIAS and idx not in seen:
            seen.add(idx)
            idx = seqs[idx]["alias"]
        return idx

    def rebuild_lookup(self):
        """The hash table again, from every first variation (same size unless it gets too full)."""
        firsts = [s for s in self.sequences() if s["var"] == 0]
        size = max(len(self.lookup()), 1)
        while size < len(firsts) * 3 // 2 + 1:
            size = size * 2 + 1
        table = [-1] * size
        for s in firsts:
            slot = s["anim"] % size
            while table[slot] >= 0:
                slot = (slot + 1) % size
            table[slot] = s["i"]
        n, o = self.arr(OFS_LOOKUP)
        if size <= n:
            struct.pack_into(f"<{size}h", self.b, o, *table)
            struct.pack_into("<I", self.b, OFS_LOOKUP, size)
        else:
            struct.pack_into("<2I", self.b, OFS_LOOKUP, size, self.append(struct.pack(f"<{size}h", *table)))

    def append(self, data: bytes) -> int:
        while len(self.b) % 16:
            self.b.append(0)
        o = len(self.b)
        self.b += data
        return o

    def tracks(self) -> list[tuple[int, bool]]:
        """Every animated track with one list per sequence: (offset, has values). Events have timestamps only."""
        nseq = self.arr(OFS_SEQUENCES)[0]
        size = len(self.b)

        def is_track(o):
            if o + 20 > size:
                return False
            interp, gseq, tn, to, vn, vo = struct.unpack_from("<Hh4I", self.b, o)
            return interp <= 3 and tn == vn == nseq and 0 < to < size and 0 < vo < size and to != vo

        out = []
        for hdr, rec, offsets in TRACK_BLOCKS:
            n, base = self.arr(hdr)
            for r in range(n):
                start = base + r * rec
                if offsets is None:
                    out += [(o, True) for o in range(start, start + rec - 19, 2) if is_track(o)]
                else:
                    out += [(start + t, True) for t in offsets if is_track(start + t)]
        n, base = self.arr(OFS_EVENTS)
        for r in range(n):
            o = base + r * 36 + 24
            interp, gseq, tn, to = struct.unpack_from("<Hh2I", self.b, o)
            if tn == nseq and 0 < to < size:
                out.append((o, False))
        return sorted(set(out))

    def add_sequence(self, seq: bytes):
        """Append a sequence; every per-sequence track gets an empty list for it."""
        found = self.tracks()
        for o, values in found:
            for a in ((o + 4, o + 12) if values else (o + 4,)):
                n, ofs = struct.unpack_from("<2I", self.b, a)
                lists = bytes(self.b[ofs:ofs + n * 8]) + struct.pack("<2I", 0, 0)
                struct.pack_into("<2I", self.b, a, n + 1, self.append(lists))
        n, o = self.arr(OFS_SEQUENCES)
        data = bytes(self.b[o:o + n * SEQ_SIZE]) + seq
        struct.pack_into("<2I", self.b, OFS_SEQUENCES, n + 1, self.append(data))
        return len(found)

    def textures(self) -> list[tuple[int, str]]:
        n, o = self.arr(OFS_TEXTURES)
        out = []
        for i in range(n):
            kind, _, ln, no = struct.unpack_from("<4I", self.b, o + i * 16)
            out.append((kind, self.b[no:no + ln].split(b"\0")[0].decode("latin-1") if kind == 0 and ln > 1 else ""))
        return out

    def companions(self) -> list[str]:
        base = self.path[:-3]
        out = [f"{base}{i:02d}.skin" for i in range(min(struct.unpack_from("<I", self.b, 0x44)[0], 4))]
        out += [f"{base}{s['anim']:04d}-{s['var']:02d}.anim" for s in self.sequences()
                if not s["flags"] & F_IN_MODEL and not s["flags"] & F_ALIAS]
        out += [name for kind, name in self.textures() if name]
        return out

    def plays(self, anims: Anims, anim: int) -> tuple[int | None, list[int]]:
        """The sequence the client plays for `anim` (then the AnimationData fallbacks), and the path it took."""
        path, seen = [anim], set()
        while anim not in seen:
            seen.add(anim)
            idx = self.find(anim)
            if idx is not None:
                return idx, path
            anim = anims.fallback.get(anim, 0)
            path.append(anim)
        return None, path


def resolve(src: Layers, spec: str) -> tuple[str, list[str]]:
    """A model path, and notes on which display / creature it came from."""
    notes = []
    display = None
    if spec.lower().startswith("c:"):
        entry = int(spec[2:])
        out = sql(f"SELECT m.CreatureDisplayID, t.name FROM creature_template t JOIN creature_template_model m "
                  f"ON m.CreatureID = t.entry WHERE t.entry = {entry} ORDER BY m.Idx")
        if not out:
            sys.exit(f"creature {entry}: not found (or MySQL is off)")
        display = int(out[0][0])
        notes.append(f"creature {entry} {out[0][1]} -> display {display}")
    elif spec.isdigit():
        display = int(spec)
    if display is None:
        path = spec.replace("/", "\\")
        return (path[:-4] + ".m2" if path.lower().endswith((".mdx", ".mdl")) else path), notes
    cdi = raw_dbc(src, "CreatureDisplayInfo.dbc")
    rec = next((r for r in cdi.records if Dbc.rid(r) == display), None)
    if not rec:
        sys.exit(f"display {display}: not in CreatureDisplayInfo.dbc")
    r = row(cdi, rec)
    model_id, scale = r[1], struct.unpack_from("<f", rec, 16)[0]
    textures = [cdi.string(x) for x in r[6:9] if x]
    cmd = raw_dbc(src, "CreatureModelData.dbc")
    mrec = next((m for m in cmd.records if Dbc.rid(m) == model_id), None)
    if not mrec:
        sys.exit(f"display {display}: model {model_id} not in CreatureModelData.dbc")
    name = cmd.string(row(cmd, mrec)[2])
    notes.append(f"display {display}: model data {model_id}, display scale {scale:g}, skins {', '.join(textures) or '-'}")
    return name[:-4] + ".m2", notes


def load(src: Layers, spec: str) -> tuple[Model, list[str]]:
    path, notes = resolve(src, spec)
    data = src.read(path)
    if not data:
        sys.exit(f"{path}: not found in any source")
    notes.append(f"{path} (from {src.origin(path)})")
    return Model(path, data), notes


def sql(query: str) -> list[list[str]]:
    if not MYSQL.exists():
        return []
    r = subprocess.run([str(MYSQL), "-uacore", "-pacore", "-h127.0.0.1", "acore_world", "-N", "-B", "-e", query],
                       capture_output=True, text=True)
    return [line.split("\t") for line in r.stdout.splitlines() if line]


def save(model: Model):
    out = WORK / model.path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(bytes(model.b))
    print(f"saved: work\\{model.path}   (run `pack` to put it into the client)")


# --- commands ------------------------------------------------------------------------------------------------------
def cmd_find(a, src):
    text = " ".join(a.text)
    rows = sql("SELECT t.entry, t.name, m.CreatureDisplayID FROM creature_template t JOIN creature_template_model m "
               f"ON m.CreatureID = t.entry WHERE t.name LIKE '%{text.replace(chr(39), '')}%' ORDER BY t.name LIMIT 40")
    if rows:
        print("creatures (entry, name, display):")
        for e, n, d in rows:
            print(f"  c:{e:<8} {n:<40} display {d}")
    cmd = raw_dbc(src, "CreatureModelData.dbc")
    hits = [(Dbc.rid(r), cmd.string(row(cmd, r)[2])) for r in cmd.records]
    hits = [(i, n) for i, n in hits if text.lower() in n.lower()][:40]
    if hits:
        cdi = raw_dbc(src, "CreatureDisplayInfo.dbc")
        displays = {}
        for r in cdi.records:
            displays.setdefault(row(cdi, r)[1], []).append(Dbc.rid(r))
        print("models (path, its displays):")
        for i, n in hits:
            print(f"  {n:<60} displays {', '.join(map(str, displays.get(i, [])[:8])) or '-'}")
    if not rows and not hits:
        print("nothing found")


def cmd_anims(a, src):
    anims = Anims(src)
    model, notes = load(src, a.model)
    print("\n".join(notes))
    seqs = model.sequences()
    table = model.lookup()
    print(f"\n{len(seqs)} sequences (# = sequence number for `rename`):")
    for s in seqs:
        flags = []
        if s["flags"] & F_ALIAS:
            flags.append(f"alias of #{s['alias']}")
        if not s["flags"] & F_IN_MODEL and not s["flags"] & F_ALIAS:
            flags.append(".anim file")
        if s["next"] >= 0:
            flags.append(f"next variation #{s['next']}")
        print(f"  #{s['i']:<3} {anims.label(s['anim']):<32} var {s['var']}  {s['dur']:>6} ms  {' '.join(flags)}")
    linked = [s for s in seqs if s["flags"] & F_ALIAS]
    if linked:
        print("\nlinked (an alias plays another sequence):")
        for s in linked:
            target = model.find(s["anim"])
            print(f"  {anims.label(s['anim']):<32} -> " + (f"#{target} {anims.label(seqs[target]['anim'])}"
                                                           if target is not None else "?"))
    print("\nemotes (/command -> animation -> what this model plays):")
    for command, anim in sorted(set(anims.commands)):
        idx, path = model.plays(anims, anim)
        got = f"#{idx} {anims.label(seqs[idx]['anim'])}" if idx is not None else "NOTHING (the model has none of them)"
        via = f"  (via {' -> '.join(anims.name.get(p, str(p)) for p in path)})" if len(path) > 1 else ""
        if a.all or idx is None or seqs[idx]["anim"] != anim:
            print(f"  /{command:<14} {anims.label(anim):<26} {got}{via}")
    if not a.all:
        print("  (emotes with their own animation in this model are not listed; --all lists every emote)")
    print("\ntextures:", ", ".join(n or f"skin slot (type {k})" for k, n in model.textures()))


def link_into(model: Model, anims: Anims, anim: int, target: int) -> str:
    """Make `anim` play the model's `target` (an alias sequence); raises ValueError when it cannot."""
    seqs = model.sequences()
    idx = model.find(target)
    if idx is None:
        raise ValueError(f"the model has no {anims.label(target)}")
    own = next((s for s in seqs if s["anim"] == anim and s["var"] == 0), None)
    o = model.arr(OFS_SEQUENCES)[1]
    if own and own["flags"] & F_ALIAS:                   # already an alias: just point it elsewhere
        struct.pack_into("<H", model.b, o + own["i"] * SEQ_SIZE + 62, idx)
        return f"{anims.label(anim)} now plays #{idx} {anims.label(target)}"
    if own:
        raise ValueError(f"{anims.label(anim)} has its own sequence (#{own['i']}): rename it first, or leave it")
    new = len(seqs)
    seq = bytearray(model.b[o + idx * SEQ_SIZE:o + (idx + 1) * SEQ_SIZE])
    struct.pack_into("<2H", seq, 0, anim, 0)
    struct.pack_into("<I", seq, 12, struct.unpack_from("<I", seq, 12)[0] | F_ALIAS)
    struct.pack_into("<hH", seq, 60, -1, seqs[idx]["alias"])     # joins the target's ring of aliases
    struct.pack_into("<H", model.b, o + idx * SEQ_SIZE + 62, new)
    model.add_sequence(bytes(seq))
    model.rebuild_lookup()
    if model.find(anim) != idx:
        raise ValueError("internal check failed: the new link does not resolve")
    return f"{anims.label(anim)} now plays #{idx} {anims.label(target)} (new alias sequence #{new})"


def cmd_link(a, src):
    """`anim` may be several, comma-separated: all of them play `target`; the model is saved once."""
    anims = Anims(src)
    model, _ = load(src, a.model)
    target = anims.id(a.target)
    done = 0
    for name in [x.strip() for x in str(a.anim).split(",") if x.strip()]:
        try:
            print(link_into(model, anims, anims.id(name), target))
            done += 1
        except ValueError as e:
            print(f"skipped: {e}")
    if not done:
        sys.exit("nothing linked")
    save(model)


def cmd_rename(a, src):
    anims = Anims(src)
    model, _ = load(src, a.model)
    seqs = model.sequences()
    if not 0 <= a.seq < len(seqs):
        sys.exit(f"no sequence #{a.seq} (0-{len(seqs) - 1})")
    s, new = seqs[a.seq], anims.id(a.anim)
    if any(x["anim"] == new and x["var"] == s["var"] for x in seqs):
        sys.exit(f"the model already has {anims.label(new)} variation {s['var']}: rename that one first")
    if not s["flags"] & F_IN_MODEL and not s["flags"] & F_ALIAS:   # its keyframes live in a .anim file named after it
        base = model.path[:-3]
        old_file, new_file = f"{base}{s['anim']:04d}-{s['var']:02d}.anim", f"{base}{new:04d}-{s['var']:02d}.anim"
        data = src.read(old_file)
        if not data:
            sys.exit(f"{old_file} not found: cannot move the sequence's keyframes")
        (WORK / new_file).parent.mkdir(parents=True, exist_ok=True)
        (WORK / new_file).write_bytes(data)
        print(f"keyframes copied: work\\{new_file}")
    for x in seqs:                                       # its other variations follow it
        if x["anim"] == s["anim"]:
            struct.pack_into("<H", model.b, model.arr(OFS_SEQUENCES)[1] + x["i"] * SEQ_SIZE, new)
    model.rebuild_lookup()
    print(f"#{a.seq}: {anims.label(s['anim'])} -> {anims.label(new)}")
    save(model)


def cmd_reset(a, src):
    path, _ = resolve(src, a.model)
    target = WORK / path
    if not target.exists():
        sys.exit(f"work\\{path}: nothing to reset")
    target.unlink()
    print(f"removed work\\{path}; `pack` again to take it out of the client too (the original comes back)")


def cmd_import(a, src):
    model, notes = load(src, a.model)
    print("\n".join(notes))
    files = [model.path] + model.companions()
    copied = 0
    for name in files:
        target = WORK / name
        if target.exists():
            print(f"  kept   work\\{name} (already there, maybe changed)")
            continue
        data = src.read(name)
        if not data:
            print(f"  MISSING {name}")
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        copied += 1
        print(f"  copied {name}  (from {src.origin(name)})")
    print(f"{copied} files into work\\. Skins named in CreatureDisplayInfo (creature colours) are not copied: "
          "they come with the display, see `anims`.")


def cmd_work(a, src):
    files = sorted(p for p in WORK.rglob("*") if p.is_file()) if WORK.is_dir() else []
    if not files:
        print("work\\ is empty")
    for p in files:
        print(f"  {p.relative_to(WORK)}  ({p.stat().st_size // 1024} KB)")


def cmd_pack(a, src):
    import forms
    import imports
    files = {str(p.relative_to(WORK)): p.read_bytes() for p in WORK.rglob("*") if p.is_file()} if WORK.is_dir() else {}
    if not files and not imports.load_imports() and not forms.edits_file():
        sys.exit("work\\ is empty and no form was edited: nothing to pack")
    target = CLIENT / "Data" / PATCH
    running = subprocess.run(["tasklist", "/FI", "IMAGENAME eq wow.exe"], capture_output=True, text=True).stdout
    if "wow.exe" in running.lower():
        sys.exit("WoW is running and keeps the patch locked: close WoW, then run `pack` again (the work folder is kept)")
    content = {}
    if target.exists():
        with mpq.Archive(target) as old:
            for name in old.names():
                content[name] = old.read(name)
        backups = CLIENT / "Devourer patch backups"
        backups.mkdir(exist_ok=True)
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        shutil.copy2(target, backups / f"{PATCH[:-4]}.before-modeltool-{stamp}.MPQ")
    lower = {k.lower(): k for k in content}
    for name, data in files.items():
        content.pop(lower.get(name.lower(), name), None)
        content[name] = data
    added = imports.apply_to_client(content, src, raw_dbc)
    forms_note = forms.apply_to_client(content, src)          # the Devourer's spells, edited animations, own icons
    temp = target.with_name(PATCH + ".new")
    mpq.write_archive(temp, content)
    temp.replace(target)
    print(f"{len(files)} files from work\\ put into {target} ({len(content)} files in it)"
          + (f", {added} imported displays in its creature tables" if added else "") + ".")
    print(forms_note)
    if added:
        print(imports.apply_to_server(src, raw_dbc, MYSQL))
    print(forms.apply_to_server(MYSQL))
    print("Delete the client's Cache folder if a change does not show.")


def main():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--from", dest="sources", action="append", default=[], metavar="SOURCE",
                        help="another place to read models from (MPQ, Data folder, loose files); repeatable")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    add = sub.add_parser
    sub.add_parser = lambda name, **kw: add(name, parents=[common], **kw)
    p = sub.add_parser("find"); p.add_argument("text", nargs="+")
    p = sub.add_parser("anims"); p.add_argument("model"); p.add_argument("--all", action="store_true")
    p = sub.add_parser("link"); p.add_argument("model"); p.add_argument("anim"); p.add_argument("target")
    p = sub.add_parser("reset"); p.add_argument("model")
    p = sub.add_parser("rename"); p.add_argument("model"); p.add_argument("seq", type=int); p.add_argument("anim")
    p = sub.add_parser("import"); p.add_argument("model")
    sub.add_parser("work")
    sub.add_parser("pack")
    a = ap.parse_args()
    src = layers(a.sources)
    {"find": cmd_find, "anims": cmd_anims, "link": cmd_link, "reset": cmd_reset, "rename": cmd_rename,
     "import": cmd_import, "work": cmd_work, "pack": cmd_pack}[a.cmd](a, src)


if __name__ == "__main__":
    main()
