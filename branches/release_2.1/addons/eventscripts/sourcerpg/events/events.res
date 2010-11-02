"events"
{
    "sourcerpg_databasesaved"
    {
        // Executed when the database has been saved
        "type"      "string" // the type that the database saved, either "interval" or "round end"
    }
    
    "sourcerpg_levelup"
    {
        // Executed when a user levels up
        "userid"    "short" // the userid of the player who leveled up
        "amount"    "long"  // the amount of levels that the user leveled up by
        "newlevel"  "long"  // the new level of the player
        "oldlevel"  "long"  // the old level of the player
        "xp"        "long"  // the amount of experience the user has
        "xpneeded"  "long"  // the amount of experience needed for the user to level up again
    }
    
    "sourcerpg_gainxp"
    {
        // Executed when a user gains experience
        "userid"    "short"  // the userid of the player who gained xp
        "amount"    "long"   // the amount of xp gained
        "levels"    "long"   // the amount of levels gained (if any)
        "newxp"     "long"   // the new xp of the player
        "oldxp"     "long"   // the old xp of the player
        "xpneeded"  "long"   // the xp needed to level up
        "reason"    "string" // the reason the xp was given
    }
    
    "sourcerpg_skillupgrade"
    {
        // Executed when a user levels up a skill
        "userid"    "short"  // the userid of the player who leveled up the skill
        "level"     "short"  // the new level of the skill that was leveled up
        "cost"      "short"  // the amount of credits it cost to buy the skill
        "skill"     "string" // the name of the skill that was leveled up
    }
    
    "sourcerpg_skilldowngrade"
    {
        // Executed when a user sells a skill
        "userid"    "short"  // the userid of the player who sold the skill
        "level"     "short"  // the new level of the skill that was sold
        "gained"    "short"  // the amount of credits gained by selling the skill
        "skill"     "string" // the name of the skill that was sold
    }
    
}