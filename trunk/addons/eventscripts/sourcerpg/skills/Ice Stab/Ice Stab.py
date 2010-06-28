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
maxLevel        = config.cvar("srpg_iceStabMax",                 3, "The maximum level of this skill")
creditStart     = config.cvar("srpg_iceStabCreditsStart",       20, "The starting amount of credits for this skill")
creditIncrement = config.cvar("srpg_iceStabCreditsIncrement",   30, "How much the credits increment after the first level")
iceTime         = config.cvar("srpg_iceStabFreezeTime",          1, "The amount of time to freeze a player multiplied by the attacker's level")
damageReduction = config.cvar("srpg_damageReductionPercentage", 50, "The percentage that the amount of damage is reduced by when the victim is frozen")

""" A list to hold userid's of who's currentyl frozen """
frozen = []

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
    if attacker and int(attacker) and attacker not in frozen:
        """ The attacker did not hurt themselves """
        player = sourcerpg.players[attacker]
        level  = player[skillName]
        if level:
            """ The player has at least level 1 in this skill """
            if event_var['es_userteam'] != event_var['es_attackerteam']:
                """ It was not a team kill """
                damage = 0
                if event_var['damage'].isdigit():
                    damage = int(event_var['damage'])
                elif event_var['dmg_health'].isdigit():
                    damage = int(event_var['dmg_health'])
                if event_var['weapon'] in map(lambda x: x.split('_')[-1], weaponlib.getWeaponNameList("#melee") ):
                    if damage > 30:
                        """ The attack was a hard hit from one of the weapons """
                        if userid not in frozen:
                            frozen.append(userid)
                        gamethread.cancelDelayed('sourcerpg_freeze_user%s' % userid)
                        es.emitsound('player', userid, 'physics/glass/glass_impact_bullet%s.wav' % random.randint(1,4), '1.0', '0.5')
                        player = playerlib.getPlayer(userid)
                        player.freeze(True)
                        player.setColor(0, 0, 255)
                        gamethread.delayedname(float(iceTime) * level, 'sourcerpg_freeze_user%s' % userid, unFreeze, userid)
                elif bool(int(damageReduction)) and userid in frozen:
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
    if userid in frozen:
        frozen.remove(userid)
    player = playerlib.getPlayer(userid)
    player.freeze(False)
    player.setColor(255, 255, 255)
                
def player_death(event_var):
    """
    Executed when a player dies - ensure that they are extinguished so we don't
    create an error
    
    @PARAM event_var - an automatically passed event instance
    """
    gamethread.cancelDelayed('sourcerpg_freeze_user%s' % event_var['userid'])
    
def player_spawn(event_var):
    """
    Executed when a player spawns. If they previously died whilst frozen, they
    will still be blue, so set their colour back to normal
    
    @PARAM event_var - an automatically passed event instance
    """
    userid = event_var['userid']

    """ If the userid is in the frozen list then remove them. """
    if userid in frozen:
        frozen.remove(userid)

    if not es.getplayerprop(userid, 'CBasePlayer.pl.deadflag'):
        player = playerlib.getPlayer(userid)
        player.setColor(255, 255, 255) # Alpha automatically set to the current value

def round_start(event_var):
    """
    Executed when a new round starts. Delete all the frozen players from the list
    as they will no longer be frozen
    
    @PARAM evetn_var - an automatically passed event instance
    """
    del frozen[:]

def player_disconnect(event_var):
    """
    A wrapper which executes the player_death function which just cancels the
    delay for the player
    """
    player_death(event_var)