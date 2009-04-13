import es

from sourcerpg import sourcerpg

skillName = "Vampire"

""" Execute the configuration information """
config = sourcerpg.skillConfig

""" Set the info of this skill """
config.addInfo(skillName, """This skill enables users to gain experience
by damagin others. The higher the level, the higher the percentage of damage
done is added to their health.""")

""" Assign all the server variables """
maxLevel        = config.cvar("srpg_vampireMax",              10, "The maximum level of the skill")
creditStart     = config.cvar("srpg_vampireCreditsStart",     15, "The starting amount of credits for this skill")
creditIncrement = config.cvar("srpg_vampireCreditsIncrement", 10, "How much the credits increment after the first level")
percentage      = config.cvar("srpg_vampirePercentage",      7.5, "Each level increments the percentage of damage drained by this much")

def load():
    """ 
    This method executes when the script loads. Register the skill
    """
    sourcerpg.skills.addSkill( skillName, maxLevel, creditStart, creditIncrement )
    
def unload():
    """
    This method executes when the script unloads. Unregister the skill
    """
    sourcerpg.skills.removeSkill( skillName )
    
def player_hurt(event_var):
    """
    Executed when a player is damaged. Get the amount of damage done and
    multiply it by the percentage
    
    @PARAM event_var - an automatically passed event instance
    """
    attacker = event_var['attacker']
    player   = sourcerpg.players[attacker]
    level    = player[skillName]
    if level:
        level = level * float(percentage) / 100.0
        if event_var['dmg_health']:
            amountToHeal = int(level * int(event_var['dmg_health']) )
        elif event_var['damage']:
            amountToHeal = int(level * int(event_var['damage']) )
        else:
            raise ValueError, "This game does not support vampire"
        if amountToHeal:
            maxHealth = player['maxHealth']
            currentHealth = es.getplayerprop(event_var['attacker'], 'CBasePlayer.m_iHealth')
            currentHealth += amountToHeal
            if currentHealth > maxHealth:
                currentHealth = maxHealth
            es.setplayerprop(event_var['attacker'], 'CBasePlayer.m_iHealth', currentHealth)