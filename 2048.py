from utils import *
import copy




def main():
    #####################
    # interactive mode
    #####################
    # board = Board(4, 4)
    # board.occupy(3, 1, Block(xValue=2, xPlayerId=0))
    # board.occupy(4, 1, Block(xValue=1, xPlayerId=1))
    # board.occupy(4, 3, Block(xValue=1, xPlayerId=0))
    # board.occupy(4, 4, Block(xValue=1, xPlayerId=1))
    # current_player_id = 0

    game_room = GameRoom(xQC=True)
    game_room.execute()

    #####################
    # batch play mode
    #####################
    # size_of_board = 3
    # num_games = 10
    # batch_player = BatchPlayer(size_of_board, num_games)
    # batch_player.run()
    # scores_avg = batch_player.getAverageScores()
    #
    # scores_dist = batch_player.getScoreDistribution()
    # df = pd.concat([scores_dist, scores_avg])
    # df.index_name = 'score'
    # print(df)

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
    main()
