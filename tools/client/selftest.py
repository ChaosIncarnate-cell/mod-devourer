#!/usr/bin/env python3
"""Self-test of the client patch tool against a made-up client (no game files needed).

    python tools/client/selftest.py [--keep]

Builds a tiny fake 3.3.5a client in a temporary folder (DBCs with a few invented rows in the real layouts,
stand-in GlueXML/FrameXML files written for this test, an "HD patch", a locale patch, an earlier Devourer patch)
and a fake CoA source (looks and models), runs build_client_patch.py with --install, and checks the result:
every DBC row equals the module's SQL, class 10 rules, the CoA copies, the load order, the MPQ, the generated SQL,
and, when Lua 5.1 is installed, runs the patched character creation code against mocked UI objects.
"""
from __future__ import annotations

import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

import build_client_patch as tool      # noqa: E402
import interface                       # noqa: E402
import mpq                             # noqa: E402
import sqlrows                         # noqa: E402
from dbc import LAYOUTS, Dbc           # noqa: E402

TOKENS = {1: "WARRIOR", 2: "PALADIN", 3: "HUNTER", 4: "ROGUE", 5: "PRIEST", 6: "DEATHKNIGHT", 7: "SHAMAN",
          8: "MAGE", 9: "WARLOCK", 11: "DRUID"}
RACES = [1, 2, 3, 4, 5, 6, 7, 8, 10, 11]
FAILS: list[str] = []


def check(cond, text):
    if not cond:
        FAILS.append(text)
        print("FAIL: " + text)


# --- a made-up client ------------------------------------------------------------------------------------------
def empty(fields: int, size: int, name: str) -> Dbc:
    return Dbc(struct.pack("<4s4I", b"WDBC", 0, fields, size, 1) + b"\0", name)


def table(layout: str, rows: list[dict]) -> bytes:
    spec = LAYOUTS[layout]["fields"]
    size = sum(1 if t == "byte" else 4 for _, t in spec)
    d = empty(len(spec), size, layout).use_layout(layout)
    for r in rows:
        d.put(d.encode([r.get(c, "" if t == "string" else 0) for c, t in spec]))
    return d.to_bytes()


def raw(fields: int, rows: list[tuple], fmt: str) -> bytes:
    size = struct.calcsize("<" + fmt)
    return (struct.pack("<4s4I", b"WDBC", len(rows), fields, size, 1)
            + b"".join(struct.pack("<" + fmt, *r) for r in rows) + b"\0")


