/*
 * mod-devourer: the form mechanics the kits left out (task 019). Released under GNU AGPL v3, like AzerothCore.
 * The spells are rows in 2026_10_03_00_devourer_tier2.sql (tools/evolved_kit.py); what a row cannot do is here.
 *
 *   Voidling line (41-43)  Void Eggs              a kill leaves a void egg; a few seconds later a voidling hatches
 *                                                 (two eggs for a Brood Devourer). The voidling is a normal hatchling
 *                                                 (NpcHatchling, Mgr::OnBroodHatched dresses it), so limits, despawn
 *                                                 and AI stay the Brood's own
 *   Voidcreeper, Broodmother  Feed the Swarm      voidlings near a kill devour the corpse and grow (3 steps)
 *   Broodmother            Broodmother's Call     every voidling fixates on the Broodmother's target and explodes
 *                                                 with Shadow damage when it dies
 *   Proto-Drake            Fire Breath            the worn colouring picks the element of the breath
 */

#include "Devourer.h"

#include "CellImpl.h"
#include "Creature.h"
#include "CreatureAI.h"
#include "GridNotifiers.h"
#include "GridNotifiersImpl.h"
#include "MotionMaster.h"
#include "ObjectAccessor.h"
#include "Player.h"
#include "ScriptMgr.h"
#include "SpellAuraEffects.h"
#include "SpellAuras.h"
#include "SpellInfo.h"
#include "SpellScript.h"
#include "SpellScriptLoader.h"
#include "TemporarySummon.h"
#include "Unit.h"
#include <algorithm>
#include <list>

using namespace Devourer;

namespace
{
    // tools/evolved_kit.py: shape s uses 9102000 + (s - 16) * 10 + slot
    constexpr uint32 SpellFireBreathFire = 9102206;       // Proto-Drake (36), slots 6-9: one helper per element
    constexpr uint32 SpellFireBreathNature = 9102207;
    constexpr uint32 SpellFireBreathStorm = 9102208;
    constexpr uint32 SpellFireBreathFrost = 9102209;
    constexpr uint32 SpellFedVoidling = 9102266;          // Voidcreeper (42), slot 6: a step of Feed the Swarm
    constexpr uint32 SpellBroodmothersCall = 9102276;     // Voidcreeper Broodmother (43), slot 6: the fixation mark
    constexpr uint32 SpellBroodBurst = 9102277;           // slot 7: what a marked voidling does when it dies

    constexpr uint32 ShapeVoidling = 41;
    constexpr uint32 ShapeVoidcreeper = 42;
    constexpr uint32 ShapeBroodmother = 43;

    constexpr uint32 EggDelay = 3000;                     // ms from the kill to the hatching
    constexpr uint32 HatchlingLife = 20000;               // like the Brood's own
    constexpr uint32 BroodCap = 8;                        // voidlings (and eggs about to hatch) at once
    constexpr uint32 CallBroodSize = 3;                   // Broodmother's Call hatches up to this many if there are fewer
    constexpr float FeedReach = 15.0f;                    // voidlings this close to a kill come to eat
    constexpr uint32 FeedDelay = 1500;                    // ms until the meal makes it grow
    constexpr uint8 FeedSteps = 3;
    constexpr float FeedGrowth = 1.15f;                   // scale per step (the aura adds the damage)
    constexpr float BurstReach = 8.0f;
    constexpr float CallReach = 40.0f;

    bool InVoidLine(uint32 shape)
    {
        return shape >= ShapeVoidling && shape <= ShapeBroodmother;
    }

    std::list<Unit*> EnemiesAround(Unit* center, Player* player, float range)
    {
        std::list<Unit*> list;
        Acore::AnyUnfriendlyUnitInObjectRangeCheck check(center, player, range);
        Acore::UnitListSearcher<Acore::AnyUnfriendlyUnitInObjectRangeCheck> searcher(center, list, check);
        Cell::VisitObjects(center, searcher, range);
        list.remove_if([&](Unit* unit) { return !unit->IsAlive() || !player->IsValidAttackTarget(unit); });
        return list;
    }

