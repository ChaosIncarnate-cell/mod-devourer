#!/usr/bin/env python3
"""The model tool with a face: a local web page that shows a model in 3D, plays its animations, lists what every
emote plays, and links / renames / resets / packs with buttons. Uses modeltool.py for everything it changes.

    python server.py            then open http://localhost:8765  (modeltool-viewer.bat does both)
"""
from __future__ import annotations

import contextlib
import io
import json
import struct
import sys
import threading
import traceback
from argparse import Namespace
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
import imports                                               # noqa: E402
import parts                                                 # noqa: E402
import modeltool as mt                                       # noqa: E402

PORT = 8765
HERE = Path(__file__).resolve().parent
lock = threading.Lock()
state = {"src": None, "anims": None}


def sources():
    if state["src"] is None:
        state["src"] = mt.layers([])
        state["anims"] = mt.Anims(state["src"])
    return state["src"], state["anims"]


def refresh():
    state["src"] = None


# --- reading a model for the viewer ----------------------------------------------------------------------------------
def display_of(src, spec: str) -> int | None:
    if spec.lower().startswith("c:"):
        out = mt.sql(f"SELECT CreatureDisplayID FROM creature_template_model WHERE CreatureID = {int(spec[2:])} "
                     "ORDER BY Idx")
        return int(out[0][0]) if out else None
    return int(spec) if spec.isdigit() else None


def skins_of(src, display: int | None) -> list[str]:
    if not display:
        return []
    cdi = mt.raw_dbc(src, "CreatureDisplayInfo.dbc")
    rec = next((r for r in cdi.records if mt.Dbc.rid(r) == display), None)
    if not rec:
        return []
    r = mt.row(cdi, rec)
    return [cdi.string(x) for x in r[6:9]]


