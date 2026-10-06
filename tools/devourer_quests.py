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
HDR_OUT = os.path.join(ROOT, "src", "DevourerQuestsIds.h")
HEIGHTS = os.path.join(ROOT, "tools", "quest_heights.json")   # "map x y" -> ground z, for spawns written with z 0.0


def _heights():
    import json
    try:
        with open(HEIGHTS, encoding="utf-8") as f:
            return json.load(f)
    except OSError:
        return {}


def ground_z(map_id, x, y, z):
    """The z to spawn at: the given one, or (z exactly 0.0) the ground height measured for that spot."""
    if z != 0.0 or map_id == 35:
        return z
    key = f"{map_id} {x} {y}"
    heights = _heights()
    assert key in heights, f"no height for {key}: run the heights tool (docs/tasks/022-mount-quests.md)"
    return heights[key]


def zero_spots(books):
    """Every spawn still written with z 0.0 (for the heights tool)."""
    out = []
    for book in books:
        for thing in book.things:
            out += [(m, x, y) for (m, x, y, z, o) in thing.spawns if z == 0.0 and m != 35]
        for beast in book.beasts:
            out += [(m, x, y) for (m, x, y, z, o) in beast.spawns if z == 0.0 and m != 35]
    return out


class Block:
    """One id block and output set: the lantern quests (task 021) and the mount quests (task 022) each have one."""
    def __init__(self, name, task, quests, credits, beasts, givers, things, go_guids, npc_guids, sql, doc,
                 speaker=0, speaker_guids=(0, 0)):
        self.name, self.task = name, task
        self.q_first, self.q_last = quests
        self.credit_first, self.credit_last = credits
        self.beast_first, self.beast_last = beasts
        self.giver_first, self.giver_last = givers      # gameobject_template: lanterns / the WANTED board
        self.thing_first, self.thing_last = things      # gameobject_template: what the witches leave to be touched
        self.guid_first, self.guid_last = go_guids      # gameobject spawns
        self.npc_guid_first, self.npc_guid_last = npc_guids   # creature spawns (the quests' own creatures)
        self.speaker, (self.speaker_guid_first, self.speaker_guid_last) = speaker, speaker_guids
        self.sql_out = os.path.join(ROOT, "data", "sql", "db-world", sql)
        self.doc_out = os.path.join(ROOT, "docs", doc)


LANTERNS = Block("lanterns", "021", (9105000, 9105399), (9105400, 9105899), (9105900, 9105979), (9105000, 9105099),
                 (9105100, 9105199), (9920000, 9920499), (9920600, 9920999), "2026_10_05_10_devourer_quests.sql",
                 "quests.md", speaker=9105990, speaker_guids=(9920500, 9920599))
MOUNTS = Block("mounts", "022", (9109000, 9109399), (9109400, 9109899), (9109900, 9109979), (9109000, 9109009),
               (9109010, 9109199), (9921000, 9921999), (9922000, 9922999), "2026_10_06_20_devourer_mount_quests.sql",
               "mount-quests.md")

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
    17: ("Bloodsnout Worg", 9102010), 18: ("Armoredon", 9102020), 19: ("Shadowclaw", 9102030),
    20: ("Rockjaw Backbreaker", 9102040), 21: ("Vampiric Duskbat", 9102050), 22: ("Greatwyrm", 9102060),
    23: ("Royal Blue Flutterer", 9102070), 24: ("Thunder Lizard", 9102080), 25: ("Viper", 9102090),
    26: ("Wind Serpent", 9102100), 27: ("Baby Eagle", 9102110), 28: ("Baby Komodo", 9102120),
    29: ("Komodo Dragon", 9102130), 30: ("Water Salamander", 9102140), 31: ("Snapjaw", 9102150),
    32: ("Spikeshell", 9102160), 33: ("Borer", 9102170), 34: ("Deep Borer", 9102180), 35: ("Whelp", 9102190),
    36: ("Proto-Drake", 9102200), 37: ("Storm Dragon", 9102210), 38: ("Owl", 9102220), 39: ("Moonkin", 9102230),
    40: ("Moontouched Owlbeast", 9102240), 41: ("Voidling", 9102250), 42: ("Voidcreeper", 9102260),
    43: ("Voidcreeper Broodmother", 9102270), 44: ("Earthen Proto-Drake", 9102280), 45: ("Primal Tallstrider", 9102290),
    46: ("Bear Cub", 9102300), 47: ("Dreambear", 9102310), 48: ("Runebear", 9102320), 49: ("Grub", 9102330),
    50: ("Rhino Beetle", 9102340), 51: ("Glasswing", 9102350), 52: ("Kunchong", 9102360), 53: ("Stingwing", 9102370),
}

# Lines of shapes (a form and what it grows into): "as a wolf" also counts as its worg.
LINES = {
    "wolf": (5, 17), "trogg": (6, 20), "saber": (7, 19), "moth": (8, 23), "boar": (9, 18),
    "plainstrider": (10, 16, 45), "bat": (11, 21), "manawyrm": (12, 22), "warpstalker": (13, 24), "komodo_storm": (28, 24),
    "toad": (14, 15, 30), "viper": (25, 26, 1, 3), "eagle": (27, 26), "komodo": (28, 29), "turtle": (31, 32),
    "borer": (33, 34), "whelp": (35, 36, 37, 44), "owl": (38, 39, 40), "void": (41, 42, 43),
    "berserker": (4, 2),
    "bear": (46, 47, 48), "grub": (49, 50, 51, 52, 53), "beetle": (50, 52), "glasswing": (51, 53),
}


class Lantern:
    """A gameobject questgiver: Hagatha's lantern in a region, or Wren's WANTED board in the In-Between."""
    def __init__(self, key, region, map_id, x, y, z, o, where, name="Hagatha's Lantern", display=None, size=1.4):
        self.key, self.region, self.map, self.x, self.y, self.z, self.o, self.where = (
            key, region, map_id, x, y, z, o, where)
        self.name, self.display, self.size = name, display or LANTERN_DISPLAY, size
        self.entry = None

    @property
    def Region(self):
        """The region's name at the start of a sentence ("The Barrens")."""
        return self.region[:1].upper() + self.region[1:]


