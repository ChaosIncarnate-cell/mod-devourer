/*
 * mod-devourer: what each specialization adds to the shapes.
 * Released under GNU AGPL v3, like AzerothCore.
 *
 *   Glutton      Devour Whole (swallow a weakened enemy, heal, one of its abilities bursts out), Gorged stacks
 *                (bigger and tougher with every meal), a meal buff chosen by what was eaten.
 *   Skinchanger  leaving a shape in combat leaves its echo fighting for a few seconds; faster shifting.
 *   Brood        Hatch Brood (two hatchlings in the worn shape's kin); hatchlings devour what dies near them and feed
 *                their mother; Devour on one of your own hatchlings eats it back.
 */

#include "Devourer.h"
#include "DevourerSpellIds.h"
#include "DevourerTalentIds.h"

#include "Creature.h"
#include "CreatureAI.h"
#include "DBCStores.h"
#include "Player.h"
#include "SpellInfo.h"
#include "SpellMgr.h"
#include "TemporarySummon.h"
#include "Spell.h"
#include "Util.h"
#include "GridNotifiers.h"
#include "GridNotifiersImpl.h"
#include "CellImpl.h"
#include "MotionMaster.h"
#include "ObjectAccessor.h"
#include "SpellAuras.h"
#include "Timer.h"
#include <algorithm>
#include <cmath>
#include <list>
#include <string>

namespace Devourer
{
    namespace
    {
        constexpr uint32 SyncInterval = 3000;
        constexpr uint32 EchoDuration = 8000;
        constexpr uint32 PupDuration = 6000;             // task 009: Pack Prowess
        constexpr uint32 SummonGuardianProperties = 61;
        constexpr float BroodReach = 40.0f;
        constexpr uint8 DevourWholeLevelGap = 5;
        constexpr float DevourWholeHealthPct = 25.0f;

        struct SpecSpell
        {
            uint32 Spec;
            uint32 Spell;
            uint8 MinLevel;
        };

        // Each spec's identity passive (on CoA the first entry of its tree) and its abilities.
        // ChaosCore0.3: Devour Whole is a Glutton talent now (the talent tree teaches it), no longer handed out.
        // The spec abilities at 20/40/60 come from tools/placeholders.py (DevourerTalentIds.h; task 015 made them real).
        constexpr SpecSpell SpecSpells[] =
        {
            { SpecGlutton,     SpellIdentityGlutton,         1 },
            { SpecSkinchanger, SpellIdentitySkinchanger,     1 },
            { SpecBrood,       SpellIdentityBrood,           1 },
            { SpecBrood,       SpellHatchBrood,              1 },
            { SpecGlutton,     SpellIronGut,                 20 },
            { SpecGlutton,     SpellDevouringChallenge,      40 },
            { SpecGlutton,     SpellLastSupper,              60 },
            { SpecSkinchanger, SpellMimicStrike,             20 },
            { SpecSkinchanger, SpellSkinSwap,                40 },
            { SpecSkinchanger, SpellFormOfMany,              60 },
            { SpecBrood,       SpellCallTheClutch,           20 },
            { SpecBrood,       SpellFeedTheYoung,            40 },
            { SpecBrood,       SpellBroodSwarm,              60 },
        };

        constexpr uint32 GorgedDigestAfter = 6000;       // out of combat this long, Gorged melts a stack per tick
        constexpr uint32 GorgedHeldFor = 300000;          // Stretched Gut: 5 min
        constexpr uint32 StomachTime = 10000;             // Regurgitate: how long the swallowed ability stays in
        constexpr uint32 StomachTimeStretched = 20000;    // with Stretched Gut
        constexpr float FeastReach = 10.0f;
        constexpr float OverrunReach = 25.0f;
        constexpr float OverrunDash = 20.0f;
        constexpr float OverrunWidth = 3.0f;              // how close to the path an enemy must stand to be run over
        constexpr uint32 MealSpells[] = { SpellMealMeat, SpellMealFlesh, SpellMealEssence, SpellMealGrave,
                                          SpellMealDragon, SpellMealDemon };

        void Dress(Creature* summon, Player* owner, uint32 display, float healthShare, float minDmg, float maxDmg)
        {
            if (display)
                summon->SetDisplayId(display);
            uint32 const health = std::max<uint32>(1, uint32(owner->GetMaxHealth() * healthShare));
            summon->SetCreateHealth(health);
            summon->SetMaxHealth(health);
            summon->SetHealth(health);
            float const level = float(owner->GetLevel());
            summon->SetBaseWeaponDamage(BASE_ATTACK, MINDAMAGE, level * minDmg);
            summon->SetBaseWeaponDamage(BASE_ATTACK, MAXDAMAGE, level * maxDmg);
            summon->UpdateDamagePhysical(BASE_ATTACK);
            summon->SetFaction(owner->GetFaction());
        }

        void Engage(Creature* summon, Player* owner)
        {
            Unit* victim = owner->GetVictim();
            if (!victim || !summon->IsValidAttackTarget(victim))
                return;
            if (CreatureAI* ai = summon->AI())
                ai->AttackStart(victim);
        }
    }

    // --- spec abilities follow the active specialization -------------------------------------------------

