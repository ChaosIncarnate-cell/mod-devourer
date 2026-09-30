/*
 * mod-devourer: spell, aura, player, world and command scripts.
 * Released under GNU AGPL v3, like AzerothCore.
 */

#include "Devourer.h"
#include "DevourerSpellIds.h"

#include "Chat.h"
#include "CommandScript.h"
#include "Creature.h"
#include "GridNotifiers.h"
#include "GridNotifiersImpl.h"
#include "ObjectAccessor.h"
#include "Player.h"
#include "ScriptMgr.h"
#include "SpellAuraEffects.h"
#include "SpellAuras.h"
#include "SpellScript.h"
#include "SpellScriptLoader.h"
#include "TemporarySummon.h"
#include "UnitScript.h"

using namespace Devourer;
using namespace Acore::ChatCommands;

// --- Devour: a 3 s channel on a corpse; when it runs its full length the body is eaten --------------------

class spell_devourer_devour : public SpellScript
{
    PrepareSpellScript(spell_devourer_devour);

    SpellCastResult CheckCast()
    {
        Player* player = GetCaster()->ToPlayer();
        if (!player || !sDevourer.IsDevourer(player))
            return SPELL_FAILED_DONT_REPORT;
        Unit* target = GetExplTargetUnit();
        if (sDevourer.IsOwnHatchling(player, target))
            return SPELL_CAST_OK;                        // a Brood eats its own hatchling back
        std::string why;
        if (!sDevourer.CanDevour(player, target ? target->ToCreature() : nullptr, why))
        {
            sDevourer.Tell(player, why);
            return SPELL_FAILED_DONT_REPORT;
        }
        return SPELL_CAST_OK;
    }

    void RememberMeal(SpellEffIndex /*effIndex*/)
    {
        Player* player = GetCaster()->ToPlayer();
        Unit* target = GetHitUnit();
        if (!player || !target)
            return;
        if (sDevourer.IsOwnHatchling(player, target))
        {
            player->InterruptNonMeleeSpells(false);      // no channel: the hatchling is gone in one bite
            sDevourer.Cannibalize(player, target->ToCreature());
            return;
        }
        sDevourer.Get(player).Meal = target->GetGUID();
    }

    void Register() override
    {
        OnCheckCast += SpellCheckCastFn(spell_devourer_devour::CheckCast);
        OnEffectHitTarget += SpellEffectFn(spell_devourer_devour::RememberMeal, EFFECT_0, SPELL_EFFECT_DUMMY);
    }
};

class spell_devourer_devour_aura : public AuraScript
{
    PrepareAuraScript(spell_devourer_devour_aura);

    void ChannelEnded(AuraEffect const* /*aurEff*/, AuraEffectHandleModes /*mode*/)
    {
        Player* player = GetTarget()->ToPlayer();
        if (!player)
            return;
        State& state = sDevourer.Get(player);
        ObjectGuid meal = state.Meal;
        state.Meal.Clear();
        if (GetTargetApplication()->GetRemoveMode() != AURA_REMOVE_BY_EXPIRE)
            return;                                      // moved, hit or cancelled: no meal
        if (meal.IsEmpty())
            meal = player->GetGuidValue(UNIT_FIELD_CHANNEL_OBJECT);
        if (Creature* corpse = ObjectAccessor::GetCreature(*player, meal))
        {
            std::string why;
            if (sDevourer.CanDevour(player, corpse, why))
                sDevourer.Devour(player, corpse);
        }
    }

    void Register() override
    {
        AfterEffectRemove += AuraEffectRemoveFn(spell_devourer_devour_aura::ChannelEnded, EFFECT_1, SPELL_AURA_DUMMY,
            AURA_EFFECT_HANDLE_REAL);
    }
};

// --- Shape forms: every "<Shape> Form" spell is a transform aura; the module puts the body and kit on -------

class spell_devourer_form : public SpellScript
{
    PrepareSpellScript(spell_devourer_form);

