import es
import random

from sourcerpg import sourcerpg

skillName = "Disable"

""" Execute the configuration information """
config = sourcerpg.skillConfig

""" Set the info of this skill """
config.addInfo(skillName, """This skill allows a player to force their victims to drop their
weapon when hit.""")

""" Assign all the server variables """
maxLevel        = config.cvar("srpg_disableMax",               10, "The maximum level of this skill")
creditStart     = config.cvar("srpg_disableCreditsStart",      15, "The starting amount of credits for this skill")
creditIncrement = config.cvar("srpg_disableCreditsIncrement",  10, "How much the credits increment after the first level")
percentage      = config.cvar("srpg_disablePercentage",         2, "The percentage multiplied by the attackers level each bullet has of disabling their victim")

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
    This event executes when a player is damaged. Check for opposite teams,
    if so, run the test to see if we should run the drop.

    @PARAM event_var - an automatically passed event instance
    """
    userid   = event_var['userid']
    attacker = event_var['attacker']
    player   = sourcerpg.players[attacker]
    if attacker and userid != attacker:
        if event_var['es_userteam'] != event_var['es_attackerteam']:
            level = player[skillName]
            if level:
                """ The attacker is at least level 1 in the drop skill """
                if random.randint(1, 100) <= level * float(percentage):
                    """ We have the drop percentage, drop it """
                    es.cexec(userid, 'drop')