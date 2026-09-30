"""The model pack (mountsADDING): new creature models for the CoA client, as mounts, Devourer shapes and
NPC looks.

    python devourer_models.py --dbc-dir <server Data\\dbc> --out <dir>

writes
    models.list                 archived name <TAB> file below mountsADDING, for mpqtool on the PC
    CreatureModelData.dbc       the client's table plus the new models   (goes into patch-T.MPQ)
    CreatureDisplayInfo.dbc     the client's table plus the new displays (goes into patch-T.MPQ)
    2026_09_27_00_devourer_models.sql   the same rows for the server, mount creatures, the mount
                                        trainers and the Devourer evolutions

MOUNTS is also read by devourer_content.py, which makes the mount spells.
"""
import argparse
import struct
from pathlib import Path

# --- ids ------------------------------------------------------------------------------------------
MODEL_BASE = 902001          # CreatureModelData   (CoA's highest: 901224)
DISPLAY_BASE = 980001        # CreatureDisplayInfo (CoA's highest: 977363)
MOUNT_CREATURE_BASE = 9102100
MOUNT_SPELL_BASE = 9100500
LOOK_CREATURE_BASE = 9102500
TRAINER_ENTRY, TRAINER_ID = 9102900, 9102900
TRAINER_GUIDS = (9910101, 9910102)

# --- files: archived folder <- folder below mountsADDING (files skipped by name) -----------------
FOLDERS = [
    ("Creature\\Dragonhawk2", "Dragonhawk2", ()),
    ("Creature\\DragonhawkMountHoly", "DragonhawkmountHoly", ()),
    ("Creature\\DragonhawkMountVoid", "DragonhawkmountVoid", ()),
    # CoA already ships the fel / sun / void dread ravens and the raven lord mount: only the rest.
    ("Creature\\DreadRavenWarbird", "dreadravenwarbird",
     ("dreadravenwarbirdfel", "dreadravenwarbirdfelmount", "dreadravenwarbirdsun", "dreadravenwarbirdsunmount",
      "dreadravenwarbirdvoidmount")),
    ("Creature\\RavenLord", "ravenlord", ("ravenlordmount",)),
    ("Creature\\Drake2", "Creature/Drake2", ()),
    ("Creature\\DrakeGrand2", "Creature/drakegrand2", ()),
    ("Creature\\DrakeMount2", "Creature/drakemount2", ()),
    ("Creature\\KakapoMount", "Creature/Creature/KakapoMount", ()),
    ("Creature\\AlastorSE", "VoidCase2/AlastorSE", ()),
    ("Creature\\BelPeol", "VoidCase2/Belpeol", ()),
    ("Creature\\KaliMagnusHM", "VoidCase2/KaliMagnusHM", ()),
    ("Creature\\Krauzeria", "VoidCase2/Krauzeria", ()),
    ("Creature\\Lythalia", "VoidCase2/Lythalia", ()),
    ("Creature\\Valla_Hunteress", "VoidCase2/Valla_hunteress", ()),
]
# Models taken apart from the Sethrak-for-Draenei pack (gongel, v3 patch-D.mpq): it puts them over the draenei
# player models. Here they get their own folders and names, so draenei and CoA's own Sethrak stay as they
# are. (new folder, new base name, the pack's model and base name, textures: pack file -> name here)
PACK = "Sethrak_for_Draenei_female_&_male+voice_attack,deatk_etc._v3/patch-D.mpq"
REPACKED = [
    ("Creature\\DevourerSethrak", "DevourerSethrak", "character\\draenei\\male", "DraeneiMale",
     {"creature\\sethrak_melee\\sethrak_dust.blp": "sethrak_dust.blp",
      "creature\\sethrak_melee\\sethrak_melee_brown.blp": "sethrak_melee_brown.blp",
      "creature\\sethrak_melee\\armorreflect4.blp": "armorreflect4.blp"}),
    ("Creature\\DevourerSethraliss", "DevourerSethraliss", "creature\\snakeloa", "snakeloa",
     {"creature\\snakeloa\\" + t: t for t in ("snakeloa_1_body_blue.blp", "snakeloa_2_armor_blue.blp",
      "snakeloa_fx1_blue.blp", "snakeloa_fx2_blue.blp", "snakeloa_fx3_blue.blp", "armorreflect4.blp")}),
]

# The keeps of the skipped model names: their .m2, .skin and .anim files; textures stay.
MODEL_EXTENSIONS = (".m2", ".skin", ".anim")

