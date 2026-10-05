"""Task 021: the content of the Devourer's quests (tools/devourer_quests.py writes the SQL, header and doc from it).

Every creature, place and reward here was checked against the live world database and the server's map files
(2026-10-05): the creatures are spawned in that region at about the quest's level, the lanterns, objects and trail
points stand on dry ground, and the rewards are stock 3.3.5a items a Devourer can use.

Second pass (2026-10-05, owner: "keep things unique and fun"): at most one plain "devour some of X" quest per lantern;
every lantern has quests only a Devourer could do: follow a scent trail with Sniff, walk among a pack in its own shape,
let a beast show its trick before eating it, spare one special creature, eat against Wren's clock, frighten things
off, hear one of the sisters' tales with Bramble by a campfire. Mounts are not rewards here (the mounts thread owns
where every mount comes from); the spared creatures give a stock companion pet instead.

Voices: Hagatha Hollowmoor tells tales ("little horror"); Wren Hollowmoor makes lists ("Snack").
"""

from devourer_quests import (HAGATHA, WREN, HUMAN, ORC, DWARF, NIGHTELF, UNDEAD, TAUREN, GNOME, TROLL, BLOODELF,
                             DRAENEI, LINES, devour, visit, emote, trail, struck, spare, among, EMOTE_PET, EMOTE_ROAR)

# Creature families and types (creature_template.family / type)
F_WOLF, F_CAT, F_SPIDER, F_BEAR, F_BOAR, F_CROC, F_CARRION, F_CRAB, F_RAPTOR, F_TALLSTRIDER = 1, 2, 3, 4, 5, 6, 7, 8, 11, 12
F_SCORPID, F_TURTLE, F_BAT, F_HYENA, F_BIRD, F_WINDSERPENT, F_DRAGONHAWK, F_RAVAGER, F_WARPSTALKER = (
    20, 21, 24, 25, 26, 27, 30, 31, 32)
F_SPOREBAT, F_NETHERRAY, F_SERPENT, F_MOTH, F_CHIMAERA, F_DEVILSAUR, F_SILITHID, F_WORM, F_RHINO, F_WASP = (
    33, 34, 35, 37, 38, 39, 41, 42, 43, 44)
T_BEAST, T_DRAGON, T_DEMON, T_ELEMENTAL, T_GIANT, T_UNDEAD, T_HUMANOID = 1, 2, 3, 4, 5, 6, 7
FACTION_SHY = 31                              # "prey": never attacks, can be attacked (the creatures to spare)

# Zones (AreaTable ids), for the quest log headers
Z_ELWYNN, Z_DUNMOROGH, Z_TELDRASSIL, Z_AZUREMYST, Z_DUROTAR, Z_MULGORE, Z_TIRISFAL, Z_EVERSONG = (
    12, 1, 141, 3524, 14, 215, 85, 3430)
Z_WESTFALL, Z_LOCHMODAN, Z_DARKSHORE, Z_BLOODMYST, Z_BARRENS, Z_SILVERPINE, Z_GHOSTLANDS = (
    40, 38, 148, 3525, 17, 130, 3433)
DERBY_WREN = 9101360                          # Wren at the Derby's starting line (task 020)

LANTERN_OPEN = "The lantern's flame leans toward you, and "
CRYSTAL = 2971                                # the look of a blue power crystal


def breadcrumb(book, qid, title, level, giver, ender, races, text, reward_text, story, prev=None, sort=0):
    return book.quest(qid, title, level, level, giver, ender, "hagatha", text,
                      f"Find Hagatha's Lantern in {ender.region}: {ender.where}.",
                      "The lantern is not lit yet? Then you are not there yet, little horror.",
                      reward_text, prev=prev, races=races, xp=2, sort=sort, story=story)


def mercy(book, qid, title, level, lantern, beast, points, intro, found, kept, reward, sort, story, prev=None):
    """One special creature of the region, found by its scent: spare it (/pet it) instead of eating it. It follows
    the Devourer for a while, then goes home; killing it fails the quest. A stock companion pet is the reward."""
    return book.quest(
        qid, title, level, max(1, level - 1), lantern, lantern, "wren", intro,
        f"Follow the scent of {beast.name} with Sniff, find it, and /pet it. Do not eat it.",
        found, kept,
        objectives=[trail(f"{beast.name} found", beast.name, lantern.map, points, summon=beast.entry, radius=18.0),
                    emote(1, f"{beast.name} spared", EMOTE_PET, entries=[beast.entry], follow=True),
                    spare(f"{beast.name} eaten", entries=[beast.entry])],
        prev=prev, sort=sort, items=[reward], xp=4, story=story)


def build(book):
    import devourer_quests_teens
    import devourer_quests_twenties
    import devourer_quests_thirties
    import devourer_quests_high
    finales = home(book)
    teens = devourer_quests_teens.teens(book, finales)
    twenties = devourer_quests_twenties.twenties(book, teens)
    thirties = devourer_quests_thirties.thirties(book, twenties)
    devourer_quests_high.high(book, thirties)


# --- Homecoming: a lantern in every home region (levels 6-11) --------------------------------------------------------