    SpellCastResult CheckCast()
    {
        Player* player = GetCaster()->ToPlayer();
        if (!player || !sDevourer.IsDevourer(player) || !sDevourer.ShapeByFormSpell(GetSpellInfo()->Id))
            return SPELL_FAILED_DONT_REPORT;
        if (player->HasAura(GetSpellInfo()->Id) && !GetSpell()->IsTriggered())
            return SPELL_FAILED_ONLY_SHAPESHIFT;         // already wearing it
        return SPELL_CAST_OK;
    }

    void Shifted()
    {
        if (Player* player = GetCaster()->ToPlayer())
            if (!GetSpell()->IsTriggered())
                sDevourer.AfterShift(player, GetSpellInfo()->Id);
    }

    void Register() override
    {
        OnCheckCast += SpellCheckCastFn(spell_devourer_form::CheckCast);
        AfterCast += SpellCastFn(spell_devourer_form::Shifted);
    }
};

class spell_devourer_form_aura : public AuraScript
{
    PrepareAuraScript(spell_devourer_form_aura);

    void Applied(AuraEffect const* /*aurEff*/, AuraEffectHandleModes /*mode*/)
    {
        if (Player* player = GetTarget()->ToPlayer())
            sDevourer.OnFormApplied(player, GetId());
    }

    void Removed(AuraEffect const* /*aurEff*/, AuraEffectHandleModes /*mode*/)
    {
        if (Player* player = GetTarget()->ToPlayer())
            sDevourer.OnFormRemoved(player, GetId());
    }

    void Register() override
    {
        AfterEffectApply += AuraEffectApplyFn(spell_devourer_form_aura::Applied, EFFECT_0, SPELL_AURA_TRANSFORM,
            AURA_EFFECT_HANDLE_REAL);
        AfterEffectRemove += AuraEffectRemoveFn(spell_devourer_form_aura::Removed, EFFECT_0, SPELL_AURA_TRANSFORM,
            AURA_EFFECT_HANDLE_REAL);
    }
};

// --- Glutton: Devour Whole -------------------------------------------------------------------------------

class spell_devourer_devour_whole : public SpellScript
{
    PrepareSpellScript(spell_devourer_devour_whole);

    SpellCastResult CheckCast()
    {
        Player* player = GetCaster()->ToPlayer();
        if (!player || !sDevourer.IsDevourer(player))
            return SPELL_FAILED_DONT_REPORT;
        std::string why;
        if (!sDevourer.CanDevourWhole(player, GetExplTargetUnit(), why))
        {
            sDevourer.Tell(player, why);
            return SPELL_FAILED_DONT_REPORT;
        }
        return SPELL_CAST_OK;
    }

    void Swallow(SpellEffIndex /*effIndex*/)
    {
        Player* player = GetCaster()->ToPlayer();
        Creature* victim = GetHitUnit() ? GetHitUnit()->ToCreature() : nullptr;
        std::string why;
        if (player && victim && sDevourer.CanDevourWhole(player, victim, why))
            sDevourer.DevourWhole(player, victim);
    }

    void Register() override
    {
        OnCheckCast += SpellCheckCastFn(spell_devourer_devour_whole::CheckCast);
        OnEffectHitTarget += SpellEffectFn(spell_devourer_devour_whole::Swallow, EFFECT_0, SPELL_EFFECT_DUMMY);
    }
};

// --- Brood: Hatch Brood (the summon effect makes the guardians; the module dresses them) ------------------

class spell_devourer_hatch_brood : public SpellScript
{
    PrepareSpellScript(spell_devourer_hatch_brood);

    void Hatched()
    {
        if (Player* player = GetCaster()->ToPlayer())
            sDevourer.OnBroodHatched(player);
    }

    void Register() override
    {
        AfterCast += SpellCastFn(spell_devourer_hatch_brood::Hatched);
    }
};

// --- Vashnik: Rising Serpents (the summon effect makes the guardians; the module roots and dresses them) -----

class spell_devourer_rising_serpents : public SpellScript
{
    PrepareSpellScript(spell_devourer_rising_serpents);