# --- models: key -> (path, template CreatureModelData id) ------------------------------------------
MODELS = {
    "dh2": ("Creature\\Dragonhawk2\\Dragonhawk2.mdx", 2363),
    "dh2mount": ("Creature\\Dragonhawk2\\Dragonhawk2mount.mdx", 3045),
    "dh2elite": ("Creature\\Dragonhawk2\\Dragonhawk2mountelite.mdx", 3045),
    "dhholy": ("Creature\\DragonhawkMountHoly\\DragonhawkMountHoly.mdx", 3045),
    "dhvoid": ("Creature\\DragonhawkMountVoid\\DragonhawkMountVoid.mdx", 3045),
    "ravenholy": ("Creature\\DreadRavenWarbird\\dreadravenwarbirdholymount.mdx", 100392),
    "ravenwind": ("Creature\\DreadRavenWarbird\\dreadravenwarbirdwind.mdx", 7197),
    "ravenlord": ("Creature\\RavenLord\\ravenlord.mdx", 7197),
    "ravenlordp": ("Creature\\RavenLord\\ravenlord_purple.mdx", 7197),
    "drake2": ("Creature\\Drake2\\drake2.mdx", 153),
    "drake2az": ("Creature\\Drake2\\drake2Azure.mdx", 153),
    "ndrake2": ("Creature\\Drake2\\northrenddrake2.mdx", 3019),
    "ndrake2az": ("Creature\\Drake2\\northrenddrake2azure.mdx", 3019),
    "dm2": ("Creature\\DrakeMount2\\drakemount2.mdx", 2858),
    "dm2armored": ("Creature\\DrakeMount2\\drakemount2armored.mdx", 2858),
    "dm2azure": ("Creature\\DrakeMount2\\drakemount2azure.mdx", 2858),
    "dm2elite": ("Creature\\DrakeMount2\\drakemount2elite.mdx", 2858),
    "grand": ("Creature\\DrakeGrand2\\drakemount2grand.mdx", 2858),
    "grandalex": ("Creature\\DrakeGrand2\\drakemount2GrandAlex.mdx", 2858),
    "grandhalion": ("Creature\\DrakeGrand2\\drakemount2grandHalion.mdx", 2858),
    "grandmalygos": ("Creature\\DrakeGrand2\\drakemount2grandMalygos.mdx", 2858),
    "grandnefarian": ("Creature\\DrakeGrand2\\drakemount2grandNefarian.mdx", 2858),
    "grandnozdormu": ("Creature\\DrakeGrand2\\drakemount2grandnozdormu.mdx", 2858),
    "grandonyxia": ("Creature\\DrakeGrand2\\drakemount2grandonyxia.mdx", 2858),
    "grandterac": ("Creature\\DrakeGrand2\\drakemount2GrandTerac.mdx", 2858),
    "grandysera": ("Creature\\DrakeGrand2\\drakemount2GrandYsera.mdx", 2858),
    "kakapo": ("Creature\\KakapoMount\\KakapoMount.mdx", 5829),
    "alastor": ("Creature\\AlastorSE\\alastorstrixefuartus.mdx", 3253),
    "belpeol": ("Creature\\BelPeol\\bel_peol.mdx", 2548),
    "adonai": ("Creature\\KaliMagnusHM\\Adonai.mdx", 3253),
    "kalimagnus": ("Creature\\KaliMagnusHM\\kalimagnushm.mdx", 3253),
    "kalimagnusp": ("Creature\\KaliMagnusHM\\KaliMagnusP.mdx", 3253),
    "krauzeria": ("Creature\\Krauzeria\\krauzeria.mdx", 2548),
    "lythalia": ("Creature\\Lythalia\\lythalia.mdx", 3253),
    "valla": ("Creature\\Valla_Hunteress\\valla_hunteress.mdx", 3253),
    # From the Sethrak-for-Draenei pack (gongel), moved out of the draenei folders: see REPACKED.
    "sethrak": ("Creature\\DevourerSethrak\\DevourerSethrak.mdx", 402214),
    "sethraliss": ("Creature\\DevourerSethraliss\\DevourerSethraliss.mdx", 402214),
}

RUNES = "TestAzureDrake_Runes"
ARMOR = ["companiondrake_armor_color_%d" % n for n in range(4256723, 4256731)]

