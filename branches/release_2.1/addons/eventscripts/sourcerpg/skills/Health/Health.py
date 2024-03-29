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

baseHealth = {}

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
                gamethread.delayed(0, getBaseHealth, userid)
                gamethread.delayed(0, gamethread.delayed, (0, setHealth, userid))
        
def player_disconnect(event_var):
    """
    Executed when a player disconnects from the server. If they have an instance
    in the global dictionary, remove them from it
    
    @PARAM event_var - an automatically passed event instace
    """ 
    userid = event_var['userid']
    if userid in baseHealth:
        del baseHealth[userid]

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
        
def getBaseHealth(userid):
    """
    A function to store the base health so we can refer back to this without
    it growing exponentially

    @PARAM userid - the user who to get the base health for
    """
    baseHealth[userid] = sourcerpg.players[userid]['baseHealth']

def setHealth(userid):
    """
    A function which alters the maximum and current health of a player to
    match their current level
    
    @PARAM userid - the userid of which to set the health of
    """
    player = sourcerpg.players[userid]
    level  = player[skillName]
    if userid not in baseHealth:
        baseHealth[userid] = player['baseHealth']
    level  = level * int(healthIncrement) + baseHealth[userid]
    player['maxHealth'] = level
    es.setplayerprop(userid, 'CBasePlayer.m_iHealth', player['maxHealth'])