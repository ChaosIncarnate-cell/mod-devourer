#!/usr/bin/env python3
"""Builds the Devourer's client patch (one MPQ) from the owner's own 3.3.5a client, plus the server SQL that must
match it (task 004).

    python tools/client/build_client_patch.py --client "C:\\WoW" [--coa "D:\\CoA\\Data"] [--class-icon emblem.png]
                                              [--name patch-Z.MPQ] [--install]

It reads every file from the client's archives in the client's own load order, so what it changes is what the
game really uses (an HD patch's CreatureDisplayInfo.dbc, for example, is extended, not replaced by a clean copy).
Nothing it reads or writes is committed; all output goes to tools/client/out/ (git-ignored), the client's Data
folder (--install) and two git-ignored SQL files.

What goes into the MPQ:
  DBFilesClient  ChrClasses (class 10), CharBaseInfo (every race may be a Devourer), TalentTab/Talent, Spell,
                 CreatureDisplayInfo/CreatureModelData (the rows of the committed SQL, byte for byte the same
                 values the server gets), SkillRaceClassInfo/SkillLineAbility/CharStartOutfit (the warrior's skills
                 and outfit for class 10, same rules as tools/build_class_dbc_sql.py), the gt* tables (class 10
                 = the warrior, as 2026_09_30_01 does on the server), and the looks that only exist in the CoA
                 client (Sethrak 200004 and the Sethrak camp) copied from it (--coa)
  Interface      GlueXML/FrameXML changes (interface.py) and the class icon
  Creature\\...   the models and textures of the Devourer's looks, copied from the CoA client (--coa)

SQL it writes into data/sql/db-world/ (both git-ignored, applied by the worldserver like the module's other SQL):
  2026_09_30_05_devourer_class_dbc.generated.sql   the same file tools/build_class_dbc_sql.py writes, from the
                                                   client's DBCs
  2026_09_30_06_devourer_coa_looks.generated.sql   the display/model rows copied from the CoA client

Needs Python 3.9+ and Pillow (python -m pip install pillow). No StormLib: mpq.py reads and writes MPQs.
"""
from __future__ import annotations

import argparse
import datetime
import re
import shutil
import struct
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "tools"))

import blp                                   # noqa: E402
import build_class_dbc_sql as rules          # noqa: E402  (tools/build_class_dbc_sql.py)
import interface                             # noqa: E402
import mpq                                   # noqa: E402
import sqlrows                               # noqa: E402
from dbc import LAYOUTS, Dbc                  # noqa: E402

CLASS_ID = rules.CLASS_ID
WARRIOR = 1
MARKER = "Devourer\\patch.txt"               # identifies an MPQ this tool wrote
DEFAULT_NAME = "patch-Z.MPQ"
SQL_DIR = REPO / "data" / "sql" / "db-world"
CLASS_SQL = rules.OUT_NAME                   # 2026_09_30_05_devourer_class_dbc.generated.sql
LOOKS_SQL = "2026_09_30_06_devourer_coa_looks.generated.sql"
LOCALES = ["enUS", "enGB", "koKR", "frFR", "deDE", "enCN", "zhCN", "enTW", "zhTW", "esES", "esMX", "ruRU",
           "ptPT", "ptBR", "itIT", "Unk"]
LOCALE_DIRS = ["enUS", "enGB", "deDE", "frFR", "esES", "esMX", "ruRU", "koKR", "zhCN", "zhTW", "enCN", "enTW",
               "ptBR", "ptPT", "itIT"]
PATCH_SUFFIXES = [""] + [f"-{c}" for c in "23456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"]

# gt tables the server install copies from the warrior (2026_09_30_01_devourer_class.sql): (file, first row of
# class 10, first row of the warrior, rows per class). One-field files are indexed by row, two-field ones by ID.
GT_TABLES = [
    ("gtChanceToMeleeCrit.dbc", 900, 0, 100),
    ("gtChanceToSpellCrit.dbc", 900, 0, 100),
    ("gtOCTRegenHP.dbc", 900, 0, 100),
    ("gtRegenHPPerSpt.dbc", 900, 0, 100),
    ("gtRegenMPPerSpt.dbc", 900, 0, 100),
    ("gtChanceToMeleeCritBase.dbc", 9, 0, 1),
    ("gtChanceToSpellCritBase.dbc", 9, 0, 1),
    ("gtOCTClassCombatRatingScalar.dbc", 289, 1, 32),
]