def home(book):
    elwynn = book.lantern("elwynn", "Elwynn Forest", 0, -9620.0, -560.0, 54.44, 2.4, "south-east of Crystal Lake")
    dunmorogh = book.lantern("dunmorogh", "Dun Morogh", 0, -5620.0, -1100.0, 392.25, 1.2, "the hills east of Kharanos")
    teldrassil = book.lantern("teldrassil", "Teldrassil", 1, 9810.0, 840.0, 1304.01, 3.9, "the woods south-east of Dolanaar")
    azuremyst = book.lantern("azuremyst", "Azuremyst Isle", 530, -4050.0, -12000.0, 1.55, 5.1, "Moongraze Woods")
    durotar = book.lantern("durotar", "Durotar", 1, 300.0, -4500.0, 28.58, 0.7, "the scrub west of Razor Hill")
    mulgore = book.lantern("mulgore", "Mulgore", 1, -2100.0, -900.0, -1.06, 2.0, "the plains north-east of Bloodhoof")
    tirisfal = book.lantern("tirisfal", "Tirisfal Glades", 0, 2500.0, 600.0, 30.68, 4.4, "the glades north-west of Brill")
    eversong = book.lantern("eversong", "Eversong Woods", 530, 8900.0, -6600.0, 33.61, 1.6, "the woods west of the Dead Scar")

    book.region("Homecoming: the lanterns of the home regions (levels 6-11)",
                "After Wren's Apprentice, Hagatha sends the Devourer home: her lantern burns in the region it came "
                "from. Each home lantern has one plain lesson, one thing only a Devourer could do there, a named "
                "beast to finish, and one special creature to find with Sniff and spare.")

    homes = (
        (9105001, HUMAN, elwynn), (9105002, DWARF | GNOME, dunmorogh), (9105003, NIGHTELF, teldrassil),
        (9105004, DRAENEI, azuremyst), (9105005, ORC | TROLL, durotar), (9105006, TAUREN, mulgore),
        (9105007, UNDEAD, tirisfal), (9105008, BLOODELF, eversong),
    )
    for qid, races, lantern in homes:
        breadcrumb(
            book, qid, "A Lantern at Home", 6, HAGATHA, lantern, races,
            "You were not born, little horror, you were found. But even a found thing has a place it was found in, "
            f"and the world remembers you there. I have hung one of my lanterns in {lantern.region}: "
            f"{lantern.where}. Go back the way Wren brought you and look for its light.$B$BWhen you stand beside it, "
            "my sister and I will hear you, wherever we are.",
            "There you are. The flame knew you before I did.$B$BSit, hungry thing. Your home is full of meals, and "
            "every meal is a lesson. Some are not meals at all; I will tell you which.",
            f"Hagatha sends the Devourer home, to her lantern in {lantern.region}.", prev=9101305)

    return {
        "elwynn": (elwynn, elwynn_quests(book, elwynn)),
        "dunmorogh": (dunmorogh, dunmorogh_quests(book, dunmorogh)),
        "teldrassil": (teldrassil, teldrassil_quests(book, teldrassil)),
        "azuremyst": (azuremyst, azuremyst_quests(book, azuremyst)),
        "durotar": (durotar, durotar_quests(book, durotar)),
        "mulgore": (mulgore, mulgore_quests(book, mulgore)),
        "tirisfal": (tirisfal, tirisfal_quests(book, tirisfal)),
        "eversong": (eversong, eversong_quests(book, eversong)),
    }


def elwynn_quests(book, lantern):
    s = Z_ELWYNN
    greymuzzle = book.beast("greymuzzle", "Grey-Muzzle", 1922, level=8, faction=FACTION_SHY, passive=True,
                            subname="Too Old to Hunt")
    a = book.quest(
        9105010, "The Wolves of Elwynn", 6, 6, lantern, lantern, "hagatha",
        "Hagatha's voice comes out of the lantern, dry as old paper:$B$BThe wolf was the first shape you ever wore, "
        "little horror, before Wren ever found you, and you wore it badly. A wolf is not teeth. A wolf is the pack it "
        "runs with. The forests of Elwynn are full of them, mangy and grey and hungry.$B$BEat six of them. Not to kill "
        "them, to know them. Then come back and tell me what they tasted of.",
        "Devour 6 wolves in Elwynn Forest.",
        "Six wolves, I said. I can count your meals, little horror. I can smell them on you.",
        "Fear, mostly. And rabbit. That is the taste of a wolf that runs alone.$B$BTake something for your trouble. "
        "Old things I have kept; they will fit a shape like yours better than they fit me.",
        objectives=[devour(6, "Elwynn wolf devoured", family=F_WOLF)], sort=s,
        choices=[(3511, "Cloak of the People's Militia"), (23404, "Padded Running Shoes"), (2218, "Craftsman's Dagger")],
        story="The lesson: Hagatha has the Devourer eat six of Elwynn's wolves, to know the wolf it wears.")
    b = book.quest(
        9105011, "Wren's Eating Contest", 8, 7, lantern, lantern, "wren",
        "The lantern rattles, and Wren's voice bursts out of it:$B$BSnack! CONTEST. I've always wanted to run one. "
        "Rules: there's a lake just north-west of the lantern, full of murlocs. When you say yes, I start my "
        "egg-timer. You eat six murlocs before the sand runs out. I've never timed anything before, so the "
        "egg-timer might be a spoon. It's a spoon.$B$BReady? Say yes and GO!",
        "Devour 6 murlocs at Crystal Lake before Wren's spoon runs out (5 minutes).",
        "Out of time? We'll go again! I'll hold the spoon better.",
        "SIX! Before the spoon! You're the champion of the lake. The champion of Elwynn. Of everywhere I've "
        "timed, which is here.$B$BHere's your prize. I made a ribbon, but Hagatha made me give you this instead.",
        objectives=[devour(6, "Crystal Lake murloc devoured", entries=[285, 735])], prev=a.id, sort=s, timed=300,
        choices=[(6085, "Footman Tunic"), (5617, "Vagabond Leggings"), (3440, "Bonecracker")],
        story="Wren's first eating contest: six Crystal Lake murlocs against her spoon-timer (5 minutes).")
    c = book.quest(
        9105012, "Hogger's Last Supper", 10, 9, lantern, lantern, "hagatha",
        "The flame sinks low, and Hagatha tells it slow:$B$BThe Riverpaw gnolls tell of one of their own who ate so "
        "much that the pack could not feed him any more, so they left him at the edge of the forest, and he ate the "
        "edge of the forest instead. They call him Hogger.$B$BBefore you eat a famous thing, little horror, let it "
        "show you why it is famous. Go to Forest's Edge in the south-west. Let Hogger use his tricks on you, his "
        "charge and his butting skull. Then eat him, and the tricks will taste of something.",
        "At Forest's Edge in Elwynn Forest, let Hogger use one of his tricks on you, then devour him.",
        "Hogger is still the hungriest thing in Elwynn. That should bother you more than it does.",
        "Now you are the hungriest thing in Elwynn. Do not let it go to your head; it is a very small forest.$B$B"
        "Remember how his charge felt, and the taste after. That is how a Devourer learns: first the blow, then the "
        "meal.",
        objectives=[struck(1, "Hogger's trick felt", entries=[448]), devour(1, "Hogger devoured", entries=[448])],
        prev=b.id, sort=s, xp=6,
        choices=[(1436, "Frontier Britches"), (1302, "Black Whelp Gloves"), (3581, "Serrated Knife")],
        story="Hagatha's tale of Hogger, who ate the edge of the forest. Let him show his tricks, then eat him.")
    mercy(book, 9105013, "Grey-Muzzle", 8, lantern, greymuzzle,
          [(-9643, -722), (-9556, -823), (-9536, -940), (-9530, -1060)],
          "Wren, quiet for once:$B$BSnack, there's an old wolf in the hills east of here. Too old to keep up with "
          "the pack, so they left him. Hagatha says he smells of wet leaves and rabbit and being alone. Turn on your "
          "Sniff by the lantern and follow his smell.$B$BAnd Snack? Don't eat this one. Just... pat him. Somebody "
          "should.",
          "Did you find him? Follow your nose, Snack. Wet leaves and rabbit.",
          "You patted him. He followed you a bit, didn't he? Then he went home. Good.$B$BHagatha found a pup in a "
          "basket by the cauldron this morning and says it's yours, since you're so good with old wolves. I didn't "
          "ask where it came from. Neither should you.",
          (12264, "Worg Carrier", 1), s,
          "Mercy: Sniff out Grey-Muzzle, an old wolf the pack left behind, and pat him instead of eating him. Reward: a "
          "worg pup companion.", prev=a.id)
    return c


