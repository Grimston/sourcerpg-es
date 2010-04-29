# SourceRPG release 2.0.0 by Steven Hartin
# ./sourcerpg/addons/sourcerpg_admin/sourcerpg_admin.py

#################################
#### DO NOT EDIT THIS FILE, #####
####    IF YOU DO, THINGS   #####
####   THINGS COULD BREAK   #####
#################################
import es
import cmdlib
import langlib
import playerlib
import popuplib
import gamethread

import os

from sourcerpg import sourcerpg

""" Import the psyco module which improves speed """
import psyco
psyco.full()

# Set the addon info data
info = es.AddonInfo()
info.name     = 'SourceRPG Admin'
info.basename = sourcerpg.info.basename + "/addons/sourcerpg_admin"
info.author   = sourcerpg.info.author

# Create the langlib function
text = lambda userid, textIdent, tokens = {}: "No strings.ini found in ./sourcerpg/addons/sourcerpg_admin/"
textPath = os.path.join( es.getAddonPath(info.basename), "strings.ini" )
if os.path.isfile(textPath):
    text = langlib.Strings(textPath)

class AdminManager(object):
    """
    This class manages the admin menu so that we can easilly add options and
    callbacks to this main popup. It allows us to keep a reference of the main
    popup so we don't have to find it at a later stage.
    """
    def __init__(self):
        """ Default constructor. Initialize variables. """
        self.popup = popuplib.easymenu("sourcerpg_admin", "_popup_userid", popup.mainCallback)
        self.popup.settitle("=== %s Admin ===" % sourcerpg.prefix)
        
    def __del__(self):
        """ Default deconstructor. clear the initializations we creating in __init__ """
        popuplib.delete("sourcerpg_admin")
        
    def addOption(self, value, text):
        """
        This method acts as a wrapper for the easymenu addoption function.
        It allows us to add an option to the admin menu which will be used
        as a callback. The only difference is the fact that value must either be
        a function or another popup
        
        @PARAM value - either a function or another popup name to execute when it is chosen
        @PARAM text - the text which appears on the menu
        """
        self.popup.addoption(value, text)
        
    def mainCommand(self, userid, args):
        """
        This method is executed when a player successfully calls the chat command.
        This will only open if a player is authorized, so it's safe to not
        check for authorization.
        
        @PARAM userid - the userid who issued the command
        @PARAM args - any additional arguments after the command
        """
        self.popup.send(userid)
    
    def clientAddXp(self, userid, args):
        """
        This method is a client command callback when an admin runs the command
        rpgaddxp <steamid> <amount>. This will be generally called from the
        custom menu with the escape input box. Execute the addition of the experience
        
        @PARAM userid - the admin's id who executed the command
        @PARAM args - any additional arguments after the command
        """
        steamid, amount = args
        amount = int(amount)
        popup.addXp(userid, amount, "sourcerpg_addxp_player%s" % steamid)
        
    def clientAddLevels(self, userid, args):
        """
        This method is a client command callback when an admin runs the command
        rpgaddlevels <steamid> <amount>. This will be generally called from the
        custom menu with the escape input box. Execute the addition of the levels
        
        @PARAM userid - the admin's id who executed the command
        @PARAM args - any additional arguments after the command
        """
        steamid, amount = args
        amount = int(amount)
        popup.addLevels(userid, amount, "sourcerpg_addlevel_player%s" % steamid)
    
    def clientAddCredits(self, userid, args):
        """
        This method is a client command callback when an admin runs the command
        rpgaddcredits <steamid> <amount>. This will be generally called from the
        custom menu with the escape input box. Execute the addition of the credits
        
        @PARAM userid - the admin's id who executed the command
        @PARAM args - any additional arguments after the command
        """
        steamid, amount = args
        amount = int(amount)
        popup.addCredits(userid, amount, "sourcerpg_addcredit_player%s" % steamid)
    
    @staticmethod
    def failCommand(userid, args):
        """
        Executed when a player attempts to access the administrative menu
        but is not authorized to do so. Send them a message telling them why
        they were not permitted to open the menu
        
        @PARAM userid - the id of the user who attempted to gain access
        @PARAM args - any additional arguments after the command
        """
        tell(userid, 'not authed')

