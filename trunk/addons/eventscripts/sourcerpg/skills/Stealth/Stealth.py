import es
import gamethread
import playerlib

from sourcerpg import sourcerpg

skillName = "Stealth"

""" Execute the configuration information """
config = sourcerpg.skillConfig

""" Set the info of this skill """
config.addInfo(skillName, """This skill allows a player to become more invisible and
increasingly difficult to be seen""")

""" Assign all the server variables """
maxLevel        = config.cvar("srpg_stealthMax",                5, "The maximum level of this skill")
creditStart     = config.cvar("srpg_stealthCreditsStart",      15, "The starting amount of credits for this skill")
creditIncrement = config.cvar("srpg_stealthCreditsIncrement",  10, "How much the credits increment after the first level")
minStealth      = config.cvar("srpg_minimumStealthPercentage", 20, "The minimum percentage of stealth a player receives at the maximum level")

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
    Executed when a player spawns. Grab the current level of the player, if the
    stealth level is greater than 0, then execute the assignment after a tick
    has passed so we can allow other things to mess with the stealth value
    
    @PARAM event_var - an automatically passed event instance
    """
    userid = event_var['userid']
    if not es.getplayerprop(userid, 'CBasePlayer.pl.deadflag'):
        """ If the player is not dead """
        player = sourcerpg.players[userid]
        level  = player[skillName]
        if level:
            """ If the level is greater than 0 """
            gamethread.delayed(0, setStealth, userid)
            
def sourcerpg_skillupgrade(event_var):
    """
    An event which executes when a player upgrades a skill. If the skill is
    this skill, then ensure that their value is altered acoordingly
    
    @PARAM event_var - an automatically passed event instance
    """
    if event_var['skill'] == skillName:
        setStealth(event_var['userid'])
        
def sourcerpg_skilldowngrade(event_var):
    """
    An event which executes when a player sells a skill. If the skill is
    this skill, then ensure that their value is altered acoordingly
    
    @PARAM event_var - an automatically passed event instance
    """
    if event_var['skill'] == skillName:
        setStealth(event_var['userid'])
            
def setStealth(userid):
    """
    This function assigns a new stealth value to a player dependant on their
    level. It will update the player's alpha value in the SourceRPG class so
    we can reference this value in other skills
    
    @PARAM userid - the user who we wish to assign the new stealth to
    """
    player = sourcerpg.players[userid]
    level  = player[skillName]
    eachSegment = int(255 / 100. * float(minStealth) )
    eachSegment = player['minStealth'] - (level * eachSegment)
    if eachSegment < 0:
        eachSegment = 0
    elif eachsegment > 255:
        eachSegment = 255
    player['minStealth'] = eachSegment
    
    """ Get the current color of the player and modify the alpha value """
    playerlibInstance = playerlib.getPlayer(userid)
    red, green, blue, alpha = playerlibInstance.getColor()
    playerlibInstance.setColor(red, green, blue, eachSegment)