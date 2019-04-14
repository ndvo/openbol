
# This will hold information about the screens during runtime. This stub is just a reminder of that.
screens = {}

# EXPLANATION ON THE SAVE FILE
# The save file is a dictionary consisted on three segments: the 'status' entry holds data from the user's team, the
# 'tournament' entry holds information on the tournament he is or previously was, while the 'match' entry holds information on the current match.
# The file is constantly updated in memory here, and is called g.save everywhere else. After every important
# occurance, it is pickled and saved in the external file 'save'.
# A new save will be called as
#
# gameSave(
#
# status = {'name': '', 'crest': '', 'fans': 0, 'level': 1,'available_crests':['snts', 'rlmd', 'bmnc'],'laurels':{'win':0,'tie':0,'lose':0,'3rd':0,'2nd':0,'1st':0,'premiere':0,'world':0}, 'milestones':{'profile': False, 'tutorial': False, '3rd': False, '2nd': False, '1st': False, 'premiere': False}, 'details': True},
#
# tournament = {'id': '', 'tries': 2, 'hand_size': 3, 'available_cards': [], 'selected_cards': [], 'teams': [{'name':'','result':''},{'name':'','result':''},{'name':'','result':''},{'name':'','result':''}] },
#
# match = {'opponent': '', 'play':0, 'action': 'strategy', 'score': [0,0], 'players': [{'position':'','status':'healthy'}, {'position':'','status':'healthy'}, {'position':'','status':'healthy'}, {'position':'','status':'healthy'}, {'position':'','status':'healthy'}, {'position':'','status':'healthy'}, {'position':'','status':'healthy'}, {'position':'','status':'healthy'}, {'position':'','status':'healthy'}, {'position':'','status':'healthy'}]
#
#  })
save = {}


# You can overwrite reading the save file for testing purposes. If it is set to None, then it reads the save file
# normally. If set to 'newbie' it will create a new save file. If set to 'pro', it will take a powerful team with
# everything unlocked.
debug_player =  None #'pro' #None #'newbie' #'pro'

# When the player has not selected a formation, we must place his men in default positions. This allows
# us to set how many men will be placed in each zone for formationless teams.
sans_formation = [4,4,2]


# CONSTANTS
# These are definitions to be used throught the game, including font sources, color components and the like.

COLOR_BLACK = (0,0,0,1)
COLOR_BLACK_ALPHA_50 = (0,0,0,0.5)
COLOR_BROWN = (0.56,0.64,0.35,1.0)
COLOR_BROWN_LIGHT = (0.22,0.46,0.03,1.0)
COLOR_BROWN_DARK = (0.24,0.31,0.16,1.0)
COLOR_GRAY_DARK = (0.4,0.4,0.4,1.0)
COLOR_PURPLE = (0.56,0.29,0.65,1.0)
COLOR_WHITE = (1,1,1,1)

FONT_MANDINGO = './data/fonts/MANDINGO.TTF'


# DATABASE
# This game doesn't need an advanced database. The necessary data are right here.