    // A voidling hatches at `pos` (if there is room in the brood); the Brood's own code dresses it.
    bool Hatch(Player* mother, Position const& pos)
    {
        if (!mother->IsAlive() || sDevourer.Mine(mother, NpcHatchling).size() >= BroodCap)
            return false;
        if (!mother->SummonCreature(NpcHatchling, pos, TEMPSUMMON_TIMED_DESPAWN, HatchlingLife, 0, GuardianProperties()))
            return false;
        sDevourer.OnBroodHatched(mother, false);
        return true;
    }

    // Void Eggs: the egg stands still where the creature fell and hatches after EggDelay.
    void LayEgg(Player* mother, Position pos, uint32 index)
    {
        if (sDevourer.Mine(mother, NpcVoidEgg).size() + sDevourer.Mine(mother, NpcHatchling).size() >= BroodCap)
            return;
        pos.m_positionX += 0.8f * float(index);
        pos.m_positionY += 0.8f * float(index);
        TempSummon* egg = mother->SummonCreature(NpcVoidEgg, pos, TEMPSUMMON_TIMED_DESPAWN, EggDelay + 1000);
        if (!egg)
            return;
        ObjectGuid const guid = egg->GetGUID();
        mother->m_Events.AddEventAtOffset([mother, guid]()
        {
            Creature* egg = ObjectAccessor::GetCreature(*mother, guid);
            if (!egg)
                return;
            Position const where = egg->GetPosition();
            egg->DespawnOrUnsummon();
            Hatch(mother, where);
        }, Milliseconds(EggDelay));
    }

    // Feed the Swarm: the voidling nearest to the corpse comes to eat; the meal makes it grow one step.
    void FeedSwarm(Player* mother, Creature* victim)
    {
        Creature* eater = nullptr;
        for (Creature* hatchling : sDevourer.Mine(mother, NpcHatchling, CallReach))
        {
            if (!hatchling->IsWithinDist(victim, FeedReach))
                continue;
            Aura const* fed = hatchling->GetAura(SpellFedVoidling);
            if (fed && fed->GetStackAmount() >= FeedSteps)
                continue;
            if (!eater || hatchling->GetDistance(victim) < eater->GetDistance(victim))
                eater = hatchling;
        }
        if (!eater)
            return;

        eater->GetMotionMaster()->MovePoint(0, victim->GetPositionX(), victim->GetPositionY(), victim->GetPositionZ());
        eater->HandleEmoteCommand(EMOTE_ONESHOT_EAT_NO_SHEATHE);
        ObjectGuid const guid = eater->GetGUID();
        mother->m_Events.AddEventAtOffset([mother, guid]()
        {
            Creature* young = ObjectAccessor::GetCreature(*mother, guid);
            if (!young || !young->IsAlive())
                return;
            Aura const* fed = young->GetAura(SpellFedVoidling);
            if (fed && fed->GetStackAmount() >= FeedSteps)
                return;
            young->CastSpell(young, SpellFedVoidling, true);        // +15% damage per step (the aura)
            young->SetObjectScale(young->GetObjectScale() * FeedGrowth);
        }, Milliseconds(FeedDelay));
    }

    // Breath colouring: the worn display picks the element (task 019 B).
    uint32 BreathFor(uint32 display)
    {
        switch (display)
        {
            case 994155: case 994156: case 994157: case 994159:     // the earth looks
                return SpellFireBreathNature;
            case 994160:                                            // the storm look
                return SpellFireBreathStorm;
            case 994161: case 994162:                               // the blue fire looks
                return SpellFireBreathFrost;
            default:                                                // the red look, and anything else
                return SpellFireBreathFire;
        }
    }
}

namespace Devourer
{
    void VoidBroodOnKill(Player* mother, Creature* victim)
    {
        uint32 const shape = sDevourer.Get(mother).Worn;
        if (!InVoidLine(shape) || victim->GetEntry() == NpcVoidEgg || victim->GetEntry() == NpcHatchling)
            return;

        uint32 const eggs = sDevourer.SpecOf(mother) == SpecBrood ? 2 : 1;      // a Brood Devourer gets two
        for (uint32 i = 0; i < eggs; ++i)
            LayEgg(mother, victim->GetPosition(), i);

        if (shape == ShapeVoidcreeper || shape == ShapeBroodmother)
            FeedSwarm(mother, victim);
    }
}

