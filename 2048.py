import sys
sys.path += [
    './game',
    './display',
    './training']

from collections import Counter
from player import *
from utils import *
from training import Trainer, PolicyEvaluator

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
    expected_return = [0, 0, 0]
    confidence = [1, 1, 1]

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
    file_name = 'misc/rl/scale_p1_2x2_5000/recordings/ep0001.pkl'
    peor = PolicyEvaluator([], 2, 5000,
                xGameRecordingFileName=file_name)
    vs_mc, vsa_mc = peor.getValueFunctions('mc')
    vs_td, vsa_td = peor.getValueFunctions('td')
    df_vsmc = pd.DataFrame(vs_mc,index=['count','value']).transpose()
    df_vstd = pd.DataFrame(vs_td,index=['count','value']).transpose()

    for df in [df_vsmc, df_vstd]:
        df['state_value'] = df['value']/df['count']
    cols = ['state_value']

    pd.set_option('display.max_rows',None)
    pd.set_option('display.max_columns', None)
    pd.options.display.width = 0
    print(df_vsmc[cols].join(df_vstd[cols],
                how='outer',lsuffix='_mc',rsuffix='_td'
            ).sort_values(by='state_value_mc',
             ascending=False).head(50))




    # players = [GreedyPlayer(xId=0), RandomPlayer(xId=1)]
    # peer = PolicyEvaluator(players, 2, 100)
    # peer.evaluate()
    # d_greedy = {'state': [],
    #      'value': [],
    #      'num_episodes': []
    #      }
    # for item in peer.state_values.items():
    #     d_greedy['state'].append(item[0])
    #     d_greedy['value'].append(item[1][1]/item[1][0])
    #     d_greedy['num_episodes'].append(item[1][0])
    #
    # df_greedy = pd.DataFrame(d_greedy)
    # print(df_greedy)
    #
    #
    # players = [RandomPlayer()]
    # peer = PolicyEvaluator(players, 4, 5000)
    # peer.evaluate()
    # d_random = {'state': [],
    #      'value': [],
    #      'num_episodes': []
    #      }
    # for item in peer.state_values.items():
    #     d_random['state'].append(item[0])
    #     d_random['value'].append(item[1][1]/item[1][0])
    #     d_random['num_episodes'].append(item[1][0])
    #
    # df_random = pd.DataFrame(d_random)
    #
    # pd.set_option('display.max_rows',None)
    # pd.set_option('display.max_columns', None)
    # pd.options.display.width = 0
    # df = df_greedy.merge(df_random, on='state', how='outer',
    #     suffixes=('_greedy','_random')
    #     ) .sort_values(by='value_greedy', ascending=False)
    #

    # df = pd.read_csv('s3://zeno-of-elea/misc/rl/state_values_2x2_greedy_vs_random_5k_games.csv')
    # print(df[df.columns[2:]].sum(axis=0)/5000)
    # print('saved')

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