def client_dbcs() -> dict[str, bytes]:
    d = {}
    d["ChrClasses.dbc"] = table("ChrClasses", [{"ID": c, "Name_Lang_enUS": t.title(), "Filename": t,
                                                "DisplayPower": 1 if c == 1 else 0} for c, t in TOKENS.items()])
    pairs = [(r, 1) for r in RACES if r != 10] + [(r, 2) for r in (1, 3, 10, 11)] + [(r, 6) for r in RACES]
    d["CharBaseInfo.dbc"] = raw(2, sorted(pairs), "2B")
    d["TalentTab.dbc"] = table("TalentTab", [{"ID": 161, "Name_Lang_enUS": "Arms", "ClassMask": 1}])
    d["Talent.dbc"] = table("Talent", [{"ID": 121, "TabID": 161, "SpellRank_1": 12294}])
    d["Spell.dbc"] = table("Spell", [{"ID": i, "Name_Lang_enUS": f"Spell {i}"} for i in (78, 201, 668, 12294)])
    # SkillLine: ID, category, ... (56 fields). 43 Swords (6), 26 Arms (7), 413 Mail (8), 98 Common (10)
    d["SkillLine.dbc"] = raw(56, [(sid, cat) + (0,) * 54 for sid, cat in ((26, 7), (43, 6), (98, 10), (413, 8))],
                             "56I")
    d["SkillRaceClassInfo.dbc"] = raw(8, [(1, 43, 0x6FF, 3, 0, 0, 0, 0), (2, 26, 0x6FF, 1, 0, 0, 0, 0),
                                          (3, 413, 0x6FF, 3, 0, 0, 0, 0), (4, 98, 1, 0xFFFFFFFF, 0, 0, 0, 0),
                                          (5, 43, 0x200, 2, 0, 0, 0, 0)], "8I")
    d["SkillLineAbility.dbc"] = raw(14, [(1, 43, 201, 0, 3) + (0,) * 9, (2, 26, 12294, 0, 1) + (0,) * 9,
                                         (3, 98, 668, 0, 0) + (0,) * 9], "14I")
    outfits, oid = [], 1
    for race in RACES:
        for gender in (0, 1):
            for cls in ((2,) if race == 10 else (1, 2) if race in (1, 3, 11) else (1,)):
                outfits.append((oid, race, cls, gender, 0) + tuple(range(100 * cls, 100 * cls + 24)) + (0,) * 48)
                oid += 1
    d["CharStartOutfit.dbc"] = raw(77, outfits, "I4B72i")
    d["CreatureDisplayInfo.dbc"] = table("CreatureDisplayInfo", [{"ID": 4312, "ModelID": 100, "CreatureModelScale": 1.0}])
    d["CreatureModelData.dbc"] = table("CreatureModelData", [{"ID": 100, "ModelName": "Creature\\Snake\\Snake.mdx"}])
    d["CreatureDisplayInfoExtra.dbc"] = table("CreatureDisplayInfoExtra", [{"ID": 1, "DisplayRaceID": 1}])
    for name, rows in (("gtChanceToMeleeCrit.dbc", 1100), ("gtChanceToSpellCrit.dbc", 1100), ("gtOCTRegenHP.dbc", 1100),
                       ("gtRegenHPPerSpt.dbc", 1100), ("gtRegenMPPerSpt.dbc", 1100),
                       ("gtChanceToMeleeCritBase.dbc", 11), ("gtChanceToSpellCritBase.dbc", 11)):
        d[name] = raw(1, [(float(i),) for i in range(rows)], "f")
    d["gtOCTClassCombatRatingScalar.dbc"] = raw(2, [(i, float(i) / 10) for i in range(1, 353)], "If")
    return d


CC_LUA = """-- stand-in for GlueXML CharacterCreate.lua (test only)
MAX_CLASSES_PER_RACE = 10;
CLASS_ICON_TCOORDS = {
@COORDS@
};
function CharacterCreateEnumerateClasses(...)
	CharacterCreate.numClasses = select("#", ...) / 3;
	if ( CharacterCreate.numClasses > MAX_CLASSES_PER_RACE ) then
		message("Too many classes!  Update MAX_CLASSES_PER_RACE");
		return;
	end
	local index = 1;
	for i = 1, select("#", ...), 3 do
		local coords = CLASS_ICON_TCOORDS[strupper(select(i + 1, ...))];
		_G["CharacterCreateClassButton"..index.."NormalTexture"]:SetTexCoord(coords[1], coords[2], coords[3], coords[4]);
		_G["CharacterCreateClassButton"..index.."PushedTexture"]:SetTexCoord(coords[1], coords[2], coords[3], coords[4]);
		index = index + 1;
	end
end
function SetCharacterClass(id)
	CharacterCreate.selectedClass = id;
	local className, classFileName = GetSelectedClass();
	local coords = CLASS_ICON_TCOORDS[classFileName];
	CharacterCreateClassIcon:SetTexCoord(coords[1], coords[2], coords[3], coords[4]);
end
""".replace("@COORDS@", ",\n".join(f'\t["{t}"] = {{0, 0.25, 0, 0.25}}' for t in TOKENS.values()))

