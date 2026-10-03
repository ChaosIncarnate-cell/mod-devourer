/*
 * mod-devourer: the starting forms' scripted abilities (task 009, batch 1: Wolf, Saber, Moth, Boar).
 * The spells themselves are rows in 2026_09_30_08_devourer_start.sql (tools/start_kit.py); what a row cannot do
 * is here. Released under GNU AGPL v3, like AzerothCore.
 *
 *   Wolf   Pack Prowess      strikes on an enemy below 30% call two spectral pups (proc, 15 sec rest in spell_proc)
 *          Ravaging Feast    eats the Devourer's bleeds on the enemy and heals for what they had left
 *   Saber  Anima Shred       10 Anima, 20 from behind
 *          Phase Prowl       leaving it leaves Poised to Strike (+50% on the next strike; the Shadowclaw's also silences)
 *          Shadow Reflexes   needs no script: a proc (dodge/parry, 20 sec rest) that triggers a vanish + Phase Prowl
 *   Moth   Cocoon Metamorphosis   a blow below 25% health is stopped there and the moth is cocooned; once a fight
 *   Boar   Barbed Bristles   15% of a melee hit taken goes back to the attacker as Nature damage
 */

#include "Devourer.h"

#include "Player.h"
#include "ScriptMgr.h"
#include "SpellAuraEffects.h"
#include "SpellAuras.h"
#include "SpellInfo.h"
#include "SpellScript.h"
#include "SpellScriptLoader.h"
#include "Unit.h"
#include <algorithm>

using namespace Devourer;

namespace
{
    constexpr float PackProwessHealthPct = 30.0f;
    constexpr uint32 FeastHealthPctPerBleed = 3;
    constexpr int32 ShredBehindBonus = 10;               // Anima, on top of the spell's 10
    constexpr uint32 BristlesPct = 15;
}

// Wolf: Pack Prowess. The aura procs on the Devourer's melee hits (spell_proc: 15 sec rest); only on an enemy
// below 30% health does it call the pups.
class spell_devourer_pack_prowess : public AuraScript
{
    PrepareAuraScript(spell_devourer_pack_prowess);

    bool CheckProc(ProcEventInfo& eventInfo)
    {
        Unit* target = eventInfo.GetActionTarget();
        return GetTarget()->IsPlayer() && target && target->IsAlive() && target != GetTarget() &&
            target->HealthBelowPct(int32(PackProwessHealthPct));
    }

    void Proc(ProcEventInfo& eventInfo)
    {
        if (Player* player = GetTarget()->ToPlayer())
            sDevourer.CallPups(player, eventInfo.GetActionTarget());
    }

    void Register() override
    {
        DoCheckProc += AuraCheckProcFn(spell_devourer_pack_prowess::CheckProc);
        OnProc += AuraProcFn(spell_devourer_pack_prowess::Proc);
    }
};

// Wolf: Ravaging Feast. Every bleed of this Devourer on the enemy (Tear Throat, the pups' Pup Bite) closes; the
// Devourer is healed for the damage they had left to do, plus 3% of its maximum health for each.
class spell_devourer_ravaging_feast : public SpellScript
{
    PrepareSpellScript(spell_devourer_ravaging_feast);

    void Feast(SpellEffIndex /*effIndex*/)
    {
        Player* player = GetCaster()->ToPlayer();
        Unit* target = GetHitUnit();
        if (!player || !target)
            return;

        uint32 left = 0;
        uint32 bleeds = 0;
        for (uint32 spellId : { SpellWolfTearThroat, SpellWolfPupBite })
        {
            Aura* aura = target->GetAura(spellId, player->GetGUID());
            if (!aura)
                continue;
            for (uint8 i = 0; i < MAX_SPELL_EFFECTS; ++i)
                if (AuraEffect const* effect = aura->GetEffect(i))
                    if (effect->GetAuraType() == SPELL_AURA_PERIODIC_DAMAGE)
                        left += uint32(std::max(0, effect->GetAmount())) *
                            uint32(std::max(0, effect->GetTotalTicks() - int32(effect->GetTickNumber())));
            ++bleeds;
            target->RemoveAura(aura);
        }
        if (!bleeds)
            return;

        uint32 const heal = left + uint32(player->CountPctFromMaxHealth(int32(FeastHealthPctPerBleed * bleeds)));
        HealInfo healInfo(player, player, heal, GetSpellInfo(), GetSpellInfo()->GetSchoolMask());
        player->HealBySpell(healInfo);
    }

    void Register() override
    {
        OnEffectHitTarget += SpellEffectFn(spell_devourer_ravaging_feast::Feast, EFFECT_0, SPELL_EFFECT_DUMMY);
    }
};

// Saber: Anima Shred. The spell gives 10 Anima; struck from behind, 10 more.
class spell_devourer_anima_shred : public SpellScript
{
    PrepareSpellScript(spell_devourer_anima_shred);

