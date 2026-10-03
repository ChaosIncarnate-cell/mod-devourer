/*
 * mod-devourer: the Devourer, a class that becomes what it eats.
 * Released under GNU AGPL v3, like AzerothCore.
 *
 * Class 10 (CLASS_DEVOURER, see core-patch/; the id is Devourer.ClassId). The Devourer devours slain creatures
 * to unlock their shapes, then shifts between them. Every shape brings four abilities and a passive, learned while it is worn.
 * Anima (the rage bar; called Hunger before 2026-09-30) is the only resource: strong abilities, spec abilities and
 * active talents cost it; devouring, its own blows and its pet's kills gather it (Concentrate is gone, task 015); it
 * does not drain away out of combat. All shapes share one shift cooldown.
 *
 * Data:
 *   world      devourer_shape          one row per shape: its form spell, base display, kit, passive
 *              devourer_shape_source   creature entry -> shape (+ the colouring that creature grants)
 *              devourer_skin           display -> shape and colouring name
 *              devourer_shape_family   creature family -> shape (task 009: any creature of it gives the shape,
 *                                      each of its looks is a colouring, built at startup)
 *              devourer_favourite_food shape -> creature type / family / name part: 2x Bio Points
 *   characters character_devourer_shape    unlocked shapes, chosen colouring
 *              character_devourer_skin     unlocked colourings
 *              character_devourer_worn    the shape worn at logout
 */

#ifndef MOD_DEVOURER_H
#define MOD_DEVOURER_H

#include "Define.h"
#include "ObjectGuid.h"
#include "DevourerTalentIds.h"
#include <array>
#include <deque>
#include <functional>
#include <list>
#include <map>
#include <set>
#include <string>
#include <unordered_map>
#include <vector>

class Creature;
class Unit;
class Player;
class Spell;
class DamageInfo;
class SpellInfo;
class Aura;

struct SummonPropertiesEntry;

namespace Devourer
{
    // Task 016: the properties every summon of this module uses (hatchlings, echoes, pups): a guardian that is NOT of
    // category pet, so it never takes the pet slot (Unit::SetMinion dismisses the hunter-like pet for those).
    SummonPropertiesEntry const* GuardianProperties();

    constexpr uint8 KitSize = 4;
    constexpr uint32 ItemSethrakIdol = 9100100;   // teaches the first shape until it can be devoured in the world
    constexpr uint32 NpcHatchling = 9101100;      // Brood hatchling (guardian from Hatch Brood)
    constexpr uint32 NpcEcho = 9101101;           // Skinchanger: the echo a left shape leaves behind
    constexpr uint32 DefaultBroodDisplay = 4312;  // a serpent, when a shape names no kin
    constexpr uint32 SpellGhostVisual = 22650;    // "Ghost Visual": echoes are translucent
    constexpr uint32 NpcRisingSerpent = 9101102;  // Vashnik: stationary serpents that repeat its spells
    constexpr uint32 RisingSerpentDisplays[2] = { 991040, 991045 };   // Twinfangs: purple, pale teal
    constexpr uint32 EmoteReadySpellOmni = 917;   // ChaosCore0.3: ONESHOT_READYSPELLOMNI, Overrun's wind-up