CC_XML = """<Ui>
	<Script file="CharacterCreate.lua"/>
	<CheckButton name="CharacterCreateClassButtonTemplate" virtual="true"/>
	<Frame name="CharacterCreate">
		<Frames>
@BUTTONS@
		</Frames>
	</Frame>
</Ui>
""".replace("@BUTTONS@", "\n".join(
    f'\t\t\t<CheckButton name="CharacterCreateClassButton{i}" inherits="CharacterCreateClassButtonTemplate" id="{i}">\n'
    f'\t\t\t\t<Anchors>\n\t\t\t\t\t<Anchor point="LEFT" x="{i}" y="0"/>\n\t\t\t\t</Anchors>\n\t\t\t</CheckButton>'
    for i in range(1, 11)))


RAID_LUA = """-- stand-in for Blizzard_RaidUI.lua (test only)
RAID_SUBGROUP_LISTS = {};
RAID_CLASS_BUTTONS = { ["WARRIOR"] = { button = 1 } };
function RaidGroupFrame_Update(members)
	for i, j in next, RAID_SUBGROUP_LISTS do
		RAID_SUBGROUP_LISTS[i] = nil;
	end
	for index in pairs(RAID_CLASS_BUTTONS) do
		RAID_SUBGROUP_LISTS[index] = {};
	end
	for i, fileName in ipairs(members) do
		tinsert(RAID_SUBGROUP_LISTS[fileName], i);
	end
end
"""

CALENDAR_LUA = """-- stand-in for Blizzard_Calendar.lua (test only)
local CalendarClassData = { };
do
	for i, class in ipairs(CLASS_SORT_ORDER) do
		CalendarClassData[class] = { name = nil, counts = { [1] = 0, [2] = 0 } };
	end
end
function Calendar_Count(classFilename, status)
	CalendarClassData[classFilename].counts[status] = CalendarClassData[classFilename].counts[status] + 1;
	return CalendarClassData[classFilename].counts[status];
end
"""


def m2(name_textures: list[str], skins: int, sequences: list[tuple[int, int, int]]) -> bytes:
    """A skeleton WotLK model: header, sequences and texture table only."""
    head = bytearray(0x130)
    head[0:8] = b"MD20" + struct.pack("<I", 264)
    body = bytearray()
    seq_ofs = len(head)
    for anim, sub, flags in sequences:
        body += struct.pack("<2HIfI", anim, sub, 1000, 1.0, flags) + bytes(64 - 16)
    tex_ofs = seq_ofs + len(body)
    table_size = 16 * len(name_textures)
    names = bytearray()
    entries = bytearray()
    for n in name_textures:
        if n:
            entries += struct.pack("<4I", 0, 0, len(n) + 1, tex_ofs + table_size + len(names))
            names += n.encode() + b"\0"
        else:
            entries += struct.pack("<4I", 11, 0, 0, 0)
    struct.pack_into("<2I", head, 0x1C, len(sequences), seq_ofs)
    struct.pack_into("<I", head, 0x44, skins)
    struct.pack_into("<2I", head, 0x50, len(name_textures), tex_ofs)
    return bytes(head + body + entries + names)


