import sys
sys.path += [
    './game',
    './display',
    './training']

from collections import Counter
from utils import *
from training import Trainer


# class Undo(BaseException):
#     def __init__(self, xKeyboardInput, xMessage='Undo Exception'):
#         self.message = 'pressed {}, an {}'.format(xKeyboardInput, xMessage)
#         super().__init__(self.message)

def unittest():
    """
    unit test
    """
    # board = Board(4)
    # board.occupy(3, 1, Block(xValue=2, xPlayerId=0))
    # board.occupy(4, 1, Block(xValue=1, xPlayerId=1))
    # board.occupy(4, 3, Block(xValue=1, xPlayerId=0))
    # board.occupy(4, 4, Block(xValue=1, xPlayerId=1))

    board = Board(2)
    board.occupy(1,2,Block(xValue=1, xPlayerId=0))
    board.occupy(2,1,Block(xValue=2, xPlayerId=0))
    board.occupy(2,2,Block(xValue=1, xPlayerId=0))
    board.updateStatus()
    print('board', board.getSnapshot())

    player = ComputerPlayer()
    print(board.available_moves)
    available_moves = ['LEFT','DOWN', 'UP']
    expected_return = [3.5, 4.2, 4.17]
    confidence = [50, 40, 40]

    actions = []
    for _ in range(1000):
        actions.append(
            player.sampleFromList(
                available_moves,
                expected_return,
                confidence
            )
            # player.generateValidMove(
            #                     board,
            #                     expected_return,
            #                     confidence)
       )
    print(Counter(actions))

#
# def interactiveplay():
#     """
#     interactive mode
#     """
#     board = Board(4, 4)
#     board.occupy(3, 1, Block(xValue=2, xPlayerId=0))
#     board.occupy(4, 1, Block(xValue=1, xPlayerId=1))
#     board.occupy(4, 3, Block(xValue=1, xPlayerId=0))
#     board.occupy(4, 4, Block(xValue=1, xPlayerId=1))
#
#     game_room = GameRoom(xSize=3, xQC=False)
#     game_room.execute()



def main():
    trainer = Trainer(xNumPlayers=1,
                      xSizeOfBoard=2,
                      xNumGames=1000,
                      xQC=True)

    # for i in range(50):
    #     print('epoch', i)
    #     trainer.execute()

    trainer.check(xEpoch=1)
    trainer.check(xEpoch=49)

    # unittest()

    pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
