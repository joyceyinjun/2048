import copy
import sys

sys.path += ['../', '../display']
from config import EXIT_STRING, UNDO_STRING


class Game:
    def __init__(self, xBoard, xPlayers, xCurrentPlayerId=0,
                 xRecordGame=False):
        self.board = xBoard
        self.last_board = None
        self.players = xPlayers
        self.current_player_id = xCurrentPlayerId
        self.isAlive = None
        self.updateStatus()

        self.record_game = xRecordGame
        if self.record_game:
            self.recording = []

    def record(self, xCurrentPlayerId, xCurrentBoardSnapshot,
                        xPlayerAction, xInstantReturn):
        self.recording += [(xCurrentPlayerId,
                         xCurrentBoardSnapshot,
                         xPlayerAction,
                         xInstantReturn
                         )]


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
        if self.record_game:
            player_option = min(1,len(self.players)-1)
            record_player_id = self.current_player_id
            record_board = self.board.getSnapshot(
                xPlayer=player_option
            )
            record_score = self.board.getPlayerStatus(record_player_id)[0]
            record_move = move

        if move != UNDO_STRING:
            self.proceedOneStep(move)
        elif move == UNDO_STRING and self.last_board:
            self.restoreLastStep()
        self.updateStatus()

        if self.record_game:
            record_score = self.board.getPlayerStatus(record_player_id)[0]\
                                    - record_score
            self.record(record_player_id, record_board,
                        record_move, record_score)

    def play(self):
        while self.isAlive:
            self.next()