def make_client(root: Path):
    data = root / "Data"
    (data / "enUS").mkdir(parents=True)
    files = {f"DBFilesClient\\{k}": v for k, v in client_dbcs().items()}
    files["Interface\\GlueXML\\CharacterCreate.lua"] = CC_LUA.encode()
    files["Interface\\GlueXML\\CharacterCreate.xml"] = b"\xef\xbb\xbf" + CC_XML.encode()
    files["Interface\\GlueXML\\GlueStrings.lua"] = b'CLASS_WARRIOR = "old";\n'
    files["Interface\\FrameXML\\Constants.lua"] = (b'RAID_CLASS_COLORS = {\n\t["WARRIOR"] = { r = 0.78, g = 0.61, b = 0.43 },\n};\n'
                                                   b'CLASS_ICON_TCOORDS = {\n\t["WARRIOR"] = {0, 0.25, 0, 0.25},\n};\n')
    files["Interface\\FrameXML\\WorldStateFrame.lua"] = b'CLASS_BUTTONS = {\n\t["WARRIOR"] = {0, 0.25, 0, 0.25},\n};\n'
    files["Interface\\AddOns\\Blizzard_RaidUI\\Blizzard_RaidUI.lua"] = RAID_LUA.encode()
    files["Interface\\AddOns\\Blizzard_Calendar\\Blizzard_Calendar.lua"] = CALENDAR_LUA.encode()
    files["Creature\\Snake\\Snake.m2"] = m2([], 1, [])
    mpq.write_archive(data / "enUS" / "locale-enUS.MPQ", files)
    mpq.write_archive(data / "common.MPQ", {"Creature\\Sethrak_Melee\\sethrak_melee_red.blp": b"BLP2 stock"})
    # a newer GlueStrings in a locale patch: the tool must patch this one
    mpq.write_archive(data / "enUS" / "patch-enUS-3.MPQ",
                      {"Interface\\GlueXML\\GlueStrings.lua": b'CLASS_WARRIOR = "locale patch 3";\n'})
    # an "HD patch" with its own CreatureDisplayInfo: the tool must extend it, not the clean copy
    cdi = Dbc(files["DBFilesClient\\CreatureDisplayInfo.dbc"], "x").use_layout("CreatureDisplayInfo")
    cdi.put(cdi.encode([60000, 100, 0, 0, 2.0, 255, "hd", "", "", "", 0, 0, 0, 0, 0, 0]))
    mpq.write_archive(data / "patch-A.MPQ", {"DBFilesClient\\CreatureDisplayInfo.dbc": cdi.to_bytes()})
    # an earlier Devourer patch (would clash: ChrClasses with class 10) and an archive the client never loads
    old = Dbc(files["DBFilesClient\\ChrClasses.dbc"], "x").use_layout("ChrClasses")
    old.put(old.encode([10] + [0] * 59))
    mpq.write_archive(data / "patch-Y.MPQ", {tool.MARKER: b"old", "DBFilesClient\\ChrClasses.dbc": old.to_bytes()})
    mpq.write_archive(data / "backup.MPQ", {"DBFilesClient\\ChrClasses.dbc": old.to_bytes()})


def make_coa(root: Path, committed: list[Path]) -> tuple[Path, Path]:
    loose = root / "coa-loose"
    (loose / "DBFilesClient").mkdir(parents=True)
    cdi = [{"ID": 80018, "ModelID": 402214, "CreatureModelScale": 1.0, "TextureVariation_1": "sethrak_camp"},
           {"ID": 80305, "ModelID": 402215, "ExtendedDisplayInfoID": 7, "CreatureModelScale": 1.0},
           {"ID": 200004, "ModelID": 402214, "CreatureModelScale": 1.0, "TextureVariation_1": "sethrak_melee_red"},
           {"ID": 280018, "ModelID": 402214, "CreatureModelScale": 1.5},
           {"ID": 991040, "ModelID": 402216, "CreatureModelScale": 1.0},
           {"ID": 991045, "ModelID": 402216, "CreatureModelScale": 0.8}]
    (loose / "DBFilesClient" / "CreatureDisplayInfo.dbc").write_bytes(table("CreatureDisplayInfo", cdi))
    cmd = [{"ID": 402214, "ModelName": "Creature\\Sethrak_Melee\\Sethrak_Melee.mdx", "ModelScale": 1.0},
           {"ID": 402215, "ModelName": "Creature\\SethrakCaster\\SethrakCaster.mdx", "ModelScale": 1.0},
           {"ID": 402216, "ModelName": "Creature\\Twinfangs\\Twinfangs.mdx", "ModelScale": 1.0}]
    (loose / "DBFilesClient" / "CreatureModelData.dbc").write_bytes(table("CreatureModelData", cmd))
    (loose / "DBFilesClient" / "CreatureDisplayInfoExtra.dbc").write_bytes(
        table("CreatureDisplayInfoExtra", [{"ID": 7, "DisplayRaceID": 8, "BakeName": "sethrak.blp"}]))

    files = {}
    models = [v["ModelName"] for v in cmd] + [v["ModelName"] for v in
                                               sqlrows.table_rows(committed, "creaturemodeldata_dbc").values()]
    for model in models:
        base = model.rsplit(".", 1)[0]
        folder = base.rsplit("\\", 1)[0]
        files[base + ".m2"] = m2([folder + "\\own_texture.blp", ""], 2, [(0, 0, 0x20), (5, 0, 0), (6, 1, 0x40)])
        files[base + "00.skin"] = b"SKIN0"
        files[base + "01.skin"] = b"SKIN1"
        files[base + "0005-00.anim"] = b"ANIM"
        files[folder + "\\own_texture.blp"] = b"BLP2 own"
    for row in sqlrows.table_rows(committed, "creaturedisplayinfo_dbc").values():
        model = next(v["ModelName"] for v in list(sqlrows.table_rows(committed, "creaturemodeldata_dbc").values()) + cmd
                     if v["ID"] == row["ModelID"])
        folder = model.rsplit("\\", 1)[0]
        for tex in (row["TextureVariation_1"], row["TextureVariation_2"], row["TextureVariation_3"]):
            if tex and tex != "berserker_teal_skin":            # one texture left out on purpose
                files[f"{folder}\\{tex}.blp"] = b"BLP2 " + tex.encode()
    files["Creature\\Sethrak_Melee\\sethrak_camp.blp"] = b"BLP2 camp"
    files["Textures\\BakedNpcTextures\\sethrak.blp"] = b"BLP2 baked"
    archive = root / "coa-patch-T.MPQ"
    mpq.write_archive(archive, files)
    return loose, archive


