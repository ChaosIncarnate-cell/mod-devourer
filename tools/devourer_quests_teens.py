"""Task 021: the first lanterns abroad (levels 11-20). Part of tools/devourer_quests_content.py."""

from devourer_quests import devour
from devourer_quests_content import breadcrumb, LANTERN_OPEN

Z_WESTFALL, Z_LOCHMODAN, Z_DARKSHORE, Z_BLOODMYST, Z_BARRENS, Z_SILVERPINE, Z_GHOSTLANDS = (
    40, 38, 148, 3525, 17, 130, 3433)
DERBY_WREN = 9101360                          # Wren at the Derby's starting line (task 020)
BAIT = 216                                    # the look of Hagatha's Bait (the sisters' bubbling cauldron)


def onward(book, qid, level, home, lantern, prev, line):
    """The last quest of a lantern: Hagatha points to the next one."""
    return breadcrumb(
        book, qid, f"A Lantern in {lantern.region}", level, home, lantern, 0,
        f"You have eaten what {home.region} had to teach, little horror. {line}$B$BI have hung another lantern in "
        f"{lantern.region}, {lantern.where}. Go to it. The beasts there are bigger, and so are the tales.",
        "You found it. Of course you did; you follow your stomach, and your stomach follows me.$B$BSit. Listen. "
        f"{lantern.region} is hungry too.",
        f"Hagatha sends the Devourer on to her lantern in {lantern.region}.", prev=prev)


def teens(book, homes):
    westfall = book.lantern("westfall", "Westfall", 0, -10800.0, 1100.0, 39.36, 5.6,
                            "the plains south-west of Sentinel Hill")
    lochmodan = book.lantern("lochmodan", "Loch Modan", 0, -5600.0, -3200.0, 325.16, 0.4,
                             "Grizzlepaw Ridge, south of Thelsamar")
    darkshore = book.lantern("darkshore", "Darkshore", 1, 6300.0, 150.0, 33.71, 2.9, "the hills south of Auberdine")
    bloodmyst = book.lantern("bloodmyst", "Bloodmyst Isle", 530, -2300.0, -11900.0, 25.92, 1.0,
                             "the red woods north of Blood Watch")
    barrens = book.lantern("barrens", "The Barrens", 1, -780.0, -2680.0, 92.04, 2.2,
                           "beside Wren's Derby, west of the Crossroads")
    silverpine = book.lantern("silverpine", "Silverpine Forest", 0, 500.0, 1200.0, 87.17, 4.0,
                              "the pines south of the Sepulcher")
    ghostlands = book.lantern("ghostlands", "Ghostlands", 530, 7400.0, -6900.0, 51.34, 3.3,
                              "Sungraze Peak, south-west of Tranquillien")

    book.region("The first lanterns abroad (levels 11-20)",
                "Each home lantern points to one of seven lanterns abroad. Their quests lead into the first molts: "
                "the beasts and the named creatures the tier-2 forms grow on.")

    nxt = {"elwynn": (9105013, westfall, "The plains west of it are full of hungry things that got there first."),
           "dunmorogh": (9105023, lochmodan, "Beyond the tunnel the troggs dig deeper and the crocolisks grow longer."),
           "teldrassil": (9105033, darkshore, "Across the water the cats grow black and the owls grow wise."),
           "azuremyst": (9105043, bloodmyst, "North of you the island bleeds, and its beasts have drunk it."),
           "durotar": (9105053, barrens, "West of you the grass goes on for ever, and so does what lives in it."),
           "mulgore": (9105063, barrens, "East of the mesas the grass goes on for ever, and so does what lives in it."),
           "tirisfal": (9105073, silverpine, "South of you the worgs howl under the pines."),
           "eversong": (9105083, ghostlands, "South of you the woods are dead, and the dead are hungry.")}
    for key, (qid, target, line) in nxt.items():
        home_lantern, finale = homes[key]
        onward(book, qid, 11, home_lantern, target, finale.id, line)

    return {
        "westfall": (westfall, westfall_quests(book, westfall)),
        "lochmodan": (lochmodan, lochmodan_quests(book, lochmodan)),
        "darkshore": (darkshore, darkshore_quests(book, darkshore)),
        "bloodmyst": (bloodmyst, bloodmyst_quests(book, bloodmyst)),
        "barrens": (barrens, barrens_quests(book, barrens)),
        "silverpine": (silverpine, silverpine_quests(book, silverpine)),
        "ghostlands": (ghostlands, ghostlands_quests(book, ghostlands)),
    }