def dunmorogh_quests(book, lantern):
    s = Z_DUNMOROGH
    frostwhisker = book.beast("frostwhisker", "Frostwhisker", 1199, level=6, faction=FACTION_SHY, passive=True,
                              scale=0.7, subname="Lost in the Snow")
    a = book.quest(
        9105020, "Stone in the Belly", 7, 6, lantern, lantern, "hagatha",
        "Hagatha's voice, slow and low as falling snow:$B$BThe trogg is a strange thing to wear, little horror. It came "
        "out of the stone and never forgot it; its skin is half rock, its hunger is all of it. The Rockjaw troggs dig "
        "in Gol'Bolar Quarry, south-east of here, and around the lake beyond.$B$BEat six of them. You will feel the "
        "stone settle in your belly. That weight is the beginning of the trogg's strength.",
        "Devour 6 Rockjaw troggs in Dun Morogh.",
        "Your belly is still light, little horror. Six troggs.",
        "Heavy, is it? Good. A thing that carries stone inside it does not fall over easily.$B$BTake one of these. "
        "Something to wear over the weight.",
        objectives=[devour(6, "Rockjaw trogg devoured", entries=[1115, 1116, 1117])], sort=s,
        choices=[(5617, "Vagabond Leggings"), (26051, "2 Stone Sledgehammer"), (4974, "Compact Fighting Knife")],
        story="The lesson: six Rockjaw troggs, for the stone in a trogg's belly.")
    book.quest(
        9105021, "One of the Rockjaw", 8, 7, lantern, lantern, "hagatha",
        "Hagatha, almost amused:$B$BYou wear the trogg's shape, little horror. Then you can do what no dwarf has ever "
        "done: walk into the middle of Gol'Bolar Quarry and be welcome. Wear your trogg. Walk in slowly. The Rockjaw "
        "will sniff you and grunt and let you pass, because you smell of stone.$B$BDo not start a fight. A trogg "
        "that bites its own kin is not one of them any more.",
        "Wearing your Trogg (or what it grew into), walk to the middle of Gol'Bolar Quarry without starting a fight.",
        "They will let you in, little horror. If you let them.",
        "You stood among them and they did not know you. Remember how that felt: being one of many, and none of "
        "them knowing what you are.$B$BTake this.",
        objectives=[among("Walked among the Rockjaw", 0, -5816.0, -1525.0, [1115, 1116, 1117, 1118],
                          LINES["trogg"])],
        prev=a.id, sort=s, needs=LINES["trogg"],
        choices=[(2036, "Dusty Mining Gloves"), (23404, "Padded Running Shoes"), (2218, "Craftsman's Dagger")],
        story="For a Devourer with the Trogg shape: walk into the Rockjaw quarry as one of them, and start no fight.")
    b = book.quest(
        9105022, "The White Wolf of Iceflow", 10, 9, lantern, lantern, "hagatha",
        "The flame goes white, and Hagatha tells it:$B$BThe dwarves of Kharanos speak of a wolf as white as the lake "
        "it hunts by. Timber, they call him, as if naming him would make him smaller. He comes and goes, and no dwarf "
        "has caught him in years.$B$BYou have a better nose than any dwarf. Turn on your Sniff here, by the lantern, "
        "and follow his scent west, through the village and north over the ridge to Iceflow Lake. At the end of the trail "
        "he will be waiting. He always is, for the ones who can follow.",
        "Follow Timber's scent with Sniff from the lantern to Iceflow Lake, then devour him.",
        "The white wolf's trail is still out there. Sniff it out, little horror.",
        "The white wolf, inside you. The dwarves will tell their children Timber finally lost a hunt.$B$BTake this.",
        objectives=[trail("Timber's trail followed", "Timber", 0,
                          [(-5447, -753), (-5499, -512), (-5429, -303), (-5294, -112), (-5274, 110)], summon=1132),
                    devour(1, "Timber devoured", entries=[1132])],
        prev=a.id, sort=s,
        choices=[(1436, "Frontier Britches"), (28159, "Undertaker's Gloves"), (3570, "Bonegrinding Pestle")],
        story="Follow the white wolf Timber's scent with Sniff from the lantern to Iceflow Lake, and eat him.")
    c = book.quest(
        9105023, "The Backbreaker", 11, 10, lantern, lantern, "hagatha",
        "Hagatha tells it, and the flame grinds like stone:$B$BThe dwarves tell of a trogg that gnawed on a stone "
        "giant's toe. It never stopped growing harder. Neither did its hunger. Its children still dig at Helm's Bed "
        "Lake: the biggest of the Rockjaw, the ones the dwarves call Backbreakers.$B$BEat one. One is enough to show "
        "you what your troggs could become.",
        "Devour a Rockjaw Backbreaker at Helm's Bed Lake in Dun Morogh.",
        "The Backbreakers still dig, little horror. One of them, I said.",
        "Now you have tasted what a trogg grows into. Remember it: one day your own stone will crack open and "
        "something like that will crawl out.$B$BWear this until then.",
        objectives=[devour(1, "Rockjaw Backbreaker devoured", entries=[1118])], prev=b.id, sort=s, xp=6,
        choices=[(2036, "Dusty Mining Gloves"), (5327, "Greasy Tinker's Pants"), (1302, "Black Whelp Gloves")],
        story="Hagatha's tale of the trogg that gnawed a giant's toe; the Devourer eats a Rockjaw Backbreaker.")
    mercy(book, 9105024, "Frostwhisker", 7, lantern, frostwhisker,
          [(-5650, -893), (-5783, -777), (-5800, -620)],
          "Wren, hushed:$B$BSnack, a snow leopard kit got lost in the Tundrid Hills, west of the lantern. I can hear it "
          "crying from HERE. It's very small and very cold and it smells of snow and milk. Sniff it out.$B$BDon't eat "
          "it. I mean it. Pat it, and it'll find its mother.",
          "Is it still crying, Snack? Snow and milk. Follow it.",
          "It found its mother! I heard the purring all the way in the In-Between.$B$BHagatha says a kindness should "
          "be paid in kind, so here: a kitten of your very own. A white one, for the snow.",
          (8489, "Cat Carrier (White Kitten)", 1), s,
          "Mercy: Sniff out a lost snow leopard kit in the Tundrid Hills and pat it home. Reward: a white kitten "
          "companion.", prev=a.id)
    return c


