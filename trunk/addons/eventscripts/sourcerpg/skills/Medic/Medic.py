import es
import repeat

from sourcerpg import sourcerpg

skillName = "Medic"

""" Execute the configuration information """
config = sourcerpg.skillConfig

""" Set the info of this skill """
config.addInfo(skillName, """This skill allows a player to heal close by team mates
until their health / armor is full.""")

""" Assign all the server variables """
maxLevel        = config.cvar("srpg_medicMax",                5, "The maximum level of the skill")
creditStart     = config.cvar("srpg_medicCreditsStart",      25, "The starting amount of credits for this skill")
creditIncrement = config.cvar("srpg_medicCreditsIncrement",  15, "How much the credits increment after the first level")
minDistance     = config.cvar('srpg_medicMinDistance',      300, "The radius of the healing effect at level 1")
distanceInc     = config.cvar('srpg_medicDistanceIncrement', 50, "How much the radius grows each level")
delay           = config.cvar('srpg_medicDelay',              5, "The delay between the loops of the healing effect")
healingInc      = config.cvar('srpg_medicHealingIncrement',   5, "The amount of health each loop will do, multiplied by the player\'s level")

class HealManager(object):
    """
    This class will manage the heal objects which will be used to heal certain
    players and their teammates
    """
    def __init__(self):
        """
        Default constructor - initialize variables and assingn default values
        """
        self.objects = {}
    
    def __contains__(self, userid):
        """
        Test for validity to see if an object exists within the class container.

        @RETURN boolean - whether or not the object exists within the container
        """
        userid = int(userid)
        return bool(userid in self.objects)

    def __iter__(self):
        """
        Called automatically when we wish to iterate through the HealObject
        instances

        @RETURN iterObject - of each instance
        """
        for key in self.objects.itervalues():
            yield key

    def __getitem__(self, userid):
        """
        Returns an instance of an object referenced by the user's ID.

        @RETURN HealObject instance
        """
        userid = int(userid)
        if self.__contains__(userid):
            return self.objects[userid]
        return None

    def addObject(self, userid):
        """
        Add a userid into the object and store the value as a HealObject instance.

        @PARAM userid - the id of the user
        """
        userid = int(userid)
        self.objects[userid] = HealObject(userid)

    def removeObject(self, userid):
        """
        Remove an object from the classes container. This will call the
        deconstructor ont he HealObject instance so there is no need to manually
        clean up the repeat instance.

        @PARAM userid - the id of the user
        """
        if self.__contains__(userid):
            name = self.objects[int(userid)].name
            repeat.stop(name)
            repeat.delete(name)
            del self.objects[int(userid)]

