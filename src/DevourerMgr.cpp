/*
 * mod-devourer: shapes, devouring, the shared shift cooldown, Anima (the rage bar, once called Hunger).
 * Released under GNU AGPL v3, like AzerothCore.
 */

#include "Devourer.h"
#include "DevourerSpellIds.h"

#include "Chat.h"
#include "Config.h"
#include "Creature.h"
#include "DBCStores.h"
#include "DatabaseEnv.h"
#include "Log.h"
#include "MapMgr.h"
#include "ObjectMgr.h"
#include "Player.h"
#include "SpellAuras.h"
#include "SpellInfo.h"
#include "SpellMgr.h"
#include "WorldPacket.h"
#include "World.h"
#include "WorldSession.h"
#include <algorithm>
#include <cctype>
#include <cstdlib>
#include <sstream>

namespace Devourer
{
    Mgr& Mgr::Instance()
    {
        static Mgr instance;
        return instance;
    }

    void Mgr::LoadConfig()
    {
        _enabled = sConfigMgr->GetOption<bool>("Devourer.Enable", true);
        _classId = uint8(sConfigMgr->GetOption<uint32>("Devourer.ClassId", 10));
        _requireLooted = sConfigMgr->GetOption<bool>("Devourer.RequireLooted", true);
        _hungerPerMeal = sConfigMgr->GetOption<uint32>("Devourer.HungerPerMeal", 30);
        _hungerPerSwing = sConfigMgr->GetOption<uint32>("Devourer.HungerPerSwing", 2);
        _shiftCooldown = sConfigMgr->GetOption<uint32>("Devourer.ShiftCooldown", 8000);
        _skinchangerShiftCooldown = sConfigMgr->GetOption<uint32>("Devourer.SkinchangerShiftCooldown", 3000);
        _shapeBarSlot = uint8(std::min<uint32>(sConfigMgr->GetOption<uint32>("Devourer.ShapeBarSlot", 60), 140));
        _animaPerShift = std::min<uint32>(sConfigMgr->GetOption<uint32>("Devourer.AnimaPerShift", 0), 100);
    }

    void Mgr::LoadWorldData()
    {
        _shapes.clear();
        _shapeByForm.clear();
        _shapesByKitSpell.clear();
        _sources.clear();
        _skins.clear();

        if (QueryResult result = WorldDatabase.Query(
                "SELECT shape_id, name, form_spell, display_id, scale, spell_1, spell_2, spell_3, spell_4, passive, brood_display "
                "FROM devourer_shape"))
        {
            do
            {
                Field* f = result->Fetch();
                Shape shape;
                shape.Id = f[0].Get<uint32>();
                shape.Name = f[1].Get<std::string>();
                shape.FormSpell = f[2].Get<uint32>();
                shape.Display = f[3].Get<uint32>();
                shape.Scale = f[4].Get<float>();
                for (uint8 i = 0; i < KitSize; ++i)
                    shape.Kit[i] = f[5 + i].Get<uint32>();
                shape.Passive = f[9].Get<uint32>();
                shape.BroodDisplay = f[10].Get<uint32>();
                if (!sSpellMgr->GetSpellInfo(shape.FormSpell))
                {
                    LOG_ERROR("module", "mod-devourer: shape {} has no form spell {}; skipped", shape.Id, shape.FormSpell);
                    continue;
                }
                _shapeByForm[shape.FormSpell] = shape.Id;
                for (uint32 spellId : shape.Kit)
                    if (spellId)
                        _shapesByKitSpell[spellId].push_back(shape.Id);
                _shapes[shape.Id] = std::move(shape);
            } while (result->NextRow());
        }

        if (QueryResult result = WorldDatabase.Query("SELECT creature_entry, shape_id, display_id FROM devourer_shape_source"))
        {
            do
            {
                Field* f = result->Fetch();
                uint32 const shapeId = f[1].Get<uint32>();
                if (shapeId && !_shapes.count(shapeId))   // shape 0 (task 009): not that body, gives nothing
                    continue;
                _sources[f[0].Get<uint32>()] = { shapeId, f[2].Get<uint32>() };
            } while (result->NextRow());
        }

        if (QueryResult result = WorldDatabase.Query("SELECT display_id, shape_id, name, brood_display FROM devourer_skin"))
        {
            do
            {
                Field* f = result->Fetch();
                if (_shapes.count(f[1].Get<uint32>()))
                    _skins[f[0].Get<uint32>()] = { f[1].Get<uint32>(), f[2].Get<std::string>(), f[3].Get<uint32>() };
            } while (result->NextRow());
        }

        LoadFamilies();
        LoadGrowthData();
        BuildHints();
        LOG_INFO("module", "mod-devourer: {} shapes, {} colourings, {} creatures and {} creature families that grant "
            "them, {} evolutions", _shapes.size(), _skins.size(), _sources.size(), _familyShapes.size(),
            _evolutions.size());
    }

    bool Mgr::IsDevourer(Player const* player) const
    {
        return _enabled && player && player->getClass() == _classId;
    }

