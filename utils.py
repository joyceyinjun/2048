import os
import random
import sys
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

WINDOW_X, WINDOW_Y = 1120, 120
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (WINDOW_X, WINDOW_Y)
WINDOW_SIZE = (768, 768)
SCREEN_COLOR = (250, 248, 239)
EDGE_PERCENTAGE = 0.16
BORDER_COLOR = (187, 173, 160)
BORDER_WIDTH = 16

DIRECTIONS = ['UP', 'DOWN', 'LEFT', 'RIGHT']
EXIT_STRING = 'Q'

EMPTY_BLOCK_COLOR = (205, 193, 180)
# block color, font size
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

# pygame.init()
# FONTS = pygame.font.get_fonts()
FONT, BLOCK_FONT_SIZE = 'papyrus', 60
FONT_COLOR = (61, 97, 124)
STATUS_FONT_SIZE = 18
MSG_FONT_SIZE = 32


class Block:
    """
    BLOCK
    """

    def __init__(self, xValue):
        self.value = xValue
        self.font_color = BLOCK_SETUP[self.value][0]
        self.font_size = int(BLOCK_SETUP[self.value][1] * BLOCK_FONT_SIZE)
        self.block_color = BLOCK_SETUP[self.value][2]

    def __str__(self):
        return '<Block {}>'.format(self.value)

    def __repr__(self):
        return '<Block {}>'.format(self.value)


class Board:
    """
    BOARD
    """

    def __init__(self, xNx, xNy):
        assert xNx == xNy, "Value Error in board init"
        self.Nx = xNx
        self.Ny = xNy
        self.isEmpty = True
        self.occupied = {}
        self.unoccupied = [(x + 1, y + 1) for x in range(self.Nx) for y in range(self.Ny)]

    def clearBoard(self):
        self.occupied = {}
        self.isEmpty = True

    def getTotalScore(self):
        total_score = 0
        for location in self.occupied.keys():
            total_score += self.occupied[location].value
        return total_score

    def isOccupied(self, xX, xY):
        if self.isEmpty:
            return False
        return (xX, xY) in self.occupiedPair.keys()

    def occupy(self, xX, xY, xBlock):
        self.occupied[(xX, xY)] = xBlock
        self.isEmpty = False
        self.unoccupied = [z for z in self.unoccupied if z != (xX, xY)]

    def release(self, xX, xY):
        if (xX, xY) in self.occupied.keys():
            del self.occupied[(xX, xY)]
            self.unoccupied.append((xX, xY))

    def populate(self, xValue=1):
        if len(self.unoccupied) == 0:
            return False
        block = Block(xValue)
        i = random.randint(0, len(self.unoccupied) - 1)
        x, y = self.unoccupied[i]
        self.occupy(x, y, block)
        return True

    def rotate(self, xTimes):
        assert xTimes in [1, 2, 3], "Value Error in rotation"

        def rotateXY(xLoc, yLoc, zTimes):
            for i in range(zTimes):
                xLoc, yLoc = self.Nx + 1 - yLoc, xLoc
            return xLoc, yLoc

        unoccupied_updated = []
        for x, y in self.unoccupied:
            x, y = rotateXY(x, y, xTimes)
            unoccupied_updated.append((x, y))
        self.unoccupied = unoccupied_updated
        occupied_updated = {}
        for x, y in self.occupied.keys():
            value = self.occupied[(x, y)].value
            x, y = rotateXY(x, y, xTimes)
            occupied_updated[(x, y)] = Block(value)
        self.occupied = occupied_updated

    def collapse(self, xMove=True):
        def collapseList(xList):
            input_size = len(xList)
            flag_movement = False
            shredded_list = [z for z in xList if z > 0]
            if shredded_list + [0] * (input_size - len(shredded_list)) != xList:
                flag_movement = True

            i = 0
            while i < len(shredded_list) - 1:
                if shredded_list[i] == shredded_list[i + 1]:
                    shredded_list[i] *= 2
                    shredded_list = shredded_list[:i + 1] + shredded_list[i + 2:]
                    flag_movement = True
                i += 1
            output = shredded_list + [0] * (input_size - len(shredded_list))
            return output, flag_movement

        board_movement = False
        for xLoc in range(self.Nx):
            x = xLoc + 1
            input_list = []
            for yLoc in range(self.Ny):
                y = yLoc + 1
                if (x, y) in self.occupied.keys():
                    input_list.append(self.occupied[(x, y)].value)
                else:
                    input_list.append(0)
            output_list, row_movement = collapseList(input_list)

            board_movement |= row_movement

            if row_movement and xMove:
                for yLoc in range(self.Ny):
                    y = yLoc + 1
                    if (x, y) in self.occupied.keys():
                        self.release(x, y)
                    if output_list[yLoc] > 0:
                        self.occupy(x, y, Block(output_list[yLoc]))

        return board_movement

    def collapseTo(self, xDirection, xMove=True):
        assert xDirection in ['UP', 'DOWN', 'LEFT', 'RIGHT'], \
            "Value Error in collapseTo"
        if xDirection == 'LEFT':
            self.rotate(1)
        elif xDirection == 'DOWN':
            self.rotate(2)
        elif xDirection == 'RIGHT':
            self.rotate(3)

        board_movement = self.collapse(xMove)

        if xDirection == 'LEFT':
            self.rotate(3)
        elif xDirection == 'DOWN':
            self.rotate(2)
        elif xDirection == 'RIGHT':
            self.rotate(1)

        return board_movement

    def isAlive(self, xReturnMoves=False):
        availableMoves = []
        for direction in DIRECTIONS:
            if self.collapseTo(direction, xMove=False):
                if not xReturnMoves:
                    return True
                availableMoves.append(direction)
        if not xReturnMoves:
            return False
        return availableMoves

    def __str__(self):
        if self.isEmpty:
            return '<Board Empty>'
        ans = '<Board '
        for x, y in self.occupied.keys():
            ans += '[{} at ({},{})], '.format(self.occupied[(x, y)], x, y)
        ans = ans[:-2] + '>'
        return ans


