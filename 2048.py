from utils import *



def main():

    game_room = GameRoom()
    game_room.execute()


    #### batch playing mode
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


    ####  unit test
    # board = Board(2,2)
    # board.occupy(1,1,Block(2,0))
    # board.occupy(2,1,Block(1,0))
    #
    # moves = board.isAlive(xReturnMoves=True)
    # print('available moves', moves)
    # move = 'DOWN'
    # board_move = board.collapseTo(move)
    # print('board move success', board_move)

    # QC(board)




if __name__ == "__main__":
    main()
