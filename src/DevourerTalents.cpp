/*
 * mod-devourer: the three talent trees, the spec abilities and their Anima (task 015).
 * Released under GNU AGPL v3, like AzerothCore.
 *
 * tools/placeholders.py builds the spells (docs/talents.md lists every talent and how it works). Here is what the
 * spells cannot do alone:
 *   - the "mark" talents: a passive dummy aura per rank; Rank() finds the highest rank the player knows
 *   - UpdatePerks, once a second: armour, damage, dodge, strike speed ... that depend on a state (Gorged stacks,
 *     living hatchlings, the Anima bar, a shift a moment ago) are worked out here and written into three hidden
 *     auras (Devourer's Nature), so the client shows them in the normal character sheet
 *   - Devourer's Hide, an absorb that takes nothing and watches every blow: Last Supper, Fat Reserves, the roar,
 *     Slow Chew
 *   - the spec abilities and the active talents (spell_devourer_spec), the Brood's hatchlings, the Skinchanger's echoes
 */

#include "Devourer.h"
#include "DevourerSpellIds.h"

#include "CellImpl.h"
#include "Creature.h"
#include "CreatureAI.h"
#include "DBCStores.h"
#include "GridNotifiers.h"
#include "GridNotifiersImpl.h"
#include "Log.h"
#include "MotionMaster.h"
#include "ObjectAccessor.h"
#include "Pet.h"
#include "Player.h"
#include "ScriptMgr.h"
#include "SpellAuraEffects.h"
#include "SpellAuras.h"
#include "SpellInfo.h"
#include "SpellMgr.h"
#include "SpellScript.h"
#include "TemporarySummon.h"
#include "Timer.h"
#include "Util.h"
#include <algorithm>
#include <cmath>
#include <list>
#include <string>

namespace Devourer
{
    namespace
    {
        constexpr float ChallengeReach = 10.0f;
        constexpr float EggburstReach = 5.0f;
        constexpr float BroodReach = 40.0f;
        constexpr uint32 HatchlingLife = 20000;

        std::list<Unit*> EnemiesAround(Unit* center, Player* player, float range)
        {
            std::list<Unit*> list;
            Acore::AnyUnfriendlyUnitInObjectRangeCheck check(center, player, range);
            Acore::UnitListSearcher<Acore::AnyUnfriendlyUnitInObjectRangeCheck> searcher(center, list, check);
            Cell::VisitObjects(center, searcher, range);
            list.remove_if([&](Unit* unit) { return !unit->IsAlive() || !player->IsValidAttackTarget(unit); });
            return list;
        }

        // What the three hidden Devourer's Nature auras hold (percent; Perks are summed over every talent).
        struct Perks
        {
            int32 Armour = 0, Taken = 0, Done = 0, DonePhysical = 0, Dodge = 0, Haste = 0, HealTaken = 0, Speed = 0,
                  Health = 0;
        };

        void SetEffect(Player* player, uint32 spellId, uint8 index, int32 value)
        {
            Aura* aura = player->GetAura(spellId);
            if (!aura)
            {
                if (!value || !sSpellMgr->GetSpellInfo(spellId))
                    return;
                aura = player->AddAura(spellId, player);
                if (!aura)
                    return;
            }
            if (AuraEffect* effect = aura->GetEffect(index))
                if (effect->GetAmount() != value)
                    effect->ChangeAmount(value);
        }
    }

    // --- helpers ------------------------------------------------------------------------------------------------

    uint8 Mgr::Rank(Player const* player, TalentRef talent) const
    {
        for (uint8 rank = talent.Ranks; rank > 0; --rank)
            if (player->HasSpell(talent.First + rank - 1))
                return rank;
        return 0;
    }

    uint8 Mgr::GorgedStacks(Player const* player) const
    {
        Aura const* gorged = player->GetAura(SpellGorged);
        return gorged ? gorged->GetStackAmount() : 0;
    }

    // Gorged grows to 10; Belly of the Beast adds up to 3, Stomach of Stone makes it 15.
    uint8 Mgr::GorgedCap(Player const* player) const
    {
        if (Rank(player, TalStomachOfStone))
            return 15;
        return 10 + Rank(player, TalBellyOfTheBeast);
    }

