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

baseStealth = {}

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
        if player is not None:
            level  = player[skillName]
            if level:
                """ If the level is greater than 0 """
                gamethread.delayed(0, getBaseStealth, userid)
                gamethread.delayed(0, gamethread.delayed(0, setStealth, userid) )
            
def player_disconnect(event_var):
    """
    Executed when a player disconnects from the server. If they have an instance
    in the global dictionary, remove them from it
    
    @PARAM event_var - an automatically passed event instace
    """ 
    userid = event_var['userid']
    if userid in baseStealth:
        del baseStealth[userid]

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
            
def getBaseStealth(userid):
    """
    A function to store the base stealth so we can refer back to this without
    it growing exponentially

    @PARAM userid - the user who to get the base health for
    """
    baseStealth[userid] = sourcerpg.players[userid]['minStealth']

def setStealth(userid):
    """
    This function assigns a new stealth value to a player dependant on their
    level. It will update the player's alpha value in the SourceRPG class so
    we can reference this value in other skills
    
    @PARAM userid - the user who we wish to assign the new stealth to
    """
    player = sourcerpg.players[userid]
    level  = player[skillName]
    percentage = int(baseStealth[userid] * float(minStealth) / 100.)
    eachSegment = int( (baseStealth[userid] - percentage) / maxLevel )
    eachSegment = baseStealth[userid] - (level * eachSegment)
    if eachSegment < 0:
        eachSegment = 0
    elif eachSegment > 255:
        eachSegment = 255
    player['minStealth'] = eachSegment
    
    """ Get the current color of the player and modify the alpha value """
    playerlibInstance = playerlib.getPlayer(userid)
    red, green, blue, alpha = playerlibInstance.getColor()
    playerlibInstance.setColor(red, green, blue, eachSegment)