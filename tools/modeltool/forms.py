"""The Devourer's forms in the model tool: look at a form in 3D, change what it is and what it can do, then pack.

What can be changed (all of it is kept in tools/form_edits.json, which tools/start_kit.py puts on top of its own
definitions, so the edits survive every regeneration and are committed with the module):
  a form      name, look (display id), size, the base colouring's name, icon
  a spell     name, texts, level, icon, any spell_dbc column (cost, cooldown, range, effects ...), and the
              animation the form plays for it (while casting / when cast / while channelling)

After each save start_kit.py writes its SQL and doc again. `pack` (modeltool.py) then puts into patch-Z.MPQ:
the Devourer's Spell.dbc rows from that SQL, the edited animations as own SpellVisual / SpellVisualKit rows, the
owner's icons as SpellIcon rows (+ their .blp from work\\), and runs the SQL on the server's database.

Where a spell gets its template's look: Spell.SpellVisualID_1 -> SpellVisual.dbc (kits for "while casting",
"cast", "channel" ...) -> SpellVisualKit.dbc (AnimID: the animation the caster plays). An edited animation gets a
copy of that visual whose kits play the chosen animation; the template's effects (glows, sounds) stay.
"""
from __future__ import annotations

import base64
import hashlib
import io
import json
import os
import re
import struct
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "tools"))

import modeltool as mt                                       # noqa: E402
import sqlrows                                               # noqa: E402  (tools/client)
import start_kit as sk                                       # noqa: E402  (tools/start_kit.py)
from build_client_patch import client_strings                # noqa: E402
from dbc import LAYOUTS, Dbc                                 # noqa: E402

b = sk.b                                                     # tools/coa/build_devourer_spells.py: columns, Dbc
ENUMS = json.loads((HERE / "spell_enums.json").read_text(encoding="utf-8"))
STAMP = HERE / ".forms-on-server"                           # hash of the SQL last run on the server (git-ignored)
KIT_FIELD = {"precast": 1, "cast": 2, "channel": 6}          # SpellVisual.dbc: which field holds which kit
VISUAL_FIELDS, KIT_FIELDS = 32, 38                           # 3.3.5a (12340) SpellVisual / SpellVisualKit
NO_ANIM = 0xFFFFFFFF                                         # -1 in a kit: no animation
SCHOOLS = [(1, "Physical"), (2, "Holy"), (4, "Fire"), (8, "Nature"), (16, "Frost"), (32, "Shadow"), (64, "Arcane")]
SLOTS = {0: "Form", 1: "Ability", 2: "Ability", 3: "Passive", 4: "Later ability", 5: "Later ability",
         6: "Cast by the kit", 7: "Cast by the kit", 8: "Cast by the kit", 9: "Cast by the kit"}
# Columns the editor never offers as raw fields: the id, texts, and the level (it has its own box).
HIDDEN = {"ID", "SpellLevel", "BaseLevel"} | {b.COLUMNS[i] for i in b.STRING_COLS} | \
         {f"{g}_Mask" for g in b.STRING_GROUPS}
state: dict = {}


# --- reading --------------------------------------------------------------------------------------------------------
def spell_dbc(src) -> tuple:
    """(build_devourer_spells.Dbc of a stock Spell.dbc for the templates, where it came from). The server's copy
    if it can be found (the committed SQL was made from it), else the client's."""
    if "spells" not in state:
        env = os.environ.get("CHROMATICAW_SPELL_DBC")
        found = [Path(env)] if env else []
        found += [mt.ROOT / p / "Spell.dbc" for p in ("server/data/dbc", "server/dbc", "data/dbc", "dbc")]
        path = next((p for p in found if p.is_file()), None)
        if path:
            state["spells"] = (b.Dbc(path), str(path))
        else:
            state["spells"] = (b.Dbc(mt.raw_dbc(src, "Spell.dbc").to_bytes()), "the client's Spell.dbc")
    return state["spells"]