class Thing:
    """Something the witches leave in the world (a goober gameobject that answers for one quest): a token to touch
    (an objective), a lure that calls the creature a quest wants (summon = its entry, count of them), or a campfire
    that tells a tale (lines, by speaker; companion: Bramble must listen too; reaction: what she says after)."""
    def __init__(self, key, name, display, spawns, size=1.0, summon=0, count=1, lines=(), speaker="",
                 companion=False, reaction="", follow=False, shapes=(), shared=False):
        self.key, self.name, self.display, self.spawns, self.size, self.summon, self.count = (
            key, name, display, spawns, size, summon, count)
        self.lines, self.speaker, self.companion, self.reaction = list(lines), speaker, companion, reaction
        self.follow = follow                      # a lure whose creature stays with the Devourer until the quest ends
        self.shapes = tuple(shapes)               # a lure that only answers to one of these shapes
        self.shared = shared                      # several quests use it (no quest on the template; the script picks)
        self.entry = None
        self.quest = None


class Beast:
    """A creature of the quests' own (a creature_template copy of a stock one, with its own name and maybe look)."""
    def __init__(self, key, name, clone_of, display=0, scale=1.0, level=None, faction=None, subname="",
                 passive=False, spawns=(), npcflag=0, gossip=(), sound=0):
        self.key, self.name, self.clone_of, self.display, self.scale = key, name, clone_of, display, scale
        self.level, self.faction, self.subname, self.passive = level, faction, subname, passive
        self.spawns, self.npcflag, self.gossip, self.sound = list(spawns), npcflag, list(gossip), sound
        self.gossip_quest, self.gossip_credit = 0, 0   # set by the gossip objective that uses it
        self.entry = None


class Obj:
    def __init__(self, kind, count, text, **kw):
        self.kind, self.count, self.text, self.kw = kind, count, text, kw
        self.credit = None


def kill(entry, count, text):
    """Plain kill of one stock creature (the core counts it, also for the group)."""
    return Obj("kill", count, text, entry=entry)


FLAG_COMPANION, FLAG_FLEE, FLAG_FAIL, FLAG_FOLLOW, FLAG_NIGHT, FLAG_NOFLYING, FLAG_SNIFF, FLAG_NOSNIFF = (
    1, 2, 4, 8, 16, 32, 64, 128)
VISIT_QUIET, VISIT_NIGHT, VISIT_DAWN, VISIT_WALKING, VISIT_NOFLYING, VISIT_SNIFF, VISIT_NOSNIFF, VISIT_STILL = (
    1, 2, 4, 8, 16, 32, 64, 128)
CARRY_FAIL_LOST = 1
EVENT_LOOT = 6


def devour(count, text, entries=(), family=0, ctype=0, elite=False, any_meal=False, shapes=(), companion=None):
    """Devour (Mgr::EatShape): any of the entries, a creature family, a creature type, an elite, or anything.
    companion: a line Bramble says when she watches it happen (then she has to be there for it to count)."""
    return Obj("devour", count, text, entries=tuple(entries), family=family, ctype=ctype, elite=elite,
               any_meal=any_meal, shapes=tuple(shapes), companion=companion)


def slay(count, text, entries=(), family=0, ctype=0, elite=False, any_kill=False, shapes=()):
    """Kill while wearing one of the shapes (or, without shapes, a kill the core alone cannot count)."""
    return Obj("slay", count, text, entries=tuple(entries), family=family, ctype=ctype, elite=elite,
               any_kill=any_kill, shapes=tuple(shapes))


EMOTE_PET, EMOTE_ROAR, EMOTE_HUG, EMOTE_WAVE, EMOTE_DANCE, EMOTE_KISS, EMOTE_BOW, EMOTE_CHEER = (
    410, 75, 56, 101, 34, 58, 17, 21)


def emote(count, text, emote_id, entries=(), family=0, ctype=0, shapes=(), flee=False, follow=False):
    """Do a text emote (/roar, /pet, ...) at a creature that fits; each creature counts once.
    flee: it runs away; follow: it trots after the Devourer for a while, then goes home (a spared one)."""
    return Obj("emote", count, text, emote=emote_id, entries=tuple(entries), family=family, ctype=ctype,
               elite=False, shapes=tuple(shapes), flee=flee, follow=follow)


def struck(count, text, entries=(), family=0, ctype=0, shapes=()):
    """Let a creature that fits use one of its abilities on the Devourer (its trick, learned before the meal)."""
    return Obj("struck", count, text, entries=tuple(entries), family=family, ctype=ctype, elite=False,
               shapes=tuple(shapes))


def spare(text, entries):
    """Not an objective in the log: killing one of these fails the quest (the one the Devourer was asked to spare)."""
    return Obj("spare", 0, text, entries=tuple(entries), family=0, ctype=0, elite=False, shapes=())


def ability(count, text, spell, entries=(), family=0, ctype=0, shapes=()):
    """Use a form's ability (spell id) on a creature that fits; each creature counts once."""
    return Obj("ability", count, text, spell=spell, entries=tuple(entries), family=family, ctype=ctype,
               elite=False, shapes=tuple(shapes))


def visit(text, map_id, x, y, radius=25.0, shapes=(), quiet=False, night=False, dawn=False, walking=False,
          noflying=False, sniff=None, stay=0, still=False, achievement=0, above=-100000):
    """Be at a place (maybe in a certain shape; quiet: without being in a fight, i.e. walked in unnoticed; night /
    dawn: at that time of day; walking: not running, not mounted; noflying: not on a flying mount; sniff True/False:
    with Sniff on / off; stay: for that many seconds (still: without moving); achievement: a criteria asset given;
    above: standing at least that high (z), for tops and ledges)."""
    flags = ((VISIT_QUIET if quiet else 0) | (VISIT_NIGHT if night else 0) | (VISIT_DAWN if dawn else 0)
             | (VISIT_WALKING if walking else 0) | (VISIT_NOFLYING if noflying else 0)
             | (VISIT_SNIFF if sniff is True else 0) | (VISIT_NOSNIFF if sniff is False else 0)
             | (VISIT_STILL if still else 0))
    return Obj("visit", 1, text, map=map_id, x=x, y=y, radius=radius, shapes=tuple(shapes), quiet=quiet, flags=flags,
               stay=stay, achievement=achievement, above=above)


def among(text, map_id, x, y, entries, shapes, radius=15.0):
    """Walk to the middle of a pack (x, y) in one of the shapes without starting a fight. While the Devourer wears
    the shape there, the pack's creatures (entries) take it for one of their own and do not attack."""
    return Obj("visit", 1, text, map=map_id, x=x, y=y, radius=radius, shapes=tuple(shapes), quiet=True,
               among=tuple(entries))


