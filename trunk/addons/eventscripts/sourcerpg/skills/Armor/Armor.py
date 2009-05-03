import es
import gamethread

from sourcerpg import sourcerpg

skillName = "Armor"

""" Execute the configuration information """
config = sourcerpg.skillConfig

""" Set the info of this skill """
config.addInfo(skillName, """This skill allows a player to increase their maximum
armor, and the amount of health they start with.""")

""" Assign all the server variables """
maxLevel        = config.cvar("srpg_armorMax",              16, "The maximum level of this skill")
creditStart     = config.cvar("srpg_armorCreditsStart",     15, "The starting amount of credits for this skill")
creditIncrement = config.cvar("srpg_armorCreditsIncrement", 10, "How much the credits increment after the first level")
armorIncrement  = config.cvar("srpg_armorIncrements",       25, "How much additional health each level acquires")

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
    An event which occurs when a player spawns. Set the default armor value.
    
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
                gamethread.delayed(0, getBaseArmor, userid)
                gamethread.delayed(0, gamethread.delayed, (0, setArmor, userid) )
        
def sourcerpg_skillupgrade(event_var):
    """
    An event which executes when a player upgrades a skill. If the skill is
    this skill, then ensure that their health is altered acoordingly
    
    @PARAM event_var - an automatically passed event instance
    """
    if event_var['skill'] == skillName:
        setArmor(event_var['userid'])
        
def sourcerpg_skilldowngrade(event_var):
    """
    An event which executes when a player sells a skill. If the skill is
    this skill, then ensure that their health is altered acoordingly
    
    @PARAM event_var - an automatically passed event instance
    """
    if event_var['skill'] == skillName:
        setArmor(event_var['userid']) 
        
def getBaseArmor(userid):
    """
    A function to store the base armor so we can refer back to this without
    it growing exponentially

    @PARAM userid - the user who to get the base armor for
    """
    baseArmor[userid] = sourcerpg.players[userid]['maxArmor']

def setArmor(userid):
    """
    A function which alters the maximum and current armor of a player to
    match their current level
    
    @PARAM userid - the userid of which to set the armor of
    """
    player = sourcerpg.players[userid]
    armor  = baseArmor[userid]
    level  = player[skillName]
    level  = level * int(armorIncrement) + armor
    player['maxArmor'] = level
    es.setplayerprop(userid, 'CCSPlayer.m_ArmorValue', level)