# --- mounts: (name, model, scale, textures, flying) -------------------------------------------------
MOUNTS = [
    ("Crimson Dragonhawk", "dh2mount", 1.2, ("Dragonhawk2Red", "Dragonhawk2MountSaddleBronze"), True),
    ("Silver Dragonhawk", "dh2mount", 1.2, ("Dragonhawk2Silver", "Dragonhawk2MountSaddleSilver"), True),
    ("Silver Covenant Dragonhawk", "dh2mount", 1.2, ("Dragonhawk2SilverCovenant", "Dragonhawk2MountSaddleSilverCovenant"), True),
    ("Sunreaver Dragonhawk", "dh2mount", 1.2, ("DragonHawkSunReaverMount", "Dragonhawk2MountSaddleSunreaver"), True),
    ("Blessed Dragonhawk", "dh2mount", 1.2, ("Dragonhawk2Holy", "Dragonhawk2MountSaddleHoly"), True),
    ("Gilded Dragonhawk", "dh2elite", 1.2, ("Dragonhawk2Red", "Dragonhawk2mountSaddle_gold"), True),
    ("Dawnlight Dragonhawk", "dhholy", 1.2, (), True),
    ("Voidwing Dragonhawk", "dhvoid", 1.2, (), True),
    ("Radiant Dread Raven", "ravenholy", 0.35, (), True),
    ("Black Drake", "dm2", 1.0, ("TestBlackDrake_Skin", ARMOR[0], RUNES), True),
    ("Bronze Drake", "dm2", 1.0, ("TestBronzeDrake_Skin", ARMOR[1], RUNES), True),
    ("Green Drake", "dm2", 1.0, ("TestGreenDrake_Skin", ARMOR[2], RUNES), True),
    ("Red Drake", "dm2", 1.0, ("TestRedDrake_Skin", ARMOR[3], RUNES), True),
    ("Twilight Drake", "dm2", 1.0, ("TestTwilightDrake_Skin", ARMOR[4], RUNES), True),
    ("White Drake", "dm2", 1.0, ("TestWhiteDrake_Skin", ARMOR[5], RUNES), True),
    ("Mottled Drake", "dm2", 1.0, ("TestMottledDrake_Skin", ARMOR[6], RUNES), True),
    ("Chromatic Drake", "dm2", 1.0, ("TestChromaticDrake_Skin", ARMOR[7], RUNES), True),
    ("Armored Blue Drake", "dm2armored", 1.0, ("TestBlueDrake_Skin", "companiondrake_armor_Blue", RUNES), True),
    ("Armored Twilight Drake", "dm2armored", 1.0, ("TestPurpleTwilightDrake_Skin", ARMOR[4], RUNES), True),
    ("Azure Drake", "dm2azure", 1.0, ("TestAzureDrake_Skin", "companiondrake_armor_Azure", RUNES), True),
    ("Elite Red Drake", "dm2elite", 1.0, ("TestRedTwilightDrake_Skin", ARMOR[3], RUNES), True),
    ("Grand Alexstrasza Drake", "grandalex", 1.1, ("AlexDrake_01", "AlexDrake_02", "armor_GoldRed"), True),
    ("Grand Halion Drake", "grandhalion", 1.1, ("HalionDrake_01", "HalionDrake_02", "armor_BlackGold"), True),
    ("Grand Malygos Drake", "grandmalygos", 1.1, ("MalygosDrake_01", "MalygosDrake_02", "armor_SilverBlue"), True),
    ("Grand Nefarian Drake", "grandnefarian", 1.1, ("NefarianDrake_01", "NefarianDrake_02", "armor_BlackGold"), True),
    ("Grand Nozdormu Drake", "grandnozdormu", 1.1, ("NozdormuDrake_01", "NozdormuDrake_02", "armor_GoldBrown"), True),
    ("Grand Onyxia Drake", "grandonyxia", 1.1, ("OnyxiaDrake_01", "OnyxiaDrake_02", "armor_BronzeBlack"), True),
    ("Grand Terrace Drake", "grandterac", 1.1, ("TeracDrake_01", "TeracDrake_02", "armor_BronzeGreen"), True),
    ("Grand Ysera Drake", "grandysera", 1.1, ("YseraDrake_01", "YseraDrake_02", "armor_BronzePurple"), True),
    ("Grand Night Drake", "grand", 1.1, ("NightDrake_01", "NightDrake_02", "armor_SilverPurple"), True),
    ("Grand Murozond Drake", "grand", 1.1, ("MurozondDrake_01", "MurozondDrake_02", "armor_BronzeBlack"), True),
    ("Grand Ultraxion Drake", "grand", 1.1, ("UltraxionDrake_01", "UltraxionDrake_02", "armor_GoldWhite"), True),
    ("Kakapo", "kakapo", 0.4, ("kakapo_green", "smoothreflect_round"), False),
]

