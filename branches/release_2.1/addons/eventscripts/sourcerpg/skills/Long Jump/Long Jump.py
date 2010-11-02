import es

from sourcerpg import sourcerpg

skillName = "Long Jump"

""" Execute the configuration information """
config = sourcerpg.skillConfig

""" Set the info of this skill """
config.addInfo(skillName, """This skill allows a player to jump further,
depending on their level.""")

""" Assign all the server variables """
maxLevel        = config.cvar("srpg_longJumpMax",               5, "The maximum level of the skill")
creditStart     = config.cvar("srpg_longJumpCreditsStart",     20, "The starting amount of credits for this skill")
creditIncrement = config.cvar("srpg_longJumpCreditsIncrement", 15, "How much the credits increment after the first level")

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

def player_jump(event_var):
    """
    Executed when a player jumps. Get the level and set their velecity to
    a greater amount.
    """
    userid = event_var['userid']
    player = sourcerpg.players[userid]
    level  = player[skillName] 
    if level:
        """ Acqure their current vectors """
        horizontalVector = es.getplayerprop(userid, 'CBasePlayer.localdata.m_vecVelocity[0]')
        verticalVector   = es.getplayerprop(userid, 'CBasePlayer.localdata.m_vecVelocity[1]')
        
        """ Multiply them by the level then by a quater so it's not such a huge difference """
        horizontalVector = (level * horizontalVector) * 0.25
        verticalVector   = (level * verticalVector)   * 0.25
        
        """ Create a string vector which is used by valve """
        vector = "%s,%s,0" % (horizontalVector, verticalVector)
        
        """ Assign the new vector to the players velocity """
        es.setplayerprop(userid, 'CBasePlayer.localdata.m_vecBaseVelocity', vector)