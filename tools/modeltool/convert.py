"""Newer WoW models (wow.export RAW exports: chunked MD21, version 272-274) -> the 3.3.5a client's format (MD20 v264).

The model block inside MD21 is laid out like ours; what changes:
  - the outer chunks go (MD21 keeps its model block; TXID / SFID / AFID tell which files go with it, by file id; the
    .manifest.json wow.export writes next to the model turns those ids into file names)
  - version 264; header flags only those our client knows (tilt x/y, texture combiner combos)
  - textures named by path again (Creature\\<Name>\\<file>.blp); creature skins (types 11-13) stay skins, filled by
    the display's colourings
  - .anim files: the AFM2 chunk header goes (our client reads the keyframes straight from the file)
  - .skin: newer shader codes (0x8000 and up) -> 0, the classic shader picked from the materials
  - materials: blend mode 7 -> 4 (additive), newer flag bits dropped
  - particle emitters: 492 -> 476 bytes, packed gravity unpacked, multi-texture -> first texture; emitters that
    spawn little models are left out; ribbons keep their layout
Returns the converted files under their game paths, the colourings found, and a report of what was changed.
"""
from __future__ import annotations

import json
import struct
from pathlib import Path

KNOWN_FLAGS = 0x1 | 0x2 | 0x8
OFS = dict(name=0x08, flags=0x10, sequences=0x1C, num_skin=0x44, textures=0x50, materials=0x70,
           ribbons=0x120, particles=0x128)


def chunks(data: bytes) -> dict[str, bytes]:
    out, o = {}, 0
    while o + 8 <= len(data):
        tag = data[o:o + 4].decode("latin-1")
        size = struct.unpack_from("<I", data, o + 4)[0]
        out[tag] = data[o + 8:o + 8 + size]
        o += 8 + size
    return out


def colourings(folder: Path, model: str, used: set[str]) -> dict[str, Path]:
    """Creature colourings next to the model: <model>_<colour>.blp (or .png), the textures a skin slot can use."""
    found = {}
    for p in sorted(folder.iterdir()):
        stem = p.stem.lower()
        if p.suffix.lower() not in (".blp", ".png") or not stem.startswith(model.lower() + "_") or p.name.lower() in used:
            continue
        colour = stem[len(model) + 1:]
        if p.suffix.lower() == ".blp" or colour not in found:      # the game's own .blp wins over a .png copy
            found[colour] = p
    return found


PARTICLE_NEW, PARTICLE_OLD = 492, 476
P_FLAGS, P_TEXTURE, P_GEOMETRY, P_RECURSION, P_BLEND, P_TYPE, P_HEAD_TAIL = 4, 22, 24, 32, 40, 44, 45
P_GRAVITY, P_HEAD_CELL, P_TAIL_CELL = 132, 316, 332
PF_COMPRESSED_GRAVITY, PF_MULTI_TEXTURE = 0x800000, 0x10000000


def gravity_float(packed: bytes) -> float:
    """The newer packed gravity (int8 x, int8 y, int16 z: a direction and a strength) as our client's single
    number: how fast particles fall (its downward part)."""
    x, y, z = struct.unpack("<bbh", packed)
    dx, dy = x / 128.0, y / 128.0
    dz = max(0.0, 1.0 - dx * dx - dy * dy) ** 0.5
    mag = z * 0.04238648
    if mag < 0:
        dz, mag = -dz, -mag
    return -(dz * mag)


