/*
 * mod-devourer: the Devourer's quests in the world (task 021, src/DevourerQuests.cpp).
 * Released under GNU AGPL v3, like AzerothCore.
 */

#ifndef DEVOURER_QUESTS_H
#define DEVOURER_QUESTS_H

class Creature;
class Player;

namespace Devourer::Quests
{
    // A meal counts for the "devour" objectives of the quests in the Devourer's log (called by Mgr::EatShape).
    void OnMeal(Player* player, Creature* meal);
}

#endif
