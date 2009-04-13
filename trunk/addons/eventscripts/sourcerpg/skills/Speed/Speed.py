import es
import gamethread

from sourcerpg import sourcerpg

skillName = "Speed"

""" Execute the configuration information """
config = sourcerpg.skillConfig

""" Set the info of this skill """
config.addInfo(skillName, """This skill allows a player to increase their speed depending
on their level""")

""" Assign all the server variables """
maxLevel        = config.cvar("srpg_speedMax",               5, "The maximum level of this skill")
creditStart     = config.cvar("srpg_speedCreditsStart",     20, "The starting amount of credits for this skill")
creditIncrement = config.cvar("srpg_speedCreditsIncrement", 25, "How much the credits increment after the first level")
maxSpeed        = config.cvar("srpg_speedMaximum",         1.5, "The maximum speed a player can go with the speed ability")

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
    Executed when a player spawns. Execute the setSpeed function after a tick
    so that it has time to assign the normal speed and other addons to modify
    it within the first tick.
    
    @PARAM event_var - an automatically passed event instance
    """
    if not es.getplayeprop(ev['userid'], 'CBasePlayer.pl.deadflag'):
        userid = event_var['userid']
        player = sourcerpg.players[userid]
        if player[skillName]:
            gamethread.delayed(0, setSpeed, userid)
        
def sourcerpg_skillupgrade(event_var):
    """
    An event which executes when a player upgrades a skill. If the skill is
    Speed, then ensure that their speed is altered acoordingly
    
    @PARAM event_var - an automatically passed event instance
    """
    if event_var['skill'] == skillName:
        setSpeed(event_var['userid'])
        
def sourcerpg_skilldowngrade(event_var):
    """
    An event which executes when a player sells a skill. If the skill is
    Speed, then ensure that their speed is altered acoordingly
    
    @PARAM event_var - an automatically passed event instance
    """
    if event_var['skill'] == skillName:
        setSpeed(event_var['userid'])
        
def setSpeed(userid):
    """
    A function which alters the maximum and current speed of a player to
    match their current level
    
    @PARAM userid - the userid of which to set the speed of
    """
    player = sourcerpg.players[userid]
    level  = player[skillName]
    if level:
        eachSegment = float(speedMaximum) - 1.0 / maxLevel
        level = level * eachSegement + player['maxSpeed']
        player['maxSpeed'] = level
        es.setplayerprop(userid, 'CBasePlayer.localdata.m_flLaggedMovementValue', level)