def teldrassil_quests(book, lantern):
    s = Z_TELDRASSIL
    moonpaw = book.beast("moonpaw", "Moonpaw", 2042, level=6, faction=FACTION_SHY, passive=True, scale=0.6,
                         subname="Nightsaber Cub")
    a = book.quest(
        9105030, "Moonlit Teeth", 6, 6, lantern, lantern, "hagatha",
        "Hagatha's voice is soft as moss:$B$BThe nightsaber hunts by moonlight and is never seen until it wants to be. "
        "The elves love them. That is the trouble with being loved, little horror: you stop being careful.$B$BEat six "
        "of the great cats of Teldrassil. Learn how quiet a hunter can be.",
        "Devour 6 nightsabers in Teldrassil.",
        "Six cats. They are quiet, but they are not hidden from you.",
        "Quiet, were they? You were quieter. That is the lesson.$B$BThese were left in my lantern by someone who did "
        "not need them any more.",
        objectives=[devour(6, "Nightsaber devoured", entries=[2042, 2043, 2033])], sort=s,
        choices=[(23405, "Farstrider's Tunic"), (26020, "Shard-Covered Leggings"), (4974, "Compact Fighting Knife")],
        story="The lesson: six of Teldrassil's nightsabers, to learn how quiet a hunter can be.")
    book.quest(
        9105031, "Among the Stalkers", 8, 7, lantern, lantern, "hagatha",
        "Hagatha, pleased:$B$BYou wear the saber's shape, little horror. Then go and lie down among the nightsaber "
        "stalkers by Lake Al'Ameth, south of here, as if you were one of them. Wear your saber. Walk soft. They "
        "will sniff you and decide you belong.$B$BDo not hunt them. Not this time. This time you are learning what it "
        "is to be a cat among cats.",
        "Wearing your Saber (or what it grew into), walk among the nightsaber stalkers by Lake Al'Ameth without "
        "starting a fight.",
        "They are waiting for one more cat, little horror.",
        "Did they purr? I think they purred. A Devourer that can lie down among its meals and not eat them is a "
        "Devourer that will live a long time.$B$BTake this.",
        objectives=[among("Lay down among the stalkers", 1, 9397.0, 859.0, [2043, 2042, 2033], LINES["saber"])],
        prev=a.id, sort=s, needs=LINES["saber"],
        choices=[(6215, "Balanced Fighting Stick"), (23404, "Padded Running Shoes"), (3511, "Cloak of the People's Militia")],
        story="For a Devourer with the Saber shape: lie down among the nightsaber stalkers as one of them.")
    b = book.quest(
        9105032, "What the Owl Swallowed", 8, 7, lantern, lantern, "wren",
        "Wren, excited:$B$BSnack, owls swallow things WHOLE. Mice, beetles, secrets. Hagatha says if you eat a strigid "
        "owl you'll see what it saw last, because that's how owls work and also how you work. Eat one. Then tell me "
        "what you saw!$B$BAnd then go there, because I want to know what's there.",
        "Devour a strigid owl, then go where its last memory shows you.",
        "Well? What did it see? Go and look!",
        "A cave full of little demons? The Fel Rock? Hagatha says the grell in there used to be sprites, before the "
        "fel got them. I'm never sleeping again.$B$BHere, for being brave and for telling me.",
        objectives=[devour(1, "Strigid owl devoured (you see a cave mouth)", entries=[1995, 1996, 1997]),
                    visit("The cave the owl saw", 1, 10110.0, 1170.0, radius=45.0)],
        prev=a.id, sort=s,
        choices=[(5617, "Vagabond Leggings"), (26020, "Shard-Covered Leggings"), (2218, "Craftsman's Dagger")],
        story="Eat an owl and see its last memory: a cave mouth. Go there (the Fel Rock).")
    c = book.quest(
        9105033, "The Queen of Webs", 11, 10, lantern, lantern, "hagatha",
        "Hagatha's tale comes thin and careful, like thread:$B$BIn the Oracle Glade in the north of the island there "
        "is a spider the elves call Lady Sathrah. She eats what the glade's guardians let fall, and they let a great "
        "deal fall. She has grown fat on their kindness and thinks herself a queen.$B$BThere are no queens to a "
        "Devourer, little horror. Only meals with longer names.",
        "Devour Lady Sathrah in the Oracle Glade, Teldrassil.",
        "The queen still sits in her web.",
        "A long name, and in the end only a meal. Remember that when you meet names longer than hers.$B$BTake your "
        "pick. She had no use for them, and neither do I.",
        objectives=[devour(1, "Lady Sathrah devoured", entries=[7319])], prev=b.id, sort=s, xp=6,
        choices=[(1302, "Black Whelp Gloves"), (5327, "Greasy Tinker's Pants"), (3581, "Serrated Knife")],
        story="Hagatha's tale of Lady Sathrah, the spider who thinks herself a queen.")
    mercy(book, 9105034, "Moonpaw", 7, lantern, moonpaw,
          [(9844, 671), (9974, 598), (10020, 470)],
          "Wren, softly:$B$BSnack, there's a nightsaber cub east of the lantern whose mother didn't come back. I think "
          "something ate her. Not you. Probably not you. It smells of moss and milk and moonlight. Sniff it out and pat "
          "it, so it knows not everything with teeth is bad.",
          "Moss and milk and moonlight, Snack. Follow it.",
          "You patted it! It followed you, didn't it? The elves will find it in the morning and think the moon looked "
          "after it. Let them.$B$BHere's a cat for you. A black one, for the night.",
          (8491, "Cat Carrier (Black Tabby)", 1), s,
          "Mercy: Sniff out an orphaned nightsaber cub and pat it instead of eating it. Reward: a black kitten "
          "companion.", prev=a.id)
    return c