# The data from all opponent teams. The key is the team's name, as it is referenced in the app's code. The name is
# how it is outputed to the user. The origin is just for aesthetics reason. The def, mid and atk value refers to
# the strength of the team's zone.
opponents = { 'sloth':{'name':'sloths', 'origin':'orinoco', 'def':11, 'mid':7,'atk':9, 'league':'3rd'}, 'tapir':{'name':'tapirs', 'origin':'colombia', 'def':12, 'mid':7,'atk':8, 'league':'3rd'}, 'paca':{'name':'pacas', 'origin':'suriname', 'def':10, 'mid':9,'atk':8, 'league':'3rd'}, 'capybara':{'name':'pacas', 'origin':'pantanal', 'def':11, 'mid':9,'atk':7, 'league':'3rd'}, 'turtle':{'name':'turtles', 'origin':'bahia', 'def':13, 'mid':9,'atk':8, 'league':'2nd'}, 'opossum':{'name':'opossums', 'origin':'texas', 'def':9, 'mid':10,'atk':11, 'league':'2nd'}, 'toucan':{'name':'toucans', 'origin':'caribbean', 'def':15, 'mid':8,'atk':7, 'league':'2nd'}, 'condor':{'name':'condors', 'origin':'andes', 'def':8, 'mid':13,'atk':9, 'league':'2nd'}, 'wren':{'name':'wrens', 'origin':'bolivia', 'def':12, 'mid':13,'atk':8, 'league':'1st'}, 'lizard':{'name':'lizards', 'origin':'cerrado', 'def':14, 'mid':10,'atk':9, 'league':'1st'}, 'dolphin':{'name':'dolphins', 'origin':'amazon', 'def':14, 'mid':11,'atk':8, 'league':'1st'}, 'wolf':{'name':'maned wolves', 'origin':'parana', 'def':10, 'mid':12,'atk':11, 'league':'1st'}, 'otter':{'name':'giant otters', 'origin':'guyana', 'def':12, 'mid':15,'atk':9, 'league':'premiere'}, 'crocodile':{'name':'crocodiles', 'origin':'everglades', 'def':17, 'mid':8,'atk':11, 'league':'premiere'}, 'jaguar':{'name':'jaguars', 'origin':'yucatan', 'def':12, 'mid':10,'atk':14, 'league':'premiere'}, 'penguin':{'name':'penguins', 'origin':'antarctica', 'def':14, 'mid':11,'atk':11, 'league':'premiere'} } 

# The data from all formations. The key is the name as referenced in the app's code. The men indicates how many players
# may be placed in each zone (defense, midfield, attack) and the strength is the value for that zone.
formations = { 'sf-pyr': {'men': [2,3,5], 'strength': [8,6,10]}, 'sf-4231': {'men': [4,5,1], 'strength': [8,7,9]}, 'sf-433': {'men': [4,3,3], 'strength': [10,7,7]}, 'sf-libero': {'men': [5,3,2], 'strength': [12,7,5]}, 'sf-metodo': {'men': [2,5,3], 'strength': [8,8,8]}, 'sf-442': {'men': [4,4,2], 'strength': [10,8,6]}, 'sf-343': {'men': [3,4,3], 'strength': [7,9,8]}, 'sf-wm': {'men': [3,4,3], 'strength': [9,9,6]}, 'sf-352': {'men': [3,5,2], 'strength': [10,9,5]}, 'sf-kami': {'men': [1,6,3], 'strength': [4,10,10]}, 'sf-424': {'men': [4,2,4], 'strength': [9,4,11]}, 'sf-451': {'men': [4,5,1], 'strength': [9,12,3]} }

# The data from all tactics. The key is the name as referenced in the app's code. The strength is the value modifier for the zone. Keep in mind that effects that are conditioned to certain circumstances (such as the longball bonus that apllies only during counterattacks) will not be represented here. They are carefully coded in the calculate_zone_strength function of the mainScreen class or in the relevant places.
tactics = { 't-ball': {'strength': [0,2,0]}, 't-count': {'strength': [0,0,0]}, 't-long': {'strength': [0,0,0]}, 't-indiv': {'strength': [0,0,0]}, 't-set': {'strength': [0,0,2]}, 't-zone': {'strength': [2,0,0]}, 't-man': {'strength': [0,0,0]}, 't-for': {'strength': [0,0,0]}, 't-col': {'strength': [-1,-1,4]}, 't-runs': {'strength': [0,1,1]}, 't-direct': {'strength': [-2,2,2]}, 't-offside': {'strength': [0,0,0]} }


# must be reviewed
job_list = []
enforce_zones = True
#formation = [3,4,3] #stub
team = {'formation':[3,4,3], 'zone_attack':4, 'zone_midfield':10, 'zone_defense':12, 'hand':['mock','mock','mock','mock','mock','mock','mock','mock','mock','mock','mock','mock','mock','mock','mock','mock','mock','mock','mock','mock','mock','mock','mock']}
match = {'score_player':2,'score_opponent':2,'play':1}

next_team = None #Used to ease transition between screens