def model_json(spec: str, skin_tex: str = "", skin_id: str = "") -> dict:
    src, anims = sources()
    model, notes = mt.load(src, spec)
    b = model.b
    arr = model.arr

    # vertices: position, bone weights, bone indices, normal, uv
    n, o = arr(0x3C)
    pos, nrm, uv, bw, bi = [], [], [], [], []
    for i in range(n):
        p = o + i * 48
        x, y, z = struct.unpack_from("<3f", b, p)
        w = struct.unpack_from("<4B", b, p + 12)
        ix = struct.unpack_from("<4B", b, p + 16)
        nx, ny, nz = struct.unpack_from("<3f", b, p + 20)
        u, v = struct.unpack_from("<2f", b, p + 32)
        pos += [x, y, z]; nrm += [nx, ny, nz]; uv += [u, v]
        bw += [c / 255 for c in w]; bi += list(ix)

    # the first .skin: triangles, submeshes, and which texture each batch uses
    skin = src.read(model.path[:-3] + "00.skin")
    if not skin or skin[:4] != b"SKIN":
        raise ValueError("no .skin file for this model")
    vn, vo, inn, io_, _, _, sn, so, tn, to = struct.unpack_from("<10I", skin, 4)
    remap = struct.unpack_from(f"<{vn}H", skin, vo)
    tris = struct.unpack_from(f"<{inn}H", skin, io_)
    subs = []
    for i in range(sn):
        sid, level, vstart, vcount, istart, icount = struct.unpack_from("<6H", skin, so + i * 48)
        istart += level << 16
        subs.append(dict(geoset=sid, tris=[remap[t] for t in tris[istart:istart + icount]]))
    tex_lookup = list(struct.unpack_from(f"<{arr(0x80)[0]}h", b, arr(0x80)[1])) if arr(0x80)[0] else []
    textures = model.textures()
    mats = [struct.unpack_from("<2H", b, arr(0x70)[1] + i * 4) for i in range(arr(0x70)[0])]
    batches = []
    for i in range(tn):
        flags, prio, shader, sub, geoset, color, mat, layer, count, combo = struct.unpack_from("<BbHHHhHHHH", skin,
                                                                                               to + i * 24)
        tex = tex_lookup[combo] if combo < len(tex_lookup) else -1
        mflags, blend = mats[mat] if mat < len(mats) else (0, 0)
        batches.append(dict(sub=sub, tex=tex, layer=layer, blend=blend, twoSided=bool(mflags & 4),
                            unlit=bool(mflags & 1), mflags=mflags, mat=mat, geoset=subs[sub]["geoset"] if sub < len(subs) else 0))
    for bt, extra in zip(batches, parts.Parts(src, spec, editing=False).info()):
        bt["opacity"] = extra["opacity"]

    # bones: parent, pivot
    n, o = arr(0x2C)
    bones = []
    for i in range(n):
        p = o + i * 88
        parent = struct.unpack_from("<h", b, p + 8)[0]
        pivot = struct.unpack_from("<3f", b, p + 76)
        key = struct.unpack_from("<i", b, p)[0]
        bones.append(dict(parent=parent, pivot=pivot, key=parts.KEY_BONES[key] if 0 <= key < len(parts.KEY_BONES) else ""))

    display = display_of(src, spec)
    skins = skins_of(src, display)
    skin_list = parts.skin_list(src, model.path)
    chosen = next((s for s in skin_list if str(s["id"]) == str(skin_id)), None) if skin_id else None
    if chosen:                                           # a skin picked in the page
        display, skins = chosen["id"], chosen["textures"]
    staged = imports.staged(model.path)
    if not chosen and staged and staged["colourings"] and (skin_tex or not skins):    # converted: show a colouring
        colouring = staged["colourings"].get(skin_tex) or next(iter(staged["colourings"].values()))
        skins = imports.slot_list(colouring, staged)                    # its texture for each skin slot
    elif not chosen and not skins and skin_list:         # opened by path: the first display that uses it
        display, skins = skin_list[0]["id"], skin_list[0]["textures"]
    tex_list = []
    for kind, name in textures:
        if kind == 0:
            tex_list.append(name)
        elif kind in (11, 12, 13) and skins and skins[kind - 11]:
            folder = model.path.rsplit("\\", 1)[0]
            tex_list.append(f"{folder}\\{skins[kind - 11]}.blp")
        else:
            tex_list.append("")

    seqs = model.sequences()
    sequences = [dict(i=s["i"], anim=s["anim"], name=anims.name.get(s["anim"], "?"), var=s["var"], dur=s["dur"],
                      alias=s["alias"] if s["flags"] & mt.F_ALIAS else None,
                      external=not s["flags"] & mt.F_IN_MODEL and not s["flags"] & mt.F_ALIAS) for s in seqs]
    emotes = []
    for command, anim in sorted(set(anims.commands)):
        idx, path = model.plays(anims, anim)
        emotes.append(dict(cmd=command, anim=anim, name=anims.name.get(anim, "?"), plays=idx,
                           own=idx is not None and seqs[idx]["anim"] == anim,
                           via=[anims.name.get(p, str(p)) for p in path]))
    in_work = (mt.WORK / model.path).exists()
    effects = (arr(0x128)[0], arr(0x120)[0])            # particle emitters, ribbons
    return dict(path=model.path, notes=notes, staged=staged, skin=skins[0] if skins else "", effects=effects, pos=pos, nrm=nrm, uv=uv, bw=bw, bi=bi, subs=subs, batches=batches,
                bones=bones, textures=tex_list, texKinds=[k for k, _ in textures], skins=list(skins or []),
                display=display, skinList=skin_list, blends=parts.BLENDS, sequences=sequences, emotes=emotes, changed=in_work,
                animNames=sorted(anims.name.values(), key=str.lower),
                anims=sorted(({"id": i, "name": n, "own": any(x["anim"] == i and x["var"] == 0 and not x["flags"] & mt.F_ALIAS
                                                               for x in seqs),
                               "plays": model.plays(anims, i)[0]} for i, n in anims.name.items()), key=lambda a: a["name"].lower()))


