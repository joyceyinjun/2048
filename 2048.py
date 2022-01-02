from utils import *


# class Undo(BaseException):
#     def __init__(self, xKeyboardInput, xMessage='Undo Exception'):
#         self.message = 'pressed {}, an {}'.format(xKeyboardInput, xMessage)
#         super().__init__(self.message)


def main():
    # scr = Screen()
    # # key = scr.getKey()
    # # if key == UNDO_STRING:
    # #     print('enter raise')
    # #     raise Undo(key)
    # # print('other keys')
    #
    # try:
    #     print(normal)
    # except Undo(scr.getKey()):
    #     print('undo exception')

    #####################
    # interactive mode
    #####################
    # board = Board(4, 4)
    # board.occupy(3, 1, Block(xValue=2, xPlayerId=0))
    # board.occupy(4, 1, Block(xValue=1, xPlayerId=1))
    # board.occupy(4, 3, Block(xValue=1, xPlayerId=0))
    # board.occupy(4, 4, Block(xValue=1, xPlayerId=1))
    # current_player_id = 0

    # game_room = GameRoom(xSize=3, xQC=False)
    # game_room.execute()

    #####################
    # batch play mode
    #####################
    size_of_board = 4
    num_games = 5000
    batch_player = BatchPlayer(size_of_board, num_games)
    batch_player.run()
    scores_avg = batch_player.getAverageScores()

    scores_dist = batch_player.getScoreDistribution()
    df = pd.concat([scores_dist, scores_avg])
    df.index_name = 'score'
    df.to_csv('out2.csv')
    print('saved to csv')


    #####################
    #  unit test
    #####################
    # board = Board(4, 4)
    # board.occupy(3, 1, Block(xValue=2, xPlayerId=0))
    # board.occupy(4, 1, Block(xValue=1, xPlayerId=1))
    # board.occupy(4, 3, Block(xValue=1, xPlayerId=0))
    # board.occupy(4, 4, Block(xValue=1, xPlayerId=1))
    # current_player_id = 0
    #
    # QC(board)
    #
    # value_function = board.getNextStepValues(current_player_id)
    #
    # print('player', current_player_id)
    # print(value_function)

    # players = [ComputerPlayer(xId=0), ComputerPlayer(xId=1)]
    # game = Game(board, players)
    # game.play()
    # for player in players:
    #     print('player {}: {}'.format(
    #         player.id, game.board.getTotalScore(player.id)
    #     ))
    #
    # QC(board)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