# --- checks ------------------------------------------------------------------------------------------------
def same(a, b, kind) -> bool:
    if kind == "float":
        return abs(float(a or 0) - float(b or 0)) < 1e-6
    if kind == "string":
        return (a or "") == (b or "")
    return (int(a or 0) & 0xFFFFFFFF) == (int(b or 0) & 0xFFFFFFFF)


def lua_test(patched: Path, work: Path):
    lua = shutil.which("lua5.1") or shutil.which("lua51")
    if not lua:
        print("(no lua5.1: the character creation code was only syntax-checked)")
        return
    harness = r"""
local function Texture(file)
	return { file = file, coords = nil,
		GetTexture = function(self) return self.file end,
		SetTexture = function(self, f) self.file = f end,
		SetTexCoord = function(self, a, b, c, d) self.coords = {a, b, c, d} end }
end
CharacterCreate = {}
strupper = string.upper
function message(text) error("message: "..text) end
local ATLAS = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-Classes"
for i = 1, 11 do
	_G["CharacterCreateClassButton"..i.."NormalTexture"] = Texture(ATLAS)
	_G["CharacterCreateClassButton"..i.."PushedTexture"] = Texture(ATLAS)
end
CharacterCreateClassIcon = Texture(ATLAS)
dofile(arg[1])
assert(MAX_CLASSES_PER_RACE == 11, "MAX_CLASSES_PER_RACE")
local ICON = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-Devourer"
local order = {"Warrior","WARRIOR",1, "Paladin","PALADIN",1, "Hunter","HUNTER",1, "Rogue","ROGUE",1,
	"Priest","PRIEST",1, "Death Knight","DEATHKNIGHT",1, "Shaman","SHAMAN",1, "Mage","MAGE",1,
	"Warlock","WARLOCK",1, "Devourer","DEVOURER",1, "Druid","DRUID",1}
CharacterCreateEnumerateClasses(unpack(order))
local b10 = CharacterCreateClassButton10NormalTexture
assert(b10.file == ICON and b10.coords[2] == 1 and b10.coords[4] == 1, "button 10 shows the Devourer")
assert(CharacterCreateClassButton10PushedTexture.file == ICON, "pushed texture too")
assert(CharacterCreateClassButton11NormalTexture.file == ATLAS, "button 11 keeps the class sheet")
assert(CharacterCreateClassButton11NormalTexture.coords[2] == 0.25, "button 11 has the druid's coords")
-- a list without the Devourer: button 10 goes back to the sheet
local short = {}
for i = 1, 27 do short[i] = order[i] end
short[28], short[29], short[30] = "Druid", "DRUID", 1
CharacterCreateEnumerateClasses(unpack(short))
assert(b10.file == ATLAS and b10.coords[2] == 0.25, "button 10 restored")
GetSelectedClass = function() return "Devourer", "DEVOURER" end
SetCharacterClass(10)
assert(CharacterCreateClassIcon.file == ICON, "class icon is the Devourer's")
GetSelectedClass = function() return "Warrior", "WARRIOR" end
SetCharacterClass(1)
assert(CharacterCreateClassIcon.file == ATLAS and CharacterCreateClassIcon.coords[2] == 0.25, "class icon restored")
print("lua ok")
"""
    h = work / "harness.lua"
    h.write_text(harness)
    res = subprocess.run([lua, str(h), str(patched)], capture_output=True, text=True)
    check(res.returncode == 0 and "lua ok" in res.stdout, f"Lua run: {res.stdout}{res.stderr}")
    for extra in ("Constants.lua", "WorldStateFrame.lua", "GlueStrings.lua"):
        p = next((patched.parent.parent).rglob(extra))
        res = subprocess.run([lua, str(p)], capture_output=True, text=True)
        check(res.returncode == 0, f"{extra} runs: {res.stderr}")
    addons = patched.parent.parent / "AddOns"
    raid = work / "raid.lua"
    raid.write_text("tinsert = table.insert\n"
                    f"dofile([[{addons / 'Blizzard_RaidUI' / 'Blizzard_RaidUI.lua'}]])\n"
                    'RaidGroupFrame_Update({"WARRIOR", "DEVOURER", "DEVOURER"})\n'
                    'RaidGroupFrame_Update({"DEVOURER", "WARRIOR"})\n'
                    'assert(#RAID_SUBGROUP_LISTS["DEVOURER"] == 1 and #RAID_SUBGROUP_LISTS["WARRIOR"] == 1)\n'
                    'assert(RAID_SUBGROUP_LISTS["MAGE"] == nil)\nprint("raid ok")\n')
    res = subprocess.run([lua, str(raid)], capture_output=True, text=True)
    check("raid ok" in res.stdout, f"raid frame with a Devourer: {res.stderr}")
    cal = work / "calendar.lua"
    cal.write_text('CLASS_SORT_ORDER = {"WARRIOR"}\nCLASS_ICON_TCOORDS = {}\n'
                   f"dofile([[{addons / 'Blizzard_Calendar' / 'Blizzard_Calendar.lua'}]])\n"
                   'assert(Calendar_Count("DEVOURER", 2) == 1 and Calendar_Count("DEVOURER", 2) == 2)\n'
                   'assert(Calendar_Count("WARRIOR", 1) == 1)\nprint("calendar ok")\n')
    res = subprocess.run([lua, str(cal)], capture_output=True, text=True)
    check("calendar ok" in res.stdout, f"calendar with a Devourer: {res.stderr}")