class Screen:
    """
    SCREEN
    """

    def __init__(self, xWindowSize=WINDOW_SIZE, xFullscreen=False):
        import pygame
        pygame.init()
        self.pygame = pygame
        self.screen_color = SCREEN_COLOR

        self.icon = self.pygame.image.load('icon.jpg')
        self.pygame.display.set_icon(self.icon)
        self.caption = 'Bebop Agora'
        self.pygame.display.set_caption(self.caption)
        if xFullscreen:
            self.surface = self.pygame.display.set_mode((0, 0), self.pygame.FULLSCREEN)
        else:
            self.surface = self.pygame.display.set_mode(xWindowSize)

        self.width = self.surface.get_width()
        self.height = self.surface.get_height()

        self.exitString = EXIT_STRING

    def clearScreen(self, xDelay=0):
        self.surface.fill(self.screen_color)
        self.pygame.time.wait(xDelay)
        self.pygame.display.flip()

    def displayMessage(self, xMessage, xFont, xFontColor, xFontSize, xCenter, yCenter):
        font_obj = self.pygame.font.SysFont(xFont, xFontSize)
        text = font_obj.render(xMessage, True, xFontColor)
        text_rect = text.get_rect(center=(xCenter, yCenter))
        self.surface.blit(text, text_rect)

    def getKey(self):
        while True:
            event = self.pygame.event.poll()
            if event.type == self.pygame.QUIT:
                return self.exitString
            elif event.type == self.pygame.KEYDOWN:
                return self.pygame.key.name(event.key).upper()