    // The spec is the talent tree (of the active talent spec) with the most points spent: tab page 0 = Glutton,
    // 1 = Skinchanger, 2 = Brood. No points, or a tie for the most, is no spec.
    uint32 Mgr::SpecOf(Player const* player) const
    {
        if (!IsDevourer(player))
            return SpecNone;

        std::array<uint32, 3> points{};
        for (auto const& [spellId, talent] : player->GetTalentMap())
        {
            if (talent->State == PLAYERSPELL_REMOVED || !talent->IsInSpec(player->GetActiveSpec()))
                continue;
            TalentEntry const* talentInfo = sTalentStore.LookupEntry(talent->talentID);
            if (!talentInfo)
                continue;
            TalentTabEntry const* tab = sTalentTabStore.LookupEntry(talentInfo->TalentTab);
            if (!tab || tab->tabpage >= points.size() || !(tab->ClassMask & player->getClassMask()))
                continue;
            for (uint8 rank = 0; rank < MAX_TALENT_RANK; ++rank)
                if (talentInfo->RankID[rank] == spellId)
                {
                    points[tab->tabpage] += rank + 1;
                    break;
                }
        }

        uint32 best = SpecNone;
        uint32 most = 0;
        bool tie = false;
        for (uint8 page = 0; page < points.size(); ++page)
        {
            if (points[page] > most)
            {
                most = points[page];
                best = SpecGlutton + page;
                tie = false;
            }
            else if (points[page] && points[page] == most)
                tie = true;
        }
        return tie ? uint32(SpecNone) : best;
    }

    Shape const* Mgr::FindShape(uint32 shapeId) const
    {
        auto itr = _shapes.find(shapeId);
        return itr != _shapes.end() ? &itr->second : nullptr;
    }

    Shape const* Mgr::ShapeByFormSpell(uint32 spellId) const
    {
        auto itr = _shapeByForm.find(spellId);
        return itr != _shapeByForm.end() ? FindShape(itr->second) : nullptr;
    }

    Source const* Mgr::SourceFor(uint32 creatureEntry) const
    {
        auto itr = _sources.find(creatureEntry);
        return itr != _sources.end() ? &itr->second : nullptr;
    }

    uint32 Mgr::ShapeForFamily(uint32 family) const
    {
        auto itr = family ? _familyShapes.find(family) : _familyShapes.end();
        return itr != _familyShapes.end() ? itr->second : 0;
    }

    // Task 009: a starting form is a kind of creature. Any creature of its family gives it, and each look of that
    // family is a colouring, named after the creature that wears it most often in the world. Explicit
    // devourer_shape_source rows win (another shape, or shape 0: not that body), and so do named devourer_skin rows.
    void Mgr::LoadFamilies()
    {
        _familyShapes.clear();
        _food.clear();

        if (QueryResult result = WorldDatabase.Query("SELECT family, shape_id FROM devourer_shape_family"))
        {
            do
            {
                Field* f = result->Fetch();
                uint32 const family = f[0].Get<uint32>();
                uint32 const shapeId = f[1].Get<uint32>();
                if (family && _shapes.count(shapeId))
                    _familyShapes[family] = shapeId;
            } while (result->NextRow());
        }

        if (QueryResult result = WorldDatabase.Query(
                "SELECT shape_id, creature_type, family, name_part, label FROM devourer_favourite_food"))
        {
            do
            {
                Field* f = result->Fetch();
                FoodRule rule;
                rule.Type = f[1].Get<uint32>();
                rule.Family = f[2].Get<uint32>();
                rule.NamePart = f[3].Get<std::string>();
                std::transform(rule.NamePart.begin(), rule.NamePart.end(), rule.NamePart.begin(),
                    [](unsigned char ch) { return std::tolower(ch); });
                rule.Label = f[4].Get<std::string>();
                _food[f[0].Get<uint32>()].push_back(std::move(rule));
            } while (result->NextRow());
        }

        if (_familyShapes.empty())
            return;

        auto lower = [](std::string text)
        {
            std::transform(text.begin(), text.end(), text.begin(), [](unsigned char ch) { return std::tolower(ch); });
            return text;
        };
        std::set<std::string> taken;
        for (auto const& [display, skin] : _skins)
            taken.insert(lower(skin.Name));

        // Most spawned first: a look shared by several creatures is named after the one met most often.
        if (QueryResult result = WorldDatabase.Query(
                "SELECT sf.shape_id, ctm.CreatureDisplayID, ct.name, COUNT(c.guid) AS spawns "
                "FROM devourer_shape_family sf JOIN creature_template ct ON ct.family = sf.family "
                "JOIN creature_template_model ctm ON ctm.CreatureID = ct.entry "
                "JOIN creature c ON c.id = ct.entry "
                "LEFT JOIN devourer_shape_source ss ON ss.creature_entry = ct.entry "
                "WHERE ss.creature_entry IS NULL OR ss.shape_id = sf.shape_id "
                "GROUP BY sf.shape_id, ctm.CreatureDisplayID, ct.entry, ct.name "
                "ORDER BY spawns DESC, ct.entry"))
        {
            do
            {
                Field* f = result->Fetch();
                uint32 const shapeId = f[0].Get<uint32>();
                uint32 const display = f[1].Get<uint32>();
                Shape const* shape = FindShape(shapeId);
                if (!shape || !display || display == shape->Display || _skins.count(display) ||
                    !sCreatureDisplayInfoStore.LookupEntry(display))
                    continue;
                // The menu splits its lines on ':' and lists colourings with ','.
                std::string name;
                for (char ch : f[2].Get<std::string>())
                    if (ch != ':' && ch != ',')
                        name += ch;
                std::string unique = name;
                for (uint32 n = 2; taken.count(lower(unique)); ++n)
                    unique = name + " " + std::to_string(n);
                taken.insert(lower(unique));
                _skins[display] = { shapeId, unique, display };
            } while (result->NextRow());
        }
    }

    std::vector<Shape const*> Mgr::AllShapes() const
    {
        std::vector<Shape const*> out;
        for (auto const& [id, shape] : _shapes)
            out.push_back(&shape);
        return out;
    }

    // --- per-character state ------------------------------------------------------------------------------

    State& Mgr::Get(Player* player)
    {
        State& state = _states[player->GetGUID().GetCounter()];
        if (!state.Loaded)
        {
            Load(player, state);
            state.Loaded = true;
        }
        return state;
    }

