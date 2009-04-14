import es
import gamethread

from sourcerpg import sourcerpg

skillName = "Health"

""" Execute the configuration information """
config = sourcerpg.skillConfig

""" Set the info of this skill """
config.addInfo(skillName, """This skill allows a player to increase their maximum
health, and the amount of health they start with.""")

""" Assign all the server variables """
maxLevel        = config.cvar("srpg_healthMax",              16, "The maximum level of the health skill")
creditStart     = config.cvar("srpg_healthCreditsStart",     15, "The starting amount of credits for this skill")
creditIncrement = config.cvar("srpg_healthCreditsIncrement", 10, "How much the credits increment after the first level")
healthIncrement = config.cvar("srpg_healthIncrements",       25, "How much additional health each level acquires")

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

def player_spawn(event_var):
    """
    An event which occurs when a player spawns. Set the default health value.
    
    @PARAM event_var - an automatically passed event instance 
    """
    userid = event_var['userid']
    if not es.getplayerprop(userid, 'CBasePlayer.pl.deadflag'):
        """ Only execute if the player is alive """
        player = sourcerpg.players[userid]
        if player is not None:
            if player[skillName]:
                """
                Delay the function so it's not overwritten by resetting the
                defaults in sourcerpg
                """
                gamethread.delayed(0, setHealth, userid)
        
def sourcerpg_skillupgrade(event_var):
    """
    An event which executes when a player upgrades a skill. If the skill is
    Health, then ensure that their health is altered acoordingly
    
    @PARAM event_var - an automatically passed event instance
    """
    if event_var['skill'] == skillName:
        setHealth(event_var['userid'])
        
def sourcerpg_skilldowngrade(event_var):
    """
    An event which executes when a player sells a skill. If the skill is
    Health, then ensure that their health is altered acoordingly
    
    @PARAM event_var - an automatically passed event instance
    """
    if event_var['skill'] == skillName:
        setHealth(event_var['userid']) 
        
def setHealth(userid):
    """
    A function which alters the maximum and current health of a player to
    match their current level
    
    @PARAM userid - the userid of which to set the health of
    """
    player = sourcerpg.players[userid]
    level  = player[skillName]
    level  = level * int(healthIncrement) + player['maxHealth']
    player['maxHealth'] = level
    es.setplayerprop(userid, 'CBasePlayer.m_iHealth', player['maxHealth'])