class BoardDisplay:
    """
    BOARDSURFACE
    """

    def __init__(self, xScreen, xBoard):

        self.screen = xScreen
        self.width = self.screen.surface.get_width()
        self.height = self.screen.surface.get_height()

        self.edge_percentage = EDGE_PERCENTAGE

        self.board = xBoard
        self.Nx, self.Ny = None, None
        self.side_length = None
        self.edge_x, self.edge_y = None, None

    def drawRectangle(self, xLoc, yLoc, xWidth, xHeight, xColor=(255, 255, 255), xBorderWidth=1):
        self.screen.pygame.draw.rect(self.screen.surface, xColor, (xLoc, yLoc, xWidth, xHeight), xBorderWidth)

    def displayBlock(self, xLoc, yLoc, xBlock):
        left = self.edge_x + (xLoc - 1) * self.side_length + BORDER_WIDTH / 2
        top = self.edge_y + (yLoc - 1) * self.side_length + BORDER_WIDTH / 2
        block_side_length = self.side_length - BORDER_WIDTH

        self.drawRectangle(
            xLoc=left,
            yLoc=top,
            xWidth=block_side_length,
            xHeight=block_side_length,
            xColor=xBlock.block_color,
            xBorderWidth=0
        )

        self.screen.displayMessage(
            xMessage=str(xBlock.value),
            xFont=FONT,
            xFontColor=xBlock.font_color,
            xFontSize=xBlock.font_size,
            xCenter=self.edge_x + (xLoc - .5) * self.side_length,
            yCenter=self.edge_y + (yLoc - .5) * self.side_length
        )

    def drawBoard(self):
        self.Nx, self.Ny = self.board.Nx, self.board.Ny
        self.screen.clearScreen()

        # get edge coordinates
        edge = max(self.width * self.edge_percentage, self.height * self.edge_percentage)
        self.side_length = min(int((self.width - 2 * edge) / self.Nx), int((self.height - 2 * edge) / self.Ny))
        self.edge_x = int((self.width - self.Nx * self.side_length) / 2)
        self.edge_y = int((self.height - self.Ny * self.side_length) / 2)

        # fill within the outer bound with BORDER_COLOR
        self.drawRectangle(self.edge_x - BORDER_WIDTH / 2, self.edge_y - BORDER_WIDTH / 2,
                           self.side_length * self.Nx + BORDER_WIDTH, self.side_length * self.Ny + BORDER_WIDTH,
                           BORDER_COLOR, 0)

        # fill the background with EMPTY_BLOCK_COLOR
        self.drawRectangle(self.edge_x, self.edge_y, self.side_length * self.Nx, self.side_length * self.Ny,
                           EMPTY_BLOCK_COLOR, 0)

        # draw all borders
        for iy in range(self.Ny):
            for ix in range(self.Nx):
                left = self.edge_x + ix * self.side_length
                top = self.edge_y + iy * self.side_length
                self.drawRectangle(left, top, self.side_length, self.side_length, BORDER_COLOR, BORDER_WIDTH)

        for xLoc, yLoc in self.board.occupied.keys():
            block = self.board.occupied[(xLoc, yLoc)]
            if block is not None:
                self.displayBlock(xLoc, yLoc, block)

    def showStatus(self, xPlayer):
        self.screen.displayMessage(
            xMessage="{}".format(
                xPlayer.name
            ),
            xFont=FONT,
            xFontColor=FONT_COLOR,
            xFontSize=MSG_FONT_SIZE,
            xCenter=self.width * 1 / 5,
            yCenter=self.edge_y * 2 / 5
        )
        self.screen.displayMessage(
            xMessage="SCORE :   {}".format(self.board.getTotalScore()),
            xFont=FONT,
            xFontColor=FONT_COLOR,
            xFontSize=STATUS_FONT_SIZE,
            xCenter=self.width * 3 / 4,
            yCenter=self.edge_y * 2 / 5
        )


class Player:
    def __init__(self, xName):
        self.name = xName


class ComputerPlayer(Player):
    def __init__(self, xName='Mozart'):
        Player.__init__(self, xName)

    def generateValidMove(self, xAvailableMoves):
        if not isinstance(xAvailableMoves, list) or len(xAvailableMoves) == 0:
            return None
        return xAvailableMoves[random.randint(1, len(xAvailableMoves)) - 1]


class HumanPlayer(Player):
    def __init__(self, xScreen, xName='Dongdong'):
        Player.__init__(self, xName)
        self.screen = xScreen

    def generateValidMove(self, xAvailableMoves):
        if not isinstance(xAvailableMoves, list) or len(xAvailableMoves) == 0:
            return None
        move = ''
        while move not in xAvailableMoves and move != self.screen.exitString:
            move = self.screen.getKey()
        return move