    // Creatures of one entry that belong to the player: its minions, and what it summoned (how Hatch Brood and the
    // echoes were summoned decides which list holds them, so both are searched).
    std::list<Creature*> Mgr::Mine(Player* player, uint32 entry, float range) const
    {
        std::list<Creature*> found;
        player->GetAllMinionsByEntry(found, entry);
        std::list<Creature*> nearby;
        player->GetCreatureListWithEntryInGrid(nearby, entry, range);
        for (Creature* creature : nearby)
        {
            bool const mine = creature->GetOwnerGUID() == player->GetGUID() || creature->GetCreatorGUID() == player->GetGUID() ||
                (creature->IsSummon() && creature->ToTempSummon()->GetSummonerGUID() == player->GetGUID());
            if (mine && std::find(found.begin(), found.end(), creature) == found.end())
                found.push_back(creature);
        }
        found.remove_if([](Creature* creature) { return !creature->IsAlive(); });
        return found;
    }

    void Mgr::StunFor(Player* player, Unit* target, uint32 ms)
    {
        player->CastSpell(target, SpellCrushingJaw, true);
        if (Aura* stun = target->GetAura(SpellCrushingJaw, player->GetGUID()))
        {
            stun->SetMaxDuration(int32(ms));
            stun->SetDuration(int32(ms));
        }
    }

    // Casts a spell with every effect stronger (or weaker) by `factor`.
    void Mgr::CastScaled(Unit* caster, Unit* target, uint32 spellId, float factor, ObjectGuid original)
    {
        SpellInfo const* info = sSpellMgr->GetSpellInfo(spellId);
        if (!info || !caster || !target)
            return;
        int32 points[3] = { 0, 0, 0 };
        bool has[3] = { false, false, false };
        for (uint8 i = 0; i < 3; ++i)
            if (info->Effects[i].IsEffect())
            {
                has[i] = true;
                points[i] = int32(std::lround(info->Effects[i].CalcValue(caster) * factor));
            }
        caster->CastCustomSpell(target, spellId, has[0] ? &points[0] : nullptr, has[1] ? &points[1] : nullptr,
            has[2] ? &points[2] : nullptr, true, nullptr, nullptr, original);
    }

    // The passive "Anima" (aura 94) keeps the bar from draining out of combat. A meal is eaten out of combat, so an
    // aura that was lost (learned before it existed, a form change, a data fix) is put back here too.
    void Mgr::EnsureAnimaAura(Player* player)
    {
        if (player->HasSpell(SpellAnima) && !player->HasAura(SpellAnima))
            player->AddAura(SpellAnima, player);
    }

    void Mgr::GainAnima(Player* player, uint32 points)
    {
        if (!points)
            return;
        EnsureAnimaAura(player);
        int32 const was = player->GetPower(POWER_RAGE);
        player->ModifyPower(POWER_RAGE, int32(points * 10));
        LOG_DEBUG("module", "mod-devourer: {} gains {} Anima ({} -> {}, power type {}, Anima aura {}, in combat {})",
            player->GetName(), points, was / 10, player->GetPower(POWER_RAGE) / 10, uint32(player->getPowerType()),
            player->HasAura(SpellAnima), player->IsInCombat());
    }

    void Mgr::Defer(Player* player, std::function<void()> fn)
    {
        player->m_Events.AddEventAtOffset(std::move(fn), Milliseconds(1));
    }

    bool Mgr::IsBeastShape(uint32 shapeId) const
    {
        for (auto const& [family, shape] : _familyShapes)
            if (shape == shapeId)
                return true;
        return false;
    }

    // --- the perks worked out once a second -----------------------------------------------------------------

