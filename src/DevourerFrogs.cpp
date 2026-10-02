/*
 * mod-devourer: the frog line (owner, 2026-10-02, Parrot\to be devoured.canvas).
 * Released under GNU AGPL v3, like AzerothCore.
 *
 * The Biletoad (shape 14, Wren's chore "Pests in the Cells", see DevourerSisters.cpp) and the Giant Marsh Frog
 * (shape 15, grows out of it, 2026_10_02_00_devourer_frogs.sql). Their spells come from tools/start_kit.py; what
 * the client cannot do by itself lives here:
 *   Tongue Pull        counts for the Giant Marsh Frog's growth; brings a pest down from where it hovers
 *   Swamp Hop          on landing, the poison splash; every enemy it reaches is knocked down (and counted)
 *   Belly Flop         on landing, the slam: damage = 10% of the frog's maximum health
 * and Wren's pests: they never fight back; the ones above the cages hover until a tongue pulls them down.
 */

#include "Devourer.h"
#include "DevourerSistersIds.h"

#include "CreatureAI.h"
#include "CreatureScript.h"
#include "MotionMaster.h"
#include "Player.h"
#include "SpellInfo.h"
#include "SpellScript.h"
#include "SpellScriptLoader.h"

using namespace Devourer;

namespace
{
    // tools/start_kit.py: Biletoad 9101010 + slot, Giant Marsh Frog 9101020 + slot
    constexpr uint32 SpellTonguePull = 9101012;
    constexpr uint32 SpellSwampHop = 9101014;
    constexpr uint32 SpellSwampHopSplash = 9101016;
    constexpr uint32 SpellSwampHopKnockdown = 9101017;
    constexpr uint32 SpellBellyFlopSlam = 9101026;
    constexpr uint32 BellyFlopHealthPct = 10;
    constexpr Milliseconds LandAfter = 600ms;   // the leap is short and fast (Hungering Lunge's jump)
}

// Tongue Pull: every enemy pulled counts towards the Giant Marsh Frog.
class spell_devourer_tongue_pull : public SpellScript
{
    PrepareSpellScript(spell_devourer_tongue_pull);

    void Pulled(SpellEffIndex /*effIndex*/)
    {
        if (Player* player = GetCaster()->ToPlayer())
            if (GetHitUnit())
                sDevourer.TaskEvent(player, TaskSpellHit, SpellTonguePull);
    }

    void Register() override
    {
        OnEffectHitTarget += SpellEffectFn(spell_devourer_tongue_pull::Pulled, EFFECT_0, SPELL_EFFECT_PULL_TOWARDS);
    }
};

// Swamp Hop and Belly Flop: the leap; where the frog lands, its splash or its slam.
class spell_devourer_frog_leap : public SpellScript
{
    PrepareSpellScript(spell_devourer_frog_leap);

    void Leapt()
    {
        Unit* caster = GetCaster();
        if (!caster)
            return;
        uint32 const landing = GetSpellInfo()->Id == SpellSwampHop ? SpellSwampHopSplash : SpellBellyFlopSlam;
        caster->m_Events.AddEventAtOffset([caster, landing]()
        {
            if (caster->IsAlive())
                caster->CastSpell(caster, landing, true);
        }, LandAfter);
    }

    void Register() override
    {
        AfterCast += SpellCastFn(spell_devourer_frog_leap::Leapt);
    }
};

// Swamp Hop's splash: every enemy it reaches is knocked down for a moment, and that counts towards the Giant Marsh Frog.
class spell_devourer_swamp_hop_splash : public SpellScript
{
    PrepareSpellScript(spell_devourer_swamp_hop_splash);

    void KnockDown(SpellEffIndex /*effIndex*/)
    {
        Unit* caster = GetCaster();
        Unit* target = GetHitUnit();
        if (!caster || !target)
            return;
        caster->CastSpell(target, SpellSwampHopKnockdown, true);
        if (Player* player = caster->ToPlayer())
            sDevourer.TaskEvent(player, TaskSpellHit, SpellSwampHopKnockdown);
    }

    void Register() override
    {
        OnEffectHitTarget += SpellEffectFn(spell_devourer_swamp_hop_splash::KnockDown, EFFECT_0,
            SPELL_EFFECT_SCHOOL_DAMAGE);
    }
};

// Belly Flop's slam: as heavy as the frog.
class spell_devourer_belly_flop_slam : public SpellScript
{
    PrepareSpellScript(spell_devourer_belly_flop_slam);

    void Weight()
    {
        if (Unit* caster = GetCaster())
            SetHitDamage(int32(caster->CountPctFromMaxHealth(BellyFlopHealthPct)));
    }

    void Register() override
    {
        OnHit += SpellHitFn(spell_devourer_belly_flop_slam::Weight);
    }
};

// Wren's anima pests: they never fight back. The fireflies hover above her cages until a tongue pulls them down; a
// pest that dies up there falls (the core lets a hovering corpse fall).
struct npc_devourer_anima_pest : public CreatureAI
{
    explicit npc_devourer_anima_pest(Creature* creature) : CreatureAI(creature) { }

    void Reset() override
    {
        me->SetReactState(REACT_PASSIVE);
        if (me->GetEntry() == Sisters::NpcPestPerched)
            me->SetDisableGravity(true);
        else
            me->GetMotionMaster()->MoveRandom(3.0f);
    }

    void UpdateAI(uint32 /*diff*/) override { }

    void SpellHit(Unit* /*caster*/, SpellInfo const* spell) override
    {
        if (spell->Id == SpellTonguePull && me->GetEntry() == Sisters::NpcPestPerched)
            me->SetDisableGravity(false);
    }
};

void AddSC_devourer_frogs()
{
    RegisterSpellScript(spell_devourer_tongue_pull);
    RegisterSpellScript(spell_devourer_frog_leap);
    RegisterSpellScript(spell_devourer_swamp_hop_splash);
    RegisterSpellScript(spell_devourer_belly_flop_slam);
    RegisterCreatureAI(npc_devourer_anima_pest);
}