    void Risen()
    {
        if (Player* player = GetCaster()->ToPlayer())
            sDevourer.OnSerpentsRisen(player);
    }

    void Register() override
    {
        AfterCast += SpellCastFn(spell_devourer_rising_serpents::Risen);
    }
};

// --- Unlock item: "Idol of <Shape>" teaches a shape until creatures can be devoured for it -----------------

class spell_devourer_unlock : public SpellScript
{
    PrepareSpellScript(spell_devourer_unlock);

    SpellCastResult CheckCast()
    {
        Player* player = GetCaster()->ToPlayer();
        if (!player || !sDevourer.IsDevourer(player))
            return SPELL_FAILED_DONT_REPORT;
        uint32 const shapeId = uint32(GetSpellInfo()->Effects[EFFECT_0].MiscValue);
        if (!sDevourer.FindShape(shapeId))
            return SPELL_FAILED_DONT_REPORT;
        if (sDevourer.Get(player).Shapes.count(shapeId))
        {
            sDevourer.Tell(player, "You already know this shape.");
            return SPELL_FAILED_DONT_REPORT;
        }
        return SPELL_CAST_OK;
    }

    void Unlock(SpellEffIndex /*effIndex*/)
    {
        if (Player* player = GetCaster()->ToPlayer())
            sDevourer.Unlock(player, uint32(GetSpellInfo()->Effects[EFFECT_0].MiscValue), 0, true);
    }

    void Register() override
    {
        OnCheckCast += SpellCheckCastFn(spell_devourer_unlock::CheckCast);
        OnEffectHit += SpellEffectFn(spell_devourer_unlock::Unlock, EFFECT_0, SPELL_EFFECT_DUMMY);
    }
};

// --- Sethrak: Rain of Toads -----------------------------------------------------------------------------
// The passive procs only from Chain Lightning and Coil Strike (plus the internal cooldown in spell_proc).

class spell_devourer_rain_of_toads_passive : public AuraScript
{
    PrepareAuraScript(spell_devourer_rain_of_toads_passive);

    bool CheckProc(ProcEventInfo& eventInfo)
    {
        SpellInfo const* spell = eventInfo.GetSpellInfo();
        return spell && (spell->Id == SpellSethrakChainLightning || spell->Id == SpellSethrakCoilStrikeHit ||
                         spell->Id == SpellVashnikStormChain || spell->Id == SpellVashnikCoilingWhirlHit) &&
            eventInfo.GetActionTarget() && eventInfo.GetActionTarget()->IsAlive();
    }

    void Register() override
    {
        DoCheckProc += AuraCheckProcFn(spell_devourer_rain_of_toads_passive::CheckProc);
    }
};

// Toads fall around the struck enemy and plague up to three enemies nearby.
class spell_devourer_rain_of_toads : public SpellScript
{
    PrepareSpellScript(spell_devourer_rain_of_toads);

    static constexpr uint32 NpcToad = 1420;              // the common Toad critter, as a cosmetic
    static constexpr float Radius = 8.0f;

    void Rain(SpellEffIndex /*effIndex*/)
    {
        Unit* caster = GetCaster();
        Unit* center = GetHitUnit();
        if (!caster || !center)
            return;

        std::list<Unit*> enemies;
        Acore::AnyUnfriendlyUnitInObjectRangeCheck check(center, caster, Radius);
        Acore::UnitListSearcher<Acore::AnyUnfriendlyUnitInObjectRangeCheck> searcher(center, enemies, check);
        Cell::VisitObjects(center, searcher, Radius);
        enemies.remove_if([&](Unit* u) { return !u->IsAlive() || !caster->IsValidAttackTarget(u); });
        enemies.sort([&](Unit* a, Unit* b) { return center->GetDistance(a) < center->GetDistance(b); });

        // The Sethrak's toads plague three, the Vashnik's swarm five.
        uint32 const maxVictims = GetSpellInfo()->Id == SpellVashnikPlagueSwarmHit ? 5 : 3;
        uint32 victims = 0;
        for (Unit* enemy : enemies)
        {
            if (victims++ >= maxVictims)
                break;
            caster->CastSpell(enemy, SpellSethrakPlague, true);
            Position pos = enemy->GetNearPosition(1.5f, frand(0.0f, 2 * float(M_PI)));
            if (TempSummon* toad = caster->SummonCreature(NpcToad, pos, TEMPSUMMON_TIMED_DESPAWN, 6000))
            {
                toad->SetUnitFlag(UNIT_FLAG_NOT_SELECTABLE | UNIT_FLAG_NON_ATTACKABLE);
                toad->SetReactState(REACT_PASSIVE);
                toad->GetMotionMaster()->MoveRandom(4.0f);
            }
        }
    }

