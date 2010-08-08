import es
import gamethread
import playerlib
import weaponlib
import random

from sourcerpg import sourcerpg

skillName = "Adrenaline"

""" Execute the configuration information """
config = sourcerpg.skillConfig

""" Set the info of this skill """
config.addInfo(skillName, """This skill gives a player a temporary boost when they are damaged
for a certain length of time.""")

""" Assign all the server variables """
maxLevel        = config.cvar("srpg_adrenalineMax",               10, "The maximum level of the regen skill")
creditStart     = config.cvar("srpg_adrenalineCreditsStart",       5, "The starting amount of credits for this skill")
creditIncrement = config.cvar("srpg_adrenalineCreditsIncrement",  10, "How much the credits increment after the first level")
length          = config.cvar("srpg_adrenalineLength",           2.0, "The time (in seconds) that the effect lasts for")
refreshAmmo     = config.cvar("srpg_adrenalineRefreshClip",        0, "Enable clip refresh when damaged, 1=enable, 0=disabled")
clipRefreshPct  = config.cvar("srpg_adrenalineRefreshClipPercent", 5, "The percentage of the person's clip refreshing when hit multiplied by their adrenaline level")

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
    Executed when a player is damaged. Retrieve the victims level and speed
    them up if they aren't already in the adrenaline mode
    
    @PARAM event_var - an automatically passed event instance
    """
    userid = event_var['userid']
    player = sourcerpg.players[userid]
    level  = player[skillName]
    if level:
        """ Player is at least level 1 in this skill """
        if not player['adrenalined'] and not player['slowed']:
            """ Player is not already in the adrenaline mode """
            attacker = event_var['attacker']
            if attacker and attacker.isdigit() and int(attacker) > 1:
                """ If the attacker is a valid attacker """
                if event_var['es_attackerteam'] != event_var['es_userteam']:
                    """ If the attacker is not on the user's team """
                    if "Frost Pistol" in sourcerpg.skills:
                        """ If frost pistol is loaded check if the attack was a frost pistol attack """
                        if sourcerpg.players[attacker]['Frost Pistol']:
                            """ If the attacker has a frost pistol level """
                            weapon = event_var['weapon']
                            weapon = weaponlib.getWeapon(weapon)
                            if weapon is None:
                                return
                            weapon = weapon.name # format the weapon name
                            if weapon in weaponlib.getWeaponNameList("#secondary"):
                                """ The attack was a frost pistol attack, return early """
                                return
                            
                    player['adrenalined'] = True
                    amount = level / 10.
                    speed  = player['maxSpeed'] + amount

                    """ Set the speed and the delay """
                    playerlibInstance = playerlib.getPlayer(userid)
                    playerlibInstance.speed = speed
                    
                    if int(refreshAmmo):
                        currentWeapon = weaponlib.getWeapon(playerlibInstance.weapon)
                        if currentWeapon is not None:
                            if random.randint(1, 100) <= float(clipRefreshPct) * level:
                                playerlibInstance.clip[currentWeapon.name] = currentWeapon.clip
                    
                    gamethread.delayedname( float(length), 'sourcerpg_adrenaline_user%s' % userid, reset, (userid, speed - amount) )
            
def player_death(event_var):
    """
    An event which occurs when a player dies. Ensure that their adrenaline
    delay is canceled
    
    @PARAM event_var - an automatically passed event instance
    """
    userid = event_var['userid']
    gamethread.cancelDelayed('sourcerpg_adrenaline_user%s' % userid)
    sourcerpg.players[userid]['adrenalined'] = False
    
def player_spawn(event_var):
    """
    An event which occurs when a player spawns, ensure that their adrenalied
    key is set to False
    
    @PARAM event_var - an automatically passed event instance
    """
    userid = event_var['userid']
    if not es.getplayerprop(userid, 'CBasePlayer.pl.deadflag'):
        player = sourcerpg.players[userid]
        if player is not None:
            sourcerpg.players[userid]['adrenalined'] = False
    
def player_disconnect(event_var):
    """
    An event which occurs when a player disconnects from the game. Cancel the
    delay.
    
    @PARAM event_var - an automatically passed event instance
    """
    userid = event_var['userid']
    gamethread.cancelDelayed('sourcerpg_adrenaline_user%s' % userid)
            
def reset(userid, speed):
    """
    This method resets a player's attributes back to the default values.
    
    @PARAM userid - the player who you wish to modify
    @PARAM speed - the new speed value of the player
    """
    gamethread.cancelDelayed('sourcerpg_adrenaline_user%s' % userid)
    if es.exists('userid', userid):
        player = sourcerpg.players[userid]
        player['adrenalined'] = False
        player['maxSpeed']    = speed
        playerlib.getPlayer(userid).speed = speed