/*
 * mod-devourer: growth. A worn form earns Bio Points (BP) from every meal, weighted by the form's diet and by how
 * rare the meal was. With enough BP, the level and the evolution's tasks done, the form evolves: the next form of
 * its line is unlocked and forced on, like a first devour. The earlier form stays available.
 * Released under GNU AGPL v3, like AzerothCore.
 *
 *   world       devourer_diet             shape, creature type (0 = anything else) -> BP per meal
 *               devourer_evolution        from shape -> to shape, BP and level needed
 *               devourer_evolution_task   the evolution's tasks (kill, be hit by, devour rare / type / name / family /
 *                                         one creature, hit or use a spell, deal or take damage, heal: TaskKind)
 *   characters  character_devourer_growth BP per shape
 *               character_devourer_task   task progress per evolution
 */

#include "Devourer.h"

#include "DevourerSistersIds.h"

#include "Chat.h"
#include "Creature.h"
#include "CreatureTextMgr.h"
#include "DatabaseEnv.h"
#include "ObjectMgr.h"
#include "Player.h"
#include "QuestDef.h"
#include "WorldPacket.h"
#include "WorldSession.h"
#include <algorithm>
#include <sstream>

namespace Devourer
{
    void Mgr::LoadGrowthData()
    {
        _diet.clear();
        _evolutions.clear();

        if (QueryResult result = WorldDatabase.Query("SELECT shape_id, creature_type, bp FROM devourer_diet"))
        {
            do
            {
                Field* f = result->Fetch();
                _diet[f[0].Get<uint32>()][f[1].Get<uint32>()] = f[2].Get<uint32>();
            } while (result->NextRow());
        }

        if (QueryResult result = WorldDatabase.Query(
                "SELECT from_shape, to_shape, bp, min_level, any_task, quest FROM devourer_evolution"))
        {
            do
            {
                Field* f = result->Fetch();
                Evolution evo;
                evo.From = f[0].Get<uint32>();
                evo.To = f[1].Get<uint32>();
                evo.Bp = f[2].Get<uint32>();
                evo.MinLevel = f[3].Get<uint8>();
                evo.AnyTask = f[4].Get<uint8>() != 0;
                evo.Quest = f[5].Get<uint32>();
                if (!_shapes.count(evo.From) || !_shapes.count(evo.To))
                    continue;
                _evolutions.push_back(std::move(evo));
            } while (result->NextRow());
        }

        if (QueryResult result = WorldDatabase.Query(
                "SELECT from_shape, to_shape, task_id, kind, value, count, text, name_part FROM devourer_evolution_task "
                "ORDER BY task_id"))
        {
            do
            {
                Field* f = result->Fetch();
                EvolutionTask task;
                uint32 const from = f[0].Get<uint32>();      // 0: every road into `to` (rows from before the roads)
                uint32 const to = f[1].Get<uint32>();
                task.Id = f[2].Get<uint32>();
                task.Kind = f[3].Get<uint8>();
                task.Value = f[4].Get<uint32>();
                task.Count = std::max<uint32>(1, f[5].Get<uint32>());
                task.Text = f[6].Get<std::string>();
                std::string parts = f[7].Get<std::string>();
                std::transform(parts.begin(), parts.end(), parts.begin(), ::tolower);
                for (size_t start = 0; start <= parts.size();)
                {
                    size_t const end = std::min(parts.find('|', start), parts.size());
                    if (end > start)
                        task.Names.push_back(parts.substr(start, end - start));
                    start = end + 1;
                }
                for (Evolution& evo : _evolutions)
                    if (evo.To == to && (!from || evo.From == from))
                        evo.Tasks.push_back(task);
            } while (result->NextRow());
        }
    }

    // Normal 1, elite 3, rare 5, rare elite 8, bosses 20.
    uint32 Mgr::Rarity(Creature const* creature)
    {
        if (!creature)
            return 1;
        if (creature->isWorldBoss() || creature->IsDungeonBoss())
            return 20;
        switch (creature->GetCreatureTemplate()->rank)
        {
            case CREATURE_ELITE_ELITE:     return 3;
            case CREATURE_ELITE_RARE:      return 5;
            case CREATURE_ELITE_RAREELITE: return 8;
            case CREATURE_ELITE_WORLDBOSS: return 20;
            default:                       return 1;
        }
    }

