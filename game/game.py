class Game:
    def __init__(self, xBoard, xPlayers, xCurrentPlayerId=0):
        self.board = xBoard
        self.players = xPlayers
        self.current_player_id = xCurrentPlayerId
        self.isAlive = None
        self.updateStatus()

    def updateStatus(self):
        self.board.updateStatus()
        self.isAlive = len(self.board.available_moves) > 0

    def updatePlayer(self):
        self.current_player_id = (self.current_player_id + 1) % len(self.players)

    def next(self):
        move = self.players[self.current_player_id].generateValidMove(self.board)
        self.board.collapseTo(move)
        self.updatePlayer()
        self.board.populate(self.current_player_id)
        self.updateStatus()

    def play(self):
        while self.isAlive:
            self.next()