    void Mgr::UpdatePerks(Player* player, State& state, uint32 diff)
    {
        if (state.PerkTimer > diff)
        {
            state.PerkTimer -= diff;
            return;
        }
        state.PerkTimer = 1000;
        if (!player->IsAlive() || !player->IsInWorld())
            return;

        if (!player->HasAura(SpellHide) && sSpellMgr->GetSpellInfo(SpellHide))
            player->AddAura(SpellHide, player);

        uint32 const now = getMSTime();
        Perks p;
        uint8 const gorged = GorgedStacks(player);

        // Glutton
        if (uint8 r = Rank(player, TalBottomlessPit))
            p.Armour += r * gorged / 2;
        if (uint8 r = Rank(player, TalGristlePlating))
            p.Armour += 5 * r * (player->HasAura(SpellMealMeat) ? 2 : 1);
        if (uint8 r = Rank(player, TalIronMaw))
            p.DonePhysical += 10 * r;
        if (uint8 r = Rank(player, TalGnawingPatience))
            p.Done += r * int32(std::min<size_t>(5, player->getAttackers().size()));
        if (uint8 r = Rank(player, TalSatiation))
            if (player->GetPower(POWER_RAGE) >= 1000)
                p.Taken -= 3 * r;
        bool const stone = Rank(player, TalStomachOfStone) && gorged >= 15;
        if (stone != player->HasAura(SpellStoneStomach))
        {
            if (stone)
                player->AddAura(SpellStoneStomach, player);
            else
                player->RemoveAurasDueToSpell(SpellStoneStomach);
        }
        if (Aura* gut = player->GetAura(SpellIronGutBuff))      // Iron Gut: 30%, and 1% more for every Gorged
            if (AuraEffect* effect = gut->GetEffect(EFFECT_0))
                if (effect->GetAmount() != -(30 + int32(gorged)))
                    effect->ChangeAmount(-(30 + int32(gorged)));

        // Skinchanger
        if (Active(state.ArmourUntil, now))
            p.Armour += 3 * Rank(player, TalShiftingHide);
        if (Active(state.DamageUntil, now))
            p.Done += 4 * Rank(player, TalBorrowedClaws);
        if (Active(state.SpeedUntil, now))
            p.Speed += 10 * Rank(player, TalQuickMolt);
        if (Active(state.HasteUntil, now))
            p.Haste += 10 * Rank(player, TalSwiftChange);
        if (Active(state.DodgeUntil, now))
            p.Dodge += 3 * Rank(player, TalSoftBones);
        if (uint8 r = Rank(player, TalUnfixedNature))
        {
            std::set<uint32> distinct;
            for (auto const& [shape, when] : state.Recent)
                if (int32(now - when) < 15000)
                    distinct.insert(shape);
            p.Done += 2 * r * int32(std::min<size_t>(3, distinct.size()));
        }
        if (uint8 r = Rank(player, TalStolenStrength))
            p.Done += r * int32(std::min<size_t>(10, state.Shapes.size()));
        if (uint8 r = Rank(player, TalLivingMask))
            if (!Mine(player, NpcEcho).empty())
                p.Taken -= 5 * r;
        if (uint8 r = Rank(player, TalMaskOfMeat))
        {
            Shape const* worn = FindShape(state.Worn);
            if (worn)
                p.Health += r * (IsBeastShape(worn->Id) ? 2 : 1);
        }

        // Brood
        size_t hatchlings = 0;
        if (Rank(player, TalClutchInstinct) || Rank(player, TalHiveMind) || Active(state.NestGuardUntil, now))
            hatchlings = Mine(player, NpcHatchling).size();
        if (hatchlings)
        {
            p.Dodge += 2 * Rank(player, TalClutchInstinct);
            p.Taken -= int32(Rank(player, TalHiveMind) * std::min<size_t>(5, hatchlings));
            if (Active(state.NestGuardUntil, now))
                p.Taken -= 25;
        }
        if (Active(state.WrathUntil, now))
            p.Done += 4 * Rank(player, TalMothersWrath) * state.WrathStacks;
        else
            state.WrathStacks = 0;
        if (Active(state.BloodMilkUntil, now))
            p.Haste += 10 * Rank(player, TalBloodMilk);

        SetEffect(player, SpellNatureA, EFFECT_0, p.Armour);
        SetEffect(player, SpellNatureA, EFFECT_1, p.Taken);
        SetEffect(player, SpellNatureA, EFFECT_2, p.Done);
        SetEffect(player, SpellNatureB, EFFECT_0, p.Dodge);
        SetEffect(player, SpellNatureB, EFFECT_1, p.Haste);
        SetEffect(player, SpellNatureB, EFFECT_2, p.HealTaken);
        SetEffect(player, SpellNatureC, EFFECT_0, p.Speed);
        SetEffect(player, SpellNatureC, EFFECT_1, p.DonePhysical);
        SetEffect(player, SpellNatureC, EFFECT_2, p.Health);
    }

    // --- Anima from blows ---------------------------------------------------------------------------------------

    // Iron Maw and Chewing Cud add to the swing's Anima.
    void Mgr::OnAnimaFromSwing(Player* player)
    {
        uint32 extra = Rank(player, TalIronMaw);
        if (GorgedStacks(player) >= 5)
            extra += Rank(player, TalChewingCud);
        GainAnima(player, extra);
    }

    // --- shifts -------------------------------------------------------------------------------------------------