    void Mgr::GainBio(Player* player, Creature const* meal, float factor)
    {
        if (!meal || !IsDevourer(player))
            return;
        State& state = Get(player);
        Shape const* worn = FindShape(state.Worn);
        if (!worn)
            return;

        auto diet = _diet.find(worn->Id);
        if (diet != _diet.end())
        {
            uint32 perMeal = 0;
            auto type = diet->second.find(meal->GetCreatureType());
            if (type != diet->second.end())
                perMeal = type->second;
            else if ((type = diet->second.find(0)) != diet->second.end())
                perMeal = type->second;

            // Task 009 (owner, 2026-10-01): every Devourer gets twice the Bio Points from its shape's favourite
            // food (before: only a Glutton; the Glutton keeps its double Gorged for it, see FeedGlutton).
            uint32 gained = perMeal * Rarity(meal);
            bool const favourite = gained && IsFavouriteFood(worn->Id, meal);
            if (favourite)
                gained *= 2;
            if (factor != 1.0f)                      // task 015: a shared meal (the pet's share), a bonus on top
                gained = uint32(gained * factor);
            if (gained)
            {
                uint32& bp = state.Bio[worn->Id];
                bp += gained;
                state.GrowthDirty = true;
                std::ostringstream text;
                text << "+" << gained << " BP" << (factor != 1.0f ? ", a shared meal" : favourite ? ", a favourite meal" : "")
                     << " (" << worn->Name
                     << ": " << bp << " BP)";
                Tell(player, text.str());
            }
            else if (factor == 1.0f)
                Tell(player, "Your " + worn->Name + " body gains nothing from that meal.");
        }
        if (factor != 1.0f)
            return;                                  // a bonus share: the tasks and evolution counted the meal once

        TaskEvent(player, TaskDevourRarity, Rarity(meal));
        TaskEvent(player, TaskDevourType, meal->GetCreatureType());
        TaskEvent(player, TaskDevourName, meal->GetCreatureType(), 1, meal->GetName());
        TaskEvent(player, TaskDevourFamily, meal->GetCreatureTemplate()->family);
        TaskEvent(player, TaskDevourEntry, meal->GetEntry());
        CheckEvolution(player);
    }

    void Mgr::TaskEvent(Player* player, uint8 kind, uint32 value, uint32 amount, std::string const& name)
    {
        if (!amount)
            return;
        auto itr = _states.find(player->GetGUID().GetCounter());
        if (itr == _states.end() || !itr->second.Worn)
            return;
        State& state = itr->second;
        std::string lower = name;
        std::transform(lower.begin(), lower.end(), lower.begin(), ::tolower);

        bool finishedOne = false;
        for (Evolution const& evo : _evolutions)
        {
            if (evo.From != state.Worn || state.Shapes.count(evo.To))
                continue;
            for (EvolutionTask const& task : evo.Tasks)
            {
                if (task.Kind != kind)
                    continue;
                bool matches = false;
                switch (kind)
                {
                    case TaskKill:         matches = !task.Value || task.Value == value; break;
                    case TaskHitBy:        matches = (task.Value & value) != 0; break;
                    case TaskDevourRarity: matches = value >= task.Value; break;
                    case TaskDevourType:   matches = task.Value == value; break;
                    case TaskDevourName:
                        matches = !task.Value || task.Value == value;
                        if (matches)
                            matches = std::any_of(task.Names.begin(), task.Names.end(),
                                [&lower](std::string const& part) { return lower.find(part) != std::string::npos; });
                        break;
                    case TaskSpellHit:     matches = task.Value == value; break;
                    case TaskDevourFamily: matches = value && task.Value == value; break;
                    case TaskDevourEntry:  matches = task.Value == value; break;
                    case TaskSpellCast:    matches = task.Value == value; break;
                    case TaskDealDamage:
                    case TaskTakeDamage:   matches = !task.Value || (task.Value & value) != 0; break;
                    case TaskHeal:         matches = true; break;
                    default: break;
                }
                if (!matches)
                    continue;
                uint32& progress = state.Tasks[{ Road(evo.From, evo.To), task.Id }];
                if (progress >= task.Count)
                    continue;
                progress = std::min(task.Count, progress + amount);
                state.GrowthDirty = true;
                if (progress >= task.Count)
                {
                    Tell(player, "Growth: " + task.Text + " - done.");
                    finishedOne = true;
                }
            }
        }
        // Task 017: a moment later, so an evolution never shifts the Devourer inside a damage or spell hook.
        if (finishedOne)
            Defer(player, [this, player]() { CheckEvolution(player); });
    }

    void Mgr::CheckEvolution(Player* player)
    {
        State& state = Get(player);
        for (Evolution const& evo : _evolutions)
        {
            if (evo.From != state.Worn || state.Shapes.count(evo.To))
                continue;
            if (player->GetLevel() < evo.MinLevel || state.Bio[evo.From] < evo.Bp)
                continue;
            bool done = !evo.AnyTask || evo.Tasks.empty();
            for (EvolutionTask const& task : evo.Tasks)
            {
                bool const finished = state.Tasks[{ Road(evo.From, evo.To), task.Id }] >= task.Count;
                if (evo.AnyTask && finished)
                    done = true;
                else if (!evo.AnyTask && !finished)
                    done = false;
            }
            if (!done)
                continue;
            if (evo.Quest && OfferMolt(player, evo))
                return;                                  // task 018: the sisters do the rest (Molt)
            Evolve(player, evo);
            return;                                      // one evolution at a time
        }
    }

