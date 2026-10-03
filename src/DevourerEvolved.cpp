/*
 * mod-devourer: the evolved forms' scripted gimmicks (task 017, tier 2 of the canvas lines).
 * The spells themselves are rows in 2026_10_03_00_devourer_tier2.sql (tools/evolved_kit.py); what a row cannot do
 * is here. Released under GNU AGPL v3, like AzerothCore.
 *
 *   Greater Plainstrider  Gale Flurry             a dodge blows the attacker back and readies Windrunner Burst
 *   Bloodsnout Worg       Hamstring Cripple       strikes from behind slow the enemy by 70% (spell_proc: 4 sec rest)
 *   Raging Agam'ar        Kinetic Tremor          blows taken charge the plating; at 10 charges it bursts
 *   Vampiric Duskbat      Exsanguinating Frenzy   melee hits heal for 10% of the damage per own bleed on the enemy
 *   Arcane Wraith         Spell Devour            attacks tear a magic buff off the enemy and feed on it
 *   Void Terror           Gravitational Shadows   Nether Bolt's ticks stack a slow; at 10 the enemy collapses
 *   Viper                 Sand Slither            under the ground for 2 sec, then up behind the target (Emerge)
 *                         Cold Blood              its venom ticks 20% harder on slowed or rooted enemies (ColdBlood)
 * The Shadowclaw's opener lives in DevourerForms.cpp (spell_devourer_phase_prowl); the Rockjaw Backbreaker's and the
 * Royal Blue Flutterer's gimmicks are plain procs (spell_proc), no script.
 */

#include "Devourer.h"

#include "ObjectAccessor.h"
#include "Player.h"
#include "ScriptMgr.h"
#include "SpellAuraEffects.h"
#include "SpellAuras.h"
#include "SpellInfo.h"
#include "SpellScript.h"
#include "SpellScriptLoader.h"
#include "Unit.h"
#include <cmath>

using namespace Devourer;

namespace
{
    // tools/evolved_kit.py: shape s uses 9102000 + (s - 16) * 10 + slot
    constexpr uint32 SpellWindrunnerBurst = 9102004;
    constexpr uint32 SpellGaleFlurryKnock = 9102006;
    constexpr uint32 SpellHamstringCripple = 9102016;
    constexpr uint32 SpellTremorPlating = 9102026;
    constexpr uint32 SpellKineticTremor = 9102027;
    constexpr uint8 TremorCharges = 10;
    constexpr uint32 FrenzyPctPerBleed = 10;
    constexpr uint32 SpellDevouredMagic = 9102066;
    constexpr uint32 SpellGravitySlow = 9102086;
    constexpr uint32 SpellAnimaWhirlpool = 9102087;
    constexpr uint8 GravityStacks = 10;
    // The form review's line 1 (2026-10-03): Viper 9102090+
    constexpr uint32 SpellVenomSpit = 9102091;
    constexpr uint32 SpellColdBlood = 9102093;
    constexpr uint32 SpellViperEmerge = 9102096;
    constexpr uint32 ColdBloodPct = 20;

    // A positive magic aura on `target` that a dispel could take, or null.
    Aura* StealableBuff(Unit* target)
    {
        for (auto const& [spellId, app] : target->GetAppliedAuras())
        {
            Aura* aura = app->GetBase();
            if (app->IsPositive() && !aura->IsPassive() && aura->GetSpellInfo()->Dispel == DISPEL_MAGIC)
                return aura;
        }
        return nullptr;
    }
}

// Greater Plainstrider: Gale Flurry. Procs on a dodge (spell_proc: hit mask dodge, 6 sec rest): the attacker is
// blown 5 yards back and Windrunner Burst is ready again.
class spell_devourer_gale_flurry : public AuraScript
{
    PrepareAuraScript(spell_devourer_gale_flurry);

    bool CheckProc(ProcEventInfo& eventInfo)
    {
        Unit* attacker = eventInfo.GetActor();
        return attacker && attacker != GetTarget() && attacker->IsAlive();
    }

    void Proc(ProcEventInfo& eventInfo)
    {
        Unit* owner = GetTarget();
        owner->CastSpell(eventInfo.GetActor(), SpellGaleFlurryKnock, true);
        if (Player* player = owner->ToPlayer())
            player->RemoveSpellCooldown(SpellWindrunnerBurst, true);
    }

    void Register() override
    {
        DoCheckProc += AuraCheckProcFn(spell_devourer_gale_flurry::CheckProc);
        OnProc += AuraProcFn(spell_devourer_gale_flurry::Proc);
    }
};