# --- looks: creatures and characters (display, a creature to .npc add, .morph) ----------------------
# (key, name, model, scale, textures, creature type, evolution use)
LOOKS = [
    ("dh_sun", "Sunstrider Dragonhawk", "dh2", 1.2, ("Dragonhawkskin",), 1),
    ("dh_jade", "Jade Dragonhawk", "dh2", 1.2, ("DragonhawkSkin02",), 1),
    ("dh_dusk", "Dusk Dragonhawk", "dh2", 1.2, ("DragonhawkSkin04",), 1),
    ("dh_ember", "Ember Dragonhawk", "dh2", 1.2, ("DragonhawkSkin06",), 1),
    ("drake_red", "Crimson Drake", "drake2", 1.0, ("TestRedDrake_Skin", RUNES, "companiondrake_armor_Azure"), 2),
    ("drake_azure", "Azure Drake", "drake2az", 1.0, ("TestAzureDrake_Skin", RUNES, "companiondrake_armor_Azure"), 2),
    ("ndrake_black", "Northrend Black Drake", "ndrake2", 1.0, ("TestBlackDrake_Skin",), 2),
    ("ndrake_azure", "Northrend Azure Drake", "ndrake2az", 1.0, ("TestAzureDrake_Skin", RUNES, "companiondrake_armor_Azure"), 2),
    ("raven_lord", "Raven Lord", "ravenlord", 0.35, (), 1),
    ("raven_shadow", "Shadow Raven Lord", "ravenlordp", 0.35, (), 1),
    ("raven_storm", "Storm Dread Raven", "ravenwind", 0.35,
     ("dreadravenwarbirdwind_1", "dreadravenwarbirdwind_2", "dreadravenwarbirdwindarmor"), 1),
    ("alastor", "Alastor", "alastor", 1.0, (), 7),
    ("belpeol", "Bel'peol", "belpeol", 1.0, (), 3),
    ("adonai", "Adonai", "adonai", 1.0, (), 7),
    ("kalimagnus", "Kali Magnus", "kalimagnus", 1.0, (), 7),
    ("kalimagnusp", "Kali Magnus (small)", "kalimagnusp", 1.0, (), 7),
    ("krauzeria", "Krauzeria", "krauzeria", 1.0, (), 3),
    ("lythalia", "Lythalia", "lythalia", 1.0, (), 7),
    ("valla", "Valla the Huntress", "valla", 1.0, (), 7),
    ("sethrak_dust", "Sethrak Wanderer", "sethrak", 1.0, ("sethrak_dust", "sethrak_melee_brown"), 7),
    ("sethraliss", "Sethraliss", "sethraliss", 1.2, (), 7),
]

# --- Devourer evolutions: (node, name, branch, look key, parent node, min level, school, feats, instinct)
DRAGONHAWK_FEATS, DRAGONHAWK_INSTINCT = (9100232, 9100315), 9100233
CARRION_FEATS, CARRION_INSTINCT = (9100228, 9100313), 9100229
SETHRAK_FEATS, SETHRAK_INSTINCT = (9100290, 9100291), 9100292      # Constricting Coils, Shed Skin / Scaled Ward
POISON_SPIT = 9100326
EVOLUTIONS = [
    # any dragonhawk (the root matches the family of its creature: Feral Dragonhawk Hatchling)
    (30, "Dragonhawk", "Sky", None, 0, 1, 2, DRAGONHAWK_FEATS, DRAGONHAWK_INSTINCT),
    (31, "Sunstrider Dragonhawk", "Sky", "dh_sun", 30, 30, 2, DRAGONHAWK_FEATS, DRAGONHAWK_INSTINCT),
    (32, "Crimson Drake", "Sky", "drake_red", 31, 55, 2, DRAGONHAWK_FEATS, DRAGONHAWK_INSTINCT),
    (33, "Northrend Black Drake", "Sky", "ndrake_black", 32, 70, 2, DRAGONHAWK_FEATS, DRAGONHAWK_INSTINCT),
    (34, "Azure Drake", "Sky", "drake_azure", 31, 55, 6, DRAGONHAWK_FEATS, DRAGONHAWK_INSTINCT),
    (35, "Northrend Azure Drake", "Sky", "ndrake_azure", 34, 70, 6, DRAGONHAWK_FEATS, DRAGONHAWK_INSTINCT),
    # any carrion bird (root: Wiry Swoop)
    (40, "Carrion Bird", "Raven", None, 0, 1, 5, CARRION_FEATS, CARRION_INSTINCT),
    (41, "Raven Lord", "Raven", "raven_lord", 40, 50, 5, CARRION_FEATS, CARRION_INSTINCT),
    (42, "Shadow Raven Lord", "Raven", "raven_shadow", 41, 65, 5, CARRION_FEATS, CARRION_INSTINCT),
    (43, "Storm Dread Raven", "Raven", "raven_storm", 41, 70, 3, CARRION_FEATS, CARRION_INSTINCT),
    # the Sethrak Sandstalker of the Tanaris camp (humanoid) -> the Wanderer -> Sethraliss, loa of storms
    (50, "Sethrak", "Serpent", None, 0, 1, 0, SETHRAK_FEATS, SETHRAK_INSTINCT),
    (51, "Sethrak Wanderer", "Serpent", "sethrak_dust", 50, 50, 0, SETHRAK_FEATS, SETHRAK_INSTINCT),
    (52, "Sethraliss", "Serpent", "sethraliss", 51, 70, 3, (POISON_SPIT, SETHRAK_FEATS[1]), SETHRAK_INSTINCT),
]
ROOTS = {30: (15649, 17547), 40: (2969, 1228), 50: (9101001, 80305)}   # node -> (creature entry, its display)
NODE_TYPE = {50: 7, 51: 7, 52: 7}                    # creature type when not a beast (7 humanoid)
COSTS = {1: (0, 0), 30: (10, 5), 50: (15, 8), 55: (20, 10), 65: (25, 15), 70: (30, 20)}