def wake(thing, text, night=False, noflying=False):
    """Using a lure counts for the quest (the eggs that crack, the hatch): the lure's creatures come, and the
    objective is done. night / noflying: only then."""
    return Obj("wake", 1, text, thing=thing, night=night, noflying=noflying)


def gossip(beast, text):
    """The right answer to one of the quests' own creatures (its gossip) counts."""
    return Obj("gossip", 1, text, beast=beast)


def tale(thing, text):
    """Sit by a campfire (the thing, with lines) and hear one of the sisters' tales to its end."""
    return Obj("tale", 1, text, thing=thing)


def trail(text, name, map_id, points, summon=0, radius=20.0):
    """Follow a scent trail with Sniff on, point after point; the last one calls `summon` (if any)."""
    assert 2 <= len(points) <= 6
    return Obj("trail", 1, text, name=name, map=map_id, points=list(points), summon=summon, radius=radius)


def touch(thing, count, text, shapes=(), night=False, noflying=False, sniff=None):
    """Use an object (count of them, if it has several spawns); in a shape, at night, on foot, with Sniff on/off."""
    flags = ((FLAG_NIGHT if night else 0) | (FLAG_NOFLYING if noflying else 0) | (FLAG_SNIFF if sniff is True else 0)
             | (FLAG_NOSNIFF if sniff is False else 0))
    return Obj("touch", count, text, thing=thing, shapes=tuple(shapes), flags=flags)


def carry(thing, text, map_id, x, y, radius=12.0, seconds=0, dips=(), dip_radius=8.0, slow=0, achievement=0,
          fail_lost=False, picked="You pick it up. It does not want to be carried.", warning="It is fading.",
          refreshed="It brightens again.", lost="It is gone dark.", delivered="Delivered."):
    """Pick something up at an object (thing) and carry it to a place. seconds: it is lost after that long unless
    refreshed at a dip (dips: points); slow: run speed lost while carrying (%); achievement: a criteria asset given
    when it arrives without ever being lost; fail_lost: the quest fails when it is lost."""
    assert len(dips) <= 4
    return Obj("carry", 1, text, thing=thing, map=map_id, x=x, y=y, radius=radius, seconds=seconds, dips=list(dips),
               dip_radius=dip_radius, slow=slow, achievement=achievement, fail_lost=fail_lost, picked=picked,
               warning=warning, refreshed=refreshed, lost=lost, delivered=delivered)


def fish(count, text, near=0, line=""):
    """A catch from a fishing bobber while the creature (entry; 0: anywhere) is within 25 yards; it emotes line."""
    return Obj("fish", count, text, entries=(near,) if near else (), family=0, ctype=0, elite=False, shapes=(),
               any_meal=not near, line=line)


def item(entry, count, name):
    """A stock item that drops already (its own loot rows)."""
    return Obj("item", count, name, entry=entry)


class Quest:
    def __init__(self, qid, title, level, minlevel, giver, ender, voice, text, log, done, reward_text,
                 objectives=(), prev=None, races=0, needs=(), choices=(), items=(), xp=5, money=None, sort=0,
                 story="", lures=(), timed=0, event=0, mail=None):
        self.id, self.title, self.level, self.minlevel = qid, title, level, minlevel
        self.giver, self.ender, self.voice = giver, ender, voice
        self.text, self.log, self.done, self.reward_text = text, log, done, reward_text
        self.objectives = list(objectives)
        self.prev, self.races, self.needs = prev, races, tuple(needs)
        self.choices, self.items = list(choices), list(items)
        self.xp, self.sort, self.story = xp, sort, story
        self.lures = list(lures)
        self.timed = timed                        # seconds to finish it in (quest_template.TimeAllowed), 0 = none
        self.event = event                        # game_event id the quest is only offered during (holidays)
        self.mail = mail                          # (subject, body, delay seconds): a letter sent when it completes
        self.money = money if money is not None else default_money(level, xp)


def default_money(level, xp):
    base = level * level * 6
    if level >= 70:
        base = int(base * 1.4)
    scale = {1: 0.25, 2: 0.4, 3: 0.6, 4: 0.8, 5: 1.0, 6: 1.5, 7: 2.0}.get(xp, 1.0)
    return int(base * scale)


class Book:
    def __init__(self, block=None):
        self.block = block or LANTERNS
        self.lanterns, self.things, self.quests, self.beasts = [], [], [], []
        self.regions = []                         # (title, intro, [quests]) for the doc

    def lantern(self, *args, **kw):
        lantern = Lantern(*args, **kw)
        lantern.entry = self.block.giver_first + len(self.lanterns)
        assert lantern.entry <= self.block.giver_last
        self.lanterns.append(lantern)
        return lantern

    def beast(self, *args, **kw):
        beast = Beast(*args, **kw)
        beast.entry = self.block.beast_first + len(self.beasts)
        assert beast.entry <= self.block.beast_last
        self.beasts.append(beast)
        return beast

    def thing(self, *args, **kw):
        thing = Thing(*args, **kw)
        thing.entry = self.block.thing_first + len(self.things)
        assert thing.entry <= self.block.thing_last
        self.things.append(thing)
        return thing

    def region(self, title, intro):
        self.regions.append((title, intro, []))

    def quest(self, *args, **kw):
        quest = Quest(*args, **kw)
        assert self.block.q_first <= quest.id <= self.block.q_last, quest.id
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
        return f"{who.name} ({who.where}, {who.region})"
    return {HAGATHA: "Hagatha Hollowmoor in the In-Between", WREN: "Wren Hollowmoor in the In-Between",
            9101360: "Wren Hollowmoor at the Derby's starting line, west of the Crossroads"}[who]