    // The base kit every Devourer has from level 1 (tools/start_kit.py, 2026_09_30_08).
    constexpr uint32 SpellRush = 9100990;         // no target needed: the module runs 20 yards straight ahead
    constexpr uint32 SpellRushHit = 9100991;      // what Rush does to an enemy in its path
    // 9100992 was Concentrate (task 015: removed, the pet replaced it; TeachBasics takes it from older characters)
    constexpr uint32 SpellConcentrateOld = 9100992;
    constexpr uint32 SpellAnima = 9100993;        // hidden passive: Anima does not drain away out of combat
    // Class skill lines: the Devourer's three spellbook tabs, one per talent tree (tasks 008, 011, 2026_09_30_09)
    constexpr uint32 SkillGlutton = 900;
    constexpr uint32 SkillSkinchanger = 901;
    constexpr uint32 SkillBrood = 902;
    constexpr uint32 SkillTabs[] = { SkillGlutton, SkillSkinchanger, SkillBrood };
    // Task 015: the hunter's pet spells (stock 3.3.5a). The Devourer answers "hunter" to CLASS_CONTEXT_PET, so the core's
    // own pet code does the rest (tame, call, dismiss, revive, feed, the pet bar, the stable).
    constexpr uint32 SpellTameBeast = 1515;
    constexpr uint32 SpellCallPet = 883;
    constexpr uint32 SpellDismissPet = 2641;
    constexpr uint32 SpellRevivePet = 982;
    constexpr uint32 SpellMendPet = 136;
    constexpr uint32 SpellFeedPet = 6991;
    constexpr uint32 SpellBeastLore = 1462;
    constexpr uint32 PetSpells[] = { SpellTameBeast, SpellCallPet, SpellDismissPet, SpellRevivePet, SpellMendPet,
                                     SpellFeedPet, SpellBeastLore };
    constexpr char const* MenuPrefix = "DVR";     // addon messages for the shape menu (client: DevourerMenu.lua)

    // Task 009, starter forms batch 1 (tools/start_kit.py, 2026_09_30_08): the spells the module's scripts use.
    constexpr uint32 SpellWolfTearThroat = 9100911;      // its bleed: Ravaging Feast eats it
    constexpr uint32 SpellWolfPupBite = 9100916;         // the spectral pups' bleed (Pack Prowess)
    constexpr uint32 SpellSaberPhaseProwl = 9100932;
    constexpr uint32 SpellSaberPoised = 9100936;         // Poised to Strike: Phase Prowl's opener bonus
    constexpr uint32 SpellSniff = 9100995;               // task 013: toggle aura, marks prey on the client (Mgr::SniffScan)
    constexpr float SniffRadius = 40.0f;                 // yards around the Devourer
    constexpr uint32 SniffInterval = 3000;               // ms between two scans
    constexpr uint8 SniffMaxNames = 60;                  // names sent per scan
    constexpr uint32 SpellShapeStride = 9100994;         // every shape runs 15% faster (owner, 2026-10-03)
    constexpr uint32 SpellWarpSurge = 9101006;           // Warp Stalker: the speed after Warp (spell_devourer_warp)
    constexpr uint32 SpellMothSilkenCocoon = 9100946;    // Cocoon Metamorphosis wraps the moth in it
    constexpr uint32 SpellBoarBristlesHit = 9100956;     // Barbed Bristles' Nature damage
    // Task 017, the evolved forms (tools/evolved_kit.py, 2026_10_03_00): shape s uses 9102000 + (s - 16) * 10 + slot.
    constexpr uint32 SpellShadowclawProwl = 9102032;     // the Shadowclaw's Phase Prowl ...
    constexpr uint32 SpellShadowclawPoised = 9102037;    // ... leaves this Poised to Strike (it also silences)
     // addon messages for the shape menu (client: DevourerMenu.lua)

    // The three talent trees (tab pages 0-2); see Mgr::SpecOf.
    enum Spec : uint32
    {
        SpecNone        = 0,
        SpecGlutton     = 1,
        SpecSkinchanger = 2,
        SpecBrood       = 3,
    };

    struct Shape
    {
        uint32 Id = 0;
        std::string Name;
        uint32 FormSpell = 0;                    // the spellbook spell that shifts into this shape
        uint32 Display = 0;                      // base colouring
        float Scale = 1.0f;
        std::array<uint32, KitSize> Kit{};       // the four abilities
        uint32 Passive = 0;
        uint32 BroodDisplay = 0;                 // what a Brood's hatchlings look like while this shape is worn
    };