    void Behind()
    {
        Player* player = GetCaster()->ToPlayer();
        Unit* target = GetHitUnit();
        if (player && target && target->isInBack(player))
            player->ModifyPower(POWER_RAGE, ShredBehindBonus * 10);
    }

    void Register() override
    {
        AfterHit += SpellHitFn(spell_devourer_anima_shred::Behind);
    }
};

// Saber: Phase Prowl. Coming out of it (by striking, or being found) leaves Poised to Strike: the next strike within
// 5 sec deals 50% more damage (its charge is used up by that strike, spell_proc). Not when cancelled or dead.
class spell_devourer_phase_prowl : public AuraScript
{
    PrepareAuraScript(spell_devourer_phase_prowl);

    void Left(AuraEffect const* /*aurEff*/, AuraEffectHandleModes /*mode*/)
    {
        Unit* target = GetTarget();
        AuraRemoveMode const how = GetTargetApplication()->GetRemoveMode();
        if (!target->IsAlive() || how == AURA_REMOVE_BY_CANCEL || how == AURA_REMOVE_BY_DEATH)
            return;
        // Task 017: the Shadowclaw's Phase Prowl leaves its own Poised to Strike (it also silences).
        target->CastSpell(target, GetId() == SpellShadowclawProwl ? SpellShadowclawPoised : SpellSaberPoised, true);
    }

    void Register() override
    {
        AfterEffectRemove += AuraEffectRemoveFn(spell_devourer_phase_prowl::Left, EFFECT_0, SPELL_AURA_MOD_STEALTH,
            AURA_EFFECT_HANDLE_REAL);
    }
};

// Moth: Cocoon Metamorphosis. An endless absorb that takes nothing, except the part of one blow that would drop
// the moth below 25% health; then the cocoon (Mgr::TryCocoon). Once a fight.
class spell_devourer_cocoon : public AuraScript
{
    PrepareAuraScript(spell_devourer_cocoon);

    void Amount(AuraEffect const* /*aurEff*/, int32& amount, bool& /*canBeRecalculated*/)
    {
        amount = -1;
    }

    void Absorb(AuraEffect* /*aurEff*/, DamageInfo& dmgInfo, uint32& absorbAmount)
    {
        absorbAmount = 0;
        if (Player* player = GetTarget()->ToPlayer())
            sDevourer.TryCocoon(player, dmgInfo.GetDamage(), absorbAmount);
    }

    void Register() override
    {
        DoEffectCalcAmount += AuraEffectCalcAmountFn(spell_devourer_cocoon::Amount, EFFECT_0, SPELL_AURA_SCHOOL_ABSORB);
        OnEffectAbsorb += AuraEffectAbsorbFn(spell_devourer_cocoon::Absorb, EFFECT_0);
    }
};

// Boar: Barbed Bristles. Procs on melee hits taken (spell_proc); 15% of the damage goes back as Nature damage.
class spell_devourer_barbed_bristles : public AuraScript
{
    PrepareAuraScript(spell_devourer_barbed_bristles);

    bool CheckProc(ProcEventInfo& eventInfo)
    {
        DamageInfo const* damage = eventInfo.GetDamageInfo();
        Unit* attacker = eventInfo.GetActor();
        return damage && damage->GetDamage() && attacker && attacker != GetTarget() && attacker->IsAlive();
    }

    void Proc(ProcEventInfo& eventInfo)
    {
        int32 const back = std::max<int32>(1, int32(eventInfo.GetDamageInfo()->GetDamage() * BristlesPct / 100));
        GetTarget()->CastCustomSpell(eventInfo.GetActor(), SpellBoarBristlesHit, &back, nullptr, nullptr, true);
    }

    void Register() override
    {
        DoCheckProc += AuraCheckProcFn(spell_devourer_barbed_bristles::CheckProc);
        OnProc += AuraProcFn(spell_devourer_barbed_bristles::Proc);
    }
};

// Warp Stalker: Warp blinks forward, then Warp Surge (owner, 2026-10-03) makes it run faster for a moment.
class spell_devourer_warp : public SpellScript
{
    PrepareSpellScript(spell_devourer_warp);

    void Surge()
    {
        GetCaster()->CastSpell(GetCaster(), SpellWarpSurge, true);
    }

    void Register() override
    {
        AfterCast += SpellCastFn(spell_devourer_warp::Surge);
    }
};

void AddSC_devourer_forms()
{
    RegisterSpellScript(spell_devourer_pack_prowess);
    RegisterSpellScript(spell_devourer_ravaging_feast);
    RegisterSpellScript(spell_devourer_anima_shred);
    RegisterSpellScript(spell_devourer_phase_prowl);
    RegisterSpellScript(spell_devourer_cocoon);
    RegisterSpellScript(spell_devourer_barbed_bristles);
    RegisterSpellScript(spell_devourer_warp);
}
