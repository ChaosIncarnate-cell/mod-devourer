#!/usr/bin/env python3
"""Checks the form editor (forms.py, its web API in server.py, `pack`) against a made-up client, without a game,
a database or the real start_kit output (everything is written into a temporary folder).

    python selftest_forms.py            ends with FORMS SELFTEST PASSED
"""
from __future__ import annotations

import io
import json
import os
import random
import struct
import sys
import tempfile
import threading
import urllib.request
from argparse import Namespace
from pathlib import Path

HERE = Path(__file__).resolve().parent
TMP = Path(tempfile.mkdtemp(prefix="forms-selftest-"))
os.environ["CHROMATICAW_ROOT"] = str(TMP)                   # before modeltool is imported: the made-up game folder
os.environ.pop("CHROMATICAW_SPELL_DBC", None)
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "client"))

import forms                                                 # noqa: E402
import modeltool as mt                                       # noqa: E402
import mpq                                                   # noqa: E402
import selftest as client_test                               # noqa: E402  (tools/client: table(), raw(), m2())
import start_kit as sk                                       # noqa: E402
from dbc import Dbc                                          # noqa: E402

b = sk.b
FAILS: list[str] = []
VISUAL, CAST_KIT, PRECAST_KIT = 500, 600, 601
ANIM_STAND, ANIM_ATTACK, ANIM_CAST, ANIM_ROAR, ANIM_HOWL = 0, 17, 53, 55, 999
ICON_CLAW = 1


def check(cond, text):
    print(("ok   " if cond else "FAIL ") + text)
    if not cond:
        FAILS.append(text)


# --- the made-up client ------------------------------------------------------------------------------------------
def spell_dbc() -> bytes:
    """Every template start_kit uses: random words, but a known visual and icon, and a name."""
    ids = {d[2] for f in sk.FORMS for d in sk.form_spells(f)} | {d[3] for d in sk.BASE}
    rnd = random.Random(3)
    strings = bytearray(b"\0")
    rows = []
    for i in sorted(ids):
        w = [rnd.getrandbits(12) for _ in range(234)]
        w[0] = i
        for c in b.STRING_COLS:
            w[c] = 0
        w[b.COL["Name_Lang_enUS"]] = len(strings)
        strings += f"Template {i}".encode() + b"\0"
        w[b.COL["SpellVisualID_1"]] = VISUAL
        w[b.COL["SpellIconID"]] = ICON_CLAW
        rows.append(struct.pack("<234I", *w))
    return struct.pack("<4s4I", b"WDBC", len(rows), 234, 936, len(strings)) + b"".join(rows) + bytes(strings)


def dbc_with_strings(fields: int, rows: list[list]) -> bytes:
    """A table of 4-byte fields; str values go into the string block."""
    strings = bytearray(b"\0")
    out = []
    for r in rows:
        w = []
        for v in r:
            if isinstance(v, str):
                w.append(len(strings))
                strings += v.encode() + b"\0"
            elif isinstance(v, float):
                w.append(struct.unpack("<I", struct.pack("<f", v))[0])
            else:
                w.append(v & 0xFFFFFFFF)
        out.append(struct.pack(f"<{fields}I", *(w + [0] * (fields - len(w)))))
    return struct.pack("<4s4I", b"WDBC", len(out), fields, fields * 4, len(strings)) + b"".join(out) + bytes(strings)


def icon_blp() -> bytes:
    from PIL import Image
    import blp
    return blp.to_blp(Image.new("RGBA", (64, 64), (200, 40, 40, 255)), 64)


