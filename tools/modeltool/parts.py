"""Editing the parts of a model: what you click in the page is one draw call ("batch") of the model's first .skin.

    hide / see-through   a constant texture-weight track (on a global loop) for that batch; opaque materials become
                         alpha-blended so the weight shows
    how it is drawn      the batch gets its own material (blend mode, unlit, two-sided ...)
    texture              which of the model's textures the batch uses
    size                 a bone's scale keys, in every sequence (the .m2, or the sequence's .anim file)
    recolour             hue / saturation / brightness of a texture, the whole texture or only where the part sits on
                         it. A skin texture (types 11-13) becomes a custom skin: its own display id (skins.json)

Edited models are saved with one .skin only (the full-detail one we edited), so the client cannot pick another.
"""
from __future__ import annotations

import io
import json
import struct
from pathlib import Path

import modeltool as mt

HERE = Path(__file__).resolve().parent
SKINS = mt.WORK.parent / "skins.json"                   # next to work\ (a test work folder has its own)
FIRST_SKIN = 1010001
OFS_TEX_WEIGHTS, OFS_MATERIALS, OFS_TEX_LOOKUP, OFS_WEIGHT_LOOKUP, OFS_BONES = 0x58, 0x70, 0x80, 0x90, 0x2C
BONE_SIZE, BONE_TRANSFORMED = 88, 0x200
BLENDS = ["opaque", "cut-out (alpha test)", "see-through (alpha)", "glow, no alpha (add)", "glow (add)",
          "darken (modulate)", "darken 2x (modulate 2x)"]
KEY_BONES = ["ArmL", "ArmR", "ShoulderL", "ShoulderR", "SpineLow", "Waist", "Head", "Jaw", "IndexFingerR",
             "MiddleFingerR", "PinkyFingerR", "RingFingerR", "ThumbR", "IndexFingerL", "MiddleFingerL", "PinkyFingerL",
             "RingFingerL", "ThumbL", "$BTH", "$CSR", "$CSL", "Breath", "Name", "NameMount", "$CHD", "$CCH", "Root"]


