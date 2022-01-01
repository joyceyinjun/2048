import sys

sys.path += ['../display']
import random
from config import KEY_MAPPING


def sampleFromList(xList):
    return xList[random.randint(1, len(xList)) - 1]


class Player:
    def __init__(self, xScreen, xName, xId, xQC=False):
        self.name = xName
        self.id = xId
        self.screen = xScreen
        self.qc = xQC


class HumanPlayer(Player):
    def __init__(self, xScreen, xName='Dongdong', xId=0):
        Player.__init__(self, xScreen, xName, xId)

    def generateValidMove(self, xBoard):
        available_moves = xBoard.available_moves
        if not isinstance(available_moves, list) or len(available_moves) == 0:
            return None
        move = ''
        while move not in available_moves:
            move = KEY_MAPPING[self.id].get(self.screen.getKey(), None)
        return move


class ComputerPlayer(Player):
    def __init__(self, xScreen=None, xName='Mozart', xId=0, xQC=False):
        Player.__init__(self, xScreen, xName, xId, xQC)

    def wait(self, xWaitKey):
        if self.screen:
            if xWaitKey:
                self.screen.getKey()
            else:
                self.screen.pygame.time.wait(1500)

    def generateValidMove(self, xBoard):
        self.wait(self.qc)
        available_moves = xBoard.available_moves
        if not available_moves:
            return None
        return sampleFromList(available_moves)


class SmartPlayer(ComputerPlayer):
    def __init__(self, xScreen=None, xName='Junjun', xId=0, xQC=False):
        ComputerPlayer.__init__(self, xScreen, xName, xId, xQC)

    def generateValidMove(self, xBoard):
        value_function = xBoard.getNextStepValues(self.id)
        if not value_function:
            return None

        top_moves = []
        max_value, min_num_blocks = 0, xBoard.Nx * xBoard.Ny

        for key in value_function:
            if (value_function[key][0] > max_value) or \
                    (value_function[key][0] == max_value and
                     value_function[key][1] < min_num_blocks):
                top_moves = [key]
                max_value, min_num_blocks = value_function[key]
            elif value_function[key][0] == max_value and \
                    value_function[key][1] == min_num_blocks:
                top_moves.append(key)

        if self.qc:
            print('values', value_function)
            print('moves', top_moves)
        self.wait(xWaitKey=self.qc)

        return sampleFromList(top_moves)
