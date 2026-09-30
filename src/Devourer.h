/*
 * mod-devourer: the Devourer, a class that becomes what it eats.
 * Released under GNU AGPL v3, like AzerothCore.
 *
 * Class 10 (CLASS_DEVOURER, see core-patch/; the id is Devourer.ClassId). The Devourer devours slain creatures
 * to unlock their shapes, then shifts between them. Every shape brings four abilities and a passive, learned while it is worn.
 * Hunger (the rage bar) is the only resource. All shapes share one shift cooldown.
 *
 * Data:
 *   world      devourer_shape          one row per shape: its form spell, base display, kit, passive
 *              devourer_shape_source   creature entry -> shape (+ the colouring that creature grants)
 *              devourer_skin           display -> shape and colouring name
 *   characters character_devourer_shape    unlocked shapes, chosen colouring
 *              character_devourer_skin     unlocked colourings
 *              character_devourer_worn    the shape worn at logout
 */

#ifndef MOD_DEVOURER_H
#define MOD_DEVOURER_H

#include "Define.h"
#include "ObjectGuid.h"
#include <array>
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

namespace Devourer
{
    constexpr uint8 KitSize = 4;
    constexpr uint32 ItemSethrakIdol = 9100100;   // teaches the first shape until it can be devoured in the world
    constexpr uint32 NpcHatchling = 9101100;      // Brood hatchling (guardian from Hatch Brood)
    constexpr uint32 NpcEcho = 9101101;           // Skinchanger: the echo a left shape leaves behind
    constexpr uint32 DefaultBroodDisplay = 4312;  // a serpent, when a shape names no kin
    constexpr uint32 SpellGhostVisual = 22650;    // "Ghost Visual": echoes are translucent
    constexpr uint32 NpcRisingSerpent = 9101102;  // Vashnik: stationary serpents that repeat its spells
    constexpr uint32 RisingSerpentDisplays[2] = { 991040, 991045 };   // Twinfangs: purple, pale teal
    constexpr uint32 EmoteReadySpellOmni = 917;   // ChaosCore0.3: ONESHOT_READYSPELLOMNI, Overrun's wind-up

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

    struct Skin
    {
        uint32 ShapeId = 0;
        std::string Name;                        // what .devour skin <name> takes
        uint32 BroodDisplay = 0;                 // a Brood's hatchlings while this colouring is worn
    };

    // Growth: a form earns Bio Points (BP) from what it eats while worn, weighted by its diet and the meal's rarity.
    // With enough BP, the level and its tasks done, it evolves into the next form of its line.
    enum TaskKind : uint8
    {
        TaskKill         = 1,                    // kill creatures of a type (value = creature type, 0 = any)
        TaskHitBy        = 2,                    // be hit by a school (value = school mask)
        TaskDevourRarity = 3,                    // devour creatures at least this rare (value = rarity multiplier)
        TaskDevourType   = 4,                    // devour creatures of a type (value = creature type)
    };

    struct EvolutionTask
    {
        uint32 Id = 0;
        uint8 Kind = 0;
        uint32 Value = 0;
        uint32 Count = 0;
        std::string Text;
    };

    struct Evolution
    {
        uint32 From = 0;
        uint32 To = 0;
        uint32 Bp = 0;
        uint8 MinLevel = 0;
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
        std::set<ObjectGuid> Eaten;              // corpses already fed on (they stay for their loot)
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
    };

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

        [[nodiscard]] Shape const* FindShape(uint32 shapeId) const;
        [[nodiscard]] Shape const* ShapeByFormSpell(uint32 spellId) const;
        [[nodiscard]] Source const* SourceFor(uint32 creatureEntry) const;
        [[nodiscard]] std::vector<Shape const*> AllShapes() const;

        // --- devouring ---------------------------------------------------------------------------------
        bool CanDevour(Player* player, Creature* corpse, std::string& why) const;
        void Devour(Player* player, Creature* corpse);
        bool Unlock(Player* player, uint32 shapeId, uint32 display, bool shiftNow);