class Parts:
    def __init__(self, src, spec: str, editing: bool = True):
        self.src = src
        self.model, _ = mt.load(src, spec)
        self.b = self.model.b
        if editing and "staging" in str(src.origin(self.model.path)).lower():
            raise ValueError("this model is only converted: import it first (step 2), then edit its parts")
        self.skin_path = self.model.path[:-3] + "00.skin"
        skin = src.read(self.skin_path)
        if not skin or skin[:4] != b"SKIN":
            raise ValueError("no .skin file for this model")
        self.skin = bytearray(skin)
        self.anims: dict[str, bytearray] = {}            # .anim files changed (bone sizes)

    # --- arrays --------------------------------------------------------------------------------------------------
    def arr(self, ofs):
        return self.model.arr(ofs)

    def grow(self, ofs: int, rec: bytes) -> int:
        """Append one record to the .m2 array whose header is at `ofs`; returns its index."""
        n, o = self.arr(ofs)
        size = len(rec)
        data = bytes(self.b[o:o + n * size]) + rec
        struct.pack_into("<2I", self.b, ofs, n + 1, self.model.append(data))
        return n

    def batches(self) -> list[int]:
        """Offsets of the batch records in the .skin."""
        n, o = struct.unpack_from("<2I", self.skin, 36)
        return [o + i * 24 for i in range(n)]

    def batch(self, i: int) -> int:
        bs = self.batches()
        if not 0 <= i < len(bs):
            raise ValueError(f"no part #{i}")
        return bs[i]

    # --- reading -----------------------------------------------------------------------------------------------------
    def opacity(self, i: int) -> float:
        combo = struct.unpack_from("<H", self.skin, self.batch(i) + 20)[0]
        n, o = self.arr(OFS_WEIGHT_LOOKUP)
        if combo >= n:
            return 1.0
        w = struct.unpack_from("<h", self.b, o + combo * 2)[0]
        wn, wo = self.arr(OFS_TEX_WEIGHTS)
        if not 0 <= w < wn:
            return 1.0
        _, _, tn, to, vn, vo = struct.unpack_from("<Hh4I", self.b, wo + w * 20)
        for k in range(vn):                              # the first list with a value (in the .m2)
            c, p = struct.unpack_from("<2I", self.b, vo + k * 8)
            if c and p + 2 <= len(self.b):
                return max(0.0, min(1.0, struct.unpack_from("<h", self.b, p)[0] / 32767))
        return 1.0

    def info(self) -> list[dict]:
        mats = self.arr(OFS_MATERIALS)
        out = []
        for i, p in enumerate(self.batches()):
            mat = struct.unpack_from("<H", self.skin, p + 10)[0]
            flags, blend = struct.unpack_from("<2H", self.b, mats[1] + mat * 4) if mat < mats[0] else (0, 0)
            out.append(dict(opacity=round(self.opacity(i), 3), mat=mat, mflags=flags, blendMode=blend))
        return out

    # --- see-through / hide ------------------------------------------------------------------------------------------
    def own_material(self, i: int) -> int:
        """The batch's material, copied first if other batches share it."""
        p = self.batch(i)
        mat = struct.unpack_from("<H", self.skin, p + 10)[0]
        if sum(struct.unpack_from("<H", self.skin, q + 10)[0] == mat for q in self.batches()) > 1:
            n, o = self.arr(OFS_MATERIALS)
            mat = self.grow(OFS_MATERIALS, bytes(self.b[o + mat * 4:o + mat * 4 + 4]))
            struct.pack_into("<H", self.skin, p + 10, mat)
        return mat

    def set_draw(self, i: int, blend: int | None = None, flags: int | None = None):
        mat = self.own_material(i)
        o = self.arr(OFS_MATERIALS)[1] + mat * 4
        old_flags, old_blend = struct.unpack_from("<2H", self.b, o)
        struct.pack_into("<2H", self.b, o, old_flags if flags is None else flags & 0x1F,
                         old_blend if blend is None else max(0, min(6, blend)))

    def set_opacity(self, i: int, value: float):
        value = max(0.0, min(1.0, value))
        p = self.batch(i)
        combo = struct.unpack_from("<H", self.skin, p + 20)[0]
        ln, lo = self.arr(OFS_WEIGHT_LOOKUP)
        wn, wo = self.arr(OFS_TEX_WEIGHTS)
        mine = None                                      # a constant track only this batch uses: just change it
        if combo < ln and sum(struct.unpack_from("<H", self.skin, q + 20)[0] == combo for q in self.batches()) == 1:
            w = struct.unpack_from("<h", self.b, lo + combo * 2)[0]
            if 0 <= w < wn and sum(struct.unpack_from("<h", self.b, lo + k * 2)[0] == w for k in range(ln)) == 1:
                interp, gseq, tn, to, vn, vo = struct.unpack_from("<Hh4I", self.b, wo + w * 20)
                if gseq >= 0 and tn == vn == 1 and struct.unpack_from("<I", self.b, vo)[0] == 1:
                    mine = struct.unpack_from("<2I", self.b, vo)[1]
        if mine is not None:
            struct.pack_into("<h", self.b, mine, round(value * 32767))
        else:
            gseq = self.grow(mt.OFS_GLOBALS, struct.pack("<I", 1000))      # a 1 s loop of its own
            t = self.model.append(struct.pack("<I", 0))
            v = self.model.append(struct.pack("<h", round(value * 32767)))
            tl = self.model.append(struct.pack("<2I", 1, t))
            vl = self.model.append(struct.pack("<2I", 1, v))
            w = self.grow(OFS_TEX_WEIGHTS, struct.pack("<Hh4I", 0, gseq, 1, tl, 1, vl))
            combo = self.grow(OFS_WEIGHT_LOOKUP, struct.pack("<h", w))
            struct.pack_into("<H", self.skin, p + 20, combo)
        mats = self.arr(OFS_MATERIALS)
        mat = struct.unpack_from("<H", self.skin, p + 10)[0]
        if value < 1 and mat < mats[0] and struct.unpack_from("<H", self.b, mats[1] + mat * 4 + 2)[0] in (0, 1):
            self.set_draw(i, blend=2)                    # opaque ignores the weight: blend it
        return value

    # --- texture -------------------------------------------------------------------------------------------------------
    def set_texture(self, i: int, tex: int):
        n = self.arr(mt.OFS_TEXTURES)[0]
        if not 0 <= tex < n:
            raise ValueError(f"no texture #{tex}")
        p = self.batch(i)
        ln, lo = self.arr(OFS_TEX_LOOKUP)
        k = next((k for k in range(ln) if struct.unpack_from("<h", self.b, lo + k * 2)[0] == tex), None)
        if k is None:
            k = self.grow(OFS_TEX_LOOKUP, struct.pack("<h", tex))
        struct.pack_into("<H", self.skin, p + 16, k)

    def rename_texture(self, tex: int, path: str):
        """Point a fixed texture (type 0) at another file."""
        o = self.arr(mt.OFS_TEXTURES)[1] + tex * 16
        text = path.encode("latin-1") + b"\0"
        struct.pack_into("<2I", self.b, o + 8, len(text), self.model.append(text))

    # --- size: a bone's scale ------------------------------------------------------------------------------------------
    def anim_buf(self, s: dict) -> bytearray:
        name = f"{self.model.path[:-3]}{s['anim']:04d}-{s['var']:02d}.anim"
        if name not in self.anims:
            data = self.src.read(name)
            if not data:
                raise ValueError(f"{name} not found: cannot change that animation's keys")
            self.anims[name] = bytearray(data)
        return self.anims[name]

    def scale_bone(self, bone: int, factor: float) -> int:
        """Every scale key of the bone times `factor` (sequences without keys get one). Children follow the bone."""
        n, o = self.arr(OFS_BONES)
        if not 0 <= bone < n:
            raise ValueError(f"no bone #{bone}")
        if not 0.05 <= factor <= 20:
            raise ValueError("size must be between 5% and 2000%")
        p = o + bone * BONE_SIZE
        struct.pack_into("<I", self.b, p + 4, struct.unpack_from("<I", self.b, p + 4)[0] | BONE_TRANSFORMED)
        track = p + 56
        interp, gseq, tn, to, vn, vo = struct.unpack_from("<Hh4I", self.b, track)
        seqs = self.model.sequences()
        lists = 1 if gseq >= 0 else len(seqs)
        if tn < lists or vn < lists:                     # unanimated bone: one (empty) list per sequence first
            to = self.model.append(bytes(self.b[to:to + tn * 8]) + bytes(8 * (lists - tn)))
            vo = self.model.append(bytes(self.b[vo:vo + vn * 8]) + bytes(8 * (lists - vn)))
            tn = vn = lists
            struct.pack_into("<Hh4I", self.b, track, interp or 1, gseq, tn, to, vn, vo)
        changed = 0
        for k in range(lists):
            s = seqs[k] if gseq < 0 else None
            if s and s["flags"] & mt.F_ALIAS:
                continue                                 # plays another sequence
            external = s is not None and not s["flags"] & mt.F_IN_MODEL
            buf = self.anim_buf(s) if external else self.b
            c, at = struct.unpack_from("<2I", self.b, vo + k * 8)
            if c:
                for j in range(c):
                    x, y, z = struct.unpack_from("<3f", buf, at + j * 12)
                    struct.pack_into("<3f", buf, at + j * 12, x * factor, y * factor, z * factor)
            else:
                def put(data: bytes) -> int:
                    while len(buf) % 16:
                        buf.append(0)
                    pos = len(buf)
                    buf.extend(data)
                    return pos
                struct.pack_into("<2I", self.b, to + k * 8, 1, put(struct.pack("<I", 0)))
                struct.pack_into("<2I", self.b, vo + k * 8, 1, put(struct.pack("<3f", factor, factor, factor)))
            changed += 1
        return changed

    # --- saving --------------------------------------------------------------------------------------------------------
    def save(self) -> list[str]:
        struct.pack_into("<I", self.b, 0x44, 1)          # one .skin: the one edited
        out = {self.model.path: bytes(self.b), self.skin_path: bytes(self.skin)}
        out.update({k: bytes(v) for k, v in self.anims.items()})
        for path, data in out.items():
            (mt.WORK / path).parent.mkdir(parents=True, exist_ok=True)
            (mt.WORK / path).write_bytes(data)
        return sorted(out)