def reset():
    """Forget the client's tables (after a pack changed them); the parsed Spell.dbc stays."""
    for key in ("tables", "lookups"):
        state.pop(key, None)


def words(d, rec: bytes) -> tuple:
    return struct.unpack_from(f"<{len(rec) // 4}I", rec)


def f32(word: int) -> float:
    return round(struct.unpack("<f", struct.pack("<I", word))[0], 4)


def s32(word: int) -> int:
    return word - (1 << 32) if word & 0x80000000 else word


def table(src, name: str) -> tuple:
    """(Dbc, {id: words}) of a client table, or (None, {}) if the client has none."""
    cache = state.setdefault("tables", {})
    if name not in cache:
        try:
            d = mt.raw_dbc(src, name)
            cache[name] = d, {Dbc.rid(r): words(d, r) for r in d.records}
        except SystemExit:
            cache[name] = None, {}
    return cache[name]


def typed(col: int, word: int):
    """A raw spell_dbc word as the editor shows it."""
    if col in b.FLOAT_COLS:
        return f32(word)
    if col in b.UNSIGNED_COLS:
        return word
    return s32(word)


def lookups(src) -> dict:
    """Everything the editor's lists need: durations, cast times, ranges, radii, icons, animations, enums."""
    if "lookups" in state:
        return state["lookups"]

    def secs(ms: int) -> str:
        return "instant" if ms == 0 else f"{ms / 1000:g} sec"

    out = {"schools": SCHOOLS, **{k: ENUMS[k] for k in ("effects", "auras", "targets", "mechanics", "powers")}}
    _, rows = table(src, "SpellDuration.dbc")
    out["durations"] = {i: ("until cancelled" if s32(w[1]) < 0 else secs(s32(w[1])) if w[1] else "none")
                        for i, w in rows.items()}
    _, rows = table(src, "SpellCastTimes.dbc")
    out["casttimes"] = {i: secs(s32(w[1])) for i, w in rows.items()}
    d, rows = table(src, "SpellRange.dbc")
    out["ranges"] = {i: f"{d.string(w[6]) if len(w) > 6 else ''} ({f32(w[1]):g}-{f32(w[3]):g} yd)".strip()
                     for i, w in rows.items()}
    _, rows = table(src, "SpellRadius.dbc")
    out["radii"] = {i: f"{f32(w[1]):g} yd" for i, w in rows.items()}
    d, rows = table(src, "SpellIcon.dbc")
    icons = {i: d.string(w[1]) for i, w in rows.items()}
    for i, path in edits_file().get("icons", {}).items():
        icons[int(i)] = path
    out["icons"] = icons
    out["anims"] = mt.Anims(src).name
    state["lookups"] = out
    return out


def edits_file() -> dict:
    return sk.load_edits()


def spell_name(dbc, sid: int) -> str:
    try:
        off = dbc.row(sid)[b.COL["Name_Lang_enUS"]]
    except KeyError:
        return "?"
    end = dbc.strings.find(b"\0", off)
    return dbc.strings[off:end].decode("utf-8", "replace") if off else ""


def search_spells(src, text: str) -> list[dict]:
    """Stock spells by name or id (to borrow a look from): id, name, visual, icon."""
    dbc, _ = spell_dbc(src)
    if "names" not in state:
        col_name, col_vis, col_icon = b.COL["Name_Lang_enUS"], b.COL["SpellVisualID_1"], b.COL["SpellIconID"]
        names = []
        for sid, i in dbc.index.items():
            w = struct.unpack_from(f"<{dbc.fields}I", dbc.records, i * dbc.rsize)
            off = w[col_name]
            end = dbc.strings.find(b"\0", off)
            names.append((sid, dbc.strings[off:end].decode("utf-8", "replace") if off else "", w[col_vis], w[col_icon]))
        state["names"] = sorted(names)
    text = text.strip().lower()
    hits = [n for n in state["names"] if text and (text == str(n[0]) or text in n[1].lower())]
    return [dict(id=i, name=n, visual=v, icon=c) for i, n, v, c in hits[:80]]


