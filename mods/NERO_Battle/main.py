import OpenNero
import NERO.client as client
import NERO.constants as constants
import module

def ModMain(mode = ""):
    module.getMod()  # initialize the NERO_Battle module.
    client.ClientMain()

def ModTick(dt):
    mod = module.getMod()
    if mod.environment:
        mod.environment.tick(dt)
    if OpenNero.getAppConfig().rendertype == 'null':
        return
    script_server = module.getServer()
    data = script_server.read_data()
    while data:
        module.parseInput(data.strip())
        data = script_server.read_data()

def Match(team0, team1):
    '''Run a single battle between two population files.'''
    mod = module.getMod()
    mod.load_team(team0, constants.OBJECT_TYPE_TEAM_0)
    mod.load_team(team1, constants.OBJECT_TYPE_TEAM_1)
    mod.set_speedup(100)
    OpenNero.enable_ai()
