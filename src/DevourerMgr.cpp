/*
 * mod-devourer: shapes, devouring, the shared shift cooldown, Hunger.
 * Released under GNU AGPL v3, like AzerothCore.
 */

#include "Devourer.h"
#include "DevourerSpellIds.h"

#include "AscensionSpecialization.h"
#include "Chat.h"
#include "Config.h"
#include "Creature.h"
#include "DatabaseEnv.h"
#include "Log.h"
#include "ObjectMgr.h"
#include "Player.h"
#include "SpellAuras.h"
#include "SpellInfo.h"
#include "SpellMgr.h"
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
        _classId = uint8(sConfigMgr->GetOption<uint32>("Devourer.ClassId", 20));
        _requireLooted = sConfigMgr->GetOption<bool>("Devourer.RequireLooted", true);
        _hungerPerMeal = sConfigMgr->GetOption<uint32>("Devourer.HungerPerMeal", 30);
        _hungerPerSwing = sConfigMgr->GetOption<uint32>("Devourer.HungerPerSwing", 2);
        _shiftCooldown = sConfigMgr->GetOption<uint32>("Devourer.ShiftCooldown", 8000);
        _skinchangerShiftCooldown = sConfigMgr->GetOption<uint32>("Devourer.SkinchangerShiftCooldown", 3000);
        _shapeBarSlot = uint8(std::min<uint32>(sConfigMgr->GetOption<uint32>("Devourer.ShapeBarSlot", 60), 140));
    }

    void Mgr::LoadWorldData()
    {
        _shapes.clear();
        _shapeByForm.clear();
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
                _shapes[shape.Id] = std::move(shape);
            } while (result->NextRow());
        }

        if (QueryResult result = WorldDatabase.Query("SELECT creature_entry, shape_id, display_id FROM devourer_shape_source"))
        {
            do
            {
                Field* f = result->Fetch();
                if (!_shapes.count(f[1].Get<uint32>()))
                    continue;
                _sources[f[0].Get<uint32>()] = { f[1].Get<uint32>(), f[2].Get<uint32>() };
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

        LoadGrowthData();
        LOG_INFO("module", "mod-devourer: {} shapes, {} colourings, {} creatures that grant them, {} evolutions",
            _shapes.size(), _skins.size(), _sources.size(), _evolutions.size());
    }

    bool Mgr::IsDevourer(Player const* player) const
    {
        return _enabled && player && player->getClass() == _classId;
    }

    uint32 Mgr::SpecOf(Player const* player) const
    {
        return GetAscensionActiveSpecialization(player);
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

    bool Mgr::Unlock(Player* player, uint32 shapeId, uint32 display, bool shiftNow)
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
            if (!isNew)
                Tell(player, "A new colouring for your " + shape->Name + " shape: " + SkinName(display) +
                    ". Wear it with /devour skin " + SkinName(display) + ".");
        }

        if (!player->HasSpell(shape->FormSpell))
            player->learnSpell(shape->FormSpell);

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

    void Mgr::GrantKit(Player* player, State& state, Shape const& shape)
    {
        RevokeKit(player, state);
        std::vector<uint32> spells(shape.Kit.begin(), shape.Kit.end());
        spells.push_back(shape.Passive);
        for (uint32 spellId : spells)
        {
            if (!spellId || player->HasSpell(spellId) || !sSpellMgr->GetSpellInfo(spellId))
                continue;
            player->learnSpell(spellId, true);
            state.Granted.push_back(spellId);
        }

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
                uint32 slot = uint32(_shapeBarSlot) + i;
                if (saved != state.Bar.end())
                {
                    auto own = saved->second.find(spellId);
                    if (own != saved->second.end())
                        slot = own->second;
                }
                if (slot >= MAX_ACTION_BUTTONS)
                    continue;                                    // NotOnBar, or out of range
                ActionButton const* there = player->GetActionButton(uint8(slot));
                if (there && !(there->GetType() == ACTION_BUTTON_SPELL && there->GetAction() == spellId))
                    continue;                                    // the player put something else there
                player->addActionButton(uint8(slot), spellId, ACTION_BUTTON_SPELL);
            }
            player->SendActionButtons(1);
        }
        state.KitShape = shape.Id;
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
            if (!spellId)
                continue;
            uint8 found = NotOnBar;
            for (uint8 slot = 0; slot < MAX_ACTION_BUTTONS; ++slot)
            {
                ActionButton const* button = player->GetActionButton(slot);
                if (!button || button->GetType() != ACTION_BUTTON_SPELL || button->GetAction() != spellId)
                    continue;
                if (found == NotOnBar)
                    found = slot;
                if (clear && std::find(state.Granted.begin(), state.Granted.end(), spellId) != state.Granted.end())
                    player->removeActionButton(slot);    // the ability is unlearned next: no dead buttons
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
        if (state.KitShape)
        {
            RememberBar(player, state, true);
            if (_shapeBarSlot)
                player->SendActionButtons(1);
        }
        state.KitShape = 0;
        for (uint32 spellId : state.Granted)
            player->removeSpell(spellId, SPEC_MASK_ALL, true);
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

    void Mgr::TeachBasics(Player* player)
    {
        if (!IsDevourer(player))
            return;
        SyncSpecSpells(player);
        if (!player->HasSpell(SpellDevour) && !player->HasSpell(SpellDevourQuick) && sSpellMgr->GetSpellInfo(SpellDevour))
            player->learnSpell(SpellDevour);
        SyncTalentSpells(player);                        // ChaosCore0.3: Quick Devour takes Devour's place
        // Form spells follow the shapes owned (a shape added by a GM or a data fix is taught here too).
        State& state = Get(player);
        // A Devourer with no shape yet gets the idol. (CoA hands out the starting items itself, so
        // playercreateinfo_item does not reach new characters.)
        if (state.Shapes.empty() && !player->HasItemCount(ItemSethrakIdol, 1, true) &&
            sObjectMgr->GetItemTemplate(ItemSethrakIdol))
        {
            if (player->AddItem(ItemSethrakIdol, 1))
                Tell(player, "An Idol of the Sethrak is in your bags. Use it to take your first shape.");
            else
                Tell(player, "Your bags are full: make room for the Idol of the Sethrak and log in again.");
        }
        for (auto const& [id, owned] : state.Shapes)
            if (Shape const* shape = FindShape(id))
                if (!player->HasSpell(shape->FormSpell))
                    player->learnSpell(shape->FormSpell);
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
}
