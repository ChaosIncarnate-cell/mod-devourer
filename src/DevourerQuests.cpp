/*
 * mod-devourer: the Devourer's quests in the world (task 021).
 * Released under GNU AGPL v3, like AzerothCore.
 *
 * Hagatha's lanterns burn where the world is thin, one in each region the Devourer passes through; the sisters speak
 * through them and send it hunting. The quests are plain quests (tools/devourer_quests.py writes them); this file only
 * gives the objectives the core has no word for: "devour", "slay while wearing a shape", "go and look", and the
 * things the witches leave in the world to be touched. Each of those objectives has a credit creature of its own
 * (never spawned), and the rules here say which event gives that credit.
 *
 * Data: DevourerQuestsIds.h and data/sql/db-world/2026_10_05_10_devourer_quests.sql, both written by the tool.
 */

#include "Devourer.h"
#include "DevourerQuests.h"
#include "DevourerQuestsIds.h"

#include "Chat.h"
#include "Creature.h"
#include "CreatureAI.h"
#include "GameObject.h"
#include "GameObjectScript.h"
#include "ObjectAccessor.h"
#include "Player.h"
#include "PlayerScript.h"
#include "Random.h"
#include "TemporarySummon.h"
#include <set>
#include <unordered_map>

using namespace Devourer;
using namespace Devourer::Quests;

namespace
{
    constexpr uint32 VisitCheckEvery = 1000;     // ms between two looks at the "go and look" objectives
    constexpr uint32 UseRespawnSeconds = 60;     // a touched object comes back after this
    constexpr uint32 LureLifetime = 300000;      // ms a lured beast waits (its corpse then follows its own decay)

    bool Wears(Player* player, CreditRule const& rule)
    {
        if (!rule.Shapes[0])
            return true;
        uint32 const worn = sDevourer.Get(player).Worn;
        for (uint32 shape : rule.Shapes)
            if (shape && shape == worn)
                return true;
        return false;
    }

    bool Matches(Creature const* creature, CreditRule const& rule)
    {
        CreatureTemplate const* info = creature->GetCreatureTemplate();
        switch (rule.Filter)
        {
            case FilterEntry: return creature->GetEntry() == rule.Value;
            case FilterFamily: return info->family == rule.Value;
            case FilterType: return info->type == rule.Value;
            case FilterElite: return info->rank != CREATURE_ELITE_NORMAL;
            case FilterAny: return true;
            default: return false;
        }
    }

    // Every rule of this event that fits gives its credit once (two rules may share a credit: "this or that").
    void Credit(Player* player, Creature* creature, uint8 event)
    {
        if (!sDevourer.IsDevourer(player) || !creature)
            return;
        std::set<uint32> given;
        for (CreditRule const& rule : CreditRules)
        {
            if (rule.Event != event || given.count(rule.Credit))
                continue;
            if (player->GetQuestStatus(rule.Quest) != QUEST_STATUS_INCOMPLETE)
                continue;
            if (!Matches(creature, rule) || !Wears(player, rule))
                continue;
            player->KilledMonsterCredit(rule.Credit);
            given.insert(rule.Credit);
        }
    }

    void Visits(Player* player)
    {
        for (VisitRule const& rule : VisitRules)
        {
            if (player->GetMapId() != rule.Map || player->GetQuestStatus(rule.Quest) != QUEST_STATUS_INCOMPLETE)
                continue;
            if (player->GetExactDist2d(rule.X, rule.Y) > rule.Radius)
                continue;
            player->KilledMonsterCredit(rule.Credit);   // the core counts it only while that objective is open
        }
    }
}

namespace Devourer::Quests
{
    void OnMeal(Player* player, Creature* meal)
    {
        Credit(player, meal, EventMeal);
    }
}

class devourer_quests_player : public PlayerScript
{
public:
    devourer_quests_player() : PlayerScript("devourer_quests_player") { }

    void OnPlayerCreatureKill(Player* killer, Creature* killed) override
    {
        Credit(killer, killed, EventKill);
    }

    void OnPlayerCreatureKilledByPet(Player* owner, Creature* killed) override
    {
        Credit(owner, killed, EventKill);
    }

    void OnPlayerUpdate(Player* player, uint32 diff) override
    {
        if (!sDevourer.IsDevourer(player))
            return;
        uint32& timer = visitTimers[player->GetGUID().GetCounter()];
        if (timer > diff)
        {
            timer -= diff;
            return;
        }
        timer = VisitCheckEvery;
        Visits(player);
    }

    void OnPlayerLogout(Player* player) override
    {
        visitTimers.erase(player->GetGUID().GetCounter());
    }

private:
    std::unordered_map<ObjectGuid::LowType, uint32> visitTimers;
};

// The things the witches leave in the world. A token: touching it counts for the quest it belongs to, then it fades
// for a minute. A lure (Hagatha's bait): it calls the creature the quest wants (one only this Devourer sees), so a
// beast that comes back only every few hours, or that somebody else took, can still be hunted. Either one only answers
// while its quest is in the log (the gameobject template carries the quest).
class go_devourer_quest_object : public GameObjectScript
{
public:
    go_devourer_quest_object() : GameObjectScript("go_devourer_quest_object") { }

    bool OnGossipHello(Player* player, GameObject* go) override
    {
        for (UseRule const& rule : UseRules)
        {
            if (rule.Object != go->GetEntry() || player->GetQuestStatus(rule.Quest) != QUEST_STATUS_INCOMPLETE)
                continue;
            if (rule.Summon)
                Lure(player, go, rule.Summon);
            else
            {
                player->KilledMonsterCredit(rule.Credit);
                player->HandleEmoteCommand(EMOTE_ONESHOT_LOOT);
                go->DespawnOrUnsummon(0ms, Seconds(UseRespawnSeconds));
            }
            return true;
        }
        return true;                              // nobody else may use it
    }

private:
    std::unordered_map<ObjectGuid::LowType, ObjectGuid> lured;   // Devourer -> what its bait called

    void Lure(Player* player, GameObject* go, uint32 entry)
    {
        ObjectGuid& called = lured[player->GetGUID().GetCounter()];
        if (Creature* already = ObjectAccessor::GetCreature(*player, called))
            if (already->IsInWorld() && already->GetEntry() == entry)
            {
                ChatHandler(player->GetSession()).SendNotification("It is already on its way.");
                return;
            }
        player->HandleEmoteCommand(EMOTE_ONESHOT_KNEEL);
        Position at = go->GetPosition();
        go->MovePositionToFirstCollision(at, 6.0f, float(rand_norm()) * 2.0f * float(M_PI));
        if (TempSummon* beast = go->SummonCreature(entry, at.GetPositionX(), at.GetPositionY(), at.GetPositionZ(),
            at.GetAngle(player), TEMPSUMMON_TIMED_OR_CORPSE_DESPAWN, LureLifetime, nullptr, true))
        {
            called = beast->GetGUID();
            if (beast->AI())
                beast->AI()->AttackStart(player);
        }
    }
};

void AddSC_devourer_quests()
{
    new devourer_quests_player();
    new go_devourer_quest_object();
}