def westfall_quests(book, lantern):
    s = Z_WESTFALL
    a = book.quest(
        9105100, "Coyote Supper", 12, 11, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha's voice drifts out over the dry grass:$B$BThe coyotes of Westfall live on what the "
        "farmers left when they fled. They are thin, little horror, and thinness is a kind of hunger that has "
        "learned to wait.$B$BEat six of them, the runners and the pack leaders. A wolf that has eaten coyote "
        "learns to wait as well.",
        "Devour 6 coyotes in Westfall.",
        "Six coyotes. They are thin, but they are there.",
        "Thin, and patient, and hungry. You have more in common with them than with the farmers.$B$BTake this.",
        objectives=[devour(6, "Coyote devoured", entries=[834, 833])], sort=s,
        choices=[(5299, "Gloves of the Moon"), (1306, "Wolfmane Wristguards"), (2908, "Thornblade")],
        story="Hagatha teaches the patience of the thin: six of Westfall's coyotes.")
    b = book.quest(
        9105101, "Goretusk Gristle", 14, 12, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren's voice, munching something:$B$BMmf. Snack! Westfall's famous for its stew. Goretusk "
        "stew! The farmers used to make it before they all ran off. I want to make it, but I can't catch a "
        "goretusk from in here, so you have to eat the goretusks and I'll make stew in my imagination.$B$BFive "
        "goretusks. And three of the fleshrippers, the vultures, because every stew needs a bit of bird.",
        "Devour 5 goretusks and 3 fleshrippers in Westfall.",
        "Imaginary stew needs real goretusks, Snack.",
        "Imaginary stew is DONE. It's the best stew I've never had.$B$BHere's your bowl. Well. Not a bowl.",
        objectives=[devour(5, "Goretusk devoured", entries=[454, 157, 547]),
                    devour(3, "Fleshripper devoured", entries=[199, 1109, 154])], prev=a.id, sort=s,
        choices=[(1310, "Smith's Trousers"), (5609, "Steadfast Cinch"), (5757, "Hardwood Cudgel")],
        story="Wren makes imaginary Westfall stew: goretusks and fleshrippers.")
    c = book.quest(
        9105102, "Longshore Murlocs", 15, 14, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha speaks, and the flame smells of the sea:$B$BThe murlocs of the Longshore gurgle and "
        "breed and gurgle. They are not clever, little horror, but they are wet, and a toad that eats them grows "
        "fat and slippery and strange. Your toad would like that.$B$BEat six of them, anywhere along the coast.",
        "Devour 6 murlocs along the Longshore in Westfall.",
        "Six murlocs. Follow the gurgling.",
        "Slippery, salty, and loud even on the way down. Your toad will remember.$B$BTake this.",
        objectives=[devour(6, "Longshore murloc devoured", entries=[515, 126, 513, 456, 171, 458, 517, 127])],
        prev=b.id, sort=s,
        choices=[(26023, "Ravager Hide Gloves"), (6480, "Slick Deviate Leggings"), (5279, "Harpy Skinner")],
        story="Hagatha sends the Devourer along the Longshore: murlocs, for a toad that wants to grow.")
    d = book.quest(
        9105103, "Old Murk-Eye", 18, 16, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha tells it low, like a secret:$B$BAt the far south of the Longshore there is a murloc "
        "so old that his eye has gone milky, and the other murlocs bring him fish so he will not eat them "
        "instead. Old Murk-Eye, the sailors call him. He has been eating the coast for longer than Westfall has had "
        "farms.$B$BEat him, little horror. Toads stay in the swamp; the salamander is the one that crawled out "
        "and liked it. Old Murk-Eye will teach your toad to crawl.",
        "Devour Old Murk-Eye at the southern end of the Longshore in Westfall.",
        "The old one still eats the coast.",
        "Old, and cold, and finally still. Something in your toad stirred when you swallowed him; I felt it from "
        "here.$B$BTake this. You have earned something better than murloc.",
        objectives=[devour(1, "Old Murk-Eye devoured", entries=[391])], prev=c.id, sort=s, xp=6,
        choices=[(3431, "Bone-studded Leather"), (17694, "Band of the Fist"), (1264, "Headbasher")],
        story="Hagatha's tale of Old Murk-Eye, the oldest murloc of the coast (a Water Salamander task).")
    return d


