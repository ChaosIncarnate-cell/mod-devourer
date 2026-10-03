# 016 — Bug fixes from the owner's first test of 011-015

Status: open. Base: branch `task/006-007-devourer-start` (0befb0a). Branch: `task/016-bugfixes`.
Read `CLAUDE.md` first. Fix only these; no new features. Windows/MSVC builds this: never use `small`, `near`,
`far`, `min`/`max` as bare identifiers (Windows header macros).

## Bugs (owner tested in game, 2026-10-03)
1. **Devouring the pet's kills fails** with "You must have slain it yourself." (`Mgr::CanDevour`, DevourerMgr.cpp
   ~407: `isTappedBy(player)` / `hasLootRecipient()`). Fix: remember every creature killed by the Devourer, its
   pet, hatchlings or echoes (`Mgr::OnCreatureDeath` knows the owner) in the per-character state (bounded, e.g.
   last 200 GUIDs) and accept those in CanDevour.
2. **Devouring gives no Anima**, while fighting / being hit does. `Mgr::Devour` → `OnMeal` → `GainAnima`
   (+HungerPerMeal 30) looks right; find why it does not show. Check the out-of-combat rage decay: the hidden
   passive "Anima" 9100993 (aura 94 SPELL_AURA_INTERRUPT_REGEN) must be present on the player (learned AND the aura
   applied; if missing, `TeachBasics` should AddAura it), and nothing else may reset POWER_RAGE (core
   `Unit::setPowerType` sets rage to 0 whenever the power type is set). Add a LOG_DEBUG("module", ...) in GainAnima.
3. **Shape's Stride** (9100994, `tools/start_kit.py` STRIDE, cloned from Sprint 2983) shows Sprint's visual: remove
   the visual (SpellVisualID_1/2 = 0). Owner's wish if possible: instead leave **purple-blue glowing footprints**
   on the ground while moving in a shape (a stock 3.3.5a visual/spell; if none fits, just no visual).
4. **In-Between:** remove the **big blue crystal in the middle** of the ritual area (the player gets stuck on it;
   `tools/witch_sisters.py` ritual spawns, task 014); make the magic circle **more transparent / subtle**.
5. **The sisters do not channel** at the Devourer on arrival (they talk). Make the channel visible: a stock channel
   spell cast by each sister at the player (creature must face and be in range; check the creature AI path that is
   supposed to do it in DevourerSisters.cpp).
6. **Hatch Brood makes the pet disappear.** The hatchlings' summon (SummonGuardianProperties / SummonCreature in
   DevourerSpecs.cpp) must not use the pet slot; the hunter-like pet stays.
7. **Hatchlings are very loud** when several make noise at once (emotes/sounds overlap): stagger them or let only
   one of them make the sound (incl. the pet-and-hatchlings cheer from task 015).
8. **Sniff (9100995) does nothing visible.** Debug the whole path (server scan in DevourerSniff.cpp, the addon
   message, DevourerMenu.lua markers on nameplates / target frame). It must work without enabling nameplates by
   hand (if markers need nameplates, show them another way or turn nameplates on while Sniff is on).

## Done when
Each bug has a fix and a line in the PR saying how the owner checks it in game.