    void Register() override
    {
        OnEffectHitTarget += SpellEffectFn(spell_devourer_rain_of_toads::Rain, EFFECT_0, SPELL_EFFECT_DUMMY);
    }
};

// --- Berserker ------------------------------------------------------------------------------------------

// Dragging Roar: the pull flings them in; the stun lands once they have arrived.
class spell_devourer_berserker_roar : public SpellScript
{
    PrepareSpellScript(spell_devourer_berserker_roar);

    void StunOnLanding(SpellEffIndex /*effIndex*/)
    {
        Unit* caster = GetCaster();
        Unit* target = GetHitUnit();
        if (!caster || !target)
            return;
        ObjectGuid const casterGuid = caster->GetGUID();
        target->m_Events.AddEventAtOffset([target, casterGuid]()
        {
            if (!target->IsAlive())
                return;
            if (Unit* roarer = ObjectAccessor::GetUnit(*target, casterGuid))
                roarer->CastSpell(target, SpellBerserkerRoarStun, true);
        }, 800ms);
    }

    void Register() override
    {
        OnEffectHitTarget += SpellEffectFn(spell_devourer_berserker_roar::StunOnLanding, EFFECT_1, SPELL_EFFECT_DUMMY);
    }
};

// Smash hits a stunned enemy 50% harder.
class spell_devourer_berserker_smash : public SpellScript
{
    PrepareSpellScript(spell_devourer_berserker_smash);

    void Crush()
    {
        Unit* target = GetHitUnit();
        if (target && target->HasAuraType(SPELL_AURA_MOD_STUN))
            SetHitDamage(GetHitDamage() * 3 / 2);
    }

    void Register() override
    {
        OnHit += SpellHitFn(spell_devourer_berserker_smash::Crush);
    }
};

// Blood Scent: once a second, one stack of Scent of Blood for every living unit within 30 yards below half health.
class spell_devourer_blood_scent : public AuraScript
{
    PrepareAuraScript(spell_devourer_blood_scent);

    static constexpr float Range = 30.0f;
    static constexpr uint8 MaxStacks = 10;

    void Sniff(AuraEffect const* /*aurEff*/)
    {
        Unit* owner = GetTarget();
        std::list<Unit*> units;
        Acore::AnyUnitInObjectRangeCheck check(owner, Range);
        Acore::UnitListSearcher<Acore::AnyUnitInObjectRangeCheck> searcher(owner, units, check);
        Cell::VisitObjects(owner, searcher, Range);

        uint32 bleeding = 0;
        for (Unit* unit : units)
            if (unit != owner && unit->IsAlive() && unit->GetHealthPct() < 50.0f && !unit->IsCritter())
                ++bleeding;

        if (!bleeding)
        {
            owner->RemoveAurasDueToSpell(SpellBerserkerBloodScentBuff);
            return;
        }
        uint8 const stacks = uint8(std::min<uint32>(bleeding, MaxStacks));
        Aura* scent = owner->GetAura(SpellBerserkerBloodScentBuff);
        if (!scent)
            scent = owner->AddAura(SpellBerserkerBloodScentBuff, owner);
        if (scent && scent->GetStackAmount() != stacks)
            scent->SetStackAmount(stacks);
    }