    // A shift has just landed (Mgr::AfterShift): the cooldown that follows, and everything a shift brings.
    void Mgr::OnShift(Player* player, Shape const& shape)
    {
        State& state = Get(player);
        uint32 const now = getMSTime();
        uint32 const sinceLast = state.ShiftAt ? now - state.ShiftAt : 0xFFFFFFFF;

        // One cooldown for every shape: the spell's category cools all of them down. A Skinchanger's recovers
        // faster, Fluid Flesh and Fleeting Form make it shorter still, Form of Many takes it away.
        int32 target = int32(SpecOf(player) == SpecSkinchanger ? _skinchangerShiftCooldown : _shiftCooldown);
        bool const many = Active(state.ManyUntil, now);
        uint8 const fluid = Rank(player, TalFluidFlesh);
        uint8 const fleeting = Rank(player, TalFleetingForm);
        if (fluid || fleeting)
        {
            target -= 200 * fluid;
            if (sinceLast < 5000)
                target -= 500 * fleeting;
            target = std::max(target, 1000);
        }
        if (many)
            target = 0;
        int32 const delta = target - int32(_shiftCooldown);
        if (delta < 0)
            for (auto const& [id, other] : _shapes)
                if (player->HasSpell(other.FormSpell))
                {
                    if (target == 0)
                        player->RemoveSpellCooldown(other.FormSpell, true);
                    else
                        player->ModifySpellCooldown(other.FormSpell, delta);
                }

        state.ShiftAt = now;
        if (Rank(player, TalShiftingHide))
            state.ArmourUntil = now + 6000;
        if (Rank(player, TalBorrowedClaws))
            state.DamageUntil = now + 8000;
        if (Rank(player, TalQuickMolt))
            state.SpeedUntil = now + 4000;
        if (Rank(player, TalSwiftChange))
            state.HasteUntil = now + 4000;
        if (Rank(player, TalSoftBones))
            state.DodgeUntil = now + 10000;
        state.PerkTimer = 0;                             // work the new perks out at once

        if (uint8 r = Rank(player, TalRestlessForm))
        {
            auto left = state.LeftAt.find(shape.Id);
            if (left == state.LeftAt.end() || now - left->second >= 60000)
                GainAnima(player, 5 * r);
        }
        if (uint8 r = Rank(player, TalShedSkin))
            if (!Active(state.ShedReady, now))
            {
                player->RemoveMovementImpairingAuras(true);
                state.ShedReady = now + (r >= 2 ? 20000 : 40000);
            }
        state.Recent.erase(std::remove_if(state.Recent.begin(), state.Recent.end(),
            [&](auto const& entry) { return entry.first == shape.Id || int32(now - entry.second) >= 15000; }),
            state.Recent.end());
        state.Recent.emplace_back(shape.Id, now);
    }

    void Mgr::OnShapeLeft(Player* player, Shape const& shape)
    {
        State& state = Get(player);
        state.LastLeftShape = shape.Id;
        state.LeftAt[shape.Id] = getMSTime();
    }

    // --- meals --------------------------------------------------------------------------------------------------

    // Every meal (Devour, Feast, Devour Whole): the Anima it gives, what Ravenous Guard heals, who shares it.
    void Mgr::OnMeal(Player* player, Creature const* meal, bool whole)
    {
        GainAnima(player, _hungerPerMeal + 2u * Rank(player, TalDeepHunger));
        if (uint8 r = Rank(player, TalRavenousGuard))
            if (player->GetHealthPct() < 50.0f)
                player->ModifyHealth(int32(player->CountPctFromMaxHealth(5 * r)));
        if (uint8 r = Rank(player, TalSharedMeal))
            for (Creature* hatchling : Mine(player, NpcHatchling, 10.0f))
                if (hatchling->IsWithinDist(player, 10.0f))
                    hatchling->ModifyHealth(int32(hatchling->CountPctFromMaxHealth(10 * r)));
        PetShareMeal(player, meal, whole || (meal && (meal->isElite() || meal->GetLevel() >= player->GetLevel() + 3)));
    }

    // --- the hidden absorb: every blow the Devourer takes ----------------------------------------------------------

