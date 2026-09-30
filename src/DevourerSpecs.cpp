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
#include "DevourerPlaceholderIds.h"

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
        // The (placeholder) abilities at 20/40/60 come from tools/placeholders.py (DevourerPlaceholderIds.h).
        constexpr SpecSpell SpecSpells[] =
        {
            { SpecGlutton,     SpellIdentityGlutton,         1 },
            { SpecSkinchanger, SpellIdentitySkinchanger,     1 },
            { SpecBrood,       SpellIdentityBrood,           1 },
            { SpecBrood,       SpellHatchBrood,              1 },
            { SpecGlutton,     SpellPlaceholderGlutton20,     20 },
            { SpecGlutton,     SpellPlaceholderGlutton40,     40 },
            { SpecGlutton,     SpellPlaceholderGlutton60,     60 },
            { SpecSkinchanger, SpellPlaceholderSkinchanger20, 20 },
            { SpecSkinchanger, SpellPlaceholderSkinchanger40, 40 },
            { SpecSkinchanger, SpellPlaceholderSkinchanger60, 60 },
            { SpecBrood,       SpellPlaceholderBrood20,       20 },
            { SpecBrood,       SpellPlaceholderBrood40,       40 },
            { SpecBrood,       SpellPlaceholderBrood60,       60 },
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
        if (state.SyncTimer > diff)
        {
            state.SyncTimer -= diff;
            return;
        }
        state.SyncTimer = SyncInterval;
        if (state.GrowthDirty)
            SaveGrowth(player);
        if (state.SyncedSpec != SpecOf(player) || state.SyncedLevel != player->GetLevel())
            SyncSpecSpells(player);
        SyncTalentSpells(player);                        // talents can change at any time, not only with the spec
        DigestGorged(player, state);
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
        player->ModifyPower(POWER_RAGE, int32(_hungerPerMeal * 10));
        player->CastSpell(player, SpellSated, true);
        FeedGlutton(player, victim);

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
        bool const favourite = worn && FavouriteFood(worn->Id) && meal->GetCreatureType() == FavouriteFood(worn->Id);
        player->CastSpell(player, SpellGorged, true);
        if (favourite)
        {
            player->CastSpell(player, SpellGorged, true);
            Tell(player, "Your " + worn->Name + " body loves that meal: Gorged twice.");
        }
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
        for (uint32 other : MealSpells)
            if (other != buff)
                player->RemoveAurasDueToSpell(other);
        player->CastSpell(player, buff, true);
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
        uint32 const hold = player->HasSpell(SpellTalentStretchedGut) ? GorgedHeldFor : GorgedDigestAfter;
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
            player->ModifyPower(POWER_RAGE, int32(_hungerPerMeal * 10));
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
    void Mgr::Overrun(Player* player, uint32 hitSpell, bool chase)
    {
        Get(player).OverrunWindup = 0;
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
            dest = player->GetFirstCollisionPosition(OverrunDash, 0.0f);

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

    void Mgr::OnBroodHatched(Player* player)
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

        std::list<Creature*> hatchlings;
        player->GetAllMinionsByEntry(hatchlings, NpcHatchling);
        for (Creature* hatchling : hatchlings)
        {
            if (!hatchling->IsAlive() || hatchling->GetDisplayId() == display)
                continue;                                // already dressed
            Dress(hatchling, player, display, 0.15f, 0.9f, 1.4f);
            if (adult)
                hatchling->SetObjectScale(0.5f);
            Engage(hatchling, player);
        }
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
        Tell(player, "You eat one of your own hatchlings.");
    }

    void Mgr::OnCreatureDeath(Creature* victim, Unit* killer)
    {
        if (!killer || victim->GetEntry() == NpcHatchling || victim->GetEntry() == NpcEcho)
            return;
        Player* mother = killer->GetCharmerOrOwnerPlayerOrPlayerItself();
        if (!mother || !IsDevourer(mother) || SpecOf(mother) != SpecBrood)
            return;

        State& state = Get(mother);
        if (state.Eaten.count(victim->GetGUID()))
            return;

        std::list<Creature*> hatchlings;
        mother->GetAllMinionsByEntry(hatchlings, NpcHatchling);
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
        mother->ModifyPower(POWER_RAGE, 10 * 10);
        mother->ModifyHealth(int32(mother->CountPctFromMaxHealth(3)));
        EatShape(mother, victim, "Your hatchlings devour " + victim->GetName() + " and feed you.");
    }

    // --- Skinchanger --------------------------------------------------------------------------------------

    void Mgr::SpawnEcho(Player* player, Shape const& shape)
    {
        if (!player->IsInCombat() || !player->GetVictim())
            return;

        TempSummon* echo = player->SummonCreature(NpcEcho, player->GetPosition(), TEMPSUMMON_TIMED_DESPAWN, EchoDuration,
            0, sSummonPropertiesStore.LookupEntry(SummonGuardianProperties));
        if (!echo)
            return;

        Dress(echo, player, ShownDisplay(player, shape), 0.25f, 1.5f, 2.2f);
        echo->AddAura(SpellGhostVisual, echo);
        Engage(echo, player);
        // The echo remembers the shape's first ability and throws it once.
        if (Unit* victim = player->GetVictim())
            if (shape.Kit[0] && sSpellMgr->GetSpellInfo(shape.Kit[0]))
                echo->CastSpell(victim, shape.Kit[0], true, nullptr, nullptr, player->GetGUID());
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
