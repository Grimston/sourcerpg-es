import es
import gamethread

from sourcerpg import sourcerpg

skillName = "Napalm Grenade"

""" Execute the configuration information """
config = sourcerpg.skillConfig

""" Set the info of this skill """
config.addInfo(skillName, """This skill allows a player to set others on fire when they
damage them with a HE grenade. The length of time is 1 second per level.""")

""" Assign all the server variables """
maxLevel        = config.cvar("srpg_napalmMax",              10, "The maximum level of this skill")
creditStart     = config.cvar("srpg_napalmCreditsStart",     10, "The starting amount of credits for this skill")
creditIncrement = config.cvar("srpg_napalmCreditsIncrement", 10, "How much the credits increment after the first level")

def load():
    """ 
    This method executes when the script loads. Register the skill
    """
    sourcerpg.skills.addSkill( skillName, maxLevel, creditStart, creditIncrement )
    es.doblock("corelib/noisy_on")
    
def unload():
    """
    This method executes when the script unloads. Unregister the skill
    """
    sourcerpg.skills.removeSkill( skillName )
    es.doblock("corelib/noisy_off")
    
def player_hurt(event_var):
    """
    When a player is damaged, check for team attacks, then if the wepapon is
    a hegrenade, then set the player on fire, and delay and extinguish
    
    @PARAM event_var - an automatically passed event instance
    """
    userid   = event_var['userid']
    attacker = event_var['attacker']
    if attacker.isdigit() and int(attacker) > 0:
        """ The attacker did not hurt themselves """
        player = sourcerpg.players[attacker]
        if player is not None:
            level  = player[skillName]
            if level:
                """ The player has at least level 1 in napalm nade """
                if event_var['es_userteam'] <> event_var['es_attackerteam']:
                    """ It was not a team kill """
                    if event_var['weapon'] == "hegrenade":
                        """ Was a kill with a grenade """
                        es.fire(userid, "!self", "IgniteLifetime", 1.0 * level)
                
def weapon_fire(event_var):
    """
    If the weapon is a grenade, set it on fire.

    @PARAM event_var - an automatically passed event instance
    """
    if event_var['weapon'] == "hegrenade":
        userid = event_var['userid']
        player = sourcerpg.players[userid]
        if player is not None:
            if player[skillName]:
                gamethread.delayed(0.1, es.fire, (userid, 'hegrenade_projectile', 'ignite')) # delay a tick so the entity is created