    struct Source
    {
        uint32 ShapeId = 0;
        uint32 Display = 0;                      // colouring this creature grants; 0 = the base one
    };

    // Task 009: a meal is a shape's favourite food when every field a rule sets matches (0 / empty = any).
    struct FoodRule
    {
        uint32 Type = 0;                         // creature type
        uint32 Family = 0;                       // creature family
        std::string NamePart;                    // lower case; the creature's name contains it
        std::string Label;                       // what the menu shows; empty = the type or family name
    };

    struct Skin
    {
        uint32 ShapeId = 0;
        std::string Name;                        // what .devour skin <name> takes
        uint32 BroodDisplay = 0;                 // a Brood's hatchlings while this colouring is worn
        bool Free = false;                       // task 017: comes with the shape (the retail looks of older forms)
    };

    // Growth: a form earns Bio Points (BP) from what it eats while worn, weighted by its diet and the meal's rarity.
    // With enough BP, the level and its tasks done, it evolves into the next form of its line.
    enum TaskKind : uint8
    {
        TaskKill         = 1,                    // kill creatures of a type (value = creature type, 0 = any)
        TaskHitBy        = 2,                    // be hit by a school (value = school mask)
        TaskDevourRarity = 3,                    // devour creatures at least this rare (value = rarity multiplier)
        TaskDevourType   = 4,                    // devour creatures of a type (value = creature type)
        TaskDevourName   = 5,                    // devour creatures whose name holds one of name_part ('|'-separated),
                                                 // value = creature type (0 = any)
        TaskSpellHit     = 6,                    // hit an enemy with a spell (value = spell id; the frog line's scripts)
        // Task 017 (the evolved forms):
        TaskDevourFamily = 7,                    // devour creatures of a family (value = creature_template.family)
        TaskDevourEntry  = 8,                    // devour one creature (value = creature entry)
        TaskSpellCast    = 9,                    // use a spell (value = spell id; every cast counts)
        TaskDealDamage   = 10,                   // deal damage (value = school mask, 0 = any; count = damage)
        TaskTakeDamage   = 11,                   // take damage (value = school mask, 0 = any; count = damage)
        TaskHeal         = 12,                   // heal yourself (count = health)
    };

    struct EvolutionTask
    {
        uint32 Id = 0;
        uint8 Kind = 0;
        uint32 Value = 0;
        uint32 Count = 0;
        std::string Text;
        std::vector<std::string> Names;          // TaskDevourName: lower-case name parts
    };

    struct Evolution
    {
        uint32 From = 0;
        uint32 To = 0;
        uint32 Bp = 0;
        uint8 MinLevel = 0;
        bool AnyTask = false;                    // the frog line (2026-10-02): any one task is enough, not all
        uint32 Quest = 0;                        // task 018: its molt quest (handing it in is the evolution); 0 = none
        std::vector<EvolutionTask> Tasks;
    };

    struct Owned
    {
        uint32 Eaten = 0;
        uint32 Display = 0;                      // chosen colouring; 0 = base
        std::set<uint32> Skins;                  // unlocked colourings (base is always available)
    };

    struct State
    {
        std::map<uint32, Owned> Shapes;          // shape id -> progress
        uint32 Worn = 0;                         // shape worn now (and restored at login)

        // runtime only
        uint32 Pending = 0;                      // set just before a form spell lands
        ObjectGuid Meal;                         // corpse being devoured
        std::vector<uint32> Granted;             // kit spells learned for the worn shape
        bool Loaded = false;
        uint32 SyncTimer = 0;                    // spec abilities are re-checked every few seconds
        uint32 SyncedSpec = 0xFFFFFFFF;
        uint8 SyncedLevel = 0;                   // spec abilities also open by level (placeholders at 20/40/60)
        std::set<ObjectGuid> Eaten;              // corpses already fed on (they stay for their loot)
        std::deque<ObjectGuid> Kills;            // task 016: the last kills of the Devourer, its pet, hatchlings and echoes
        std::map<uint32, uint32> Bio;            // shape id -> Bio Points earned while worn
        std::map<std::pair<uint32, uint32>, uint32> Tasks;   // (evolved shape, task id) -> progress
        bool GrowthDirty = false;

