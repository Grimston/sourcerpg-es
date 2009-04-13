import es
import playerlib
import weaponlib
import gamethread

from sourcerpg import sourcerpg

skillName = "Frost Pistol"

""" Execute the configuration information """
config = sourcerpg.skillConfig

""" Set the info of this skill """
config.addInfo(skillName, """This skill allows a player to slow down their victim by
damaging them with a secondary weapon.""")

""" Assign all the server variables """
maxLevel        = config.cvar("srpg_frostPistolMax",                5, "The maximum level of this skill")
creditStart     = config.cvar("srpg_frostPistolCreditsStart",      20, "The starting amount of credits for this skill")
creditIncrement = config.cvar("srpg_frostPistolCreditsIncrement",  25, "How much the credits increment after the first level")
freezeTime      = config.cvar("srpg_frostPistolFreezeTime",       0.1, "The amount of time to freeze a player by multiplied by the attackers level")

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
    When a player is damaged, check for team attacks, then if the weapon is
    a secondary weapon then freeze the player
    
    @PARAM event_var - an automatically passed event instance
    """
    userid   = event_var['userid']
    attacker = event_var['attacker']
    if int(attacker):
        """ The attacker did not hurt themselves """
        player = sourcerpg.players[attacker]
        level  = player[skillName]
        if level:
            """ The player has at least level 1 in this skill """
            if event_var['es_userteam'] <> event_var['es_attackerteam']:
                """ It was not a team kill """
                if event_var['weapon'] in weaponlib.getWeaponNameList('#secondary'):
                    if not player['slowed']:
                        """ Ensure that they're only slowed once """
                        player['slowed'] = True
                        speed  = player['maxSpeed']
                        speed /= 2.0
                        player['maxSpeed'] = speed
                        player = playerlib.getPlayer(userid)
                        player.speed = speed
                        red, green, blue, alpha = player.getColor()
                        player.setColor(0, 0, 255, alpha)
                        gamethread.delayedname('sourcerpg_slow_user%s' % userid, float(freezeTime) * level, speedUp, userid)
                    
def speedUp(userid):
    """
    A function to assign a player's speed and color back to normal after being
    slowed down by a frost pistol.
    
    @PARAM userid - the player who to speed up again.
    """
    player = sourcerpg.players[userid]
    player['slowed'] = False
    speed  = player['maxSpeed']
    speed *= 2.
    player['maxSpeed'] = speed
    playerlibPlayer = playerlib.getPlayer(userid)
    playerlibPlayer.speed = speed
    
    """ Assign their color back to normal """
    red, green, blue, alpha = player.getColor()
    playerlibPlayer.setColor(255, 255, blue, alpha)
                
def player_spawn(event_var):
    """
    Occurs when a player spawns. Assing a key to their dictionary value so we
    can hold if they're currently slowed or not 
    """
    userid = event_var['userid']
    if not es.getplayerprop(userid, 'CBasePlayer.pl.deadflag'):
        sourcerpg.players[userid]['slowed'] = False
                
def player_death(event_var):
    """
    Executed when a player dies - ensure that they are unfrozen so we don't
    create an error
    
    @PARAM event_var - an automatically passed event instance
    """
    gamethread.cancelDelayed('sourcerpg_slow_user%s' % event_var['userid'])
    
def player_disconnect(event_var):
    """
    A wrapper which executes the player_death function which just cancels the
    delay for the player
    """
    player_death(event_var)