/*
 * mod-devourer: the Devourer's pet (task 015).
 * Released under GNU AGPL v3, like AzerothCore.
 *
 * Concentrate is gone; the Devourer tames a beast, like a hunter. The core's own pet code does all of it (tame, call,
 * dismiss, revive, mend, feed, the pet bar and frame, the stable master) as soon as the Devourer answers "yes, a
 * hunter" to CLASS_CONTEXT_PET (devourer_player::OnPlayerIsClass); no core change. Here is only what the Devourer
 * adds, small and in its own voice:
 *   - the pet's kills feed Anima (what Concentrate used to give)
 *   - a meal is shared: when the Devourer devours near its pet, the pet eats too and the Devourer earns a half share
 *     of Bio Points more
 *   - the pet whimpers when the Devourer eats something big
 *   - the pet takes on a hint of the worn shape's size
 *   - the pet and the Brood's hatchlings play
 */

#include "Devourer.h"
#include "DevourerSpellIds.h"

#include "Creature.h"
#include "Pet.h"
#include "Player.h"
#include "SpellInfo.h"
#include "SpellMgr.h"
#include "Util.h"
#include <algorithm>
#include <cmath>
#include <string>

namespace Devourer
{
    namespace
    {
        constexpr float MealReach = 25.0f;               // how near the pet must be to share a meal
        constexpr uint32 KillAnima = 5;
        constexpr uint8 GreyLevelGap = 8;                // a kill this far under the Devourer's level is not a meal
    }

    // The hunter's pet spells for every Devourer, new and older characters alike; and Concentrate, which the pet replaces,
    // goes (its button becomes Call Pet).
    void Mgr::TeachPet(Player* player)
    {
        for (uint32 spellId : PetSpells)
            if (!player->HasSpell(spellId) && sSpellMgr->GetSpellInfo(spellId))
                player->learnSpell(spellId);
        // Pet Bond: the pet spells cost a Devourer no mana (a hidden spell modifier on the hunter's spell family).
        if (!player->HasSpell(SpellPetBond) && sSpellMgr->GetSpellInfo(SpellPetBond))
            player->learnSpell(SpellPetBond);
        if (player->HasSpell(SpellConcentrateOld))
        {
            if (ReplaceButtons(player, SpellConcentrateOld, SpellCallPet))
                player->SendActionButtons(1);
            player->removeSpell(SpellConcentrateOld, SPEC_MASK_ALL, false);
        }
    }

    // What the pet kills feeds the Devourer (the pet's own kills, not the Devourer's).
    void Mgr::OnPetKill(Player* player, Creature* victim)
    {
        if (!victim || victim->GetLevel() + GreyLevelGap < player->GetLevel())
            return;
        GainAnima(player, KillAnima);
    }

    // A shared meal: the pet eats too (and mends a little), and the Devourer earns half the Bio Points again.
    // Something big (an elite, a far higher level, or a whole swallow) makes the pet whimper.
    void Mgr::PetShareMeal(Player* player, Creature const* meal, bool big)
    {
        Pet* pet = player->GetPet();
        if (!pet || !pet->IsAlive() || !meal || !pet->IsWithinDist(meal, MealReach))
            return;
        pet->HandleEmoteCommand(EMOTE_ONESHOT_EAT_NO_SHEATHE);
        pet->ModifyHealth(int32(pet->CountPctFromMaxHealth(20)));
        GainBio(player, meal, 0.5f);
        if (big)
        {
            ObjectGuid const guid = pet->GetGUID();
            Defer(player, [this, player, guid]()
            {
                Pet* whimper = player->GetPet();
                if (!whimper || whimper->GetGUID() != guid || !whimper->IsAlive())
                    return;
                whimper->HandleEmoteCommand(EMOTE_ONESHOT_CRY);
                Tell(player, "Your " + whimper->GetName() + " whimpers: that was a big one.");
            });
        }
        else
            Tell(player, "Your " + pet->GetName() + " shares the meal.");
    }

    // The brood and the pet: hatchlings come out, the pet is glad of them.
    void Mgr::PetPlay(Player* player)
    {
        Pet* pet = player->GetPet();
        if (!pet || !pet->IsAlive())
            return;
        pet->HandleEmoteCommand(EMOTE_ONESHOT_CHEER);
        for (Creature* hatchling : Mine(player, NpcHatchling, 30.0f))
            hatchling->HandleEmoteCommand(EMOTE_ONESHOT_CHEER);
    }

    // The pet takes on a hint of the worn shape's size: a quarter of the way there, never under 0.9 or over 1.3.
    void Mgr::SyncPet(Player* player, State& state)
    {
        Pet* pet = player->GetPet();
        if (!pet || !pet->IsAlive())
        {
            state.PetSeen.Clear();
            return;
        }
        Shape const* worn = FindShape(state.Worn);
        float const factor = worn ? std::clamp(1.0f + 0.25f * (worn->Scale - 1.0f), 0.9f, 1.3f) : 1.0f;
        if (state.PetSeen == pet->GetGUID() && std::fabs(state.PetScale - factor) < 0.01f)
            return;
        state.PetSeen = pet->GetGUID();
        state.PetScale = factor;
        pet->RecalculateObjectScale();
        if (std::fabs(factor - 1.0f) > 0.01f)
            pet->SetObjectScale(pet->GetObjectScale() * factor);
    }
}
