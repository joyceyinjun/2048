import sys
sys.path += [
    './game',
    './display',
    './training']

from collections import Counter
# from player import *
from utils import *
from training import Trainer

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
    available_moves = ['LEFT','RIGHT', 'UP']
    expected_return = [4.2, 4.1, 4.17]
    confidence = [2, 1, 2]

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


def interactiveplay():
    """
    interactive mode
    """
    board = Board(4, 4)
    board.occupy(3, 1, Block(xValue=2, xPlayerId=0))
    board.occupy(4, 1, Block(xValue=1, xPlayerId=1))
    board.occupy(4, 3, Block(xValue=1, xPlayerId=0))
    board.occupy(4, 4, Block(xValue=1, xPlayerId=1))

    game_room = GameRoom(xSize=3, xQC=False)
    game_room.execute()


def evaluatePlayers():
    players = [
        RandomPlayer(xName='Mozart', xId=0),
        GreedyPlayer(xName='Dongdong', xId=1),
        # LearnedPlayer(xName='Junjun', xId=0)
    ]

    # file_name = 'misc/rl/2x2_10000/value_functions/ep0050.pkl'
    # q_values = FileHandler().loadFromPickle(file_name)

    # batch_player = BatchPlayer(players, 2, q_values, 1000, False)
    batch_player = BatchPlayer(players, 3, None, 1000, False)
    batch_player.run()
    print(batch_player.getScoreDistribution())
    print(batch_player.getAverageScores())


def train():
    trainer = Trainer(xTag='scale_p1',
                    xNumPlayers=1,
                    xSizeOfBoard=2,
                    xNumGames=5000,
                    xTotalEpoch=50,
                    xQC=True)

    # trainer.execute()

    state = str(tuple([0, 1, 2, 1]))
    # # state = str(tuple([0,0,0,0,1,1,4,8,8]))
    trainer.checkState(xEpochs=[1,7,49], xState=state)
    trainer.checkStats([1,7,49])

def main():

    train()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
