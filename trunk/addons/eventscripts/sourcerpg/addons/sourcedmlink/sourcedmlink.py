import es

from sourcerpg import sourcerpg

addonName = "sourcedmlink"

def load():
    """
    Regiser the addon with the main sourcerpg addon container
    """
    sourcerpg.addons.addAddon(addonName)
    
def unload():
    """
    Unregister the addon with the main sourcerpg addon container
    """
    sourcerpg.addons.removeAddon(addonName)

def player_spawn(event_var):
    """
    Executed when a player spawns. Assign their maximum default health attribute
    to 51,300. This will make it look like a player has 100 health but they
    really don't. If the player has more health, then this value is added to
    by that amount rather than statically assigned to 100 + amount.
    
    @PARAM event_var - automatic passed event instance
    """
    if not es.getplayerprop(event_var['userid'], 'CBasePlayer.pl.deadflag'):
        sourcerpg.players[event_var['userid']]['baseHealth'] = 51300