# --- the forms --------------------------------------------------------------------------------------------------------
def forms_of(edits: dict) -> list:
    return sk.edited_forms(edits)


def overview(src) -> dict:
    edits = edits_file()
    out = [dict(shape="base", name="Every Devourer (base kit)", display=0, icon=0, edited=any(
        str(d[0]) in edits.get("spells", {}) for d in sk.BASE))]
    for f in sorted(forms_of(edits), key=lambda f: f.shape):
        spells = range(f.base, f.base + 10)
        out.append(dict(shape=f.shape, name=f.name, display=f.display, icon=f.icon,
                        edited=str(f.shape) in edits.get("forms", {}) or
                        any(str(s) in edits.get("spells", {}) for s in spells)))
    return dict(forms=out, edits=str(sk.EDITS.relative_to(REPO)))


def defs_of(shape, edits: dict) -> tuple:
    """(the edited Form or None for the base kit, its spell definitions with edits)."""
    if shape == "base":
        return None, [sk.edit_spell((sid, lvl, t, o, x), edits) for sid, lvl, cost, t, o, x in sk.BASE]
    f = next((f for f in forms_of(edits) if f.shape == int(shape)), None)
    if not f:
        raise ValueError(f"no form with shape {shape}")
    return f, sk.form_spells(f, edits)


def visual_anims(src, visual: int) -> dict:
    """The animation each kit of a SpellVisual plays: {kind: anim id or -1}, kinds without a kit left out."""
    _, vis = table(src, "SpellVisual.dbc")
    _, kits = table(src, "SpellVisualKit.dbc")
    out = {}
    v = vis.get(visual)
    for kind, field in KIT_FIELD.items():
        kit = kits.get(v[field]) if v and v[field] else None
        if kit:
            out[kind] = s32(kit[2])
    return out


def form_detail(src, anims, shape) -> dict:
    edits = edits_file()
    dbc, dbc_from = spell_dbc(src)
    look = lookups(src)
    f, defs = defs_of(shape, edits)
    _, plain = defs_of(shape, {**edits, "spells": {}})            # without spell edits: what "reset" goes back to
    plain = {d[0]: d for d in plain}
    scripts = dict(sk.SCRIPTS)
    scripts[sk.RUSH] = "spell_devourer_rush"
    if f:
        scripts[f.base] = "spell_devourer_form"
    model, model_note = None, ""
    if f:
        try:
            model, _ = mt.load(src, str(f.display))
        except SystemExit as e:
            model_note = str(e.code)
    spells = []
    for sid, level, template, overrides, (name, desc, tip) in defs:
        row = sk.spell_row(dbc, sid, level, template, overrides)
        p = plain[sid]
        base_row = sk.spell_row(dbc, sid, p[1], p[2], p[3])
        e = edits.get("spells", {}).get(str(sid), {})
        slot = sid - f.base if f else None
        # the animation: an edited one, else what the visual's kits play
        base_visual = row[b.COL["SpellVisualID_1"]] if not e.get("anim") else e["anim"].get("base_visual", 0)
        played = visual_anims(src, base_visual)
        if e.get("anim"):
            played.update({k: v for k, v in e["anim"].items() if k in KIT_FIELD})
        plays = {}
        seqs = model.sequences() if model else []
        for kind, anim in played.items():
            if model and anim >= 0:
                idx, _ = model.plays(anims, anim)
                plays[kind] = dict(seq=idx, name=anims.name.get(seqs[idx]["anim"], "?") if idx is not None else None,
                                   own=idx is not None and seqs[idx]["anim"] == anim)
        spells.append(dict(
            id=sid, slot=slot, kind=SLOTS.get(slot, "Base kit") if slot is not None else "Base kit", level=level,
            template=dict(id=template, name=spell_name(dbc, template)), name=name, description=desc, aura=tip,
            plain=dict(name=p[4][0], description=p[4][1], aura=p[4][2], level=p[1]),
            values={c: typed(i, row[i]) for i, c in enumerate(b.COLUMNS) if c not in HIDDEN},
            plainValues={c: typed(i, base_row[i]) for i, c in enumerate(b.COLUMNS) if c not in HIDDEN},
            edit=e, script=scripts.get(sid), icon=look["icons"].get(row[b.COL["SpellIconID"]], ""),
            visual=dict(id=base_visual, anims=played, plays=plays, custom=bool(e.get("anim")))))
    model_plays = {}                                         # anim id -> [sequence, its name, its own?]
    if model:
        seqs = model.sequences()
        for aid in anims.name:
            idx, _ = model.plays(anims, aid)
            if idx is not None:
                model_plays[aid] = [idx, anims.name.get(seqs[idx]["anim"], "?"), seqs[idx]["anim"] == aid]
    form = None
    if f:
        code = next(x for x in sk.FORMS if x.shape == f.shape)
        form = dict(shape=f.shape, name=f.name, display=f.display, scale=f.scale, skin=f.skin, icon=f.icon,
                    iconPath=look["icons"].get(f.icon, ""), base=f.base, family=f.family, zone=f.zone,
                    code={k: getattr(code, k) for k in sk.FORM_FIELDS}, edit=edits.get("forms", {}).get(str(f.shape), {}),
                    model=model.path if model else None, modelNote=model_note)
    return dict(form=form, spells=spells, modelPlays=model_plays, templatesFrom=dbc_from,
                edits=str(sk.EDITS.relative_to(REPO)))