class BuildError(Exception):
    pass


# --- where files come from ---------------------------------------------------------------------------------
class Folder:
    """Loose files below a folder (e.g. an extracted CoA patch), looked up case-insensitively."""

    def __init__(self, root: Path):
        self.root, self.label = root, str(root)
        self.index = {str(p.relative_to(root)).replace("/", "\\").lower(): p for p in root.rglob("*") if p.is_file()}

    def has(self, name: str) -> bool:
        return name.replace("/", "\\").lower() in self.index

    def read(self, name: str) -> bytes | None:
        p = self.index.get(name.replace("/", "\\").lower())
        return p.read_bytes() if p else None


class MpqSource:
    def __init__(self, path: Path):
        self.path, self.label = path, path.name
        self.archive = mpq.Archive(path)

    def has(self, name: str) -> bool:
        return self.archive.has(name)

    def read(self, name: str) -> bytes | None:
        return self.archive.read(name)


class Layers:
    """Sources from lowest to highest priority: the last one that has a file wins, like the client."""

    def __init__(self, sources: list):
        self.sources = sources

    def find(self, name: str):
        for src in reversed(self.sources):
            if src.has(name):
                return src
        return None

    def has(self, name: str) -> bool:
        return self.find(name) is not None

    def read(self, name: str) -> bytes | None:
        src = self.find(name)
        return src.read(name) if src else None

    def origin(self, name: str) -> str:
        src = self.find(name)
        return src.label if src else "-"


def load_order(locale: str) -> list[tuple[bool, str]]:
    """Every archive name the client loads, lowest priority first, as (in the locale folder, lower-case name).

    Order as AzerothCore's map extractor opens them (src/tools/map_extractor, later ones win): the base archives,
    the locale archives and locale patches, then Data\\patch*.MPQ; custom patches load after the numbered ones,
    letters after digits.
    """
    lc = locale.lower()
    order = [(False, n) for n in ("common.mpq", "common-2.mpq", "expansion.mpq", "lichking.mpq")]
    order += [(True, n) for n in (f"locale-{lc}.mpq", f"speech-{lc}.mpq", f"expansion-locale-{lc}.mpq",
                                  f"lichking-locale-{lc}.mpq", f"expansion-speech-{lc}.mpq", f"lichking-speech-{lc}.mpq")]
    order += [(True, f"patch-{lc}{s.lower()}.mpq") for s in PATCH_SUFFIXES]
    order += [(False, f"patch{s.lower()}.mpq") for s in PATCH_SUFFIXES]
    return order


def client_archives(data: Path, locale: str) -> tuple[list[Path], list[Path]]:
    """The client's archives in load order (lowest priority first), and MPQs the client does not load."""
    def mpqs(folder: Path) -> dict[str, Path]:
        return {p.name.lower(): p for p in folder.iterdir() if p.is_file() and p.suffix.lower() == ".mpq"} \
            if folder.is_dir() else {}

    found = {False: mpqs(data), True: mpqs(data / locale)}
    order = [found[in_loc].pop(name) for in_loc, name in load_order(locale) if name in found[in_loc]]
    return order, sorted(found[False].values()) + sorted(found[True].values())


def rank(path: Path, data: Path, locale: str) -> int:
    key = (path.parent != data, path.name.lower())
    order = load_order(locale)
    return order.index(key) if key in order else -1


def detect_locale(data: Path) -> str:
    for loc in LOCALE_DIRS:
        folder = data / loc
        if folder.is_dir() and any(p.name.lower() == f"locale-{loc.lower()}.mpq" for p in folder.iterdir()):
            return loc
    raise BuildError(f"no locale folder with locale-xxXX.MPQ in {data}; pass --locale")


def coa_layers(paths: list[Path]) -> Layers:
    """--coa arguments, lowest priority first: an MPQ, a folder of MPQs (loaded in client order), or loose files."""
    sources = []
    for p in paths:
        if p.is_file():
            sources.append(MpqSource(p))
        elif p.is_dir():
            loc = next((l for l in LOCALE_DIRS if (p / l).is_dir()), "enUS")
            archives, extra = client_archives(p, loc)
            archives += [a for a in extra if a.parent == p]         # CoA's own patch names (patch-TZ ...)
            if archives:
                sources += [MpqSource(a) for a in archives]
            else:
                sources.append(Folder(p))
        else:
            raise BuildError(f"--coa {p}: not found")
    return Layers(sources)


