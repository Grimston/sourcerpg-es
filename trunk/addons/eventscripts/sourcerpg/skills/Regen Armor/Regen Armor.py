import es
import repeat

from sourcerpg import sourcerpg

skillName = "Regen Armor"

""" Execute the configuration information """
config = sourcerpg.skillConfig

""" Set the info of this skill """
config.addInfo(skillName, """This skill allows a player to regenerate a certain amount of armor every
so often until their maximum armor is reached.""")

""" Assign all the server variables """
maxLevel        = config.cvar("srpg_regenArmorMax",              10, "The maximum level of the regen skill")
creditStart     = config.cvar("srpg_regenArmorCreditsStart",      5, "The starting amount of credits for this skill")
creditIncrement = config.cvar("srpg_regenArmorCreditsIncrement", 10, "How much the credits increment after the first level")
regenDelay      = config.cvar("srpg_regenArmorDelayTimer",      1.0, "The time (in seconds) between each time a user's regen power adds more armor") 

class RegenManager(object):
    """
    This object is only used to manage all the RegenObject instances. It allows
    us to add or remove players from this class as / when needed
    """
    def __init__(self):
        """
        Default constructor, initialize the classes container
        """
        self.regenObjects = {}
        
    def __contains__(self, userid):
        """
        Executed when we need to see if the container contains a userid
        
        @RETURN boolean - whether or not the user exists
        """
        userid = int(userid)
        return userid in self.regenObjects
        
    def __delitem__(self, userid):
        """
        Executed automatically when an item from the singleton attempts to be
        removed. Delete them from this container
        
        @PARAM userid - the user who to remove
        """
        userid = int(userid)
        if self.__contains__(userid):
            del self.regenObjects[userid] # calls deconstructor
            
    def __getitem__(self, userid):
        """
        Checks if a player exists, if so, then it returns their RegenObject
        instance
        
        @PARAM userid - the user who to return the instance of
        @RETURN RegenObject - the instance related to the user
        """
        userid = int(userid)
        if self.__contains__(userid):
            return self.regenObjects[userid]
        return None
        
    def addPlayer(self, userid):
        """
        A function to add a player to the container
        
        @PARAM userid - the user who to add
        """
        userid = int(userid)
        if not self.__contains__(userid):
            self.regenObjects[userid] = RegenObject(userid)
            
    def removePlayer(self, userid):
        """
        A wrapper function to execute the __delitem__ method
        
        @PARAM userid - the userid to remove
        """
        self.__delitem__(userid)
            
class RegenObject(object):
    """
    This object is player specific and acts as a wrapper between our main
    class instance and a repeat instance. Ensure that we can start and stop
    the repeat as / when needed
    """
    def __init__(self, userid):
        """
        Default constructor, initialize variables
        
        @PARAM userid - the user who this class represents
        """
        self.userid   = int(userid)
        self.regening = False
        self.repeat   = None
        
    def __del__(self):
        """
        Default deconstructor, executed when this object is removed. Ensure
        that the repeat is stopped and removed
        """
        if self.repeat is not None:
            self.repeat.stop()
            self.repeat.delete()
        
    def startRegen(self, amount, delay):
        """
        This method creates a repeat if it doesn't exist and then begins the 
        repeat to heal the user every so often
        
        @PARAM amount - the amount of health to heal
        @PARAM delay - the time (in seconds) to delay each heal
        """
        if not self.isRunning():
            self.repeat = repeat.create("sourcerpg_regenarmor_user%s" % self.userid, self.addArmor, amount)
            self.repeat.start(delay, 0)
        
    def stopRegen(self):
        """
        This method stops the repeat and removes the repeat instance and sets
        the repeat attribute to None
        """
        if self.repeat is not None:
            self.repeat.stop()
            self.repeat.delete()
            self.repeat = None
            
    def isRunning(self):
        """
        This option tests if the current repeat is active
        
        @RETURN boolean - whether or not this repeat is currently active
        """
        if self.repeat is None:
            return False
        return bool( self.repeat.info('status') != repeat.STATUS_STOPPED )
            
    def addArmor(self, amount):
        """
        This function gets the current health and adds the amount to their health.
        If the health is above their maximum (defined in sourcerpg) then set it
        to their maximum armor and stop the regeneration
        
        @PARAM amount - amount of health to add
        """
        currentArmor = self.getArmor(self.userid) + amount
        player = sourcerpg.players[self.userid]
        if currentArmor > player['maxArmor']:
            currentArmor = player['maxArmor']
            self.stopRegen()
        self.setArmor(self.userid, currentArmor)
        
    @staticmethod
    def getArmor(userid):
        """
        This static method returns the amount of armor a user has
        
        @PARAM userid - the userid to get the health of
        @RETURN integer - amount of armor a user has
        """
        return es.getplayerprop(userid, 'CCSPlayer.m_ArmorValue')
        
    @staticmethod
    def setArmor(userid, amount):
        """
        This static method sets a new value of armor to a user
        
        @PARAM userid - the userid to get the armor of
        @PARAM amount - the new amount of armor to set to
        """
        es.setplayerprop(userid, 'CCSPlayer.m_ArmorValue', amount)