    void Mgr::OnHitTaken(Player* player, DamageInfo& damageInfo, uint32& absorb)
    {
        State& state = Get(player);
        uint32 const damage = damageInfo.GetDamage();
        Unit* attacker = damageInfo.GetAttacker();
        if (!damage || !player->IsAlive())
            return;
        uint32 const now = getMSTime();

        // Last Supper: a blow that would kill, with a full bar. Survive at 20% and eat every Gorged stack.
        if (player->HasSpell(SpellLastSupper) && !Active(state.LastSupperReady, now) &&
            player->GetPower(POWER_RAGE) >= 1000 && damage >= player->GetHealth())
        {
            state.LastSupperReady = now + 300000;
            uint32 const stacks = GorgedStacks(player);
            uint32 const floor = uint32(player->CountPctFromMaxHealth(20));
            uint32 const health = uint32(player->GetHealth());
            absorb = health > floor ? damage - (health - floor) : damage;
            absorb = std::min(absorb, damage);
            player->SetPower(POWER_RAGE, 0);
            Defer(player, [this, player, stacks, floor, health]()
            {
                if (!player->IsAlive())
                    return;
                if (health < floor)
                    player->SetHealth(floor);
                player->RemoveAurasDueToSpell(SpellGorged);
                if (stacks)
                    player->ModifyHealth(int32(player->CountPctFromMaxHealth(3 * stacks)));
                player->HandleEmoteCommand(EMOTE_ONESHOT_EAT_NO_SHEATHE);
                Tell(player, "Last Supper: you refuse to die and eat everything you carry.");
            });
            return;
        }

        // Fat Reserves: the first time a fight drops the Devourer under 30%, stored fat forms a shield.
        if (Rank(player, TalFatReserves) && !Active(state.FatReady, now) && player->IsInCombat() &&
            player->HealthBelowPctDamaged(30, damage))
        {
            state.FatReady = now + 180000;
            int32 const shield = int32(player->CountPctFromMaxHealth(15));
            Defer(player, [player, shield]()
            {
                if (player->IsAlive())
                    player->CastCustomSpell(player, SpellFatReserves, &shield, nullptr, nullptr, true);
            });
        }

        if (!attacker || attacker == player || !player->IsValidAttackTarget(attacker))
            return;

        // The roar (Devouring Challenge): every enemy that strikes feeds the Devourer once.
        if (Active(state.ChallengeUntil, now) && state.ChallengeFed.insert(attacker->GetGUID()).second)
            GainAnima(player, 5);

        // Slow Chew: an enemy that strikes swings slower for a while.
        if (uint8 r = Rank(player, TalSlowChew))
        {
            ObjectGuid const guid = attacker->GetGUID();
            Defer(player, [player, guid, r]()
            {
                Unit* enemy = ObjectAccessor::GetUnit(*player, guid);
                if (enemy && enemy->IsAlive())
                {
                    int32 const slow = -2 * int32(r);
                    player->CastCustomSpell(enemy, SpellSlowChew, &slow, nullptr, nullptr, true);
                }
            });
        }
    }

    // --- the Brood ----------------------------------------------------------------------------------------------

    // The talents that shape a hatchling: health, bite, armour, shells, size.
    void Mgr::TuneHatchling(Player* player, Creature* hatchling, float healthShare, float minDmg, float maxDmg, bool swarm)
    {
        bool const queen = Rank(player, TalQueenOfTheBrood) > 0;
        float const hp = 1.0f + 0.03f * Rank(player, TalWarmNest);
        float const bite = 1.0f + 0.05f * Rank(player, TalEggTooth) + (queen ? 0.20f : 0.0f);
        uint32 const health = std::max<uint32>(1, uint32(player->GetMaxHealth() * healthShare * hp));
        hatchling->SetCreateHealth(health);
        hatchling->SetMaxHealth(health);
        hatchling->SetHealth(health);
        if (swarm)                                       // Brood Swarm: half of the Devourer's attack power
        {
            float const half = player->GetTotalAttackPowerValue(BASE_ATTACK) * 0.5f / 14.0f * 2.0f;
            hatchling->SetBaseWeaponDamage(BASE_ATTACK, MINDAMAGE, half * 0.8f * bite);
            hatchling->SetBaseWeaponDamage(BASE_ATTACK, MAXDAMAGE, half * 1.2f * bite);
        }
        else
        {
            float const level = float(player->GetLevel());
            hatchling->SetBaseWeaponDamage(BASE_ATTACK, MINDAMAGE, level * minDmg * bite);
            hatchling->SetBaseWeaponDamage(BASE_ATTACK, MAXDAMAGE, level * maxDmg * bite);
        }
        hatchling->UpdateDamagePhysical(BASE_ATTACK);
        if (uint8 r = Rank(player, TalLitterBond))       // a share of the Devourer's armour
            hatchling->SetStatFlatModifier(UNIT_MOD_ARMOR, BASE_VALUE, float(player->GetArmor()) * 0.02f * r);
        if (uint8 r = Rank(player, TalThickShells))
        {
            int32 const less = -5 * int32(r);
            hatchling->CastCustomSpell(hatchling, SpellThickShells, &less, nullptr, nullptr, true);
        }
        (void)queen;
    }

    void Mgr::OnHatchlingHit(Player* mother, Creature* hatchling, Unit* victim, uint32 damage)
    {
        if (!victim || !damage || !mother->IsValidAttackTarget(victim))
            return;
        if (uint8 r = Rank(mother, TalNestWeb))
        {
            int32 const slow = -2 * int32(r);
            hatchling->CastCustomSpell(victim, SpellNestWeb, &slow, nullptr, nullptr, true);
        }
        if (uint8 r = Rank(mother, TalYoungTeeth))
        {
            int32 const tick = std::max<int32>(1, int32(damage * 0.3f * r / 3.0f));
            hatchling->CastCustomSpell(victim, SpellYoungTeeth, &tick, nullptr, nullptr, true);
        }
        if (victim->HasAura(SpellNestScentMark, mother->GetGUID()))
            GainAnima(mother, 2);
    }