# --- reporting ---------------------------------------------------------------------------------------------
class Report:
    def __init__(self):
        self.lines: list[str] = []
        self.warnings: list[str] = []

    def info(self, text: str):
        self.lines.append(text)
        print(text)

    def warn(self, text: str):
        self.warnings.append(text)
        print("WARNING: " + text)


# --- SQL helpers -------------------------------------------------------------------------------------------
def sql_value(v, kind: str) -> str:
    if kind == "string":
        return "'" + (v or "").replace("\\", "\\\\").replace("'", "''") + "'"
    if kind == "float":
        return f32(v)
    return str(v)


def f32(v) -> str:
    """The shortest decimal that is the same 32-bit float (DBC floats are 32-bit)."""
    packed = struct.pack("<f", float(v))
    for digits in range(1, 10):
        text = f"{float(v):.{digits}g}"
        if struct.pack("<f", float(text)) == packed:
            return text if any(c in text for c in ".e") else text + ".0"
    return repr(float(v))


def sql_rows(table: str, layout, rows: list[list]) -> list[str]:
    cols = ", ".join(f"`{c}`" for c, _ in layout)
    ids = ", ".join(str(r[0]) for r in rows)
    return [f"DELETE FROM `{table}` WHERE `ID` IN ({ids});",
            f"INSERT INTO `{table}` ({cols}) VALUES",
            ",\n".join("(" + ", ".join(sql_value(v, k) for v, (_, k) in zip(r, layout)) + ")" for r in rows) + ";",
            "INSERT IGNORE INTO `devourer_client_rows` (`tbl`, `ID`) VALUES "
            + ", ".join(f"('{table}', {r[0]})" for r in rows) + ";", ""]