def lochmodan_quests(book, lantern):
    s = Z_LOCHMODAN
    lure = book.thing("loch_bait", "Hagatha's Bait", BAIT, [(0, -5145.0, -3650.0, 303.4, 0.0)], size=0.7,
                      summon=2476)
    a = book.quest(
        9105110, "Stonesplinter Bones", 13, 12, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha speaks:$B$BThe Stonesplinter troggs of the valley south of here dig because "
        "digging is all they remember. Their bones are half stone already. A trogg that eats them grows harder "
        "in the back, where the blows land.$B$BEat six of them in Stonesplinter Valley.",
        "Devour 6 Stonesplinter troggs in Loch Modan.",
        "Six troggs. They are still digging.",
        "Hard to chew? Good. Something hard to chew is something hard to kill.$B$BTake this.",
        objectives=[devour(6, "Stonesplinter trogg devoured", entries=[1161, 1162, 1166, 1163, 1197, 1164])],
        sort=s,
        choices=[(5629, "Hammerfist Gloves"), (24351, "Mace of the Hand"), (22998, "Ghostclaw Leggings")],
        story="Hagatha teaches the trogg's hard back: six Stonesplinter troggs.")
    b = book.quest(
        9105111, "Bear Fat and Boar Bristle", 14, 12, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren, half singing:$B$BBear fat for the cauldron, boar bristle for the brush! Snack, "
        "Hagatha's out of both and she's being VERY grumpy about it. The loch is full of black bears and mountain "
        "boars.$B$BEat four bears and four boars and I'll scrape what I need off your shadow. Don't ask.",
        "Devour 4 black bears and 4 mountain boars in Loch Modan.",
        "Still no fat, still no bristle. Hagatha's still grumpy.",
        "Hagatha's smiling. Well. Her face is doing something.$B$BHere, from both of us.",
        objectives=[devour(4, "Black bear devoured", entries=[1186, 1188, 1189]),
                    devour(4, "Mountain boar devoured", entries=[1190, 1191, 1192])], prev=a.id, sort=s,
        choices=[(1310, "Smith's Trousers"), (5351, "Bounty Hunter's Ring"), (2908, "Thornblade")],
        story="Wren needs bear fat and boar bristle for Hagatha's cauldron.")
    c = book.quest(
        9105112, "The Loch's Teeth", 16, 14, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha's voice goes still as water:$B$BThe crocolisks of the loch lie along the shore like "
        "logs, and the dwarves who fish there have learned to count the logs. Eat four of them, little horror. "
        "Their shape is the beginning of a long road: the komodo, and after the komodo, the dragon of the "
        "southern islands.",
        "Devour 4 Loch Crocolisks in Loch Modan.",
        "Four of them. Count the logs.",
        "Your belly is full of patience now. A komodo is only a crocolisk that stopped waiting.$B$BTake this.",
        objectives=[devour(4, "Loch Crocolisk devoured", entries=[1693])], prev=b.id, sort=s,
        choices=[(3585, "Camouflaged Tunic"), (26023, "Ravager Hide Gloves"), (5757, "Hardwood Cudgel")],
        story="Hagatha starts the Devourer on the long crocolisk road: four Loch Crocolisks.")
    d = book.quest(
        9105113, "The Large Loch Crocolisk", 22, 20, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha tells it slowly, and you can hear her smile:$B$BThe dwarves of Thelsamar tell their "
        "children of a crocolisk in the loch so big it once ate a boat. The children do not believe it. The "
        "boat's owner does. It surfaces only once in a long while, and then it goes back down.$B$BI have left a "
        "bait on the eastern shore of the loch. Touch it, and it will come up for you. Eat it. A komodo "
        "that has eaten the Large Loch Crocolisk is ready to become a dragon.",
        "Devour the Large Loch Crocolisk in Loch Modan. Hagatha's Bait, on the eastern shore of the loch, will call it.",
        "It is still at the bottom of the loch. Touch my bait.",
        "A crocolisk that ate a boat, and a Devourer that ate the crocolisk. The children will tell it now.$B$B"
        "Take this. And when your komodo is grown enough, it will know what to do.",
        objectives=[devour(1, "Large Loch Crocolisk devoured", entries=[2476])], prev=c.id, sort=s, xp=6,
        lures=[lure],
        choices=[(6670, "Panther Armor"), (16659, "Deftkin Belt"), (6093, "Orc Crusher")],
        story="Hagatha's bait calls the Large Loch Crocolisk, the one that ate a boat (a Komodo Dragon task).")
    return d


