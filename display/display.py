import sys
from config import *


class Screen:
    """
    SCREEN
    """

    def __init__(self, xWindowSize=WINDOW_SIZE, xFullscreen=False):
        import pygame
        pygame.init()
        self.pygame = pygame
        self.screen_color = SCREEN_COLOR

        self.icon = self.pygame.image.load('./display/icon.jpg')
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
                sys.exit(0)
            elif event.type == self.pygame.KEYDOWN:
                if self.pygame.key.name(event.key).upper() == self.exitString:
                    sys.exit(0)
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

    def colorFlip(self, xRgbColor, xId=0):
        if xId == 1:
            return xRgbColor[2], xRgbColor[1], xRgbColor[0]
        return xRgbColor

    def drawRectangle(self, xLoc, yLoc, xWidth, xHeight,
                      xColor, xBorderWidth):
        self.screen.pygame.draw.rect(
            self.screen.surface, xColor,
            (xLoc, yLoc, xWidth, xHeight),
            xBorderWidth
        )

    def displayBlock(self, xLoc, yLoc, xBlock):
        left = self.edge_x + (xLoc - 1) * self.side_length + BORDER_WIDTH / 2
        top = self.edge_y + (yLoc - 1) * self.side_length + BORDER_WIDTH / 2
        block_side_length = self.side_length - BORDER_WIDTH

        block_color = self.colorFlip(BLOCK_SETUP[xBlock.value][2],
                                     xBlock.player_id)
        font_color = self.colorFlip(BLOCK_SETUP[xBlock.value][0],
                                    xBlock.player_id)
        font_size = int(BLOCK_SETUP[xBlock.value][1] * BLOCK_FONT_SIZE)

        self.drawRectangle(
            xLoc=left,
            yLoc=top,
            xWidth=block_side_length,
            xHeight=block_side_length,
            xColor=block_color,
            xBorderWidth=0
        )

        self.screen.displayMessage(
            xMessage=str(xBlock.value),
            xFont=BLOCK_FONT,
            xFontColor=font_color,
            xFontSize=font_size,
            xCenter=self.edge_x + (xLoc - .5) * self.side_length,
            yCenter=self.edge_y + (yLoc - .5) * self.side_length
        )

    def drawBoard(self):
        self.Nx, self.Ny = self.board.Nx, self.board.Ny
        self.screen.clearScreen()

        # get edge coordinates
        edge = max(self.width * self.edge_percentage,
                   self.height * self.edge_percentage)
        self.side_length = min(
            int((self.width - 2 * edge) / self.Nx),
            int((self.height - 2 * edge) / self.Ny)
        )
        self.edge_x = int((self.width - self.Nx * self.side_length) / 2)
        self.edge_y = int((self.height - self.Ny * self.side_length) / 2)

        # fill within the outer bound with BORDER_COLOR
        self.drawRectangle(
            self.edge_x - BORDER_WIDTH / 2,
            self.edge_y - BORDER_WIDTH / 2,
            self.side_length * self.Nx + BORDER_WIDTH,
            self.side_length * self.Ny + BORDER_WIDTH,
            BORDER_COLOR, 0)

        # fill the background with EMPTY_BLOCK_COLOR
        self.drawRectangle(self.edge_x, self.edge_y,
                           self.side_length * self.Nx,
                           self.side_length * self.Ny,
                           EMPTY_BLOCK_COLOR, 0)

        # draw all borders
        for iy in range(self.Ny):
            for ix in range(self.Nx):
                left = self.edge_x + ix * self.side_length
                top = self.edge_y + iy * self.side_length
                self.drawRectangle(
                    left, top,
                    self.side_length, self.side_length,
                    BORDER_COLOR, BORDER_WIDTH
                )

        for xLoc, yLoc in self.board.occupied.keys():
            block = self.board.occupied[(xLoc, yLoc)]
            if block is not None:
                self.displayBlock(xLoc, yLoc, block)

    def showStatus(self, xPlayers, xCurrentPlayerId=0):
        y_top = self.edge_y * 3 / 5
        y_interval = self.edge_y * 3 / 10
        for i, player in enumerate(xPlayers):
            if i == xCurrentPlayerId:
                color = ACTIVE_FONT_COLOR
            else:
                color = MSG_FONT_COLOR
            self.screen.displayMessage(
                xMessage="{} :  {}".format(
                    player.name,
                    self.board.getPlayerStatus(player.id)[0]
                ),
                xFont=FONT,
                xFontColor=color,
                xFontSize=STATUS_FONT_SIZE,
                xCenter=self.width * 3 / 4,
                yCenter=y_top + (i - 1) * y_interval
            )


class GameDisplay:
    """
    GAME DISPLAY
    """

    def __init__(self, xScreen, xGame):
        self.screen = xScreen
        self.game = xGame
        if self.screen:
            self.board_display = BoardDisplay(self.screen, self.game.board)

    def showAndWait(self, xShowBoard=True, xWaitKey=False):
        if xShowBoard:
            self.board_display.drawBoard()
            self.board_display.showStatus(self.game.players, self.game.current_player_id)
            self.screen.pygame.display.flip()
        if xWaitKey:
            return self.screen.getKey()

    def end(self, xGameOver=True):
        if xGameOver:
            self.showAndWait(xShowBoard=True, xWaitKey=False)
            self.board_display.screen.displayMessage(
                xMessage='GAME OVER',
                xFont=FONT,
                xFontColor=MSG_FONT_COLOR,
                xFontSize=MSG_FONT_SIZE,
                xCenter=self.board_display.width * 2 / 5,
                yCenter=self.board_display.edge_y / 2
            )
            self.screen.pygame.display.flip()
