# The Devourer's pet (task 015)

Owner, 2026-10-03: *Concentrate goes; the Devourer gets a pet like the hunter, "and maybe add some nice
interactions".* Brood's hatchlings are separate from the pet.

## What the Devourer has now

Taught from level 1 (new characters from `playercreateinfo_spell_custom`, every character at login by
`Mgr::TeachPet`); all are the stock 3.3.5a hunter spells, so the client already has their icons and texts:

| Spell | Id | |
|---|---|---|
| Tame Beast | 1515 | tame a beast no higher than your level (20 sec channel) |
| Call Pet | 883 | on the default bars (button 2, where Concentrate was) |
| Dismiss Pet | 2641 | |
| Revive Pet | 982 | |
| Mend Pet | 136 | |
| Feed Pet | 6991 | the usual pet food |
| Beast Lore | 1462 | |

Plus the hidden **Pet Bond** (9101047): a spell modifier on the hunter's spell family, -100% cost, so Revive Pet and
Mend Pet cost a Devourer no mana (a Devourer has none). They sit on the Devourer's spellbook tab (`tools/spellbook.py`).

The stable master works for a Devourer; the pet bar and pet frame are the game's own.

## No core change

The core already asks `Player::IsClass(CLASS_HUNTER, CLASS_CONTEXT_PET)` everywhere pets are tamed, called,
stabled or given hunter stats (`Pet::InitStatsForLevel`, `Spell::EffectTameCreature`, `EffectSummonPet`,
`EffectCreateTamedPet`, `Player::GetStableMaster` gossip ...), and the module answers that question
(`devourer_player::OnPlayerIsClass`: yes, for a Devourer, in that context only). The core patch stays as it was, still
dormant without class-10 characters. Not covered: the character-select screen shows no pet portrait for a Devourer
(`Player::BuildEnumData` checks the class directly; cosmetic).

## Anima instead of Concentrate

Concentrate gave +30 Anima every 30 seconds. Instead:
- **the pet's kills feed Anima**: +5 for each kill of the pet (not for grey ones),
- **a swing gives 3 Anima, not 2** (`Devourer.HungerPerSwing`, config),
- devouring still gives 30 (`Devourer.HungerPerMeal`).
Strong abilities cost Anima as before; the new spec abilities and active talents are listed in `docs/talents.md`.

## Interactions (the Devourer's voice; say yes or no to each)

1. **Shared meal.** When the Devourer devours (or swallows whole) within 25 yards of its pet, the pet eats too (eat
   emote, mends 20%) and the Devourer earns **half the Bio Points again** for that meal ("+N BP, a shared meal").
2. **Whimper.** If the meal is something big (an elite, three levels over the Devourer, or any Devour Whole), the pet
   whimpers a moment later ("Your <pet> whimpers: that was a big one.").
3. **A hint of the worn shape.** The pet's size follows the worn shape by a quarter of the way (never under 0.9 or
   over 1.3 of its own size): a big shape makes the pet a little bigger.
4. **Play.** When Hatch Brood hatches, the pet and the hatchlings cheer (emote) together; they never fight or
   ignore each other (they are friends).

## Not done / to check in game

- **Pet talents**: whether the client shows the pet talent window for class 10 is a client question (`HasPetUI`).
  If it does not, nothing on the server side can change that.
- **Pet damage**: hunter pets scale with the owner's *ranged* attack power; a Devourer has no ranged weapon, so check
  that the pet hits for something sensible, or tell me the number you want.
- `Revive Pet` / `Mend Pet` cost mana in the stock data; **Pet Bond** is meant to zero that. If either still says "Not
  enough mana", tell me.