def darkshore_quests(book, lantern):
    s = Z_DARKSHORE
    lure = book.thing("shadowclaw_bait", "Hagatha's Bait", BAIT, [(1, 6560.0, 310.0, 31.22, 0.0)], size=0.7,
                      summon=2175)
    a = book.quest(
        9105120, "Moonstalkers", 12, 11, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha speaks under her breath:$B$BThe moonstalkers of Darkshore are the nightsaber's "
        "darker cousins. The night elves left this coast to them when they left everything else. Eat six of "
        "them, little horror, the runts and the grown ones. A saber needs to know the dark it hunts in.",
        "Devour 6 moonstalkers in Darkshore.",
        "Six moonstalkers. They are darker than the night, but not darker than you.",
        "Darker. Quieter. Hungrier. Your cat will be all three one day.$B$BTake this.",
        objectives=[devour(6, "Moonstalker devoured", entries=[2070, 2069])], sort=s,
        choices=[(5299, "Gloves of the Moon"), (22998, "Ghostclaw Leggings"), (5279, "Harpy Skinner")],
        story="Hagatha teaches the dark the saber hunts in: six moonstalkers.")
    b = book.quest(
        9105121, "Thistle and Stride", 14, 12, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren's voice, bouncing:$B$BSnack! Two things. One: the bears in Darkshore are called THISTLE "
        "bears, which means they're prickly, which means they're a challenge. Two: the striders have long legs "
        "and long legs are tasty.$B$BFour bears, four striders. I'm keeping score!",
        "Devour 4 thistle bears and 4 foreststriders in Darkshore.",
        "Score's still zero, Snack. Bears and striders!",
        "Eight points! That's a record. It's the only record. Still a record.$B$BPrize!",
        objectives=[devour(4, "Thistle bear devoured", entries=[2163, 2164, 2165]),
                    devour(4, "Foreststrider devoured", entries=[2321, 2322, 2323])], prev=a.id, sort=s,
        choices=[(1306, "Wolfmane Wristguards"), (1310, "Smith's Trousers"), (24351, "Mace of the Hand")],
        story="Wren keeps score: thistle bears and foreststriders.")
    c = book.quest(
        9105122, "The Moonkin of Darkshore", 15, 13, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha speaks, and the flame goes silver:$B$BAn owl that eats enough moonlight stands up "
        "one night and becomes a moonkin. Darkshore's moonkin went mad when the coast went dark, and their oracle "
        "most of all. They wander the woods east of Auberdine, raving at the trees.$B$BEat four of them, and their "
        "oracle. Your owl is waiting to stand up.",
        "Devour 4 moonkin and the Moonkin Oracle in Darkshore.",
        "The moonkin still rave at the trees. And the oracle loudest.",
        "Moonlight and madness. A heavy meal. Your owl will carry it.$B$BTake this.",
        objectives=[devour(4, "Moonkin devoured", entries=[10159, 10158, 10160]),
                    devour(1, "Moonkin Oracle devoured", entries=[10157])], prev=b.id, sort=s,
        choices=[(26023, "Ravager Hide Gloves"), (3585, "Camouflaged Tunic"), (2908, "Thornblade")],
        story="Hagatha's tale of the mad moonkin and their oracle (a Moonkin task).")
    d = book.quest(
        9105123, "Shadowclaw", 16, 14, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha's voice drops to almost nothing:$B$BOn Darkshore they say a black cat once swallowed "
        "a scream, and it has hunted in silence ever since. Shadowclaw. It walks the woods north-east of Auberdine and "
        "comes when it pleases, which is rarely.$B$BIt will come for my bait. I left it in the woods north-east of the "
        "town. Touch it, then eat what comes. Mind your voice near it.",
        "Devour Shadowclaw in Darkshore. Hagatha's Bait, in the woods north-east of Auberdine, will call it.",
        "The cat still hunts in silence. Touch my bait, little horror.",
        "Did it scream when it died? No. It had nothing left to scream with.$B$BTake this, and when your saber is "
        "ready, you will hunt as quietly as that.",
        objectives=[devour(1, "Shadowclaw devoured", entries=[2175])], prev=c.id, sort=s, xp=6, lures=[lure],
        choices=[(3741, "Stomping Boots"), (17694, "Band of the Fist"), (3431, "Bone-studded Leather")],
        story="Hagatha's bait calls Shadowclaw, the cat that swallowed a scream (a Shadowclaw task).")
    return d