    void Removed(AuraEffect const* /*aurEff*/, AuraEffectHandleModes /*mode*/)
    {
        GetTarget()->RemoveAurasDueToSpell(SpellBerserkerBloodScentBuff);
    }

    void Register() override
    {
        OnEffectPeriodic += AuraEffectPeriodicFn(spell_devourer_blood_scent::Sniff, EFFECT_0, SPELL_AURA_PERIODIC_DUMMY);
        AfterEffectRemove += AuraEffectRemoveFn(spell_devourer_blood_scent::Removed, EFFECT_0, SPELL_AURA_PERIODIC_DUMMY,
            AURA_EFFECT_HANDLE_REAL);
    }
};

// --- ChaosCore0.3: the Glutton ---------------------------------------------------------------------------

// Regurgitate: releases the ability of the enemy swallowed with Devour Whole (the button only exists while one
// is held in).
class spell_devourer_regurgitate : public SpellScript
{
    PrepareSpellScript(spell_devourer_regurgitate);

    SpellCastResult CheckCast()
    {
        Player* player = GetCaster()->ToPlayer();
        if (!player || !sDevourer.IsDevourer(player) || !sDevourer.Get(player).StomachFull)
            return SPELL_FAILED_DONT_REPORT;
        return SPELL_CAST_OK;
    }

    void Release(SpellEffIndex /*effIndex*/)
    {
        if (Player* player = GetCaster()->ToPlayer())
            sDevourer.ReleaseStomach(player, false);
    }

    void Register() override
    {
        OnCheckCast += SpellCheckCastFn(spell_devourer_regurgitate::CheckCast);
        OnEffectHit += SpellEffectFn(spell_devourer_regurgitate::Release, EFFECT_0, SPELL_EFFECT_DUMMY);
    }
};

// Meal: Grave (an undead meal): a share of the melee damage dealt heals the Devourer.
class spell_devourer_meal_grave : public AuraScript
{
    PrepareAuraScript(spell_devourer_meal_grave);

    bool CheckProc(ProcEventInfo& eventInfo)
    {
        DamageInfo* damage = eventInfo.GetDamageInfo();
        return damage && damage->GetDamage() > 0;
    }

    void Leech(AuraEffect const* aurEff, ProcEventInfo& eventInfo)
    {
        PreventDefaultAction();
        uint32 const heal = CalculatePct(eventInfo.GetDamageInfo()->GetDamage(), aurEff->GetAmount());
        if (heal && GetTarget()->IsAlive())
            GetTarget()->ModifyHealth(int32(heal));
    }

    void Register() override
    {
        DoCheckProc += AuraCheckProcFn(spell_devourer_meal_grave::CheckProc);
        OnEffectProc += AuraEffectProcFn(spell_devourer_meal_grave::Leech, EFFECT_0, SPELL_AURA_DUMMY);
    }
};

// Digested: while it lasts, the meal buff the Devourer carries is twice as strong.
class spell_devourer_digested : public AuraScript
{
    PrepareAuraScript(spell_devourer_digested);

    static constexpr uint32 Meals[] = { SpellMealMeat, SpellMealFlesh, SpellMealEssence, SpellMealGrave,
                                        SpellMealDragon, SpellMealDemon };
    uint32 _meal = 0;

    void Scale(uint32 mealId, bool up)
    {
        Aura* meal = GetTarget()->GetAura(mealId);
        if (!meal)
            return;
        for (uint8 i = 0; i < MAX_SPELL_EFFECTS; ++i)
            if (AuraEffect* effect = meal->GetEffect(i))
                effect->ChangeAmount(up ? effect->GetAmount() * 2 : effect->GetAmount() / 2);
    }

    void Applied(AuraEffect const* /*aurEff*/, AuraEffectHandleModes /*mode*/)
    {
        for (uint32 meal : Meals)
            if (GetTarget()->HasAura(meal))
            {
                _meal = meal;
                Scale(meal, true);
                break;
            }
    }

    void Removed(AuraEffect const* /*aurEff*/, AuraEffectHandleModes /*mode*/)
    {
        if (_meal)
            Scale(_meal, false);
        _meal = 0;
    }

