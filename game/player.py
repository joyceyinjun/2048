import random

class Player:
    def __init__(self, xScreen, xName, xId):
        self.name = xName
        self.id = xId
        self.screen = xScreen


class ComputerPlayer(Player):
    def __init__(self, xScreen=None, xName='Mozart', xId=0):
        Player.__init__(self, xScreen, xName, xId)

    def generateValidMove(self, xAvailableMoves, xWaitKey=False):
        if self.screen:
            if xWaitKey:
                self.screen.getKey()
            else:
                self.screen.pygame.time.wait(1500)
        if not isinstance(xAvailableMoves, list) or len(xAvailableMoves) == 0:
            return None
        return xAvailableMoves[random.randint(1, len(xAvailableMoves)) - 1]


class HumanPlayer(Player):
    def __init__(self, xScreen, xName='Dongdong', xId=0):
        Player.__init__(self, xScreen, xName, xId)

    def generateValidMove(self, xAvailableMoves):
        if not isinstance(xAvailableMoves, list) or len(xAvailableMoves) == 0:
            return None
        move = ''
        while move not in xAvailableMoves:
            move = self.screen.getKey()
        return move