def convert_particles(md: bytearray, arr, append, anim_bufs: dict) -> list[str]:
    report = []
    n, o = arr(OFS["particles"])
    if n:
        nseq = arr(OFS["sequences"])[0]
        kept, dropped_models, gravity_fixed, multi = [], 0, 0, 0
        for i in range(n):
            rec = bytearray(md[o + i * PARTICLE_NEW:o + i * PARTICLE_NEW + PARTICLE_OLD])
            flags = struct.unpack_from("<I", rec, P_FLAGS)[0]
            if struct.unpack_from("<I", rec, P_GEOMETRY)[0] or struct.unpack_from("<I", rec, P_RECURSION)[0]:
                dropped_models += 1                      # spawns little models: those are not converted
                continue
            if flags & PF_MULTI_TEXTURE:                 # 3 textures packed 5 bits each: keep the first
                tex = struct.unpack_from("<H", rec, P_TEXTURE)[0]
                struct.pack_into("<H", rec, P_TEXTURE, tex & 0x1F)
                multi += 1
            if flags & PF_COMPRESSED_GRAVITY:            # every gravity key, in the model and in the .anim files
                interp, gseq, tn, to, vn, vo = struct.unpack_from("<Hh4I", rec, P_GRAVITY)
                for k in range(vn):
                    c, vofs = struct.unpack_from("<2I", md, vo + k * 8)
                    buf = md if gseq >= 0 or k not in anim_bufs else anim_bufs[k]
                    for j in range(c):
                        at = vofs + j * 4
                        if at + 4 <= len(buf):
                            struct.pack_into("<f", buf, at, gravity_float(bytes(buf[at:at + 4])))
                gravity_fixed += 1
            # the two bytes ours reads as particle type and head/tail hold multi-texture settings in the newer
            # format: a normal particle, head (or tail when only a tail cell track is set)
            head = struct.unpack_from("<I", rec, P_HEAD_CELL)[0]
            tail = struct.unpack_from("<I", rec, P_TAIL_CELL)[0]
            struct.pack_into("<BB", rec, P_TYPE, 0, 1 if tail and not head else 0)
            if rec[P_BLEND] > 4:
                rec[P_BLEND] = 4
            struct.pack_into("<I", rec, P_FLAGS, flags & ~(PF_COMPRESSED_GRAVITY | PF_MULTI_TEXTURE) & 0x0FFFFFFF)
            kept.append(bytes(rec))
        struct.pack_into("<2I", md, OFS["particles"], len(kept), append(b"".join(kept)) if kept else 0)
        report.append(f"{len(kept)} of {n} particle emitters converted to our client's layout"
                      + (f" ({gravity_fixed} with packed gravity unpacked)" if gravity_fixed else "")
                      + (f"; {multi} multi-texture emitters keep their first texture" if multi else ""))
        if dropped_models:
            report.append(f"{dropped_models} emitters that spawn little models left out (not converted yet)")
    if arr(OFS["ribbons"])[0]:
        report.append(f"{arr(OFS['ribbons'])[0]} ribbon trails kept (same layout in both versions)")
    return report