    void Register() override
    {
        AfterEffectApply += AuraEffectApplyFn(spell_devourer_digested::Applied, EFFECT_0, SPELL_AURA_DUMMY,
            AURA_EFFECT_HANDLE_REAL);
        AfterEffectRemove += AuraEffectRemoveFn(spell_devourer_digested::Removed, EFFECT_0, SPELL_AURA_DUMMY,
            AURA_EFFECT_HANDLE_REAL);
    }
};

// Bile Coating (Digested choice): absorbs 5% of maximum health for every stack of Gorged, at least 5%.
class spell_devourer_bile_coating : public AuraScript
{
    PrepareAuraScript(spell_devourer_bile_coating);

    void Amount(AuraEffect const* /*aurEff*/, int32& amount, bool& canBeRecalculated)
    {
        canBeRecalculated = false;
        Unit* owner = GetUnitOwner();
        if (!owner)
            return;
        uint32 stacks = 1;
        if (Aura const* gorged = owner->GetAura(SpellGorged))
            stacks = std::max<uint32>(1, gorged->GetStackAmount());
        amount = int32(owner->CountPctFromMaxHealth(int32(5 * stacks)));
    }

    void Register() override
    {
        DoEffectCalcAmount += AuraEffectCalcAmountFn(spell_devourer_bile_coating::Amount, EFFECT_0,
            SPELL_AURA_SCHOOL_ABSORB);
    }
};

// --- ChaosCore0.3: the Baby Berserker ------------------------------------------------------------------

// Overrun: a 0.5 sec wind-up (ReadySpellOmni), then the run (the module moves the Devourer and knocks over what
// is in the way).
class spell_devourer_baby_overrun : public SpellScript
{
    PrepareSpellScript(spell_devourer_baby_overrun);

    SpellCastResult CheckCast()
    {
        Player* player = GetCaster()->ToPlayer();
        if (!player || !sDevourer.IsDevourer(player))
            return SPELL_FAILED_DONT_REPORT;
        if (player->HasUnitState(UNIT_STATE_ROOT))
            return SPELL_FAILED_ROOTED;
        sDevourer.OverrunWindup(player);
        return SPELL_CAST_OK;
    }

    void Run(SpellEffIndex /*effIndex*/)
    {
        if (Player* player = GetCaster()->ToPlayer())
            sDevourer.Overrun(player);
    }

    void Register() override
    {
        OnCheckCast += SpellCheckCastFn(spell_devourer_baby_overrun::CheckCast);
        OnEffectHit += SpellEffectFn(spell_devourer_baby_overrun::Run, EFFECT_0, SPELL_EFFECT_DUMMY);
    }
};

// Gnaw: the grapple opens a bleeding wound; every second of it is a bite that heals the Devourer.
class spell_devourer_baby_gnaw : public SpellScript
{
    PrepareSpellScript(spell_devourer_baby_gnaw);

    void Wound()
    {
        Unit* caster = GetCaster();
        Unit* target = GetHitUnit();
        if (caster && target && target->IsAlive())
            caster->CastSpell(target, SpellBabyGnawBleed, true);
    }

    void Register() override
    {
        AfterHit += SpellHitFn(spell_devourer_baby_gnaw::Wound);
    }
};

class spell_devourer_baby_gnaw_aura : public AuraScript
{
    PrepareAuraScript(spell_devourer_baby_gnaw_aura);

    void Bite(AuraEffect const* /*aurEff*/)
    {
        sDevourer.GnawBite(GetCaster(), GetTarget());
    }

    void Register() override
    {
        OnEffectPeriodic += AuraEffectPeriodicFn(spell_devourer_baby_gnaw_aura::Bite, EFFECT_0,
            SPELL_AURA_PERIODIC_DUMMY);
    }
};

// Void Frenzy: the roar is the spell itself; the five strikes follow.
class spell_devourer_baby_void_frenzy : public SpellScript
{
    PrepareSpellScript(spell_devourer_baby_void_frenzy);