    void Mgr::BeforeLogout(Player* player)
    {
        auto itr = _states.find(player->GetGUID().GetCounter());
        if (itr == _states.end() || !itr->second.KitShape)
            return;
        RememberBar(player, itr->second, true);          // remembers where they are, then takes them off
        itr->second.KitShape = 0;                        // Forget must not remember the now empty slots
    }

    void Mgr::Forget(Player* player)
    {
        auto itr = _states.find(player->GetGUID().GetCounter());
        if (itr != _states.end() && itr->second.KitShape)
            RememberBar(player, itr->second, false);   // keeps where the worn shape's abilities are at logout
        if (itr != _states.end() && itr->second.StomachFull)
            ReplaceButtons(player, SpellRegurgitate, SpellDevourWhole);   // ChaosCore0.3: the button is saved as Devour Whole
        if (itr != _states.end() && itr->second.GrowthDirty)
            SaveGrowth(player);
        _states.erase(player->GetGUID().GetCounter());
    }

    void Mgr::Load(Player* player, State& state)
    {
        uint32 const guid = player->GetGUID().GetCounter();
        if (QueryResult result = CharacterDatabase.Query(
                "SELECT shape_id, eaten, display_id FROM character_devourer_shape WHERE guid = {}", guid))
        {
            do
            {
                Field* f = result->Fetch();
                Owned& owned = state.Shapes[f[0].Get<uint32>()];
                owned.Eaten = f[1].Get<uint32>();
                owned.Display = f[2].Get<uint32>();
            } while (result->NextRow());
        }
        if (QueryResult result = CharacterDatabase.Query(
                "SELECT shape_id, display_id FROM character_devourer_skin WHERE guid = {}", guid))
        {
            do
            {
                Field* f = result->Fetch();
                auto itr = state.Shapes.find(f[0].Get<uint32>());
                if (itr != state.Shapes.end())
                    itr->second.Skins.insert(f[1].Get<uint32>());
            } while (result->NextRow());
        }
        if (QueryResult result = CharacterDatabase.Query(
                "SELECT shape_id FROM character_devourer_worn WHERE guid = {}", guid))
            state.Worn = result->Fetch()[0].Get<uint32>();
        if (QueryResult result = CharacterDatabase.Query(
                "SELECT shape_id, bp FROM character_devourer_growth WHERE guid = {}", guid))
        {
            do
            {
                Field* f = result->Fetch();
                state.Bio[f[0].Get<uint32>()] = f[1].Get<uint32>();
            } while (result->NextRow());
        }
        if (QueryResult result = CharacterDatabase.Query(
                "SELECT to_shape, task_id, progress FROM character_devourer_task WHERE guid = {}", guid))
        {
            do
            {
                Field* f = result->Fetch();
                state.Tasks[{ f[0].Get<uint32>(), f[1].Get<uint32>() }] = f[2].Get<uint32>();
            } while (result->NextRow());
        }
        if (QueryResult result = CharacterDatabase.Query(
                "SELECT shape_id, spell, slot FROM character_devourer_bar WHERE guid = {}", guid))
        {
            do
            {
                Field* f = result->Fetch();
                state.Bar[f[0].Get<uint32>()][f[1].Get<uint32>()] = f[2].Get<uint8>();
            } while (result->NextRow());
        }
    }

    void Mgr::SaveShape(Player* player, uint32 shapeId, Owned const& owned)
    {
        CharacterDatabase.Execute(
            "REPLACE INTO character_devourer_shape (guid, shape_id, eaten, display_id) VALUES ({}, {}, {}, {})",
            player->GetGUID().GetCounter(), shapeId, owned.Eaten, owned.Display);
    }

    void Mgr::SaveSkin(Player* player, uint32 shapeId, uint32 display)
    {
        CharacterDatabase.Execute(
            "REPLACE INTO character_devourer_skin (guid, shape_id, display_id) VALUES ({}, {}, {})",
            player->GetGUID().GetCounter(), shapeId, display);
    }

    void Mgr::SaveState(Player* player, State const& state)
    {
        CharacterDatabase.Execute("REPLACE INTO character_devourer_worn (guid, shape_id) VALUES ({}, {})",
            player->GetGUID().GetCounter(), state.Worn);
    }

    // --- devouring ----------------------------------------------------------------------------------------

    bool Mgr::CanDevour(Player* player, Creature* corpse, std::string& why) const
    {
        if (!corpse || corpse->IsAlive())
        {
            why = "Only the dead can be devoured.";
            return false;
        }
        auto itr = _states.find(player->GetGUID().GetCounter());
        if (itr != _states.end() && itr->second.Eaten.count(corpse->GetGUID()))
        {
            why = "Nothing is left of it to eat.";
            return false;
        }
        if (_requireLooted && !corpse->isTappedBy(player) && !corpse->hasLootRecipient())
        {
            why = "You must have slain it yourself.";
            return false;
        }
        return true;
    }

    void Mgr::Devour(Player* player, Creature* corpse)
    {
        std::string const name = corpse->GetName();
        State& state = Get(player);
        state.Eaten.insert(corpse->GetGUID());
        // A corpse with loot left stays for it; an emptied one is gone.
        if (corpse->loot.isLooted())
            corpse->DespawnOrUnsummon(1500ms);
        player->HandleEmoteCommand(EMOTE_ONESHOT_EAT_NO_SHEATHE);
        player->ModifyPower(POWER_RAGE, int32(_hungerPerMeal * 10));
        FeedGlutton(player, corpse);
        EatShape(player, corpse, "You devour " + name + ".");
        if (player->HasSpell(SpellTalentFeast))          // ChaosCore0.3: Feast eats every corpse around it too
            Feast(player, corpse);
    }