    void Mgr::OnUpdate(Player* player, uint32 diff)
    {
        if (!IsDevourer(player))
            return;
        State& state = Get(player);
        KeepShapeShown(player, state);
        UpdateStomach(player, state, diff);
        UpdatePerks(player, state, diff);                // task 015: armour, damage ... that depend on a state
        if (state.SyncTimer > diff)
        {
            state.SyncTimer -= diff;
            return;
        }
        state.SyncTimer = SyncInterval;
        if (state.GrowthDirty)
            SaveGrowth(player);
        if (state.CocoonUsed && !player->IsInCombat())
            state.CocoonUsed = false;                    // task 009: Cocoon Metamorphosis, once per fight
        if (state.SyncedSpec != SpecOf(player) || state.SyncedLevel != player->GetLevel())
            SyncSpecSpells(player);
        SyncTalentSpells(player);                        // talents can change at any time, not only with the spec
        DigestGorged(player, state);
        SyncBrood(player, state);                        // task 015: Brood Mother, Queen of the Brood
        SyncPet(player, state);                          // task 015: the pet takes on a hint of the worn shape's size
    }

    void Mgr::SyncSpecSpells(Player* player)
    {
        if (!IsDevourer(player))
            return;
        State& state = Get(player);
        uint32 const spec = SpecOf(player);
        state.SyncedSpec = spec;
        state.SyncedLevel = player->GetLevel();
        for (SpecSpell const& entry : SpecSpells)
        {
            if (!sSpellMgr->GetSpellInfo(entry.Spell))
                continue;
            bool const wanted = entry.Spec == spec && player->GetLevel() >= entry.MinLevel;
            if (wanted && !player->HasSpell(entry.Spell))
                player->learnSpell(entry.Spell);
            else if (!wanted && player->HasSpell(entry.Spell))
                player->removeSpell(entry.Spell, SPEC_MASK_ALL, false);
        }
    }

    // --- Glutton ------------------------------------------------------------------------------------------

    bool Mgr::CanDevourWhole(Player* player, Unit* target, std::string& why) const
    {
        Creature* victim = target ? target->ToCreature() : nullptr;
        if (!victim || !victim->IsAlive() || !player->IsValidAttackTarget(victim))
        {
            why = "Only a living enemy can be swallowed whole.";
            return false;
        }
        if (victim->isWorldBoss() || victim->IsDungeonBoss() || victim->GetCreatureTemplate()->rank >= CREATURE_ELITE_RAREELITE)
        {
            why = "It is far too big to swallow.";
            return false;
        }
        bool const weakened = victim->GetHealthPct() <= DevourWholeHealthPct;
        bool const outmatched = !victim->isElite() && victim->GetLevel() + DevourWholeLevelGap <= player->GetLevel();
        if (!weakened && !outmatched)
        {
            why = "Weaken it first (below 25% health).";
            return false;
        }
        return true;
    }

    void Mgr::DevourWhole(Player* player, Creature* victim)
    {
        // Its own abilities, remembered before it dies.
        std::vector<uint32> abilities;
        for (uint32 spellId : victim->m_spells)
            if (SpellInfo const* info = sSpellMgr->GetSpellInfo(spellId))
                if (!info->IsPassive() && !info->HasEffect(SPELL_EFFECT_SUMMON) && !info->HasEffect(SPELL_EFFECT_TELEPORT_UNITS))
                    abilities.push_back(spellId);

        std::string const name = victim->GetName();
        if (!victim->hasLootRecipient())
            victim->SetLootRecipient(player);
        Unit::Kill(player, victim);

        State& state = Get(player);
        state.Eaten.insert(victim->GetGUID());
        player->HandleEmoteCommand(EMOTE_ONESHOT_EAT_NO_SHEATHE);
        OnMeal(player, victim, true);                    // task 015: Anima, talents, the pet whimpers
        player->CastSpell(player, SpellSated, true);
        FeedGlutton(player, victim);
        if (uint8 const r = Rank(player, TalUnendingMeal))           // Unending Meal: and a heal at once
            player->ModifyHealth(int32(player->CountPctFromMaxHealth(5 * r)));
        if (uint8 const r = Rank(player, TalCrushingJaw))            // Crushing Jaw: the others stand stunned
        {
            Acore::AnyUnfriendlyUnitInObjectRangeCheck check(player, player, 8.0f);
            std::list<Unit*> around;
            Acore::UnitListSearcher<Acore::AnyUnfriendlyUnitInObjectRangeCheck> searcher(player, around, check);
            Cell::VisitObjects(player, searcher, 8.0f);
            for (Unit* enemy : around)
                if (enemy != victim && enemy->IsAlive() && player->IsValidAttackTarget(enemy))
                    StunFor(player, enemy, uint32(1500 * r));
        }

        uint32 const spellId = abilities.empty() ? 0 : Acore::Containers::SelectRandomContainerElement(abilities);
        // ChaosCore0.3, Regurgitate (talent): the ability stays in. Devour Whole becomes Regurgitate until it is
        // released, or it bursts out by itself when the time is up (and the Devourer is Digested).
        if (player->HasSpell(SpellTalentRegurgitate) && sSpellMgr->GetSpellInfo(SpellRegurgitate))
        {
            if (state.StomachFull)
                ReleaseStomach(player, false);           // one meal at a time: the older one comes up first
            state.StomachFull = true;
            state.StomachSpell = spellId;
            state.StomachLeft = player->HasSpell(SpellTalentStretchedGut) ? StomachTimeStretched : StomachTime;
            if (!player->HasSpell(SpellRegurgitate))
                player->learnSpell(SpellRegurgitate, true);
            if (ReplaceButtons(player, SpellDevourWhole, SpellRegurgitate))
                player->SendActionButtons(1);
            EatShape(player, victim, "You swallow " + name + " whole and hold it in. Regurgitate within " +
                std::to_string(state.StomachLeft / 1000) + " sec.");
            return;
        }

        if (spellId)
        {
            SpellInfo const* info = sSpellMgr->GetSpellInfo(spellId);
            Unit* target = player;
            if (!info->IsPositive())
            {
                target = player->GetVictim();
                if (!target || !target->IsAlive())
                    target = player->SelectNearbyTarget(nullptr, 30.0f);
            }
            if (target)
            {
                if (uint8 const r = Rank(player, TalDigestiveFire))   // Digestive Fire: it hits harder
                    CastScaled(player, target, spellId, 1.0f + 0.15f * r);
                else
                    player->CastSpell(target, spellId, true);
                Tell(player, "Its " + std::string(info->SpellName[0] ? info->SpellName[0] : "power") + " bursts out of you.");
            }
        }

        EatShape(player, victim, "You swallow " + name + " whole.");
    }