def assign_credits(book):
    nxt = book.block.credit_first
    for quest in sorted(book.quests, key=lambda x: x.id):
        for obj in quest.objectives:
            if obj.kind in ("devour", "slay", "visit", "touch", "emote", "ability", "trail", "struck", "tale", "carry",
                            "fish", "gossip", "wake"):
                obj.credit = nxt
                nxt += 1
                assert nxt <= book.block.credit_last + 1
            if obj.kind in ("touch", "tale", "carry"):
                thing = obj.kw["thing"]
                assert thing.shared or thing.quest in (None, quest.id), "one quest per thing"
                assert not thing.summon, "a lure is not an objective"
                thing.quest = thing.quest or quest.id
            if obj.kind == "wake":
                thing = obj.kw["thing"]
                assert thing.summon and (thing.shared or thing.quest in (None, quest.id)), "one quest per lure"
                thing.quest = thing.quest or quest.id
            if obj.kind == "gossip":
                beast = obj.kw["beast"]
                assert beast.gossip, "a gossip objective needs a creature with gossip"
                beast.gossip_quest, beast.gossip_credit = quest.id, obj.credit
        for thing in quest.lures:
            assert thing.summon and (thing.shared or thing.quest in (None, quest.id)), "one quest per lure"
            thing.quest = thing.quest or quest.id


def check(book):
    by_id = {quest.id: quest for quest in book.quests}
    for quest in book.quests:
        assert 1 <= quest.minlevel <= quest.level <= 80, quest.title
        assert len([o for o in quest.objectives if o.kind != "spare"]) <= 4, quest.title
        kills = [o for o in quest.objectives if o.kind not in ("item", "spare")]
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
            if obj.kind not in ("devour", "slay", "emote", "ability", "struck", "spare", "fish"):
                continue
            event = {"devour": "EventMeal", "slay": "EventKill", "emote": "EventEmote", "ability": "EventSpell",
                     "struck": "EventStruck", "spare": "EventKill", "fish": "EventLoot"}[obj.kind]
            detail = obj.kw.get("emote", 0) or obj.kw.get("spell", 0)
            flags = ((FLAG_COMPANION if obj.kw.get("companion") else 0) | (FLAG_FLEE if obj.kw.get("flee") else 0)
                     | (FLAG_FAIL if obj.kind == "spare" else 0) | (FLAG_FOLLOW if obj.kw.get("follow") else 0))
            line = obj.kw.get("companion") or obj.kw.get("line") or ""
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
                rules.append((quest.id, obj.credit or 0, event, name, value, detail, flags, shapes, line,
                              quest.title, obj.text))
    return rules


def cstr(text):
    return '"' + str(text).replace('\\', '\\\\').replace('"', '\\"') + '"'