MOUNT_TRAINER_SPAWNS = [   # map, x, y, z, o: Stormwind Trade District, Orgrimmar Valley of Strength
    (0, -8829.5, 626.3, 94.1, 3.9),
    (1, 1624.2, -4378.2, 12.0, 0.6),
]


# --- DBC helpers ----------------------------------------------------------------------------------
class Dbc:
    def __init__(self, path):
        data = Path(path).read_bytes()
        magic, self.count, self.fields, self.rsize, ssize = struct.unpack_from("<4s4I", data)
        assert magic == b"WDBC"
        body = data[20:20 + self.count * self.rsize]
        self.rows = [bytearray(body[i * self.rsize:(i + 1) * self.rsize]) for i in range(self.count)]
        self.strings = bytearray(data[20 + self.count * self.rsize:])
        self.index = {struct.unpack_from("<I", r, 0)[0]: r for r in self.rows}

    def string(self, offset):
        return self.strings[offset:self.strings.index(b"\0", offset)].decode("utf-8", "replace")

    def add_string(self, text):
        if not text:
            return 0
        offset = len(self.strings)
        self.strings += text.encode("utf-8") + b"\0"
        return offset

    def u32(self, row, field):
        return struct.unpack_from("<I", row, field * 4)[0]

    def set_u32(self, row, field, value):
        struct.pack_into("<I", row, field * 4, value & 0xFFFFFFFF)

    def f32(self, row, field):
        return struct.unpack_from("<f", row, field * 4)[0]

    def set_f32(self, row, field, value):
        struct.pack_into("<f", row, field * 4, value)

    def write(self, path):
        body = b"".join(bytes(r) for r in self.rows)
        header = struct.pack("<4s4I", b"WDBC", len(self.rows), self.fields, self.rsize, len(self.strings))
        Path(path).write_bytes(header + body + bytes(self.strings))


def sql_str(text):
    return "NULL" if text is None else "'" + text.replace("\\", "\\\\").replace("'", "''") + "'"


