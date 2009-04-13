import es
import weaponlib
import repeat

from sourcerpg import sourcerpg

skillName = "Regen Ammo"

""" Execute the configuration information """
config = sourcerpg.skillConfig

""" Set the info of this skill """
config.addInfo(skillName, """This skill allows a player to regenerate ammo for their primary
and secondary weapons every so often until their maximum ammo is reached.""")

""" Assign all the server variables """
maxLevel        = config.cvar("srpg_regenAmmoMax",               5, "The maximum level of this skill")
creditStart     = config.cvar("srpg_regenAmmoCreditsStart",      5, "The starting amount of credits for this skill")
creditIncrement = config.cvar("srpg_regenAmmoCreditsIncrement", 10, "How much the credits increment after the first level")
regenDelay      = config.cvar("srpg_regenAmmoDelayTimer",      1.0, "The time (in seconds) between each time a user's regen power increments their ammo") 

class RegenAmmoManager(object):
    """
    This object is only used to manage all the RegenAmmoObject instances. It allows
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
            self.regenObjects[userid] = RegenAmmoObject(userid)
            
    def removePlayer(self, userid):
        """
        A wrapper function to execute the __delitem__ method
        
        @PARAM userid - the userid to remove
        """
        self.__delitem__(userid)
            
class RegenAmmoObject(object):
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
        self.handle   = es.getplayerhandle(self.userid)
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
        
    def start(self, amount, delay):
        """
        This method creates a repeat if it doesn't exist and then begins the 
        repeat to increment ammo every so often
        
        @PARAM amount - the amount of ammo to add
        @PARAM delay - the time (in seconds) to delay each repeat
        """
        if not self.isRunning():
            self.repeat = repeat.create("sourcerpg_regenammo_user%s" % self.userid, self.addAmmo, amount)
            self.repeat.start(delay, 0)
        
    def stop(self):
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
            
    def addAmmo(self, amount):
        """
        This function gets the current weapons of the user and adds ammo
        to their weapons.
        
        @PARAM amount - amount of ammo to add
        """
        weaponList  = weaponlib.getWeaponList('#primary')
        weaponList += weaponlib.getWeaponList("#secondary")
        for weapon in weaponList:
            for index in weapon.indexlist:
                if es.getindexprop(index, 'CBaseEntity.m_hOwnerEntity') == self.handle:
                    maxAmmo = weapon.maxammo
                    prop    = weapon.prop
                    currentAmmo = es.getplayerprop(self.userid, prop)
                    
                    currentAmmo += amount
                    if currentAmmo > maxAmmo:
                        currentAmmo = maxAmmo
                    es.setplayerprop(self.userid, prop, currentAmmo)
        
""" Create the RegenManager() singleton """
ammo = RegenAmmoManager()

def load():
    """ 
    This method executes when the script loads. Register the skill
    """
    sourcerpg.skills.addSkill( skillName, maxLevel, creditStart, creditIncrement )
    es.doblock("corelib/noisy_on")
    
    """ Add any active people to the list when the mod loads """
    for player in es.getUseridList():
        ammo.addPlayer(player)
    
def unload():
    """
    This method executes when the script unloads. Unregister the skill
    """
    sourcerpg.skills.removeSkill( skillName )
    es.doblock("corelib/noisy_off")
    
def player_activate(event_var):
    """
    Activated when a player joins the server. Add them to the repeat class
    so we can check for ammo etc.
    
    @PARAM event_var - an automatically pased event variable instance
    """
    ammo.addPlayer(event_var['userid'])
    
def player_disconnect(event_var):
    """
    Activated when a player leaves the server. Ensure that any active loops
    are stopped and that the instance is destroyed
    """
    
    del ammo[event_var['userid']]
    
def item_pickup(event_var):
    """
    Executed when a player picks up a weapon. If the repeat is not running,
    start the check
    
    @PARAM event_var - an automatically passed event instance
    """
    userid = event_var['userid']
    player = sourcerpg.players[userid]
    if player[skillName]:
        ammoPlayer = ammo[userid]
        if not ammoPlayer.isRunning():
            ammoPlayer.start( player[skillName], float(regenDelay) )
        
def weapon_reload(event_var):
    """
    Executed automatically when a weapon is reloaded. If the repeat is
    not currently currently running and the player has a skill, then
    start the repeat.
    
    @PARAM event_var - an automatically passed event instance
    """
    item_pickup(event_var)
    
def player_death(event_var):
    """
    Executed when a player dies. If they have a repeat currently active then
    ensure it is stopped to save resources
    
    @PARAM event_var - an automatically passed event instance
    """
    player = ammo[event_var['userid']]
    if player.isRunning():
        player.stop()
        
def sourcerpg_skillupgrade(event_var):
    """
    This event executes when a player's skill is upgraded. If the skill was
    regen ammo, then stop any active loops, and create a new instance
    with the new values so that upgrades take place instantly
    
    @PARAM event_var - an auotomatically passed event instance
    """
    if event_var['skill'] == skillName:
        userid = event_var['userid']
        ammo[userid].stop()
        ammo[userid].start( int(event_var['level']), float(regenDelay) )
        
def sourcerpg_skilldowngrade(event_var):
    """
    This event executes when a player's skill is downgraded. If the skill was
    regen ammo, then stop any active loops, and create a new instance
    with the new values so that downgrades take place instantly
    
    @PARAM event_var - an auotomatically passed event instance
    """
    if event_var['skill'] == skillName:
        userid = event_var['userid']
        level  = int(event_var['level'])
        ammo[userid].stop()
        if level:
            ammo[userid].start( level, float(regenDelay) )