def write_header(books):
    rules = [r for book in books for r in credit_rules(book)]
    quests_all = sorted((q for book in books for q in book.quests), key=lambda x: x.id)
    out = [
        "// Generated by tools/devourer_quests.py (task 021) -- change the tool and run it again.",
        "#ifndef DEVOURER_QUESTS_IDS_H",
        "#define DEVOURER_QUESTS_IDS_H",
        "",
        "#include <cstdint>",
        "",
        "namespace Devourer::Quests",
        "{",
        "    enum Event : uint8_t { EventMeal = 1, EventKill = 2, EventEmote = 3, EventSpell = 4, EventStruck = 5, EventLoot = 6 };",
        "    enum Filter : uint8_t { FilterEntry = 1, FilterFamily = 2, FilterType = 3, FilterElite = 4, FilterAny = 5 };",
        "    enum Flag : uint8_t { FlagCompanion = 1, FlagFlee = 2, FlagFail = 4, FlagFollow = 8, FlagNight = 16, FlagNoFlying = 32,"
        " FlagSniff = 64, FlagNoSniff = 128 };",
        "    enum VisitFlag : uint8_t { VisitQuiet = 1, VisitNight = 2, VisitDawn = 4, VisitWalking = 8, VisitNoFlying = 16,"
        " VisitSniff = 32, VisitNoSniff = 64, VisitStill = 128 };",
        "    enum CarryFlag : uint8_t { CarryFailLost = 1 };",
        "",
        "    // An event (a meal, a kill, an emote at a creature, an ability on it) that fits gives the credit of one",
        "    // quest objective, while the quest is open. Detail: the text emote (TEXT_EMOTE_*) or the spell, 0 for meals",
        "    // and kills. Flags: FlagCompanion (Bramble must watch; she says Line), FlagFlee (the creature runs away),",
        "    // FlagFail (killing it fails the quest: the one to spare), FlagFollow (it follows the Devourer a while).",
        "    struct CreditRule { uint32_t Quest; uint32_t Credit; uint8_t Event; uint8_t Filter; uint32_t Value;"
        " uint32_t Detail; uint8_t Flags; uint32_t Shapes[4]; char const* Line; };",
        "    constexpr CreditRule CreditRules[] =",
        "    {",
    ]
    for qid, credit, event, name, value, detail, flags, shapes, line, title, text in rules:
        out.append(f"        {{ {qid}, {credit}, {event}, {name}, {value}, {detail}, {flags},"
                   f" {{ {', '.join(map(str, shapes))} }}, {cstr(line)} }},   // {title}: {text}")
    out += [
        "    };",
        "",
        "    // Being there: within Radius yards of X, Y on Map (in one of the Shapes, if any; VisitQuiet: not in a fight;",
        "    // the other flags: at night / at dawn / walking / not flying / with Sniff on or off / standing still), for",
        "    // Seconds if any; Achievement: a criteria asset (ACHIEVEMENT_CRITERIA_TYPE_BE_SPELL_TARGET) given with it.",
        "    struct VisitRule { uint32_t Quest; uint32_t Credit; uint32_t Map; float X, Y, Radius; uint32_t Shapes[4];"
        " uint8_t Flags; uint16_t Seconds; uint32_t Achievement; float Above; };",
        "    // Above: the Devourer has to stand at least that high (the top of a temple, a ledge); -100000 = anywhere.",
        "    constexpr VisitRule VisitRules[] =",
        "    {",
    ]
    visits = [(quest, obj) for quest in quests_all for obj in quest.objectives if obj.kind == "visit"]
    for quest, obj in visits:
        kw = obj.kw
        shapes = list(kw.get("shapes", ()))[:4]
        shapes += [0] * (4 - len(shapes))
        flags = kw.get("flags", VISIT_QUIET if kw.get("quiet") else 0)
        out.append(f"        {{ {quest.id}, {obj.credit}, {kw['map']}, {float(kw['x'])}f, {float(kw['y'])}f, {float(kw['radius'])}f,"
                   f" {{ {', '.join(map(str, shapes))} }}, {flags}, {kw.get('stay', 0)}, {kw.get('achievement', 0)},"
                   f" {float(kw.get('above', -100000))}f }},"
                   f"   // {quest.title}: {obj.text}")
    if not visits:
        out.append("        { 0, 0, 0, 0.0f, 0.0f, 0.0f, { 0, 0, 0, 0 }, 0, 0, 0, -100000.0f },")
    out += [
        "    };",
        "",
        "    // A witch's object (gameobject entry): a token gives the credit of its quest, a lure calls Count x Summon,",
        "    // a campfire tells Lines (by Speaker) and counts at the end (FlagCompanion: Bramble listens; Reaction).",
        "    // Flags on a touch: FlagNight / FlagNoFlying / FlagSniff / FlagNoSniff; on a lure: FlagFollow (it stays).",
        "    struct UseRule { uint32_t Object; uint32_t Quest; uint32_t Credit; uint32_t Summon; uint32_t Count;"
        " uint8_t Flags; uint8_t LineCount; char const* const* Lines; char const* Speaker; char const* Reaction;"
        " uint32_t Shapes[4]; };",
        "@@TALE_LINES@@",
        "    constexpr UseRule UseRules[] =",
        "    {",
    ]
    touches = [(quest, obj) for quest in quests_all for obj in quest.objectives if obj.kind == "touch"]
    tales = [(quest, obj) for quest in quests_all for obj in quest.objectives if obj.kind == "tale"]
    lines_decl = []
    for quest, obj in tales:
        thing = obj.kw["thing"]
        lines_decl.append(f"    constexpr char const* TaleLines{thing.entry}[] = {{ "
                          + ", ".join(cstr(line) for line in thing.lines) + " };")
    def shapes4(seq):
        lst = list(seq)[:4]
        return "{ " + ", ".join(map(str, lst + [0] * (4 - len(lst)))) + " }"
    for quest, obj in touches:
        out.append(f"        {{ {obj.kw['thing'].entry}, {quest.id}, {obj.credit}, 0, 0, {obj.kw.get('flags', 0)}, 0, nullptr,"
                   f" \"\", \"\", {shapes4(obj.kw.get('shapes', ()))} }},   // {quest.title}: {obj.text}")
    for quest, obj in tales:
        thing = obj.kw["thing"]
        out.append(f"        {{ 0, {quest.id}, {obj.credit}, 0, 0, {FLAG_COMPANION if thing.companion else 0},"
                   f" {len(thing.lines)}, TaleLines{thing.entry}, {cstr(thing.speaker)}, {cstr(thing.reaction)},"
                   f" {{ 0, 0, 0, 0 }} }},   // {quest.title}: {obj.text}")
    wakes = [(quest, obj) for quest in quests_all for obj in quest.objectives if obj.kind == "wake"]
    lures = [(quest, thing, 0) for quest in quests_all for thing in quest.lures]
    lures += [(quest, obj.kw["thing"], obj.credit) for quest, obj in wakes]
    wake_flags = {(quest.id, obj.kw["thing"].entry): (FLAG_NIGHT if obj.kw.get("night") else 0)
                  | (FLAG_NOFLYING if obj.kw.get("noflying") else 0) for quest, obj in wakes}
    for quest, thing, credit in lures:
        flags = (FLAG_FOLLOW if thing.follow else 0) | wake_flags.get((quest.id, thing.entry), 0)
        out.append(f"        {{ {thing.entry}, {quest.id}, {credit}, {thing.summon}, {thing.count},"
                   f" {flags}, 0, nullptr, \"\", \"\", {shapes4(thing.shapes)} }},"
                   f"   // {quest.title}: {thing.name}")
    if not touches and not lures and not tales:
        out.append('        { 0, 0, 0, 0, 0, 0, 0, nullptr, "", "", { 0, 0, 0, 0 } },')
    out += [
        "    };",
        "",
        "    // A pack that takes the Devourer for one of its own: within Radius x 3 of X, Y, wearing one of the Shapes,",
        "    // the Entries there do not attack it (they forget it again when it leaves or changes shape).",
        "    struct DisguiseRule { uint32_t Quest; uint32_t Map; float X, Y, Radius; uint32_t Shapes[4];"
        " uint32_t Entries[8]; };",
        "    constexpr DisguiseRule DisguiseRules[] =",
        "    {",
    ]
    packs = [(quest, obj) for quest in quests_all for obj in quest.objectives if obj.kind == "visit" and obj.kw.get("among")]
    for quest, obj in packs:
        kw = obj.kw
        shapes = list(kw["shapes"])[:4] + [0] * (4 - len(kw["shapes"][:4]))
        entries = list(kw["among"])[:8] + [0] * (8 - len(kw["among"][:8]))
        out.append(f"        {{ {quest.id}, {kw['map']}, {kw['x']}f, {kw['y']}f, {kw['radius']}f,"
                   f" {{ {', '.join(map(str, shapes))} }}, {{ {', '.join(map(str, entries))} }} }},"
                   f"   // {quest.title}")
    if not packs:
        out.append("        { 0, 0, 0.0f, 0.0f, 0.0f, { 0, 0, 0, 0 }, { 0, 0, 0, 0, 0, 0, 0, 0 } },")
    out += [
        "    };",
        "",
        "    // A scent trail: with Sniff on, the Devourer is told the way to the next point; the last one calls Summon.",
        "    struct TrackPoint { float X, Y; };",
        "    struct TrackRule { uint32_t Quest; uint32_t Credit; uint32_t Map; uint8_t Count; TrackPoint Points[6];"
        " float Radius; uint32_t Summon; char const* Name; };",
        "    constexpr TrackRule TrackRules[] =",
        "    {",
    ]
    trails = [(quest, obj) for quest in quests_all for obj in quest.objectives if obj.kind == "trail"]
    for quest, obj in trails:
        kw = obj.kw
        pts = list(kw["points"]) + [(0.0, 0.0)] * (6 - len(kw["points"]))
        out.append(f"        {{ {quest.id}, {obj.credit}, {kw['map']}, {len(kw['points'])}, {{ "
                   + ", ".join(f"{{ {float(x)}f, {float(y)}f }}" for x, y in pts)
                   + f" }}, {kw['radius']}f, {kw['summon']}, {cstr(kw['name'])} }},   // {quest.title}")
    if not trails:
        out.append('        { 0, 0, 0, 0, { }, 0.0f, 0, "" },')
    out += [
        "    };",
        "",
        "    // Carrying something: picked up at Pick (gameobject entry), delivered within Radius of X, Y on Map. With Seconds",
        "    // it is lost after that long, unless the Devourer passes one of the Refresh points (within RefreshRadius);",
        "    // Slow: run speed lost while carrying (%); Achievement: a criteria asset given when it arrives never lost.",
        "    struct CarryRule { uint32_t Quest; uint32_t Credit; uint32_t Pick; uint32_t Map; float X, Y, Radius;"
        " uint16_t Seconds; uint8_t RefreshCount; TrackPoint Refresh[4]; float RefreshRadius; uint8_t Slow;"
        " uint32_t Achievement; uint8_t Flags; char const* PickedUp; char const* Warning; char const* Refreshed;"
        " char const* Lost; char const* Delivered; };",
        "    constexpr CarryRule CarryRules[] =",
        "    {",
    ]
    carries = [(quest, obj) for quest in quests_all for obj in quest.objectives if obj.kind == "carry"]
    for quest, obj in carries:
        kw = obj.kw
        dips = list(kw["dips"]) + [(0.0, 0.0)] * (4 - len(kw["dips"]))
        out.append(f"        {{ {quest.id}, {obj.credit}, {kw['thing'].entry}, {kw['map']}, {float(kw['x'])}f, {float(kw['y'])}f,"
                   f" {float(kw['radius'])}f, {kw['seconds']}, {len(kw['dips'])}, {{ "
                   + ", ".join(f"{{ {float(x)}f, {float(y)}f }}" for x, y in dips)
                   + f" }}, {float(kw['dip_radius'])}f, {kw['slow']}, {kw['achievement']},"
                   f" {CARRY_FAIL_LOST if kw['fail_lost'] else 0}, {cstr(kw['picked'])}, {cstr(kw['warning'])},"
                   f" {cstr(kw['refreshed'])}, {cstr(kw['lost'])}, {cstr(kw['delivered'])} }},   // {quest.title}: {obj.text}")
    if not carries:
        out.append('        { 0, 0, 0, 0, 0.0f, 0.0f, 0.0f, 0, 0, { }, 0.0f, 0, 0, 0, "", "", "", "", "" },')
    out += [
        "    };",
        "",
        "    // A letter after a quest: server mail from Wren, Delay seconds later.",
        "    struct MailRule { uint32_t Quest; char const* Subject; char const* Body; uint32_t Delay; };",
        "    constexpr MailRule MailRules[] =",
        "    {",
    ]
    mails = [quest for quest in quests_all if quest.mail]
    for quest in mails:
        subject, body, delay = quest.mail
        out.append(f"        {{ {quest.id}, {cstr(subject)}, {cstr(body)}, {delay} }},   // {quest.title}")
    if not mails:
        out.append('        { 0, "", "", 0 },')
    out += [
        "    };",
        "",
        "    // One of the quests' own creatures that talks (npc_devourer_quest_beast): it says Text, offers Options; the",
        "    // right one gives Credit (while Quest is open; Quest 0: always), a wrong one casts WrongSpell on the Devourer.",
        "    struct GossipOption { char const* Label; char const* Reply; bool Right; };",
        "    struct GossipRule { uint32_t Entry; uint32_t Quest; uint32_t Credit; char const* Text; uint8_t OptionCount;"
        " GossipOption Options[4]; uint32_t WrongSpell; };",
        "    constexpr GossipRule GossipRules[] =",
        "    {",
    ]
    talkers = [beast for book in books for beast in book.beasts if beast.gossip]
    for beast in talkers:
        text, options, wrong = beast.gossip
        assert 1 <= len(options) <= 4, beast.name
        opts = list(options) + [("", "", False)] * (4 - len(options))
        out.append(f"        {{ {beast.entry}, {getattr(beast, 'gossip_quest', 0)}, {getattr(beast, 'gossip_credit', 0)},"
                   f" {cstr(text)}, {len(options)}, {{ "
                   + ", ".join(f"{{ {cstr(label)}, {cstr(reply)}, {'true' if right else 'false'} }}" for label, reply, right in opts)
                   + f" }}, {wrong} }},   // {beast.name}")
    if not talkers:
        out.append('        { 0, 0, 0, "", 0, { }, 0 },')
    out += ["    };", "}", "", "#endif", ""]
    text = "\n".join(out).replace("@@TALE_LINES@@", "\n".join(lines_decl))
    with open(HDR_OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def write_sql(book):
    quests = sorted(book.quests, key=lambda x: x.id)
    B = book.block
    o = []
    o += [
        f"-- mod-devourer task {B.task}: the Devourer's quests in the world ({B.name}). src/DevourerQuests.cpp.",
        "-- Generated by tools/devourer_quests.py -- change the tool and run it again. Safe to run again.",
        f"-- Ids {B.q_first}-{B.credit_last} (quests, credits, givers, objects), gameobject guids {B.guid_first}-{B.guid_last},"
        f" creature guids {B.npc_guid_first}-{B.npc_guid_last}.",
        "",
        f"DELETE FROM `gameobject` WHERE `guid` BETWEEN {B.guid_first} AND {B.guid_last};",
        f"DELETE FROM `creature` WHERE `guid` BETWEEN {B.npc_guid_first} AND {B.npc_guid_last};",
        f"DELETE FROM `gameobject_queststarter` WHERE `quest` BETWEEN {B.q_first} AND {B.q_last};",
        f"DELETE FROM `gameobject_questender` WHERE `quest` BETWEEN {B.q_first} AND {B.q_last};",
        f"DELETE FROM `creature_queststarter` WHERE `quest` BETWEEN {B.q_first} AND {B.q_last};",
        f"DELETE FROM `creature_questender` WHERE `quest` BETWEEN {B.q_first} AND {B.q_last};",
        f"DELETE FROM `gameobject_template` WHERE `entry` BETWEEN {B.giver_first} AND {B.thing_last};",
        f"DELETE FROM `creature_template_model` WHERE `CreatureID` BETWEEN {B.credit_first} AND {B.credit_last};",
        f"DELETE FROM `creature_template` WHERE `entry` BETWEEN {B.credit_first} AND {B.credit_last};",
        f"DELETE FROM `conditions` WHERE `SourceTypeOrReferenceId` IN (19, 20) AND `SourceEntry` BETWEEN {B.q_first} AND {B.q_last};",
        f"DELETE FROM `quest_offer_reward` WHERE `ID` BETWEEN {B.q_first} AND {B.q_last};",
        f"DELETE FROM `quest_request_items` WHERE `ID` BETWEEN {B.q_first} AND {B.q_last};",
        f"DELETE FROM `quest_template_addon` WHERE `ID` BETWEEN {B.q_first} AND {B.q_last};",
        f"DELETE FROM `quest_template` WHERE `ID` BETWEEN {B.q_first} AND {B.q_last};",
        "",
        "-- --- Hagatha's lanterns (questgivers, one per region) and the witches' objects (goobers, one quest each) ---",
        "INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `IconName`, `castBarCaption`, `unk1`,"
        " `size`, `Data0`, `Data1`, `AIName`, `ScriptName`, `VerifiedBuild`) VALUES",
    ]
    rows = []
    for lantern in book.lanterns:
        rows.append(f"({lantern.entry}, 2, {lantern.display}, {q(lantern.name)}, '', '', '',"
                    f" {lantern.size}, 0, 0, '', '', 0)")
    for thing in book.things:
        assert thing.quest, thing.key
        if thing.lines:                          # a tale is told at any fire (mod-chromatica-extras), not at an object
            continue
        rows.append(f"({thing.entry}, 10, {thing.display}, {q(thing.name)}, '', '', '', {thing.size}, 0,"
                    f" {0 if thing.shared else thing.quest}, '', 'go_devourer_quest_object', 0)")
    o.append(",\n".join(rows) + ";")
    o += ["", "INSERT INTO `gameobject` (`guid`, `id`, `map`, `spawnMask`, `phaseMask`, `position_x`, `position_y`,"
              " `position_z`, `orientation`, `rotation0`, `rotation1`, `rotation2`, `rotation3`, `spawntimesecs`,"
              " `animprogress`, `state`, `Comment`) VALUES"]
    rows, guid = [], B.guid_first
    import math
    for lantern in book.lanterns:
        rows.append(f"({guid}, {lantern.entry}, {lantern.map}, 1, 1, {lantern.x}, {lantern.y}, {lantern.z},"
                    f" {lantern.o}, 0, 0, {round(math.sin(lantern.o / 2), 6)}, {round(math.cos(lantern.o / 2), 6)},"
                    f" 300, 255, 1, {q('mod-devourer: ' + lantern.name + ', ' + lantern.where)})")
        guid += 1
    for thing in book.things:
        if thing.lines:
            continue
        for (map_id, x, y, z, ori) in thing.spawns:
            z = ground_z(map_id, x, y, z)
            rows.append(f"({guid}, {thing.entry}, {map_id}, 1, 1, {x}, {y}, {z}, {ori}, 0, 0,"
                        f" {round(math.sin(ori / 2), 6)}, {round(math.cos(ori / 2), 6)}, 60, 255, 1,"
                        f" {q('mod-devourer: ' + thing.name)})")
            guid += 1
    assert guid <= B.guid_last + 1
    o.append(",\n".join(rows) + ";")

    if B.speaker:
      o += ["", "-- --- the lantern's voice: an invisible creature at every lantern, for the LLM companions to speak through ---",
          f"DELETE FROM `creature` WHERE `guid` BETWEEN {B.speaker_guid_first} AND {B.speaker_guid_last};",
          f"DELETE FROM `creature_template_model` WHERE `CreatureID` = {B.speaker};",
          f"DELETE FROM `creature_template` WHERE `entry` = {B.speaker};",
          "DROP TEMPORARY TABLE IF EXISTS `devourer_tmp_ct`;",
          f"CREATE TEMPORARY TABLE `devourer_tmp_ct` SELECT * FROM `creature_template` WHERE `entry` = {TRIGGER_TEMPLATE};",
          f"UPDATE `devourer_tmp_ct` SET `entry` = {B.speaker}, `name` = {q('Hagatha' + chr(39) + 's Lantern')},"
          " `subname` = NULL, `faction` = 35, `npcflag` = 0, `unit_flags` = 33554434, `flags_extra` = 0, `AIName` = '',"
          " `ScriptName` = '', `VerifiedBuild` = 0;",
          "INSERT INTO `creature_template` SELECT * FROM `devourer_tmp_ct`;",
          "DROP TEMPORARY TABLE `devourer_tmp_ct`;",
          "INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`,"
          f" `VerifiedBuild`) VALUES ({B.speaker}, 0, {INVISIBLE_MODEL}, 1, 1, 0);",
          "INSERT INTO `creature` (`guid`, `id`, `map`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`,"
          " `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`, `Comment`) VALUES"]
      speakers = []
      for i, lantern in enumerate(book.lanterns):
        guid = B.speaker_guid_first + i
        assert guid <= B.speaker_guid_last
        speakers.append(f"({guid}, {B.speaker}, {lantern.map}, 1, 1, {lantern.x}, {lantern.y}, {round(lantern.z + 1.0, 2)},"
                        f" {lantern.o}, 300, 0, 0, {q('mod-devourer: the voice of Hagatha' + chr(39) + 's Lantern, ' + lantern.where)})")
      o.append(",\n".join(speakers) + ";")

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

    if book.beasts:
        o += ["", "-- --- the quests' own creatures (copies of stock ones, with their own names) ----------------------------",
              f"DELETE FROM `creature_template_model` WHERE `CreatureID` BETWEEN {B.beast_first} AND {B.beast_last};",
              f"DELETE FROM `creature_template` WHERE `entry` BETWEEN {B.beast_first} AND {B.beast_last};",
              f"DELETE FROM `creature_text` WHERE `CreatureID` BETWEEN {B.beast_first} AND {B.beast_last};"]
        for beast in book.beasts:
            o.append("DROP TEMPORARY TABLE IF EXISTS `devourer_tmp_ct`;")
            o.append(f"CREATE TEMPORARY TABLE `devourer_tmp_ct` SELECT * FROM `creature_template` WHERE `entry` = {beast.clone_of};")
            sets = [f"`entry` = {beast.entry}", f"`name` = {q(beast.name)}", f"`subname` = {q(beast.subname)}",
                    "`KillCredit1` = 0", "`KillCredit2` = 0", "`lootid` = 0", "`pickpocketloot` = 0", "`skinloot` = 0",
                    "`AIName` = ''", "`ScriptName` = ''", "`VerifiedBuild` = 0"]
            if beast.level:
                sets += [f"`minlevel` = {beast.level}", f"`maxlevel` = {beast.level}"]
            if beast.faction:
                sets.append(f"`faction` = {beast.faction}")
            if beast.npcflag or beast.gossip:
                sets.append(f"`npcflag` = {beast.npcflag | (1 if beast.gossip else 0)}")
            if beast.gossip:
                sets.append("`ScriptName` = 'npc_devourer_quest_beast'")
            o.append("UPDATE `devourer_tmp_ct` SET " + ", ".join(sets) + ";")
            o.append("INSERT INTO `creature_template` SELECT * FROM `devourer_tmp_ct`;")
            o.append("DROP TEMPORARY TABLE `devourer_tmp_ct`;")
            if beast.display:
                o.append("INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`,"
                         f" `Probability`, `VerifiedBuild`) VALUES ({beast.entry}, 0, {beast.display}, {beast.scale}, 1, 0);")
            else:
                o.append("INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`,"
                         " `Probability`, `VerifiedBuild`) SELECT " + str(beast.entry) + ", 0, `CreatureDisplayID`,"
                         f" `DisplayScale` * {beast.scale}, 1, 0 FROM `creature_template_model` WHERE `CreatureID` = "
                         f"{beast.clone_of} AND `Idx` = 0;")
            if beast.sound:
                o.append("INSERT INTO `creature_text` (`CreatureID`, `GroupID`, `ID`, `Text`, `Type`, `Language`,"
                         f" `Probability`, `Emote`, `Duration`, `Sound`, `BroadcastTextId`, `TextRange`, `comment`) VALUES"
                         f" ({beast.entry}, 0, 0, '', 16, 0, 100, 0, 0, {beast.sound}, 0, 0, {q('mod-devourer: ' + beast.name)});")
        spawned = [(beast, sp) for beast in book.beasts for sp in beast.spawns]
        if spawned:
            o.append("INSERT INTO `creature` (`guid`, `id`, `map`, `spawnMask`, `phaseMask`, `position_x`, `position_y`,"
                     " `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`, `Comment`) VALUES")
            rows, guid = [], B.npc_guid_first
            for beast, (map_id, x, y, z, ori) in spawned:
                z = ground_z(map_id, x, y, z)
                rows.append(f"({guid}, {beast.entry}, {map_id}, 1, 1, {x}, {y}, {z}, {ori}, 120, 0, 0,"
                            f" {q('mod-devourer: ' + beast.name)})")
                guid += 1
            assert guid <= B.npc_guid_last + 1
            o.append(",\n".join(rows) + ";")
    o += ["", "-- --- the quests -------------------------------------------------------------------------------------"]
    cols = ("`ID`, `QuestType`, `QuestLevel`, `MinLevel`, `QuestSortID`, `QuestInfoID`, `RewardXPDifficulty`,"
            " `RewardMoney`, `Flags`, `AllowableRaces`, `LogTitle`, `LogDescription`, `QuestDescription`,"
            " `AreaDescription`, `QuestCompletionLog`, "
            + ", ".join(f"`RequiredNpcOrGo{i}`, `RequiredNpcOrGoCount{i}`" for i in range(1, 5)) + ", "
            + ", ".join(f"`RequiredItemId{i}`, `RequiredItemCount{i}`" for i in range(1, 5)) + ", "
            + ", ".join(f"`RewardItem{i}`, `RewardAmount{i}`" for i in range(1, 5)) + ", "
            + ", ".join(f"`RewardChoiceItemID{i}`, `RewardChoiceItemQuantity{i}`" for i in range(1, 7)) + ", "
            + ", ".join(f"`ObjectiveText{i}`" for i in range(1, 5)) + ", `TimeAllowed`, `VerifiedBuild`")
    o.append(f"INSERT INTO `quest_template` ({cols}) VALUES")
    rows = []
    for quest in quests:
        npcs = [o2 for o2 in quest.objectives if o2.kind not in ("item", "spare")]
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
                  + [q(t) for t in texts] + [quest.timed, 0])
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
        if quest.event:
            conds.append(f"(19, 0, {quest.id}, 0, 0, 12, 0, {quest.event}, 0, 0, 0, 0, 0, '',"
                         f" {q('mod-devourer: ' + quest.title + ' only during game event ' + str(quest.event))})")
    if conds:
        o += ["", "-- Quests for one shape (or its line): offered only to a Devourer that owns it (knows its form spell).",
              "INSERT INTO `conditions` (`SourceTypeOrReferenceId`, `SourceGroup`, `SourceEntry`, `SourceId`,"
              " `ElseGroup`, `ConditionTypeOrReference`, `ConditionTarget`, `ConditionValue1`, `ConditionValue2`,"
              " `ConditionValue3`, `NegativeCondition`, `ErrorType`, `ErrorTextId`, `ScriptName`, `Comment`) VALUES",
              ",\n".join(conds) + ";"]
    o.append("")
    with open(B.sql_out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(o))


