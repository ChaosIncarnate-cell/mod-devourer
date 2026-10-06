/*
 * mod-devourer: the Devourer's quests in the world (task 021).
 * Released under GNU AGPL v3, like AzerothCore.
 *
 * Hagatha's lanterns burn where the world is thin, one in each region the Devourer passes through; the sisters speak
 * through them and send it out. The quests are plain quests (tools/devourer_quests.py writes them); this file gives the
 * objectives the core has no word for, each counted through a credit creature of its own (never spawned):
 *   meals        devour something (Mgr::EatShape calls OnMeal), maybe in a certain shape, maybe with Bramble watching
 *   kills        slay something while wearing a shape
 *   emotes       /pet, /roar, ... at a creature; a roar can send it running
 *   spells       use a form's ability on a creature (Tongue Pull a murloc, Hind Kick a worker, ...)
 *   visits       be at a place
 *   scent trails follow a trail with Sniff on; the end of it calls the beast that left it
 *   objects      touch what the witches left (a token), or wake it (Hagatha's bait calls a beast, or a swarm)
 * Every rule only answers while its quest is open in the Devourer's log.
 *
 * Data: DevourerQuestsIds.h and data/sql/db-world/2026_10_05_10_devourer_quests.sql, both written by the tool.
 */

#include "Devourer.h"
#include "DevourerQuests.h"
#include "DevourerQuestsIds.h"

#include "AllSpellScript.h"
#include "CreatureScript.h"
#include "DatabaseEnv.h"
#include "GameTime.h"
#include "Mail.h"
#include "ScriptedGossip.h"
#include "Timer.h"
#include "Chat.h"
#include "Config.h"
#include "Creature.h"
#include "CreatureAI.h"
#include "GameObject.h"
#include "GameObjectScript.h"
#include "Group.h"
#include "MotionMaster.h"
#include "ObjectAccessor.h"
#include "Player.h"
#include "PlayerScript.h"
#include "Random.h"
#include "Spell.h"
#include "SpellInfo.h"
#include "TemporarySummon.h"
#include "WorldScript.h"
#include "WorldSession.h"
#if __has_include("ExtrasHooks.h")
#include "ExtrasHooks.h"                       // mod-chromatica-extras: one campfire for everyone (task 021)
#define DEVOURER_ONE_CAMPFIRE 1
#endif
#include <cmath>
#include <set>
#include <string>
#include <unordered_map>
#include <vector>

using namespace Devourer;
using namespace Devourer::Quests;

namespace
{
    constexpr uint32 TickEvery = 1000;           // ms between two looks at visits and scent trails
    constexpr uint32 HintEvery = 3;              // ticks between two scent hints
    constexpr uint32 UseRespawnSeconds = 60;     // a touched token comes back after this
    constexpr uint32 SummonLifetime = 300000;    // ms a called beast waits (its corpse then follows its own decay)
    constexpr float EmoteRange = 15.0f;          // yards: close enough to pet or to roar at
    constexpr float CompanionRange = 30.0f;      // yards: Bramble close enough to watch
    constexpr uint32 FleeTime = 8000;            // ms a frightened creature runs
    constexpr uint32 FollowTime = 20;            // seconds a spared creature follows before it goes home
    constexpr uint32 TaleLineEvery = 6000;       // ms between two lines of a campfire tale
    constexpr float FollowerLeash = 60.0f;       // yards: a staying follower that falls behind is brought back
    constexpr float FishRange = 25.0f;           // yards: the ottuk close enough to share a fish with
    constexpr uint32 WrenEntry = 9101301;        // Wren Hollowmoor: the letters come from her

    std::string companionName = "Bramble";       // Devourer.WitchCompanion, the same option as the sisters'

    using Key = ObjectGuid::LowType;

    struct Trail
    {
        uint8 Stage = 0;                          // the next point; == Count: the end was reached
        uint8 Hint = 0;
        ObjectGuid Beast;
    };

    std::unordered_map<Key, std::set<std::pair<uint32, ObjectGuid>>> counted;   // creatures an emote or spell counted
    std::unordered_map<Key, std::unordered_map<uint32, Trail>> trails;           // per Devourer, per quest
    std::unordered_map<Key, uint32> tickTimers;
    std::unordered_map<Key, std::vector<ObjectGuid>> called;                    // what a Devourer's objects woke
    std::set<Key> telling;                                                     // a campfire tale is running
    std::unordered_map<Key, uint32> fireside;                                  // fallback: ms sat by a fire with Bramble
    std::unordered_map<Key, std::unordered_map<uint32, uint32>> staying;       // ms stood still at a visit, by credit