    void Mgr::FeedGlutton(Player* player, Creature const* meal)
    {
        if (SpecOf(player) != SpecGlutton || !meal)
            return;

        // One more stack of Gorged: bigger, tougher. The worn shape's favourite food counts twice.
        State& state = Get(player);
        Shape const* worn = FindShape(state.Worn);
        bool const favourite = worn && IsFavouriteFood(worn->Id, meal);
        player->CastSpell(player, SpellGorged, true);
        if (favourite)
        {
            player->CastSpell(player, SpellGorged, true);
            Tell(player, "Your " + worn->Name + " body loves that meal: Gorged twice.");
        }
        if (Aura* gorged = player->GetAura(SpellGorged))              // task 015: Belly of the Beast, Stomach of Stone
            if (gorged->GetStackAmount() > GorgedCap(player))
                gorged->SetStackAmount(GorgedCap(player));
        state.GorgedIdle = 0;

        // What was eaten decides the meal (ChaosCore0.3: Zack's list). Machines give only Indigestion.
        uint32 buff = SpellMealEssence;
        switch (meal->GetCreatureType())
        {
            case CREATURE_TYPE_BEAST:
            case CREATURE_TYPE_CRITTER:
                buff = SpellMealMeat;
                break;
            case CREATURE_TYPE_HUMANOID:
            case CREATURE_TYPE_GIANT:
                buff = SpellMealFlesh;
                break;
            case CREATURE_TYPE_UNDEAD:
                buff = SpellMealGrave;
                break;
            case CREATURE_TYPE_DRAGONKIN:
                buff = SpellMealDragon;
                break;
            case CREATURE_TYPE_DEMON:
                buff = SpellMealDemon;
                break;
            case CREATURE_TYPE_MECHANICAL:
                player->CastSpell(player, SpellIndigestion, true);
                Tell(player, "Gears and bolts do not agree with you.");
                return;
            default:
                break;
        }
        player->RemoveAurasDueToSpell(SpellDigested);    // Digested lets go of the old meal before it changes
        bool const grand = Rank(player, TalGrandAppetite) > 0;       // task 015: the buff before this one stays too
        for (uint32 other : MealSpells)
            if (other != buff && !(grand && other == state.LastMealSpell))
                player->RemoveAurasDueToSpell(other);
        player->CastSpell(player, buff, true);
        if (grand)
            if (Aura* meal = player->GetAura(buff))
            {
                meal->SetMaxDuration(30 * 60 * 1000);
                meal->SetDuration(30 * 60 * 1000);
            }
        state.LastMealSpell = buff;
        if (buff == SpellMealDragon)
            player->CastSpell(player, SpellMealDragonBreath, true);   // the dragon breathes out of you
    }

    // --- ChaosCore0.3: the Glutton's talents -----------------------------------------------------------------

    uint32 Mgr::FavouriteFood(uint32 shapeId) const
    {
        auto diet = _diet.find(shapeId);
        if (diet == _diet.end())
            return 0;
        uint32 best = 0, bestBp = 0;
        for (auto const& [type, bp] : diet->second)
            if (type && bp > bestBp)
            {
                best = type;
                bestBp = bp;
            }
        return best;
    }

    // Task 009: devourer_favourite_food decides when the shape has rows (creature type, family, a part of the
    // name: every field a row sets must match); otherwise the diet's best creature type, as before.
    bool Mgr::IsFavouriteFood(uint32 shapeId, Creature const* meal) const
    {
        if (!meal)
            return false;
        auto itr = _food.find(shapeId);
        if (itr == _food.end() || itr->second.empty())
        {
            uint32 const type = FavouriteFood(shapeId);
            return type && meal->GetCreatureType() == type;
        }
        std::string name = meal->GetName();
        std::transform(name.begin(), name.end(), name.begin(), [](unsigned char ch) { return std::tolower(ch); });
        uint32 const family = meal->GetCreatureTemplate()->family;
        for (FoodRule const& rule : itr->second)
        {
            if (rule.Type && rule.Type != meal->GetCreatureType())
                continue;
            if (rule.Family && rule.Family != family)
                continue;
            if (!rule.NamePart.empty() && name.find(rule.NamePart) == std::string::npos)
                continue;
            return true;
        }
        return false;
    }

    bool Mgr::ReplaceButtons(Player* player, uint32 from, uint32 to)
    {
        bool changed = false;
        for (uint8 slot = 0; slot < MAX_ACTION_BUTTONS; ++slot)
        {
            ActionButton const* button = player->GetActionButton(slot);
            if (!button || button->GetType() != ACTION_BUTTON_SPELL || button->GetAction() != from)
                continue;
            player->addActionButton(slot, to, ACTION_BUTTON_SPELL);
            changed = true;
        }
        return changed;
    }