def anim_json(spec: str, seq: int) -> dict:
    """Keyframes of one sequence for every bone (an alias plays its target)."""
    src, _ = sources()
    model, _ = mt.load(src, spec)
    b = model.b
    seqs = model.sequences()
    seen = set()
    while seqs[seq]["flags"] & mt.F_ALIAS and seq not in seen:
        seen.add(seq)
        seq = seqs[seq]["alias"]
    s = seqs[seq]
    data = b
    if not s["flags"] & mt.F_IN_MODEL:                       # keyframes in Creature\X\X<anim>-<var>.anim
        data = src.read(f"{model.path[:-3]}{s['anim']:04d}-{s['var']:02d}.anim") or b""
    n_glob, o_glob = model.arr(mt.OFS_GLOBALS)

    def track(off, fmt, size):
        interp, gseq, tn, to, vn, vo = struct.unpack_from("<Hh4I", b, off)
        k = seq
        buf = data
        if gseq >= 0:                                        # global loop: one list for every sequence, in the .m2
            k, buf = 0, b
        if k >= tn or k >= vn:
            return None
        c, o = struct.unpack_from("<2I", b, to + k * 8)
        c2, o2 = struct.unpack_from("<2I", b, vo + k * 8)
        if not c or not c2 or o + 4 * c > len(buf) or o2 + size * c2 > len(buf):
            return None
        times = list(struct.unpack_from(f"<{c}I", buf, o))
        vals = [struct.unpack_from("<" + fmt, buf, o2 + j * size) for j in range(c2)]
        return dict(interp=interp, t=times, v=vals)

    n, o = model.arr(0x2C)
    out = []
    for i in range(n):
        p = o + i * 88
        out.append(dict(t=track(p + 16, "3f", 12), r=track(p + 36, "4h", 8), s=track(p + 56, "3f", 12)))
    return dict(seq=seq, dur=s["dur"], bones=out)


def texture_png(path: str) -> bytes | None:
    src, _ = sources()
    data = src.read(path)
    if not data:
        return None
    from PIL import Image
    img = Image.open(io.BytesIO(data))
    out = io.BytesIO()
    img.convert("RGBA").save(out, "PNG")
    return out.getvalue()


def run(command: str, **kw) -> dict:
    """A modeltool command, its printed output as the answer."""
    src, _ = sources()
    buf = io.StringIO()
    ok = True
    with contextlib.redirect_stdout(buf):
        try:
            getattr(mt, f"cmd_{command}")(Namespace(sources=[], **kw), src)
        except SystemExit as e:
            ok = False
            print(e.code if isinstance(e.code, str) else "failed")
    refresh()
    return dict(ok=ok, text=buf.getvalue().strip())


def convert_step(file: str, name: str | None) -> dict:
    meta = imports.stage(file, name)
    refresh()
    return meta


def import_step(body: dict) -> dict:
    e = imports.import_model(body["name"], body.get("colours", []), float(body.get("scale", 1)),
                             int(body.get("template", 21950)), mt.WORK)
    refresh()
    if mt.load_settings().get("autobind_on_import"):
        e = {**e, "autobind": run("autobind", model=e["path"])["text"]}
    return e


def edit(fn, spec: str, *args, **kw) -> dict:
    """A part edit: its message as the answer; a refused edit is shown, not a crash."""
    src, _ = sources()
    try:
        text = fn(src, spec, *args, **kw)
    except ValueError as e:
        return dict(ok=False, text=str(e))
    refresh()
    return dict(ok=True, text=text)


def recolour_step(body: dict) -> dict:
    src, _ = sources()
    try:
        r = parts.recolour(src, body["m"], int(body["part"]), float(body.get("hue", 0)), float(body.get("sat", 1)),
                           float(body.get("bright", 1)), bool(body.get("onlyPart", True)), body.get("skins") or [],
                           body.get("display"), str(body["skinId"]) if body.get("skinId") else None)
    except ValueError as e:
        return dict(ok=False, text=str(e))
    refresh()
    return dict(ok=True, **r)


def settings_json() -> dict:
    _, anims = sources()
    return dict(settings=mt.load_settings(), defaults=mt.DEFAULT_RULES, commands=sorted({c for c, _ in anims.commands}),
                animNames=sorted(anims.name.values(), key=str.lower))


