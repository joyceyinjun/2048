from utils import *

class BatchPlayer:
    """
    BATCHPLAYER
    """

    def __init__(self,xNumRounds):
        self.num_rounds = xNumRounds
        self.scores = []

    def play(self):
        for _ in range(self.num_rounds):
            game = Game(xScreen=None, xHuman=False, xSize=4)
            game.play()
            self.scores.append(game.board.getTotalScore())

def main():
    batch_player = BatchPlayer(100)
    batch_player.play()
    print('number of games played: {}'.format(len(batch_player.scores)))
    print('average score: {}'.format(sum(batch_player.scores)/len(batch_player.scores)))



if __name__ == "__main__":
    main()