def build(dbc_dir, out):
    out.mkdir(parents=True, exist_ok=True)
    cmd = Dbc(dbc_dir / "CreatureModelData.dbc")
    cdi = Dbc(dbc_dir / "CreatureDisplayInfo.dbc")
    assert max(cmd.index) < MODEL_BASE and max(cdi.index) < DISPLAY_BASE

    template_display = {}
    for row in cdi.rows:
        template_display.setdefault(cdi.u32(row, 1), row)

    sql = ["-- mod-devourer: the model pack (mountsADDING) - generated by tools/devourer_models.py. Safe to run again.",
           f"DELETE FROM `creaturemodeldata_dbc` WHERE `ID` BETWEEN {MODEL_BASE} AND {MODEL_BASE + 999};",
           f"DELETE FROM `creaturedisplayinfo_dbc` WHERE `ID` BETWEEN {DISPLAY_BASE} AND {DISPLAY_BASE + 999};",
           f"DELETE FROM `creature_model_info` WHERE `DisplayID` BETWEEN {DISPLAY_BASE} AND {DISPLAY_BASE + 999};"]

    model_ids = {}
    cmd_cols = ["ID", "Flags", "ModelName", "SizeClass", "ModelScale", "BloodID", "FootprintTextureID",
                "FootprintTextureLength", "FootprintTextureWidth", "FootprintParticleScale", "FoleyMaterialID",
                "FootstepShakeSize", "DeathThudShakeSize", "SoundID", "CollisionWidth", "CollisionHeight",
                "MountHeight", "GeoBoxMinX", "GeoBoxMinY", "GeoBoxMinZ", "GeoBoxMaxX", "GeoBoxMaxY", "GeoBoxMaxZ",
                "WorldEffectScale", "AttachedEffectScale", "MissileCollisionRadius", "MissileCollisionPush",
                "MissileCollisionRaise"]
    float_fields = {4, 7, 8, 9, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27}
    for n, (key, (path, template)) in enumerate(MODELS.items()):
        mid = MODEL_BASE + n
        model_ids[key] = mid
        row = bytearray(cmd.index[template])
        cmd.set_u32(row, 0, mid)
        cmd.set_u32(row, 2, cmd.add_string(path))
        cmd.rows.append(row)
        values = []
        for i, col in enumerate(cmd_cols):
            if i == 2:
                values.append(sql_str(path))
            elif i in float_fields:
                values.append(repr(round(cmd.f32(row, i), 6)))
            else:
                v = cmd.u32(row, i)
                values.append(str(v - (1 << 32) if v >= 1 << 31 else v))
        sql.append(f"INSERT INTO `creaturemodeldata_dbc` ({', '.join('`%s`' % c for c in cmd_cols)}) VALUES ({', '.join(values)});")

    displays = {}
    def add_display(key, model_key, scale, textures):
        did = DISPLAY_BASE + len(displays)
        displays[key] = did
        template = template_display[MODELS[model_key][1]]
        row = bytearray(template)
        cdi.set_u32(row, 0, did)
        cdi.set_u32(row, 1, model_ids[model_key])
        cdi.set_u32(row, 3, 0)                       # no ExtendedDisplayInfo
        cdi.set_f32(row, 4, scale)
        cdi.set_u32(row, 5, 255)
        tex = list(textures) + [""] * (3 - len(textures))
        for i in range(3):
            cdi.set_u32(row, 6 + i, cdi.add_string(tex[i]))
        cdi.set_u32(row, 9, 0)                       # portrait
        cdi.set_u32(row, 14, 0)                      # geoset data
        cdi.set_u32(row, 15, 0)                      # effect package
        cdi.rows.append(row)
        u = lambda f: cdi.u32(row, f)
        s = lambda f: (u(f) - (1 << 32) if u(f) >= 1 << 31 else u(f))
        sql.append("INSERT INTO `creaturedisplayinfo_dbc` (`ID`, `ModelID`, `SoundID`, `ExtendedDisplayInfoID`, "
                   "`CreatureModelScale`, `CreatureModelAlpha`, `TextureVariation_1`, `TextureVariation_2`, "
                   "`TextureVariation_3`, `PortraitTextureName`, `BloodLevel`, `BloodID`, `NPCSoundID`, "
                   "`ParticleColorID`, `CreatureGeosetData`, `ObjectEffectPackageID`) VALUES "
                   f"({did}, {model_ids[model_key]}, {s(2)}, 0, {scale}, 255, "
                   f"{sql_str(tex[0] or None)}, {sql_str(tex[1] or None)}, {sql_str(tex[2] or None)}, NULL, "
                   f"{s(10)}, {s(11)}, {s(12)}, {s(13)}, 0, 0);")
        radius = max(0.3, 0.5 * scale) if MODELS[model_key][1] not in (3253, 2548) else 0.4
        sql.append(f"INSERT INTO `creature_model_info` (`DisplayID`, `BoundingRadius`, `CombatReach`, `Gender`) "
                   f"VALUES ({did}, {radius:.2f}, 1.5, 2);")
        return did

    # Mounts: display, the creature the mount aura shows, and the spell id (devourer_content.py).
    sql.append(f"DELETE FROM `creature_template_model` WHERE `CreatureID` BETWEEN {MOUNT_CREATURE_BASE} AND {LOOK_CREATURE_BASE + 399};")
    sql.append(f"DELETE FROM `creature_template` WHERE `entry` BETWEEN {MOUNT_CREATURE_BASE} AND {LOOK_CREATURE_BASE + 399};")
    for i, (name, model, scale, textures, flying) in enumerate(MOUNTS):
        did = add_display(f"mount{i}", model, scale, textures)
        entry = MOUNT_CREATURE_BASE + i
        sql.append(f"INSERT INTO `creature_template` (`entry`, `name`, `subname`, `minlevel`, `maxlevel`, `faction`, "
                   f"`npcflag`, `unit_class`, `unit_flags`, `type`, `flags_extra`) VALUES ({entry}, {sql_str(name)}, "
                   f"'Mount', 1, 1, 35, 0, 1, 33554432, 1, 128);")
        sql.append(f"INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, "
                   f"`Probability`) VALUES ({entry}, 0, {did}, 1, 1);")

    # Looks: a creature for each, to .npc add; the display for .morph.
    for i, (key, name, model, scale, textures, ctype) in enumerate(LOOKS):
        did = add_display(key, model, scale, textures)
        entry = LOOK_CREATURE_BASE + i
        sql.append(f"INSERT INTO `creature_template` (`entry`, `name`, `minlevel`, `maxlevel`, `faction`, `npcflag`, "
                   f"`unit_class`, `type`) VALUES ({entry}, {sql_str(name)}, 60, 60, 35, 0, 1, {ctype});")
        sql.append(f"INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, "
                   f"`Probability`) VALUES ({entry}, 0, {did}, 1, 1);")

    # The mount trainers: Valla in Stormwind and Orgrimmar teaches every mount above.
    sql += [
        f"DELETE FROM `creature` WHERE `guid` IN ({TRAINER_GUIDS[0]}, {TRAINER_GUIDS[1]});",
        f"DELETE FROM `creature_template_model` WHERE `CreatureID` = {TRAINER_ENTRY};",
        f"DELETE FROM `creature_template` WHERE `entry` = {TRAINER_ENTRY};",
        f"DELETE FROM `creature_default_trainer` WHERE `CreatureId` = {TRAINER_ENTRY};",
        f"DELETE FROM `trainer_spell` WHERE `TrainerId` = {TRAINER_ID};",
        f"DELETE FROM `trainer` WHERE `Id` = {TRAINER_ID};",
        f"INSERT INTO `creature_template` (`entry`, `name`, `subname`, `minlevel`, `maxlevel`, `faction`, `npcflag`, "
        f"`unit_class`, `type`, `flags_extra`) VALUES ({TRAINER_ENTRY}, 'Valla', 'Keeper of Rare Mounts', 80, 80, 35, "
        f"17, 1, 7, 2);",
        f"INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`) "
        f"VALUES ({TRAINER_ENTRY}, 0, {displays['valla']}, 1, 1);",
        f"INSERT INTO `trainer` (`Id`, `Type`, `Requirement`, `Greeting`) VALUES ({TRAINER_ID}, 2, 0, "
        f"'Dragonhawks, drakes and stranger things. Pick one, and mind the teeth.');",
        f"INSERT INTO `creature_default_trainer` (`CreatureId`, `TrainerId`) VALUES ({TRAINER_ENTRY}, {TRAINER_ID});",
    ]
    for i in range(len(MOUNTS)):
        sql.append(f"INSERT INTO `trainer_spell` (`TrainerId`, `SpellId`, `MoneyCost`, `ReqLevel`) VALUES "
                   f"({TRAINER_ID}, {MOUNT_SPELL_BASE + i}, 0, 20);")
    for guid, (map_id, x, y, z, o) in zip(TRAINER_GUIDS, MOUNT_TRAINER_SPAWNS):
        sql.append(f"INSERT INTO `creature` (`guid`, `id`, `map`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, "
                   f"`position_z`, `orientation`, `spawntimesecs`) VALUES ({guid}, {TRAINER_ENTRY}, {map_id}, 1, 1, "
                   f"{x}, {y}, {z}, {o}, 300);")

    # Devourer evolutions: the Sky tree (dragonhawks into drakes) and the Raven tree.
    sql.append("DELETE FROM `devourer_evolution` WHERE `node_id` BETWEEN 30 AND 59;")
    for node, name, branch, look, parent, level, school, feats, instinct in EVOLUTIONS:
        if look is None:
            entry, display = ROOTS[node]
        else:
            entry, display = 0, displays[look]
        cost_type, cost_school = COSTS[level] if level in COSTS else (10, 5)
        sql.append("INSERT INTO `devourer_evolution` (`node_id`, `name`, `branch`, `display_id`, `creature_entry`, "
                   "`parent_node`, `creature_type`, `min_level`, `cost_type_essence`, `cost_school`, "
                   "`cost_school_essence`, `feat1`, `feat2`, `instinct`) VALUES "
                   f"({node}, {sql_str(name)}, {sql_str(branch)}, {display}, {entry}, {parent}, {NODE_TYPE.get(node, 1)}, {level}, "
                   f"{cost_type}, {school}, {cost_school}, {feats[0]}, {feats[1]}, {instinct});")
    # Evolved bodies keep the shape of their family (Dragonhawk: caster, Carrion Bird: predator).
    sky = " ".join(str(displays[k]) for k in ("dh_sun", "drake_red", "ndrake_black", "drake_azure", "ndrake_azure"))
    raven = " ".join(str(displays[k]) for k in ("raven_lord", "raven_shadow", "raven_storm"))
    sql.append(f"UPDATE `devourer_shape` SET `displays` = '{sky}' WHERE `shape_id` = 20;")
    sql.append(f"UPDATE `devourer_shape` SET `displays` = '{raven}' WHERE `shape_id` = 18;")
    sethrak = " ".join(["80018 280018 80305 200004"] + [str(displays[k]) for k in ("sethrak_dust", "sethraliss")])
    sql.append(f"UPDATE `devourer_shape` SET `displays` = '{sethrak}' WHERE `shape_id` = 3;")

    (out / "2026_09_27_00_devourer_models.sql").write_text("\n".join(sql) + "\n", encoding="utf-8", newline="\n")
    cmd.write(out / "CreatureModelData.dbc")
    cdi.write(out / "CreatureDisplayInfo.dbc")
    return displays, model_ids