        // --- specs -------------------------------------------------------------------------------------
        void OnUpdate(Player* player, uint32 diff);
        void SyncSpecSpells(Player* player);
        bool CanDevourWhole(Player* player, Unit* target, std::string& why) const;
        void DevourWhole(Player* player, Creature* victim);
        void FeedGlutton(Player* player, Creature const* meal);
        void OnBroodHatched(Player* player);
        [[nodiscard]] bool IsOwnHatchling(Player* player, Unit* unit) const;
        void Cannibalize(Player* player, Creature* hatchling);
        void OnCreatureDeath(Creature* victim, Unit* killer);
        void SpawnEcho(Player* player, Shape const& shape);
        void OnSerpentsRisen(Player* player);
        [[nodiscard]] std::list<Creature*> RisenSerpents(Player* player) const;   // ChaosCore0.2
        void OnAutoAttackHit(Player* player);                                     // ChaosCore0.2: Hunger per swing
        void MirrorSpell(Player* player, Spell const* spell);

        // --- ChaosCore0.3: the Glutton's talents and meals --------------------------------------------
        [[nodiscard]] uint32 FavouriteFood(uint32 shapeId) const;   // the creature type a shape's diet rates highest
        void SyncTalentSpells(Player* player);                        // Quick Devour replaces Devour on the bars
        void DigestGorged(Player* player, State& state);              // Gorged melts away out of combat
        void UpdateStomach(Player* player, State& state, uint32 diff);
        void ReleaseStomach(Player* player, bool expired);            // Regurgitate, pressed or run out
        void Feast(Player* player, Creature* first);                  // Feast: every corpse nearby
        static bool ReplaceButtons(Player* player, uint32 from, uint32 to);

        // --- ChaosCore0.3: the Baby Berserker -------------------------------------------------------------
        void OverrunWindup(Player* player);
        void Overrun(Player* player);
        void GnawBite(Unit* caster, Unit* target);
        void VoidFrenzy(Player* player, Unit* target);

        // --- growth (Bio Points and evolution) ---------------------------------------------------------
        void LoadGrowthData();
        [[nodiscard]] static uint32 Rarity(Creature const* creature);
        void GainBio(Player* player, Creature const* meal);
        void TaskEvent(Player* player, uint8 kind, uint32 value, uint32 amount = 1);
        void CheckEvolution(Player* player);
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

    private:
        void Load(Player* player, State& state);
        void SaveShape(Player* player, uint32 shapeId, Owned const& owned);
        void SaveSkin(Player* player, uint32 shapeId, uint32 display);
        void SaveState(Player* player, State const& state);
        void GrantKit(Player* player, State& state, Shape const& shape);
        void EatShape(Player* player, Creature* meal, std::string const& how);   // shape/colouring the meal carries
        void RevokeKit(Player* player, State& state);
        void RememberBar(Player* player, State& state, bool clear);   // reads (and clears) the kit's buttons

        std::unordered_map<ObjectGuid::LowType, State> _states;
        std::map<uint32, Shape> _shapes;
        std::unordered_map<uint32, uint32> _shapeByForm;
        std::unordered_map<uint32, Source> _sources;
        std::map<uint32, Skin> _skins;           // display id -> named colouring
        std::map<uint32, std::map<uint32, uint32>> _diet;   // shape -> creature type (0 = anything else) -> BP
        std::vector<Evolution> _evolutions;

        bool _enabled = true;
        uint8 _classId = 10;
        bool _requireLooted = true;
        uint32 _hungerPerMeal = 30;
        uint32 _hungerPerSwing = 2;              // ChaosCore0.2: Hunger per auto-attack hit (0 = off)
        uint32 _shiftCooldown = 8000;
        uint32 _skinchangerShiftCooldown = 3000;
        uint8 _shapeBarSlot = 60;                // first action button for the kit, 0 = leave the bars alone
    };
}

#define sDevourer Devourer::Mgr::Instance()

#endif