    // Quick Devour (talent) is a second Devour spell: 1 sec, not broken by damage. Whichever fits is known and on
    // the bars; the other one is taken away.
    void Mgr::SyncTalentSpells(Player* player)
    {
        if (!IsDevourer(player))
            return;
        bool const quick = player->HasSpell(SpellTalentQuickDevour);
        uint32 const want = quick ? SpellDevourQuick : SpellDevour;
        uint32 const drop = quick ? SpellDevour : SpellDevourQuick;
        if (!sSpellMgr->GetSpellInfo(want))
            return;
        if (!player->HasSpell(want))
            player->learnSpell(want);
        if (player->HasSpell(drop))
        {
            if (ReplaceButtons(player, drop, want))
                player->SendActionButtons(1);
            player->removeSpell(drop, SPEC_MASK_ALL, false);
        }
    }

    // Gorged lasts through the fight. Out of combat it melts away, a stack every few seconds; Stretched Gut holds
    // the stacks for 5 min first.
    void Mgr::DigestGorged(Player* player, State& state)
    {
        Aura* gorged = player->GetAura(SpellGorged);
        if (!gorged || player->IsInCombat())
        {
            state.GorgedIdle = 0;
            return;
        }
        state.GorgedIdle += SyncInterval;
        uint32 const hold = player->HasSpell(SpellTalentStretchedGut) ? GorgedHeldFor :
            GorgedDigestAfter + 20000u * Rank(player, TalThickGullet);   // task 015: Thick Gullet
        if (state.GorgedIdle >= hold)
            gorged->ModStackAmount(-1);
    }

    void Mgr::UpdateStomach(Player* player, State& state, uint32 diff)
    {
        if (!state.StomachFull)
            return;
        if (state.StomachLeft > diff)
        {
            state.StomachLeft -= diff;
            return;
        }
        ReleaseStomach(player, true);
    }

    // Regurgitate: the swallowed ability comes out at the Devourer's target. Pressed, it is the Devourer's choice
    // of moment; run out, it bursts out by itself and the Devourer is Digested (or, with a Digested talent, gets
    // Thick Hide or Bile Coating instead).
    void Mgr::ReleaseStomach(Player* player, bool expired)
    {
        State& state = Get(player);
        if (!state.StomachFull)
            return;
        uint32 const spellId = state.StomachSpell;
        state.StomachFull = false;
        state.StomachSpell = 0;
        state.StomachLeft = 0;
        if (ReplaceButtons(player, SpellRegurgitate, SpellDevourWhole))
            player->SendActionButtons(1);
        if (player->HasSpell(SpellRegurgitate))
            player->removeSpell(SpellRegurgitate, SPEC_MASK_ALL, true);

        if (!player->IsAlive())
            return;
        if (SpellInfo const* info = spellId ? sSpellMgr->GetSpellInfo(spellId) : nullptr)
        {
            Unit* target = player;
            if (!info->IsPositive())
            {
                target = player->GetVictim();
                if (!target || !target->IsAlive())
                    target = player->GetSelectedUnit();
                if (!target || !target->IsAlive() || !player->IsValidAttackTarget(target))
                    target = player->SelectNearbyTarget(nullptr, 30.0f);
            }
            if (target)
            {
                if (uint8 const r = Rank(player, TalDigestiveFire))   // task 015: Digestive Fire
                    CastScaled(player, target, spellId, 1.0f + 0.15f * r);
                else
                    player->CastSpell(target, spellId, true);
                Tell(player, "Its " + std::string(info->SpellName[0] ? info->SpellName[0] : "power") +
                    (expired ? " bursts out of you." : " comes up."));
            }
        }
        if (!expired)
            return;
        if (player->HasSpell(SpellTalentThickHide))
            player->CastSpell(player, SpellDigestedThickHide, true);
        else if (player->HasSpell(SpellTalentBileCoating))
            player->CastSpell(player, SpellDigestedBileCoating, true);
        else
            player->CastSpell(player, SpellDigested, true);
    }

    // Feast (talent): Devour eats every slain creature around the first one.
    void Mgr::Feast(Player* player, Creature* first)
    {
        std::list<Creature*> corpses;
        Acore::AllDeadCreaturesInRange check(first, FeastReach, true);   // true: skip the living
        Acore::CreatureListSearcher<Acore::AllDeadCreaturesInRange> searcher(first, corpses, check);
        Cell::VisitObjects(first, searcher, FeastReach);
        uint32 eaten = 0;
        for (Creature* corpse : corpses)
        {
            std::string why;
            if (!CanDevour(player, corpse, why))
                continue;
            Get(player).Eaten.insert(corpse->GetGUID());
            if (corpse->loot.isLooted())
                corpse->DespawnOrUnsummon(1500ms);
            OnMeal(player, corpse, false);
            FeedGlutton(player, corpse);
            EatShape(player, corpse, "You also devour " + corpse->GetName() + ".");
            ++eaten;
        }
        if (eaten)
            Tell(player, "A feast: " + std::to_string(eaten + 1) + " meals at once.");
    }

    // --- ChaosCore0.3: the Baby Berserker ---------------------------------------------------------------------

    // Overrun's wind-up (a 0.5 sec cast) plays ReadySpellOmni. The cast is checked twice (start and finish):
    // the emote is played once per wind-up.
    void Mgr::OverrunWindup(Player* player)
    {
        State& state = Get(player);
        uint32 const now = getMSTime();
        if (state.OverrunWindup && getMSTimeDiff(state.OverrunWindup, now) < 1000)
            return;
        state.OverrunWindup = now;
        player->HandleEmoteCommand(EmoteReadySpellOmni);
    }