def repoint_textures(m2, folder):
    """The model's texture names point into the pack's folders: aim them at our folder (same file names)."""
    data = bytearray(m2)
    count, table = struct.unpack_from("<II", data, 0x50)
    for i in range(count):
        kind, flags, length, offset = struct.unpack_from("<IIII", data, table + 16 * i)
        if not length:
            continue
        name = bytes(data[offset:offset + length]).split(b"\0")[0].decode("latin-1")
        leaf = name.replace("/", "\\").split("\\")[-1]
        new = (folder + "\\" + leaf).encode("latin-1") + b"\0"
        while len(data) % 16:
            data.append(0)
        struct.pack_into("<II", data, table + 16 * i + 8, len(new), len(data))
        data += new
    return bytes(data)


def repack(extracted, out):
    """extracted: the pack's files (as the archive names them, / for \\). Writes out/models/... and returns
    models.list lines "archived<TAB>pkg:relative"."""
    lines = []
    for folder, base, src_dir, src_base, textures in REPACKED:
        src = extracted / src_dir.replace("\\", "/")
        dest = out / "models" / folder.replace("\\", "/")
        dest.mkdir(parents=True, exist_ok=True)
        def put(name, data):
            (dest / name).write_bytes(data)
            lines.append(f"{folder}\\{name}\tpkg:models\\{folder}\\{name}")
        for f in sorted(src.iterdir()):
            low = f.name.lower()
            if not low.startswith(src_base.lower()) or not low.endswith(MODEL_EXTENSIONS) or "_lod" in low:
                continue
            name = base + f.name[len(src_base):]
            data = f.read_bytes()
            put(name, repoint_textures(data, folder) if low.endswith(".m2") else data)
        for pack_name, name in textures.items():
            put(name, (extracted / pack_name.replace("\\", "/")).read_bytes())
    return lines