// Bloodsnout Worg: Hamstring Cripple. Procs on the worg's melee hits (spell_proc: 4 sec rest); only from behind.
class spell_devourer_hamstring_cripple : public AuraScript
{
    PrepareAuraScript(spell_devourer_hamstring_cripple);

    bool CheckProc(ProcEventInfo& eventInfo)
    {
        Unit* target = eventInfo.GetActionTarget();
        return target && target != GetTarget() && target->IsAlive() && target->isInBack(GetTarget());
    }

    void Proc(ProcEventInfo& eventInfo)
    {
        GetTarget()->CastSpell(eventInfo.GetActionTarget(), SpellHamstringCripple, true);
    }

    void Register() override
    {
        DoCheckProc += AuraCheckProcFn(spell_devourer_hamstring_cripple::CheckProc);
        OnProc += AuraProcFn(spell_devourer_hamstring_cripple::Proc);
    }
};

// Raging Agam'ar: Kinetic Tremor. Every melee blow taken adds a charge of Tremor Plating (kept 15 sec); at 10 the
// plating bursts: the Tremor (damage and a 1.5 sec knock-down around the boar).
class spell_devourer_kinetic_tremor : public AuraScript
{
    PrepareAuraScript(spell_devourer_kinetic_tremor);

    bool CheckProc(ProcEventInfo& eventInfo)
    {
        DamageInfo const* damage = eventInfo.GetDamageInfo();
        return damage && damage->GetDamage() && eventInfo.GetActor() != GetTarget();
    }

    void Proc(ProcEventInfo& /*eventInfo*/)
    {
        Unit* owner = GetTarget();
        owner->CastSpell(owner, SpellTremorPlating, true);
        Aura* plating = owner->GetAura(SpellTremorPlating);
        if (!plating || plating->GetStackAmount() < TremorCharges)
            return;
        owner->RemoveAura(plating);
        owner->CastSpell(owner, SpellKineticTremor, true);
    }

    void Register() override
    {
        DoCheckProc += AuraCheckProcFn(spell_devourer_kinetic_tremor::CheckProc);
        OnProc += AuraProcFn(spell_devourer_kinetic_tremor::Proc);
    }
};

// Vampiric Duskbat: Exsanguinating Frenzy. A melee hit heals for 10% of its damage for every bleed (and every stack
// of one) the Devourer has on the enemy.
class spell_devourer_exsanguinating_frenzy : public AuraScript
{
    PrepareAuraScript(spell_devourer_exsanguinating_frenzy);

    bool CheckProc(ProcEventInfo& eventInfo)
    {
        DamageInfo const* damage = eventInfo.GetDamageInfo();
        Unit* target = eventInfo.GetActionTarget();
        return damage && damage->GetDamage() && target && target != GetTarget();
    }

    void Proc(ProcEventInfo& eventInfo)
    {
        Player* player = GetTarget()->ToPlayer();
        Unit* target = eventInfo.GetActionTarget();
        if (!player || !target)
            return;

        uint32 bleeds = 0;
        for (AuraEffect const* effect : target->GetAuraEffectsByType(SPELL_AURA_PERIODIC_DAMAGE))
            if (effect->GetCasterGUID() == player->GetGUID() &&
                (effect->GetSpellInfo()->GetAllEffectsMechanicMask() & (1 << MECHANIC_BLEED)))
                bleeds += effect->GetBase()->GetStackAmount();
        if (!bleeds)
            return;

        uint32 const heal = eventInfo.GetDamageInfo()->GetDamage() * FrenzyPctPerBleed * bleeds / 100;
        if (!heal)
            return;
        HealInfo healInfo(player, player, heal, GetSpellInfo(), GetSpellInfo()->GetSchoolMask());
        player->HealBySpell(healInfo);
    }

    void Register() override
    {
        DoCheckProc += AuraCheckProcFn(spell_devourer_exsanguinating_frenzy::CheckProc);
        OnProc += AuraProcFn(spell_devourer_exsanguinating_frenzy::Proc);
    }
};

// Arcane Wraith: Spell Devour. An attack (spell_proc: 6 sec rest) tears one magic buff off the enemy, and the
// Devourer feeds on it: Devoured Magic, +10% magic damage, 3 stacks.
class spell_devourer_spell_devour : public AuraScript
{
    PrepareAuraScript(spell_devourer_spell_devour);