    void Frenzy(SpellEffIndex /*effIndex*/)
    {
        Player* player = GetCaster()->ToPlayer();
        if (player && GetHitUnit())
            sDevourer.VoidFrenzy(player, GetHitUnit());
    }

    void Register() override
    {
        OnEffectHitTarget += SpellEffectFn(spell_devourer_baby_void_frenzy::Frenzy, EFFECT_0, SPELL_EFFECT_DUMMY);
    }
};

// --- player lifecycle ----------------------------------------------------------------------------------

class devourer_player : public PlayerScript
{
public:
    devourer_player() : PlayerScript("devourer_player") { }

    void OnPlayerLogin(Player* player) override
    {
        if (!sDevourer.IsDevourer(player))
            return;
        sDevourer.TeachBasics(player);
        sDevourer.Restore(player);
    }

    void OnPlayerLogout(Player* player) override
    {
        sDevourer.Forget(player);
    }

    void OnPlayerResurrect(Player* player, float /*restorePercent*/, bool& /*applySickness*/) override
    {
        sDevourer.Restore(player);
    }

    void OnPlayerLevelChanged(Player* player, uint8 /*oldLevel*/) override
    {
        sDevourer.TeachBasics(player);
    }

    void OnPlayerUpdate(Player* player, uint32 diff) override
    {
        sDevourer.OnUpdate(player, diff);
    }

    void OnPlayerSpellCast(Player* player, Spell* spell, bool /*skipCheck*/) override
    {
        if (sDevourer.IsDevourer(player))
            sDevourer.MirrorSpell(player, spell);
    }

    // Growth tasks: kills made in a form.
    void OnPlayerCreatureKill(Player* player, Creature* killed) override
    {
        if (sDevourer.IsDevourer(player))
            sDevourer.TaskEvent(player, TaskKill, killed->GetCreatureType());
    }

    // The core only knows the ten classes. Where it asks "is this a warrior?" for stats (attack power from
    // strength and agility), a Devourer answers yes; for the armour it may wear it answers "a rogue" (leather,
    // task 006), and it never counts as a shield bearer. Warrior and rogue abilities stay off.
    Optional<bool> OnPlayerIsClass(Player const* player, Classes unitClass, ClassContext context) override
    {
        bool const asWarrior = unitClass == CLASS_WARRIOR && context == CLASS_CONTEXT_STATS;
        bool const asRogue = unitClass == CLASS_ROGUE && context == CLASS_CONTEXT_EQUIP_ARMOR_CLASS;
        if (!asWarrior && !asRogue)
            return std::nullopt;
        if (!sDevourer.IsDevourer(player))
            return std::nullopt;
        return true;
    }
};

// Brood hatchlings devour what dies near them.
class devourer_unit : public UnitScript
{
public:
    devourer_unit() : UnitScript("devourer_unit") { }

    void OnUnitDeath(Unit* unit, Unit* killer) override
    {
        if (Creature* victim = unit->ToCreature())
            sDevourer.OnCreatureDeath(victim, killer);
    }

    // Growth tasks: hits taken in a form, by school.
    void ModifyMeleeDamage(Unit* target, Unit* attacker, uint32& damage) override
    {
        if (Player* player = target->ToPlayer())
            if (damage && sDevourer.IsDevourer(player))
                sDevourer.TaskEvent(player, TaskHitBy, SPELL_SCHOOL_MASK_NORMAL);
        // ChaosCore0.2: a Devourer's own auto-attack hits fill Hunger a little.
        if (Player* player = attacker ? attacker->ToPlayer() : nullptr)
            if (damage)
                sDevourer.OnAutoAttackHit(player);
    }

    void ModifySpellDamageTaken(Unit* target, Unit* /*attacker*/, int32& damage, SpellInfo const* spellInfo) override
    {
        if (Player* player = target->ToPlayer())
            if (damage > 0 && spellInfo && sDevourer.IsDevourer(player))
                sDevourer.TaskEvent(player, TaskHitBy, spellInfo->GetSchoolMask());
    }
};