        // Hotbar (Copus55, 2026-09-28): where the player keeps each shape's abilities, saved per shape.
        std::map<uint32, std::map<uint32, uint8>> Bar;   // shape id -> kit spell -> action slot (NotOnBar = taken off)
        uint32 KitShape = 0;                             // runtime: the shape whose kit is on the bars now

        // ChaosCore0.3, the Glutton (runtime only)
        uint32 GorgedIdle = 0;                           // ms out of combat while Gorged
        uint32 StomachSpell = 0;                         // Regurgitate: the swallowed enemy's ability, held in
        uint32 StomachLeft = 0;                          // ms until it bursts out by itself
        bool StomachFull = false;
        uint32 OverrunWindup = 0;                        // getMSTime() of the last Overrun wind-up emote

        // Task 009 (runtime only)
        bool CocoonUsed = false;                         // Moth: Cocoon Metamorphosis, once per fight

        // Task 013 (runtime only)
        uint32 SniffTimer = 0;                           // ms until the next scan while Sniff is on
        // Task 015 (runtime only; times are getMSTime() values)
        uint32 BroodEmoteAt = 0;                         // task 016: getMSTime() of the last hatchling eating emote
        uint32 PerkTimer = 0;                            // ms until the talent auras are worked out again
        uint32 ShiftAt = 0;                              // the last shift
        uint32 LastLeftShape = 0;                        // the shape left last (Stolen Instinct, Echo Flesh)
        std::map<uint32, uint32> LeftAt;                 // shape id -> when it was left (Restless Form)
        std::vector<std::pair<uint32, uint32>> Recent;   // (shape id, when) shapes worn lately (Unfixed Nature)
        uint32 ArmourUntil = 0, DamageUntil = 0, SpeedUntil = 0, HasteUntil = 0, DodgeUntil = 0;   // after a shift
        uint32 ShedReady = 0;                            // Shed Skin
        uint32 ManyUntil = 0;                            // Form of Many
        uint32 WornFacesUntil = 0;                       // Worn Faces
        uint32 NestGuardUntil = 0;                       // Nest Guard
        uint32 ChallengeUntil = 0;                       // Devouring Challenge
        std::set<ObjectGuid> ChallengeFed;               // enemies that already fed the Devourer in that roar
        uint32 FatReady = 0;                             // Fat Reserves
        uint32 LastSupperReady = 0;
        uint32 WrathUntil = 0;                           // Mother's Wrath
        uint8 WrathStacks = 0;
        uint32 BloodMilkUntil = 0;
        uint32 HatchCount = 0;                           // Many Mouths: every second Hatch Brood
        uint32 LastMealSpell = 0;                        // Grand Appetite: the meal buff before this one
        ObjectGuid PetSeen;                              // the pet the size hint was last set on
        float PetScale = 0.0f;
        uint32 QueenTimer = 0;
    };

    // A time that has been set and has not come yet (getMSTime() wraps, so the difference is compared).
    inline bool Active(uint32 until, uint32 now)
    {
        return until && int32(until - now) > 0;
    }

    constexpr uint8 NotOnBar = 255;                      // the player took that ability off the bars

    class Mgr
    {
    public:
        static Mgr& Instance();

        void LoadConfig();
        void LoadWorldData();

        [[nodiscard]] bool Enabled() const { return _enabled; }
        [[nodiscard]] bool IsDevourer(Player const* player) const;
        [[nodiscard]] uint32 SpecOf(Player const* player) const;
        State& Get(Player* player);
        void Forget(Player* player);
        void BeforeLogout(Player* player);       // takes the worn shape's buttons off before the character is saved

