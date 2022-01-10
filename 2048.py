from utils import *

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
    board.occupy(1,1,Block(xValue=1, xPlayerId=0))
    board.occupy(2,2,Block(xValue=2, xPlayerId=0))

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

def batchplay(xSizeOfBoard, xNumGames):
    """
    batch play mode
    """
    players = [
        ComputerPlayer(xName='Mozart', xId=0),
    ]
    size_of_board = xSizeOfBoard
    num_games = xNumGames
    batch_player = BatchPlayer(players, size_of_board, num_games)
    batch_player.run()

    file_name = 'misc/recordings_2x2_{}.pkl'.format(num_games)
    saveToPickle(batch_player.recordings, file_name)
    return file_name

def calculateValueFunction(file_name, xNumGames):
    # loading from pickle
    num_games = xNumGames
    recordings = loadFromPickle(file_name)
    print('loaded {} recordings'.format(len(recordings)))

    state_action_pair_values = {}
    state_values = {}
    for recording in recordings:
        value = 0
        for snapshot in reversed(recording):
            _, state, action, score = snapshot
            value += score
            key = (str(tuple(state)), action)
            if not state_action_pair_values.get(key):
                state_action_pair_values[key] = [1, value]
            else:
                count, value_cum = state_action_pair_values.get(key)
                state_action_pair_values[key] = [count + 1, value_cum + value]
            key = str(tuple(state))
            if not state_values.get(key):
                state_values[key] = [1, value]
            else:
                count, value_cum = state_values.get(key)
                state_values[key] = [count + 1, value_cum + value]

    df_state_values = pd.DataFrame(state_values,
                                   index=['count', 'score']
                                   ).transpose()
    df_state_action_pair_values = \
        pd.DataFrame(state_action_pair_values,
                     index=['count', 'score']
                     ).transpose()

    df = {'state_values': df_state_values,
          'state_action_pair_values': df_state_action_pair_values
          }
    file_name = 'misc/value_functions_2x2_{}.pkl'.format(num_games)
    saveToPickle(df, file_name)
    return file_name

def main():
    num_games = 1000000
    # recording_file = batchplay(2, num_games)
    # print('saved', recording_file)
    recording_file = 'misc/recordings_2x2_{}.pkl'.format(num_games)
    value_file = calculateValueFunction(recording_file, num_games)
    print('saved', value_file)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
