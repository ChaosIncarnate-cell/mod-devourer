"""Bringing models from wow.export into the game, one step at a time (the model tool's page has a button for each):

  1. convert   a wow.export model -> staging\\Creature\\<Name>\\... (our client's format, colourings as .blp);
               nothing in the game changes, the page shows the result in 3D
  2. import    staging -> work\\, and a creature model + one display per chosen colouring (imports.json);
               display ids 994001+, model data ids 904001+
  3. pack      (modeltool.py) puts work\\ into patch-Z.MPQ, and with it the displays: into the client's
               CreatureDisplayInfo / CreatureModelData, and into the server's creaturedisplayinfo_dbc /
               creaturemodeldata_dbc (the server reads those at start: restart it)
"""
from __future__ import annotations

import io
import json
import shutil
import struct
import subprocess
from pathlib import Path

import convert

HERE = Path(__file__).resolve().parent
STAGING = HERE / "staging"
IMPORTS = HERE / "imports.json"
EXPORTS = Path.home() / "wow.export"
FIRST_DISPLAY, FIRST_MODEL = 994001, 904001
MAX_TEXTURE = 1024


# --- textures --------------------------------------------------------------------------------------------------------
def png_to_blp(path) -> bytes:
    """An image as BLP2 with DXT5 compression (8-bit alpha) and every mip level, like the game's own textures."""
    from PIL import Image
    img = (path if hasattr(path, "convert") else Image.open(path)).convert("RGBA")   # a file or an image
    w, h = img.size
    pw, ph = 1, 1
    while pw < min(w, MAX_TEXTURE):
        pw *= 2
    while ph < min(h, MAX_TEXTURE):
        ph *= 2
    if (pw, ph) != (w, h):
        img = img.resize((pw, ph), Image.LANCZOS)
    mips = []
    while True:
        out = io.BytesIO()
        img.save(out, "DDS", pixel_format="DXT5")
        data = out.getvalue()
        blocks = max(1, (img.size[0] + 3) // 4) * max(1, (img.size[1] + 3) // 4) * 16
        mips.append(data[128:128 + blocks])
        if img.size == (1, 1) or len(mips) == 16:
            break
        img = img.resize((max(1, img.size[0] // 2), max(1, img.size[1] // 2)), Image.LANCZOS)
    header = 4 + 4 + 4 + 8 + 64 + 64 + 1024
    offsets, sizes, pos = [], [], header
    for m in mips:
        offsets.append(pos)
        sizes.append(len(m))
        pos += len(m)
    offsets += [0] * (16 - len(mips))
    sizes += [0] * (16 - len(mips))
    # type 1, encoding 2 (DXT), alpha depth 8, alpha encoding 7 (DXT5), has mips
    return (b"BLP2" + struct.pack("<I", 1) + bytes([2, 8, 7, 1]) + struct.pack("<2I", pw, ph)
            + struct.pack("<16I", *offsets) + struct.pack("<16I", *sizes) + bytes(1024) + b"".join(mips))


# --- 1. convert --------------------------------------------------------------------------------------------------------
def exported_models() -> list[dict]:
    """Every model wow.export saved (creatures first)."""
    if not EXPORTS.is_dir():
        return []
    out = []
    for p in sorted(EXPORTS.rglob("*.m2")):
        rel = p.relative_to(EXPORTS)
        out.append(dict(file=str(rel), name=p.stem, kind=rel.parts[0] if len(rel.parts) > 1 else ""))
    out.sort(key=lambda m: (m["kind"] != "creature", m["file"].lower()))
    return out


def game_name(stem: str) -> str:
    return "".join(part[:1].upper() + part[1:] for part in stem.replace("-", "_").split("_"))


def stage(export_file: str, name: str | None = None) -> dict:
    src = (EXPORTS / export_file).resolve()
    if EXPORTS.resolve() not in src.parents:
        raise ValueError("not a file in the wow.export folder")
    name = name or game_name(src.stem)
    result = convert.convert(src, name)
    folder = STAGING / f"Creature\\{name}"
    if folder.exists():
        shutil.rmtree(folder)
    for path, data in result["files"].items():
        (STAGING / path).parent.mkdir(parents=True, exist_ok=True)
        (STAGING / path).write_bytes(data)
    colours, texs = {}, set()                            # colour -> its texture for skin slots 1-3 ("" = none)
    for colour, slots in result["colourings"].items():
        colours[colour] = ["", "", ""]
        for k, p in slots.items():
            p = Path(p)
            tex = f"{name}_{p.stem[len(src.stem):].lstrip('_')}"   # voidcreeper_glow1_red -> Voidcreeper_glow1_red,
                                                                   # shadowstalkerpantherglow_blue -> ..._glow_blue
            if tex not in texs:
                data = p.read_bytes() if p.suffix.lower() == ".blp" else png_to_blp(p)
                (STAGING / f"Creature\\{name}\\{tex}.blp").write_bytes(data)
                texs.add(tex)
            colours[colour][int(k) - 1] = tex
    meta = dict(name=name, path=result["path"], source=export_file, report=result["report"], colourings=colours,
                skin_slots=result["skin_slots"], bbox=result["bbox"],
                files=sorted(result["files"]) + [f"Creature\\{name}\\{t}.blp" for t in sorted(texs)])
    (STAGING / f"Creature\\{name}\\modeltool.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    return meta


def slot_list(tex, meta: dict) -> list[str]:
    """A colouring's texture for skin slots 1-3. Older conversions kept one name and used it in every slot."""
    if isinstance(tex, list):
        return tex
    return [tex if k in meta.get("skin_slots", [1]) else "" for k in (1, 2, 3)]


def staged(path: str) -> dict | None:
    meta = STAGING / Path(path).parent / "modeltool.json"
    return json.loads(meta.read_text(encoding="utf-8")) if meta.exists() else None


# --- 2. import ---------------------------------------------------------------------------------------------------------
def load_imports() -> dict:
    return json.loads(IMPORTS.read_text(encoding="utf-8")) if IMPORTS.exists() else {}


def save_imports(data: dict):
    IMPORTS.write_text(json.dumps(data, indent=1), encoding="utf-8")


def import_model(name: str, colours: list[str], scale: float, template: int, work: Path) -> dict:
    meta = staged(f"Creature\\{name}\\x.m2")
    if not meta:
        raise ValueError(f"{name}: convert it first")
    if not colours and meta["colourings"]:
        raise ValueError("choose at least one colouring")
    imports = load_imports()
    entry = imports.get(name, {})
    used_displays = {d for e in imports.values() for d in e.get("displays", {}).values()}
    used_models = {e["model_id"] for e in imports.values() if "model_id" in e}
    model_id = entry.get("model_id") or next(i for i in range(FIRST_MODEL, FIRST_MODEL + 1000) if i not in used_models)
    displays = dict(entry.get("displays", {}))
    for colour in colours or ["base"]:
        if colour not in displays:
            displays[colour] = next(i for i in range(FIRST_DISPLAY, FIRST_DISPLAY + 10000)
                                    if i not in used_displays and i not in displays.values())
    displays = {c: d for c, d in displays.items() if c in (colours or ["base"])}
    for path in meta["files"]:
        owners = [c for c, t in meta["colourings"].items()
                  if any(path.endswith(f"\\{x}.blp") for x in slot_list(t, meta) if x)]
        if owners and not set(owners) & set(colours):    # a texture only colourings you did not pick use
            continue
        if path.lower().endswith(".m2") and (work / path).exists():
            continue                                     # changed in the tool already (links): keep those changes
        (work / path).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(STAGING / path, work / path)
    imports[name] = dict(path=meta["path"], source=meta["source"], model_id=model_id, displays=displays,
                         textures={c: slot_list(meta["colourings"].get(c, ""), meta) for c in displays}, scale=scale,
                         template=template, bbox=meta["bbox"], skin_slots=meta["skin_slots"])
    save_imports(imports)
    return imports[name]


# --- 3. pack: the displays into the client's tables and the server's ---------------------------------------------
def rows(src, raw_dbc) -> tuple[list[list], list[list]]:
    """(CreatureModelData rows, CreatureDisplayInfo rows) of every import, in layout order."""
    from dbc import Dbc
    cmd = Dbc(raw_dbc(src, "CreatureModelData.dbc").to_bytes(), "CreatureModelData").use_layout("CreatureModelData")
    cdi = Dbc(raw_dbc(src, "CreatureDisplayInfo.dbc").to_bytes(), "CreatureDisplayInfo").use_layout("CreatureDisplayInfo")
    cmd_cols, cdi_cols = cmd.columns(), cdi.columns()
    models, displays, made = [], [], {}
    for name, e in load_imports().items():
        t_disp = cdi.find(e["template"])
        if not t_disp:
            raise ValueError(f"{name}: template display {e['template']} not found")
        t_disp = cdi.decode(t_disp)
        t_model = cmd.decode(cmd.find(t_disp[cdi_cols.index("ModelID")]))
        m = dict(zip(cmd_cols, t_model))
        x0, y0, z0, x1, y1, z1 = e["bbox"]
        m.update(ID=e["model_id"], ModelName=e["path"][:-3] + ".mdx", ModelScale=1.0,
                 CollisionWidth=max(x1 - x0, y1 - y0) / 2, CollisionHeight=z1 - z0,
                 GeoBoxMinX=x0, GeoBoxMinY=y0, GeoBoxMinZ=z0, GeoBoxMaxX=x1, GeoBoxMaxY=y1, GeoBoxMaxZ=z1)
        models.append([m[c] for c in cmd_cols])
        for colour, display in e["displays"].items():
            d = dict(zip(cdi_cols, t_disp))
            tex = slot_list(e["textures"].get(colour, ""), e)
            d.update(ID=display, ModelID=e["model_id"], CreatureModelScale=float(e["scale"]), CreatureModelAlpha=255,
                     ExtendedDisplayInfoID=0, PortraitTextureName="", CreatureGeosetData=0,
                     TextureVariation_1=tex[0], TextureVariation_2=tex[1], TextureVariation_3=tex[2])
            displays.append([d[c] for c in cdi_cols])
            made[display] = d
    import parts                                         # custom skins: copies of a display with other textures
    displays += parts.skin_rows(cdi, cdi_cols, made)
    return models, displays


def apply_to_client(content: dict, src, raw_dbc) -> int:
    """Adds the import rows to the CreatureModelData / CreatureDisplayInfo inside the patch."""
    from dbc import Dbc
    models, displays = rows(src, raw_dbc)
    if not models and not displays:
        return 0
    lower = {k.lower(): k for k in content}
    for table, new in (("CreatureModelData", models), ("CreatureDisplayInfo", displays)):
        key = f"DBFilesClient\\{table}.dbc"
        data = content.get(lower.get(key.lower(), key)) or raw_dbc(src, f"{table}.dbc").to_bytes()
        d = Dbc(data, table).use_layout(table)
        for values in new:
            d.put(d.encode(values))
        content.pop(lower.get(key.lower(), key), None)
        content[key] = d.to_bytes()
    return len(displays)


def apply_to_server(src, raw_dbc, mysql: Path) -> str:
    from dbc import LAYOUTS
    models, displays = rows(src, raw_dbc)
    if not models and not displays:
        return ""

    def value(v):
        return "'" + v.replace("\\", "\\\\").replace("'", "''") + "'" if isinstance(v, str) else repr(v)

    sql = []
    for table, layout, new in (("creaturemodeldata_dbc", "CreatureModelData", models),
                               ("creaturedisplayinfo_dbc", "CreatureDisplayInfo", displays)):
        cols = ", ".join(f"`{c}`" for c, _ in LAYOUTS[layout]["fields"])
        sql += [f"REPLACE INTO `{table}` ({cols}) VALUES ({', '.join(value(v) for v in row)});" for row in new]
    r = subprocess.run([str(mysql), "-uacore", "-pacore", "-h127.0.0.1", "acore_world"], input="\n".join(sql),
                       capture_output=True, text=True)
    errors = [l for l in r.stderr.splitlines() if "Warning" not in l]
    if r.returncode or errors:
        return "server tables NOT updated: " + " ".join(errors)[:300]
    return f"server: {len(models)} models, {len(displays)} displays (restart the server to see them)"