    // Overrun: run down the target (or 20 yards straight ahead) and knock over every enemy in the way. Rush (the
    // base kit) always runs straight ahead (chase = false) and knocks over with its own, lighter hit.
    void Mgr::Overrun(Player* player, uint32 hitSpell, bool chase, float extra)
    {
        Get(player).OverrunWindup = 0;
        if (hitSpell == SpellRushHit)                    // task 015: Wandering Skin takes Rush further, leaves an echo
            if (uint8 const r = Rank(player, TalWanderingSkin))
            {
                extra += 2.0f * r;
                if (Shape const* worn = FindShape(Get(player).Worn))
                    SpawnEcho(player, *worn, false, true);
            }
        uint32 const hit = hitSpell ? hitSpell : SpellBabyOverrunHit;
        Unit* target = chase ? player->GetSelectedUnit() : nullptr;
        if (target && (!target->IsAlive() || !player->IsValidAttackTarget(target) ||
                       !player->IsWithinDistInMap(target, OverrunReach) || !player->IsWithinLOSInMap(target)))
            target = nullptr;

        Position dest;
        if (target)
        {
            player->SetFacingToObject(target);
            float const dist = std::max(0.0f, player->GetExactDist2d(target) - target->GetCombatReach());
            dest = player->GetFirstCollisionPosition(dist, player->GetRelativeAngle(target));
        }
        else
            dest = player->GetFirstCollisionPosition(OverrunDash + extra, 0.0f);

        // Who stands in the way: enemies close to the line from here to the end of the run.
        float const sx = player->GetPositionX(), sy = player->GetPositionY();
        float const dx = dest.GetPositionX() - sx, dy = dest.GetPositionY() - sy;
        float const length = std::sqrt(dx * dx + dy * dy);
        std::list<Unit*> around;
        Acore::AnyUnfriendlyUnitInObjectRangeCheck check(player, player, length + OverrunWidth);
        Acore::UnitListSearcher<Acore::AnyUnfriendlyUnitInObjectRangeCheck> searcher(player, around, check);
        Cell::VisitObjects(player, searcher, length + OverrunWidth);

        std::vector<std::pair<float, ObjectGuid>> struck;  // distance along the run -> enemy
        for (Unit* unit : around)
        {
            if (!unit->IsAlive() || !player->IsValidAttackTarget(unit))
                continue;
            float const ux = unit->GetPositionX() - sx, uy = unit->GetPositionY() - sy;
            float along = length > 0.1f ? (ux * dx + uy * dy) / length : 0.0f;
            float const side = length > 0.1f ? std::fabs(ux * dy - uy * dx) / length : std::sqrt(ux * ux + uy * uy);
            if (unit == target || (along >= -1.0f && along <= length + OverrunWidth &&
                                   side <= OverrunWidth + unit->GetCombatReach() * 0.5f))
                struck.emplace_back(std::max(0.0f, std::min(along, length)), unit->GetGUID());
        }

        player->GetMotionMaster()->MoveCharge(dest.GetPositionX(), dest.GetPositionY(), dest.GetPositionZ());
        for (auto const& [along, guid] : struck)
        {
            ObjectGuid const victimGuid = guid;
            uint32 const delay = uint32(along / SPEED_CHARGE * 1000.0f) + 50;
            player->m_Events.AddEventAtOffset([player, victimGuid, hit]()
            {
                Unit* victim = ObjectAccessor::GetUnit(*player, victimGuid);
                if (victim && victim->IsAlive() && player->IsAlive() && player->IsValidAttackTarget(victim))
                    player->CastSpell(victim, hit, true);
            }, Milliseconds(delay));
        }
        if (target)
            player->Attack(target, true);
    }

    // Gnaw: one bite every second of the grapple.
    void Mgr::GnawBite(Unit* caster, Unit* target)
    {
        Player* player = caster ? caster->ToPlayer() : nullptr;
        if (!player || !player->IsAlive())
            return;
        int32 heal = int32(player->CountPctFromMaxHealth(4));
        if (Aura const* chewed = target ? target->GetAura(SpellBabyChewed, player->GetGUID()) : nullptr)
            if (chewed->GetStackAmount() >= 5)
                heal *= 2;                               // Teething: a well-chewed enemy feeds twice as well
        player->ModifyHealth(heal);
        player->ModifyPower(POWER_RAGE, 5 * 10);
    }

    // Void Frenzy: the roar (the spell's own visual) takes 0.9 sec, then five fast strikes.
    void Mgr::VoidFrenzy(Player* player, Unit* target)
    {
        ObjectGuid const victimGuid = target->GetGUID();
        for (uint32 i = 0; i < 5; ++i)
            player->m_Events.AddEventAtOffset([player, victimGuid]()
            {
                Unit* victim = ObjectAccessor::GetUnit(*player, victimGuid);
                if (!victim || !victim->IsAlive() || !player->IsAlive() || !player->IsValidAttackTarget(victim) ||
                    !player->IsWithinMeleeRange(victim))
                    return;
                player->SetFacingToObject(victim);
                player->CastSpell(victim, SpellBabyVoidFrenzyHit, true);
            }, Milliseconds(900 + i * 400));
    }

    // --- Brood --------------------------------------------------------------------------------------------