    void Mgr::EatShape(Player* player, Creature* meal, std::string const& how)
    {
        GainBio(player, meal);
        Source const* source = SourceFor(meal->GetEntry());
        // Task 009: no row of its own, so its kind decides: any creature of a form's family gives the form, and
        // its look is the colouring.
        Source byFamily;
        if (!source)
            if (uint32 const shapeId = ShapeForFamily(meal->GetCreatureTemplate()->family))
            {
                auto skin = _skins.find(meal->GetNativeDisplayId());
                byFamily.ShapeId = shapeId;
                byFamily.Display = skin != _skins.end() && skin->second.ShapeId == shapeId ? skin->first : 0;
                source = &byFamily;
            }
        Shape const* shape = source ? FindShape(source->ShapeId) : nullptr;
        if (!shape)
        {
            Tell(player, how);
            return;
        }

        State& state = Get(player);
        bool const newShape = !state.Shapes.count(shape->Id);
        Unlock(player, shape->Id, source->Display, newShape);
        Owned& owned = state.Shapes[shape->Id];
        ++owned.Eaten;
        SaveShape(player, shape->Id, owned);
        Tell(player, newShape ? how + " Its shape is yours: " + shape->Name + "." : how);
    }

    bool Mgr::Unlock(Player* player, uint32 shapeId, uint32 display, bool shiftNow, bool quiet)
    {
        Shape const* shape = FindShape(shapeId);
        if (!shape || !IsDevourer(player))
            return false;

        State& state = Get(player);
        bool const isNew = !state.Shapes.count(shapeId);
        Owned& owned = state.Shapes[shapeId];
        if (isNew)
            SaveShape(player, shapeId, owned);
        if (display && display != shape->Display && owned.Skins.insert(display).second)
        {
            SaveSkin(player, shapeId, display);
            if (!isNew && !quiet)
                Tell(player, "A new colouring for your " + shape->Name + " shape: " + SkinName(display) +
                    ". Wear it with /devour skin " + SkinName(display) + ".");
        }

        if (!player->HasSpell(shape->FormSpell))
            player->learnSpell(shape->FormSpell);
        if (!quiet)
            SendMenu(player);

        // The first time, the body forces itself on its eater.
        if (shiftNow)
        {
            player->RemoveSpellCooldown(shape->FormSpell, true);
            player->CastSpell(player, shape->FormSpell, true);
        }
        return true;
    }

    // --- shapes -------------------------------------------------------------------------------------------

    uint32 Mgr::ShownDisplay(Player* player, Shape const& shape)
    {
        State& state = Get(player);
        auto itr = state.Shapes.find(shape.Id);
        if (itr != state.Shapes.end() && itr->second.Display && itr->second.Skins.count(itr->second.Display))
            return itr->second.Display;
        return shape.Display;
    }

    void Mgr::OnFormApplied(Player* player, uint32 formSpell)
    {
        Shape const* shape = ShapeByFormSpell(formSpell);
        if (!shape)
            return;

        // One shape at a time: wearing a new one sheds the old.
        for (auto const& [id, other] : _shapes)
            if (other.FormSpell != formSpell)
                player->RemoveAurasDueToSpell(other.FormSpell);

        State& state = Get(player);
        player->SetDisplayId(ShownDisplay(player, *shape));
        player->RecalculateObjectScale();                // keeps Gorged's growth
        if (shape->Scale != 1.0f)
            player->SetObjectScale(player->GetObjectScale() * shape->Scale);
        state.Worn = shape->Id;
        SaveState(player, state);
        GrantKit(player, state, *shape);
        SendMenu(player);
    }

    // ChaosCore0.2: a teleport or map change can reset the display to the form spell's placeholder creature (a
    // wolf). Checked on every player update; it only writes when the shown body is wrong, and it leaves any other
    // transform (a polymorph, a costume) alone, because then the form spell is not the active transform.
    void Mgr::KeepShapeShown(Player* player, State& state)
    {
        if (!state.Worn || !player->IsAlive() || !player->IsInWorld())
            return;
        Shape const* shape = FindShape(state.Worn);
        if (!shape || player->getTransForm() != shape->FormSpell)
            return;
        uint32 const want = ShownDisplay(player, *shape);
        if (!want || player->GetDisplayId() == want)
            return;
        player->SetDisplayId(want);
        player->RecalculateObjectScale();                // same as OnFormApplied: keeps Gorged's growth
        if (shape->Scale != 1.0f)
            player->SetObjectScale(player->GetObjectScale() * shape->Scale);
    }

    // ChaosCore0.2: auto-attacks slowly fill Hunger.
    void Mgr::OnAutoAttackHit(Player* player)
    {
        if (_hungerPerSwing && IsDevourer(player))
            player->ModifyPower(POWER_RAGE, int32(_hungerPerSwing * 10));
    }

    void Mgr::OnFormRemoved(Player* player, uint32 formSpell)
    {
        auto itr = _states.find(player->GetGUID().GetCounter());
        if (itr == _states.end())
            return;                               // logging out: nothing left to clean up
        State& state = itr->second;
        Shape const* shape = ShapeByFormSpell(formSpell);
        if (!shape || state.Worn != shape->Id)
            return;                               // an older form, already replaced

        RevokeKit(player, state);
        player->RestoreDisplayId();
        player->RecalculateObjectScale();
        if (player->IsAlive() && SpecOf(player) == SpecSkinchanger)
            SpawnEcho(player, *shape);
        // Death keeps the wish (the shape comes back on resurrection); anything else returns to the Devourer.
        if (player->IsAlive())
        {
            state.Worn = 0;
            SaveState(player, state);
            SendMenu(player);
        }
    }

