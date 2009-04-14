import es
import playerlib
import weaponlib

from sourcerpg import sourcerpg

skillName = "Recover Weapons"

""" Execute the configuration information """
config = sourcerpg.skillConfig

""" Set the info of this skill """
config.addInfo(skillName, """This skill allows a player to set recover their weapons when
they die. These are static levels so that's why the maximum level is not configurable.""")

""" Assign all the server variables """
creditStart     = config.cvar("srpg_recoverWeaponsCreditsStart",     25, "The starting amount of credits for this skill")
creditIncrement = config.cvar("srpg_recoverWeaponsCreditsIncrement", 50, "How much the credits increment after the first level")

def load():
    """
    This method executes when the script loads. Register the skill
    """
    sourcerpg.skills.addSkill( skillName, 3, creditStart, creditIncrement )
    es.addons.registerClientCommandFilter(clientFilter)

def unload():
    """
    This method executes when the script unloads. Unregister the skill
    """
    sourcerpg.skills.removeSkill( skillName )
    es.addons.unregisterClientCommandFilter(clientFilter)

def player_activate(event_var):
    """
    Executed automatically when a player activates on the server. Ensure that
    they have the items in the dictionary loaded.

    @PARAM event_var - an automatic passed event instance
    """
    player              = sourcerpg.players[event_var['userid']]
    player['recover']   = False
    player['primary']   = None
    player['secondary'] = None

    for weaponName in weaponlib.getWeaponNameList("#grenade"):
        player[weaponName] = 0

def player_spawn(event_var):
    """
    Executed automatically when a player spawns. Test to see if their recover
    key is active, if so, activate their weapons and give them back their
    previous weapons.

    @PARAM event_var - an automatically passed event instance
    """
    userid = event_var['userid']
    if es.getplayerprop(userid, 'CBasePlayer.pl.deadflag'):
        """ The player is dead so we ignore this event, return early """
        return
    player = sourcerpg.players[userid]
    if player['recover']:
        level = player[skillName]
        if level:
            """ Player is at least level one in this skill """
            for weaponName in weaponlib.getWeaponNameList("#grenade"):
                while player[weaponName]:
                    es.server.queuecmd('es_xgive %s %s' %  (userid, weaponName) )
                    player[weaponName] -= 1

            if level >= 2:
                """ Player has at least level 2, give them back their secondary """
                if player["secondary"]:
                    es.server.queuecmd('es_xgive %s %s' % (userid, player["secondary"]) )

            if level >= 3:
                """ Player has at least level 3, give them back their primary """
                if player["primary"]:
                    es.server.queuecmd('es_xgive %s %s' % (userid, player["primary"]) )

            player['recover'] = False

def player_death(event_var):
    """
    Executed when a player dies. Get the current level of this skill, and then
    save all related weapons.

    @PARAM event_var - an automatically passed event instance
    """
    userid = event_var['userid']
    player = sourcerpg.players[userid]
    level  = player[skillName]
    if level:
        """ Player is at least level 1 in the level """
        player['recover'] = True

def item_pickup(event_var):
    """
    Exeecuted when a player picks up a weapon. Store their current weapon
    so it remembers the value

    @PARAM event_var - an automatically passed event instance
    """
    weapon = event_var['item']
    userid = event_var['userid']
    player = sourcerpg.players[userid]
    level  = player[skillName]
    if level:
        """ Player is at least level 1 in this skill """
        if weapon.startswith("weapon_"):
            """ The item picked up was a weapon """
            if weapon in weaponlib.getWeaponNameList('#primary') and level >= 3:
                player['primary'] = weapon

            elif weapon in weaponlib.getWeaponNameList('#secondary') and level >= 2:
                player['secondary'] = weapon

            elif weapon in weaponlib.getWeaponNameList('#grenade'):
                player[weapon] += 1

def flashbang_detonate(event_var):
    """
    Executed when a flashbang detonates. Deduct their flashbang value if they
    have one.

    @PARAM event_var - an automatically passed event instance
    """
    userid = event_var['userid']
    player = sourcerpg.players[userid]
    level  = player[skillName]
    if level:
        player['weapon_flashbang'] -= 1

def hegrenade_detonate(event_var):
    """
    Executed when a he grenade detonates. Deduct their he count if they have
    one.

    @PARAM event_var - an automatically passed event instnace
    """
    userid = event_var['userid']
    player = sourcerpg.players[userid]
    level  = player[skillName]
    if level:
        player['weapon_hegrenade'] -= 1

def smokegrenade_detonate(event_var):
    """
    Executed when a smoke grenade detonates. Deduct their he count if they have
    one.

    @PARAM event_var - an automatically passed event instnace
    """
    userid = event_var['userid']
    player = sourcerpg.players[userid]
    level  = player[skillName]
    if level:
        player['weapon_smokegrenade'] -= 1

def clientFilter(userid, args):
    """
    Executed when a client command is issued from a player. Test to see if drop
    was the command; if so, then remove the weapon.

    @PARAM userid - the id of the user who issued the client command
    @PARAM args - a list of arguments, with index 0 being the command.
    """
    if args and args[0].lower() == "drop":
        """ Player is about to issue the drop command """
        player = sourcerpg.players[userid]
        level  = player[skillName]
        if level:
            """ The player has recover weapons, get their active weapn and remove it """
            weapon = playerlib.getPlayer(userid).get("weapon")
            
            if level >= 3 and weapon in weaponlib.getWeaponNameList("#primary"):
                player['primary'] = None

            elif level >= 2 and weapon in weaponlib.getWeaponNameList("#secondary"):
                player['secondary'] = None

    return True