        [[nodiscard]] Shape const* FindShape(uint32 shapeId) const;
        [[nodiscard]] Shape const* ShapeByFormSpell(uint32 spellId) const;
        // A form ability cast outside its shape fails (2026-10-03: abilities stay learned instead of coming and going).
        [[nodiscard]] bool KitSpellBlocked(Player* player, uint32 spellId);
        [[nodiscard]] Source const* SourceFor(uint32 creatureEntry) const;
        [[nodiscard]] uint32 ShapeForFamily(uint32 family) const;   // task 009: 0 = none
        [[nodiscard]] std::vector<Shape const*> AllShapes() const;

        // --- devouring ---------------------------------------------------------------------------------
        static void RememberKill(State& state, ObjectGuid guid);
        bool CanDevour(Player* player, Creature* corpse, std::string& why) const;
        void Devour(Player* player, Creature* corpse);
        bool Unlock(Player* player, uint32 shapeId, uint32 display, bool shiftNow, bool quiet = false);
        void UnlockAll(Player* player);          // GM: every shape and every colouring

        // --- specs -------------------------------------------------------------------------------------
        void OnUpdate(Player* player, uint32 diff);
        void SyncSpecSpells(Player* player);
        bool CanDevourWhole(Player* player, Unit* target, std::string& why) const;
        void DevourWhole(Player* player, Creature* victim);
        void FeedGlutton(Player* player, Creature const* meal);
        void OnBroodHatched(Player* player, bool fromSpell = true);
        void TuneHatchling(Player* player, Creature* hatchling, float healthShare, float minDmg, float maxDmg,
                           bool swarm);                                            // task 015: the Brood talents
        [[nodiscard]] bool IsOwnHatchling(Player* player, Unit* unit) const;
        void Cannibalize(Player* player, Creature* hatchling);
        void OnCreatureDeath(Creature* victim, Unit* killer);
        void SpawnEcho(Player* player, Shape const& shape, bool smallEcho = false, bool force = false);
        void OnSerpentsRisen(Player* player);
        [[nodiscard]] std::list<Creature*> RisenSerpents(Player* player) const;   // ChaosCore0.2
        void OnAutoAttackHit(Player* player);                                     // ChaosCore0.2: Hunger per swing
        void MirrorSpell(Player* player, Spell const* spell);

        // --- task 013: Sniff -----------------------------------------------------------------------------
        // Marks creatures around the Devourer on its client (addon messages, see SniffScan): 'N' = would give a new
        // shape or colouring, 'F' = the worn shape's favourite food, 0 = nothing to mark.
        [[nodiscard]] char SniffKind(Player* player, Creature const* creature);
        void SniffScan(Player* player);
        void SniffClear(Player* player) const;

        // --- ChaosCore0.3: the Glutton's talents and meals --------------------------------------------
        [[nodiscard]] uint32 FavouriteFood(uint32 shapeId) const;   // the creature type a shape's diet rates highest
        // Task 009: devourer_favourite_food when the shape has rows, else FavouriteFood's creature type.
        [[nodiscard]] bool IsFavouriteFood(uint32 shapeId, Creature const* meal) const;
        [[nodiscard]] std::string FavouriteFoodText(uint32 shapeId) const;
        void SyncTalentSpells(Player* player);                        // Quick Devour replaces Devour on the bars
        void DigestGorged(Player* player, State& state);              // Gorged melts away out of combat
        void UpdateStomach(Player* player, State& state, uint32 diff);
        void ReleaseStomach(Player* player, bool expired);            // Regurgitate, pressed or run out
        void Feast(Player* player, Creature* first);                  // Feast: every corpse nearby
        static bool ReplaceButtons(Player* player, uint32 from, uint32 to);