    void Mgr::AfterShift(Player* player, uint32 formSpell)
    {
        // One cooldown for every shape: the spell's category cools all of them down, a Skinchanger's recovers
        // faster.
        if (SpecOf(player) != SpecSkinchanger || _skinchangerShiftCooldown >= _shiftCooldown)
            return;
        int32 const faster = -int32(_shiftCooldown - _skinchangerShiftCooldown);
        for (auto const& [id, shape] : _shapes)
            if (player->HasSpell(shape.FormSpell))
                player->ModifySpellCooldown(shape.FormSpell, faster);
        (void)formSpell;
    }

    // 2026-10-03: form abilities are learned once (when the shape is owned and the level allows) and stay in the
    // spellbook and on the bars; KitSpellBlocked keeps them to their own shape. Before, they were learned on every
    // shift and unlearned on the way out, which spammed "You have learned", refilled the spellbook and cost the
    // bar buttons. Only the shape's passive still comes and goes, as an aura.
    void Mgr::LearnKits(Player* player, State const& state)
    {
        for (auto const& [id, owned] : state.Shapes)
            if (Shape const* shape = FindShape(id))
                for (uint32 spellId : shape->Kit)
                    if (spellId && !player->HasSpell(spellId) && KitSpellOpen(player, spellId))
                        player->learnSpell(spellId);
    }

    bool Mgr::KitSpellBlocked(Player* player, uint32 spellId)
    {
        auto itr = _shapesByKitSpell.find(spellId);
        if (itr == _shapesByKitSpell.end() || !IsDevourer(player))
            return false;
        State& state = Get(player);
        for (uint32 shapeId : itr->second)
            if (state.KitShape == shapeId)
                return false;
        return true;
    }

    void Mgr::GrantKit(Player* player, State& state, Shape const& shape)
    {
        RevokeKit(player, state);
        LearnKits(player, state);
        for (uint32 spellId : shape.Kit)                 // also a shape worn but not owned (Wren's Biletoad)
            if (spellId && !player->HasSpell(spellId) && KitSpellOpen(player, spellId))
                player->learnSpell(spellId);
        for (uint32 aura : { shape.Passive, SpellShapeStride })
            if (aura && sSpellMgr->GetSpellInfo(aura) && !player->HasAura(aura))
                player->AddAura(aura, player);
        state.KitShape = shape.Id;

        // Hotbar (Copus55, 2026-09-28): each ability goes back where the player last kept it in this shape;
        // the first time to the default slot (Devourer.ShapeBarSlot + i). A slot the player filled with
        // something else is never overwritten, and an ability the player took off the bars stays off.
        if (_shapeBarSlot)
        {
            auto saved = state.Bar.find(shape.Id);
            for (uint8 i = 0; i < KitSize; ++i)
            {
                uint32 const spellId = shape.Kit[i];
                if (!spellId || !player->HasSpell(spellId))
                    continue;
                uint32 slot = MAX_ACTION_BUTTONS;
                bool remembered = false;
                if (saved != state.Bar.end())
                {
                    auto own = saved->second.find(spellId);
                    if (own != saved->second.end())
                    {
                        slot = own->second;
                        remembered = true;
                    }
                }
                // Never placed before: the first free slot of the main bar (the bar every UI shows), else the
                // bar at Devourer.ShapeBarSlot.
                if (!remembered)
                {
                    for (uint8 s = 0; s < 12 && slot == MAX_ACTION_BUTTONS; ++s)
                        if (!player->GetActionButton(s))
                            slot = s;
                    if (slot == MAX_ACTION_BUTTONS)
                        slot = uint32(_shapeBarSlot) + i;
                }
                if (slot >= MAX_ACTION_BUTTONS)
                    continue;                                    // NotOnBar, or out of range
                ActionButton const* there = player->GetActionButton(uint8(slot));
                if (there && !(there->GetType() == ACTION_BUTTON_SPELL && there->GetAction() == spellId))
                    continue;                                    // the player put something else there
                player->addActionButton(uint8(slot), spellId, ACTION_BUTTON_SPELL);
            }
            player->SendActionButtons(1);
            RememberBar(player, state, false);           // a first placement is remembered right away
        }
    }

    void Mgr::RememberBar(Player* player, State& state, bool clear)
    {
        Shape const* shape = FindShape(state.KitShape);
        if (!_shapeBarSlot || !shape)
            return;
        std::map<uint32, uint8>& bar = state.Bar[shape->Id];
        uint32 const guid = player->GetGUID().GetCounter();
        for (uint32 spellId : shape->Kit)
        {
            // A spell not learned yet (it opens at a later level) cannot have been taken off the bars.
            if (!spellId || !player->HasSpell(spellId))
                continue;
            uint8 found = NotOnBar;
            for (uint8 slot = 0; slot < MAX_ACTION_BUTTONS; ++slot)
            {
                ActionButton const* button = player->GetActionButton(slot);
                if (!button || button->GetType() != ACTION_BUTTON_SPELL || button->GetAction() != spellId)
                    continue;
                if (found == NotOnBar)
                    found = slot;
                if (clear)
                    player->removeActionButton(slot);    // off the bars while the shape is not worn
            }
            auto itr = bar.find(spellId);
            if (itr != bar.end() && itr->second == found)
                continue;
            bar[spellId] = found;
            CharacterDatabase.Execute(
                "REPLACE INTO character_devourer_bar (guid, shape_id, spell, slot) VALUES ({}, {}, {}, {})",
                guid, shape->Id, spellId, found);
        }
    }