def edit_part(src, spec: str, part: int, opacity=None, blend=None, flags=None, texture=None) -> str:
    p = Parts(src, spec)
    said = []
    if texture is not None:
        p.set_texture(part, int(texture))
        said.append(f"texture #{texture}")
    if blend is not None or flags is not None:
        p.set_draw(part, None if blend is None else int(blend), None if flags is None else int(flags))
        said.append("drawing")
    if opacity is not None:
        v = p.set_opacity(part, float(opacity))
        said.append("hidden" if v == 0 else f"{round(v * 100)}% visible")
    p.save()
    return f"part #{part}: " + ", ".join(said) + " (Pack into game to see it there)"


def scale_bone(src, spec: str, bone: int, factor: float) -> str:
    p = Parts(src, spec)
    n = p.scale_bone(int(bone), float(factor))
    p.save()
    return f"bone #{bone} × {factor:g} in {n} animations (Pack into game to see it there)"


# --- recolour and custom skins ---------------------------------------------------------------------------------------
def load_skins() -> dict:
    return json.loads(SKINS.read_text(encoding="utf-8")) if SKINS.exists() else {}


def save_skins(data: dict):
    SKINS.write_text(json.dumps(data, indent=1), encoding="utf-8")


def skin_list(src, path: str) -> list[dict]:
    """Every skin of a model: the client's displays using it, imported colourings, custom skins."""
    cmd = mt.raw_dbc(src, "CreatureModelData.dbc")
    want = path[:-3].lower()
    ids = {mt.Dbc.rid(r) for r in cmd.records if cmd.string(mt.row(cmd, r)[2]).lower()[:-4] == want}
    out = []
    cdi = mt.raw_dbc(src, "CreatureDisplayInfo.dbc")
    for r in cdi.records:
        row = mt.row(cdi, r)
        if row[1] in ids:
            out.append(dict(id=row[0], name=f"display {row[0]}", textures=[cdi.string(x) for x in row[6:9]], custom=False))
    import imports
    for name, e in imports.load_imports().items():
        if e["path"].lower() == path.lower():
            known = {s["id"] for s in out}
            out += [dict(id=d, name=f"{name} {c}", textures=imports.slot_list(e["textures"].get(c, ""), e), custom=False)
                    for c, d in e["displays"].items() if d not in known]
    out += [dict(id=int(k), name=v["name"], textures=v["textures"], custom=True, base=v["base"])
            for k, v in load_skins().items() if v["path"].lower() == path.lower()]
    return out