class devourer_world : public WorldScript
{
public:
    devourer_world() : WorldScript("devourer_world") { }

    void OnAfterConfigLoad(bool /*reload*/) override { sDevourer.LoadConfig(); }
    // Switched off, the module does not even read its tables (they may not be installed).
    void OnStartup() override
    {
        if (sDevourer.Enabled())
            sDevourer.LoadWorldData();
    }
};

// --- commands: .devour, .devour skin <shape> <display>, .devour unlock <shape> (GM), .devour reload (GM) --

class devourer_commands : public CommandScript
{
public:
    devourer_commands() : CommandScript("devourer_commands") { }

    ChatCommandTable GetCommands() const override
    {
        static ChatCommandTable devourTable =
        {
            { "",       HandleList,   SEC_PLAYER,        Console::No },
            { "skin",   HandleSkin,   SEC_PLAYER,        Console::No },
            { "unlock", HandleUnlock, SEC_GAMEMASTER,    Console::No },
            { "reload", HandleReload, SEC_ADMINISTRATOR, Console::Yes },
        };
        static ChatCommandTable commandTable = { { "devour", devourTable } };
        return commandTable;
    }

    static bool HandleList(ChatHandler* handler)
    {
        Player* player = handler->GetSession()->GetPlayer();
        if (!sDevourer.IsDevourer(player))
        {
            handler->SendSysMessage("Only a Devourer has shapes.");
            return true;
        }
        sDevourer.ListShapes(player);
        return true;
    }

    static bool HandleSkin(ChatHandler* handler, std::string name)
    {
        Player* player = handler->GetSession()->GetPlayer();
        if (sDevourer.IsDevourer(player))
            sDevourer.ChooseSkin(player, name);
        return true;
    }

    static bool HandleUnlock(ChatHandler* handler, uint32 shapeId)
    {
        Player* target = handler->getSelectedPlayerOrSelf();
        if (!target || !sDevourer.IsDevourer(target))
        {
            handler->SendSysMessage("Select a Devourer.");
            return true;
        }
        if (!sDevourer.Unlock(target, shapeId, 0, true))
            handler->PSendSysMessage("No shape {}.", shapeId);
        return true;
    }

    static bool HandleReload(ChatHandler* handler)
    {
        if (!sDevourer.Enabled())
        {
            handler->SendSysMessage("mod-devourer is switched off (Devourer.Enable = 0).");
            return true;
        }
        sDevourer.LoadWorldData();
        handler->SendSysMessage("Devourer shapes reloaded.");
        return true;
    }
};

void AddSC_devourer()
{
    RegisterSpellAndAuraScriptPair(spell_devourer_devour, spell_devourer_devour_aura);
    RegisterSpellAndAuraScriptPair(spell_devourer_form, spell_devourer_form_aura);
    RegisterSpellScript(spell_devourer_unlock);
    RegisterSpellScript(spell_devourer_devour_whole);
    RegisterSpellScript(spell_devourer_hatch_brood);
    RegisterSpellScript(spell_devourer_berserker_roar);
    RegisterSpellScript(spell_devourer_berserker_smash);
    RegisterSpellScript(spell_devourer_blood_scent);
    RegisterSpellScript(spell_devourer_rising_serpents);
    RegisterSpellScript(spell_devourer_rain_of_toads);
    RegisterSpellScript(spell_devourer_rain_of_toads_passive);
    // ChaosCore0.3
    RegisterSpellScript(spell_devourer_regurgitate);
    RegisterSpellScript(spell_devourer_meal_grave);
    RegisterSpellScript(spell_devourer_digested);
    RegisterSpellScript(spell_devourer_bile_coating);
    RegisterSpellScript(spell_devourer_baby_overrun);
    RegisterSpellAndAuraScriptPair(spell_devourer_baby_gnaw, spell_devourer_baby_gnaw_aura);
    RegisterSpellScript(spell_devourer_baby_void_frenzy);
    new devourer_player();
    new devourer_unit();
    new devourer_world();
    new devourer_commands();
}