    void Mgr::RevokeKit(Player* player, State& state)
    {
        if (Shape const* shape = FindShape(state.KitShape))
        {
            // Owner, 2026-10-03: a shape's buttons leave the bars with it and come back when it is worn again.
            RememberBar(player, state, true);
            if (_shapeBarSlot)
                player->SendActionButtons(1);
            if (shape->Passive)
                player->RemoveAurasDueToSpell(shape->Passive);
            player->RemoveAurasDueToSpell(SpellShapeStride);
        }
        state.KitShape = 0;
        // Characters from before 2026-10-03 may still carry temporary kit spells: they are permanent now.
        state.Granted.clear();
    }

    void Mgr::ChooseSkin(Player* player, uint32 shapeId, uint32 display)
    {
        State& state = Get(player);
        auto itr = state.Shapes.find(shapeId);
        Shape const* shape = FindShape(shapeId);
        if (!shape || itr == state.Shapes.end())
        {
            Tell(player, "You have not devoured that shape.");
            return;
        }
        if (display && display != shape->Display && !itr->second.Skins.count(display))
        {
            Tell(player, "You have not devoured that colouring.");
            return;
        }
        itr->second.Display = display == shape->Display ? 0 : display;
        SaveShape(player, shapeId, itr->second);
        if (state.Worn == shapeId)
            player->SetDisplayId(ShownDisplay(player, *shape));
        Tell(player, "Your " + shape->Name + " shape now wears " + SkinName(ShownDisplay(player, *shape)) + ".");
        SendMenu(player);
    }

    std::string Mgr::SkinName(uint32 display) const
    {
        auto itr = _skins.find(display);
        return itr != _skins.end() ? itr->second.Name : std::to_string(display);
    }

    // ".devour skin <name>": the name (or display id) says which shape's colouring it is.
    void Mgr::ChooseSkin(Player* player, std::string const& nameOrDisplay)
    {
        std::string wanted = nameOrDisplay;
        std::transform(wanted.begin(), wanted.end(), wanted.begin(), [](unsigned char ch) { return std::tolower(ch); });
        uint32 display = 0;
        if (!wanted.empty() && std::all_of(wanted.begin(), wanted.end(), [](unsigned char ch) { return std::isdigit(ch); }))
            display = uint32(std::strtoul(wanted.c_str(), nullptr, 10));
        else
            for (auto const& [id, skin] : _skins)
            {
                std::string name = skin.Name;
                std::transform(name.begin(), name.end(), name.begin(), [](unsigned char ch) { return std::tolower(ch); });
                if (name == wanted)
                {
                    display = id;
                    break;
                }
            }

        auto itr = _skins.find(display);
        if (!display || itr == _skins.end())
        {
            Tell(player, "No colouring by that name. .devour lists yours.");
            return;
        }
        ChooseSkin(player, itr->second.ShapeId, display);
    }

    void Mgr::Restore(Player* player)
    {
        if (!IsDevourer(player) || !player->IsAlive())
            return;
        State& state = Get(player);
        Shape const* shape = FindShape(state.Worn);
        if (shape && player->HasSpell(shape->FormSpell) && !player->HasAura(shape->FormSpell))
            player->CastSpell(player, shape->FormSpell, true);
    }

    // Task 007: a kit ability opens at its spell's level (the starting forms' last two abilities come at 10 and 20).
    bool Mgr::KitSpellOpen(Player const* player, uint32 spellId)
    {
        SpellInfo const* info = sSpellMgr->GetSpellInfo(spellId);
        return info && player->GetLevel() >= info->SpellLevel;
    }

    void Mgr::TeachBasics(Player* player)
    {
        if (!IsDevourer(player))
            return;
        SyncSpecSpells(player);
        if (!player->HasSpell(SpellDevour) && !player->HasSpell(SpellDevourQuick) && sSpellMgr->GetSpellInfo(SpellDevour))
            player->learnSpell(SpellDevour);
        SyncTalentSpells(player);                        // ChaosCore0.3: Quick Devour takes Devour's place
        // The base kit (2026-09-30): Rush, Concentrate and the Anima passive, for new and older characters alike.
        for (uint32 spellId : { SpellRush, SpellConcentrate, SpellAnima })
            if (!player->HasSpell(spellId) && sSpellMgr->GetSpellInfo(spellId))
                player->learnSpell(spellId);
        // Tasks 008, 011: the class skills that give the Devourer its three spellbook tabs. New characters get
        // them from playercreateinfo_skills, older ones here (nothing happens while a SkillRaceClassInfo row is
        // missing).
        for (uint32 skillId : SkillTabs)
            if (!player->HasSkill(skillId))
                player->LearnDefaultSkill(skillId, 0);
        // Form spells follow the shapes owned (a shape added by a GM or a data fix is taught here too). A new
        // Devourer starts without a shape: it devours the first one from its starting zone's beasts (task 007),
        // so the Idol of the Sethrak is no longer handed out.
        State& state = Get(player);
        for (auto const& [id, owned] : state.Shapes)
            if (Shape const* shape = FindShape(id))
                if (!player->HasSpell(shape->FormSpell))
                    player->learnSpell(shape->FormSpell);
        // A level gained can open abilities; the worn shape's new ones also go on the bars.
        if (Shape const* worn = FindShape(state.KitShape))
        {
            bool opened = false;
            for (uint32 spellId : worn->Kit)
                opened |= spellId && !player->HasSpell(spellId) && KitSpellOpen(player, spellId);
            if (opened)
                GrantKit(player, state, *worn);
        }
        LearnKits(player, state);
    }

    // --- chat ---------------------------------------------------------------------------------------------

    void Mgr::Tell(Player* player, std::string const& text) const
    {
        if (player && player->GetSession())
            ChatHandler(player->GetSession()).SendSysMessage(text);
    }