# --- the build ---------------------------------------------------------------------------------------------
class Builder:
    def __init__(self, client: Layers, coa: Layers | None, report: Report):
        self.client, self.coa, self.report = client, coa, report
        self.files: dict[str, bytes] = {}
        self.dbcs: dict[str, Dbc] = {}
        self.added: dict[str, set[int]] = {}          # ids of the rows the patch adds, per DBC
        self.missing: list[str] = []
        self.baked: list[str] = []                     # baked NPC textures of dressed looks copied from CoA
        # Task 017: the evolved forms' spells live in their own file (tools/evolved_kit.py).
        self.committed = sorted(p for p in [*SQL_DIR.glob("2026_09_30_0*.sql"), *SQL_DIR.glob("*_devourer_tier2.sql")]
                                if ".generated." not in p.name)
        self.class_sql: list[str] = []
        self.overwrite_reserved = False                # --overwrite-reserved
        self.own_client = client                       # the client without --foreign patches: a model the patch
                                                       # needs is carried unless this has it
        self.looks_sql: list[str] = []

    # DBCs ------------------------------------------------------------------------------------------------
    def pristine(self, name: str) -> bytes:
        data = self.client.read("DBFilesClient\\" + name)
        if data is None:
            raise BuildError(f"DBFilesClient\\{name} not found in the client's archives")
        return data

    def dbc(self, name: str, layout: str | None = None) -> Dbc:
        if name not in self.dbcs:
            self.dbcs[name] = Dbc(self.pristine(name), name)
            self.added[name] = set()
            origin = self.client.origin("DBFilesClient\\" + name)
            self.report.info(f"  {name} from {origin}")
        d = self.dbcs[name]
        if layout and d.layout is None:
            d.use_layout(layout)
        return d

    def load_rules(self, name: str):
        return rules.Dbc(self.pristine(name), name)

    def build_dbcs(self):
        r = self.report
        r.info("DBCs (client copies):")
        taken = rules.taken_ids(self.load_rules)
        if taken and not self.overwrite_reserved:
            raise BuildError("ids the Devourer uses are already taken in the client's DBCs:\n  " + "\n  ".join(taken)
                             + "\n  (copies of an earlier Devourer patch inside another patch? then run again with "
                               "--overwrite-reserved)")
        if taken:
            r.warn("ids in the Devourer's ranges found in the client's DBCs (--overwrite-reserved: the Devourer's "
                   "rows replace them):\n    " + "\n    ".join(taken))

        # rows of the committed SQL, the same values the server gets
        for dbc_name, spec in sorted(LAYOUTS.items()):
            rows = sqlrows.table_rows(self.committed, spec["table"])
            if not rows:
                continue
            d = self.dbc(dbc_name + ".dbc", dbc_name)
            cols = d.columns()
            for rid, row in sorted(rows.items()):
                unknown = set(row) - set(cols)
                if unknown:
                    raise BuildError(f"{spec['table']} {rid}: unknown columns {sorted(unknown)}")
                if d.find(rid) is not None and not (self.overwrite_reserved and self.reserved(dbc_name, rid)):
                    raise BuildError(f"{dbc_name}.dbc already has id {rid}")
                self.add(d, d.encode(client_strings([row.get(c) for c in cols], cols)))
            r.info(f"    {dbc_name}: {len(rows)} rows from the module's SQL")

        # the warrior's skills and outfit (tools/build_class_dbc_sql.py rules)
        class_lines = rules.class_skill_lines(self.load_rules)
        rci = rules.race_class_rows(self.load_rules, class_lines)
        sla = rules.ability_rows(self.load_rules, class_lines)
        cso = rules.outfit_rows(self.load_rules)
        for name, layout, rows in (("SkillRaceClassInfo.dbc", "SkillRaceClassInfo", rci),
                                   ("SkillLineAbility.dbc", "SkillLineAbility", sla),
                                   ("CharStartOutfit.dbc", "CharStartOutfit", cso)):
            d = self.dbc(name, layout)
            for row in rows:
                d.put(d.encode(list(row)))
            r.info(f"    {layout}: {len(rows)} rows for class {CLASS_ID}")
        self.class_sql = rules.sql_lines(rci, sla, cso, "tools/client/build_client_patch.py from the client's")

        self.build_gt()
        self.build_char_base_info()

    @staticmethod
    def reserved(dbc_name: str, rid: int) -> bool:
        """Is this id inside the Devourer's reserved range of that DBC (tools/build_class_dbc_sql.py RESERVED)?"""
        return any(name == dbc_name + ".dbc" and any(lo <= rid <= hi for lo, hi in ranges)
                   for name, ranges in rules.RESERVED)

    def add(self, d: Dbc, rec: bytes):
        d.put(rec)
        self.added[d.name].add(Dbc.rid(rec))

    def build_gt(self):
        for name, first, warrior, count in GT_TABLES:
            d = self.dbc(name)
            if d.fields == 1:
                index = {i: i for i in range(len(d.records))}
            elif d.fields == 2:
                index = {Dbc.rid(rec): i for i, rec in enumerate(d.records)}
            else:
                raise BuildError(f"{name}: {d.fields} fields, expected 1 or 2")
            for k in range(count):
                src, dst = index.get(warrior + k), index.get(first + k)
                if src is None or dst is None:
                    raise BuildError(f"{name}: row {warrior + k} or {first + k} missing")
                value = d.records[src][-4:]
                d.records[dst] = d.records[dst][:-4] + value
        self.report.info(f"    gt tables: class {CLASS_ID} = the warrior ({len(GT_TABLES)} files)")

    def build_char_base_info(self):
        d = self.dbc("CharBaseInfo.dbc")
        if d.size != 2:
            raise BuildError(f"CharBaseInfo.dbc: record size {d.size}, expected 2")
        pairs = {(rec[0], rec[1]) for rec in d.records}
        races = sorted({race for race, _ in pairs})
        pairs |= {(race, CLASS_ID) for race in races}
        d.records = [bytes(p) for p in sorted(pairs)]
        self.report.info(f"    CharBaseInfo: class {CLASS_ID} for races {races}")

    # looks that only exist in the CoA client ---------------------------------------------------------------
    def wanted_displays(self) -> set[int]:
        want = set()
        for table, column in (("creature_model_info", "DisplayID"), ("creature_template_model", "CreatureDisplayID"),
                              ("devourer_shape", "display_id"), ("devourer_shape", "brood_display"),
                              ("devourer_skin", "display_id"), ("devourer_skin", "brood_display"),
                              ("devourer_shape_source", "display_id")):
            want |= sqlrows.column_values(self.committed, table, column)
        return {d for d in want if d}

    def own_dbc(self, name: str, layout: str) -> Dbc:
        """A DBC as the client has it without --foreign patches: what the patch must bring itself."""
        if self.own_client is self.client:
            return self.dbc(name, layout)
        data = self.own_client.read("DBFilesClient\\" + name)
        if data is None:
            raise BuildError(f"DBFilesClient\\{name} not found in the client's archives")
        return Dbc(data, name).use_layout(layout)

    def build_looks(self):
        r = self.report
        self.dbc("CreatureDisplayInfo.dbc", "CreatureDisplayInfo")          # the tables the patch extends
        self.dbc("CreatureModelData.dbc", "CreatureModelData")
        cdi = self.own_dbc("CreatureDisplayInfo.dbc", "CreatureDisplayInfo")
        cmd = self.own_dbc("CreatureModelData.dbc", "CreatureModelData")
        from_sql = set(sqlrows.table_rows(self.committed, "creaturedisplayinfo_dbc"))   # the module's own looks
        need = sorted(d for d in self.wanted_displays() if d not in from_sql and cdi.find(d) is None)
        coa_rows: dict[str, list[list]] = {"CreatureDisplayInfo": [], "CreatureModelData": [],
                                           "CreatureDisplayInfoExtra": []}
        if need:
            if not self.coa:
                r.warn(f"looks {need} are in neither the module's SQL nor the client: pass --coa to copy them "
                       "from the CoA client (without them those creatures and shapes have no model)")
            else:
                coa_cdi = self.coa_dbc("CreatureDisplayInfo")
                coa_cmd = self.coa_dbc("CreatureModelData")
                coa_extra = None
                for did in need:
                    rec = coa_cdi.find(did) if coa_cdi else None
                    if rec is None:
                        r.warn(f"display {did}: not in the CoA client's CreatureDisplayInfo.dbc either")
                        continue
                    values = coa_cdi.decode(rec)
                    coa_rows["CreatureDisplayInfo"].append(values)
                    extra = values[3]
                    if extra and self.own_dbc("CreatureDisplayInfoExtra.dbc", "CreatureDisplayInfoExtra").find(extra) is None:
                        coa_extra = coa_extra or self.coa_dbc("CreatureDisplayInfoExtra")
                        erec = coa_extra.find(extra) if coa_extra else None
                        if erec is None:
                            r.warn(f"display {did}: its CreatureDisplayInfoExtra {extra} is missing")
                        else:
                            coa_rows["CreatureDisplayInfoExtra"].append(coa_extra.decode(erec))
                            self.baked.append(coa_extra.decode(erec)[-1])
                            r.warn(f"display {did} is a dressed humanoid (extra {extra}): its armour pieces "
                                   "(ItemDisplayInfo) must exist in this client")
                # models of every display we add (ours and CoA's) that neither the SQL nor the client has
                ours = sqlrows.table_rows(self.committed, "creaturemodeldata_dbc")
                displays = list(sqlrows.table_rows(self.committed, "creaturedisplayinfo_dbc").values())
                models = {int(v["ModelID"]) for v in displays} | {v[1] for v in coa_rows["CreatureDisplayInfo"]}
                for mid in sorted(models):
                    if mid in ours or cmd.find(mid) is not None:
                        continue
                    rec = coa_cmd.find(mid) if coa_cmd else None
                    if rec is None:
                        r.warn(f"model {mid}: not in the CoA client's CreatureModelData.dbc")
                        continue
                    coa_rows["CreatureModelData"].append(coa_cmd.decode(rec))

        sql = ["-- Generated by tools/client/build_client_patch.py -- do not edit, do not commit.",
               "-- Looks the Devourer's creatures and shapes use that only existed in the CoA client's own DBCs,",
               "-- copied from it. The client patch carries the same rows. Removed by uninstall/world.sql.",
               "CREATE TABLE IF NOT EXISTS `devourer_client_rows` (",
               "    `tbl` VARCHAR(64) NOT NULL,",
               "    `ID` INT UNSIGNED NOT NULL,",
               "    PRIMARY KEY (`tbl`, `ID`)",
               ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci",
               "  COMMENT='mod-devourer: DBC rows copied from the CoA client by the client patch tool (read by the uninstall)';",
               ""]
        for layout, rows in coa_rows.items():
            if not rows:
                continue
            d = self.dbc(layout + ".dbc", layout)
            for values in rows:
                self.add(d, d.encode(values))
            sql += sql_rows(LAYOUTS[layout]["table"], d.layout, rows)
            r.info(f"    {layout}: {len(rows)} rows from the CoA client ({', '.join(str(v[0]) for v in rows)})")
        self.looks_sql = sql

    def coa_dbc(self, layout: str) -> Dbc | None:
        data = self.coa.read(f"DBFilesClient\\{layout}.dbc")
        if data is None:
            self.report.warn(f"the CoA sources have no DBFilesClient\\{layout}.dbc")
            return None
        d = Dbc(data, f"CoA {layout}.dbc")
        try:
            return d.use_layout(layout)
        except ValueError as e:
            raise BuildError(f"{e}; the CoA client's table has another layout")

    # model files ---------------------------------------------------------------------------------------------
    def build_models(self):
        r = self.report
        cdi, cmd = self.dbcs["CreatureDisplayInfo.dbc"], self.dbcs["CreatureModelData.dbc"]
        displays = self.added["CreatureDisplayInfo.dbc"]
        before = len(self.files)
        for did in sorted(displays):
            values = cdi.decode(cdi.find(did))
            mrec = cmd.find(values[1])
            if mrec is None:
                r.warn(f"display {did}: model {values[1]} unknown")
                continue
            model = cmd.decode(mrec)[2]
            m2 = re.sub(r"\.(mdx|mdl)$", ".m2", model, flags=re.I)
            folder = m2.rsplit("\\", 1)[0] if "\\" in m2 else ""
            if not self.client.has(m2):
                data = self.asset(m2)
                if data:
                    for path in m2_companions(m2, data):
                        self.asset(path, skip_if_in_client=True)
            for tex in values[6:9]:
                if tex:
                    self.asset(f"{folder}\\{tex}.blp" if folder else f"{tex}.blp", skip_if_in_client=True)
        for bake in self.baked:
            if bake:
                self.asset("Textures\\BakedNpcTextures\\" + bake, skip_if_in_client=True)
        r.info(f"Models and textures: {len(self.files) - before} files from the CoA client")
        if self.missing:
            r.warn("files found neither in the client nor in the CoA sources:\n    " + "\n    ".join(self.missing))

    def asset(self, path: str, skip_if_in_client: bool = False) -> bytes | None:
        known = next((k for k in self.files if k.lower() == path.lower()), None)
        if known:
            return self.files[known]
        if skip_if_in_client and self.own_client.has(path):
            return None
        data = self.coa.read(path) if self.coa else None
        if data is None:
            if not self.client.has(path) and path not in self.missing:
                self.missing.append(path)
            return None
        self.files[path] = data
        return data

    # interface -----------------------------------------------------------------------------------------------
    def build_interface(self, icon: Path | None):
        r = self.report
        r.info("Interface:")
        for path, (patch, required) in interface.PATCHES.items():
            raw = self.client.read(path)
            if raw is None:
                if required:
                    raise BuildError(f"{path} not found in the client's archives")
                continue
            bom = raw.startswith(b"\xef\xbb\xbf")
            text = raw[3:].decode("utf-8", "surrogateescape") if bom else raw.decode("utf-8", "surrogateescape")
            try:
                new, note = patch(text)
            except interface.PatchError as e:
                raise BuildError(str(e))
            if new != text:
                self.files[path] = (b"\xef\xbb\xbf" if bom else b"") + new.encode("utf-8", "surrogateescape")
            r.info(f"  {path} (from {self.client.origin(path)}): {note}")
        for path, source in interface.EXTRA_FILES.items():
            self.files[path] = source.read_bytes()
            r.info(f"  {path}: from {source.name} (ours)")
        self.check_lua()

        if icon and icon.suffix.lower() == ".blp":
            data = icon.read_bytes()
            blp.read_blp_size(data)
        else:
            Image, _, _ = blp._pil()
            img = Image.open(icon) if icon else blp.placeholder_icon(64)
            data = blp.to_blp(img, size=64)
        self.files[interface.ICON_PATH + ".blp"] = data
        r.info(f"  {interface.ICON_PATH}.blp: {'from ' + str(icon) if icon else 'placeholder icon'}")

    def check_lua(self):
        luac = next((shutil.which(n) for n in ("luac5.1", "luac51", "luac") if shutil.which(n)), None)
        if not luac:
            self.report.info("  (no luac found: Lua syntax not checked)")
            return
        for path, data in self.files.items():
            if path.lower().endswith(".lua"):
                body = data[3:] if data.startswith(b"\xef\xbb\xbf") else data
                res = subprocess.run([luac, "-p", "-"], input=body, capture_output=True)
                if res.returncode:
                    raise BuildError(f"Lua syntax error in {path}: {res.stderr.decode('latin-1').strip()}")
        self.report.info(f"  Lua syntax checked with {luac}")

    def finish_dbcs(self):
        for name, d in self.dbcs.items():
            self.files["DBFilesClient\\" + name] = d.to_bytes()