def azuremyst_quests(book, lantern):
    s = Z_AZUREMYST
    kit = book.beast("cleankit", "Clean-Furred Kit", 17202, level=6, faction=FACTION_SHY, passive=True, scale=0.6,
                     subname="Untouched by the Crystals")
    a = book.quest(
        9105040, "Long Legs on the Isle", 6, 6, lantern, lantern, "hagatha",
        "Hagatha speaks, and the flame sways like a long neck:$B$BThe timberstriders of this island are cousins of the "
        "plainstriders of Mulgore. They were here before the draenei crashed, picking at the moss. A strider is legs "
        "and a beak and a great deal of running away.$B$BEat six. If their shape is not yours yet, it will be.",
        "Devour 6 timberstriders on Azuremyst Isle.",
        "Six striders, little horror. They run, but not far.",
        "Long legs. You will want them one day, when something bigger than you is hungry.$B$BTake one of these.",
        objectives=[devour(6, "Timberstrider devoured", entries=[17372, 17373, 17374])], sort=s,
        choices=[(26018, "Elekk Handler's Leathers"), (24439, "Savage Leggings"), (4974, "Compact Fighting Knife")],
        story="The lesson: six timberstriders, cousins of the plainstrider.")
    b = book.quest(
        9105041, "Bullies of Bristlelimb", 8, 7, lantern, lantern, "wren",
        "Wren, cross:$B$BSnack, the Bristlelimb furbolgs in the south-west keep the Stillpine furbolgs in CAGES. "
        "That's not nice. You know what's nice? Scaring bullies. Go to Bristlelimb Village, in any shape you like, "
        "the scarier the better, and ROAR at them. Right in their faces. Five of them. Watch them run!$B$BYou don't "
        "even have to eat them. I know. I'm surprised too.",
        "Roar (/roar) at 5 Bristlelimb furbolgs at Bristlelimb Village and send them running.",
        "Still five bullies, Snack. Bigger roar!",
        "They RAN! I heard them from here! Bullies always run.$B$BHagatha says that was childish. Hagatha also "
        "laughed. Here!",
        objectives=[emote(5, "Bristlelimb furbolg sent running", EMOTE_ROAR, entries=[17184, 17183, 17185],
                          flee=True)],
        prev=a.id, sort=s,
        choices=[(26024, "Vindicator's Leather Moccasins"), (26020, "Shard-Covered Leggings"), (24343, "The Thumper")],
        story="Wren hates bullies: roar at the furbolgs of Bristlelimb Village until they run.")
    c = book.quest(
        9105042, "The Moonwing Owlbeasts", 10, 9, lantern, lantern, "hagatha",
        "The flame turns the colour of a bruise, and Hagatha tells it:$B$BWhen the draenei ship fell, its broken "
        "crystals poisoned the island's owlbeasts. The worst of them gather at the Moonwing Den in the south-west, "
        "raving and calling down the moon. Let one of the aberrant ones call the moon down on you, little horror. "
        "Feel what the crystals did to it. Then eat three.$B$BOne day you will meet owlbeasts that the moon touched "
        "instead of the crystals, and you will know the difference.",
        "Let an Aberrant Owlbeast cast its Moonfire on you, then devour 3 owlbeasts on Azuremyst Isle.",
        "Three owlbeasts, and their moon. Their madness keeps them home; go to them.",
        "Sharp, and it stays. That was the crystals' madness, and the moon's. Now you know both.$B$BThese came out "
        "of the wreck. The draenei will not miss them.",
        objectives=[struck(1, "Moonfire felt", entries=[17187]),
                    devour(3, "Owlbeast devoured", entries=[17186, 17187, 17188])],
        prev=b.id, sort=s, xp=6,
        choices=[(26021, "Vindicator's Leather Chaps"), (28159, "Undertaker's Gloves"), (26052, "Vindicator's Smasher")],
        story="Hagatha's tale of the crystal-maddened owlbeasts: feel their Moonfire, then eat three.")
    mercy(book, 9105043, "The Clean-Furred Kit", 7, lantern, kit,
          [(-4180, -11900), (-4257, -11847), (-4320, -11760)],
          "Wren, worried:$B$BSnack, all the nightstalkers on the island are sick from the crystals. All of them except "
          "ONE. A little kit south-west of the lantern, and it smells clean, like rain. If anything eats it, there "
          "won't be any clean ones left.$B$BSniff it out and pat it. Then it'll know where you are if it needs you.",
          "Rain, Snack. It smells of rain. Follow it.",
          "The clean one is safe. The draenei will find it, and maybe it'll help them make the others better.$B$B"
          "Hagatha says you deserve a cat that's clean all the way through. Here's one.",
          (8490, "Cat Carrier (Siamese)", 1), s,
          "Mercy: Sniff out the one nightstalker kit the crystals did not touch, and pat it. Reward: a kitten "
          "companion.", prev=a.id)
    return c