def bloodmyst_quests(book, lantern):
    s = Z_BLOODMYST
    a = book.quest(
        9105130, "Ravager Hatchlings", 12, 11, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren, horrified and delighted:$B$BSnack, the red island has RAVAGERS. Babies! All claws and "
        "no manners. They fell out of the ship with everything else and they've been eating the island ever "
        "since. That's YOUR job.$B$BEat six of the hatchlings before they grow up and get ideas.",
        "Devour 6 Bloodmyst Hatchlings on Bloodmyst Isle.",
        "Six hatchlings, Snack. They're getting ideas.",
        "Crunchy babies. That sounds bad when I say it out loud.$B$BHere!",
        objectives=[devour(6, "Bloodmyst Hatchling devoured", entries=[17525])], sort=s,
        choices=[(26023, "Ravager Hide Gloves"), (23408, "Farstrider's Bracers"), (2908, "Thornblade")],
        story="Wren wants the ravager hatchlings eaten before they grow up.")
    b = book.quest(
        9105131, "Blue Wings", 15, 13, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha speaks, and the flame turns blue:$B$BThe draenei say the bluest moths dream for "
        "the ones they put to sleep. The royal blue flutterers of this island are the bluest of all; they drift "
        "over the north of it, along the Bloodwash. Never ask them what they dream about.$B$BEat four. Your moth "
        "will dream bluer.",
        "Devour 4 Royal Blue Flutterers on Bloodmyst Isle.",
        "Four flutterers. They drift; follow them.",
        "Did you dream? Do not tell me. Some dreams are better swallowed.$B$BTake this.",
        objectives=[devour(4, "Royal Blue Flutterer devoured", entries=[17350, 17349])], prev=a.id, sort=s,
        choices=[(22998, "Ghostclaw Leggings"), (5351, "Bounty Hunter's Ring"), (5757, "Hardwood Cudgel")],
        story="Hagatha's tale of the moths that dream for others (the Royal Blue Flutterer is a moth's molt).")
    c = book.quest(
        9105132, "The Warp Piston", 16, 15, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha's voice comes wrong, as if from far away:$B$BWhere the ship's engine broke open, at "
        "the Warp Piston in the north-east, the world has thinned to a rag. Things come through. Void anomalies, "
        "the draenei call them: little tears that learned to move.$B$BEat three of them, little horror. You were "
        "born from the dark between; you will find they taste of home.",
        "Devour 3 Void Anomalies at the Warp Piston on Bloodmyst Isle.",
        "Three anomalies. The world is thin there; mind you do not fall through.",
        "Home, wasn't it? Cold and close. Your voidling and your warp stalker will both grow on that taste.$B$B"
        "Take this.",
        objectives=[devour(3, "Void Anomaly devoured", entries=[17550])], prev=b.id, sort=s,
        choices=[(3585, "Camouflaged Tunic"), (1306, "Wolfmane Wristguards"), (24351, "Mace of the Hand")],
        story="Hagatha sends the Devourer to the torn world at the Warp Piston (a Voidcreeper and Void Terror task).")
    d = book.quest(
        9105133, "Wyrmscar", 17, 15, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren, whispering for once:$B$BSnack, on Wyrmscar Island in the south-west there are dragons. "
        "DEAD dragons. Well, undead. Bony little whelps that the blood elves are poking with spells. Hagatha says "
        "a whelp is a whelp even when it's mostly bones.$B$BEat five of the veridian whelps and broodlings. "
        "Bones are good for your teeth!",
        "Devour 5 veridian whelps or broodlings on Wyrmscar Island, Bloodmyst Isle.",
        "Five bony whelps, Snack. Crunch crunch.",
        "Dragon bones! You've eaten DRAGON. Well, dragon-ish. I'm telling everyone.$B$BHere's your prize.",
        objectives=[devour(5, "Veridian whelp devoured", entries=[17588, 17589])], prev=c.id, sort=s, xp=6,
        choices=[(3741, "Stomping Boots"), (16990, "Spritekin Cloak"), (1264, "Headbasher")],
        story="Wren sends the Devourer to crunch the bony whelps of Wyrmscar Island.")
    return d


