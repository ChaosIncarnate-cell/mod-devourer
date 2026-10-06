"""Fill tools/quest_heights.json for every spawn written with z 0.0, and check the given z of the others.
Terrain height from the server's .map files; inside cities (WMO floors the .map does not have) the nearest stock
creature's z wins when it is far from the terrain."""
import sys, json, math, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import devourer_quests as dq, devourer_quests_content as dc, mount_quests as mq
import wq
# census.json: the stock creatures' spawn points (entry, name, zone, pts), written from the world database by hand;
# not in the repo. Without it the tool uses the terrain only (wrong inside cities with their own floors).
CENSUS = os.environ.get("QUEST_CENSUS", os.path.join(HERE, "census.json"))
C = json.load(open(CENSUS)) if os.path.exists(CENSUS) else []
pts = []
for c in C:
    for p in c['pts']:
        pts.append((p[0], p[1], p[2], c['zone'], c['name']))


def near_npc(mp, x, y, r=25.0):
    names = {z[2] for z in wq.zones() if z[0] == mp}
    best = None
    for px, py, pz, zn, name in pts:
        if zn not in names:
            continue                      # the census has no map: its zone keeps other continents out
        d = math.hypot(px - x, py - y)
        if d < r and (best is None or d < best[0]):
            best = (d, pz, name)
    return best


books = []
for block, mod in ((dq.LANTERNS, dc), (dq.MOUNTS, mq)):
    b = dq.Book(block); mod.build(b); books.append(b)
out = {}
problems = 0
for book in books:
    for kind, objs in (('thing', book.things), ('beast', book.beasts)):
        for o in objs:
            for (m, x, y, z, ori) in o.spawns:
                if m == 35:
                    continue
                g = wq.ground(m, x, y)
                npc = near_npc(m, x, y)
                gz = g[0] if g else None
                water = g[2] if g else None
                if z == 0.0:
                    use = gz
                    why = 'terrain'
                    if npc and (gz is None or (abs(npc[1] - gz) > 4 and npc[0] <= 12)):
                        use, why = round(npc[1], 2), f'npc {npc[2]} {npc[0]:.0f}yd'
                    if use is None:
                        print('!! no height', kind, o.key, m, x, y); problems += 1; continue
                    out[f"{m} {x} {y}"] = round(use, 2)
                    flag = ''
                    if water is not None and water > use + 1.0: flag += f' WATER {water:.1f}'
                    if g and g[1] > 1.0 and why == 'terrain': flag += f' slope {g[1]:.1f}'
                    if flag or why != 'terrain':
                        print(f'   {kind} {o.key} {m} {x} {y} -> {use} ({why}){flag}')
                        if 'WATER' in flag: problems += 1
                else:
                    ref = gz if not (npc and gz is not None and abs(npc[1] - gz) > 4) else npc[1]
                    if ref is None or abs(ref - z) > 2.0:
                        print(f'!! {kind} {o.key} {m} {x} {y} z {z} vs ground {gz} npc {npc and round(npc[1], 1)}')
                        problems += 1
json.dump(out, open(os.path.join(os.path.dirname(HERE), 'quest_heights.json'), 'w'), indent=0, sort_keys=True)
print(len(out), 'heights; problems', problems)