def delete_skin(skin_id: str) -> str:
    data = load_skins()
    e = data.pop(str(skin_id), None)
    if not e:
        raise ValueError(f"no custom skin {skin_id}")
    folder = e["path"].rsplit("\\", 1)[0]
    for t in e["textures"]:
        f = mt.WORK / f"{folder}\\{t}.blp"
        if f"_skin{skin_id}_" in t and f.exists():
            f.unlink()
    save_skins(data)
    return f"custom skin {skin_id} deleted (Pack into game to take it out there too)"


def rename_skin(skin_id: str, name: str) -> str:
    data = load_skins()
    data[str(skin_id)]["name"] = name.strip() or data[str(skin_id)]["name"]
    save_skins(data)
    return "renamed"


def skins_for(path: str) -> dict:
    return {k: v for k, v in load_skins().items() if v["path"].lower() == path.lower()}


def recolour_image(img, hue: float, sat: float, bright: float, mask=None):
    """Hue turned by `hue` degrees, saturation and brightness times sat / bright; alpha kept. The page's preview
    does the same maths."""
    from PIL import Image
    img = img.convert("RGBA")
    alpha = img.getchannel("A")
    h, s, v = img.convert("RGB").convert("HSV").split()
    shift = round(hue / 360 * 256)
    h = h.point(lambda x: (x + shift) % 256)
    s = s.point(lambda x: max(0, min(255, round(x * sat))))
    v = v.point(lambda x: max(0, min(255, round(x * bright))))
    out = Image.merge("HSV", (h, s, v)).convert("RGB")
    out.putalpha(alpha)
    return Image.composite(out, img, mask) if mask is not None else out


def part_mask(p: Parts, part: int, size: tuple[int, int]):
    """Where the part's triangles lie on its texture (a little wider, so the seams are covered)."""
    from PIL import Image, ImageDraw
    sub = struct.unpack_from("<H", p.skin, p.batch(part) + 4)[0]
    vn, vo, inn, io_, _, _, sn, so = struct.unpack_from("<8I", p.skin, 4)
    remap = struct.unpack_from(f"<{vn}H", p.skin, vo)
    tris = struct.unpack_from(f"<{inn}H", p.skin, io_)
    _, _, _, _, istart, icount = struct.unpack_from("<6H", p.skin, so + sub * 48)
    istart += struct.unpack_from("<H", p.skin, so + sub * 48 + 2)[0] << 16
    _, verts = p.arr(0x3C)
    w, h = size
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    for t in range(istart, istart + icount - 2, 3):
        pts = []
        for k in range(3):
            u, v = struct.unpack_from("<2f", p.b, verts + remap[tris[t + k]] * 48 + 32)
            pts.append(((u % 1.0) * w, (v % 1.0) * h))
        draw.polygon(pts, fill=255, outline=255)
        draw.line(pts + [pts[0]], fill=255, width=3)
    return mask


