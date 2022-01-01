import sys
sys.path += ['./game', './display']

from collections import Counter
import pandas as pd

from display import *
from board import *
from player import *
from game import *


class GameRoom:
    """
    GAMEROOM
    """

    def __init__(self, xSize=4, xQC=False, xBoard=None):
        self.screen = Screen()
        self.size_of_board = xSize
        self.player_options = []
        self.players = []

        self.board = xBoard
        self.game = None
        self.game_display = None
        self.qc = xQC

    def openScreen(self):
        self.screen.clearScreen()
        self.screen.displayMessage(
            xMessage='1 OR 2 PLAYERS ?',
            xFont=FONT,
            xFontColor=MSG_FONT_COLOR,
            xFontSize=MSG_FONT_SIZE + 4,
            xCenter=self.screen.width / 2,
            yCenter=self.screen.height * 2 / 7
        )
        self.screen.pygame.display.flip()

        key = ''
        while key not in ('1','2'):
            key = self.screen.getKey()
        num_players = int(key)

        self.player_options = []
        cnt = 1
        while cnt <= num_players:
            self.screen.clearScreen()
            self.screen.displayMessage(
                xMessage='SELECT PLAYER - {}'.format(cnt),
                xFont=FONT,
                xFontColor=MSG_FONT_COLOR,
                xFontSize=MSG_FONT_SIZE + 4,
                xCenter=self.screen.width / 2,
                yCenter=self.screen.height * 2 / 7
            )
            self.screen.displayMessage(
                xMessage='0: MACHINE',
                xFont=FONT,
                xFontColor=MSG_FONT_COLOR,
                xFontSize=MSG_FONT_SIZE - 4,
                xCenter=self.screen.width / 2,
                yCenter=self.screen.height * 3 / 7
            )
            self.screen.displayMessage(
                xMessage='other: HUMAN',
                xFont=FONT,
                xFontColor=MSG_FONT_COLOR,
                xFontSize=MSG_FONT_SIZE - 4,
                xCenter=self.screen.width / 2,
                yCenter=self.screen.height * 4 / 7
            )
            self.screen.pygame.display.flip()
            cnt += 1
            self.player_options.append(self.screen.getKey())

    def interScreen(self):
        self.screen.displayMessage(
            xMessage='Play again ? Press Y ...',
            xFont=FONT,
            xFontColor=MSG_FONT_COLOR,
            xFontSize=MSG_FONT_SIZE,
            xCenter=self.screen.width / 2,
            yCenter=self.screen.height - self.game_display.board_display.edge_y/2
        )
        self.screen.pygame.display.flip()

        key = self.screen.getKey()
        return key

    def endScreen(self):
        self.screen.clearScreen()
        self.screen.displayMessage(
            xMessage='Bye Bye ~ ~ ~',
            xFont=FONT,
            xFontColor=MSG_FONT_COLOR,
            xFontSize=MSG_FONT_SIZE + 4,
            xCenter=self.screen.width / 2,
            yCenter=self.screen.height * 3 / 7
        )
        self.screen.pygame.display.flip()
        self.screen.pygame.time.wait(2000)
        self.screen.pygame.quit()

    def stage(self):
        # initiate players
        self.players = []
        for i, player_option in enumerate(self.player_options):
            if player_option == '0':
                self.players.append(
                    SmartPlayer(
                        xScreen=self.screen,
                        xName=PLAYER_NAMES[i],
                        xId=i,
                        xQC=self.qc
                    )
                )
            else:
                self.players.append(
                    HumanPlayer(
                        xScreen=self.screen,
                        xName=PLAYER_NAMES[i],
                        xId=i
                    )
                )

        # initiate board if not given
        if not self.board:
            self.board = Board(self.size_of_board, self.size_of_board)
            for player in self.players:
                flag = False
                while not flag:
                    flag = self.board.populate(xPlayerId=player.id)
        # initiate game
        self.game = Game(
            xBoard=self.board,
            xPlayers=self.players,
            xCurrentPlayerId=0
        )

        # initiate game display
        self.game_display = GameDisplay(self.screen, self.game)

        # show initial board
        self.game_display.showAndWait()

    def play(self):
        while self.game.isAlive:
            self.game.next()
            self.game_display.showAndWait()
        self.game_display.end()
        self.screen.pygame.time.wait(2000)

    def execute(self):
        play_again = 'Y'
        while play_again == 'Y':
            self.openScreen()
            self.stage()
            self.play()
            play_again = self.interScreen()
        self.endScreen()


class BatchPlayer:
    """
    BATCHPLAYER
    """

    def __init__(self, xSizeOfBoard, xNumRounds):
        self.players = [
            ComputerPlayer(xName='Mozart', xId=0),
            # ComputerPlayer(xName='DongDong', xId=1),
        ]
        self.size_of_board = xSizeOfBoard
        self.num_rounds = xNumRounds
        self.scores = {}
        for i in range(len(self.players)):
            self.scores[i] = []

    def run(self):
        for _ in range(self.num_rounds):
            game = Game(xPlayers=self.players, xSize=self.size_of_board)
            game.play()
            for i in range(len(self.players)):
                self.scores[i].append(game.board.getTotalScore(i))

    def getAverageScores(self):
        scores_avg = {}
        for i in range(len(self.players)):
            scores_avg[self.players[i].name] = sum(self.scores[i])
            scores_avg[self.players[i].name] /= self.num_rounds
        return pd.DataFrame(scores_avg, index=['Average Score'])

    def getScoreDistribution(self):
        counts = []
        for i in range(len(self.scores)):
            counts.append(Counter(self.scores[i]))

        df = pd.DataFrame(counts).transpose().sort_index().rename(
            columns={z.id: z.name for z in self.players}
        ).fillna(0).astype(int)
        df.index_name = 'score'

        return df


class QC:
    def __init__(self,xBoard):
        screen = Screen()
        board_display = BoardDisplay(screen,xBoard)
        board_display.drawBoard()
        screen.pygame.display.flip()
        screen.getKey()
