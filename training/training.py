import copy
import sys
sys.path += ['../game']


from collections import Counter
import numpy as np
import pandas as pd
import time
import pickle
import boto3

from board import *
from player import *
from game import *

BUCKET = 'zeno-of-elea'


class BatchPlayer:
    """
    BATCHPLAYER
    """

    def __init__(self, xPlayers, xSizeOfBoard, xQValues, xNumRounds):
        self.players = xPlayers
        self.size_of_board = xSizeOfBoard
        self.q_values = xQValues
        self.num_rounds = xNumRounds
        self.recordings = []

    def recordScores(self, xGame):
        for i in range(len(self.players)):
            score, _ = xGame.board.getPlayerStatus(i)
            self.scores[i].append(score)

    def recordGame(self, xGame):
        self.recordings.append(xGame.recording)

    def run(self):
        start_time = time.time()
        for k in range(self.num_rounds):
            board = Board(self.size_of_board)
            board.initForGame(self.players)
            game = Game(xBoard=board, xPlayers=self.players,
                        xQValues=self.q_values,
                        xRecordGame=True)
            game.play()
            self.recordGame(game)
            # self.recordScores(game)
            # if (k + 1) % 5000 == 0:
            #     print('games played: {}'.format(k + 1))
            #     print('elapsed time: {:.3f} seconds'.format(time.time() - start_time))
            #     start_time = time.time()

    def getAverageScores(self):
        scores_avg = {}
        for i in range(len(self.players)):
            scores_avg[self.players[i].name] = sum(self.scores[i])
            scores_avg[self.players[i].name] /= self.num_rounds
        return pd.DataFrame(scores_avg, index=['Average Score'])

    def getScoreDistribution(self):
        counts = []
        for i in range(len(self.scores)):
            counts.append(Counter(self.scores[i]))

        df = pd.DataFrame(counts).transpose().sort_index().rename(
            columns={z.id: z.name for z in self.players}
        ).fillna(0).astype(int)
        df.index_name = 'score'

        return df


class FileHandler:
    @staticmethod
    def saveToPickle( xContent, xFileName, xBucket=BUCKET):
        pickle_obj = pickle.dumps(xContent)
        s3_resource = boto3.resource('s3')
        s3_resource.Object(xBucket, xFileName).put(Body=pickle_obj)

    @staticmethod
    def loadFromPickle(xFileName, xBucket=BUCKET):
        s3_resource = boto3.resource('s3')
        pickle_obj = s3_resource.Bucket(xBucket).Object(xFileName).get()['Body'].read()
        return pickle.loads(pickle_obj)


class Trainer:
    def __init__(self, xNumPlayers,
                 xSizeOfBoard, xNumGames, xQC=False):
        self.num_players = xNumPlayers
        self.size_of_board = xSizeOfBoard
        self.num_games = xNumGames
        self.QC = xQC
        self.epoch = 0

        self.game_recordings = None
        self.q_values, self.q_values_delta = None, None
        self.file_handler = FileHandler()
        self.game_recordings_file_name = None
        self.q_values_file_name = None

    def updateFileNames(self):
        file_prefix = 'misc/rl/{}x{}_{}'.format(
                self.size_of_board, self.size_of_board,
                self.num_games)
        file_suffix = 'ep{:04d}.pkl'.format(self.epoch)
        self.game_recordings_file_name = '{}/recordings/{}'.format(
            file_prefix, file_suffix
        )
        self.q_values_file_name = '{}/q_values/{}'.format(
                file_prefix, file_suffix
        )

    def playGames(self):
        """
        batch play mode
        """
        self.epoch += 1
        self.updateFileNames()

        players = []
        for i in range(self.num_players):
            players.append(ComputerPlayer(xId=i))

        batch_player = BatchPlayer(players, self.size_of_board,
                                   self.q_values,
                                   self.num_games)
        batch_player.run()
        self.game_recordings = batch_player.recordings
        self.file_handler.saveToPickle(self.game_recordings,
                                self.game_recordings_file_name)
        if self.QC:
            print('saved {} recordings to {}'.format(
                len(self.game_recordings), self.game_recordings_file_name
            ))

    @staticmethod
    def updateValues(xDictionary, xKey, xValue):
        """
        update dictionary with value to key
        xDictionary entry:
        {xKey: [xCount, xValue]}
        """
        xDictionary.setdefault(xKey, [0, 0])
        xDictionary[xKey] = [
            xDictionary[xKey][0] + 1,
            xDictionary[xKey][1] + xValue
        ]

    def getCurrentQValues(self):
        """
        calculate the state value functions
        and the state-action value functions
        from game recordings of current epoch
        """
        if self.game_recordings is None:
            self.game_recordings = self.file_handler.loadFromPickle(
                            self.game_recordings_file_name)
            print('loaded {} recordings from {}'.format(
                len(self.game_recordings),self.game_recordings_file_name
            ))

        self.q_values_delta = {}
        for recording in self.game_recordings:
            value = 0  # reset the value at termination state to 0
            for snapshot in reversed(recording):
                _, state, action, score, state_next = snapshot
                value += score

                key = (str(tuple(state)), action)
                self.updateValues(self.q_values_delta, key, value)

    def updateQValues(self):
        """
        update q_values with q_values_delta
        """
        if self.q_values is None:
            self.q_values = self.q_values_delta
        else:
            for key in self.q_values_delta.keys():
                self.q_values.setdefault(key, [0, 0])
                count, value = self.q_values[key]
                count_delta, value_delta = self.q_values_delta[key]
                self.q_values[key] = [
                            count/2+count_delta,
                            value/2+value_delta
                            ]

        self.file_handler.saveToPickle(self.q_values,
                                       self.q_values_file_name)
        if self.QC:
            print("""
            saved {} state-action pairs to {}
            """.format(len(self.q_values),self.q_values_file_name))

    def execute(self):
        self.playGames()
        self.getCurrentQValues()
        self.updateQValues()

    def check(self, xEpoch):
        self.epoch = xEpoch
        self.updateFileNames()

        self.q_values = self.file_handler.loadFromPickle(
            self.q_values_file_name
        )
        if self.QC:
            print('loaded state values from {}'.format(
                self.q_values_file_name
            ))
        state = str(tuple([0,1,2,1]))

        print('{:30s} | q-value |  # experiments'.format('state-action pair'))
        print('-'*60)
        q_values, actions  = [], []
        for state_action in self.q_values.keys():
            # print(state_action, self.q_values[state_action])
            if state_action[0] == state:
                count_sa, value_sa = self.q_values[state_action]
                q_values.append(value_sa/count_sa)
                actions.append(state_action[1])
                print('{:30s} |  {:.3f}  | {:.2f} '.format(
                          str(state_action), value_sa/count_sa, count_sa
                ))