def money_text(copper):
    g, s, c = copper // 10000, copper // 100 % 100, copper % 100
    parts = ([f"{g}g"] if g else []) + ([f"{s}s"] if s else []) + ([f"{c}c"] if c and not g else [])
    return " ".join(parts) or "0"


def write_doc(book):
    out = [f"# The Devourer's quests (task {book.block.task}: {book.block.name})", "",
           "Generated by `tools/devourer_quests.py` -- edit the tool, not this file. Every quest is for the Devourer only",
           "(class 10). Rewards are items (pick one where there is a choice), money and experience.", ""]
    total = 0
    for title, intro, quests in book.regions:
        out += [f"## {title}", "", intro, "",
                "| Lvl | Quest | Story | Objectives | Rewards |", "|---|---|---|---|---|"]
        for quest in quests:
            total += 1
            objs = "; ".join(f"{o2.text} x{o2.count}" if o2.count > 1 else o2.text for o2 in quest.objectives
                             if o2.kind != "spare") or "-"
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
    with open(book.block.doc_out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out))


def main():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import devourer_quests_content
    import mount_quests
    books = []
    for block, module in ((LANTERNS, devourer_quests_content), (MOUNTS, mount_quests)):
        book = Book(block)
        module.build(book)
        check(book)
        assign_credits(book)
        write_sql(book)
        write_doc(book)
        books.append(book)
        print(f"{block.name}: {len(book.quests)} quests, {len(book.lanterns)} givers, {len(book.things)} objects,"
              f" {len(book.beasts)} creatures -> {os.path.relpath(block.sql_out, ROOT)}, {os.path.relpath(block.doc_out, ROOT)}")
    write_header(books)
    print("->", os.path.relpath(HDR_OUT, ROOT))


if __name__ == "__main__":
    main()