def write_list(listing, out, extra=()):
    """listing: files below mountsADDING (forward slashes). Writes models.list."""
    lines = []
    for archived, source, skip in FOLDERS:
        prefix = source.rstrip("/") + "/"
        for name in sorted(listing):
            if not name.startswith(prefix) or "/" in name[len(prefix):]:
                continue
            leaf = name[len(prefix):]
            low = leaf.lower()
            if low.endswith(".png") or low.endswith(".txt"):
                continue
            # a skipped model: <name>.m2, <name>NN.skin, <name>NNNN-NN.anim
            if low.endswith(MODEL_EXTENSIONS) and any(
                    low.startswith(s) and (low[len(s):len(s) + 1].isdigit() or low[len(s):len(s) + 1] == ".")
                    for s in skip):
                continue
            lines.append(f"{archived}\\{leaf}\t{name.replace('/', chr(92))}")
            # The holy dread raven's animation files carry a shorter name than its model.
            if low.startswith("dreadravenwarbirdholy0") and low.endswith(".anim"):
                alias = "dreadravenwarbirdholymount" + leaf[len("dreadravenwarbirdholy"):]
                lines.append(f"{archived}\\{alias}\t{name.replace('/', chr(92))}")
    lines += list(extra)
    (out / "models.list").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return lines


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dbc-dir", required=True, type=Path)
    ap.add_argument("--listing", type=Path, help="text file: one path below mountsADDING per line")
    ap.add_argument("--pack", type=Path, help="the Sethrak pack's patch-D.mpq extracted (see REPACKED)")
    ap.add_argument("--out", required=True, type=Path)
    a = ap.parse_args()
    displays, models = build(a.dbc_dir, a.out)
    extra = repack(a.pack, a.out) if a.pack else []
    if a.listing:
        n = write_list(a.listing.read_text().split("\n"), a.out, extra)
        print(f"{len(n)} files in models.list")
    print(f"{len(models)} models, {len(displays)} displays")