def main() -> int:
    keep = "--keep" in sys.argv
    tmp = Path(tempfile.mkdtemp(prefix="devourer-selftest-"))
    committed = sorted(p for p in tool.SQL_DIR.glob("2026_09_30_0*.sql") if ".generated." not in p.name)
    try:
        client = tmp / "WoW"
        make_client(client)
        loose, coa_mpq = make_coa(tmp, committed)
        sql_dir, out = tmp / "sql", tmp / "out"
        rc = tool.main(["--client", str(client), "--coa", str(loose), "--coa", str(coa_mpq), "--install",
                        "--out", str(out), "--sql-dir", str(sql_dir)])
        check(rc == 0, "build succeeded")
        if rc:
            return 1
        data = client / "Data"
        check((data / "patch-Z.MPQ").exists(), "installed as Data/patch-Z.MPQ")
        check(not (data / "patch-Y.MPQ").exists(), "the earlier Devourer patch was removed")
        check((data / "backup.MPQ").exists(), "unrelated archives are left alone")
        arc = mpq.Archive(data / "patch-Z.MPQ")
        check(arc.has(tool.MARKER), "marker file")

        def dbc(name, layout=None):
            d = Dbc(arc.read("DBFilesClient\\" + name), name)
            return d.use_layout(layout) if layout else d

        # rows of the committed SQL, byte-equal values
        for layout, spec in LAYOUTS.items():
            rows = sqlrows.table_rows(committed, spec["table"])
            if not rows:
                continue
            d = dbc(layout + ".dbc", layout)
            kinds = dict(spec["fields"])
            for rid, row in rows.items():
                rec = d.find(rid)
                check(rec is not None, f"{layout} {rid} present")
                if rec is None:
                    continue
                got = dict(zip(d.columns(), d.decode(rec)))
                expected = dict(zip(d.columns(), tool.client_strings([row.get(c) for c in d.columns()],
                                                                     d.columns())))
                for col in row:
                    want = expected[col]                 # the SQL's value; empty locale slots get the enUS text
                    check(same(got[col], want, kinds[col]), f"{layout} {rid} {col}: {got[col]!r} != {want!r}")
                if "Name_Lang_enUS" in got and got["Name_Lang_enUS"]:
                    check(got["Name_Lang_deDE"] == got["Name_Lang_enUS"], f"{layout} {rid}: locale slots filled")
            ids = [Dbc.rid(r) for r in d.records]
            check(ids == sorted(ids), f"{layout}: sorted by id")

        cdi = dbc("CreatureDisplayInfo.dbc", "CreatureDisplayInfo")
        check(cdi.find(60000) is not None, "the HD patch's display row is kept")
        for did in (80018, 80305, 200004, 280018, 991040, 991045):
            check(cdi.find(did) is not None, f"CoA display {did} copied")
        cmd = dbc("CreatureModelData.dbc", "CreatureModelData")
        for mid in (402214, 402215, 402216):
            check(cmd.find(mid) is not None, f"CoA model {mid} copied")
        check(dbc("CreatureDisplayInfoExtra.dbc", "CreatureDisplayInfoExtra").find(7) is not None, "CoA extra 7")

        cbi = dbc("CharBaseInfo.dbc")
        pairs = {(r[0], r[1]) for r in cbi.records}
        check(all((r, 10) in pairs for r in RACES), "CharBaseInfo: every race may be a Devourer")
        check(len(cbi.records) == len(pairs), "CharBaseInfo: no duplicates")

        rci = dbc("SkillRaceClassInfo.dbc")
        masks = {rci.words(i)[0]: rci.words(i)[3] for i in range(len(rci.records))}
        check(masks[1] == 3 | 512 and masks[3] == 3 | 512, "SkillRaceClassInfo: warrior skills get class 10")
        check(masks[2] == 1 and masks[5] == 2 and masks[4] == 0xFFFFFFFF, "SkillRaceClassInfo: others unchanged")
        sla = dbc("SkillLineAbility.dbc")
        check({sla.words(i)[0]: sla.words(i)[4] for i in range(3)} == {1: 3 | 512, 2: 1, 3: 0}, "SkillLineAbility")
        cso = dbc("CharStartOutfit.dbc")
        dev = [struct.unpack_from("<I4B3i", r) for r in cso.records if r[5] == 10]
        check(len(dev) == 2 * len(RACES), "CharStartOutfit: an outfit per race and gender")
        check(all(o[5] == (200 if o[1] == 10 else 100) for o in dev), "CharStartOutfit: warrior's, else paladin's")

        melee = dbc("gtChanceToMeleeCrit.dbc")
        vals = [struct.unpack("<f", r)[0] for r in melee.records]
        check(vals[900:1000] == vals[0:100] and vals[1000] == 1000.0, "gtChanceToMeleeCrit: class 10 = warrior")
        base = dbc("gtChanceToMeleeCritBase.dbc")
        check(struct.unpack("<f", base.records[9])[0] == 0.0, "gtChanceToMeleeCritBase")
        scalar = dbc("gtOCTClassCombatRatingScalar.dbc")
        sv = {struct.unpack("<If", r)[0]: struct.unpack("<If", r)[1] for r in scalar.records}
        check(all(abs(sv[288 + k] - sv[k]) < 1e-6 for k in range(1, 33)) and abs(sv[321] - 32.1) < 1e-4,
              "gtOCTClassCombatRatingScalar: class 10 = warrior")

        # models and textures from the CoA sources
        for path in ("Creature\\Berserker\\berserker.m2", "Creature\\Berserker\\berserker00.skin",
                     "Creature\\Berserker\\berserker01.skin", "Creature\\Berserker\\berserker0005-00.anim",
                     "Creature\\Berserker\\own_texture.blp", "Creature\\Sethrak_Melee\\Sethrak_Melee.m2",
                     "Creature\\Sethrak_Melee\\devourer_sethrak_ember.blp", "Creature\\Sethrak_Melee\\sethrak_camp.blp",
                     "Creature\\Twinfangs\\Twinfangs.m2", "Textures\\BakedNpcTextures\\sethrak.blp"):
            check(arc.has(path), f"asset {path}")
        check(not arc.has("Creature\\Berserker\\berserker0006-01.anim"), "no .anim for an alias sequence")
        check(not arc.has("Creature\\Sethrak_Melee\\sethrak_melee_red.blp"), "textures the client has are not copied")
        report = (out / "report.txt").read_text()
        check("berserker_teal_skin.blp" in report, "a missing texture is reported")

        # interface
        glue = arc.read("Interface\\GlueXML\\GlueStrings.lua").decode()
        check("locale patch 3" in glue and "CLASS_DEVOURER" in glue, "GlueStrings patched from the locale patch")
        xml = arc.read("Interface\\GlueXML\\CharacterCreate.xml")
        check(xml.startswith(b"\xef\xbb\xbf"), "XML keeps its BOM")
        import xml.etree.ElementTree as ET
        root = ET.fromstring(xml[3:].decode())
        b11 = root.find(".//CheckButton[@name='CharacterCreateClassButton11']")
        check(b11 is not None and b11.get("inherits") == "CharacterCreateClassButtonTemplate", "button 11 in XML")
        check(arc.read(interface.ICON_PATH + ".blp")[:4] == b"BLP2", "class icon")
        lua_test(out / "files" / "Interface" / "GlueXML" / "CharacterCreate.lua", tmp)

        # SQL
        generated = (sql_dir / tool.CLASS_SQL).read_text()
        pristine = tmp / "dbc"
        pristine.mkdir()
        for name, blob in client_dbcs().items():
            (pristine / name).write_bytes(blob)
        server = tmp / "server.sql"
        subprocess.run([sys.executable, str(HERE.parent / "build_class_dbc_sql.py"), "--dbc", str(pristine),
                        "--out", str(server)], check=True, capture_output=True)
        check(generated.split("\n")[1:] == server.read_text().split("\n")[1:],
              "the client tool writes the same class SQL as tools/build_class_dbc_sql.py")
        looks = (sql_dir / tool.LOOKS_SQL).read_text()
        for did in (80018, 80305, 200004, 280018, 991040, 991045, 402214):
            check(str(did) in looks, f"looks SQL has {did}")
        check("devourer_client_rows" in looks, "looks SQL records its rows for the uninstall")

        # running it again replaces the installed patch (it is excluded as a source)
        rc = tool.main(["--client", str(client), "--coa", str(loose), "--coa", str(coa_mpq), "--install",
                        "--out", str(out), "--sql-dir", str(sql_dir)])
        check(rc == 0, "a second build over the installed patch works")
    finally:
        if keep:
            print(f"kept {tmp}")
        else:
            shutil.rmtree(tmp, ignore_errors=True)
    print("\nSELFTEST " + ("PASSED" if not FAILS else f"FAILED ({len(FAILS)})"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
