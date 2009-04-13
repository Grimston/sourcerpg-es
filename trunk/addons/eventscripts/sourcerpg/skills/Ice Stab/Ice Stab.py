import es
import gamethread
import playerlib
import random
import weaponlib

from sourcerpg import sourcerpg

skillName = "Ice Stab"

""" Execute the configuration information """
config = sourcerpg.skillConfig

""" Set the info of this skill """
config.addInfo(skillName, """This skill allows a player to freeze another player by
stabbing them with a knife""")

""" Assign all the server variables """
maxLevel        = config.cvar("srpg_iceStabMax",                 5, "The maximum level of this skill")
creditStart     = config.cvar("srpg_iceStabCreditsStart",       20, "The starting amount of credits for this skill")
creditIncrement = config.cvar("srpg_iceStabCreditsIncrement",   25, "How much the credits increment after the first level")
iceTime         = config.cvar("srpg_iceStabFreezeTime",          1, "The amount of time to freeze a player multiplied by the attacker's level")
damageReduction = config.cvar("srpg_damageReductionPercentage", 50, "The percentage that the amount of damage is reduced by when the victim is frozen")

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
        level  = player[skillName]
        if level:
            """ The player has at least level 1 in this skill """
            if event_var['es_userteam'] <> event_var['es_attackerteam']:
                """ It was not a team kill """
                damage = 0
                if event_var['damage'].isdigit():
                    damage = int(event_var['damage'])
                elif event_var['dmg_health'].isdigit():
                    damage = int(event_var['dmg_health'])
                if event_var['weapon'] in weaponlib.getWeaponNameList("#melee"):
                    if damage > 30:
                        """ The attack was a hard hit from one of the weapons """
                        gamethread.cancelDelayed('sourcerpg_freeze_user%s' % userid)
                        es.emitsound('player', userid, 'physics/glass/glass_impact_bullet%s.wav' % random.randint(1,4), '1.0', '0.5')
                        player = playerlib.getPlayer(userid)
                        player.freeze(True)
                        red, green, blue, alpha = player.getColor()
                        player.setColor(0, 0, 255, alpha)
                        gamethread.delayedname('sourcerpg_freeze_user%s' % userid, float(iceTime) * level, unFreeze, userid)
                elif bool(int(damageReduction)):
                    """ Damage reduction """
                    if not es.getplayerprop(userid, 'CBasePlayer.pl.deadflag'):
                        player = playerlib.getPlayer(userid)
                        player.health += int(damage / 100. * damageReduction)
                
def unFreeze(userid):
    """
    This function unfreezes a player and resets their color and status back to
    normal.
    
    @PARAM userid - the player who to unfreeze
    """
    player = playerlib.getPlayer(userid)
    player.freeze(False)
    red, green, blue, alpha = player.getColor()
    player.setColor(255, 255, 255, alpha)
                
def player_death(event_var):
    """
    Executed when a player dies - ensure that they are extinguished so we don't
    create an error
    
    @PARAM event_var - an automatically passed event instance
    """
    gamethread.cancelDelayed('sourcerpg_freeze_user%s' % event_var['userid'])
    
def player_disconnect(event_var):
    """
    A wrapper which executes the player_death function which just cancels the
    delay for the player
    """
    player_death(event_var)