        // --- ChaosCore0.3: the Baby Berserker -------------------------------------------------------------
        void OverrunWindup(Player* player);
        void Overrun(Player* player, uint32 hitSpell = 0, bool chase = true, float extra = 0.0f);   // Rush: its own hit, no chase
        void GnawBite(Unit* caster, Unit* target);
        void VoidFrenzy(Player* player, Unit* target);

        // --- task 009: starter forms batch 1 (src/DevourerForms.cpp has their spell scripts) -------------
        void CallPups(Player* player, Unit* target);                   // Wolf: Pack Prowess
        bool TryCocoon(Player* player, uint32 damage, uint32& absorb);  // Moth: Cocoon Metamorphosis

        // --- task 015: talents, spec abilities, the pet (src/DevourerTalents.cpp, src/DevourerPet.cpp) --------
        [[nodiscard]] uint8 Rank(Player const* player, TalentRef talent) const;      // 0 = not learned
        void UpdatePerks(Player* player, State& state, uint32 diff);                  // every second
        void OnShift(Player* player, Shape const& shape);                             // after a shift (AfterShift)
        void OnShapeLeft(Player* player, Shape const& shape);
        void OnMeal(Player* player, Creature const* meal, bool whole);                // Anima, heals, shared meals
        void OnHitTaken(Player* player, DamageInfo& damage, uint32& absorb);          // Devourer's Hide (an absorb)
        [[nodiscard]] bool CanCastSpec(Player* player, SpellInfo const* spell, Unit* target, std::string& why);
        void CastSpec(Player* player, SpellInfo const* spell, Unit* target);          // spec abilities, active talents
        void OnHatchlingHit(Player* mother, Creature* hatchling, Unit* victim, uint32 damage);
        void OnHatchlingDeath(Player* mother, Creature* hatchling);
        void SyncBrood(Player* player, State& state);                                 // leash, Queen of the Brood
        void SyncPet(Player* player, State& state);                                   // the pet's size hint
        void OnAnimaFromSwing(Player* player);
        [[nodiscard]] uint8 GorgedStacks(Player const* player) const;
        [[nodiscard]] uint8 GorgedCap(Player const* player) const;
        [[nodiscard]] std::list<Creature*> Mine(Player* player, uint32 entry, float range = 60.0f) const;
        void StunFor(Player* player, Unit* target, uint32 ms);
        void CastScaled(Unit* caster, Unit* target, uint32 spellId, float factor, ObjectGuid original = ObjectGuid::Empty);
        void GainAnima(Player* player, uint32 points);
        void EnsureAnimaAura(Player* player);
        void Defer(Player* player, std::function<void()> fn);                         // runs a moment later, safely
        [[nodiscard]] bool IsBeastShape(uint32 shapeId) const;
        void TeachPet(Player* player);                                                // the hunter's pet spells
        void OnPetKill(Player* player, Creature* victim);                             // the pet's kills feed Anima
        void PetShareMeal(Player* player, Creature const* meal, bool big);            // the pet eats with you
        void PetPlay(Player* player);                                                 // the pet and the hatchlings

        // --- growth (Bio Points and evolution) ---------------------------------------------------------
        void LoadGrowthData();
        [[nodiscard]] static uint32 Rarity(Creature const* creature);
        void GainBio(Player* player, Creature const* meal, float factor = 1.0f);   // factor != 1: a bonus share
        void TaskEvent(Player* player, uint8 kind, uint32 value, uint32 amount = 1, std::string const& name = {});
        void CheckEvolution(Player* player);
        void Evolve(Player* player, Evolution const& evo);          // the old body tears open, the new one is put on
        bool OfferMolt(Player* player, Evolution const& evo);       // task 018: true = waiting for its molt quest
        bool Molt(Player* player, uint32 questId);                  // task 018: a molt quest handed in to Wren
        void SaveGrowth(Player* player);
        [[nodiscard]] std::string GrowthText(Player* player, uint32 shapeId);