def make_client():
    data = TMP / "WOW HD CLIENT" / "Data"
    (data / "enUS").mkdir(parents=True)
    files = {
        "Spell.dbc": spell_dbc(),
        "AnimationData.dbc": dbc_with_strings(8, [[ANIM_STAND, "Stand", 0, 0, 0, 0], [ANIM_ATTACK, "Attack1H", 0, 0, 0, 0],
                                                  [ANIM_CAST, "SpellCastDirected", 0, 0, 0, ANIM_STAND],
                                                  [ANIM_ROAR, "BattleRoar", 0, 0, 0, ANIM_STAND],
                                                  [ANIM_HOWL, "Howl", 0, 0, 0, ANIM_ROAR]]),
        "Emotes.dbc": dbc_with_strings(7, [[1, "ROAR", ANIM_ROAR]]),
        "EmotesText.dbc": dbc_with_strings(19, [[1, "roar", 1]]),
        "SpellDuration.dbc": dbc_with_strings(4, [[21, -1, 0, -1], [1, 10000, 0, 10000], [105, 9000, 0, 9000]]),
        "SpellCastTimes.dbc": dbc_with_strings(4, [[1, 0, 0, 0], [16, 1500, 0, 1500]]),
        "SpellRange.dbc": dbc_with_strings(40, [[1, 0.0, 0.0, 0.0, 0.0, 0, "Self Only"],
                                                [2, 0.0, 0.0, 5.0, 5.0, 0, "Combat Range"]]),
        "SpellRadius.dbc": dbc_with_strings(4, [[14, 8.0, 0.0, 8.0]]),
        "SpellIcon.dbc": dbc_with_strings(2, [[ICON_CLAW, "Interface\\Icons\\Ability_Claw"]]),
        "SpellVisual.dbc": dbc_with_strings(32, [[VISUAL, PRECAST_KIT, CAST_KIT, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7]]),
        "SpellVisualKit.dbc": dbc_with_strings(38, [[CAST_KIT, -1, ANIM_CAST, 11, 12], [PRECAST_KIT, -1, ANIM_STAND]]),
        "CreatureDisplayInfo.dbc": client_test.table("CreatureDisplayInfo", [
            {"ID": f.display, "ModelID": 100, "CreatureModelScale": 1.0} for f in sk.FORMS]),
        "CreatureModelData.dbc": client_test.table("CreatureModelData", [{"ID": 100, "ModelName": "Creature\\Wolf\\Wolf.mdx"}]),
    }
    archive = {f"DBFilesClient\\{k}": v for k, v in files.items()}
    flags = mt.F_IN_MODEL
    archive["Creature\\Wolf\\Wolf.m2"] = with_lookup(client_test.m2([], 1, [(ANIM_STAND, 0, flags), (ANIM_ATTACK, 0, flags),
                                                                          (ANIM_ROAR, 0, flags)]))
    archive["Interface\\Icons\\Ability_Claw.blp"] = icon_blp()
    mpq.write_archive(data / "enUS" / "locale-enUS.MPQ", archive)
    mpq.write_archive(data / "common.MPQ", {"readme.txt": b"made up"})
    # the Devourer's client patch as build_client_patch.py leaves it: the client's Spell.dbc with the Devourer's rows
    mpq.write_archive(data / mt.PATCH, {"Devourer\\patch.txt": b"test", "DBFilesClient\\Spell.dbc": files["Spell.dbc"]})


def with_lookup(model: bytes) -> bytes:
    """The made-up model with the animation lookup table the client hashes into."""
    m = mt.Model("Creature\\Wolf\\Wolf.m2", model)
    m.rebuild_lookup()
    return bytes(m.b)