    struct Carry
    {
        int32 Left = 0;                           // ms before it goes dark / escapes (0: no timer)
        bool Dark = false;
    };
    std::unordered_map<Key, std::unordered_map<uint32, Carry>> carrying;      // per Devourer, per quest
    std::unordered_map<Key, std::vector<std::pair<ObjectGuid, uint32>>> followers;   // stay until the quest ends
    std::unordered_map<Key, uint8> slowedBy;                                    // the slow a carry applied (%)
    std::unordered_map<Key, std::set<ObjectGuid>> fooled;                      // pack members that take it for kin

    bool Open(Player* player, uint32 quest)
    {
        return player->GetQuestStatus(quest) == QUEST_STATUS_INCOMPLETE;
    }

    bool Wears(Player* player, uint32 const (&shapes)[4])
    {
        if (!shapes[0])
            return true;
        uint32 const worn = sDevourer.Get(player).Worn;
        for (uint32 shape : shapes)
            if (shape && shape == worn)
                return true;
        return false;
    }

    uint32 Hour()
    {
        tm const lt = Acore::Time::TimeBreakdown(GameTime::GetGameTime().count());
        return uint32(lt.tm_hour);
    }

    bool IsNight() { uint32 const h = Hour(); return h >= 21 || h < 6; }
    bool IsDawn() { uint32 const h = Hour(); return h >= 5 && h < 8; }