# --- saving -----------------------------------------------------------------------------------------------------------
def save(src, shape, body: dict) -> dict:
    """body: {form: {field: value}, spells: {id: {name, description, aura, level, fields: {col: value},
    anim: {kind: anim id} | null, reset: true}}}. Only what differs from the code is kept; then start_kit runs."""
    edits = edits_file()
    edits.setdefault("forms", {})
    edits.setdefault("spells", {})
    dbc, _ = spell_dbc(src)
    if body.get("form") is not None and shape != "base":
        code = next(x for x in sk.FORMS if x.shape == int(shape))
        e = {k: v for k, v in body["form"].items() if k in sk.FORM_FIELDS and v != getattr(code, k)}
        for k in ("display", "icon"):
            if k in e:
                e[k] = int(e[k])
        if "scale" in e:
            e["scale"] = float(e["scale"])
        if e:
            edits["forms"][str(shape)] = e
        else:
            edits["forms"].pop(str(shape), None)
    for sid, change in (body.get("spells") or {}).items():
        sid = str(int(sid))
        if change.get("reset"):
            edits["spells"].pop(sid, None)
            continue
        e = edits["spells"].setdefault(sid, {})
        for k in ("name", "description", "aura"):
            if k in change:
                e[k] = str(change[k])
        if "level" in change:
            e["level"] = int(change["level"])
        for col, value in (change.get("fields") or {}).items():
            if col not in b.COL or col in HIDDEN:
                raise ValueError(f"spell {sid}: {col} cannot be edited")
            e.setdefault("fields", {})[col] = float(value) if b.COL[col] in b.FLOAT_COLS else int(value)
        if "anim" in change:
            if change["anim"]:
                e["anim"] = {k: int(v) for k, v in change["anim"].items() if k in KIT_FIELD}
            else:
                e.pop("anim", None)
    prune(dbc, shape, edits, src)
    for key in ("forms", "spells"):
        if not edits[key]:
            edits.pop(key)
    write_edits(edits)
    lines = sk.generate(dbc, edits)
    return dict(text="\n".join(lines))