def convert(m2_file: Path, game_name: str) -> dict:
    folder = m2_file.parent
    model = m2_file.stem
    game_dir = f"Creature\\{game_name}"
    report = []
    raw = m2_file.read_bytes()
    if raw[:4] == b"MD20":
        raise ValueError("this is already an old-style model (MD20): open it directly, no conversion needed")
    ch = chunks(raw)
    if "MD21" not in ch:
        raise ValueError("not a model file (no MD21 chunk)")
    if "SKID" in ch:
        raise ValueError("this model keeps its skeleton in a .skel file: not supported yet")
    md = bytearray(ch["MD21"])
    version = struct.unpack_from("<I", md, 4)[0]
    if not 264 <= version <= 274:
        raise ValueError(f"model version {version}: only 264-274 are supported")
    manifest_file = folder / f"{model}.manifest.json"
    manifest = json.loads(manifest_file.read_text(encoding="utf-8")) if manifest_file.exists() else {}
    by_id = {}
    for key in ("textures", "skins", "lodSkins", "anims"):
        for e in manifest.get(key, []):
            by_id[e["fileDataID"]] = e["file"]

    def u32s(tag):
        data = ch.get(tag, b"")
        return list(struct.unpack_from(f"<{len(data) // 4}I", data))

    def arr(o):
        return struct.unpack_from("<2I", md, o)

    def append(data: bytes) -> int:
        while len(md) % 16:
            md.append(0)
        o = len(md)
        md.extend(data)
        return o

    struct.pack_into("<I", md, 4, 264)
    flags = struct.unpack_from("<I", md, OFS["flags"])[0]
    if flags & ~KNOWN_FLAGS:
        report.append(f"header flags {flags:#x} -> {flags & KNOWN_FLAGS:#x} (newer bits our client does not know)")
    struct.pack_into("<I", md, OFS["flags"], flags & KNOWN_FLAGS)

    files: dict[str, bytes] = {}
    # textures
    txid = u32s("TXID")
    n, o = arr(OFS["textures"])
    used = set()
    skin_slots = []
    for i in range(n):
        kind, tflags, ln, no = struct.unpack_from("<4I", md, o + i * 16)
        if kind == 0:
            fid = txid[i] if i < len(txid) else 0
            name = by_id.get(fid)
            if not name and ln > 1:
                name = md[no:no + ln].split(b"\0")[0].decode("latin-1").split("\\")[-1]
            if not name or not (folder / name).exists():
                report.append(f"texture {i}: file id {fid} not exported (it will show white)")
                continue
            used.add(name.lower())
            path = f"{game_dir}\\{name}"
            files[path] = (folder / name).read_bytes()
            text = path.encode("latin-1") + b"\0"
            struct.pack_into("<4I", md, o + i * 16, 0, tflags & 0x3, len(text), append(text))
        elif kind in (11, 12, 13):
            skin_slots.append(kind - 10)
            struct.pack_into("<4I", md, o + i * 16, kind, tflags & 0x3, 0, 0)
        else:
            report.append(f"texture {i}: type {kind} (a player/item texture) left empty")
            struct.pack_into("<4I", md, o + i * 16, kind, tflags & 0x3, 0, 0)
    # the skin texture of a single-texture export is listed in the manifest like a normal texture: not "used"
    found = colourings(folder, model, used)

    # materials
    n, o = arr(OFS["materials"])
    for i in range(n):
        mflags, blend = struct.unpack_from("<2H", md, o + i * 4)
        if blend > 6:
            report.append(f"material {i}: blend mode {blend} -> 4 (additive)")
            blend = 4
        struct.pack_into("<2H", md, o + i * 4, mflags & 0x1F, blend)

    # animations stored outside the model (kept as buffers: the particle gravity below may change them)
    afid = {}
    data = ch.get("AFID", b"")
    for i in range(len(data) // 8):
        anim, sub, fid = struct.unpack_from("<2HI", data, i * 8)
        afid[(anim, sub)] = fid
    n, o = arr(OFS["sequences"])
    anim_bufs = {}                                       # sequence index -> its .anim keyframes
    anim_names = {}
    for i in range(n):
        anim, sub, _, _, sflags = struct.unpack_from("<2HIfI", md, o + i * 64)
        if sflags & 0x20 or sflags & 0x40:
            continue
        name = by_id.get(afid.get((anim, sub), 0)) or f"{model}{anim:04d}-{sub:02d}.anim"
        p = folder / name
        if not p.exists():
            report.append(f"animation {anim}-{sub}: {name} not exported (that animation will not play)")
            continue
        a = p.read_bytes()
        if a[:4] in (b"AFM2", b"AFSA", b"AFSB"):
            parts = chunks(a)
            if "AFSA" in parts or "AFSB" in parts:
                report.append(f"animation {anim}-{sub}: uses a separate skeleton's keyframes (not supported)")
            a = parts.get("AFM2", b"")
        anim_bufs[i] = bytearray(a)
        anim_names[i] = f"{game_dir}\\{game_name}{anim:04d}-{sub:02d}.anim"

    # effects: particle emitters (newer: 492 bytes, ours 476) and ribbons (same layout)
    report += convert_particles(md, arr, append, anim_bufs)
    for i, buf in anim_bufs.items():
        files[anim_names[i]] = bytes(buf)

    # the first .skin (our client uses one level of detail)
    sfid = u32s("SFID")
    skin_name = by_id.get(sfid[0]) if sfid else None
    skin_file = folder / (skin_name or f"{model}00.skin")
    if not skin_file.exists():
        raise ValueError(f"{skin_file.name} not exported: the model cannot be drawn without it")
    skin = bytearray(skin_file.read_bytes())
    tn, to = struct.unpack_from("<2I", skin, 36)
    newer = 0
    for i in range(tn):
        shader = struct.unpack_from("<H", skin, to + i * 24 + 2)[0]
        if shader & 0x8000 or shader > 0x20:
            struct.pack_into("<H", skin, to + i * 24 + 2, 0)
            newer += 1
    if newer:
        report.append(f"{newer} draw calls: newer shader codes -> the classic shader (shine/reflection may look simpler)")
    files[f"{game_dir}\\{game_name}00.skin"] = bytes(skin)
    struct.pack_into("<I", md, OFS["num_skin"], 1)

    path = f"{game_dir}\\{game_name}.m2"
    files[path] = bytes(md)
    bbox = struct.unpack_from("<6f", md, 0xA0)
    return dict(path=path, files=files, report=report, skin_slots=skin_slots,
                colourings={c: str(p) for c, p in found.items()}, bbox=bbox, source=str(m2_file))