    // Hatch Brood's summon effect makes the guardians (fromSpell); the module dresses them: the worn shape's kin, and
    // what the Brood talents add. Task 015: Many Mouths (every second hatching) and Swollen Sac hatch more young than
    // the spell does; Queen of the Brood makes them large. Other callers (Endless Clutch, Brood Swarm ...) refill
    // the brood and only dress the new ones.
    void Mgr::OnBroodHatched(Player* player, bool fromSpell)
    {
        State& state = Get(player);
        Shape const* worn = FindShape(state.Worn);
        // The hatchlings take after the colouring worn (its own young when it has them), then the shape's kin.
        uint32 display = worn && worn->BroodDisplay ? worn->BroodDisplay : DefaultBroodDisplay;
        if (worn)
        {
            auto skin = _skins.find(ShownDisplay(player, *worn));
            if (skin != _skins.end() && skin->second.BroodDisplay)
                display = skin->second.BroodDisplay;
        }
        // An adult body worn by a hatchling is shrunk; a real young model or another kin keeps its size.
        bool const adult = worn && (display == worn->Display || _skins.count(display));
        bool const queen = Rank(player, TalQueenOfTheBrood) > 0;

        if (fromSpell)
        {
            ++state.HatchCount;
            uint32 extra = Rank(player, TalSwollenSac);
            if (state.HatchCount % 2 == 0)
                extra += Rank(player, TalManyMouths);
            uint32 const life = 20000 + 2000u * Rank(player, TalSwellingBrood);
            for (uint32 i = 0; i < extra; ++i)
            {
                Position pos = player->GetPosition();
                player->MovePositionToFirstCollision(pos, 2.0f, 0.6f + float(i) * 1.2f);
                player->SummonCreature(NpcHatchling, pos, TEMPSUMMON_TIMED_DESPAWN, life, 0,
                    sSummonPropertiesStore.LookupEntry(SummonGuardianProperties));
            }
        }

        for (Creature* hatchling : Mine(player, NpcHatchling))
        {
            if (!hatchling->IsAlive() || hatchling->GetDisplayId() == display)
                continue;                                // already dressed
            Dress(hatchling, player, display, 0.15f, 0.9f, 1.4f);
            TuneHatchling(player, hatchling, 0.15f, 0.9f, 1.4f, false);
            if (adult)
                hatchling->SetObjectScale(0.5f);
            if (queen)
                hatchling->SetObjectScale(hatchling->GetObjectScale() * 1.5f);
            Engage(hatchling, player);
        }
        if (fromSpell)
            PetPlay(player);                             // the pet is glad of them
    }

    bool Mgr::IsOwnHatchling(Player* player, Unit* unit) const
    {
        return unit && unit->IsAlive() && unit->GetEntry() == NpcHatchling && unit->GetOwnerGUID() == player->GetGUID();
    }

    void Mgr::Cannibalize(Player* player, Creature* hatchling)
    {
        hatchling->DespawnOrUnsummon();
        player->HandleEmoteCommand(EMOTE_ONESHOT_EAT_NO_SHEATHE);
        player->ModifyHealth(int32(player->CountPctFromMaxHealth(15)));
        player->ModifyPower(POWER_RAGE, 15 * 10);
        if (Rank(player, TalBloodMilk))                  // task 015: Blood Milk: and the strikes come faster
        {
            State& state = Get(player);
            state.BloodMilkUntil = getMSTime() + 10000;
            state.PerkTimer = 0;
        }
        Tell(player, "You eat one of your own hatchlings.");
    }

    void Mgr::OnCreatureDeath(Creature* victim, Unit* killer)
    {
        // Task 015: a hatchling dies: Twitching Eggs, Mother's Wrath, Endless Clutch.
        if (victim->GetEntry() == NpcHatchling)
            if (Player* owner = victim->GetCharmerOrOwnerPlayerOrPlayerItself())
                if (IsDevourer(owner))
                    OnHatchlingDeath(owner, victim);
        if (!killer || victim->GetEntry() == NpcHatchling || victim->GetEntry() == NpcEcho)
            return;
        Player* mother = killer->GetCharmerOrOwnerPlayerOrPlayerItself();
        if (!mother || !IsDevourer(mother))
            return;
        if (killer->IsPet())
            OnPetKill(mother, victim);                   // task 015: the pet's kills feed Anima

        State& state = Get(mother);
        if (state.Eaten.count(victim->GetGUID()))
            return;

        // Task 015, Worn Faces: for a while the Skinchanger's echo eats what dies near it, as a hatchling would.
        if (Active(state.WornFacesUntil, getMSTime()))
        {
            Creature* echo = nullptr;
            for (Creature* candidate : Mine(mother, NpcEcho, BroodReach))
                if (candidate->IsWithinDist(victim, BroodReach) && (!echo || candidate->GetDistance(victim) < echo->GetDistance(victim)))
                    echo = candidate;
            if (echo)
            {
                state.Eaten.insert(victim->GetGUID());
                echo->GetMotionMaster()->MovePoint(0, victim->GetPositionX(), victim->GetPositionY(), victim->GetPositionZ());
                echo->HandleEmoteCommand(EMOTE_ONESHOT_EAT_NO_SHEATHE);
                GainAnima(mother, 10);
                EatShape(mother, victim, "Your echo devours " + victim->GetName() + " and feeds you.");
                return;
            }
        }
        if (SpecOf(mother) != SpecBrood)
            return;

        std::list<Creature*> hatchlings = Mine(mother, NpcHatchling, BroodReach);
        Creature* eater = nullptr;
        for (Creature* hatchling : hatchlings)
            if (hatchling->IsAlive() && hatchling->IsWithinDist(victim, BroodReach) &&
                (!eater || hatchling->GetDistance(victim) < eater->GetDistance(victim)))
                eater = hatchling;
        if (!eater)
            return;

        state.Eaten.insert(victim->GetGUID());
        eater->GetMotionMaster()->MovePoint(0, victim->GetPositionX(), victim->GetPositionY(), victim->GetPositionZ());
        eater->HandleEmoteCommand(EMOTE_ONESHOT_EAT_NO_SHEATHE);
        GainAnima(mother, 10 + Rank(mother, TalNursingHunger));      // task 015: Nursing Hunger
        mother->ModifyHealth(int32(mother->CountPctFromMaxHealth(3)));
        if (uint8 const r = Rank(mother, TalHungryYoung))            // Hungry Young: it mends
            eater->ModifyHealth(int32(eater->CountPctFromMaxHealth(5 * r)));
        if (uint8 const r = Rank(mother, TalFeedingFrenzy))          // Feeding Frenzy: it runs faster for a while
        {
            ObjectGuid const guid = eater->GetGUID();
            float const was = eater->GetSpeedRate(MOVE_RUN);
            eater->SetSpeedRate(MOVE_RUN, was * (1.0f + 0.03f * r));
            mother->m_Events.AddEventAtOffset([mother, guid, was]()
            {
                if (Unit* young = ObjectAccessor::GetUnit(*mother, guid))
                    if (Creature* creature = young->ToCreature())
                        creature->SetSpeedRate(MOVE_RUN, was);
            }, Milliseconds(6000));
        }
        EatShape(mother, victim, "Your hatchlings devour " + victim->GetName() + " and feed you.");
    }