""" Create the RegenManager() singleton """
regen = RegenManager()

def load():
    """ 
    This method executes when the script loads. Register the skill
    """
    sourcerpg.skills.addSkill( skillName, maxLevel, creditStart, creditIncrement )
    
    """ If loaded late then ensure all players are added """
    for player in es.getUseridList():
        regen.addPlayer(player)
    
def unload():
    """
    This method executes when the script unloads. Unregister the skill
    """
    sourcerpg.skills.removeSkill( skillName )
    
def player_activate(event_var):
    """
    This event ensures that a player is in the RegenManager object so we can
    have access to their RegenObject instance
    
    @PARAM event_var - an automatically passed event instance
    """
    regen.addPlayer(event_var['userid'])
    
def player_disconnect(event_var):
    """
    This event ensures that a player is removed from memory when they leave the server
    
    @PARAM event_var - an automatically passed event instnace
    """
    del regen[event_var['userid']]
    
def player_death(event_var):
    """
    This event activates when a player dies. Ensure that the regeneration stops
    
    @PARAM event_var - an automatically passed event instance
    """
    userid = event_var['userid']
    if regen[userid].isRunning():
        regen[userid].stopRegen()
    
def player_hurt(event_var):
    """
    This event executes when a player is damaged. If the user's regeneration
    isn't currently running, then create one and start the regeneration
    
    @PARAM event_var - an automatically passed event instance
    """
    userid = event_var['userid']
    level  = sourcerpg.players[userid][skillName]
    if level:
        if not regen[userid].isRunning():
            regen[userid].startRegen(level, float(regenDelay) )
            
def sourcerpg_skillupgrade(event_var):
    """
    This event executes when a player's skill is upgraded. If the skill was
    regeneration, then stop any active regenerations, and create a new instance
    with the new values so that upgrades take place instantly
    
    @PARAM event_var - an auotomatically passed event instance
    """
    if event_var['skill'] == skillName:
        userid = event_var['userid']
        regen[userid].stopRegen()
        regen[userid].startRegen( int(event_var['level']), float(regenDelay) )
        
def sourcerpg_skilldowngrade(event_var):
    """
    This event executes when a player's skill is downgraded. If the skill was
    regeneration, then stop any active regenerations, and create a new instance
    with the new values so that downgrades take place instantly
    
    @PARAM event_var - an auotomatically passed event instance
    """
    if event_var['skill'] == skillName:
        userid = event_var['userid']
        level  = int(event_var['level'])
        regen[userid].stopRegen()
        if level:
            regen[userid].startRegen( level, float(regenDelay) )