    bool CheckProc(ProcEventInfo& eventInfo)
    {
        Unit* target = eventInfo.GetActionTarget();
        return target && target != GetTarget() && target->IsAlive() && StealableBuff(target);
    }

    void Proc(ProcEventInfo& eventInfo)
    {
        Unit* owner = GetTarget();
        Unit* target = eventInfo.GetActionTarget();
        Aura* buff = StealableBuff(target);
        if (!buff)
            return;
        target->RemoveAurasDueToSpellByDispel(buff->GetId(), GetId(), buff->GetCasterGUID(), owner);
        owner->CastSpell(owner, SpellDevouredMagic, true);
    }

    void Register() override
    {
        DoCheckProc += AuraCheckProcFn(spell_devourer_spell_devour::CheckProc);
        OnProc += AuraProcFn(spell_devourer_spell_devour::Proc);
    }
};

// Void Terror: Gravitational Shadows, on Nether Bolt's damage over time. Each tick slows the enemy by 5% more; at 10
// stacks the slow is gone and the enemy collapses into an anima whirlpool (Shadow damage around it).
class spell_devourer_gravitational_shadows : public AuraScript
{
    PrepareAuraScript(spell_devourer_gravitational_shadows);

    void Tick(AuraEffect const* /*aurEff*/)
    {
        Unit* caster = GetCaster();
        Unit* target = GetTarget();
        if (!caster || !target->IsAlive())
            return;
        caster->CastSpell(target, SpellGravitySlow, true);
        Aura* slow = target->GetAura(SpellGravitySlow, caster->GetGUID());
        if (!slow || slow->GetStackAmount() < GravityStacks)
            return;
        target->RemoveAura(slow);
        caster->CastSpell(target, SpellAnimaWhirlpool, true);
    }

    void Register() override
    {
        OnEffectPeriodic += AuraEffectPeriodicFn(spell_devourer_gravitational_shadows::Tick, EFFECT_1,
            SPELL_AURA_PERIODIC_DAMAGE);
    }
};

// Viper: Sand Slither. When the 2 sec under the ground are over, the viper comes up behind its target (if it has one
// in reach) with the model's Emerge animation.
class spell_devourer_sand_slither : public AuraScript
{
    PrepareAuraScript(spell_devourer_sand_slither);

    void Surface(AuraEffect const* /*aurEff*/, AuraEffectHandleModes /*mode*/)
    {
        Player* player = GetTarget()->ToPlayer();
        if (!player || !player->IsAlive() || GetTargetApplication()->GetRemoveMode() == AURA_REMOVE_BY_DEATH)
            return;
        Unit* target = player->GetSelectedUnit();
        if (target && target != player && target->IsAlive() && player->IsValidAttackTarget(target) &&
            player->IsWithinDist(target, 40.0f) && target->GetMapId() == player->GetMapId())
        {
            Position behind = target->GetNearPosition(2.0f, float(M_PI));
            player->NearTeleportTo(behind.GetPositionX(), behind.GetPositionY(), behind.GetPositionZ(),
                behind.GetAngle(target));
        }
        player->CastSpell(player, SpellViperEmerge, true);
    }

    void Register() override
    {
        AfterEffectRemove += AuraEffectRemoveFn(spell_devourer_sand_slither::Surface, EFFECT_2, SPELL_AURA_DUMMY,
            AURA_EFFECT_HANDLE_REAL);
    }
};

namespace Devourer
{
    // Viper: Cold Blood. Called for every tick of damage over time (devourer_unit).
    void ColdBlood(Unit* target, Unit* attacker, uint32& damage, SpellInfo const* spell)
    {
        if (!damage || !spell || !target || !attacker || !attacker->IsPlayer() ||
            spell->Id != SpellVenomSpit || !attacker->HasAura(SpellColdBlood))
            return;
        if (target->HasAuraType(SPELL_AURA_MOD_ROOT) || target->HasAuraType(SPELL_AURA_MOD_DECREASE_SPEED))
            damage += damage * ColdBloodPct / 100;
    }
}

void AddSC_devourer_evolved()
{
    RegisterSpellScript(spell_devourer_sand_slither);
    RegisterSpellScript(spell_devourer_gale_flurry);
    RegisterSpellScript(spell_devourer_hamstring_cripple);
    RegisterSpellScript(spell_devourer_kinetic_tremor);
    RegisterSpellScript(spell_devourer_exsanguinating_frenzy);
    RegisterSpellScript(spell_devourer_spell_devour);
    RegisterSpellScript(spell_devourer_gravitational_shadows);
}