def to_blp(img) -> bytes:
    import imports
    return imports.png_to_blp(img)


def recolour(src, spec: str, part: int, hue: float, sat: float, bright: float, only_part: bool,
             skins: list[str], base_display: int | None, skin_id: str | None) -> dict:
    """Recolour the texture the part uses. A fixed texture gets a recoloured copy the model points at; a skin texture
    goes into a custom skin (made from the shown skin when it is not one already)."""
    from PIL import Image
    p = Parts(src, spec)
    pb = p.batch(part)
    combo = struct.unpack_from("<H", p.skin, pb + 16)[0]
    ln, lo = p.arr(OFS_TEX_LOOKUP)
    tex = struct.unpack_from("<h", p.b, lo + combo * 2)[0] if combo < ln else -1
    textures = p.model.textures()
    if not 0 <= tex < len(textures):
        raise ValueError("this part has no texture")
    kind, name = textures[tex]
    folder = p.model.path.rsplit("\\", 1)[0]
    if kind == 0:
        current = name
    elif kind in (11, 12, 13):
        slot = kind - 11
        if not skins or not skins[slot]:
            raise ValueError("no skin is shown for this model: pick one in Skins first")
        current = f"{folder}\\{skins[slot]}.blp"
    else:
        raise ValueError(f"texture type {kind} (player / item texture) cannot be recoloured here")
    data = src.read(current)
    if not data:
        raise ValueError(f"{current} not found")
    img = Image.open(io.BytesIO(data)).convert("RGBA")
    mask = part_mask(p, part, img.size) if only_part else None
    img = recolour_image(img, hue, sat, bright, mask)

    if kind == 0:
        stem = current.rsplit("\\", 1)[-1][:-4]
        new = f"{folder}\\{stem if stem.endswith('_rc') else stem + '_rc'}.blp"
        (mt.WORK / new).parent.mkdir(parents=True, exist_ok=True)
        (mt.WORK / new).write_bytes(to_blp(img))
        if new.lower() != current.lower():
            p.rename_texture(tex, new)
            p.save()
        return dict(text=f"recoloured: {new}", skin=skin_id)

    all_skins = load_skins()
    if not skin_id or skin_id not in all_skins:          # a new custom skin from the one shown
        if not base_display:
            raise ValueError("this skin has no display id yet (import the model first)")
        used = {int(k) for k in all_skins}
        skin_id = str(next(i for i in range(FIRST_SKIN, FIRST_SKIN + 100000) if i not in used))
        all_skins[skin_id] = dict(path=p.model.path, base=int(base_display), textures=list(skins) + [""] * (3 - len(skins)),
                                  name=f"custom {skin_id}")
    entry = all_skins[skin_id]
    model_name = p.model.path.rsplit("\\", 1)[-1][:-3]
    tex_name = f"{model_name}_skin{skin_id}_{slot + 1}"
    (mt.WORK / f"{folder}\\{tex_name}.blp").parent.mkdir(parents=True, exist_ok=True)
    (mt.WORK / f"{folder}\\{tex_name}.blp").write_bytes(to_blp(img))
    entry["textures"][slot] = tex_name
    save_skins(all_skins)
    return dict(text=f"custom skin {skin_id} ({entry['name']}): slot {slot + 1} recoloured. Pack into game, then "
                     f".morph {skin_id}", skin=skin_id)


def skin_rows(cdi, cdi_cols, import_rows: dict[int, dict]) -> list[list]:
    """CreatureDisplayInfo rows of the custom skins: a copy of the base display with the skin's textures."""
    out = []
    for sid, e in load_skins().items():
        base = import_rows.get(e["base"])
        if base is None:
            rec = cdi.find(e["base"])
            if not rec:
                continue
            base = dict(zip(cdi_cols, cdi.decode(rec)))
        d = dict(base)
        t = e["textures"]
        d.update(ID=int(sid), TextureVariation_1=t[0], TextureVariation_2=t[1], TextureVariation_3=t[2],
                 PortraitTextureName="")
        out.append([d[c] for c in cdi_cols])
    return out