    void Mgr::ListShapes(Player* player)
    {
        State& state = Get(player);
        if (state.Shapes.empty())
        {
            Tell(player, "You have devoured no shape yet.");
            return;
        }
        for (auto const& [id, owned] : state.Shapes)
        {
            Shape const* shape = FindShape(id);
            if (!shape)
                continue;
            std::ostringstream line;
            line << shape->Name << " (shape " << id << ", eaten " << owned.Eaten << ")"
                 << (state.Worn == id ? " - worn" : "") << ". Colourings: " << SkinName(shape->Display);
            for (uint32 skin : owned.Skins)
                line << ", " << SkinName(skin);
            line << " (wearing: " << SkinName(ShownDisplay(player, *shape)) << ")";
            Tell(player, line.str());
            std::string const growth = GrowthText(player, id);
            if (!growth.empty())
                Tell(player, growth);
        }
    }

    // GM: every shape and every colouring, without the one-by-one messages.
    void Mgr::UnlockAll(Player* player)
    {
        if (!IsDevourer(player))
            return;
        for (auto const& [id, shape] : _shapes)
            Unlock(player, id, 0, false, true);
        for (auto const& [display, skin] : _skins)
            Unlock(player, skin.ShapeId, display, false, true);
        Tell(player, "Every shape and colouring is yours.");
        SendMenu(player, true);
    }

    // The gallery's "how to get it", built from the world data at startup: which creatures give the shape (and
    // which colouring), the zone of their first spawn, and the evolution that grows it with its tasks.
    void Mgr::BuildHints()
    {
        _hints.clear();
        auto zoneName = [](Field* f) -> std::string
        {
            if (f[0].IsNull())
                return "not placed in the world";
            uint32 const zone = sMapMgr->GetZoneId(PHASEMASK_NORMAL, f[0].Get<uint32>(), f[1].Get<float>(),
                f[2].Get<float>(), f[3].Get<float>());
            if (AreaTableEntry const* area = sAreaTableStore.LookupEntry(zone))
                return area->area_name[sWorld->GetDefaultDbcLocale()];
            return "unknown place";
        };

        // Task 009: a form that is a kind of creature: "Devour any wolf, e.g. ...", the youngest kinds from three
        // different places.
        std::set<uint32> kinds;
        for (auto const& [family, shapeId] : _familyShapes)
            kinds.insert(shapeId);
        if (!kinds.empty())
            if (QueryResult result = WorldDatabase.Query(
                    "SELECT sf.shape_id, ct.name, c.map, c.position_x, c.position_y, c.position_z "
                    "FROM devourer_shape_family sf JOIN creature_template ct ON ct.family = sf.family "
                    "JOIN creature c ON c.guid = (SELECT MIN(c2.guid) FROM creature c2 WHERE c2.id = ct.entry) "
                    "LEFT JOIN devourer_shape_source ss ON ss.creature_entry = ct.entry "
                    "WHERE ss.creature_entry IS NULL OR ss.shape_id = sf.shape_id "
                    "ORDER BY sf.shape_id, ct.minlevel, ct.entry"))
            {
                std::map<uint32, std::vector<std::pair<std::string, std::string>>> examples;   // shape -> (name, zone)
                do
                {
                    Field* f = result->Fetch();
                    uint32 const shapeId = f[0].Get<uint32>();
                    auto& list = examples[shapeId];
                    if (list.size() >= 3 || !FindShape(shapeId))
                        continue;
                    std::string const where = zoneName(f + 2);
                    if (std::none_of(list.begin(), list.end(), [&where](auto const& e) { return e.second == where; }))
                        list.emplace_back(f[1].Get<std::string>(), where);
                } while (result->NextRow());
                for (auto const& [shapeId, list] : examples)
                {
                    Shape const* shape = FindShape(shapeId);
                    if (!shape || list.empty())
                        continue;
                    std::string kind = shape->Name;
                    std::transform(kind.begin(), kind.end(), kind.begin(), [](unsigned char ch) { return std::tolower(ch); });
                    std::string line = "Devour any " + kind;
                    for (size_t i = 0; i < list.size(); ++i)
                        line += (i ? ", " : ", e.g. ") + list[i].first + " (" + list[i].second + ")";
                    _hints[shapeId].push_back(line);
                }
            }

        if (QueryResult result = WorldDatabase.Query(
                "SELECT s.shape_id, s.display_id, ct.name, c.map, c.position_x, c.position_y, c.position_z "
                "FROM devourer_shape_source s JOIN creature_template ct ON ct.entry = s.creature_entry "
                "LEFT JOIN creature c ON c.guid = (SELECT MIN(c2.guid) FROM creature c2 WHERE c2.id = s.creature_entry) "
                "ORDER BY s.shape_id, s.display_id, s.creature_entry"))
        {
            do
            {
                Field* f = result->Fetch();
                uint32 const shapeId = f[0].Get<uint32>();
                uint32 const display = f[1].Get<uint32>();
                Shape const* shape = FindShape(shapeId);
                if (!shape)
                    continue;
                if (kinds.count(shapeId) && (!display || display == shape->Display))
                    continue;                            // "Devour any ..." already says it
                std::string line = "Devour " + f[2].Get<std::string>() + " - " + zoneName(f + 3);
                if (display && display != shape->Display)
                    line = "Colouring " + SkinName(display) + ": " + line;
                _hints[shapeId].push_back(line);
            } while (result->NextRow());
        }
        for (Evolution const& evo : _evolutions)
        {
            Shape const* from = FindShape(evo.From);
            std::vector<std::string>& lines = _hints[evo.To];
            lines.push_back("Grows out of the " + (from ? from->Name : std::string("?")) + " shape: " +
                std::to_string(evo.Bp) + " Bio Points, level " + std::to_string(evo.MinLevel));
            for (EvolutionTask const& task : evo.Tasks)
                lines.push_back((evo.AnyTask && evo.Tasks.size() > 1 ? "Any one task: " : "Task: ") + task.Text);
        }
    }