class Game:
    """
    GAME
    """

    def __init__(self, xScreen, xHuman=True, xNumBlocks=2, xSize=2):
        self.screen = xScreen
        self.board = Board(xSize, xSize)
        if self.screen:
            self.board_display = BoardDisplay(self.screen, self.board)
        self.human = xHuman

        flag = False
        count = 0
        while not flag or count < xNumBlocks:
            flag = self.board.populate()
            if flag:
                count += 1

        if self.human:
            self.player = HumanPlayer(self.screen)
        else:
            self.player = ComputerPlayer()

    def showAndWait(self, xShowBoard=True, xWaitKey=True):
        if xShowBoard:
            self.board_display.drawBoard()
            self.board_display.showStatus(self.player)
        self.screen.pygame.display.flip()
        if xWaitKey:
            return self.screen.getKey()

    def play(self, xShowProcess=True):
        flag_game_over = False
        flag_movement, flag_alive = True, True
        available_moves = -1

        flag_wait_key = not self.human and xShowProcess
        flag_show_board = self.human or xShowProcess
        while flag_alive:
            if self.screen:
                self.showAndWait(xShowBoard=flag_show_board,
                             xWaitKey=flag_wait_key)
            if available_moves == -1:  # recalculate only the first time
                available_moves = self.board.isAlive(xReturnMoves=True)
            move = self.player.generateValidMove(xAvailableMoves=available_moves)

            if self.screen and move == self.screen.exitString:
                return flag_game_over

            board_movement = self.board.collapseTo(move)
            if board_movement:
                self.board.populate()
                available_moves = self.board.isAlive(xReturnMoves=True)
                if len(available_moves) == 0:
                    flag_alive = False
        flag_game_over = True
        return flag_game_over

    def end(self, xGameOver=True):
        if xGameOver:
            self.showAndWait(xShowBoard=True, xWaitKey=False)
            self.board_display.screen.displayMessage(
                xMessage='GAME OVER',
                xFont=FONT,
                xFontColor=FONT_COLOR,
                xFontSize=MSG_FONT_SIZE,
                xCenter=self.board_display.width / 2,
                yCenter=self.board_display.height - self.board_display.edge_y / 2
            )
            self.screen.pygame.display.flip()


class GameRoom:
    """
    GAMEROOM
    """
    def __init__(self):
        self.screen = Screen()
        self.player_option = None
        self.size_of_board = 2

    def openScreen(self):
        self.screen.clearScreen()
        self.screen.displayMessage(
                xMessage='SELECT PLAYER',
                xFont=FONT,
                xFontColor=FONT_COLOR,
                xFontSize=MSG_FONT_SIZE+4,
                xCenter=self.screen.width/2,
                yCenter=self.screen.height * 2/7
        )
        self.screen.displayMessage(
                xMessage='0: MACHINE',
                xFont=FONT,
                xFontColor=FONT_COLOR,
                xFontSize=MSG_FONT_SIZE-4,
                xCenter=self.screen.width/2,
                yCenter=self.screen.height * 3/7
        )
        self.screen.displayMessage(
                xMessage='other: HUMAN',
                xFont=FONT,
                xFontColor=FONT_COLOR,
                xFontSize=MSG_FONT_SIZE-4,
                xCenter=self.screen.width/2,
                yCenter=self.screen.height * 4/7
        )
        self.screen.pygame.display.flip()

        self.player_option = self.screen.getKey()
        if self.player_option == self.screen.exitString:
            sys.exit(0)

    def interScreen(self):
        self.screen.clearScreen()
        self.screen.displayMessage(
                xMessage='Play again ?',
                xFont=FONT,
                xFontColor=FONT_COLOR,
                xFontSize=MSG_FONT_SIZE+4,
                xCenter=self.screen.width/2,
                yCenter=self.screen.height * 3/7
        )
        self.screen.displayMessage(
                xMessage='Press Y ...',
                xFont=FONT,
                xFontColor=FONT_COLOR,
                xFontSize=MSG_FONT_SIZE+4,
                xCenter=self.screen.width/2,
                yCenter=self.screen.height * 4/7
        )
        self.screen.pygame.display.flip()

        key = self.screen.getKey()
        if key == self.screen.exitString:
            sys.exit(0)
        return key

    def endScreen(self):
        self.screen.clearScreen()
        self.screen.displayMessage(
                xMessage='Bye Bye ~ ~ ~',
                xFont=FONT,
                xFontColor=FONT_COLOR,
                xFontSize=MSG_FONT_SIZE+4,
                xCenter=self.screen.width/2,
                yCenter=self.screen.height * 3/7
        )
        self.screen.pygame.display.flip()
        self.screen.pygame.time.wait(2000)
        self.screen.pygame.quit()

    def play(self):
        if self.player_option == '0':
            game = Game(xScreen=self.screen,
                        xHuman=False,
                        xSize=self.size_of_board)
            game_over = game.play(xShowProcess=False)
        else:
            game = Game(xScreen=self.screen,
                        xHuman=True,
                        xSize=self.size_of_board)
            game_over = game.play(xShowProcess=True)

        if game_over:
            game.end(xGameOver=game_over)
            self.screen.pygame.time.wait(1000)

    def execute(self):
        play_again = 'Y'
        while play_again == 'Y':
            self.openScreen()
            self.play()
            play_again = self.interScreen()
        self.endScreen()


