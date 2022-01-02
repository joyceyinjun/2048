import copy
import sys

sys.path += ['../', '../display']
from config import EXIT_STRING, UNDO_STRING


class Game:
    def __init__(self, xBoard, xPlayers, xCurrentPlayerId=0):
        self.board = xBoard
        self.last_board = None
        self.players = xPlayers
        self.current_player_id = xCurrentPlayerId
        self.isAlive = None
        self.updateStatus()

    def updateStatus(self):
        self.board.updateStatus()
        self.isAlive = len(self.board.available_moves) > 0

    def updatePlayer(self):
        self.current_player_id = (self.current_player_id + 1) % len(self.players)

    def restoreLastStep(self):
        self.board = self.last_board
        self.last_board = None
        self.updatePlayer()

    def proceedOneStep(self, xMove):
        self.last_board = copy.deepcopy(self.board)
        self.board.collapseTo(xMove)
        self.updatePlayer()
        self.board.populate(self.current_player_id)

    def next(self):
        move = self.players[self.current_player_id].generateValidMove(self.board)
        if move != UNDO_STRING:
            self.proceedOneStep(move)
        elif move == UNDO_STRING and self.last_board:
            self.restoreLastStep()
        self.updateStatus()

    def play(self):
        while self.isAlive:
            self.next()
