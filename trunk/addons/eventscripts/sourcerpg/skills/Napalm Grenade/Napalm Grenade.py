import es
import gamethread
import playerlib

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
    
def unload():
    """
    This method executes when the script unloads. Unregister the skill
    """
    sourcerpg.skills.removeSkill( skillName )
    
def player_hurt(event_var):
    """
    When a player is damaged, check for team attacks, then if the wepapon is
    a hegrenade, then set the player on fire, and delay and extinguish
    
    @PARAM event_var - an automatically passed event instance
    """
    userid   = event_var['userid']
    attacker = event_var['attacker']
    if int(attacker):
        """ The attacker did not hurt themselves """
        player = sourcerpg.players[attacker]
        if player is not None:
            level  = player[skillName]
            if level:
                """ The player has at least level 1 in napalm nade """
                if event_var['es_userteam'] <> event_var['es_attackerteam']:
                    """ It was not a team kill """
                    player = playerlib.getPlayer(userid)
                    player.burn()
                    gamethread.delayedname('sourcerpg_burn_user%s' % userid, 1.0 * level, player.extinguish)
                
def player_death(event_var):
    """
    Executed when a player dies - ensure that they are extinguished so we don't
    create an error
    
    @PARAM event_var - an automatically passed event instance
    """
    gamethread.cancelDelayed('sourcerpg_burn_user%s' % event_var['userid'])
    
def player_disconnect(event_var):
    """
    A wrapper which executes the player_death function which just cancels the
    delay for the player
    """
    player_death(event_var)