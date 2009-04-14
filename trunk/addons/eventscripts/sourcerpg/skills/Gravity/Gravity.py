import es
import gamethread

from sourcerpg import sourcerpg

skillName = "Gravity"

""" Execute the configuration information """
config = sourcerpg.skillConfig

""" Set the info of this skill """
config.addInfo(skillName, """This skill allows a player to reduce their gravity
so that the higher the skill level, the higher they jump""")

""" Assign all the server variables """
maxLevel        = config.cvar("srpg_gravityMax",              10, "The maximum level of this skill")
creditStart     = config.cvar("srpg_gravityCreditsStart",     15, "The starting amount of credits for this skill")
creditIncrement = config.cvar("srpg_gravityCreditsIncrement", 10, "How much the credits increment after the first level")
minGravity      = config.cvar("srpg_gravityMinimum",          30, "The lowest possible gravity (as a percentage) e.g. 30 = at maximum level user will have 30% of normal gravity")

class GravityManager(object):
    """ Class to manager the tick listener, and to manage the players gravity """
    def __init__(self):
        """ Default constructor; assign all local methos here """
        self.gravityList = {}
       
    def __getitem__(self, userid):
        """
        Executed automatically when the singleton is indexed, return the
        gravity object
        
        @PARAM userid - userid to return to GravityObject() of
        @RETRUN GravityObject - that is relevant to the player
        """
        userid = int(userid)
        if self.__contains__(userid):
            return self.gravityList[userid]
        return None
    
    def __delitem__(self, userid):
        """
        Executed automatically when del instnace[key] is executed. Remove
        the player
        
        @PARAM userid - userid to delete
        """
        self.removePlayer(userid)
        
    def __contains__(self, userid):
        """
        Executed automatically when we run a test to see if a userid exists
        within the singleton.
        
        @PARAM userid - the id of the user you want to test for validity
        @RETURN boolean - whether or not the player exists
        """
        userid = int(userid)
        return bool(userid in self.gravityList)
       
    def addPlayer(self, userid, amount):
        """ 
        Check if there are already any players in the gravityChange list.
        If there isn't, start the tick listener. Following this, check
        if the userid is in the dictionary, if so, remove them. Then create
        a new instance.
        
        @PARAM userid - the user to set the gravity to
        @PARAM amount - the new amount of gravity to assign
        """
        userid = int(userid)
        
        if not self.gravityList:
            gamethread.delayedname(0.25, 'gravity_check', self._ticker)
            
        if self.__contains__(userid):
            self.removePlayer(userid)
            
        self.gravityList[userid] = GravityObject(userid, float(amount) )
        self.gravityList[userid].update()
        self.gravityList[userid].reset()
       
    def removePlayer(self, userid):
        """ 
        Check if the player is in the dictioanry. If so, reset their gravity to 1
        and delete their instance from the dictionary. If there are no more players
        within the gravityList, remove the tick listener
        
        @PARAM userid - the use who to check
        """
        userid = int(userid)
        
        if self.__contains__(userid):
            del self.gravityList[userid]
            
        if not self.gravityList:
            gamethread.cancelDelayed('gravity_check')
       
    def clearList(self):
        """
        Loop through all the players, reset their gravity to 1, delete the gravity
        list then unregister the tick listener.
        """
        self.gravityList.clear()
        gamethread.cancelDelayed('gravity_check')
       
    def _ticker(self):
        """
        Here we loop through all of the players, and check their gravity etc.
        """
        for player in self.gravityList.itervalues():
            player.update()
        gamethread.delayedname(0.25, 'gravity_check', self._ticker)        
        
