import random
import copy
from config import DIRECTIONS


class Block:
    """
    BLOCK
    """

    def __init__(self, xValue, xPlayerId=0):
        self.value = xValue
        self.player_id = xPlayerId

    def __str__(self):
        return '<Block {}>'.format(self.value)

    def __repr__(self):
        return '<Block {}>'.format(self.value)


class Board:
    """
    BOARD
    """

    def __init__(self, xN):
        self.Nx = xN
        self.Ny = xN
        self.isEmpty = True
        self.occupied = {}
        self.unoccupied = [(x + 1, y + 1)
                           for x in range(self.Nx)
                           for y in range(self.Ny)]
        self.available_moves = None

    def clearBoard(self):
        self.occupied = {}
        self.isEmpty = True

    def getPlayerStatus(self, xPlayerId):
        total_score, num_blocks = 0, 0
        for location in self.occupied.keys():
            block = self.occupied[location]
            if block.player_id == xPlayerId:
                total_score += block.value
                num_blocks += 1
        return total_score, num_blocks

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

    def populate(self, xPlayerId, xValue=1):
        if len(self.unoccupied) == 0:
            return False
        block = Block(xValue,xPlayerId)
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
            player_id = self.occupied[(x, y)].player_id
            x, y = rotateXY(x, y, xTimes)
            occupied_updated[(x, y)] = Block(value, player_id)
        self.occupied = occupied_updated

    def collapse(self, xMove=True):
        def collapseList(xList):
            """

            """
            input_size = len(xList)
            flag_movement = False
            shredded_list = [z for z in xList if z[0] > 0]
            if shredded_list + [(0,-1)] * (input_size - len(shredded_list)) != xList:
                flag_movement = True

            i = 0
            while i < len(shredded_list) - 1:
                if shredded_list[i][0] == shredded_list[i + 1][0]:
                    # double the value; take the id of the "devouring" block
                    shredded_list[i] = (shredded_list[i][0] * 2, shredded_list[i + 1][1])
                    shredded_list = shredded_list[:i + 1] + shredded_list[i + 2:]
                    flag_movement = True
                i += 1
            output = shredded_list + [(0,-1)] * (input_size - len(shredded_list))
            return output, flag_movement

        board_movement = False
        for xLoc in range(self.Nx):
            x = xLoc + 1
            input_list = []
            for yLoc in range(self.Ny):
                y = yLoc + 1
                if (x, y) in self.occupied.keys():
                    current_block = self.occupied[(x, y)]
                    input_list.append((current_block.value, current_block.player_id))
                else:
                    input_list.append((0,-1))
            output_list, row_movement = collapseList(input_list)

            board_movement |= row_movement

            if row_movement and xMove:
                for yLoc in range(self.Ny):
                    y = yLoc + 1
                    if (x, y) in self.occupied.keys():
                        self.release(x, y)
                    if output_list[yLoc][0] > 0:
                        self.occupy(x, y, Block(output_list[yLoc][0], output_list[yLoc][1]))

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

    def updateStatus(self):
        self.available_moves = self.isAlive(xReturnMoves=True)

    def getNextStepValues(self, xCurrentPlayerId):
        self.updateStatus()
        if len(self.available_moves) == 0:
            return None

        value_function = {}
        for move in self.available_moves:
            board_cp = copy.deepcopy(self)
            board_cp.collapseTo(move)
            value_function[move] = board_cp.getPlayerStatus(xCurrentPlayerId)

        return value_function

    def __str__(self):
        if self.isEmpty:
            return '<Board Empty>'
        ans = '<Board '
        for x, y in self.occupied.keys():
            ans += '[{} at ({},{})], '.format(self.occupied[(x, y)], x, y)
        ans = ans[:-2] + '>'
        return ans