def durotar_quests(book, lantern):
    s = Z_DUROTAR
    hatchling = book.beast("clutchless", "Clutchless", 3122, level=6, faction=FACTION_SHY, passive=True, scale=0.5,
                           subname="Bloodtalon Hatchling")
    a = book.quest(
        9105050, "Tusk and Gristle", 6, 6, lantern, lantern, "hagatha",
        "Hagatha's voice is dry as the dust around the lantern:$B$BThe boar of Durotar eats thorns and stones and "
        "anything the orcs leave behind, and it charges at whatever moves. It is not clever. It does not need to be. "
        "Some hungers are like that.$B$BEat six of the mottled boars. Taste how little a boar needs to think.",
        "Devour 6 mottled boars in Durotar.",
        "Six boars. They come to you if you stand still long enough.",
        "Tough, and not much else. Do not underestimate 'not much else', little horror.$B$BHere.",
        objectives=[devour(6, "Mottled boar devoured", entries=[3099, 3100])], sort=s,
        choices=[(24439, "Savage Leggings"), (26051, "2 Stone Sledgehammer"), (4947, "Jagged Dagger")],
        story="The lesson: six mottled boars, and how little a boar needs to think.")
    b = book.quest(
        9105051, "The Scorpid Feast", 8, 7, lantern, lantern, "wren",
        "Wren, with a whistle:$B$BSnack! CONTEST TIME. The scrub round the lantern is crawling with scorpids. When "
        "you say yes, I blow this whistle and you eat eight scorpids before I run out of breath. I can hold my breath "
        "for five minutes. I practised.$B$BReady? *deep breath*",
        "Devour 8 scorpids in Durotar before Wren runs out of breath (5 minutes).",
        "*gasp* I ran out of breath! Again! Say yes again!",
        "*GASP* EIGHT! I held it the WHOLE TIME. I'm a little dizzy. You're the champion.$B$BHere's your prize. "
        "I'm going to sit down.",
        objectives=[devour(8, "Scorpid devoured", entries=[3125, 3126, 3127])], prev=a.id, sort=s, timed=300,
        choices=[(5617, "Vagabond Leggings"), (23404, "Padded Running Shoes"), (2218, "Craftsman's Dagger")],
        story="Wren's eating contest: eight scorpids before she runs out of breath (5 minutes).")
    c = book.quest(
        9105052, "The Dreadmaw", 10, 9, lantern, lantern, "hagatha",
        "Hagatha tells it slow, like a river:$B$BThe crocolisks of the Southfury River lie still for days, and the "
        "orcs who water their wolves there forget they are there, and then one day they remember. The Dreadmaw, they "
        "call them. When one closes its jaws, it tears the muscle off the bone.$B$BLet one do that to you, little "
        "horror, once. Then eat two. A thing that waits that long is a thing that is very sure of its hunger.",
        "On the Southfury River, let a Dreadmaw Crocolisk tear at you with its jaws, then devour 2 of them.",
        "They are still lying in the river. Go and remind them.",
        "Patient, wasn't it, until it wasn't? That is a crocolisk's whole secret. Some day the patience will grow "
        "teeth, and then more teeth.$B$BTake this, and go west when you are ready.",
        objectives=[struck(1, "Dreadmaw jaws felt", entries=[3110]),
                    devour(2, "Dreadmaw Crocolisk devoured", entries=[3110])], prev=b.id, sort=s, xp=6,
        choices=[(1436, "Frontier Britches"), (28159, "Undertaker's Gloves"), (3570, "Bonegrinding Pestle")],
        story="Hagatha's tale of the patient Dreadmaw crocolisks: feel their bite, then eat two.")
    mercy(book, 9105053, "Clutchless", 7, lantern, hatchling,
          [(214, -4601), (205, -4698), (140, -4760)],
          "Wren, urgently:$B$BSnack! A raptor egg hatched in the scrub south-east of the lantern and there's no mother. It's "
          "tiny and it's hissing at EVERYTHING. It smells of eggshell and dust. Sniff it out.$B$BDon't eat it. It's "
          "brave. Brave things get patted.",
          "Eggshell and dust, Snack. It's still hissing out there.",
          "It stopped hissing when you patted it! Then it followed you and fell over its own feet. I love it.$B$B"
          "Hagatha found another one at the cauldron. It's yours. Don't let it eat Bramble's boots.",
          (48118, "Leaping Hatchling", 1), s,
          "Mercy: Sniff out a motherless raptor hatchling and pat it. Reward: a raptor hatchling companion.",
          prev=a.id)
    return c