    static char const* CreatureTypeName(uint32 type)
    {
        switch (type)
        {
            case CREATURE_TYPE_BEAST:         return "Beast";
            case CREATURE_TYPE_DRAGONKIN:     return "Dragonkin";
            case CREATURE_TYPE_DEMON:         return "Demon";
            case CREATURE_TYPE_ELEMENTAL:     return "Elemental";
            case CREATURE_TYPE_GIANT:         return "Giant";
            case CREATURE_TYPE_UNDEAD:        return "Undead";
            case CREATURE_TYPE_HUMANOID:      return "Humanoid";
            case CREATURE_TYPE_CRITTER:       return "Critter";
            case CREATURE_TYPE_MECHANICAL:    return "Mechanical";
            case CREATURE_TYPE_NOT_SPECIFIED: return "Not specified";
            case CREATURE_TYPE_TOTEM:         return "Totem";
            case CREATURE_TYPE_NON_COMBAT_PET: return "Non-combat pet";
            case CREATURE_TYPE_GAS_CLOUD:     return "Gas cloud";
            default:                          return "";
        }
    }

    // Task 009: what the menu shows as a shape's favourite food ("Boar, Crocolisk"; "Beast, Plants").
    std::string Mgr::FavouriteFoodText(uint32 shapeId) const
    {
        auto itr = _food.find(shapeId);
        if (itr == _food.end() || itr->second.empty())
            return CreatureTypeName(FavouriteFood(shapeId));
        std::vector<std::string> parts;
        for (FoodRule const& rule : itr->second)
        {
            std::string text = rule.Label;
            if (text.empty() && rule.Family)
                if (CreatureFamilyEntry const* family = sCreatureFamilyStore.LookupEntry(rule.Family))
                    text = family->Name[sWorld->GetDefaultDbcLocale()];
            if (text.empty() && rule.Type)
                text = CreatureTypeName(rule.Type);
            if (!text.empty() && std::find(parts.begin(), parts.end(), text) == parts.end())
                parts.push_back(text);
        }
        std::string out;
        for (std::string const& part : parts)
            out += (out.empty() ? "" : ", ") + part;
        return out;
    }

    // The shape menu (tools/client/lua/DevourerMenu.lua) is fed by addon messages, one per line, prefix "DVR".
    // With catalog (".devour menu", and after a GM unlock), the gallery comes first:
    //   C                                                  a new catalog begins
    //   A:<1 = may unlock all (GM)>
    //   G:<shape>:<form spell>:<favourite food>:<ability>,<ability>,...:<passive>   every shape there is
    //   H:<shape>:<text>                                   how to get it, one line each
    // Then, always (also whenever a shape is gained, worn, left or recoloured):
    //   B                                                  the owned list begins
    //   S:<shape>:<form spell>:<worn 0/1>:<colouring worn>:<base colouring>   one owned shape
    //   K:<shape>:<colouring>,<colouring>,...              its other colourings, as many lines as needed
    //   E:<Anima per shift>                                done
    void Mgr::SendMenu(Player* player, bool catalog)
    {
        if (!IsDevourer(player) || !player->GetSession() || !player->IsInWorld())
            return;
        auto send = [player](std::string const& line)
        {
            WorldPacket data;
            ChatHandler::BuildChatPacket(data, CHAT_MSG_WHISPER, LANG_ADDON, player, player,
                std::string(MenuPrefix) + "\t" + line.substr(0, 250));   // 255 bytes with the prefix
            player->SendDirectMessage(&data);
        };
        if (catalog)
        {
            send("C");
            send(std::string("A:") + (player->GetSession()->GetSecurity() >= SEC_GAMEMASTER ? "1" : "0"));
            for (auto const& [id, shape] : _shapes)
            {
                std::ostringstream line;
                line << "G:" << id << ':' << shape.FormSpell << ':' << FavouriteFoodText(id) << ':';
                bool first = true;
                for (uint32 spellId : shape.Kit)
                    if (spellId)
                    {
                        line << (first ? "" : ",") << spellId;
                        first = false;
                    }
                line << ':' << shape.Passive;
                send(line.str());
                auto hints = _hints.find(id);
                if (hints != _hints.end())
                    for (std::string const& hint : hints->second)
                        send("H:" + std::to_string(id) + ":" + hint);
            }
        }

        State& state = Get(player);
        send("B");
        for (auto const& [id, owned] : state.Shapes)
        {
            Shape const* shape = FindShape(id);
            if (!shape)
                continue;
            std::ostringstream line;
            line << "S:" << id << ':' << shape->FormSpell << ':' << (state.Worn == id ? 1 : 0) << ':'
                 << SkinName(ShownDisplay(player, *shape)) << ':' << SkinName(shape->Display);
            send(line.str());
            // The colourings follow in as many K:<shape>:<colouring>,... lines as they need (a kind of creature can
            // have dozens; one message holds 255 bytes).
            std::string const head = "K:" + std::to_string(id) + ":";
            std::string chunk;
            for (uint32 skin : owned.Skins)
            {
                std::string const name = SkinName(skin);
                if (!chunk.empty() && head.size() + chunk.size() + 1 + name.size() > 240)
                {
                    send(head + chunk);
                    chunk.clear();
                }
                chunk += (chunk.empty() ? "" : ",") + name;
            }
            if (!chunk.empty())
                send(head + chunk);
        }
        send("E:" + std::to_string(_animaPerShift));
    }
}