    // --- Skinchanger --------------------------------------------------------------------------------------

    // Task 015: Many Faces, Form of Many (longer echoes, two casts), Mimic's Eye, Borrowed Voice, Flicker Shape, Mirror
    // Hunger, Skin Hoard, Hollow Shell (a second, smaller echo) and Thousand Skins (an echo out of combat, three at most).
    void Mgr::SpawnEcho(Player* player, Shape const& shape, bool small, bool force)
    {
        State& state = Get(player);
        uint32 const now = getMSTime();
        bool const thousand = Rank(player, TalThousandSkins) > 0;
        if (!force && !thousand && (!player->IsInCombat() || !player->GetVictim()))
            return;
        if ((thousand || force) && Mine(player, NpcEcho).size() >= 3)
            return;

        bool const many = Active(state.ManyUntil, now);
        uint32 const duration = (many ? 14000u : EchoDuration) + 2000u * Rank(player, TalManyFaces);
        float const share = small ? 0.5f : 1.0f;
        float const power = (1.0f + 0.10f * Rank(player, TalMimicsEye)) * share;
        TempSummon* echo = player->SummonCreature(NpcEcho, player->GetPosition(), TEMPSUMMON_TIMED_DESPAWN, duration,
            0, sSummonPropertiesStore.LookupEntry(SummonGuardianProperties));
        if (!echo)
            return;

        Dress(echo, player, ShownDisplay(player, shape), 0.25f * share, 1.5f * power, 2.2f * power);
        if (small)
            echo->SetObjectScale(echo->GetObjectScale() * 0.7f);
        echo->AddAura(SpellGhostVisual, echo);
        Engage(echo, player);

        // The echo remembers the shape's first ability and throws it once (twice in Form of Many).
        Unit* victim = player->GetVictim();
        uint32 const kit = shape.Kit[0];
        if (victim && kit && sSpellMgr->GetSpellInfo(kit))
        {
            float const voice = (1.0f + 0.04f * Rank(player, TalBorrowedVoice)) * share;
            CastScaled(echo, victim, kit, voice, player->GetGUID());
            if (many)
            {
                ObjectGuid const echoGuid = echo->GetGUID(), victimGuid = victim->GetGUID();
                player->m_Events.AddEventAtOffset([this, player, echoGuid, victimGuid, kit, voice]()
                {
                    Unit* e = ObjectAccessor::GetUnit(*player, echoGuid);
                    Unit* v = ObjectAccessor::GetUnit(*player, victimGuid);
                    if (e && e->IsAlive() && v && v->IsAlive())
                        CastScaled(e, v, kit, voice, player->GetGUID());
                }, Milliseconds(1000));
            }
        }
        if (small)
            return;

        if (uint8 const r = Rank(player, TalFlickerShape))
            player->ModifyHealth(int32(player->CountPctFromMaxHealth(3 * r)));
        if (uint8 const r = Rank(player, TalMirrorHunger))
            if (victim && (victim->getPowerType() == POWER_MANA || victim->getPowerType() == POWER_RAGE) &&
                victim->GetPower(victim->getPowerType()) > 0)
            {
                victim->ModifyPower(victim->getPowerType(), -int32(3 * r * (victim->getPowerType() == POWER_RAGE ? 10 : 1)));
                GainAnima(player, 3 * r);
            }
        if (uint8 const r = Rank(player, TalSkinHoard))
            player->m_Events.AddEventAtOffset([this, player, r]()
            {
                if (player->IsAlive())
                    GainAnima(player, 4u * r);
            }, Milliseconds(duration));
        if (uint8 const r = Rank(player, TalHollowShell))
            if (player->GetHealthPct() >= (r >= 2 ? 80.0f : 99.9f))
                SpawnEcho(player, shape, true, true);
    }

    // --- task 009: starter forms batch 1 --------------------------------------------------------------------

