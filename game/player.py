import sys
import random
import numpy as np

sys.path += ['../display']
from config import KEY_MAPPING, UNDO_STRING


class Player:
    def __init__(self, xScreen, xName, xId, xQC=False):
        self.name = xName
        self.id = xId
        self.screen = xScreen
        self.qc = xQC


class HumanPlayer(Player):
    def __init__(self, xScreen, xName='Dongdong', xId=0):
        super().__init__(xScreen, xName, xId)

    def generateValidMove(self, xBoard):
        available_moves = xBoard.available_moves
        if not isinstance(available_moves, list) or len(available_moves) == 0:
            return None

        move = ''
        while move not in available_moves and move != UNDO_STRING:
            move = KEY_MAPPING[self.id].get(self.screen.getKey(), None)
        return move


class ComputerPlayer(Player):
    def __init__(self, xScreen=None, xName='Mozart', xId=0, xQC=False):
        super().__init__(xScreen, xName, xId, xQC)

    def wait(self, xWaitKey):
        if self.screen:
            if xWaitKey:
                self.screen.getKey()
            else:
                self.screen.pygame.time.wait(1500)

    @staticmethod
    def sampleFromList(xList, xExpectedReturn=None, xConfidence=None):
        if xExpectedReturn is None:
            return xList[random.randint(1, len(xList)) - 1]
        assert len(xList) == len(xExpectedReturn) and \
               len(xList) == len(xConfidence), "INPUT DATA FORMAT INCONSISTENT"
        samples = ([np.random.normal(
            loc=r, scale=1 / np.sqrt(xConfidence[i]))
            for i, r in enumerate(xExpectedReturn)
        ])
        return xList[np.argmax(samples)]

    @staticmethod
    def getStateQValues(xState, xActions, xQValues):
        expected_return, confidence = [], []
        for action in xActions:
            key = (xState, action)
            # set value default to 0
            # as no information is available
            count, value = xQValues.get(key, [1e-4, 0])
            confidence.append(count)
            expected_return.append(value/count)
        return expected_return, confidence

    def generateValidMove(self, xBoard, xQValues):
        self.wait(self.qc)
        available_moves = xBoard.available_moves
        if not available_moves:
            return None
        if xQValues is None:
            return self.sampleFromList(available_moves)

        current_state = str(tuple(xBoard.getSnapshot()))
        expected_return, confidence = self.getStateQValues(
                        current_state, available_moves, xQValues)
        return self.sampleFromList(available_moves,
                              expected_return, confidence)


class GreedyPlayer(ComputerPlayer):
    def __init__(self, xScreen=None, xName='Junjun', xId=0, xQC=False):
        super().__init__(xScreen, xName, xId, xQC)

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

        return self.sampleFromList(top_moves)