def client_strings(values: list, cols: list[str]) -> list:
    """The client reads the string of its own locale: every empty locale slot gets the enUS text (the SQL fills
    only enUS; the server does not care)."""
    values = list(values)
    for i, c in enumerate(cols):
        if c.endswith("_enUS") and values[i]:
            base = c[:-len("enUS")]
            for loc in LOCALES[1:]:
                if base + loc in cols:
                    j = cols.index(base + loc)
                    if not values[j]:
                        values[j] = values[i]
    return values


def m2_companions(m2_path: str, data: bytes) -> list[str]:
    """The files a WotLK (version 264) model loads besides itself: its .skin files, the .anim files of sequences
    stored outside the model, and its hard-coded textures."""
    if data[:4] != b"MD20":
        return []
    base = m2_path[:-3]
    out = []
    skins = struct.unpack_from("<I", data, 0x44)[0]
    out += [f"{base}{i:02d}.skin" for i in range(min(skins, 4))]
    count, ofs = struct.unpack_from("<2I", data, 0x1C)
    for i in range(count):
        anim_id, sub_id, _, _, flags = struct.unpack_from("<2HIfI", data, ofs + i * 64)
        if not flags & 0x20 and not flags & 0x40:        # not stored in the model, not an alias
            out.append(f"{base}{anim_id:04d}-{sub_id:02d}.anim")
    count, ofs = struct.unpack_from("<2I", data, 0x50)
    for i in range(count):
        kind, _, name_len, name_ofs = struct.unpack_from("<4I", data, ofs + i * 16)
        if kind == 0 and name_len > 1:
            out.append(data[name_ofs:name_ofs + name_len].split(b"\0")[0].decode("latin-1"))
    return out