class HealObject(repeat.Repeat):
    """
    This class is a child class of the repeat class wich allows us to specify
    custom commands and variables.
    """
    def __init__(self, userid):

        self.userid   = int(userid)
        self.gameName = es.getGameName()
        self.name     = "sourcerpg_medic_user%s" % userid
        repeat.Repeat.__init__(self, self.name, self.healTeamates)
        repeat.dict_repeatInfo[self.name] = self

    def __int__(self):
        """
        Executed automatically when statically converted to an integer.

        @RETURN integer - the user's ID as an integer
        """
        return self.userid

    def __str__(self):
        """
        Executed automatically when statically converted to an integer.

        @RETURN string - the user's ID as an string
        """
        return str(self.userid)

    def __repr__(self):
        """
        Executed automatically when repr() is called on the object. Return a
        string value which simulates how Python would represent the object.

        @RETURN string - simulation of python representation
        """
        return "HealObject(%s)" % self.userid

    def healTeamates(self):
        """
        This is the actual function which will get the current level, and
        loop through all team players and if their positions are within range
        increment their armor / health.
        """
        x, y, z = es.getplayerlocation(self.userid)
        team    = es.getplayerteam(self.userid)
        player  = sourcerpg.players[self.userid]
        if team not in (2, 3):
            return
        if player is not None:
            level   = player[skillName]
            if level:
                """ The user is at least level one in the medic skill """
                distance = ( int(minDistance) + (level - 1) * float(distanceInc) )
                healing  = int(healingInc) * level
                armor    = 0

                if bool( int(effects) ) and bool( es.ServerVar('est_version') ):
                    """ Create an effect if the server owner wants to """
                    filt = {3:'#c', 2:'#t'}[team]
                    es.server.queuecmd('est_effect 10 %s 0 "sprites/lgtning.vmt" %s %s %s %s 20 0.2 10 10 0 0 255 0 255 30' % (filt, x, y, z, distance) )
                    es.server.queuecmd('est_effect 10 %s 0.2 "sprites/lgtning.vmt" %s %s %s %s 20 0.2 10 10 0 0 255 0 255 30' % (filt, x, y, z, distance) )

                for teamPlayer in filter(lambda x: es.getplayerteam(x) == team and not es.getplayerprop(x, 'CBasePlayer.pl.deadflag'), es.getUseridList() ):
                    """ Loop through all the living players on their team """
                    xx, yy, zz = es.getplayerlocation(teamPlayer)
                    if ( (x - xx) ** 2 + (y - yy) ** 2 + (z - zz) ** 2 ) ** 0.5 <= distance:
                        health = es.getplayerprop(teamPlayer, 'CBasePlayer.m_iHealth')
                        sourcerpgPlayer = sourcerpg.players[teamPlayer]
                        if health < sourcerpgPlayer['maxHealth']:
                            if health + healing > sourcerpgPlayer['maxHealth']:
                                armor = sourcerpgPlayer['maxHealth'] - health - healing
                                es.setplayerprop(teamPlayer, 'CBasePlayer.m_iHealth', sourcerpgPlayer['maxHealth'])
                            else:
                                es.setplayerprop(teamPlayer, 'CBasePlayer.m_iHealth', healing + health)
                        else:
                            armor = healing

                        if armor and self.gameName == "cstrike":
                            """ if we're playing CSS and we have armor to increment, do the task """
                            maxArmor = sourcerpgPlayer['maxArmor']
                            currentArmor = es.getplayerprop(teamPlayer, 'CCSPlayer.m_ArmorValue')
                            currentArmor += armor
                            if currentArmor > maxArmor:
                                currentArmor = maxArmor
                            es.setplayerprop(teamPlayer, 'CCSPlayer.m_ArmorValue', currentArmor)

heal = HealManager() # Create the healManager() singleton

def load():
    """
    This method executes when the script loads. Register the skill
    """
    sourcerpg.skills.addSkill( skillName, maxLevel, creditStart, creditIncrement )

    for player in es.getUseridList():
        player_activate({'userid': player})

def unload():
    """
    This method executes when the script unloads. Unregister the skill
    """
    sourcerpg.skills.removeSkill( skillName )

def player_spawn(event_var):
    """
    Executed automatically when a player spawns, start the healing check

    @PARAM event_var - an automatically passed event instnace
    """
    userid = event_var['userid']
    if not es.getplayerprop(userid, 'CBasePlayer.pl.deadflag'):
        """ Player is alive, so it is the actual player spawn event """
        if userid in heal:
            heal[userid].start(float(delay), 0)

def player_death(event_var):
    """
    Executed automatically when a player dies, stop the healing check.

    @PARAM event_var - an automatically passed event instance
    """
    userid = event_var['userid']
    heal[userid].stop()

def player_activate(event_var):
    """
    This event executes automatically when a player is activated on the server.
    Add them to the manager singleton.

    @PARAM event_var - an automatically passed event instance
    """
    heal.addObject(event_var['userid'])

def player_disconnect(event_var):
    """
    This event executes automatically when a player leaves the server.
    Remove them from the manager singleton.

    @PARAM event_var - an automatically passed event instance
    """
    heal.removeObject(event_var['userid'])