class PopupCallbacks(object):
    """
    This class allows us to keep all the popuplib callback functions in one
    place.
    """
    @staticmethod
    def mainCallback(userid, choice, popupid):
        """
        Executed when an option is selected from the main admin menu option.
        
        @PARAM userid - the user who chose the option
        @PARAM choice - the choice that the user selected
        @PARAM popupid - the name of the popup the user just chose an option from
        """
        if isinstance(choice, str) and popuplib.exists(choice):
            popuplib.send(choice, userid)
        elif callable(choice):
            choice(userid)
        else:
            raise ValueError, "Expected a function or popup for sourcerpg_admin, received type %s" % repr(choice)
            
    def buildOnlinePlayers(self, userid):
        """
        Build a popup with all the current online players.
        
        @PARAM userid - the if of the user who to send the popup to
        """
        onlineMenu = popuplib.easymenu("sourcerpg_onlineplayers", "_popup_choice", self.chosenPlayer)
        onlineMenu.settitle("=== %s Admin ===" % sourcerpg.prefix)
        for player in sourcerpg.players:
            onlineMenu.addoption(player.steamid, player.name)
        onlineMenu.submenu(10, 'sourcerpg_admin')
        onlineMenu.c_exitformat = "0. Back"
        onlineMenu.send(userid)
    
    def buildOfflinePlayers(self, userid):
        """
        Build a popup with all the current offline players.
        
        @PARAM userid - the if of the user who to send the popup to
        """
        offlineMenu = popuplib.easymenu("sourcerpg_offlineplayers", "_popup_choice", self.chosenPlayer)
        offlineMenu.settitle("=== %s Admin ===" % sourcerpg.prefix)
        
        sourcerpg.database.execute("SELECT steamid,name FROM Player ORDER BY name ASC")
        for steamid, name in sourcerpg.database.cursor.fetchall():
            offlineMenu.addoption(steamid, name)
            
        offlineMenu.submenu(10, 'sourcerpg_admin')
        offlineMenu.c_exitformat = "0. Back"
        offlineMenu.send(userid)
    
    def buildSkills(self, userid):
        """
        This method builds all the current skills and tells the user if they're
        enabled or disabled. It gives the option for admins to dynamically
        add / remove skills
        
        @PARAM userid - the user who we should send the popup to
        """
        skillPopup = popuplib.easymenu("sourcerpg_skillmenu", "_popup_choice", self.toggleSkill)
        skillPopup.settitle("=== %s Toggle Skills ===" % sourcerpg.prefix)
        for skill in filter(lambda x: x.find(".") == -1, os.listdir( os.path.join(es.getAddonPath(sourcerpg.info.basename), 'skills') ) ):
            status = "[ENABLED]" if skill in sourcerpg.skills else "[DISABLED]"
            skillPopup.addoption(skill, skill + " " + status)
        skillPopup.submenu(10, 'sourcerpg_admin')
        skillPopup.c_exitformat = "0. Back"
        skillPopup.send(userid)
        
    def toggleSkill(self, userid, choice, popupid):
        """
        This callback function allows us to toggle on / off any active / inactive
        skills
        
        @PARAM userid - the player who toggled the skills
        @PARAM choice - the name of the skill to toggle
        @PARAM popupid - the name of the popup used to access this method
        """
        tokens = {}
        tokens['skill'] = choice
        if choice in sourcerpg.skills:
            tokens['status'] = "disabled"
            es.unload("%s/skills/%s" % (sourcerpg.info.basename, choice) )
        else:
            tokens['status'] = "enabled"
            es.load("%s/skills/%s" % (sourcerpg.info.basename, choice) )
        gamethread.delayed(0, self.buildSkills, userid)
        tell(userid, 'skill toggled', tokens)
    
    def buildAddons(self, userid):
        """
        This method builds all the current addons and tells the user if they're
        enabled or disabled. It gives the option for admins to dynamically
        add / remove addons
        
        @PARAM userid - the user who we should send the popup to
        """
        addonPopup = popuplib.easymenu("sourcerpg_addonmenu", "_popup_choice", self.toggleAddon)
        addonPopup.settitle("=== %s Toggle Skills ===" % sourcerpg.prefix)
        for addon in filter(lambda x: x.find(".") == -1, os.listdir( os.path.join(es.getAddonPath(sourcerpg.info.basename), 'addons') ) ):
            status = "[ENABLED]" if addon in sourcerpg.addons else "[DISABLED]"
            addonPopup.addoption(addon, addon + " " + status)
        addonPopup.submenu(10, 'sourcerpg_admin')
        addonPopup.c_exitformat = "0. Back"
        addonPopup.send(userid)
        
    def toggleAddon(self, userid, choice, popupid):
        """
        This callback function allows us to toggle on / off any active / inactive
        addons
        
        @PARAM userid - the player who toggled the addons
        @PARAM choice - the name of the skill to toggle
        @PARAM popupid - the name of the popup used to access this method
        """
        tokens = {}
        tokens['addon'] = choice
        if choice in sourcerpg.addons:
            tokens['status'] = "disabled"
            es.unload("%s/addons/%s" % (sourcerpg.info.basename, choice) )
        else:
            tokens['status'] = "enabled"
            es.load("%s/addons/%s" % (sourcerpg.info.basename, choice) )
        gamethread.delayed(0, self.buildAddons, userid)
        tell(userid, 'addon toggled', tokens)
        
    def chosenPlayer(self, userid, choice, popupid):
        """
        This method builds a menu about a certain player. It will detail the
        simple attributes of the player then sets out certain commands we can
        execute regarding the user. Finally send the menu
        
        @PARAM userid - the id of the user we will send the menu to
        @PARAM choice - the steamid of the user the popup will represent
        @PARAM popupid - the name of the popup which was used to access this method
        """
        choice  = choice[choice.lower().find("steam"):]
        details = self.getDetails(choice)
        playerMenu = popuplib.create("sourcerpg_player%s" % choice)
        playerMenu.addline("=== %s Admin (%s) ===" % (sourcerpg.prefix, details['name']) )
        playerMenu.addline("-" * 30)
        playerMenu.addline("Status: %s" % {True: "Online", False: "Offline"}[self.isOnline(choice)])
        playerMenu.addline("Level: %s" % details['level'])
        playerMenu.addline("XP: %s/%s" % (details['xp'], details['level'] * int(sourcerpg.xpIncrement) + int(sourcerpg.startXp) ) )
        playerMenu.addline(" ")
        playerMenu.addline("->1. Give Experience")
        playerMenu.addline("->2. Give Levels")
        playerMenu.addline("->3. Give Credits")
        playerMenu.addline("->4. Upgrade a skill")
        playerMenu.addline("->5. Downgrade a skill")
        playerMenu.addline("->6. Max all skills")
        playerMenu.addline(" ")
        playerMenu.addline("->8. Reset Skills")
        playerMenu.addline("-" * 30)
        playerMenu.addline("0. Back")
        playerMenu.menuselectfb = self.executePlayerOption
        playerMenu.submenu(10, popupid)
        playerMenu.send(userid)
        
    def executePlayerOption(self, userid, choice, popupid):
        target = popupid.replace("sourcerpg_player", "")
        if choice == 1:
            """ Give experience """
            popupName = "sourcerpg_addxp_player%s" % target
            self.createAmountMenu(popupName, self.addXp, popupid).send(userid)
            
        elif choice == 2:
            """ Give levels """
            popupName = "sourcerpg_addlevel_player%s" % target
            self.createAmountMenu(popupName, self.addLevels, popupid).send(userid)
            
        elif choice == 3:
            """ Give credits """
            popupName = "sourcerpg_addcredit_player%s" % target
            self.createAmountMenu(popupName, self.addCredits, popupid).send(userid)                
            
        elif choice == 4:
            """ Upgrade a skill """
            self.buildPlayerSkillsMenu("sourcerpg_upgrade_player%s" % target, target, self.upgradeSkill, popupid, True).send(userid)
            
        elif choice == 5:
            """ Downgrade a skill """
            self.buildPlayerSkillsMenu("sourcerpg_downgrade_player%s" % target, target, self.downgradeSkill, popupid, False).send(userid)
            
        elif choice == 6:
            """ Max all skills """
            if self.isOnline(target):
                """
                Player is online, assign all levels to the player's PlayerObject
                instance 
                """
                userid = es.getuserid(target)
                for skill in sourcerpg.skills:
                    sourcerpg.players[userid][skill.name] = skill.maxLevel
                    es.event("initialize", "sourcerpg_skillupgrade")
                    es.event("setint",     "sourcerpg_skillupgrade", "userid", userid)
                    es.event("setint",     "sourcerpg_skillupgrade", "level", skill.maxLevel)
                    es.event("setint",     "sourcerpg_skillupgrade", "cost",  0)
                    es.event("setstring",  "sourcerpg_skillupgrade", "skill", skill.name)
                    es.event("fire",       "sourcerpg_skillupgrade")
            else:
                """
                The player is offline so ensure that all the new values are
                assigned
                """
                for skill in sourcerpg.skills:
                    sourcerpg.database.updateSkillForPlayer(target, skill.rowid, skill.maxLevel)
            tell(userid, 'maxed skills')
            
        elif choice == 8:
            """ Reset skills """
            if self.isOnline(target):
                player = es.getuserid(target)
                sourcerpg.players[player].resetSkills()
            else:
                """
                Because the player is offline, the next time they join .
                they'll be added to the database
                """
                sourcerpg.database.execute("DELETE FROM playerstats WHERE steamid='" + target + "'")
                sourcerpg.database.execute("DELETE FROM playerkills WHERE steamid='" + target + "'")
        
    @staticmethod
    def buildPlayerSkillsMenu(popupName, target, function, returnPopup, upgrade=True):
        """
        This function builds the skills for a player and allows us to
        choose an option from the menu calling back as the function
        
        @PARAM name - the name of the popup
        @PARAM target - the steamid of the players skills you'd like to show
        @PARAM function - the function to execute as a callback
        @PARAM returnPopup - the popup which will be used to go back to
        @RETRURN Popup_popup instance
        """
        popupInstance = popuplib.easymenu(popupName, "_popup_choice", function)
        popupInstance.settitle("=== %s Admin ===" % sourcerpg.prefix)
        """ If the target is online we can use the PlayerObject instance """
        if popup.isOnline(target):
            userid = es.getuserid(target)
            for skill in sourcerpg.skills:
                level = sourcerpg.players[userid][skill.name]
                if upgrade:
                    if level >= skill.maxLevel:
                        popupInstance.addoption(None, skill.name + " (MAXED)", False )
                    else:
                        popupInstance.addoption(skill.name, skill.name + "(" + str(level) + " => " + str(level + 1) + ")" )
                else:
                    if level <= 0:
                        popupInstance.addoption(None, skill.name + " (MINIMUM)", False)
                    else:
                        popupInstance.addoption(skill.name, skill.name + "(" + str(level) + " => " + str(level - 1) + ")" )
        else:
            """ Otherwise we have to get the skill level directly from the database """
            for skill in sourcerpg.skills:
                level = sourcerpg.database.getSkillLevel(target, skill.name)
                if upgrade:
                    if level >= skill.maxLevel:
                        popupInstance.addoption(None, skill.name + " (MAXED)", False )
                    else:
                        popupInstance.addoption(skill.name, skill.name + "(" + str(level) + " => " + str(level + 1) + ")" )
                else:
                    if level <= 0:
                        popupInstance.addoption(None, skill.name + " (MINIMUM)", False)
                    else:
                        popupInstance.addoption(skill.name, skill.name + "(" + str(level) + " => " + str(level - 1) + ")" )
        popupInstance.submenu(10, returnPopup)
        return popupInstance
        
    @staticmethod
    def createAmountMenu(name, function, returnPopup):
        """
        This menu allows us to create a new menu which will represent certain
        amounts
        
        @PARAM name - the name of the popup
        @PARAM function - the function to execute as a callback
        @PARAM returnPopup - the popup which will be used to go back to
        @RETRURN Popup_popup instance
        """
        amountMenu = popuplib.easymenu(name, "_popup_choice", function)
        amountMenu.settitle("=== %s Admin ===" % sourcerpg.prefix)
        amountMenu.addoption(1,       "1")
        amountMenu.addoption(10,      "10")
        amountMenu.addoption(100,     "100")
        amountMenu.addoption(1000,    "1,000")
        amountMenu.addoption(5000,    "5,000")
        amountMenu.addoption(10000,   "10,000")
        amountMenu.addoption(100000,  "100,000")
        amountMenu.addoption(1000000, "1,000,000")
        amountMenu.addoption("custom","Custom")
        amountMenu.submenu(10, returnPopup)
        amountMenu.c_exitformat = "0. Back"
        return amountMenu
        
    def upgradeSkill(self, userid, choice, popupid):
        """
        This method increments a skill at the admin's choice by one.
        
        @PARAM userid - the admin who decremented the skill
        @PARAM choice - the skill to decrement
        @PARAM popupid - the name of the popup used to get here
        """
        target = popupid.replace("sourcerpg_upgrade_player", "")
        if self.isOnline(target):
            sourcerpg.checkSkillForUpgrading(es.getuserid(target), choice, None, False, False)
        else:
            """ Player is offline, make sure that you don't go over the max level """
            level = sourcerpg.database.getSkillLevel(target, choice)
            skill = sourcerpg.skills[choice]
            if level < skill.maxLevel:
                sourcerpg.database.increment('playerskills', 'steamid', target, {choice:1})
        #self.chosenPlayer(userid, target, 'sourcerpg_admin')
        self.buildPlayerSkillsMenu("sourcerpg_upgrade_player%s" % target, target, self.upgradeSkill, "sourcerpg_player%s" % target, True).send(userid)
    
    def downgradeSkill(self, userid, choice, popupid):
        """
        This method decrements a skill at the admin's choice by one.
        
        @PARAM userid - the admin who decremented the skill
        @PARAM choice - the skill to decrement
        @PARAM popupid - the name of the popup used to get here
        """
        target = popupid.replace("sourcerpg_downgrade_player", "")
        if self.isOnline(target):
            sourcerpg.checkSkillForSelling(es.getuserid(target), choice, None, False, False)
        else:
            """ Player is offline, makes sure we don't go below 0 """
            level = sourcerpg.database.getSkillLevel(target, choice)
            if level > 0:
                sourcerpg.database.increment('playerskills', 'steamid', target, {choice:-1})
        #self.chosenPlayer(userid, target, 'sourcerpg_admin')
        self.buildPlayerSkillsMenu("sourcerpg_downgrade_player%s" % target, target, self.downgradeSkill, "sourcerpg_player%s" % target, False).send(userid)
        
    @staticmethod
    def addXp(userid, choice, popupid):
        """
        This method adds a cetain amount of experience to a player. If the player
        is online when we shall execute the method to add the experience; otherwise
        we have to query the experience levels and credits and simulate the 
        main thesis behind incrementing the experience and testing for levels up
        only with values from the database rather than throught the PlayerObject
        instance.
        
        @PARAM userid - the admin who gave the experience
        @PARAM choice - the amount of experience to award
        @PARAM popupid - the id of the popup which was used to give the player experience
        """
        target = popupid.replace("sourcerpg_addxp_player", "")
        if isinstance(choice, str):
            if choice.isdigit():
                choice = int(choice)
        if isinstance(choice, int):
            tokens = {}
            tokens['amount'] = str(choice)
            if popup.isOnline(target):
                player = es.getuserid(target)
                sourcerpg.players[player].addXp(choice, 'being liked by the admin')
                tokens['name'] = sourcerpg.players[player]['name']
            else:
                xp, level, credits, name = sourcerpg.database.query('playerstats', 'steamid', target, ('xp', 'level', 'credits', 'name') )
                xp += choice
                amountOfLevels = 0
                nextXpAmount = level * int(sourcerpg.xpIncrement) + int(sourcerpg.startXp)
                while xp > nextXpAmount:
                    xp -= nextXpAmount
                    amountOfLevels += 1
                    nextXpAmount += int(sourcerpg.xpIncrement)
                if amountOfLevels:
                    sourcerpg.database.update('playerstats', 'steamid', target, 
                                              {'xp'      : xp, 
                                               'level'   : level + amountOfLevels,
                                               'credits' : credits + amountOfLevels * int(sourcerpg.creditsReceived)
                                              } )
                else:
                    sourcerpg.database.update('playerstats', 'steamid', target, {'xp' : xp} )
                
                tokens['name'] = name
            tell(userid, 'add xp', tokens)
            popuplib.send(popupid, userid)
        else:
            tell(userid, 'escape')
            es.escinputbox(30, userid, '=== %s Add Xp ===' % sourcerpg.prefix, 
                'Enter the amount' , 'rpgaddxp" "%s' % target)
        
    @staticmethod
    def addLevels(userid, choice, popupid):
        """
        This method adds a cetain amount of levels to a player by a given
        steamid. If the player is currently online then add the levels by
        the sourcerpg player object; otherwise query the database and update
        it via that.
        
        @PARAM userid - the admin who gave the levels
        @PARAM choice - the amount of levels to give
        @PARAM popupid - the id of the popup which was used to give the player levels
        """
        target = popupid.replace("sourcerpg_addlevel_player", "")
        tokens = {}
        tokens['amount'] = str(choice)
        if isinstance(choice, str):
            if choice.isdigit():
                choice = int(choice)
        if isinstance(choice, int):
            if popup.isOnline(target):
                player = es.getuserid(target)
                sourcerpg.players[player].addLevel(choice)
                tokens['name'] = sourcerpg.players[player]['name']
            else:
                sourcerpg.database.increment('playerstats', 'steamid', target, {'level' : choice})
                tokens['name'] = sourcerpg.database.query('playerstats', 'steamid', target, 'name')
            tell(userid, 'add levels', tokens)
            popuplib.send(popupid, userid)
        else:
            tell(userid, 'escape')
            es.escinputbox(30, userid, '=== %s Add Xp ===' % sourcerpg.prefix,
                'Enter the amount' , 'rpgaddlevels" "%s' % target)
        
    @staticmethod
    def addCredits(userid, choice, popupid):
        """
        This method adds a cetain amount of credits to a player by a given
        steamid. If the player is currently online then add the credits by
        the sourcerpg player object; otherwise query the database and update
        it via that.
        
        @PARAM userid - the admin who gave the credits
        @PARAM choice - the amount of credits to give
        @PARAM popupid - the id of the popup which was used to give the player credits
        """
        target = popupid.replace("sourcerpg_addcredit_player", "")
        tokens = {}
        tokens['amount'] = str(choice)
        if isinstance(choice, str):
            if choice.isdigit():
                choice = int(choice)
        if isinstance(choice, int):
            if popup.isOnline(target):
                player = es.getuserid(target)
                sourcerpg.players[player]['credits'] += choice
                tokens['name'] = sourcerpg.players[player]['name']
            else:
                sourcerpg.database.increment('playerstats', 'steamid', target, {'credits' : choice})
                tokens['name'] = sourcerpg.database.query('playerstats', 'steamid', target, 'name')
            tell(userid, 'add credits', tokens)
            popuplib.send(popupid, userid)
        else:
            tell(userid, 'escape')
            es.escinputbox(30, userid, '=== %s Add Xp ===' % sourcerpg.prefix,
                'Enter the amount' , 'rpgaddcredits" "%s' % target)
    
    @staticmethod
    def confirmation(self, userid, choice, popupid):
        """
        The admin has chosen to clear the database so we shall first kill
        all players then clear the database. To ensure that all the values reset
        we need to restart the round.
        
        @PARAM userid - the admin who chose to delete the database
        @PARAM choice - whether or not the admin has confirmed the removal process
        @PARAM popupid - the id of the popup which was used to confirm the process
        """
        if choice:
            for player in es.getUseridList():
                es.sexec(player, 'kill')
                tell(player, 'database deleting')
            sourcerpg.database.clear()
            es.server.queuecmd('mp_restartround 1')
    
    @staticmethod
    def getDetails(steamid ):
        """
        This method returns the details of a user. It will either use
        the SourceRPG PlayerObject if the player is online, otherwise it'll
        query results from the database directly
        
        @RETRUN dictionary - strings containing the values of the objects
        """
        values = {}
        if popup.isOnline(steamid):
            """ The player is online, query PlayerObject instance """
            userid = es.getuserid()
            return sourcerpg.players[userid] 
        """ The player is offline, query database """


        """ Query the stats of the player """
        query = "SELECT name,level,xp,credits FROM playerstats WHERE steamid='%s'" % steamid
        print "Query: %s" % query
        sourcerpg.database.execute(query)
        values['name'], values['level'], values['xp'], values['credits'] = sourcerpg.database.cursor.fetchone()
        
        """ Query the levels of the current loaded skills """
        for skill in sourcerpg.skills:
            level = sourcerpg.database.getSkillLevel(steamid, skill.name)
            if level is None:
                level = 0
            values[skill.name] = level 
            
        """ Return a dictionary object which imitats a PlayerObect reference """
        return values
    
    @staticmethod
    def isOnline(steamid):
        """
        This method returns if a player provided by the steamid parameter is
        currently online.
        
        @PARAM steamid - the steamid of the player to test
        @RETURN boolean - whether or not the player is currently online
        """
        return bool( es.getuserid( steamid ) )