    // A hatchling has died: it bursts, the Devourer is angry, a new one may hatch.
    void Mgr::OnHatchlingDeath(Player* mother, Creature* hatchling)
    {
        State& state = Get(mother);
        uint32 const now = getMSTime();
        if (uint8 r = Rank(mother, TalTwitchingEggs))
        {
            int32 const burst = std::max<int32>(1, int32(mother->GetTotalAttackPowerValue(BASE_ATTACK) * 0.3f * r));
            for (Unit* enemy : EnemiesAround(hatchling, mother, EggburstReach))
                mother->CastCustomSpell(enemy, SpellEggburst, &burst, nullptr, nullptr, true);
        }
        if (uint8 r = Rank(mother, TalMothersWrath))
        {
            state.WrathStacks = uint8(std::min<int>(3, state.WrathStacks + 1));
            state.WrathUntil = now + 8000;
            state.PerkTimer = 0;
            (void)r;
        }
        if (uint8 r = Rank(mother, TalEndlessClutch))
            if (urand(1, 100) <= 10u * r)
            {
                Position pos = hatchling->GetPosition();
                if (TempSummon* young = mother->SummonCreature(NpcHatchling, pos, TEMPSUMMON_TIMED_DESPAWN, HatchlingLife, 0,
                        GuardianProperties()))
                {
                    OnBroodHatched(mother, false);       // dresses the new hatchling like the others
                    (void)young;
                }
            }
    }

    // Every few seconds: hatchlings left behind are called back (Brood Mother); the brood is kept up (Queen).
    void Mgr::SyncBrood(Player* player, State& state)
    {
        uint8 const mother = Rank(player, TalBroodMother);
        bool const queen = Rank(player, TalQueenOfTheBrood) > 0;
        if (!mother && !queen)
            return;
        std::list<Creature*> brood = Mine(player, NpcHatchling, 200.0f);
        if (mother)
        {
            float const leash = mother >= 2 ? 40.0f : 60.0f;
            for (Creature* hatchling : brood)
                if (hatchling->GetMapId() == player->GetMapId() && !hatchling->IsWithinDist(player, leash))
                {
                    Position pos = player->GetPosition();
                    player->MovePositionToFirstCollision(pos, 2.0f, float(M_PI));
                    hatchling->NearTeleportTo(pos.GetPositionX(), pos.GetPositionY(), pos.GetPositionZ(), pos.GetOrientation());
                }
        }
        if (queen && !brood.empty() && brood.size() < 4 && player->IsInCombat() && player->IsAlive())
        {
            Position pos = player->GetPosition();
            player->MovePositionToFirstCollision(pos, 2.0f, 2.0f);
            if (player->SummonCreature(NpcHatchling, pos, TEMPSUMMON_TIMED_DESPAWN, HatchlingLife, 0,
                    GuardianProperties()))
                OnBroodHatched(player, false);
        }
        (void)state;
    }

    // --- spec abilities and active talents ------------------------------------------------------------------------

    bool Mgr::CanCastSpec(Player* player, SpellInfo const* spell, Unit* target, std::string& why)
    {
        State& state = Get(player);
        switch (spell->Id)
        {
            case SpellSkinSwap:
            case SpellEchoFlesh:
                if (Mine(player, NpcEcho).empty())
                {
                    why = "You have no echo.";
                    return false;
                }
                break;
            case SpellStolenInstinct:
            {
                Shape const* left = FindShape(state.LastLeftShape);
                if (!left || !left->Passive || !FindShape(state.Worn))
                {
                    why = "You have no shape to borrow from.";
                    return false;
                }
                break;
            }
            case SpellCallTheClutch:
            case SpellBroodSense:
                if (Mine(player, NpcHatchling, BroodReach).empty())
                {
                    why = "You have no hatchlings.";
                    return false;
                }
                if (!target || !target->IsAlive() || !player->IsValidAttackTarget(target))
                {
                    why = "Choose an enemy first.";
                    return false;
                }
                break;
            case SpellFeedTheYoung:
            case SpellNestGuard:
                if (Mine(player, NpcHatchling, BroodReach).empty())
                {
                    why = "You have no hatchlings.";
                    return false;
                }
                if (spell->Id == SpellFeedTheYoung && player->GetHealthPct() <= 20.0f)
                {
                    why = "You are too weak to feed them.";
                    return false;
                }
                break;
            case SpellNestScent:
                if (!target || !target->IsAlive() || !player->IsValidAttackTarget(target))
                {
                    why = "Choose an enemy first.";
                    return false;
                }
                break;
            default:
                break;
        }
        return true;
    }