# --- the test ----------------------------------------------------------------------------------------------------
def main() -> int:
    make_client()
    # everything start_kit and the editor write goes below TMP
    (TMP / "repo" / "tools").mkdir(parents=True)
    sk.REPO = forms.REPO = TMP / "repo"
    sk.EDITS = TMP / "repo" / "tools" / "form_edits.json"
    sk.OUT_SQL = TMP / "repo" / "start.sql"
    sk.OUT_MD = TMP / "repo" / "start-kit.md"
    forms.STAMP = TMP / ".forms-on-server"
    mt.WORK = TMP / "work"
    mt.subprocess.run = lambda *a, **k: Namespace(stdout="", stderr="", returncode=0)   # no tasklist, no mysql here
    src = mt.layers([])
    anims = mt.Anims(src)

    o = forms.overview(src)
    check(len(o["forms"]) == len(sk.FORMS) + 1 and o["forms"][0]["shape"] == "base", "overview lists the base kit and every form")
    wolf = forms.form_detail(src, anims, 5)
    tear = next(s for s in wolf["spells"] if s["id"] == 9100911)
    check(wolf["form"]["name"] == "Wolf" and wolf["form"]["model"] == "Creature\\Wolf\\Wolf.m2", "the Wolf opens with its model")
    check(tear["visual"]["anims"] == {"precast": ANIM_STAND, "cast": ANIM_CAST}, "a spell's animations come from its visual's kits")
    check(tear["visual"]["plays"]["cast"]["name"] == "Stand" and not tear["visual"]["plays"]["cast"]["own"],
          "the model's fallback for a missing animation is shown")
    check(wolf["modelPlays"][ANIM_HOWL][1] == "BattleRoar", "fallback chain: Howl -> BattleRoar")
    check(tear["script"] is None and next(s for s in wolf["spells"] if s["id"] == 9100913)["script"] == "spell_devourer_pack_prowess",
          "scripted spells are marked")
    check(tear["template"]["name"] == "Template 17253", "template names come from Spell.dbc")

    # change the Wolf: bigger, another icon; Tear Throat renamed, cheaper cooldown, harder hit, roars when cast
    body = {"form": {**wolf["form"]["code"], "scale": 1.5, "icon": ICON_CLAW},
            "spells": {"9100911": {"name": "Throat Rip", "fields": {"RecoveryTime": 4000, "EffectBasePoints_1": 9},
                                   "anim": {"cast": ANIM_ROAR}},
                       "9100914": {"level": 12}}}
    forms.save(src, 5, body)
    edits = json.loads(sk.EDITS.read_text())
    check(edits["forms"] == {"5": {"scale": 1.5, "icon": ICON_CLAW}}, "only the changed form fields are kept")
    e = edits["spells"]["9100911"]
    check(e == {"name": "Throat Rip", "fields": {"RecoveryTime": 4000, "EffectBasePoints_1": 9},
                "anim": {"cast": ANIM_ROAR, "base_visual": VISUAL}}, f"the spell edit is minimal: {e}")
    sql = sk.OUT_SQL.read_text()
    check("'Throat Rip'" in sql and f"{sk.custom_visual(9100911)}" in sql, "start_kit's SQL has the new name and own visual")
    check("Take the shape of a wolf you have devoured: Throat Rip" in sql and "opens at level 12" in sql,
          "the form's tooltip names the kit as edited")
    check("(5, 'Wolf', 9100910, 31049, 1.5," in sql, "devourer_shape gets the new size")
    md = sk.OUT_MD.read_text()
    check("Throat Rip" in md, "docs/start-kit.md follows")

    # saving the code's values again drops the edits
    plain = forms.form_detail(src, anims, 5)
    t2 = next(s for s in plain["spells"] if s["id"] == 9100911)
    check(t2["values"]["RecoveryTime"] == 4000 and t2["visual"]["custom"] and t2["visual"]["anims"]["cast"] == ANIM_ROAR,
          "the detail shows the edited values and animation")
    forms.save(src, 5, {"spells": {"9100911": {"fields": {"RecoveryTime": t2["plainValues"]["RecoveryTime"]},
                                               "anim": {"cast": ANIM_CAST}}}})
    e = json.loads(sk.EDITS.read_text())["spells"]["9100911"]
    check(e == {"name": "Throat Rip", "fields": {"EffectBasePoints_1": 9}}, f"values equal to the code's are pruned: {e}")
    forms.save(src, 5, {"spells": {"9100911": {"anim": {"cast": ANIM_ROAR, "precast": ANIM_STAND}}}})
    e = json.loads(sk.EDITS.read_text())["spells"]["9100911"]
    check(e["anim"] == {"cast": ANIM_ROAR, "base_visual": VISUAL}, "an animation equal to the visual's own is pruned")

    # an own icon
    from PIL import Image
    png = io.BytesIO()
    Image.new("RGBA", (40, 40), (10, 200, 10, 255)).save(png, "PNG")
    import base64
    icon = forms.add_icon("Throat Rip", "data:image/png;base64," + base64.b64encode(png.getvalue()).decode())
    check(icon == {"id": sk.ICON_BASE, "path": "Interface\\Icons\\Devourer_Throat_Rip"}, f"own icon registered: {icon}")
    check(mt.WORK.joinpath("Interface", "Icons", "Devourer_Throat_Rip.blp").read_bytes()[:4] == b"BLP2", "its BLP is in work\\")
    forms.save(src, 5, {"spells": {"9100911": {"fields": {"SpellIconID": icon["id"]}}}})

    # pack: patch-Z gets the spell rows, the visual + kit, the icon row and file
    mt.cmd_pack(Namespace(), mt.layers([]))
    with mpq.Archive(TMP / "WOW HD CLIENT" / "Data" / mt.PATCH) as arc:
        spells = Dbc(arc.read("DBFilesClient\\Spell.dbc"), "Spell").use_layout("Spell")
        vis = Dbc(arc.read("DBFilesClient\\SpellVisual.dbc"), "SpellVisual")
        kits = Dbc(arc.read("DBFilesClient\\SpellVisualKit.dbc"), "SpellVisualKit")
        icons = Dbc(arc.read("DBFilesClient\\SpellIcon.dbc"), "SpellIcon")
        has_blp = arc.has("Interface\\Icons\\Devourer_Throat_Rip.blp")
        has_marker = arc.has("Devourer\\patch.txt")
    row = dict(zip(spells.columns(), spells.decode(spells.find(9100911))))
    check(row["Name_Lang_enUS"] == "Throat Rip" and row["Name_Lang_deDE"] == "Throat Rip", "client Spell.dbc: name in every locale")
    check(row["SpellVisualID_1"] == sk.custom_visual(9100911) and row["SpellIconID"] == sk.ICON_BASE,
          "client Spell.dbc: own visual and icon")
    check(len([r for r in spells.records if sk.FIRST <= Dbc.rid(r) <= sk.LAST]) == len(sk.all_defs(sk.load_edits())[1]),
          "client Spell.dbc: every start_kit spell")
    v = struct.unpack("<32I", vis.find(sk.custom_visual(9100911)))
    check(v[2] == sk.custom_kit(9100911, "cast") and v[1] == PRECAST_KIT and v[13] == 7,
          "SpellVisual: a copy with its own cast kit, the rest kept")
    k = struct.unpack("<38i", kits.find(sk.custom_kit(9100911, "cast")))
    check(k[2] == ANIM_ROAR and k[3:5] == (11, 12), "SpellVisualKit: the copy plays the chosen animation, effects kept")
    check(icons.string(struct.unpack("<2I", icons.find(sk.ICON_BASE))[1]) == "Interface\\Icons\\Devourer_Throat_Rip"
          and has_blp and has_marker, "SpellIcon row and .blp packed, the patch keeps its marker")

    # the web API, as the page uses it
    import server
    httpd = server.ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{httpd.server_address[1]}"

    def get(path):
        with urllib.request.urlopen(base + path) as r:
            return r.read(), r.headers["Content-Type"]

    def post(path, body):
        req = urllib.request.Request(base + path, json.dumps(body).encode(), method="POST")
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())

    check(len(json.loads(get("/api/forms")[0])["forms"]) == len(sk.FORMS) + 1, "GET /api/forms")
    look = json.loads(get("/api/lookups")[0])
    check(look["icons"][str(sk.ICON_BASE)].endswith("Devourer_Throat_Rip") and look["effects"]["6"] == "APPLY_AURA"
          and look["ranges"]["2"] == "Combat Range (0-5 yd)", "GET /api/lookups")
    d = json.loads(get("/api/form?shape=5")[0])
    check(d["form"]["scale"] == 1.5 and len(d["spells"]) == 7, "GET /api/form")
    check(json.loads(get("/api/form?shape=base")[0])["spells"][0]["name"] == "Rush", "GET /api/form (base kit)")
    data, kind = get(f"/api/icon?id={sk.ICON_BASE}")
    check(kind == "image/png" and data[:4] == b"\x89PNG", "GET /api/icon (own icon, from work\\)")
    data, kind = get(f"/api/icon?id={ICON_CLAW}")
    check(kind == "image/png", "GET /api/icon (the game's icon)")
    check(json.loads(get("/api/spells?q=17253")[0])["spells"][0]["visual"] == VISUAL, "GET /api/spells")
    r = post("/api/form/save", {"shape": 5, "spells": {"9100911": {"reset": True}}, "form": d["form"]["code"]})
    check(not json.loads(sk.EDITS.read_text()).get("spells", {}).get("9100911") and "detail" in r,
          "POST /api/form/save (reset a spell and the form)")
    httpd.shutdown()

    print("\nFORMS SELFTEST " + ("PASSED" if not FAILS else f"FAILED ({len(FAILS)})"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    raise SystemExit(main())