""" Create the singleton instances """
popup  = PopupCallbacks()
admin  = AdminManager()
addonName = "sourcerpg_admin"

def load():
    """
    Executed when the script loads. Ensure that the admin menu is built and
    all of the options are either other popups or functions we can call.
    """
    
    sourcerpg.addons.addAddon(addonName)
    
    cmdlib.registerSayCommand("rpg_admin", admin.mainCommand,
                              "The command to open the admin menu",
                              "sourcerpg_admin", "ADMIN", admin.failCommand)
    cmdlib.registerSayCommand("rpgadmin", admin.mainCommand,
                              "The command to open the admin menu",
                              "sourcerpg_admin", "ADMIN", admin.failCommand)
                              
    """ Register the client commands so we can use escape boxes """         
    cmdlib.registerClientCommand("rpgaddxp", admin.clientAddXp,
                                 "The command to add experience to a target",
                                 "sourcerpg_admin", "ADMIN", admin.failCommand)
    cmdlib.registerClientCommand("rpgaddlevels", admin.clientAddLevels,
                                 "The command to add levels to a target",
                                 "sourcerpg_admin", "ADMIN", admin.failCommand)
    cmdlib.registerClientCommand("rpgaddcredits", admin.clientAddCredits,
                                 "The command to add credits to a target",
                                 "sourcerpg_admin", "ADMIN", admin.failCommand)
                              
    """ Create the confirmation menu """
    confirmation = popuplib.easymenu("sourcerpg_confirmDeleteDatabase", "_popup_choice", popup.confirmation)
    confirmation.settitle("=== %s Confirmation ===" % sourcerpg.prefix)
    confirmation.setdescription("""\
!!! WARNING !!!
This is an irriversable effect! Once
you remove this database, you cannot
get it back. All skills / levels will
be destroyed. Are you sure you want
to continue?""")
    confirmation.addoption(True, "Yes")
    confirmation.addoption(False, "No")
                              
    """ Build the admin menu """
    admin.addOption( popup.buildOnlinePlayers,  "Online Players")
    admin.addOption( popup.buildOfflinePlayers, "Offline Players (Warning, may lag)" )
    admin.addOption( popup.buildSkills,   "Load/Unload Skills" )
    admin.addOption( popup.buildAddons,   "Load/Unload Addons" )
    admin.addOption( "sourcerpg_confirmDeleteDatabase",  "Delete Database" )
                              