        // --- shapes ------------------------------------------------------------------------------------
        void OnFormApplied(Player* player, uint32 formSpell);
        void OnFormRemoved(Player* player, uint32 formSpell);
        void KeepShapeShown(Player* player, State& state);   // ChaosCore0.2: puts the body back after a teleport
        void AfterShift(Player* player, uint32 formSpell);
        void ChooseSkin(Player* player, uint32 shapeId, uint32 display);
        void ChooseSkin(Player* player, std::string const& nameOrDisplay);
        [[nodiscard]] std::string SkinName(uint32 display) const;
        void Restore(Player* player);            // after login / resurrection
        void TeachBasics(Player* player);
        [[nodiscard]] uint32 ShownDisplay(Player* player, Shape const& shape);

        // --- chat --------------------------------------------------------------------------------------
        void Tell(Player* player, std::string const& text) const;
        void ListShapes(Player* player);
        void SendMenu(Player* player, bool catalog = false);   // the menu's data as addon messages; catalog: the
                                                                  // gallery too (".devour menu")

        // --- Anima ---------------------------------------------------------------------------------------
        [[nodiscard]] uint32 AnimaPerShift() const { return _animaPerShift; }

    private:
        void Load(Player* player, State& state);
        void SaveShape(Player* player, uint32 shapeId, Owned const& owned);
        void SaveSkin(Player* player, uint32 shapeId, uint32 display);
        void GrantFreeSkins(uint32 shapeId, Owned& owned) const;   // task 017: colourings that come with the shape
        void SaveState(Player* player, State const& state);
        void GrantKit(Player* player, State& state, Shape const& shape);
        [[nodiscard]] static bool KitSpellOpen(Player const* player, uint32 spellId);   // player level >= spell level
        void EatShape(Player* player, Creature* meal, std::string const& how);   // shape/colouring the meal carries
        // The shape and colouring a creature gives (devourer_shape_source first, else its family); null = nothing.
        [[nodiscard]] Shape const* MealShape(Creature const* meal, Source& out) const;
        void SendAddon(Player* player, std::string const& line) const;
        void RevokeKit(Player* player, State& state);
        void LearnKits(Player* player, State const& state);   // every open ability of every owned shape
        void RememberBar(Player* player, State& state, bool clear);   // reads (and clears) the kit's buttons

        std::unordered_map<ObjectGuid::LowType, State> _states;
        std::map<uint32, Shape> _shapes;
        std::unordered_map<uint32, uint32> _shapeByForm;
        std::unordered_map<uint32, std::vector<uint32>> _shapesByKitSpell;   // kit spell -> shapes that use it
        std::unordered_map<uint32, Source> _sources;
        std::map<uint32, Skin> _skins;           // display id -> named colouring
        std::map<uint32, std::map<uint32, uint32>> _diet;   // shape -> creature type (0 = anything else) -> BP
        std::vector<Evolution> _evolutions;
        std::map<uint32, std::vector<std::string>> _hints;   // shape -> how to get it (gallery), from the world data
        void BuildHints();
        std::unordered_map<uint32, uint32> _familyShapes;    // task 009: creature family -> shape
        std::map<uint32, std::vector<FoodRule>> _food;       // task 009: shape -> favourite food rules
        void LoadFamilies();                                 // task 009: families, their colourings, favourite food

        bool _enabled = true;
        uint8 _classId = 10;
        bool _requireLooted = true;
        uint32 _hungerPerMeal = 30;
        uint32 _hungerPerSwing = 3;              // ChaosCore0.2: Hunger per auto-attack hit (0 = off); 3 since task 015
        uint32 _shiftCooldown = 8000;
        uint32 _skinchangerShiftCooldown = 3000;
        uint8 _shapeBarSlot = 60;                // first action button for the kit, 0 = leave the bars alone
        uint32 _animaPerShift = 25;              // Anima a shift into a shape costs (0 = free)
    };
}

#define sDevourer Devourer::Mgr::Instance()

#endif
