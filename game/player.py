import sys
sys.path += ['../display']

import random
import numpy as np

from config import KEY_MAPPING, UNDO_STRING


class Player:
    """
    an interface for all players
    """
    def __init__(self, xScreen, xName, xId, xQC=False):
        self.name = xName
        self.id = xId
        self.screen = xScreen
        self.qc = xQC

    def generateValidMove(self):
        pass


class HumanPlayer(Player):
    """
    a human player takes the move defined by
    the input from keyboard
    """
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
    """
    an interface for all auto players
    """
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
            loc=r, scale=.1 / np.sqrt(xConfidence[i]))
            for i, r in enumerate(xExpectedReturn)
        ])
        return xList[np.argmax(samples)]

    def generateValidMove(self):
        pass


class RandomPlayer(ComputerPlayer):
    """
    a random player picks a random move
    among all that are allowed
    """
    def __init__(self, xScreen=None, xName='Mozart', xId=0, xQC=False):
        super().__init__(xScreen, xName, xId, xQC)

    def generateValidMove(self, xBoard, xQValues=None):
        self.wait(self.qc)
        available_moves = xBoard.available_moves
        if not available_moves:
            return None
        return self.sampleFromList(available_moves)


class GreedyPlayer(ComputerPlayer):
    """
    a greedy player always makes the move that
    maximizes the total score and results in
    smallest number of blocks
    """
    def __init__(self, xScreen=None, xName='Junjun', xId=0, xQC=False):
        super().__init__(xScreen, xName, xId, xQC)

    def generateValidMove(self, xBoard, xQValues=None):
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


class LearnedPlayer(ComputerPlayer):
    """
    a learned player is able to decide on
    actions given q values
    """
    def __init__(self, xScreen=None, xName='Mozart', xId=0, xQC=False):
        super().__init__(xScreen, xName, xId, xQC)

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

    def generateValidMove(self, xBoard, xQValues, xMethod='thompson'):
        self.wait(self.qc)
        available_moves = xBoard.available_moves
        if not available_moves:
            return None
        if xQValues is None:
            return self.sampleFromList(available_moves)
        expected_return, confidence = \
            self.getStateQValues(xBoard.getSnapshot(), available_moves, xQValues)
        # implemented thompson sampling
        if xMethod.lower() == 'thompson':
            return self.sampleFromList(available_moves,
                                   expected_return, confidence)


        current_state = str(tuple(xBoard.getSnapshot()))
        expected_return, confidence = self.getStateQValues(
                        current_state, available_moves, xQValues)
        return self.sampleFromList(available_moves,
                              expected_return, confidence)