def unload():
    """
    Executed when the script unloads. Manually remove all instance
    of the singletons so the deconstructor is called on each one
    """
    sourcerpg.addons.removeAddon(addonName)
    
    del globals()['admin']
    del globals()['popup']
    if popuplib.exists("sourcerpg_confirmDeleteDatabase"):
        popuplib.delete("sourcerpg_confirmDeleteDatabase")
    
    cmdlib.unregisterSayCommand("rpg_admin")
    cmdlib.unregisterSayCommand("rpgadmin")
    cmdlib.unregisterClientCommand("rpgaddxp")
    cmdlib.unregisterClientCommand("rpgaddlevels")
    cmdlib.unregisterClientCommand("rpgaddcredits")
                              
def tell(userid, textIdentifier, tokens = {}):
    """
    A wrapper method which allows us to tell a player a message from the
    langlib strings dictionary without referenceing the prefix or the
    language each time.
    
    @PARAM userid - the user who to tell
    @PARAM textIdentifer - the key in the langlib strings dictionary which the text recides
    @PARAM OPTION tokens - any values to replace with the map within the string
    """
    if es.exists('userid', userid):
        lang    = playerlib.getPlayer(userid).get("lang")
        prefix  = "#green%s #default- #lightgreen" % sourcerpg.prefix
        message = text(textIdentifier, tokens, lang)
        es.tell(userid, '#multi', "%s%s" % (prefix, message ) )