    void Mgr::CastSpec(Player* player, SpellInfo const* spell, Unit* target)
    {
        State& state = Get(player);
        uint32 const now = getMSTime();
        switch (spell->Id)
        {
            case SpellIronGut:
            {
                player->CastSpell(player, SpellIronGutBuff, true);
                if (Aura* gut = player->GetAura(SpellIronGutBuff))
                {
                    int32 const ms = 8000 + 2000 * int32(Rank(player, TalHungersWall));
                    gut->SetMaxDuration(ms);
                    gut->SetDuration(ms);
                }
                state.PerkTimer = 0;
                player->HandleEmoteCommand(EMOTE_ONESHOT_ROAR);
                break;
            }
            case SpellDevouringChallenge:
            {
                state.ChallengeUntil = now + 4000;
                state.ChallengeFed.clear();
                for (Unit* enemy : EnemiesAround(player, player, ChallengeReach))
                    player->CastSpell(enemy, SpellChallenged, true);
                player->HandleEmoteCommand(EMOTE_ONESHOT_ROAR);
                break;
            }
            case SpellMimicStrike:                       // a plain weapon blow, see its spell
                break;
            case SpellSkinSwap:
            {
                std::list<Creature*> echoes = Mine(player, NpcEcho);
                Creature* echo = echoes.empty() ? nullptr : echoes.front();
                if (!echo)
                    break;
                Position const mine = player->GetPosition();
                Position const theirs = echo->GetPosition();
                player->NearTeleportTo(theirs.GetPositionX(), theirs.GetPositionY(), theirs.GetPositionZ(), theirs.GetOrientation());
                echo->NearTeleportTo(mine.GetPositionX(), mine.GetPositionY(), mine.GetPositionZ(), mine.GetOrientation());
                Unit* victim = player->GetVictim();
                if (victim && victim->IsAlive() && player->IsValidAttackTarget(victim))
                    echo->CastSpell(victim, SpellChallenged, true);
                break;
            }
            case SpellFormOfMany:
                state.ManyUntil = now + 12000;
                for (auto const& [id, shape] : _shapes)
                    if (player->HasSpell(shape.FormSpell))
                        player->RemoveSpellCooldown(shape.FormSpell, true);
                break;
            case SpellCallTheClutch:
                for (Creature* hatchling : Mine(player, NpcHatchling, BroodReach))
                {
                    hatchling->CastSpell(hatchling, SpellClutchCall, true);
                    if (CreatureAI* ai = hatchling->AI())
                        ai->AttackStart(target);
                }
                break;
            case SpellFeedTheYoung:
                player->ModifyHealth(-int32(std::min<uint32>(player->CountPctFromMaxHealth(15), uint32(player->GetHealth()) - 1)));
                bool first = true;
                for (Creature* hatchling : Mine(player, NpcHatchling, BroodReach))
                {
                    hatchling->ModifyHealth(int32(hatchling->CountPctFromMaxHealth(25)));
                    hatchling->CastSpell(hatchling, SpellFedYoung, true);
                    if (first)                               // task 016: one eats loudly, the rest in silence
                        hatchling->HandleEmoteCommand(EMOTE_ONESHOT_EAT_NO_SHEATHE);
                    first = false;
                }
                break;
            case SpellBroodSwarm:
            {
                uint32 const life = 20000 + 3000 * Rank(player, TalCrawlingMass) + 4000 * Rank(player, TalSwarmTide);
                std::list<Creature*> made;
                for (uint8 i = 0; i < 6; ++i)
                {
                    Position pos = player->GetPosition();
                    player->MovePositionToFirstCollision(pos, 2.5f, float(i) * float(M_PI) / 3.0f);
                    if (TempSummon* young = player->SummonCreature(NpcHatchling, pos, TEMPSUMMON_TIMED_DESPAWN, life, 0,
                            GuardianProperties()))
                        made.push_back(young);
                }
                OnBroodHatched(player, false);           // dresses the new ones in the worn shape's kin
                for (Creature* young : made)
                {
                    TuneHatchling(player, young, 0.15f, 0.9f, 1.4f, true);
                    Unit* victim = player->GetVictim();
                    if (victim && victim->IsAlive())
                        if (CreatureAI* ai = young->AI())
                            ai->AttackStart(victim);
                }
                break;
            }
            case SpellStolenInstinct:
                if (Shape const* left = FindShape(state.LastLeftShape))
                    if (left->Passive && sSpellMgr->GetSpellInfo(left->Passive))
                    {
                        player->RemoveAurasDueToSpell(left->Passive);
                        if (Aura* borrowed = player->AddAura(left->Passive, player))
                        {
                            borrowed->SetMaxDuration(12000);
                            borrowed->SetDuration(12000);
                        }
                    }
                break;
            case SpellEchoFlesh:
            {
                std::list<Creature*> echoes = Mine(player, NpcEcho);
                Creature* echo = echoes.empty() ? nullptr : echoes.front();
                Shape const* shape = FindShape(state.LastLeftShape);
                if (!echo)
                    break;
                Position pos = player->GetPosition();
                player->MovePositionToFirstCollision(pos, 1.5f, float(M_PI) / 2);
                echo->NearTeleportTo(pos.GetPositionX(), pos.GetPositionY(), pos.GetPositionZ(), pos.GetOrientation());
                Unit* victim = player->GetVictim();
                if (victim && victim->IsAlive() && shape && shape->Kit[0] && sSpellMgr->GetSpellInfo(shape->Kit[0]))
                    CastScaled(echo, victim, shape->Kit[0], 1.0f + 0.04f * Rank(player, TalBorrowedVoice), player->GetGUID());
                break;
            }
            case SpellWornFaces:
                state.WornFacesUntil = now + 10000;
                break;
            case SpellNestGuard:
                state.NestGuardUntil = now + 8000;
                state.PerkTimer = 0;
                for (Creature* hatchling : Mine(player, NpcHatchling, BroodReach))
                {
                    Position pos = player->GetPosition();
                    player->MovePositionToFirstCollision(pos, 2.0f, float(urand(0, 628)) / 100.0f);
                    hatchling->NearTeleportTo(pos.GetPositionX(), pos.GetPositionY(), pos.GetPositionZ(), pos.GetOrientation());
                }
                break;
            case SpellBroodSense:
                for (Creature* hatchling : Mine(player, NpcHatchling, BroodReach))
                    if (CreatureAI* ai = hatchling->AI())
                        ai->AttackStart(target);
                break;
            case SpellNestScent:
                player->CastSpell(target, SpellNestScentMark, true);
                break;
            default:
                break;
        }
    }
}

