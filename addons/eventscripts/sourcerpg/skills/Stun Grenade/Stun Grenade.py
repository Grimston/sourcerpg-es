import es
import gamethread
import playerlib

from sourcerpg import sourcerpg

skillName = "Stun Grenade"

""" Execute the configuration information """
config = sourcerpg.skillConfig

""" Set the info of this skill """
config.addInfo(skillName, """This skill allows a player to stun another which makes their
screen shake when hit with a flashbang.""")

""" Assign all the server variables """
maxLevel        = config.cvar("srpg_stunNadeMax",                 5, "The maximum level of this skill")
creditStart     = config.cvar("srpg_stunNadeCreditsStart",       30, "The starting amount of credits for this skill")
creditIncrement = config.cvar("srpg_stunNadeCreditsIncrement",   20, "How much the credits increment after the first level")
removeFlash     = config.cvar("srpg_stunNadeRemoveFlash",         0, "Whether or not the normal flash bang effect is removed on this server")

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
    
def flashbang_detonate(event_var):
    """
    Executed when a flashbang detonates. Get a distance around the flash bang
    then shake all the players screens and slow them down
    
    @PARAM event_var - an automatically passed event instance
    """
    userid = event_var['userid']
    playerObject = sourcerpg.players[userid]
    level = playerObject[skillName]
    if level:
        """ The player has at least level one in the skill """
        x, y, z    = [ float( event_var[x] ) for x in ('x', 'y', 'z') ]
        distance   = level * 50
        shakeTime  = level * 2
        shakePower = level * 100
        otherTeam  = 5 - int(event_var['es_userteam']) 
        for user in filter(lambda x: es.getplayerteam(x) == otherTeam, es.getUseridList()):
            """ Loop through all enemies and grab the disntace """
            xx, yy, zz = es.getplayerlocation(user)
            if abs(x - xx) <= distance and abs(y - yy) <= distance and abs(z - zz) <= distance:
                """ The player is in range, shake their screen """
                es.usermsg('create', 'shake', 'Shake')
                es.usermsg('write',  'byte',  'shake', 0)
                es.usermsg('write',  'float', 'shake', shakePower)
                es.usermsg('write',  'float', 'shake', 1.0)
                es.usermsg('write',  'float', 'shake', shakeTime)
                es.usermsg('send',   'shake', user)
                es.usermsg('delete', 'shake')

def player_blind(event_var):
    """
    Executed when a player is blinded by a flash bang. If the value of the
    removeFlash is true, then set their flash value to 0.
    
    @PARAM event_var - an automatically passed event instance
    """
    if bool(int(removeFlash)):
        userid = event_var['userid']
        player = playerlib.getPlayer(userid)
        player.setFlash(0, 0)