// Voidcreeper Broodmother: Broodmother's Call (the old Call the Swarm: its swarm still boils out of the ground). Hatches
// voidlings up to CallBroodSize, marks every voidling (spell 9102276, below) and sends them at the Broodmother's target.
class spell_devourer_broodmothers_call : public SpellScript
{
    PrepareSpellScript(spell_devourer_broodmothers_call);

    void Call()
    {
        Player* mother = GetCaster()->ToPlayer();
        if (!mother)
            return;
        for (size_t have = sDevourer.Mine(mother, NpcHatchling).size(); have < CallBroodSize; ++have)
        {
            Position pos = mother->GetPosition();
            mother->MovePositionToFirstCollision(pos, 2.0f, 0.6f + float(have) * 1.2f);
            if (!Hatch(mother, pos))
                break;
        }
        Unit* target = mother->GetVictim();
        if (!target)
            target = mother->GetSelectedUnit();
        bool const fight = target && target != mother && mother->IsValidAttackTarget(target);
        for (Creature* hatchling : sDevourer.Mine(mother, NpcHatchling, CallReach))
        {
            mother->CastSpell(hatchling, SpellBroodmothersCall, true);
            if (fight && hatchling->AI())
                hatchling->AI()->AttackStart(target);
        }
    }

    void Register() override
    {
        AfterCast += SpellCastFn(spell_devourer_broodmothers_call::Call);
    }
};

// The mark on a voidling: every second it keeps to the Broodmother's target, and when it dies it bursts.
class spell_devourer_broodmothers_call_mark : public AuraScript
{
    PrepareAuraScript(spell_devourer_broodmothers_call_mark);

    void Fixate(AuraEffect const* /*aurEff*/)
    {
        Player* mother = GetCaster() ? GetCaster()->ToPlayer() : nullptr;
        Creature* hatchling = GetTarget()->ToCreature();
        if (!mother || !hatchling || !hatchling->IsAlive() || !hatchling->AI())
            return;
        Unit* target = mother->GetVictim();
        if (target && target != hatchling->GetVictim() && hatchling->IsValidAttackTarget(target))
            hatchling->AI()->AttackStart(target);
    }

    void Burst(AuraEffect const* /*aurEff*/, AuraEffectHandleModes /*mode*/)
    {
        if (GetTargetApplication()->GetRemoveMode() != AURA_REMOVE_BY_DEATH)
            return;
        Player* mother = GetCaster() ? GetCaster()->ToPlayer() : nullptr;
        Unit* hatchling = GetTarget();
        if (!mother)
            return;
        for (Unit* enemy : EnemiesAround(hatchling, mother, BurstReach))
            mother->CastSpell(enemy, SpellBroodBurst, true);
    }

    void Register() override
    {
        OnEffectPeriodic += AuraEffectPeriodicFn(spell_devourer_broodmothers_call_mark::Fixate, EFFECT_0,
            SPELL_AURA_PERIODIC_DUMMY);
        AfterEffectRemove += AuraEffectRemoveFn(spell_devourer_broodmothers_call_mark::Burst, EFFECT_0,
            SPELL_AURA_PERIODIC_DUMMY, AURA_EFFECT_HANDLE_REAL);
    }
};

// Proto-Drake: Fire Breath. The breath's own Fire damage is replaced, per enemy hit, by the helper of the element the
// worn colouring picks (each does the same damage in its school; the storm and blue fire breaths slow as well).
class spell_devourer_proto_breath : public SpellScript
{
    PrepareSpellScript(spell_devourer_proto_breath);

    void Breathe(SpellEffIndex effIndex)
    {
        PreventHitDefaultEffect(effIndex);
        Unit* caster = GetCaster();
        if (Unit* target = GetHitUnit())
            caster->CastSpell(target, BreathFor(caster->GetDisplayId()), true);
    }

    void Register() override
    {
        OnEffectHitTarget += SpellEffectFn(spell_devourer_proto_breath::Breathe, EFFECT_0, SPELL_EFFECT_SCHOOL_DAMAGE);
    }
};

void AddSC_devourer_void()
{
    RegisterSpellScript(spell_devourer_broodmothers_call);
    RegisterSpellScript(spell_devourer_broodmothers_call_mark);
    RegisterSpellScript(spell_devourer_proto_breath);
}