    // Task 018: a form that is ready to evolve and has a molt quest gets it in the log, already done, and Wren calls
    // from the In-Between. False when it should simply grow now (no quest data, or the quest is handed in already).
    bool Mgr::OfferMolt(Player* player, Evolution const& evo)
    {
        Quest const* quest = sObjectMgr->GetQuestTemplate(evo.Quest);
        if (!quest || player->GetQuestRewardStatus(evo.Quest))
            return false;
        if (player->GetQuestStatus(evo.Quest) != QUEST_STATUS_NONE)
            return true;                                 // in the log: waiting for the trip home
        if (!player->CanAddQuest(quest, false))
            return true;                                 // a full log: the next meal asks again
        player->AddQuestAndCheckCompletion(quest, nullptr);

        // Wren's voice from nowhere (she lives on the In-Between's map): her creature_text line as her whisper.
        CreatureTemplate const* wren = sObjectMgr->GetCreatureTemplate(Sisters::NpcWren);
        std::string const text = sCreatureTextMgr->GetLocalizedChatString(Sisters::NpcWren, 0, Sisters::WrenMoltReady,
            0, player->GetSession()->GetSessionDbLocaleIndex());
        if (wren && !text.empty())
        {
            WorldPacket data;
            ChatHandler::BuildChatPacket(data, CHAT_MSG_MONSTER_WHISPER, LANG_UNIVERSAL, ObjectGuid::Empty,
                player->GetGUID(), text, 0, wren->Name);
            player->SendDirectMessage(&data);
        }
        Shape const* from = FindShape(evo.From);
        Shape const* to = FindShape(evo.To);
        Tell(player, "Your " + (from ? from->Name : std::string("old")) + " body is ready to molt into a " +
            (to ? to->Name : std::string("new shape")) + ". Go back to the sisters in the In-Between (.inbetween) and "
            "let Wren peel it.");
        return true;
    }

    bool Mgr::Molt(Player* player, uint32 questId)
    {
        if (!questId || !IsDevourer(player))
            return false;
        State& state = Get(player);
        for (Evolution const& evo : _evolutions)
            if (evo.Quest == questId && !state.Shapes.count(evo.To))
            {
                Evolve(player, evo);
                return true;
            }
        return false;
    }

    void Mgr::Evolve(Player* player, Evolution const& evo)
    {
        Shape const* from = FindShape(evo.From);
        Shape const* to = FindShape(evo.To);
        Tell(player, "Your " + from->Name + " body has eaten enough. It tears open, and a " + to->Name +
            " crawls out.");
        SaveGrowth(player);
        // ChaosCore0.3: the grown body keeps its colouring - the colouring of the new shape whose young look
        // like the old body (a teal Baby Berserker grows into a teal Berserker).
        uint32 const young = ShownDisplay(player, *from);
        uint32 grown = 0;
        for (auto const& [display, skin] : _skins)
            if (skin.ShapeId == evo.To && skin.BroodDisplay == young)
                grown = display;
        Unlock(player, evo.To, grown, false);
        if (grown && grown != to->Display)
            ChooseSkin(player, evo.To, grown);
        Unlock(player, evo.To, 0, true);             // the first time, the body forces itself on its eater
    }

    void Mgr::SaveGrowth(Player* player)
    {
        auto itr = _states.find(player->GetGUID().GetCounter());
        if (itr == _states.end())
            return;
        State& state = itr->second;
        uint32 const guid = player->GetGUID().GetCounter();
        for (auto const& [shapeId, bp] : state.Bio)
            CharacterDatabase.Execute("REPLACE INTO character_devourer_growth (guid, shape_id, bp) VALUES ({}, {}, {})",
                guid, shapeId, bp);
        for (auto const& [key, progress] : state.Tasks)
            CharacterDatabase.Execute(
                "REPLACE INTO character_devourer_task (guid, from_shape, to_shape, task_id, progress) "
                "VALUES ({}, {}, {}, {}, {})", guid, key.first >> 16, key.first & 0xFFFF, key.second, progress);
        state.GrowthDirty = false;
    }

    std::string Mgr::GrowthText(Player* player, uint32 shapeId)
    {
        State& state = Get(player);
        std::ostringstream text;
        for (Evolution const& evo : _evolutions)
        {
            if (evo.From != shapeId)
                continue;
            Shape const* to = FindShape(evo.To);
            if (!text.str().empty())
                text << "\n";
            if (state.Shapes.count(evo.To))
            {
                text << "  Grew into: " << to->Name;
                continue;
            }
            text << "  Grows into " << to->Name << ": " << state.Bio[shapeId] << "/" << evo.Bp << " BP";
            if (player->GetLevel() < evo.MinLevel)
                text << ", level " << uint32(evo.MinLevel);
            if (evo.AnyTask && evo.Tasks.size() > 1)
                text << "; any one of";
            for (EvolutionTask const& task : evo.Tasks)
                text << "; " << task.Text << " " << std::min(task.Count, state.Tasks[{ Road(evo.From, evo.To), task.Id }]) << "/"
                     << task.Count;
        }
        if (text.str().empty() && state.Bio.count(shapeId))
            text << "  " << state.Bio[shapeId] << " BP";
        return text.str();
    }
}
