/*
 * mod-devourer, task 013: Sniff. A toggle aura (SpellSniff); while it is on, creatures around the Devourer that
 * are worth eating are marked on its client.
 *
 * Why addon messages: the 3.3.5a client has no outline shader, a tracking aura cannot filter by creature entry,
 * and a per-player visible aura would need a client-side visual we cannot ship without exe changes. What always
 * works is data: the server sends the names, the client addon (tools/client/lua/DevourerMenu.lua) draws a mark
 * on the nameplates and the target frame. See docs/sniff.md.
 *
 * Protocol (prefix DVR, one line per message):
 *   Q                    a scan begins
 *   P:<N|F>:<name>|...   names of creatures worth eating: N = new shape or colouring, F = favourite food
 *   R                    the scan ends: the client takes these marks (they expire after 10 s without a refresh)
 *   Z                    Sniff is off: remove every mark
 */

#include "Devourer.h"
#include "DevourerSpellIds.h"

#include "Cell.h"
#include "CellImpl.h"
#include "Creature.h"
#include "GridNotifiers.h"
#include "GridNotifiersImpl.h"
#include "Log.h"
#include "Player.h"
#include <algorithm>
#include <string>
#include <vector>

namespace Devourer
{
    namespace
    {
        // Every creature in range, alive or dead (the dead are what Devour eats).
        struct SniffCreatureCheck
        {
            WorldObject const* Center;
            float Range;

            bool operator()(Creature* creature) const
            {
                return creature != Center && Center->IsWithinDist(creature, Range, false);
            }
        };

        // The menu splits its lines on ':' and '|'.
        std::string CleanName(std::string const& name)
        {
            std::string out;
            for (char ch : name)
                if (ch != ':' && ch != '|' && ch != ',')
                    out += ch;
            return out;
        }
    }

    char Mgr::SniffKind(Player* player, Creature const* creature)
    {
        if (!creature || creature->IsPet() || creature->IsGuardian() || creature->IsTotem() ||
            creature->IsControlledByPlayer() || creature->IsTrigger() || creature->GetName().empty())
            return 0;
        State& state = Get(player);
        if (state.Eaten.count(creature->GetGUID()))
            return 0;                                    // already fed on: nothing new in it

        // A new shape, or a colouring of an owned shape that is not owned yet (the same test Unlock makes).
        Source source;
        if (Shape const* shape = MealShape(creature, source))
        {
            auto owned = state.Shapes.find(shape->Id);
            if (owned == state.Shapes.end())
                return 'N';
            if (source.Display && source.Display != shape->Display && !owned->second.Skins.count(source.Display))
                return 'N';
        }

        if (state.Worn && IsFavouriteFood(state.Worn, creature))
            return 'F';
        return 0;
    }

    // Every SniffInterval ms while the aura is on (OnUpdate): the marks around the Devourer, nearest creatures
    // first come first served, at most SniffMaxNames names.
    void Mgr::SniffScan(Player* player)
    {
        std::list<Creature*> around;
        SniffCreatureCheck check{ player, SniffRadius };
        Acore::CreatureListSearcher<SniffCreatureCheck> searcher(player, around, check);
        Cell::VisitObjects(player, searcher, SniffRadius);

        std::vector<std::string> fresh, favourite;
        for (Creature* creature : around)
        {
            if (fresh.size() + favourite.size() >= SniffMaxNames)
                break;
            char const kind = SniffKind(player, creature);
            if (!kind)
                continue;
            std::vector<std::string>& list = kind == 'N' ? fresh : favourite;
            std::string const name = CleanName(creature->GetName());
            if (std::find(list.begin(), list.end(), name) == list.end())
                list.push_back(name);
        }

        LOG_DEBUG("module", "mod-devourer: Sniff scan for {}: {} creatures in range, {} new, {} favourite",
            player->GetName(), around.size(), fresh.size(), favourite.size());
        SendAddon(player, "Q");
        for (auto const& [kind, list] : { std::pair<char, std::vector<std::string> const&>{ 'N', fresh },
                                          std::pair<char, std::vector<std::string> const&>{ 'F', favourite } })
        {
            std::string head = std::string("P:") + kind + ":";
            std::string chunk;
            for (std::string const& name : list)
            {
                if (!chunk.empty() && head.size() + chunk.size() + 1 + name.size() > 240)
                {
                    SendAddon(player, head + chunk);
                    chunk.clear();
                }
                chunk += (chunk.empty() ? "" : "|") + name;
            }
            if (!chunk.empty())
                SendAddon(player, head + chunk);
        }
        SendAddon(player, "R");
    }

    void Mgr::SniffClear(Player* player) const
    {
        SendAddon(player, "Z");
    }
}
