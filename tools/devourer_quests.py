#!/usr/bin/env python3
"""Task 021: the Devourer's quests in the world (Hagatha's lanterns).

Writes, from the content in tools/devourer_quests_content.py:
  data/sql/db-world/2026_10_05_10_devourer_quests.sql   quests, lanterns, the witches' objects, credits, conditions
  src/DevourerQuestsIds.h                              the rules DevourerQuests.cpp gives credit by
  docs/quests.md                                       the list for the owner (levels, story, rewards)

Ids (checked free on 2026-10-05): 9105000-9105999 for quests, creature_template (credits), gameobject_template
(lanterns, objects) and conditions' sources; spawn guids 9920000-9920999 (gameobjects). Run it again after any change:
    python tools/devourer_quests.py
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQL_OUT = os.path.join(ROOT, "data", "sql", "db-world", "2026_10_05_10_devourer_quests.sql")
HDR_OUT = os.path.join(ROOT, "src", "DevourerQuestsIds.h")
DOC_OUT = os.path.join(ROOT, "docs", "quests.md")

Q_FIRST, Q_LAST = 9105000, 9105399            # quests
CREDIT_FIRST, CREDIT_LAST = 9105400, 9105999  # credit creatures (never spawned)
LANTERN_FIRST, LANTERN_LAST = 9105000, 9105099  # gameobject_template: one lantern per region
THING_FIRST, THING_LAST = 9105100, 9105199    # gameobject_template: what the witches leave to be touched
GUID_FIRST, GUID_LAST = 9920000, 9920999      # gameobject spawns

EXTERNAL_QUESTS = {9101305: "Wren's Apprentice", 9101360: "Wren's Derby", 9101362: "The Last Lap"}
CLASS_DEVOURER = 512                          # AllowableClasses: class 10
HAGATHA, WREN = 9101300, 9101301              # the sisters in the In-Between (tools/witch_sisters.py)
LANTERN_DISPLAY = 6038                        # the look of Hagatha's Lantern in the In-Between
INVISIBLE_MODEL = 11686
TRIGGER_TEMPLATE = 15384                      # OLDWorld Trigger, the credits are copies of it

# Races (AllowableRaces bits)
HUMAN, ORC, DWARF, NIGHTELF, UNDEAD, TAUREN, GNOME, TROLL, BLOODELF, DRAENEI = (
    1, 2, 4, 8, 16, 32, 64, 128, 512, 1024)

# Filters and events, as in DevourerQuests.cpp
EVENT_MEAL, EVENT_KILL = 1, 2
FILTER_ENTRY, FILTER_FAMILY, FILTER_TYPE, FILTER_ELITE, FILTER_ANY = 1, 2, 3, 4, 5

# The Devourer's shapes (devourer_shape), for "as a ..." objectives and shape-gated quests.
SHAPES = {
    1: ("Sethrak", 9100100), 2: ("Berserker", 9100200), 3: ("Vashnik", 9100300), 4: ("Baby Berserker", 9100400),
    5: ("Wolf", 9100910), 6: ("Trogg", 9100920), 7: ("Saber", 9100930), 8: ("Moth", 9100940), 9: ("Boar", 9100950),
    10: ("Plainstrider", 9100960), 11: ("Bat", 9100970), 12: ("Mana Wyrm", 9100980), 13: ("Warp Stalker", 9101000),
    14: ("Biletoad", 9101010), 15: ("Giant Marsh Frog", 9101020), 16: ("Greater Plainstrider", 9102000),
    17: ("Bloodsnout Worg", 9102010), 18: ("Raging Agam'ar", 9102020), 19: ("Shadowclaw", 9102030),
    20: ("Rockjaw Backbreaker", 9102040), 21: ("Vampiric Duskbat", 9102050), 22: ("Arcane Wraith", 9102060),
    23: ("Royal Blue Flutterer", 9102070), 24: ("Void Terror", 9102080), 25: ("Viper", 9102090),
    26: ("Baby Wind Serpent", 9102100), 27: ("Baby Eagle", 9102110), 28: ("Baby Komodo", 9102120),
    29: ("Komodo Dragon", 9102130), 30: ("Water Salamander", 9102140), 31: ("Snapjaw", 9102150),
    32: ("Spikeshell", 9102160), 33: ("Borer", 9102170), 34: ("Deep Borer", 9102180), 35: ("Whelp", 9102190),
    36: ("Proto-Drake", 9102200), 37: ("Storm Dragon", 9102210), 38: ("Owl", 9102220), 39: ("Moonkin", 9102230),
    40: ("Moontouched Owlbeast", 9102240), 41: ("Voidling", 9102250), 42: ("Voidcreeper", 9102260),
    43: ("Voidcreeper Broodmother", 9102270), 44: ("Earthen Proto-Drake", 9102280), 45: ("Primal Tallstrider", 9102290),
}

# Lines of shapes (a form and what it grows into): "as a wolf" also counts as its worg.
LINES = {
    "wolf": (5, 17), "trogg": (6, 20), "saber": (7, 19), "moth": (8, 23), "boar": (9, 18),
    "plainstrider": (10, 16, 45), "bat": (11, 21), "manawyrm": (12, 22), "warpstalker": (13, 24),
    "toad": (14, 15, 30), "viper": (25, 26, 1, 3), "eagle": (27, 26), "komodo": (28, 29), "turtle": (31, 32),
    "borer": (33, 34), "whelp": (35, 36, 37, 44), "owl": (38, 39, 40), "void": (41, 42, 43),
    "berserker": (4, 2),
}


class Lantern:
    def __init__(self, key, region, map_id, x, y, z, o, where):
        self.key, self.region, self.map, self.x, self.y, self.z, self.o, self.where = (
            key, region, map_id, x, y, z, o, where)
        self.entry = None


class Thing:
    """Something the witches leave in the world (a goober gameobject that answers for one quest): a token to touch
    (an objective), or a lure that calls the creature a quest wants (summon = its entry)."""
    def __init__(self, key, name, display, spawns, size=1.0, summon=0):
        self.key, self.name, self.display, self.spawns, self.size, self.summon = (
            key, name, display, spawns, size, summon)
        self.entry = None
        self.quest = None


class Obj:
    def __init__(self, kind, count, text, **kw):
        self.kind, self.count, self.text, self.kw = kind, count, text, kw
        self.credit = None


def kill(entry, count, text):
    """Plain kill of one stock creature (the core counts it, also for the group)."""
    return Obj("kill", count, text, entry=entry)


def devour(count, text, entries=(), family=0, ctype=0, elite=False, any_meal=False, shapes=()):
    """Devour (Mgr::EatShape): any of the entries, a creature family, a creature type, an elite, or anything."""
    return Obj("devour", count, text, entries=tuple(entries), family=family, ctype=ctype, elite=elite,
               any_meal=any_meal, shapes=tuple(shapes))


def slay(count, text, entries=(), family=0, ctype=0, elite=False, any_kill=False, shapes=()):
    """Kill while wearing one of the shapes (or, without shapes, a kill the core alone cannot count)."""
    return Obj("slay", count, text, entries=tuple(entries), family=family, ctype=ctype, elite=elite,
               any_kill=any_kill, shapes=tuple(shapes))


def visit(text, map_id, x, y, radius=25.0):
    return Obj("visit", 1, text, map=map_id, x=x, y=y, radius=radius)


def touch(thing, count, text):
    return Obj("touch", count, text, thing=thing)


def item(entry, count, name):
    """A stock item that drops already (its own loot rows)."""
    return Obj("item", count, name, entry=entry)


class Quest:
    def __init__(self, qid, title, level, minlevel, giver, ender, voice, text, log, done, reward_text,
                 objectives=(), prev=None, races=0, needs=(), choices=(), items=(), xp=5, money=None, sort=0,
                 story="", lures=()):
        self.id, self.title, self.level, self.minlevel = qid, title, level, minlevel
        self.giver, self.ender, self.voice = giver, ender, voice
        self.text, self.log, self.done, self.reward_text = text, log, done, reward_text
        self.objectives = list(objectives)
        self.prev, self.races, self.needs = prev, races, tuple(needs)
        self.choices, self.items = list(choices), list(items)
        self.xp, self.sort, self.story = xp, sort, story
        self.lures = list(lures)
        self.money = money if money is not None else default_money(level, xp)


def default_money(level, xp):
    base = level * level * 6
    if level >= 70:
        base = int(base * 1.4)
    scale = {1: 0.25, 2: 0.4, 3: 0.6, 4: 0.8, 5: 1.0, 6: 1.5, 7: 2.0}.get(xp, 1.0)
    return int(base * scale)


class Book:
    def __init__(self):
        self.lanterns, self.things, self.quests = [], [], []
        self.regions = []                         # (title, intro, [quests]) for the doc

    def lantern(self, *args):
        lantern = Lantern(*args)
        lantern.entry = LANTERN_FIRST + len(self.lanterns)
        assert lantern.entry <= LANTERN_LAST
        self.lanterns.append(lantern)
        return lantern

    def thing(self, *args, **kw):
        thing = Thing(*args, **kw)
        thing.entry = THING_FIRST + len(self.things)
        assert thing.entry <= THING_LAST
        self.things.append(thing)
        return thing

    def region(self, title, intro):
        self.regions.append((title, intro, []))

    def quest(self, *args, **kw):
        quest = Quest(*args, **kw)
        assert Q_FIRST <= quest.id <= Q_LAST, quest.id
        assert all(q.id != quest.id for q in self.quests), quest.id
        self.quests.append(quest)
        self.regions[-1][2].append(quest)
        return quest


# --- output ----------------------------------------------------------------------------------------------------------

def q(text):
    return "'" + str(text).replace("\\", "\\\\").replace("'", "''") + "'"


def giver_ref(who):
    """('npc', entry) or ('go', entry) for a quest giver or ender."""
    if isinstance(who, Lantern):
        return ("go", who.entry)
    return ("npc", who)


def place(who):
    if isinstance(who, Lantern):
        return f"Hagatha's Lantern ({who.where}, {who.region})"
    return {HAGATHA: "Hagatha Hollowmoor in the In-Between", WREN: "Wren Hollowmoor in the In-Between"}[who]


def assign_credits(book):
    nxt = CREDIT_FIRST
    for quest in sorted(book.quests, key=lambda x: x.id):
        for obj in quest.objectives:
            if obj.kind in ("devour", "slay", "visit", "touch"):
                obj.credit = nxt
                nxt += 1
                assert nxt <= CREDIT_LAST + 1
            if obj.kind == "touch":
                assert obj.kw["thing"].quest in (None, quest.id), "one quest per thing"
                assert not obj.kw["thing"].summon, "a lure is not an objective"
                obj.kw["thing"].quest = quest.id
        for thing in quest.lures:
            assert thing.summon and thing.quest in (None, quest.id), "one quest per lure"
            thing.quest = quest.id


def check(book):
    by_id = {quest.id: quest for quest in book.quests}
    for quest in book.quests:
        assert 1 <= quest.minlevel <= quest.level <= 80, quest.title
        assert len(quest.objectives) <= 4, quest.title
        kills = [o for o in quest.objectives if o.kind != "item"]
        items = [o for o in quest.objectives if o.kind == "item"]
        assert len(kills) <= 4 and len(items) <= 4, quest.title
        assert len(quest.choices) <= 6 and len(quest.items) <= 4, quest.title
        if quest.prev:
            assert quest.prev in by_id or quest.prev in EXTERNAL_QUESTS, (quest.title, quest.prev)
            if quest.prev in by_id:
                assert by_id[quest.prev].minlevel <= quest.minlevel, quest.title
        for shape in quest.needs:
            assert shape in SHAPES, quest.title
        for obj in quest.objectives:
            for shape in obj.kw.get("shapes", ()):
                assert shape in SHAPES, quest.title
            assert len(obj.text) <= 60, (quest.title, obj.text)
        for text in (quest.text, quest.reward_text):
            assert len(text) < 2000, quest.title


def credit_rules(book):
    rules = []
    for quest in sorted(book.quests, key=lambda x: x.id):
        for obj in quest.objectives:
            if obj.kind not in ("devour", "slay"):
                continue
            event = "EventMeal" if obj.kind == "devour" else "EventKill"
            shapes = list(obj.kw.get("shapes", ()))[:4]
            shapes += [0] * (4 - len(shapes))
            filters = []
            for entry in obj.kw["entries"]:
                filters.append(("FilterEntry", entry))
            if obj.kw["family"]:
                filters.append(("FilterFamily", obj.kw["family"]))
            if obj.kw["ctype"]:
                filters.append(("FilterType", obj.kw["ctype"]))
            if obj.kw["elite"]:
                filters.append(("FilterElite", 0))
            if obj.kw.get("any_meal") or obj.kw.get("any_kill"):
                filters.append(("FilterAny", 0))
            assert filters, (quest.title, obj.text)
            for name, value in filters:
                rules.append((quest.id, obj.credit, event, name, value, shapes, quest.title, obj.text))
    return rules


def write_header(book):
    rules = credit_rules(book)
    out = [
        "// Generated by tools/devourer_quests.py (task 021) -- change the tool and run it again.",
        "#ifndef DEVOURER_QUESTS_IDS_H",
        "#define DEVOURER_QUESTS_IDS_H",
        "",
        "#include <cstdint>",
        "",
        "namespace Devourer::Quests",
        "{",
        "    enum Event : uint8_t { EventMeal = 1, EventKill = 2 };",
        "    enum Filter : uint8_t { FilterEntry = 1, FilterFamily = 2, FilterType = 3, FilterElite = 4, FilterAny = 5 };",
        "",
        "    // An event (a meal, a kill) that fits gives the credit of one quest objective, while the quest is open.",
        "    struct CreditRule { uint32_t Quest; uint32_t Credit; uint8_t Event; uint8_t Filter; uint32_t Value;"
        " uint32_t Shapes[4]; };",
        "    constexpr CreditRule CreditRules[] =",
        "    {",
    ]
    for qid, credit, event, name, value, shapes, title, text in rules:
        out.append(f"        {{ {qid}, {credit}, {event}, {name}, {value}, {{ {', '.join(map(str, shapes))} }} }},"
                   f"   // {title}: {text}")
    out += [
        "    };",
        "",
        "    // Being there: within Radius yards of X, Y on Map.",
        "    struct VisitRule { uint32_t Quest; uint32_t Credit; uint32_t Map; float X, Y, Radius; };",
        "    constexpr VisitRule VisitRules[] =",
        "    {",
    ]
    visits = [(quest, obj) for quest in sorted(book.quests, key=lambda x: x.id) for obj in quest.objectives
              if obj.kind == "visit"]
    for quest, obj in visits:
        kw = obj.kw
        out.append(f"        {{ {quest.id}, {obj.credit}, {kw['map']}, {kw['x']}f, {kw['y']}f, {kw['radius']}f }},"
                   f"   // {quest.title}: {obj.text}")
    if not visits:
        out.append("        { 0, 0, 0, 0.0f, 0.0f, 0.0f },")
    out += [
        "    };",
        "",
        "    // A witch's object (gameobject entry): a token gives the credit of its quest, a lure calls Summon.",
        "    struct UseRule { uint32_t Object; uint32_t Quest; uint32_t Credit; uint32_t Summon; };",
        "    constexpr UseRule UseRules[] =",
        "    {",
    ]
    touches = [(quest, obj) for quest in sorted(book.quests, key=lambda x: x.id) for obj in quest.objectives
               if obj.kind == "touch"]
    for quest, obj in touches:
        out.append(f"        {{ {obj.kw['thing'].entry}, {quest.id}, {obj.credit}, 0 }},   // {quest.title}: {obj.text}")
    lures = [(quest, thing) for quest in sorted(book.quests, key=lambda x: x.id) for thing in quest.lures]
    for quest, thing in lures:
        out.append(f"        {{ {thing.entry}, {quest.id}, 0, {thing.summon} }},   // {quest.title}: {thing.name}")
    if not touches and not lures:
        out.append("        { 0, 0, 0, 0 },")
    out += ["    };", "}", "", "#endif", ""]
    with open(HDR_OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out))


def write_sql(book):
    quests = sorted(book.quests, key=lambda x: x.id)
    o = []
    o += [
        "-- mod-devourer task 021: the Devourer's quests in the world (Hagatha's lanterns). src/DevourerQuests.cpp.",
        "-- Generated by tools/devourer_quests.py -- change the tool and run it again. Safe to run again.",
        f"-- Ids {Q_FIRST}-{CREDIT_LAST} (quests, credits, lanterns, objects), gameobject guids {GUID_FIRST}-{GUID_LAST}.",
        "",
        f"DELETE FROM `gameobject` WHERE `guid` BETWEEN {GUID_FIRST} AND {GUID_LAST};",
        f"DELETE FROM `gameobject_queststarter` WHERE `quest` BETWEEN {Q_FIRST} AND {Q_LAST};",
        f"DELETE FROM `gameobject_questender` WHERE `quest` BETWEEN {Q_FIRST} AND {Q_LAST};",
        f"DELETE FROM `creature_queststarter` WHERE `quest` BETWEEN {Q_FIRST} AND {Q_LAST};",
        f"DELETE FROM `creature_questender` WHERE `quest` BETWEEN {Q_FIRST} AND {Q_LAST};",
        f"DELETE FROM `gameobject_template` WHERE `entry` BETWEEN {LANTERN_FIRST} AND {THING_LAST};",
        f"DELETE FROM `creature_template_model` WHERE `CreatureID` BETWEEN {CREDIT_FIRST} AND {CREDIT_LAST};",
        f"DELETE FROM `creature_template` WHERE `entry` BETWEEN {CREDIT_FIRST} AND {CREDIT_LAST};",
        f"DELETE FROM `conditions` WHERE `SourceTypeOrReferenceId` = 19 AND `SourceEntry` BETWEEN {Q_FIRST} AND {Q_LAST};",
        f"DELETE FROM `quest_offer_reward` WHERE `ID` BETWEEN {Q_FIRST} AND {Q_LAST};",
        f"DELETE FROM `quest_request_items` WHERE `ID` BETWEEN {Q_FIRST} AND {Q_LAST};",
        f"DELETE FROM `quest_template_addon` WHERE `ID` BETWEEN {Q_FIRST} AND {Q_LAST};",
        f"DELETE FROM `quest_template` WHERE `ID` BETWEEN {Q_FIRST} AND {Q_LAST};",
        "",
        "-- --- Hagatha's lanterns (questgivers, one per region) and the witches' objects (goobers, one quest each) ---",
        "INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `IconName`, `castBarCaption`, `unk1`,"
        " `size`, `Data0`, `Data1`, `AIName`, `ScriptName`, `VerifiedBuild`) VALUES",
    ]
    rows = []
    for lantern in book.lanterns:
        rows.append(f"({lantern.entry}, 2, {LANTERN_DISPLAY}, {q(chr(39).join(['Hagatha', 's Lantern']))}, '', '', '',"
                    f" 1.4, 0, 0, '', '', 0)")
    for thing in book.things:
        assert thing.quest, thing.key
        rows.append(f"({thing.entry}, 10, {thing.display}, {q(thing.name)}, '', '', '', {thing.size}, 0,"
                    f" {thing.quest}, '', 'go_devourer_quest_object', 0)")
    o.append(",\n".join(rows) + ";")
    o += ["", "INSERT INTO `gameobject` (`guid`, `id`, `map`, `spawnMask`, `phaseMask`, `position_x`, `position_y`,"
              " `position_z`, `orientation`, `rotation0`, `rotation1`, `rotation2`, `rotation3`, `spawntimesecs`,"
              " `animprogress`, `state`, `Comment`) VALUES"]
    rows, guid = [], GUID_FIRST
    import math
    for lantern in book.lanterns:
        rows.append(f"({guid}, {lantern.entry}, {lantern.map}, 1, 1, {lantern.x}, {lantern.y}, {lantern.z},"
                    f" {lantern.o}, 0, 0, {round(math.sin(lantern.o / 2), 6)}, {round(math.cos(lantern.o / 2), 6)},"
                    f" 300, 255, 1, {q('mod-devourer: Hagatha' + chr(39) + 's Lantern, ' + lantern.where)})")
        guid += 1
    for thing in book.things:
        for (map_id, x, y, z, ori) in thing.spawns:
            rows.append(f"({guid}, {thing.entry}, {map_id}, 1, 1, {x}, {y}, {z}, {ori}, 0, 0,"
                        f" {round(math.sin(ori / 2), 6)}, {round(math.cos(ori / 2), 6)}, 60, 255, 1,"
                        f" {q('mod-devourer: ' + thing.name)})")
            guid += 1
    assert guid <= GUID_LAST + 1
    o.append(",\n".join(rows) + ";")

    credits = [(obj.credit, obj.text) for quest in quests for obj in quest.objectives if obj.credit]
    o += ["", "-- --- credits: one per objective the core cannot count by itself (never spawned) -----------------------",
          "DROP TEMPORARY TABLE IF EXISTS `devourer_tmp_ct`;",
          f"CREATE TEMPORARY TABLE `devourer_tmp_ct` SELECT * FROM `creature_template` WHERE `entry` = {TRIGGER_TEMPLATE};",
          "UPDATE `devourer_tmp_ct` SET `subname` = NULL, `faction` = 35, `npcflag` = 0, `unit_flags` = 33554434,"
          " `flags_extra` = 0, `AIName` = '', `ScriptName` = '', `VerifiedBuild` = 0;"]
    for credit, text in credits:
        o.append(f"UPDATE `devourer_tmp_ct` SET `entry` = {credit}, `name` = {q(text[:100])};")
        o.append("INSERT INTO `creature_template` SELECT * FROM `devourer_tmp_ct`;")
    o.append("DROP TEMPORARY TABLE `devourer_tmp_ct`;")
    o.append("INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`,"
             " `Probability`, `VerifiedBuild`) VALUES")
    o.append(",\n".join(f"({credit}, 0, {INVISIBLE_MODEL}, 1, 1, 0)" for credit, _ in credits) + ";")

    o += ["", "-- --- the quests -------------------------------------------------------------------------------------"]
    cols = ("`ID`, `QuestType`, `QuestLevel`, `MinLevel`, `QuestSortID`, `QuestInfoID`, `RewardXPDifficulty`,"
            " `RewardMoney`, `Flags`, `AllowableRaces`, `LogTitle`, `LogDescription`, `QuestDescription`,"
            " `AreaDescription`, `QuestCompletionLog`, "
            + ", ".join(f"`RequiredNpcOrGo{i}`, `RequiredNpcOrGoCount{i}`" for i in range(1, 5)) + ", "
            + ", ".join(f"`RequiredItemId{i}`, `RequiredItemCount{i}`" for i in range(1, 5)) + ", "
            + ", ".join(f"`RewardItem{i}`, `RewardAmount{i}`" for i in range(1, 5)) + ", "
            + ", ".join(f"`RewardChoiceItemID{i}`, `RewardChoiceItemQuantity{i}`" for i in range(1, 7)) + ", "
            + ", ".join(f"`ObjectiveText{i}`" for i in range(1, 5)) + ", `VerifiedBuild`")
    o.append(f"INSERT INTO `quest_template` ({cols}) VALUES")
    rows = []
    for quest in quests:
        npcs = [o2 for o2 in quest.objectives if o2.kind != "item"]
        items = [o2 for o2 in quest.objectives if o2.kind == "item"]
        req = []
        texts = []
        for i in range(4):
            if i < len(npcs):
                obj = npcs[i]
                req += [obj.kw["entry"] if obj.kind == "kill" else obj.credit, obj.count]
                texts.append(obj.text)
            else:
                req += [0, 0]
                texts.append("")
        ireq = []
        for i in range(4):
            ireq += [items[i].kw["entry"], items[i].count] if i < len(items) else [0, 0]
        rew = []
        for i in range(4):
            rew += [quest.items[i][0], quest.items[i][2]] if i < len(quest.items) else [0, 0]
        cho = []
        for i in range(6):
            cho += [quest.choices[i][0], 1] if i < len(quest.choices) else [0, 0]
        completion = "Return to " + place(quest.ender) + "."
        values = ([quest.id, 2, quest.level, quest.minlevel, quest.sort, 0, quest.xp, quest.money, 0, quest.races,
                   q(quest.title), q(quest.log), q(quest.text), "''", q(completion)] + req + ireq + rew + cho
                  + [q(t) for t in texts] + [0])
        rows.append("(" + ", ".join(str(v) for v in values) + ")")
    o.append(",\n".join(rows) + ";")
    o.append("INSERT INTO `quest_template_addon` (`ID`, `AllowableClasses`, `PrevQuestID`) VALUES")
    o.append(",\n".join(f"({quest.id}, {CLASS_DEVOURER}, {quest.prev or 0})" for quest in quests) + ";")
    o.append("INSERT INTO `quest_request_items` (`ID`, `EmoteOnComplete`, `EmoteOnIncomplete`, `CompletionText`,"
             " `VerifiedBuild`) VALUES")
    o.append(",\n".join(f"({quest.id}, 1, 1, {q(quest.done)}, 0)" for quest in quests) + ";")
    o.append("INSERT INTO `quest_offer_reward` (`ID`, `Emote1`, `RewardText`, `VerifiedBuild`) VALUES")
    o.append(",\n".join(f"({quest.id}, 1, {q(quest.reward_text)}, 0)" for quest in quests) + ";")

    for table, side in (("queststarter", "giver"), ("questender", "ender")):
        npc = [(giver_ref(getattr(quest, side))[1], quest.id) for quest in quests
               if giver_ref(getattr(quest, side))[0] == "npc"]
        go = [(giver_ref(getattr(quest, side))[1], quest.id) for quest in quests
              if giver_ref(getattr(quest, side))[0] == "go"]
        if npc:
            o.append(f"INSERT INTO `creature_{table}` (`id`, `quest`) VALUES "
                     + ", ".join(f"({a}, {b})" for a, b in npc) + ";")
        if go:
            o.append(f"INSERT INTO `gameobject_{table}` (`id`, `quest`) VALUES "
                     + ", ".join(f"({a}, {b})" for a, b in go) + ";")

    conds = []
    for quest in quests:
        for group, shape in enumerate(quest.needs):
            conds.append(f"(19, 0, {quest.id}, 0, {group}, 25, 0, {SHAPES[shape][1]}, 0, 0, 0, 0, 0, '',"
                         f" {q('mod-devourer: ' + quest.title + ' needs the ' + SHAPES[shape][0] + ' shape')})")
    if conds:
        o += ["", "-- Quests for one shape (or its line): offered only to a Devourer that owns it (knows its form spell).",
              "INSERT INTO `conditions` (`SourceTypeOrReferenceId`, `SourceGroup`, `SourceEntry`, `SourceId`,"
              " `ElseGroup`, `ConditionTypeOrReference`, `ConditionTarget`, `ConditionValue1`, `ConditionValue2`,"
              " `ConditionValue3`, `NegativeCondition`, `ErrorType`, `ErrorTextId`, `ScriptName`, `Comment`) VALUES",
              ",\n".join(conds) + ";"]
    o.append("")
    with open(SQL_OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(o))


def money_text(copper):
    g, s, c = copper // 10000, copper // 100 % 100, copper % 100
    parts = ([f"{g}g"] if g else []) + ([f"{s}s"] if s else []) + ([f"{c}c"] if c and not g else [])
    return " ".join(parts) or "0"


def write_doc(book):
    out = ["# The Devourer's quests (task 021)", "",
           "Generated by `tools/devourer_quests.py` -- edit the tool, not this file. Hagatha's lanterns burn where the",
           "world is thin; the sisters speak through them. Every quest is for the Devourer only (class 10). Rewards are",
           "stock 3.3.5a items (pick one where there is a choice), money and experience.", ""]
    total = 0
    for title, intro, quests in book.regions:
        out += [f"## {title}", "", intro, "",
                "| Lvl | Quest | Story | Objectives | Rewards |", "|---|---|---|---|---|"]
        for quest in quests:
            total += 1
            objs = "; ".join(f"{o2.text} x{o2.count}" if o2.count > 1 else o2.text for o2 in quest.objectives) or "-"
            rewards = []
            if quest.choices:
                rewards.append("one of: " + ", ".join(name for _, name in quest.choices))
            for _, name, count in quest.items:
                rewards.append(f"{count}x {name}" if count > 1 else name)
            rewards.append(money_text(quest.money))
            need = (" *(" + "/".join(SHAPES[s][0] for s in quest.needs) + " only)*") if quest.needs else ""
            out.append(f"| {quest.level} | {quest.title}{need} | {quest.story} | {objs} | {'; '.join(rewards)} |")
        out.append("")
    out.insert(5, f"{total} quests in {len(book.regions)} regions, {len(book.lanterns)} lanterns.")
    out.insert(6, "")
    with open(DOC_OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out))


def main():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import devourer_quests_content
    book = Book()
    devourer_quests_content.build(book)
    check(book)
    assign_credits(book)
    write_sql(book)
    write_header(book)
    write_doc(book)
    print(f"{len(book.quests)} quests, {len(book.lanterns)} lanterns, {len(book.things)} objects ->",
          os.path.relpath(SQL_OUT, ROOT), os.path.relpath(HDR_OUT, ROOT), os.path.relpath(DOC_OUT, ROOT))


if __name__ == "__main__":
    main()