def prune(dbc, shape, edits: dict, src=None):
    """Drops every spell edit that equals what the code makes; fills in each animation's base visual (and drops
    the animations that equal what that visual plays anyway)."""
    _, plain = defs_of(shape, {**edits, "spells": {}})
    for sid, level, template, overrides, texts in plain:
        e = edits["spells"].get(str(sid))
        if e is None:
            continue
        base_row = sk.spell_row(dbc, sid, level, template, overrides)
        for k, i in (("name", 0), ("description", 1), ("aura", 2)):
            if e.get(k) == texts[i]:
                e.pop(k)
        if e.get("level") == level:
            e.pop("level")
        fields = e.get("fields", {})
        for col in list(fields):
            if b.to_u32(fields[col], b.COL[col]) == base_row[b.COL[col]]:
                fields.pop(col)
        if not fields:
            e.pop("fields", None)
        if e.get("anim"):
            without = {k: v for k, v in e.items() if k != "anim"}
            d = sk.edit_spell((sid, level, template, overrides, texts), {"spells": {str(sid): without}})
            base_visual = sk.spell_row(dbc, *d[:4])[b.COL["SpellVisualID_1"]]
            e["anim"]["base_visual"] = base_visual
            plays = visual_anims(src, base_visual) if src is not None else {}
            for kind in [k for k in e["anim"] if k in KIT_FIELD]:
                if plays.get(kind, -1) == e["anim"][kind]:
                    e["anim"].pop(kind)
            if not any(k in KIT_FIELD for k in e["anim"]):
                e.pop("anim")
        if not e:
            edits["spells"].pop(str(sid))


def write_edits(edits: dict):
    sk.EDITS.write_text(json.dumps(edits, indent=1, sort_keys=True) + "\n", encoding="utf-8")


# --- the owner's icons ----------------------------------------------------------------------------------------------
def add_icon(name: str, data_url: str) -> dict:
    """An image (data: URL) as a 64x64 icon: work\\Interface\\Icons\\Devourer_<name>.blp and a SpellIcon id."""
    import blp                                               # tools/client/blp.py (needs Pillow)
    from PIL import Image
    name = re.sub(r"[^A-Za-z0-9_]", "", name.replace(" ", "_"))
    if not name:
        raise ValueError("give the icon a name (letters, digits, _)")
    raw = base64.b64decode(data_url.split(",", 1)[-1])
    img = Image.open(io.BytesIO(raw))
    path = f"Interface\\Icons\\Devourer_{name}"
    target = mt.WORK.joinpath(*(path + ".blp").split("\\"))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(blp.to_blp(img, 64))
    edits = edits_file()
    icons = edits.setdefault("icons", {})
    rid = next((int(i) for i, p in icons.items() if p.lower() == path.lower()), None)
    if rid is None:
        rid = next(i for i in range(sk.ICON_BASE, sk.ICON_LAST + 1) if str(i) not in icons)
        icons[str(rid)] = path
    write_edits(edits)
    state.pop("lookups", None)
    return dict(id=rid, path=path)


# --- pack -------------------------------------------------------------------------------------------------------------
def _table(content: dict, src, name: str) -> tuple:
    key = f"DBFilesClient\\{name}"
    lower = {k.lower(): k for k in content}
    old = lower.get(key.lower())
    data = content.pop(old) if old else mt.raw_dbc(src, name).to_bytes()
    return key, Dbc(data, name)


def _drop(d: Dbc, lo: int, hi: int):
    d.records = [r for r in d.records if not lo <= Dbc.rid(r) <= hi]