    // Wolf, Pack Prowess: two spectral pups (the Skinchanger's translucent echo, in the worn wolf's look and half
    // its size) fight for 6 sec; each bites once at once (Pup Bite, a bleed that is the Devourer's own, so Ravaging
    // Feast can eat it).
    void Mgr::CallPups(Player* player, Unit* target)
    {
        if (!target || !target->IsAlive() || !player->IsValidAttackTarget(target))
            return;
        State& state = Get(player);
        Shape const* worn = FindShape(state.Worn);
        uint32 const display = worn ? ShownDisplay(player, *worn) : 0;
        for (uint8 i = 0; i < 2; ++i)
        {
            Position pos = player->GetPosition();
            player->MovePositionToFirstCollision(pos, 1.5f, i ? float(M_PI) / 2 : -float(M_PI) / 2);
            TempSummon* pup = player->SummonCreature(NpcEcho, pos, TEMPSUMMON_TIMED_DESPAWN, PupDuration, 0,
                sSummonPropertiesStore.LookupEntry(SummonGuardianProperties));
            if (!pup)
                continue;
            Dress(pup, player, display, 0.10f, 0.4f, 0.6f);
            pup->SetObjectScale(0.5f);
            pup->AddAura(SpellGhostVisual, pup);
            if (CreatureAI* ai = pup->AI())
                ai->AttackStart(target);
            pup->CastSpell(target, SpellWolfPupBite, true, nullptr, nullptr, player->GetGUID());
        }
    }

    // Moth, Cocoon Metamorphosis: a blow that would drop the moth below 25% health (or kill it) is stopped at 25%,
    // and the moth is wrapped in Silken Cocoon. Once per fight (reset out of combat in OnUpdate).
    bool Mgr::TryCocoon(Player* player, uint32 damage, uint32& absorb)
    {
        State& state = Get(player);
        if (state.CocoonUsed || !player->IsAlive() || !player->HealthBelowPctDamaged(25, damage))
            return false;
        state.CocoonUsed = true;
        uint32 const floor = uint32(player->CountPctFromMaxHealth(25));
        uint32 const health = uint32(player->GetHealth());
        absorb = health > floor ? damage - std::min(damage, health - floor) : damage;
        player->CastSpell(player, SpellMothSilkenCocoon, true);
        return true;
    }

    // --- Vashnik: Rising Serpents --------------------------------------------------------------------------

    // ChaosCore0.2: the serpents are looked up around the Vashnik (summoned by it), not only in its list of
    // controlled minions, so they are found (dressed in the Twinfangs model, and made to cast) however they were summoned.
    std::list<Creature*> Mgr::RisenSerpents(Player* player) const
    {
        std::list<Creature*> found;
        player->GetAllMinionsByEntry(found, NpcRisingSerpent);
        std::list<Creature*> nearby;                     // not "near": Windows headers define near as a macro
        player->GetCreatureListWithEntryInGrid(nearby, NpcRisingSerpent, 60.0f);
        for (Creature* c : nearby)
        {
            bool const mine = c->GetOwnerGUID() == player->GetGUID() || c->GetCreatorGUID() == player->GetGUID() ||
                (c->IsSummon() && c->ToTempSummon()->GetSummonerGUID() == player->GetGUID());
            if (mine && std::find(found.begin(), found.end(), c) == found.end())
                found.push_back(c);
        }
        return found;
    }

    void Mgr::OnSerpentsRisen(Player* player)
    {
        std::list<Creature*> serpents = RisenSerpents(player);
        uint8 next = 0;                                  // one of each colour
        for (Creature* serpent : serpents)
        {
            uint32 const display = RisingSerpentDisplays[next++ % 2];
            if (!serpent->IsAlive() || serpent->HasUnitState(UNIT_STATE_ROOT))
                continue;                                // already dressed (ChaosCore0.2: the database now gives
                                                         // them the Twinfangs model too, so the model is no test)
            Dress(serpent, player, display, 0.2f, 0.5f, 0.8f);
            serpent->SetReactState(REACT_PASSIVE);       // they cast with you, they do not wander
            serpent->SetControlled(true, UNIT_STATE_ROOT);
            serpent->GetMotionMaster()->Clear();
            serpent->SetFacingToObject(player->GetVictim() ? static_cast<WorldObject*>(player->GetVictim()) : player);
        }
    }

    // Every spell the Vashnik casts at an enemy, its risen serpents cast too (at the same enemy; a charm goes to
    // another enemy near it, so each serpent charms one more).
    void Mgr::MirrorSpell(Player* player, Spell const* spell)
    {
        SpellInfo const* info = spell->GetSpellInfo();
        if (!info || spell->IsTriggered() || info->IsPassive())
            return;
        State& state = Get(player);
        Shape const* worn = FindShape(state.Worn);
        if (!worn || std::find(worn->Kit.begin(), worn->Kit.end(), info->Id) == worn->Kit.end())
            return;
        if (info->HasEffect(SPELL_EFFECT_CHARGE) || info->HasEffect(SPELL_EFFECT_SUMMON))
            return;                                      // serpents do not move, and do not summon
        Unit* target = spell->m_targets.GetUnitTarget();
        if (!target || !player->IsValidAttackTarget(target))
            return;

        std::list<Creature*> serpents = RisenSerpents(player);
        bool const charm = info->HasAura(SPELL_AURA_TRANSFORM);
        std::list<Unit*> others;
        if (charm)
        {
            Acore::AnyUnfriendlyUnitInObjectRangeCheck check(target, player, 10.0f);
            Acore::UnitListSearcher<Acore::AnyUnfriendlyUnitInObjectRangeCheck> searcher(target, others, check);
            Cell::VisitObjects(target, searcher, 10.0f);
            others.remove_if([&](Unit* u)
            {
                return u == target || !u->IsAlive() || u->HasAura(info->Id) || !player->IsValidAttackTarget(u);
            });
        }

        for (Creature* serpent : serpents)
        {
            if (!serpent->IsAlive())
                continue;
            Unit* aim = target;
            if (charm)
            {
                if (others.empty())
                    break;
                aim = others.front();
                others.pop_front();
            }
            serpent->SetFacingToObject(aim);
            serpent->CastSpell(aim, info->Id, true);
        }
    }
}