using namespace Devourer;

// --- the spec abilities and the active talents: the module does what the spell cannot ---------------------------------

class spell_devourer_spec : public SpellScript
{
    PrepareSpellScript(spell_devourer_spec);

    SpellCastResult CheckCast()
    {
        Player* player = GetCaster()->ToPlayer();
        if (!player || !sDevourer.IsDevourer(player))
            return SPELL_FAILED_DONT_REPORT;
        std::string why;
        if (!sDevourer.CanCastSpec(player, GetSpellInfo(), GetExplTargetUnit(), why))
        {
            sDevourer.Tell(player, why);
            return SPELL_FAILED_DONT_REPORT;
        }
        return SPELL_CAST_OK;
    }

    void Cast()
    {
        if (Player* player = GetCaster()->ToPlayer())
            sDevourer.CastSpec(player, GetSpellInfo(), GetExplTargetUnit());
    }

    void Register() override
    {
        OnCheckCast += SpellCheckCastFn(spell_devourer_spec::CheckCast);
        AfterCast += SpellCastFn(spell_devourer_spec::Cast);
    }
};

// Devourer's Hide: an endless absorb that takes nothing and lets the module look at every blow (Mgr::OnHitTaken).
class spell_devourer_hide : public AuraScript
{
    PrepareAuraScript(spell_devourer_hide);

    void Amount(AuraEffect const* /*aurEff*/, int32& amount, bool& /*canBeRecalculated*/)
    {
        amount = -1;
    }

    void Absorb(AuraEffect* /*aurEff*/, DamageInfo& dmgInfo, uint32& absorbAmount)
    {
        absorbAmount = 0;
        if (Player* player = GetTarget()->ToPlayer())
            sDevourer.OnHitTaken(player, dmgInfo, absorbAmount);
    }

    void Register() override
    {
        DoEffectCalcAmount += AuraEffectCalcAmountFn(spell_devourer_hide::Amount, EFFECT_0, SPELL_AURA_SCHOOL_ABSORB);
        OnEffectAbsorb += AuraEffectAbsorbFn(spell_devourer_hide::Absorb, EFFECT_0);
    }
};

void AddSC_devourer_talents()
{
    RegisterSpellScript(spell_devourer_spec);
    RegisterSpellScript(spell_devourer_hide);
}
