import es
import repeat
import gamethread
import playerlib

import random

from sourcerpg import sourcerpg

skillName = "Smog Grenade"

""" Execute the configuration information """
config = sourcerpg.skillConfig

""" Set the info of this skill """
config.addInfo(skillName, """This skill changes the smoke cloud emited from a smoke grenade
to be poisionous.""")

""" Assign all the server variables """
maxLevel        = config.cvar("srpg_smogMax",               5, "The maximum level of this skill")
creditStart     = config.cvar("srpg_smogCreditsStart",     20, "The starting amount of credits for this skill")
creditIncrement = config.cvar("srpg_smogCreditsIncrement", 20, "How much the credits increment after the first level")
damagePerLevel  = config.cvar("srpg_smogDamagePerLevel",    2, "How much damage per second each level the smog cloud does to others")

class SmokeGrenadeManager(object):
    """
    This class manages all aspects of smoke grenades and saves them all in a
    local container.
    """
    def __init__(self):
        """
        Intialization executed automatically on object creation. Assign default
        variables.
        """
        self.entities = {}
        self.repeat   = repeat.create("sourcerpg_smokegrenade", self.check)

    def __del__(self):
        """
        Default deconstructor. Executed autmatically on object delete. Remove
        variables.
        """
        self.clear()
        self.repeat.delete()

    def clear(self):
        """
        Iterate through all the items in the container and remove the entity
        and cancel the delays
        """
        for entity in self.entities.copy():
            self.removeEntity(entity)

    def addEntity(self, entity, userid):
        """
        Add an entity into the contianer and begin a delay to remove the items

        @PARAM entity - the entity to add
        @PARAM userid - the id of the owner of the smoke grenade
        """
        self.entities[entity] = int(userid)
        gamethread.delayedname(18, "sourcerpg_smokegrenade_entity%s" % entity, self.removeEntity, entity)

    def removeEntity(self, entity):
        """
        Remove a specific entity and cancel the delay

        @PARAM entity - the entity to remove
        """
        if entity in self.entities:
            del self.entities[entity]
            gamethread.cancelDelayed("sourcerpg_smokegrenade_entity%s" % entity)

            """ Remove the entity if it exists """
            if entity in es.createentitylist("smokegrenade_projectile"):
                es.remove(entity)

    def removeEntitiesFromPlayer(self, player):
        """
        Remove all entities from the dictionary relating to a specific player

        @PARAM player - the player to remove all instances of
        """
        player = int(player)
        for entity, userid in self.entities.copy().iteritems():
            if userid == player:
                self.removeEntity(entity)

    def stop(self):
        """
        Stop the current delay so we can restart it at round start
        """
        self.repeat.stop()

    def start(self):
        """
        Start the repeat and ensure we are checking every second indefinitely
        """
        self.repeat.start(1, 0)

    def check(self):
        """
        This function is a function which is repeated every second to check
        all current player positions and relative smoke grenades. If the
        player is in range, damage them.
        """
        smokeList = es.createentitylist("smokegrenade_projectile")
        for entity in self.entities.copy():
            if entity in smokeList:
                x, y, z = map(float, es.getindexprop(entity, 'CBaseEntity.m_vecOrigin').split(","))
                player  = self.entities[entity]
                level   = sourcerpg.players[player][skillName]
                for loopPlayer in playerlib.getPlayerList('#t,#alive' if es.getplayerteam(player) == 3 else '#ct,#alive'):
                    xx, yy, zz = loopPlayer.get('location')
                    if abs(x - xx) <= 220 and abs(y - yy) <= 220 and abs(z - zz) <= 220:
                        es.server.queuecmd('damage %s %s 32 %s' % ( int(loopPlayer), level * int(damagePerLevel), player) )
                        es.emitsound('player', int(loopPlayer), 'player/damage%s.wav' % random.randint(1, 3), '0.7', '0.6')
            else:
                self.removeEntity(entity)

smoke = SmokeGrenadeManager()

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
    smoke.clear()
    smoke.repeat.delete()

def round_freeze_end(event_var):
    """
    Start the delay to check for smokegrenade positions.

    @PARAM event_var - an automatically passed event instance
    """
    smoke.start()

def round_end(event_var):
    """
    Clear all items from the container as we don't need to check any more

    @PARAM event_var - an automatically passed event instance
    """
    smoke.clear()
    smoke.stop()

def smokegrenade_detonate(event_var):
    """
    Executed when a smoke grenade detonates. Get the userid of the person
    who detonated it and add the user and entity into the class.

    @PARAM event_var - an automatically passed event instance
    """
    userid = event_var['userid']
    player = sourcerpg.players[userid]
    level  = player[skillName]
    if level:
        """ The player has at least level 1, so create an instance of this object """
        handle      = es.getplayerhandle(userid)
        for entity in es.createentitylist("smokegrenade_projectile"):
            if handle == es.getindexprop(entity, 'CBaseEntity.m_hOwnerEntity'):
                """ Add in the entitty as we have the owner so the right handle """
                smoke.addEntity(entity, userid)
                break