def save_settings(body: dict) -> dict:
    mt.save_settings(body)
    return dict(ok=True)


def find_json(text: str) -> dict:
    src, _ = sources()
    rows = mt.sql("SELECT t.entry, t.name, m.CreatureDisplayID FROM creature_template t JOIN creature_template_model m "
                  f"ON m.CreatureID = t.entry WHERE t.name LIKE '%{text.replace(chr(39), '')}%' ORDER BY t.name LIMIT 60")
    cmd = mt.raw_dbc(src, "CreatureModelData.dbc")
    models = [cmd.string(mt.row(cmd, r)[2]) for r in cmd.records]
    models = sorted({m[:-4] + ".m2" for m in models if text.lower() in m.lower()})[:60]
    return dict(creatures=[dict(entry=e, name=n, display=d) for e, n, d in rows], models=models)


# --- http ------------------------------------------------------------------------------------------------------------
class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send(self, code, body: bytes, kind="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", kind)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def answer(self, fn):
        try:
            with lock:
                result = fn()
            if isinstance(result, bytes):
                self.send(200, result, "image/png")
            elif result is None:
                self.send(404, b"{}")
            else:
                self.send(200, json.dumps(result).encode())
        except SystemExit as e:
            self.send(400, json.dumps(dict(error=str(e.code))).encode())
        except Exception as e:                               # noqa: BLE001  (shown in the page)
            traceback.print_exc()
            self.send(500, json.dumps(dict(error=f"{type(e).__name__}: {e}")).encode())

    def do_GET(self):
        u = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        if u.path in ("/", "/index.html"):
            return self.send(200, (HERE / "viewer.html").read_bytes(), "text/html; charset=utf-8")
        routes = {
            "/api/find": lambda: find_json(q.get("q", "")),
            "/api/model": lambda: model_json(q["m"], q.get("skin", ""), q.get("sid", "")),
            "/api/exports": lambda: dict(models=imports.exported_models(), folder=str(imports.EXPORTS),
                                         imports=imports.load_imports()),
            "/api/anim": lambda: anim_json(q["m"], int(q["seq"])),
            "/api/tex": lambda: texture_png(q["p"]),
            "/api/work": lambda: run("work"),
            "/api/settings": settings_json,
        }
        if u.path in routes:
            return self.answer(routes[u.path])
        self.send(404, b"{}")

    def do_POST(self):
        u = urlparse(self.path)
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        routes = {
            "/api/link": lambda: run("link", model=body["m"], anim=body["anim"], target=body["target"]),
            "/api/rename": lambda: run("rename", model=body["m"], seq=int(body["seq"]), anim=body["anim"]),
            "/api/reset": lambda: run("reset", model=body["m"]),
            "/api/autobind": lambda: run("autobind", model=body["m"]),
            "/api/part": lambda: edit(parts.edit_part, body["m"], int(body["part"]), opacity=body.get("opacity"),
                                      blend=body.get("blend"), flags=body.get("flags"), texture=body.get("texture")),
            "/api/bone": lambda: edit(parts.scale_bone, body["m"], int(body["bone"]), float(body["factor"])),
            "/api/recolour": lambda: recolour_step(body),
            "/api/skin/delete": lambda: dict(ok=True, text=parts.delete_skin(str(body["id"]))),
            "/api/skin/rename": lambda: dict(ok=True, text=parts.rename_skin(str(body["id"]), body["name"])),
            "/api/settings": lambda: save_settings(body),
            "/api/pack": lambda: run("pack"),
            "/api/convert": lambda: convert_step(body["file"], body.get("name") or None),
            "/api/import": lambda: import_step(body),
        }
        if u.path in routes:
            return self.answer(routes[u.path])
        self.send(404, b"{}")


def main():
    port = int(sys.argv[sys.argv.index("--port") + 1]) if "--port" in sys.argv else PORT
    print(f"Model tool: http://localhost:{port}  (close this window to stop it)")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