# --- main --------------------------------------------------------------------------------------------------
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--client", required=True, type=Path, help="the 3.3.5a client folder (with Wow.exe and Data)")
    ap.add_argument("--coa", type=Path, action="append", default=[],
                    help="CoA files for the models, textures and looks: its Data folder, an MPQ or a folder of "
                         "loose files; repeat it, later ones win")
    ap.add_argument("--class-icon", type=Path, help="the class icon (PNG or other image, or a ready BLP); "
                                                    "default: a placeholder")
    ap.add_argument("--locale", help="client locale folder (default: detected)")
    ap.add_argument("--name", default=DEFAULT_NAME, help=f"the patch's file name (default {DEFAULT_NAME})")
    ap.add_argument("--out", type=Path, default=HERE / "out", help="output folder (default tools/client/out)")
    ap.add_argument("--sql-dir", type=Path, default=SQL_DIR, help="where the generated SQL goes")
    ap.add_argument("--no-sql", action="store_true", help="do not write the generated SQL files")
    ap.add_argument("--foreign", action="append", default=[], metavar="PATCH",
                    help="another project's patch in Data (e.g. patch-Y.MPQ): its DBC rows are kept, but its models "
                         "and textures do not count as the client's, so this patch stays complete without it")
    ap.add_argument("--overwrite-reserved", action="store_true",
                    help="ids in the Devourer's ranges already in the client (e.g. another patch built on top of an "
                         "earlier Devourer patch copied them): replace them instead of stopping")
    ap.add_argument("--install", action="store_true", help="copy the patch into the client's Data folder")
    a = ap.parse_args(argv)

    report = Report()
    try:
        return build(a, report)
    except BuildError as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        return 1