class GravityObject(object):
    """
    This class managers all the players, their current values and any functions
    reloving around the player.
    """
    def __init__(self, userid, amount):
        """
        Default constructor. Assign default values
        
        @PARAM userid - the user who this gravity object represents
        @PARAM amount - the default amount of gravity to assign
        """
        self.lastAirValue      = es.getplayerprop(userid, 'CBasePlayer.m_fFlags') & 1
        self.lastMovementValue = es.getplayerprop(userid, 'CBaseEntity.movetype')
        self.userid = int(userid)
        self.amount = amount
        
    def __del__(self):
        """ Default deconstructor; ensure their gravity is assigned back to 0 """
        es.server.queuecmd('es_xfire %s !self addoutput "gravity 1.0" 0.1 1' % self.userid )
        
    def update(self):
        """
        This method updates a player's settings. If they've changed, they will
        reset the players gravity
        """
        newAirValue      = es.getplayerprop(self.userid, 'CBasePlayer.m_fFlags') & 1
        newMovementValue = es.getplayerprop(self.userid, 'CBaseEntity.movetype')
        if newAirValue != self.lastAirValue:
            """ Player has jumped """
            self.lastAirValue = newAirValue
            self.reset()
        elif newMovementValue != self.lastMovementValue and newMovementValue == 2:
            """ Player has gone back to static movements, (i.e jumped off of a ladder) """
            self.lastMovementValue = 2
            self.reset()
        
    def reset(self, amountOverride = None):
        """
        This method resets a player's gravity either back to the default amount
        or if overridden, then to that amount.
        
        @PARAM OPTIONAL amountOverride - if this is set to an integral amount,
                                         that value will take presedence over the
                                         default value.
        """
        if amountOverride is None:
            es.server.queuecmd('es_xfire %s !self addoutput "gravity %s" 0.1 1'% ( self.userid, self.amount ) )
        else:
            es.server.queuecmd('es_xfire %s !self addoutput "gravity %s" 0.1 1'% ( self.userid, amountOverride ) )
       
""" Create the GravityManager() singleton """
gravity = GravityManager()

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
    gravity.clearList()

def player_spawn(event_var):
    """
    Executed when the player spawns. Reset the gravity to 1.0 in case the previous
    round they had default gravity, then ensure that a delay is assigned to
    set the gravity of the user.
    
    @PARAM event_var - an automaticall passed event instance
    """
    userid = event_var['userid']
    if not es.getplayerprop(userid, 'CBasePlayer.pl.deadflag'):
        player = sourcerpg.players[userid]
        if player is not None:
            gravity.removePlayer(userid)
            sourcerpg.players[userid]['maxGravity'] = 1.0
            """ We need to delay so the main class don't overwrite our minimum values """
            gamethread.delayed(0, setGravityAmount, userid)
        
def player_death(event_var):
    """
    Executed when a player dies. Remove them from the gravity list so they
    aren't being iterated through
    
    @PARAM event_var - an automatically passed event instance
    """
    del gravity[event_var['userid']]
        
def player_disconnect(event_var):
    """
    Executed when a player leaves the server, ensure they're removed from the
    gravity manager object
    
    @PARAM event_var - an automatically passed event instance
    """
    del gravity[event_var['userid']]
        
def sourcerpg_skillupgrade(event_var):
    """
    This event executes when a player's skill is upgraded. If the skill was
    this skill, then stop any active loops, and create a new instance
    with the new values so that upgrades take place instantly
    
    @PARAM event_var - an auotomatically passed event instance
    """
    if event_var['skill'] == skillName:
        userid = event_var['userid']
        setGravityAmount(userid)
        
def sourcerpg_skilldowngrade(event_var):
    """
    This event executes when a player's skill is downgraded. If the skill was
    this skill, then stop any active loops, and create a new instance
    with the new values so that downgrades take place instantly
    
    @PARAM event_var - an auotomatically passed event instance
    """
    if event_var['skill'] == skillName:
        userid = event_var['userid']
        level  = int(event_var['level'])
        if level:
            setGravityAmount(userid)
        else:
            del gravity[userid]
        
def setGravityAmount(userid):
    """
    This method sets the gravity value to the user
    
    @PARAM userid - the id of the user who needs the gravity setting
    """
    amount = getGravityAmount(userid)
    if amount:
        if userid in gravity:
            gravity[userid].amount = amount
        else:
            gravity.addPlayer(userid, amount)
        sourcerpg.players[userid]['maxGravity'] = amount

def getGravityAmount(userid):
    """
    This method acquires the correct value for the amount of gravity based
    from the level and the server configuration values
    
    @PARAM userid - the id of the user that needs to get the true gravity value
    @RETURN float - the true gravity amount as a decimal between 0 and 1
    """
    level = sourcerpg.players[userid][skillName]
    if level:
        percent    = float(minGravity) / 100.
        eachSlice  = (1 - percent) / int(maxLevel)
        totalSlice = eachSlice * level 
        return 1 - totalSlice
    return 0