def barrens_quests(book, lantern):
    s = Z_BARRENS
    a = book.quest(
        9105140, "Fleeting Legs", 12, 11, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha's voice rolls over the grass:$B$BIn Mulgore they tell of a chick that never stopped "
        "running. The wind caught up with it once, and has been chasing it ever since. Its children are here: the "
        "greater plainstriders, the fleeting ones, the ornery ones.$B$BEat six of them, little horror. Your "
        "strider has more running in it than it knows.",
        "Devour 6 plainstriders in the Barrens.",
        "Six striders. They will not stand still for you.",
        "Did you feel the wind? That was the chase. One day you will be the one it is chasing.$B$BTake this.",
        objectives=[devour(6, "Barrens plainstrider devoured", entries=[3244, 3246, 3245])], sort=s,
        choices=[(1306, "Wolfmane Wristguards"), (5299, "Gloves of the Moon"), (5279, "Harpy Skinner")],
        story="Hagatha's tale of the chick the wind chases: six Barrens plainstriders.")
    b = book.quest(
        9105141, "Quilboar Bacon", 15, 13, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren's voice, scandalised:$B$BSnack, the quilboar of Thorn Hill are throwing rocks at the "
        "caravans AND they smell. That's two crimes. The punishment is being eaten.$B$BEat six of the Razormane. "
        "The quilboar say a boar struck often enough forgets how to fall. Let's find out!",
        "Devour 6 Razormane quilboar in the Barrens.",
        "Six quilboar, Snack. They're still throwing rocks.",
        "Justice! Smelly justice.$B$BHagatha says quilboar is good for a boar that wants to grow. Here's your "
        "reward for being a good boar.",
        objectives=[devour(6, "Razormane quilboar devoured", entries=[3267, 3268, 3265, 3266, 3269, 3271])],
        prev=a.id, sort=s,
        choices=[(1310, "Smith's Trousers"), (5609, "Steadfast Cinch"), (24351, "Mace of the Hand")],
        story="Wren punishes the rock-throwing quilboar of Thorn Hill (a Raging Agam'ar task).")
    c = book.quest(
        9105142, "Teeth of the Savannah", 17, 15, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren, keeping count on her fingers:$B$BRaptors, Snack! The sunscale ones, with the pretty "
        "colours. And the hyenas, the hecklefangs, because they laugh at everything and it's RUDE. Four raptors "
        "and three hyenas.$B$BIf one of them laughs at you, eat that one first.",
        "Devour 4 sunscale raptors and 3 hecklefang hyenas in the Barrens.",
        "Four raptors, three hyenas. Somebody's still laughing.",
        "Nobody's laughing now. Except me. I'm laughing because you're brilliant.$B$BHere!",
        objectives=[devour(4, "Sunscale raptor devoured", entries=[3254, 3255, 3256]),
                    devour(3, "Hecklefang hyena devoured", entries=[4127, 4129])], prev=b.id, sort=s,
        choices=[(3741, "Stomping Boots"), (26023, "Ravager Hide Gloves"), (5757, "Hardwood Cudgel")],
        story="Wren wants the rude hyenas and the pretty raptors of the savannah.")
    d = book.quest(
        9105143, "The Thunderhawk Nests", 19, 17, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha tells it, and thunder rumbles somewhere in the flame:$B$BThe tauren say the thunder "
        "is only the wind serpents clearing their throats. Their young nest in the south, around Agama'gor and "
        "beyond, the thunderhawk hatchlings. A strider that eats one learns how the wind feels from above; a "
        "snake that eats one starts to grow wings.$B$BEat one, little horror. Then Wren has something for you.",
        "Devour a Thunderhawk Hatchling in the southern Barrens.",
        "The hatchlings still nest in the south.",
        "Did you feel the sky in it? Good.$B$BTake this. And go and see my sister at her starting line; she has "
        "been bursting to tell you something for days.",
        objectives=[devour(1, "Thunderhawk Hatchling devoured", entries=[3247])], prev=c.id, sort=s, xp=6,
        choices=[(6670, "Panther Armor"), (17694, "Band of the Fist"), (6093, "Orc Crusher")],
        story="Hagatha's tale of the thunder in the wind serpents' throats (a Greater Plainstrider task).")
    book.quest(
        9105144, "Wren's Starting Line", 20, 20, lantern, DERBY_WREN, "wren",
        LANTERN_OPEN + "Wren's voice, so excited it squeaks:$B$BSnack! SNACK. Come to the starting line, right next "
        "to the lantern, by the road west of the Crossroads. I'm there! Well, a bit of me is there. Enough of me to "
        "start a race. I'll explain when you get here.$B$BBring Bramble!",
        "Speak with Wren Hollowmoor at the Derby's starting line, west of the Crossroads.",
        "I'm RIGHT HERE, Snack.",
        "You came! Hagatha thinks her bird can beat you. Her BIRD. Let me tell you about the bet...",
        prev=d.id, sort=s, xp=2,
        story="Wren calls the Devourer to the Derby's starting line (Wren's Derby, task 020).")
    return d