def apply_to_client(content: dict, src, raw_dbc=None) -> str:
    """Into the patch's files: the Devourer's spell rows (start_kit's SQL), edited animations, the owner's icons."""
    edits = edits_file()
    notes = []
    # spells: the rows of the generated SQL replace the patch's rows of that range
    rows = sqlrows.table_rows([sk.OUT_SQL], LAYOUTS["Spell"]["table"])
    key, d = _table(content, src, "Spell.dbc")
    d.use_layout("Spell")
    cols = d.columns()
    _drop(d, sk.FIRST, sk.LAST)
    for rid, row in rows.items():
        d.put(d.encode(client_strings([row.get(c) for c in cols], cols)))
    content[key] = d.to_bytes()
    notes.append(f"{len(rows)} spells")

    # animations: one SpellVisual per edited spell, its kits copied with the chosen animation
    anims = {int(s): e["anim"] for s, e in edits.get("spells", {}).items() if e.get("anim")}
    vkey, vis = _table(content, src, "SpellVisual.dbc")
    kkey, kits = _table(content, src, "SpellVisualKit.dbc")
    if vis.fields != VISUAL_FIELDS or kits.fields != KIT_FIELDS:
        raise SystemExit(f"SpellVisual.dbc has {vis.fields} fields / SpellVisualKit.dbc {kits.fields}: expected "
                         f"{VISUAL_FIELDS} / {KIT_FIELDS} (3.3.5a): animations not packed")
    _drop(vis, sk.custom_visual(sk.FIRST), sk.custom_visual(sk.LAST))
    _drop(kits, sk.custom_kit(sk.FIRST, sk.KIT_KINDS[0]), sk.custom_kit(sk.LAST, sk.KIT_KINDS[-1]))
    for sid, a in sorted(anims.items()):
        base = vis.find(a.get("base_visual", 0))
        v = list(words(vis, base)) if base else [0] * VISUAL_FIELDS
        v[0] = sk.custom_visual(sid)
        for kind, field in KIT_FIELD.items():
            if kind not in a:
                continue
            old = kits.find(v[field]) if v[field] else None
            k = list(words(kits, old)) if old else [0, NO_ANIM] + [0] * (KIT_FIELDS - 2)
            k[0] = sk.custom_kit(sid, kind)
            k[2] = int(a[kind]) & 0xFFFFFFFF
            kits.put(struct.pack(f"<{KIT_FIELDS}I", *k))
            v[field] = k[0]
        vis.put(struct.pack(f"<{VISUAL_FIELDS}I", *v))
    content[vkey], content[kkey] = vis.to_bytes(), kits.to_bytes()
    if anims:
        notes.append(f"{len(anims)} edited animations")

    # icons: SpellIcon rows (their .blp files are in work\ and go in with it)
    icons = edits.get("icons", {})
    ikey, ic = _table(content, src, "SpellIcon.dbc")
    _drop(ic, sk.ICON_BASE, sk.ICON_LAST)
    names = {k.lower() for k in content}
    for rid, path in icons.items():
        ic.put(struct.pack("<2I", int(rid), ic.intern(path)))
        if not mt.WORK.joinpath(*(path + ".blp").split("\\")).exists() and (path + ".blp").lower() not in names:
            notes.append(f"MISSING work\\{path}.blp (icon {rid})")
    content[ikey] = ic.to_bytes()
    if icons:
        notes.append(f"{len(icons)} own icons")
    return "forms: " + ", ".join(notes)


def apply_to_server(mysql: Path) -> str:
    """Runs start_kit's SQL on the world database when it changed since the last pack."""
    sql = sk.OUT_SQL.read_text(encoding="utf-8")
    digest = hashlib.sha1(sql.encode()).hexdigest()
    if STAMP.exists() and STAMP.read_text().strip() == digest:
        return "server: the forms' SQL is already there"
    if not mysql.exists():
        return f"server NOT updated ({mysql} not found): restart the worldserver, it applies {sk.OUT_SQL.name} itself"
    r = subprocess.run([str(mysql), "-uacore", "-pacore", "-h127.0.0.1", "acore_world"], input=sql,
                       capture_output=True, text=True)
    errors = [line for line in r.stderr.splitlines() if "Warning" not in line]
    if r.returncode or errors:
        return "server: forms NOT updated: " + " ".join(errors)[:300]
    STAMP.parent.mkdir(parents=True, exist_ok=True)
    STAMP.write_text(digest)
    return "server: forms updated (restart the worldserver to use them)"