    // The conditions a visit or a touch may ask for (VisitFlag / Flag bits shared by both tables).
    bool Conditions(Player* player, uint8 flags, uint8 night, uint8 dawn, uint8 walking, uint8 noFlying, uint8 sniff,
                    uint8 noSniff)
    {
        if ((flags & night) && !IsNight())
            return false;
        if ((flags & dawn) && !IsDawn())
            return false;
        if ((flags & walking) && (!player->IsWalking() || player->IsMounted()))
            return false;
        if ((flags & noFlying) && (player->IsFlying() || player->HasAuraType(SPELL_AURA_FLY) ||
                                   player->HasAuraType(SPELL_AURA_MOD_INCREASE_MOUNTED_FLIGHT_SPEED)))
            return false;
        if ((flags & sniff) && !player->HasAura(SpellSniff))
            return false;
        if ((flags & noSniff) && player->HasAura(SpellSniff))
            return false;
        return true;
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

    // The witches' companion, in the Devourer's group and close by.
    Player* Companion(Player* player)
    {
        Group* group = player->GetGroup();
        if (!group || companionName.empty())
            return nullptr;
        for (GroupReference* itr = group->GetFirstMember(); itr; itr = itr->next())
            if (Player* member = itr->GetSource())
                if (member != player && member->IsInMap(player) && member->IsAlive() &&
                    member->GetName() == companionName && member->IsWithinDist(player, CompanionRange))
                    return member;
        return nullptr;
    }

    void TellTale(Player* player, UseRule const& rule);   // the fallback teller (defined with the objects below)

    // The sisters' tale a Devourer carries right now (a campfire quest in its log), if any.
    UseRule const* PendingTale(Player* player)
    {
        for (UseRule const& rule : UseRules)
            if (rule.LineCount && Open(player, rule.Quest))
                return &rule;
        return nullptr;
    }

    // Every rule of this event that fits gives its credit once (two rules may share a credit: "this or that").
    void Credit(Player* player, Creature* creature, uint8 event, uint32 detail = 0)
    {
        if (!creature || !sDevourer.IsDevourer(player))
            return;
        std::set<uint32> given;
        for (CreditRule const& rule : CreditRules)
        {
            if (rule.Event != event || rule.Detail != detail || given.count(rule.Credit) || !Open(player, rule.Quest))
                continue;
            if (!Matches(creature, rule) || !Wears(player, rule.Shapes))
                continue;
            Player* companion = nullptr;
            if (rule.Flags & FlagCompanion)
            {
                companion = Companion(player);
                if (!companion)
                    continue;                     // Bramble was not there to see it
            }
            if (rule.Flags & FlagFail)
            {
                // It was the one the quest asked to spare.
                player->FailQuest(rule.Quest);
                continue;
            }
            if ((event == EventEmote || event == EventSpell || event == EventStruck) &&
                !counted[player->GetGUID().GetCounter()].insert({ rule.Credit, creature->GetGUID() }).second)
                continue;                         // this one counted already
            player->KilledMonsterCredit(rule.Credit);
            given.insert(rule.Credit);
            if (companion && rule.Line && *rule.Line)
                companion->Say(rule.Line, LANG_UNIVERSAL);
            if ((rule.Flags & FlagFlee) && creature->IsAlive())
                creature->GetMotionMaster()->MoveFleeing(player, FleeTime);
            if ((rule.Flags & FlagFollow) && creature->IsAlive())
            {
                // Spared: it trots after the Devourer for a while, then goes home.
                creature->SetReactState(REACT_PASSIVE);
                creature->GetMotionMaster()->MoveFollow(player, 2.5f, float(M_PI) * 0.75f);
                creature->DespawnOrUnsummon(Seconds(FollowTime));
            }
        }
    }

    // Something a quest calls into the world (a lured beast, a swarm, the beast at the end of a trail): only this
    // Devourer sees it, and if it is hostile it comes for the Devourer.
    Creature* Call(Player* player, uint32 entry, float x, float y, float z)
    {
        TempSummon* beast = player->SummonCreature(entry, x, y, z, player->GetAngle(x, y) + float(M_PI),
            TEMPSUMMON_TIMED_OR_CORPSE_DESPAWN, SummonLifetime, nullptr, true);
        if (!beast)
            return nullptr;
        if (beast->AI() && beast->IsHostileTo(player))
            beast->AI()->AttackStart(player);  // a spared one is not hostile: it waits to be found
        called[player->GetGUID().GetCounter()].push_back(beast->GetGUID());
        return beast;
    }

    bool StillHere(Player* player, uint32 entry)
    {
        for (ObjectGuid const& guid : called[player->GetGUID().GetCounter()])
            if (Creature* beast = ObjectAccessor::GetCreature(*player, guid))
                if (beast->IsInWorld() && beast->GetEntry() == entry)
                    return true;
        return false;
    }

    void Visits(Player* player)
    {
        for (VisitRule const& rule : VisitRules)
        {
            if (!rule.Quest || player->GetMapId() != rule.Map || !Open(player, rule.Quest))
                continue;
            if (!Wears(player, rule.Shapes) || player->GetExactDist2d(rule.X, rule.Y) > rule.Radius)
                continue;
            if (player->GetPositionZ() < rule.Above)
                continue;                         // the top, not the foot of it
            if ((rule.Flags & VisitQuiet) && player->IsInCombat())
                continue;                         // it has to walk in unnoticed
            if (!Conditions(player, rule.Flags, VisitNight, VisitDawn, VisitWalking, VisitNoFlying, VisitSniff, VisitNoSniff))
                continue;
            if (rule.Seconds)
            {
                // Stay a while: still (the bronze flight's minute) or just there (the hover, the sitting owl).
                uint32& stayed = staying[player->GetGUID().GetCounter()][rule.Credit];
                if ((rule.Flags & VisitStill) && player->isMoving())
                {
                    stayed = 0;
                    continue;
                }
                stayed += TickEvery;
                if (stayed < rule.Seconds * 1000)
                    continue;
            }
            player->KilledMonsterCredit(rule.Credit);   // the core counts it only while that objective is open
            if (rule.Achievement)
                player->UpdateAchievementCriteria(ACHIEVEMENT_CRITERIA_TYPE_BE_SPELL_TARGET, rule.Achievement);
        }
        // The ones that need staying: being away resets the count.
        auto stay = staying.find(player->GetGUID().GetCounter());
        if (stay != staying.end())
            for (VisitRule const& rule : VisitRules)
                if (rule.Seconds && stay->second.count(rule.Credit) &&
                    (player->GetMapId() != rule.Map || player->GetExactDist2d(rule.X, rule.Y) > rule.Radius))
                    stay->second.erase(rule.Credit);
    }

    // Carrying something that does not want to be carried: the ember that dims, the elements that escape, the
    // soul-lanterns that weigh. Picked up at an object, carried to a place; dips (Refresh points) reset the timer.
    void Carries(Player* player)
    {
        Key const key = player->GetGUID().GetCounter();
        auto itr = carrying.find(key);
        if (itr == carrying.end())
            return;
        bool slowed = false;
        for (auto state = itr->second.begin(); state != itr->second.end();)
        {
            uint32 const questId = state->first;
            CarryRule const* rule = nullptr;
            for (CarryRule const& r : CarryRules)
                if (r.Quest == questId)
                    rule = &r;
            // The carry goes with the Devourer through portals and the Thin Place (the soul-lanterns start in the
            // Plaguelands and end at the cauldron); it is only delivered on the rule's own map.
            if (!rule || !Open(player, questId))
            {
                state = itr->second.erase(state);
                continue;
            }
            Carry& carry = state->second;
            if (rule->Seconds && !carry.Dark)
            {
                for (uint8 i = 0; i < rule->RefreshCount; ++i)
                    if (player->GetExactDist2d(rule->Refresh[i].X, rule->Refresh[i].Y) <= rule->RefreshRadius)
                    {
                        if (carry.Left < int32(rule->Seconds * 1000) - int32(TickEvery) * 3)
                            player->GetSession()->SendAreaTriggerMessage("{}", rule->Refreshed);
                        carry.Left = int32(rule->Seconds * 1000);
                    }
                carry.Left -= int32(TickEvery);
                if (carry.Left <= 0)
                {
                    // Gone dark (escaped, cold, blown out): it is lost; the Devourer has to pick up another.
                    carry.Dark = true;
                    player->GetSession()->SendAreaTriggerMessage("{}", rule->Lost);
                    if (rule->Flags & CarryFailLost)
                        player->FailQuest(questId);
                    state = itr->second.erase(state);
                    continue;
                }
                else if (carry.Left % 30000 < int32(TickEvery) && carry.Left < int32(rule->Seconds * 1000) / 2)
                    player->GetSession()->SendAreaTriggerMessage("{} ({} seconds)", rule->Warning, carry.Left / 1000);
            }
            if (player->GetMapId() == rule->Map && player->GetExactDist2d(rule->X, rule->Y) <= rule->Radius)
            {
                player->KilledMonsterCredit(rule->Credit);
                if (rule->Achievement && !carry.Dark)
                    player->UpdateAchievementCriteria(ACHIEVEMENT_CRITERIA_TYPE_BE_SPELL_TARGET, rule->Achievement);
                player->GetSession()->SendAreaTriggerMessage("{}", rule->Delivered);
                state = itr->second.erase(state);
                continue;
            }
            if (rule->Slow)
                slowed = true;
            ++state;
        }
        if (itr->second.empty())
            carrying.erase(itr);
        // The weight: while anything that slows is carried, the Devourer runs slower; dropped, it runs as before.
        uint8 slow = 0;
        if (slowed)
            for (CarryRule const& r : CarryRules)
                if (r.Slow > slow && carrying[key].count(r.Quest))
                    slow = r.Slow;
        uint8& applied = slowedBy[key];
        if (slow != applied)
        {
            applied = slow;
            player->UpdateSpeed(MOVE_RUN, true);
            if (slow)
                player->SetSpeed(MOVE_RUN, player->GetSpeedRate(MOVE_RUN) * (100 - slow) / 100.0f, true);
        }
    }

    bool PickUp(Player* player, GameObject* go)
    {
        for (CarryRule const& rule : CarryRules)
        {
            if (!rule.Quest || rule.Pick != go->GetEntry() || !Open(player, rule.Quest))
                continue;
            Carry& carry = carrying[player->GetGUID().GetCounter()][rule.Quest];
            carry.Left = int32(rule.Seconds * 1000);
            carry.Dark = false;
            player->HandleEmoteCommand(EMOTE_ONESHOT_LOOT);
            player->GetSession()->SendAreaTriggerMessage("{}", rule.PickedUp);
            return true;
        }
        return false;
    }

    // Followers that stay (the chick, the sapling, the pups, the ducklings): until their quest ends, they walk behind
    // the Devourer, and if they fall too far behind they catch up.
    void Followers(Player* player)
    {
        Key const key = player->GetGUID().GetCounter();
        auto itr = followers.find(key);
        if (itr == followers.end())
            return;
        for (auto f = itr->second.begin(); f != itr->second.end();)
        {
            Creature* beast = ObjectAccessor::GetCreature(*player, f->first);
            if (!beast || !beast->IsAlive())
            {
                f = itr->second.erase(f);
                continue;
            }
            if (!Open(player, f->second))
            {
                beast->DespawnOrUnsummon(Seconds(3));
                f = itr->second.erase(f);
                continue;
            }
            if (!beast->IsWithinDist(player, FollowerLeash))
            {
                beast->NearTeleportTo(player->GetPositionX(), player->GetPositionY(), player->GetPositionZ(),
                                      player->GetOrientation());
                beast->GetMotionMaster()->MoveFollow(player, 2.5f, float(M_PI) * 0.75f);
            }
            ++f;
        }
        if (itr->second.empty())
            followers.erase(itr);
    }

    void Follow(Player* player, Creature* beast, uint32 quest)
    {
        beast->SetReactState(REACT_PASSIVE);
        beast->GetMotionMaster()->MoveFollow(player, 2.5f, float(M_PI) * 0.75f);
        beast->SetRespawnTime(0);
        if (TempSummon* summon = beast->ToTempSummon())
            summon->SetTempSummonType(TEMPSUMMON_MANUAL_DESPAWN);
        followers[player->GetGUID().GetCounter()].push_back({ beast->GetGUID(), quest });
    }

    // A fish shared with the one watching: a catch from a fishing bobber while the creature the rule names is near.
    void Fish(Player* player)
    {
        std::set<uint32> given;
        for (CreditRule const& rule : CreditRules)
        {
            if (rule.Event != EventLoot || given.count(rule.Credit) || !Open(player, rule.Quest))
                continue;
            Creature* watcher = rule.Filter == FilterEntry ? player->FindNearestCreature(rule.Value, FishRange) : nullptr;
            if (!watcher && rule.Filter == FilterEntry)
                continue;
            player->KilledMonsterCredit(rule.Credit);
            given.insert(rule.Credit);
            if (watcher && rule.Line && *rule.Line)
                watcher->TextEmote(rule.Line, player);
        }
    }

    void Forget(Player* player)
    {
        auto itr = fooled.find(player->GetGUID().GetCounter());
        if (itr == fooled.end())
            return;
        for (ObjectGuid const& guid : itr->second)
            if (Creature* creature = ObjectAccessor::GetCreature(*player, guid))
                if (creature->IsAlive())
                    creature->SetReactState(REACT_AGGRESSIVE);
        fooled.erase(itr);
    }

    // Walk among them: in the right shape, in the middle of the pack, the pack takes the Devourer for one of its own.
    void Disguise(Player* player)
    {
        bool disguised = false;
        for (DisguiseRule const& rule : DisguiseRules)
        {
            if (!rule.Quest || player->GetMapId() != rule.Map || !Open(player, rule.Quest))
                continue;
            if (!Wears(player, rule.Shapes) || player->GetExactDist2d(rule.X, rule.Y) > rule.Radius * 3.0f)
                continue;
            disguised = true;
            std::vector<uint32> entries;
            for (uint32 entry : rule.Entries)
                if (entry)
                    entries.push_back(entry);
            std::list<Creature*> pack;
            player->GetCreatureListWithEntryInGrid(pack, entries, 40.0f);
            std::set<ObjectGuid>& kin = fooled[player->GetGUID().GetCounter()];
            for (Creature* member : pack)
            {
                if (!member->IsAlive())
                    continue;
                if (member->GetVictim() == player)
                {
                    member->CombatStop(true);
                    member->GetThreatMgr().ClearAllThreat();
                }
                member->SetReactState(REACT_PASSIVE);
                kin.insert(member->GetGUID());
            }
        }
        if (!disguised)
            Forget(player);
    }

    char const* Direction(float dx, float dy)
    {
        // World x runs north, world y runs west.
        static char const* const names[8] = { "north", "north-west", "west", "south-west", "south", "south-east",
            "east", "north-east" };
        float angle = std::atan2(dy, dx);
        if (angle < 0)
            angle += 2.0f * float(M_PI);
        return names[int(std::floor(angle / (float(M_PI) / 4.0f) + 0.5f)) % 8];
    }

    // Scent trails: with Sniff on, the Devourer gets told which way the scent goes; each point reached moves the trail
    // on, and the last one calls the beast that left it.
    void Trails(Player* player)
    {
        bool const sniffing = player->HasAura(SpellSniff);
        for (TrackRule const& rule : TrackRules)
        {
            if (!rule.Quest || player->GetMapId() != rule.Map || !Open(player, rule.Quest))
                continue;
            Trail& trail = trails[player->GetGUID().GetCounter()][rule.Quest];
            if (!sniffing)
                continue;
            WorldSession* session = player->GetSession();
            if (trail.Stage >= rule.Count)
            {
                // The end was reached; if the beast is gone and the quest still open, the trail ends here again.
                TrackPoint const& last = rule.Points[rule.Count - 1];
                if (rule.Summon && !StillHere(player, rule.Summon) &&
                    player->GetExactDist2d(last.X, last.Y) <= rule.Radius)
                {
                    session->SendAreaTriggerMessage("The scent is fresh again. It is coming back.");
                    Call(player, rule.Summon, last.X, last.Y, player->GetPositionZ());
                }
                continue;
            }
            TrackPoint const& point = rule.Points[trail.Stage];
            float const dx = point.X - player->GetPositionX();
            float const dy = point.Y - player->GetPositionY();
            float const dist = std::sqrt(dx * dx + dy * dy);
            if (dist <= rule.Radius)
            {
                ++trail.Stage;
                trail.Hint = 0;
                if (trail.Stage >= rule.Count)
                {
                    player->KilledMonsterCredit(rule.Credit);
                    if (rule.Summon)
                    {
                        session->SendAreaTriggerMessage("The scent ends here. Something is coming.");
                        Call(player, rule.Summon, point.X, point.Y, player->GetPositionZ());
                    }
                    else
                        session->SendAreaTriggerMessage("The scent ends here.");
                }
                else
                {
                    TrackPoint const& next = rule.Points[trail.Stage];
                    session->SendAreaTriggerMessage("The trail goes on, {}.", Direction(next.X - point.X,
                        next.Y - point.Y));
                }
                continue;
            }
            if (++trail.Hint < HintEvery)
                continue;
            trail.Hint = 0;
            char const* const how = dist < 60.0f ? "strong" : dist < 200.0f ? "clear" : "faint";
            session->SendAreaTriggerMessage("{}: the scent is {}, to the {}.", rule.Name, how, Direction(dx, dy));
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

    void OnPlayerTextEmote(Player* player, uint32 textEmote, uint32 /*emoteNum*/, ObjectGuid guid) override
    {
        if (!guid.IsCreature() || !sDevourer.IsDevourer(player))
            return;
        Creature* target = ObjectAccessor::GetCreature(*player, guid);
        if (target && target->IsAlive() && player->IsWithinDist(target, EmoteRange))
            Credit(player, target, EventEmote, textEmote);
    }

    void OnPlayerSpellCast(Player* player, Spell* spell, bool /*skipCheck*/) override
    {
        if (!spell || !sDevourer.IsDevourer(player))
            return;
        Unit* target = spell->m_targets.GetUnitTarget();
        if (Creature* creature = target ? target->ToCreature() : nullptr)
            Credit(player, creature, EventSpell, spell->GetSpellInfo()->Id);
    }

    void OnPlayerUpdate(Player* player, uint32 diff) override
    {
        if (!sDevourer.IsDevourer(player))
            return;
        uint32& timer = tickTimers[player->GetGUID().GetCounter()];
        if (timer > diff)
        {
            timer -= diff;
            return;
        }
        timer = TickEvery;
        Disguise(player);
        Visits(player);
        Trails(player);
        Carries(player);
        Followers(player);
#ifndef DEVOURER_ONE_CAMPFIRE
        Fireside(player);
#endif
    }

    void OnPlayerLootItem(Player* player, Item* /*item*/, uint32 /*count*/, ObjectGuid lootguid) override
    {
        if (!lootguid.IsGameObject() || !sDevourer.IsDevourer(player))
            return;
        GameObject* bobber = player->GetMap()->GetGameObject(lootguid);
        if (bobber && bobber->GetGoType() == GAMEOBJECT_TYPE_FISHINGNODE)
            Fish(player);
    }

    // A letter after a quest (the chick writes, Bramble sends a crash note): server mail from Wren, after a while.
    void OnPlayerCompleteQuest(Player* player, Quest const* quest) override
    {
        if (!quest || !sDevourer.IsDevourer(player))
            return;
        // Zack 2026-10-06: every quest gives the Devourer a mount or a form; the forms come here, at turn-in
        for (FormRule const& rule : FormRules)
            if (rule.Quest == quest->GetQuestId())
                sDevourer.Unlock(player, rule.Shape, rule.Display, false, false);
        for (MailRule const& rule : MailRules)
        {
            if (rule.Quest != quest->GetQuestId())
                continue;
            CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
            MailDraft(rule.Subject, rule.Body).SendMailTo(trans, MailReceiver(player, player->GetGUID().GetCounter()),
                MailSender(MAIL_CREATURE, WrenEntry), MAIL_CHECK_MASK_NONE, rule.Delay);
            CharacterDatabase.CommitTransaction(trans);
        }
    }

    // Fallback without mod-chromatica-extras: sat by a cooking fire or in an inn with Bramble for 15 s, the lantern
    // tells the pending tale itself. With the extras module the Fireside Tale does it (see devourer_quests_world).
    void Fireside(Player* player)
    {
        Key const key = player->GetGUID().GetCounter();
        UseRule const* rule = PendingTale(player);
        if (!rule || telling.count(key))
        {
            fireside.erase(key);
            return;
        }
        bool const byFire = player->IsSitState() && Companion(player) &&
            (player->HasRestFlag(REST_FLAG_IN_TAVERN) || player->FindNearestGameObjectOfType(GAMEOBJECT_TYPE_SPELL_FOCUS, 10.0f));
        if (!byFire)
        {
            fireside.erase(key);
            return;
        }
        uint32& sat = fireside[key];
        sat += TickEvery;
        if (sat < 15000)
            return;
        fireside.erase(key);
        TellTale(player, *rule);
    }

    void OnPlayerQuestAbandon(Player* player, uint32 questId) override
    {
        Key const key = player->GetGUID().GetCounter();
        auto itr = trails.find(key);
        if (itr != trails.end())
            itr->second.erase(questId);
        auto c = carrying.find(key);
        if (c != carrying.end())
            c->second.erase(questId);
    }

    void OnPlayerLogout(Player* player) override
    {
        Key const key = player->GetGUID().GetCounter();
        tickTimers.erase(key);
        counted.erase(key);
        trails.erase(key);
        called.erase(key);
        staying.erase(key);
        carrying.erase(key);
        followers.erase(key);
        slowedBy.erase(key);
        Forget(player);
    }
};

// The quests' own creatures that talk: a riddle, a bargain, a machine's stubborn logic. The right answer counts for
// the quest; a wrong one may cost something (WrongSpell on the Devourer).
class npc_devourer_quest_beast : public CreatureScript
{
public:
    npc_devourer_quest_beast() : CreatureScript("npc_devourer_quest_beast") { }

    // (quest, creature spawn) pairs already answered right; forgotten for a quest whose count is back at 0 (taken
    // again after abandoning it)
    static inline std::unordered_map<ObjectGuid, std::set<std::pair<uint32, ObjectGuid::LowType>>> told;

    static GossipRule const* Rule(Player* player, Creature* creature)
    {
        for (GossipRule const& rule : GossipRules)
            if (rule.Entry == creature->GetEntry() && (!rule.Quest || Open(player, rule.Quest)))
                return &rule;
        return nullptr;
    }

    bool OnGossipHello(Player* player, Creature* creature) override
    {
        GossipRule const* rule = Rule(player, creature);
        if (!rule)
            return false;
        ClearGossipMenuFor(player);
        if (rule->Text && *rule->Text)
            creature->Say(rule->Text, LANG_UNIVERSAL, player);
        for (uint8 i = 0; i < rule->OptionCount; ++i)
            AddGossipItemFor(player, GOSSIP_ICON_CHAT, rule->Options[i].Label, GOSSIP_SENDER_MAIN, GOSSIP_ACTION_INFO_DEF + i);
        SendGossipMenuFor(player, DEFAULT_GOSSIP_MESSAGE, creature->GetGUID());
        return true;
    }

    bool OnGossipSelect(Player* player, Creature* creature, uint32 /*sender*/, uint32 action) override
    {
        GossipRule const* rule = Rule(player, creature);
        CloseGossipMenuFor(player);
        if (!rule)
            return true;
        uint32 const i = action - GOSSIP_ACTION_INFO_DEF;
        if (i >= rule->OptionCount)
            return true;
        GossipOption const& option = rule->Options[i];
        if (option.Reply && *option.Reply)
            creature->Say(option.Reply, LANG_UNIVERSAL, player);
        if (option.Right)
        {
            // each creature counts once per Devourer and quest (ten machines means ten machines, not one ten times)
            auto& answered = told[player->GetGUID()];
            if (rule->Credit && Open(player, rule->Quest) && !player->GetReqKillOrCastCurrentCount(rule->Quest, rule->Credit))
                for (auto it = answered.begin(); it != answered.end();)
                    it = it->first == rule->Quest ? answered.erase(it) : std::next(it);
            if (rule->Credit && Open(player, rule->Quest)
                && answered.insert({ rule->Quest, creature->GetSpawnId() }).second)
                player->KilledMonsterCredit(rule->Credit);
        }
        else if (rule->WrongSpell)
            creature->CastSpell(player, rule->WrongSpell, true);
        return true;
    }
};

// The things the witches leave in the world. A token: touching it counts for its quest, then it fades for a minute.
// A lure: it calls the creature (or the swarm) its quest wants, for this Devourer only, so a beast that comes back only
// every few hours, or that somebody else took, can still be hunted. The gameobject template carries the quest, so it
// only answers while that quest is in the log.
class go_devourer_quest_object : public GameObjectScript
{
public:
    go_devourer_quest_object() : GameObjectScript("go_devourer_quest_object") { }

    // A campfire tale (a quest's Lines, told by Speaker): for the Devourer and its companion; the end counts.
    static void Tell(Player* player, GameObject* go, UseRule const& rule);

    bool OnGossipHello(Player* player, GameObject* go) override
    {
        if (PickUp(player, go))
            return true;
        for (UseRule const& rule : UseRules)
        {
            if (!rule.Object || rule.Object != go->GetEntry() || !Open(player, rule.Quest))
                continue;
            if (!Wears(player, rule.Shapes))
            {
                ChatHandler(player->GetSession()).SendNotification("Not in this shape.");
                return true;
            }
            if (!Conditions(player, rule.Flags, FlagNight, 0, 0, FlagNoFlying, FlagSniff, FlagNoSniff))
            {
                ChatHandler(player->GetSession()).SendNotification("Not now, not like this.");
                return true;
            }
            if (rule.LineCount)
            {
                Tell(player, go, rule);
                return true;
            }
            if (rule.Summon)
            {
                if (StillHere(player, rule.Summon))
                {
                    ChatHandler(player->GetSession()).SendNotification("It is already on its way.");
                    return true;
                }
                player->HandleEmoteCommand(EMOTE_ONESHOT_KNEEL);
                for (uint32 i = 0; i < std::max<uint32>(1, rule.Count); ++i)
                {
                    Position at = go->GetPosition();
                    float const angle = rule.Count > 1 ? 2.0f * float(M_PI) * i / rule.Count :
                        float(rand_norm()) * 2.0f * float(M_PI);
                    go->MovePositionToFirstCollision(at, rule.Count > 1 ? 10.0f : 6.0f, angle);
                    if (Creature* beast = Call(player, rule.Summon, at.GetPositionX(), at.GetPositionY(), at.GetPositionZ()))
                        if (rule.Flags & FlagFollow)
                            Follow(player, beast, rule.Quest);
                }
                if (rule.Credit)
                    player->KilledMonsterCredit(rule.Credit);   // waking it counts (the eggs, the hatch)
            }
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
};

namespace
{
    void SendTaleLine(Player* to, char const* speaker, char const* text)
    {
        WorldPacket data;
        ChatHandler::BuildChatPacket(data, CHAT_MSG_MONSTER_WHISPER, LANG_UNIVERSAL, ObjectGuid::Empty, to->GetGUID(),
            text, 0, speaker);
        to->SendDirectMessage(&data);
    }
}

namespace
{
    void TellTale(Player* player, UseRule const& rule) { go_devourer_quest_object::Tell(player, nullptr, rule); }

    // The end of a tale: the quest counts, and Bramble says her piece.
    void TaleTold(Player* listener, UseRule const& rule)
    {
        Player* friendNear = Companion(listener);
        if ((rule.Flags & FlagCompanion) && !friendNear)
        {
            ChatHandler(listener->GetSession()).SendNotification("Your companion was not there for the end of it.");
            return;
        }
        if (Open(listener, rule.Quest))
            listener->KilledMonsterCredit(rule.Credit);
        if (friendNear && rule.Reaction && *rule.Reaction)
            friendNear->Say(rule.Reaction, LANG_UNIVERSAL);
    }
}

// Without mod-chromatica-extras: the lantern's own teller, line by line, when the Devourer sits by a fire with Bramble.
void go_devourer_quest_object::Tell(Player* player, GameObject* /*go*/, UseRule const& rule)
{
    Key const key = player->GetGUID().GetCounter();
    if (telling.count(key))
        return;
    Player* companion = Companion(player);
    if ((rule.Flags & FlagCompanion) && !companion)
    {
        ChatHandler(player->GetSession()).SendNotification("The tale is not for you alone. Bring your companion.");
        return;
    }
    telling.insert(key);
    ObjectGuid const guid = player->GetGUID();
    ObjectGuid const companionGuid = companion ? companion->GetGUID() : ObjectGuid::Empty;
    for (uint8 i = 0; i <= rule.LineCount; ++i)
    {
        player->m_Events.AddEventAtOffset([guid, companionGuid, rule, i]()
        {
            Player* listener = ObjectAccessor::FindPlayer(guid);
            if (!listener)
                return;
            Player* friendNear = companionGuid ? ObjectAccessor::FindPlayer(companionGuid) : nullptr;
            if (i < rule.LineCount)
            {
                SendTaleLine(listener, rule.Speaker, rule.Lines[i]);
                if (friendNear)
                    SendTaleLine(friendNear, rule.Speaker, rule.Lines[i]);
                return;
            }
            telling.erase(listener->GetGUID().GetCounter());
            TaleTold(listener, rule);
        }, Milliseconds(TaleLineEvery * (i + 1)));
    }
}

class devourer_quests_spells : public AllSpellScript
{
public:
    devourer_quests_spells() : AllSpellScript("devourer_quests_spells") { }

    // A creature's ability aimed at a Devourer: "let it show you its trick".
    void OnSpellCast(Spell* spell, Unit* caster, SpellInfo const* /*spellInfo*/, bool /*skipCheck*/) override
    {
        Creature* creature = caster ? caster->ToCreature() : nullptr;
        if (!creature || !spell)
            return;
        Unit* target = spell->m_targets.GetUnitTarget();
        if (Player* player = target ? target->ToPlayer() : nullptr)
            Credit(player, creature, EventStruck);
    }
};

class devourer_quests_world : public WorldScript
{
public:
    devourer_quests_world() : WorldScript("devourer_quests_world") { }

    void OnAfterConfigLoad(bool /*reload*/) override
    {
        companionName = sConfigMgr->GetOption<std::string>("Devourer.WitchCompanion", "Bramble");
    }

#ifdef DEVOURER_ONE_CAMPFIRE
    // One campfire for everyone: a pending lantern tale is what the companions tell at the fireside, and the quest
    // completes when the Fireside Tale buff lands.
    void OnStartup() override
    {
        Extras::SetCampfireTaleProvider([](Player* player, Extras::CampfireTale& tale) -> bool
        {
            if (!sDevourer.IsDevourer(player))
                return false;
            UseRule const* rule = PendingTale(player);
            if (!rule)
                return false;
            std::string prompt = std::string(rule->Speaker) + " told this tale to the Devourer, and asked that it be "
                "told again at the fire, in your own words, to the Devourer and to everyone sitting here: ";
            for (uint8 i = 0; i < rule->LineCount; ++i)
            {
                if (i)
                    prompt += ' ';
                prompt += rule->Lines[i];
            }
            tale.Prompt = prompt;
            tale.Fallback = std::string("The companions tell ") + rule->Speaker + "'s tale: " + rule->Lines[0];
            uint32 const quest = rule->Quest;
            tale.OnTold = [quest](Player* listener)
            {
                for (UseRule const& r : UseRules)
                    if (r.Quest == quest && r.LineCount)
                        TaleTold(listener, r);
            };
            return true;
        });
    }
#endif
};

void AddSC_devourer_quests()
{
    new devourer_quests_player();
    new go_devourer_quest_object();
    new npc_devourer_quest_beast();
    new devourer_quests_spells();
    new devourer_quests_world();
}