def mulgore_quests(book, lantern):
    s = Z_MULGORE
    pup = book.beast("dusty", "Dusty", 2958, level=5, faction=FACTION_SHY, passive=True, scale=0.55,
                     subname="Prairie Pup")
    a = book.quest(
        9105060, "Legs of the Plains", 6, 6, lantern, lantern, "hagatha",
        "Hagatha speaks, and the grass in the flame bends:$B$BThe tauren say the plainstrider was the Earth Mother's "
        "first runner, sent to carry news across Mulgore before there were tauren to hear it. It still runs, little "
        "horror, and it still has no news.$B$BEat six of the grown ones, the adults and the elders.",
        "Devour 6 plainstriders in Mulgore.",
        "Six striders. They will not stop running for you.",
        "Fast. Stringy. Proud of itself for no reason. A good shape to wear when you need to leave.$B$BTake this.",
        objectives=[devour(6, "Plainstrider devoured", entries=[2956, 2957])], sort=s,
        choices=[(24439, "Savage Leggings"), (26018, "Elekk Handler's Leathers"), (4948, "Stinging Mace")],
        story="The lesson: six grown plainstriders.")
    b = book.quest(
        9105061, "The Venture Co. Problem", 8, 7, lantern, lantern, "wren",
        "Wren, furious:$B$BSnack, goblins are drilling holes in Mulgore! The Venture Company. They're camped at the "
        "mine and the broken caravan north-west of the lantern, taking the plains apart for money. The tauren are too "
        "polite to chase them off.$B$BYou're not polite. Go and ROAR at them. Five of them. In your scariest shape. "
        "Watch them drop their drills and run.",
        "Roar (/roar) at 5 Venture Co. goblins in Mulgore and send them running.",
        "Still drilling, Snack. Roar louder!",
        "They RAN. One of them ran into a kodo. The kodo was fine.$B$BHagatha says the plains will heal. Here's "
        "something for your trouble.",
        objectives=[emote(5, "Venture Co. goblin sent running", EMOTE_ROAR,
                          entries=[2975, 2976, 2977, 2978, 2979], flee=True)],
        prev=a.id, sort=s,
        choices=[(5617, "Vagabond Leggings"), (23404, "Padded Running Shoes"), (2218, "Craftsman's Dagger")],
        story="Wren wants the Venture Co. off the plains: roar at the goblins until they run.")
    c = book.quest(
        9105062, "Mazzranache", 10, 9, lantern, lantern, "hagatha",
        "The flame flickers, and Hagatha tells it:$B$BThe Bloodhoof hunters speak of Mazzranache, a beast of the "
        "plains with no herd and no name of its own; they gave it one so they could curse it. It wanders, and no "
        "hunter has found its trail in years.$B$BYou are not a hunter, little horror. You are a nose. Turn on your "
        "Sniff at the lantern and follow its scent north-west, past the broken caravan, to the Golden Plains. At the end of "
        "the trail it will be waiting. Let it sting you once, so you know its poison. Then eat it.",
        "Follow Mazzranache's scent with Sniff to the Golden Plains, let it use a trick on you, then devour it.",
        "Mazzranache still wanders. Follow your nose, little horror.",
        "A beast with a name it never wanted. Now it has no name at all, only you.$B$BWear this. And when your "
        "plainstrider is ready to grow, remember the taste.",
        objectives=[trail("Mazzranache's trail followed", "Mazzranache", 1,
                          [(-1961, -803), (-1922, -684), (-1839, -611), (-1745, -548)], summon=3068),
                    struck(1, "Mazzranache's trick felt", entries=[3068]),
                    devour(1, "Mazzranache devoured", entries=[3068])],
        prev=b.id, sort=s, xp=6,
        choices=[(26021, "Vindicator's Leather Chaps"), (1436, "Frontier Britches"), (26052, "Vindicator's Smasher")],
        story="Follow Mazzranache's scent with Sniff across the plains, feel its poison, and eat the nameless beast.")
    mercy(book, 9105063, "Dusty", 7, lantern, pup,
          [(-2300, -906), (-2440, -1012), (-2600, -1000)],
          "Wren, smiling:$B$BSnack, there's a prairie wolf pup south of the lantern who keeps trying to howl and only "
          "sneezes. The pack laughs at him. He smells of dust and grass and trying very hard.$B$BSniff him out. Pat "
          "him. Tell him the howl will come.",
          "Dust and grass and trying very hard, Snack.",
          "He followed you and SNEEZED. Then he howled! A real one, a small one. You did that.$B$BHere's a little "
          "friend for you, too. It digs. It won't howl, but it'll try.",
          (10394, "Prairie Dog Whistle", 1), s,
          "Mercy: Sniff out Dusty, the prairie pup who can only sneeze, and pat him. Reward: a prairie dog "
          "companion.", prev=a.id)
    return c


def tirisfal_quests(book, lantern):
    s = Z_TIRISFAL
    palewing = book.beast("palewing", "Pale Wing", 1553, level=6, faction=FACTION_SHY, passive=True, scale=0.6,
                          subname="Duskbat Pup")
    a = book.quest(
        9105070, "Wings in the Gloom", 6, 6, lantern, lantern, "hagatha",
        "Hagatha's voice is almost fond:$B$BThe duskbats of Tirisfal grew fat on what the plague left behind. They "
        "are blind, little horror, and they need nothing else. They hear your heart. They hear its hunger.$B$BEat six "
        "of them, the greater ones and the vampiric ones. Learn to hear like they do.",
        "Devour 6 duskbats in Tirisfal Glades.",
        "Six bats. Listen for them; they are listening for you.",
        "Did you hear them? A heartbeat, a wing, a breath. That is how a bat sees.$B$BTake this.",
        objectives=[devour(6, "Duskbat devoured", entries=[1553, 1554])], sort=s,
        choices=[(26020, "Shard-Covered Leggings"), (4974, "Compact Fighting Knife"), (23405, "Farstrider's Tunic")],
        story="The lesson: six of Tirisfal's duskbats, to hear like a bat.")
    b = book.quest(
        9105071, "Supper at Cold Hearth", 8, 7, lantern, lantern, "wren",
        "Wren, holding her nose:$B$BSnack, the dead are WALKING around Cold Hearth Manor, west of the lantern. "
        "Rotting dead and ravaged corpses. Hagatha says they're just very old meat. I say CONTEST. When you say yes I "
        "light this candle, and you eat five of them before it burns down. Five minutes. It's a short candle.$B$BDon't "
        "tell me what they taste like. Actually do.",
        "Devour 5 rotting dead or ravaged corpses near Cold Hearth Manor before Wren's candle burns down (5 minutes).",
        "The candle went out! I'll light another one. Go!",
        "FIVE! Before the candle! What did they taste like? ...Old cheese? I KNEW it.$B$BHere's your prize. I'm "
        "airing out the lantern.",
        objectives=[devour(5, "Walking dead devoured", entries=[1525, 1526])], prev=a.id, sort=s, timed=300,
        choices=[(5617, "Vagabond Leggings"), (6215, "Balanced Fighting Stick"), (23404, "Padded Running Shoes")],
        story="Wren's candle-timed contest: five of the walking dead of Cold Hearth Manor (5 minutes).")
    c = book.quest(
        9105072, "The Scarlet Table", 10, 9, lantern, lantern, "hagatha",
        "Hagatha's tale comes cold:$B$BThe Scarlet Crusade came to Tirisfal to burn the dead. They have burned a great "
        "many things that were not dead yet. Their missionaries throw fire with their prayers, little horror. Let one "
        "of them throw it at you, so you know the taste of their faith. Then eat five of them, at their farms and "
        "their watch posts around the glades.$B$BA bat that drinks the Scarlet's blood grows into something the "
        "Scarlet have nightmares about.",
        "Let a Scarlet Missionary throw its Fireball at you, then devour 5 of the Scarlet Crusade in Tirisfal Glades.",
        "Five crusaders, and one prayer of fire. They are easy to find; they shout.",
        "Sure of themselves to the very end. Now you are sure of something too.$B$BTake this, and when your bat is "
        "ready to grow, remember the taste of red.",
        objectives=[struck(1, "Scarlet fire felt", entries=[1536]),
                    devour(5, "Scarlet crusader devoured", entries=[1535, 1536, 1537, 1538, 1539, 1540])],
        prev=b.id, sort=s, xp=6,
        choices=[(1302, "Black Whelp Gloves"), (5327, "Greasy Tinker's Pants"), (3581, "Serrated Knife")],
        story="Hagatha's tale of the Scarlet's burning faith: feel a missionary's fire, then eat five crusaders.")
    mercy(book, 9105073, "Pale Wing", 7, lantern, palewing,
          [(2440, 732), (2341, 778), (2300, 870)],
          "Wren, whispering:$B$BSnack, a duskbat pup fell out of its tree by Stillwater Pond, west of the lantern. "
          "It's white. All the others are brown. They won't let it back up. It smells of pond water and being "
          "different.$B$BSniff it out and pat it. Being different is fine. Look at you.",
          "Pond water and being different, Snack.",
          "It flew! After you patted it, it flew. Not well, but up.$B$BHagatha says the pond gave her this for "
          "you. It's a cockroach. She says it's a good one. I believe her, mostly.",
          (10393, "Cockroach", 1), s,
          "Mercy: Sniff out a white duskbat pup the others won't let back up, and pat it. Reward: a (good) "
          "cockroach companion.", prev=a.id)
    return c


