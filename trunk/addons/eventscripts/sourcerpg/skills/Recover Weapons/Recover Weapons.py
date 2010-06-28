import es
import playerlib
import weaponlib
import gamethread

import spe

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
    gamethread.delayed(0, setDefaultAttributes, event_var['userid'])

def setDefaultAttributes(userid):
    """
    A function to assign the default attributes and values to the players
    object within SourceRPG. We need to delay by 0 seconds to ensure that
    1 tick is passed so we can be sure that the Player's object has been
    created.

    @PARAM userid - the id of the user we wish to assign the values to
    """
    player = sourcerpg.players[userid]
    if player is not None:
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
    if player is not None:
        if player['recover']:
            level = player[skillName]
            if level:
                currentDelay = 0.1
                """ Player is at least level one in this skill """
                for weaponName in weaponlib.getWeaponNameList("#grenade"):
                    while player[weaponName] > 0:
                        gamethread.delayed(currentDelay, giveWeapon, (userid, weaponName))
                        player[weaponName] -= 1
                        currentDelay += 0.1

                if level >= 2:
                    """ Player has at least level 2, give them back their secondary """
                    if player["secondary"]:
                        handle = es.getplayerhandle(userid)
                        for index in weaponlib.getIndexList({2 : "weapon_glock", 3 : "weapon_usp"}[es.getplayerteam(userid)]):
                            if es.getindexprop(index, 'CBaseEntity.m_hOwnerEntity') == handle:
                                gamethread.delayed(currentDelay, safeRemove, index)
                                currentDelay += 0.1
                                break
                        gamethread.delayed(currentDelay, giveWeapon, (userid, player["secondary"]) )
                        currentDelay += 0.1

                if level >= 3:
                    """ Player has at least level 3, give them back their primary """
                    if player["primary"]:
                        gamethread.delayed(currentDelay, giveWeapon, (userid, player["primary"]))

                player['recover'] = False
                
def safeRemove(index):
    """
    Ensures that an entity exists before safely removing it.
    
    @pararm int index The entity ID of the object to remove
    """
    if index in es.createentitylist():
        es.server.queuecmd("es_xremove %s" % index)
                                                           
def giveWeapon(userid, weapon):
    """
    Gives a player a named weapon. The reason we have a custom function for
    this is so we can alter the method. Currently SPE is the only safe way to
    do this.
    
    @param int userd The ID of the user
    @param str weapon The Weapon name to give to the player
    """
    spe.giveNamedItem(userid, weapon)

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
    weapon = weaponlib.getWeapon(event_var['item'])
    if weapon is None:
        """ The item picked up is not a valid weapon, return early """
        return
    weapon = weapon.name # format the weapon name
    userid = event_var['userid']
    player = sourcerpg.players[userid]
    if player is not None:
        level  = player[skillName]
        if level:
            """ Player is at least level 1 in this skill """
            if weapon in weaponlib.getWeaponNameList('#primary') and level >= 3:
                player['primary'] = weapon

            elif weapon in weaponlib.getWeaponNameList('#secondary') and level >= 2:
                if weapon != {2 : "weapon_glock", 3 : "weapon_usp"}[es.getplayerteam(userid)]:
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
    Executed when a smoke grenade detonates. Deduct their smoke count if they have
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
            weapon = weaponlib.getWeapon(playerlib.getPlayer(userid).get("weapon"))
            if weapon is None:
                # The user has no weapons, allow them to run the drop command
                return True

            weapon = weapon.name # return formated weapon
            
            if level >= 3 and weapon in weaponlib.getWeaponNameList("#primary"):
                player['primary'] = None

            elif level >= 2 and weapon in weaponlib.getWeaponNameList("#secondary"):
                player['secondary'] = None

    return True