/*
 * mod-devourer: the form mechanics the kits left out (task 019). Released under GNU AGPL v3, like AzerothCore.
 * The spells are rows in 2026_10_03_00_devourer_tier2.sql (tools/evolved_kit.py); what a row cannot do is here.
 *
 *   Proto-Drake            Fire Breath            the worn colouring picks the element of the breath
 */

#include "Devourer.h"

#include "Player.h"
#include "ScriptMgr.h"
#include "SpellScript.h"
#include "SpellScriptLoader.h"
#include "Unit.h"

using namespace Devourer;

namespace
{
    // tools/evolved_kit.py: shape s uses 9102000 + (s - 16) * 10 + slot
    constexpr uint32 SpellFireBreathFire = 9102206;       // Proto-Drake (36), slots 6-9: one helper per element
    constexpr uint32 SpellFireBreathNature = 9102207;
    constexpr uint32 SpellFireBreathStorm = 9102208;
    constexpr uint32 SpellFireBreathFrost = 9102209;

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
    RegisterSpellScript(spell_devourer_proto_breath);
}
