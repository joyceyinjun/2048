import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

DIRECTIONS = ['UP', 'RIGHT', 'DOWN', 'LEFT']
EXIT_STRING = 'Q'
UNDO_STRING = 'U'

KEY_MAPPING = {
    0: {
        'UP': 'UP', 'DOWN': 'DOWN',
        'LEFT': 'LEFT', 'RIGHT': 'RIGHT',
        'U': 'U'
    },
    1: {
        'W': 'UP', 'S': 'DOWN',
        'A': 'LEFT', 'D': 'RIGHT',
        'U': 'U'
    }
}

PLAYER_NAMES = ['Mozart', 'DongDong', 'JunJun']


#############################
#        style section
#############################
WINDOW_X, WINDOW_Y = 1120, 120
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (WINDOW_X, WINDOW_Y)
WINDOW_SIZE = (768, 768)
EDGE_PERCENTAGE = 0.16

FONT = 'papyrus'
BLOCK_FONT, BLOCK_FONT_SIZE = 'papyrus', 60
STATUS_FONT_SIZE = 24
MSG_FONT_SIZE = 32

# color scheme
SCREEN_COLOR = (250, 248, 239)
BORDER_COLOR = (187, 173, 160)
BORDER_WIDTH = 16
EMPTY_BLOCK_COLOR = (205, 193, 180)
# block color, relative font size, font color
BLOCK_SETUP = {
    1: ((119, 110, 101), 1, (238, 228, 218)),
    2: ((119, 110, 101), 1, (237, 224, 200)),
    4: ((249, 246, 242), 1, (242, 177, 120)),
    8: ((249, 246, 242), 1, (245, 149, 99)),
    16: ((249, 246, 242), 1, (246, 124, 95)),
    32: ((249, 246, 242), 1, (246, 94, 59)),
    64: ((249, 246, 242), 1, (237, 207, 114)),
    128: ((249, 246, 242), .8, (237, 204, 97)),
    256: ((249, 246, 242), .8, (237, 200, 80)),
    512: ((249, 246, 242), .8, (237, 197, 63)),
    1024: ((249, 246, 242), .7, (237, 193, 46)),
    2048: ((249, 246, 242), .7, (237, 193, 46)),
    4096: ((249, 246, 242), .7, (237, 193, 46)),
    8192: ((249, 246, 242), .7, (237, 193, 46)),
    16384: ((249, 246, 242), .6, (237, 193, 46)),
}
MSG_FONT_COLOR = (61, 97, 124)
ACTIVE_FONT_COLOR = (124, 97, 61)