def build(a, report: Report) -> int:
    data_dir = a.client / "Data"
    if not data_dir.is_dir():
        raise BuildError(f"{data_dir} not found (--client is the folder with Wow.exe)")
    if not re.fullmatch(r"patch-[0-9A-Za-z]\.mpq", a.name, re.I):
        raise BuildError(f"--name {a.name}: the 3.3.5a client loads Data\\patch-<one letter or digit>.MPQ")
    locale = a.locale or detect_locale(data_dir)
    archives, ignored = client_archives(data_dir, locale)
    ours = []
    for p in archives + ignored:
        with mpq.Archive(p) as arc:
            if arc.has(MARKER):
                ours.append(p)
    report.info(f"Client: {a.client} ({locale}), {len(archives)} archives")
    for p in ours:
        report.info(f"  {p.name}: an earlier Devourer patch, not read")
    for p in ignored:
        if p not in ours:
            report.info(f"  {p.relative_to(data_dir)}: not loaded by the client, not read")
    target = data_dir / a.name
    if target.exists() and target not in ours:
        raise BuildError(f"{target} exists and is not a Devourer patch; choose another --name")
    readers = [p for p in archives if p not in ours]
    client = Layers([MpqSource(p) for p in readers])
    coa = coa_layers(a.coa) if a.coa else None
    if coa:
        report.info("CoA sources: " + ", ".join(s.label for s in coa.sources))

    b = Builder(client, coa, report)
    b.overwrite_reserved = a.overwrite_reserved
    foreign = {f.lower() for f in a.foreign}
    if foreign:
        b.own_client = Layers([src for src in client.sources if src.label.lower() not in foreign])
        report.info("  foreign patches (tables kept, files not counted as the client's): "
                    + ", ".join(sorted(src.label for src in client.sources if src.label.lower() in foreign)))
    b.build_dbcs()
    b.build_looks()
    b.finish_dbcs()
    b.build_models()
    b.build_interface(a.class_icon)
    b.files[MARKER] = (f"mod-devourer client patch, built {datetime.date.today()} by "
                       "tools/client/build_client_patch.py.\r\nDelete this MPQ to remove the Devourer from "
                       "the client.\r\n").encode()

    # would an archive that loads after ours hide one of our files?
    mine = rank(target, data_dir, locale)
    for p in readers:
        if rank(p, data_dir, locale) < mine:
            continue
        with mpq.Archive(p) as arc:
            hidden = [f for f in b.files if arc.has(f)]
        if hidden:
            report.warn(f"{p.name} loads after {a.name} and replaces {len(hidden)} of its files "
                        f"(e.g. {hidden[0]}); use a later --name")
    for p in readers:
        if p.parent != data_dir and re.fullmatch(rf"patch-{locale}-[4-9a-z]\.mpq", p.name, re.I):
            with mpq.Archive(p) as arc:
                both = [f for f in b.files if arc.has(f)]
            if both:
                report.warn(f"{p.relative_to(data_dir)} also has {len(both)} of the patch's files (e.g. {both[0]}). "
                            "The tool assumes Data\\patch-*.MPQ beats the locale patches; if the game shows the "
                            "old version, that assumption is wrong for this client")

    # output
    out = a.out
    staged = out / "files"
    if staged.exists():
        shutil.rmtree(staged)
    for path, data in b.files.items():
        dest = staged / Path(*path.split("\\"))
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    patch = out / a.name
    mpq.write_archive(patch, b.files)
    check = mpq.Archive(patch)
    assert all(check.read(p) == d for p, d in b.files.items()), "the written MPQ does not read back"
    check.close()
    report.info(f"\n{patch}: {len(b.files)} files, {patch.stat().st_size // 1024} KB (unpacked copies in {staged})")

    if not a.no_sql:
        a.sql_dir.mkdir(parents=True, exist_ok=True)
        (a.sql_dir / CLASS_SQL).write_text("\n".join(b.class_sql), encoding="utf-8")
        (a.sql_dir / LOOKS_SQL).write_text("\n".join(b.looks_sql), encoding="utf-8")
        report.info(f"SQL: {a.sql_dir / CLASS_SQL}\n     {a.sql_dir / LOOKS_SQL}")

    if a.install:
        for p in ours:
            if p != target:
                p.unlink()
                report.info(f"removed the earlier Devourer patch {p}")
        shutil.copyfile(patch, target)
        report.info(f"installed: {target}  (delete the client's Cache folder before starting the game)")
    else:
        report.info(f"not installed: copy it to {target} (or run again with --install)")

    (out / "report.txt").write_text("\n".join(report.lines + [""] + ["WARNING: " + w for w in report.warnings]),
                                    encoding="utf-8")
    if report.warnings:
        print(f"\n{len(report.warnings)} warning(s), see above and {out / 'report.txt'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