def silverpine_quests(book, lantern):
    s = Z_SILVERPINE
    a = book.quest(
        9105150, "Worg Meat", 12, 11, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha speaks, and somewhere a wolf howls:$B$BThe worgs of Silverpine are wolves that "
        "remember something older. Their eyes are too clever. Eat six of them, little horror, the plain worgs and "
        "the mottled ones. A wolf that has eaten worg starts to remember too.",
        "Devour 6 worgs in Silverpine Forest.",
        "Six worgs. They watch you from the pines.",
        "Clever eyes, and now clever in your belly. Your wolf is listening.$B$BTake this.",
        objectives=[devour(6, "Worg devoured", entries=[1765, 1766])], sort=s,
        choices=[(1306, "Wolfmane Wristguards"), (5299, "Gloves of the Moon"), (2908, "Thornblade")],
        story="Hagatha teaches the worg's old memory: six worgs of Silverpine.")
    b = book.quest(
        9105151, "Moonrage", 14, 12, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren, outraged:$B$BSnack, the Moonrage gnolls howl at the moon all night and I can hear it "
        "from HERE. In the In-Between. Through a lantern. That's how loud they are.$B$BEat five of them so I can "
        "sleep. Please. I'm so tired.",
        "Devour 5 Moonrage gnolls in Silverpine Forest.",
        "Still howling, Snack. Still awake.",
        "Silence! Beautiful silence. I'm going to have the best nap.$B$BHere, and goodnight.",
        objectives=[devour(5, "Moonrage gnoll devoured", entries=[1769, 1770, 1779, 1782, 1924])], prev=a.id,
        sort=s,
        choices=[(1310, "Smith's Trousers"), (5609, "Steadfast Cinch"), (24351, "Mace of the Hand")],
        story="Wren cannot sleep for the Moonrage gnolls' howling.")
    c = book.quest(
        9105152, "Bloodsnout", 17, 15, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha tells it, and the flame runs red:$B$BEvery pack has one that runs behind the others. "
        "Not out of fear, little horror. It is choosing which leg to take first. Along the Greymane Wall, in the "
        "south, those ones have become a pack of their own: the bloodsnout worgs.$B$BEat four. Your wolf will know "
        "its own future when it tastes it.",
        "Devour 4 Bloodsnout Worgs along the Greymane Wall in Silverpine Forest.",
        "Four bloodsnouts. They run behind; you run faster.",
        "Did it taste familiar? It should. That is what your wolf will be.$B$BTake this.",
        objectives=[devour(4, "Bloodsnout Worg devoured", entries=[1923])], prev=b.id, sort=s,
        choices=[(3585, "Camouflaged Tunic"), (26023, "Ravager Hide Gloves"), (5757, "Hardwood Cudgel")],
        story="Hagatha's tale of the wolf that runs behind the pack: the Bloodsnout Worgs, the wolf's molt.")
    d = book.quest(
        9105153, "Fenris Isle", 18, 16, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha's voice turns sharp:$B$BOn Fenris Isle, in the lake, the Rot Hide gnolls dig up the "
        "dead and eat them. Somebody has to eat the Rot Hides, little horror; that is how the world stays tidy.$B$B"
        "Eat five of them. The dead they ate are a long way down, but a bat that drinks from them learns to "
        "drink from anything.",
        "Devour 5 Rot Hide gnolls on Fenris Isle in Silverpine Forest.",
        "Five Rot Hides. The isle is full of them.",
        "Tidy. I like tidy.$B$BTake this, little horror. You have earned it.",
        objectives=[devour(5, "Rot Hide devoured", entries=[1939, 1940, 1942, 1943])], prev=c.id, sort=s, xp=6,
        choices=[(3741, "Stomping Boots"), (17694, "Band of the Fist"), (1264, "Headbasher")],
        story="Hagatha keeps the world tidy: the grave-robbing Rot Hides of Fenris Isle.")
    return d


