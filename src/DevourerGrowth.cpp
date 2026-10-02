/*
 * mod-devourer: growth. A worn form earns Bio Points (BP) from every meal, weighted by the form's diet and by how
 * rare the meal was. With enough BP, the level and the evolution's tasks done, the form evolves: the next form of
 * its line is unlocked and forced on, like a first devour. The earlier form stays available.
 * Released under GNU AGPL v3, like AzerothCore.
 *
 *   world       devourer_diet             shape, creature type (0 = anything else) -> BP per meal
 *               devourer_evolution        from shape -> to shape, BP and level needed
 *               devourer_evolution_task   the evolution's tasks (kill, be hit by, devour rare, devour type)
 *   characters  character_devourer_growth BP per shape
 *               character_devourer_task   task progress per evolution
 */

#include "Devourer.h"

#include "Creature.h"
#include "DatabaseEnv.h"
#include "Player.h"
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
                "SELECT from_shape, to_shape, bp, min_level, any_task FROM devourer_evolution"))
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
                if (!_shapes.count(evo.From) || !_shapes.count(evo.To))
                    continue;
                _evolutions.push_back(std::move(evo));
            } while (result->NextRow());
        }

        if (QueryResult result = WorldDatabase.Query(
                "SELECT to_shape, task_id, kind, value, count, text, name_part FROM devourer_evolution_task "
                "ORDER BY task_id"))
        {
            do
            {
                Field* f = result->Fetch();
                EvolutionTask task;
                uint32 const to = f[0].Get<uint32>();
                task.Id = f[1].Get<uint32>();
                task.Kind = f[2].Get<uint8>();
                task.Value = f[3].Get<uint32>();
                task.Count = std::max<uint32>(1, f[4].Get<uint32>());
                task.Text = f[5].Get<std::string>();
                std::string parts = f[6].Get<std::string>();
                std::transform(parts.begin(), parts.end(), parts.begin(), ::tolower);
                for (size_t start = 0; start <= parts.size();)
                {
                    size_t const end = std::min(parts.find('|', start), parts.size());
                    if (end > start)
                        task.Names.push_back(parts.substr(start, end - start));
                    start = end + 1;
                }
                for (Evolution& evo : _evolutions)
                    if (evo.To == to)
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

    void Mgr::GainBio(Player* player, Creature const* meal)
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
            if (gained)
            {
                uint32& bp = state.Bio[worn->Id];
                bp += gained;
                state.GrowthDirty = true;
                std::ostringstream text;
                text << "+" << gained << " BP" << (favourite ? ", a favourite meal" : "") << " (" << worn->Name
                     << ": " << bp << " BP)";
                Tell(player, text.str());
            }
            else
                Tell(player, "Your " + worn->Name + " body gains nothing from that meal.");
        }

        TaskEvent(player, TaskDevourRarity, Rarity(meal));
        TaskEvent(player, TaskDevourType, meal->GetCreatureType());
        TaskEvent(player, TaskDevourName, meal->GetCreatureType(), 1, meal->GetName());
        CheckEvolution(player);
    }

    void Mgr::TaskEvent(Player* player, uint8 kind, uint32 value, uint32 amount, std::string const& name)
    {
        std::string lower = name;
        std::transform(lower.begin(), lower.end(), lower.begin(), ::tolower);
        auto itr = _states.find(player->GetGUID().GetCounter());
        if (itr == _states.end() || !itr->second.Worn)
            return;
        State& state = itr->second;

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
                    default: break;
                }
                if (!matches)
                    continue;
                uint32& progress = state.Tasks[{ evo.To, task.Id }];
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
        if (finishedOne)
            CheckEvolution(player);
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
                bool const finished = state.Tasks[{ evo.To, task.Id }] >= task.Count;
                if (evo.AnyTask && finished)
                    done = true;
                else if (!evo.AnyTask && !finished)
                    done = false;
            }
            if (!done)
                continue;

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
            return;                                      // one evolution at a time
        }
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
                "REPLACE INTO character_devourer_task (guid, to_shape, task_id, progress) VALUES ({}, {}, {}, {})",
                guid, key.first, key.second, progress);
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
                text << "; " << task.Text << " " << std::min(task.Count, state.Tasks[{ evo.To, task.Id }]) << "/"
                     << task.Count;
        }
        if (text.str().empty() && state.Bio.count(shapeId))
            text << "  " << state.Bio[shapeId] << " BP";
        return text.str();
    }
}