def eversong_quests(book, lantern):
    s = Z_EVERSONG
    sunwhisker = book.beast("sunwhisker", "Sunwhisker", 15651, level=6, faction=FACTION_SHY, passive=True, scale=0.55,
                            subname="Springpaw Kit")
    crystal = book.thing("eversong_crystal", "Overflowing Mana Crystal", CRYSTAL, [(530, 8895.0, -6612.0, 32.5, 0.0)],
                         size=0.6, summon=15647, count=4)
    a = book.quest(
        9105080, "Spilled Magic", 6, 6, lantern, lantern, "hagatha",
        "Hagatha speaks, and the flame hums:$B$BWhen the elves spill their magic, something always laps it up. Around "
        "the sanctums of Eversong the spill has grown legs: mana stalkers and manawraiths, little whirlwinds of "
        "leftover spell. Your mana wyrm would love them.$B$BEat six. Taste what the elves threw away.",
        "Devour 6 mana stalkers or manawraiths in Eversong Woods.",
        "Six of them. The sanctums hum with them.",
        "Sweet and thin, like the elves. That is the taste of magic without anyone holding it.$B$BTake this.",
        objectives=[devour(6, "Spilled magic devoured", entries=[15647, 15648])], sort=s,
        choices=[(28149, "Tranquillien Breeches"), (24439, "Savage Leggings"), (4974, "Compact Fighting Knife")],
        story="The lesson: six whirlwinds of the elves' spilled magic.")
    b = book.quest(
        9105081, "The Overflow", 8, 7, lantern, lantern, "wren",
        "Wren, alarmed:$B$BSnack, I left a mana crystal next to the lantern to charge and it's OVERFLOWING. Little "
        "stalkers keep popping out of it like popcorn. Touch the crystal to let the rest out all at once, and then "
        "eat them before they wander off and bother the elves.$B$BSorry. Science is messy.",
        "Touch the Overflowing Mana Crystal by the lantern and devour 4 of the mana stalkers that pour out.",
        "Still popping, Snack!",
        "The crystal's empty and so are the stalkers. Well. They're full. You're full.$B$BHere, for cleaning up after "
        "my science.",
        objectives=[devour(4, "Overflow devoured", entries=[15647])], prev=a.id, sort=s, lures=[crystal],
        choices=[(28147, "Tranquillien Scout's Bracers"), (5617, "Vagabond Leggings"), (2218, "Craftsman's Dagger")],
        story="Wren's overcharged crystal by the lantern: let the swarm of mana stalkers out and eat it.")
    c = book.quest(
        9105082, "The Wretched Feast", 10, 9, lantern, lantern, "hagatha",
        "Hagatha's voice is sad and not at all sorry:$B$BThe Wretched were elves who could not stop drinking magic, and "
        "now magic is all they are hungry for. Their withdrawal is so bitter it hurts the ones they touch. Let one of "
        "them share its Bitter Withdrawal with you, little horror. Then eat six. They haunt Sunsail Anchorage and the "
        "shore to the west.$B$BThey are like you, except they never learned to be anything else.",
        "Let one of the Wretched pass its Bitter Withdrawal to you, then devour 6 Wretched in Eversong Woods.",
        "Six of the Wretched. They will not be missed.",
        "Hungry things eating hungry things. Do not think about it too long.$B$BTake this, and when your wyrm grows, "
        "you will know why I sent you.",
        objectives=[struck(1, "Bitter Withdrawal felt", entries=[15645, 16162]),
                    devour(6, "Wretched devoured", entries=[15645, 16162, 15644])], prev=b.id, sort=s, xp=6,
        choices=[(28142, "Farstrider's Belt"), (28157, "Black Leather Jerkin"), (3581, "Serrated Knife")],
        story="Hagatha's tale of the Wretched: feel their bitter withdrawal, then eat six.")
    mercy(book, 9105083, "Sunwhisker", 7, lantern, sunwhisker,
          [(9051, -6620), (9175, -6562), (9300, -6600)],
          "Wren, soft:$B$BSnack, a springpaw kit is hiding in the ferns north of the lantern. The Wretched scared its "
          "family off. It smells of sunlight and fern and being scared. Sniff it out and pat it, gently, and it'll "
          "know it's safe.",
          "Sunlight and fern, Snack.",
          "It's not scared any more. It followed you halfway to the road, then went to look for its family.$B$B"
          "Here's a kitten that will never have to hide. An orange one, for the sun.",
          (8487, "Cat Carrier (Orange Tabby)", 1), s,
          "Mercy: Sniff out a frightened springpaw kit and pat it. Reward: an orange kitten companion.", prev=a.id)
    return c