def ghostlands_quests(book, lantern):
    s = Z_GHOSTLANDS
    a = book.quest(
        9105160, "Ghostclaw", 12, 11, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha speaks, and the flame goes pale:$B$BThe lynxes of the Ghostlands starve, because "
        "the Scourge ate everything first. A starving cat is the most honest hunter there is. Eat six of them, "
        "little horror, the starving ones and the ghostclaws.",
        "Devour 6 Ghostclaw lynxes in the Ghostlands.",
        "Six cats. They are thin; you will have to be quick.",
        "Honest hunger. Remember the taste; you will meet the other kind soon enough.$B$BTake this.",
        objectives=[devour(6, "Ghostclaw lynx devoured", entries=[16347, 16348, 16349])], sort=s,
        choices=[(22998, "Ghostclaw Leggings"), (5299, "Gloves of the Moon"), (5279, "Harpy Skinner")],
        story="Hagatha teaches honest hunger: six Ghostclaw lynxes.")
    b = book.quest(
        9105161, "Mistbats", 14, 12, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha, almost fond:$B$BIn Tirisfal the bats grew fat on what the plague left behind. "
        "Here they are the same, only paler. The mistbats, and the vampiric ones that learned to drink. Eat six "
        "of them. A bat that drinks enough grows into something that drinks you.",
        "Devour 6 mistbats in the Ghostlands.",
        "Six bats. They are in the mist; so are you.",
        "Pale and thirsty. Your bat is thirsty too now.$B$BTake this.",
        objectives=[devour(6, "Mistbat devoured", entries=[16353, 16354, 16355])], prev=a.id, sort=s,
        choices=[(1306, "Wolfmane Wristguards"), (6480, "Slick Deviate Leggings"), (24351, "Mace of the Hand")],
        story="Hagatha's tale of the bats that learned to drink (the Vampiric Duskbat line).")
    c = book.quest(
        9105162, "Arcane Devourers", 13, 12, lantern, lantern, "hagatha",
        LANTERN_OPEN + "Hagatha, amused:$B$BAround the Sanctum of the Moon there are things the elves call arcane "
        "devourers. Devourers! As if a little ball of spilled magic knew what the word means. And mana shifters, "
        "who are worse at it.$B$BEat four of the devourers and three of the shifters, little horror. Show them "
        "what the word means.",
        "Devour 4 Arcane Devourers and 3 Mana Shifters at the Sanctum of the Moon in the Ghostlands.",
        "They are still calling themselves devourers.",
        "Now there is only one Devourer near the Sanctum of the Moon.$B$BTake this. Your wyrm drank well.",
        objectives=[devour(4, "Arcane Devourer devoured", entries=[16304]),
                    devour(3, "Mana Shifter devoured", entries=[16310])], prev=b.id, sort=s,
        choices=[(3585, "Camouflaged Tunic"), (26023, "Ravager Hide Gloves"), (2908, "Thornblade")],
        story="Hagatha mocks the 'Arcane Devourers': the Devourer shows them what the word means.")
    d = book.quest(
        9105163, "Spindleweb", 17, 15, lantern, lantern, "wren",
        LANTERN_OPEN + "Wren, from very far back in the lantern:$B$BSnack I'm not coming closer to the glass because "
        "your spiders are THIS big. The spindlewebs! They're everywhere down there. Hagatha says spiders are good "
        "for you. Hagatha is not the one who has to look at them.$B$BEat five. Quickly. Don't describe them to me.",
        "Devour 5 spindleweb spiders in the Ghostlands.",
        "Are they gone? Don't tell me what they look like.",
        "Are they gone? Really gone? Okay. Okay. I'm coming back to the glass.$B$BHere. You're very brave. I'm "
        "very brave too, for not screaming.",
        objectives=[devour(5, "Spindleweb spider devoured", entries=[16350, 16351, 16352])], prev=c.id, sort=s,
        xp=6,
        choices=[(3741, "Stomping Boots"), (16990, "Spritekin Cloak"), (1264, "Headbasher")],
        story="Wren hides from the huge spindleweb spiders; the Devourer eats them.")
    return d
