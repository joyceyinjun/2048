import copy
import sys
sys.path += ['../game']

import numpy as np
import ast

from board import *
from player import *
from game import *
from utils import FileHandler, MonteCarloSimulator


class PolicyEvaluator:
    """
    evaluate policy using state value function

    policy here can be determined by either
    1. type of player (random player etc), or
    2. q-values (which a learned player uses)

    in both these cases, games will be simulated and recorded

    besides, policy can also be evaluated directly from
    game recordings

    if a q-value file is provided, the player
    needs to be a ComputerPlayer
    """
    def __init__(self, xPlayers, xSizeOfBoard, xNumRounds,
                 xQValuesFileName=None,
                 xGameRecordingFileName=None):
        self.players = xPlayers
        self.size_of_board = xSizeOfBoard
        self.num_rounds = xNumRounds
        if xQValuesFileName is not None:
            self.q_values = FileHandler().loadFromPickle(xQValuesFileName)
        else:
            self.q_values = None

        if xGameRecordingFileName is not None:
            self.game_episodes = FileHandler().loadFromPickle(xGameRecordingFileName)
        else:
            self.game_episodes = None

        self.state_values = None
        self.state_action_values = None

    def simulate(self):
        """
        monte carlo simulate game episodes
        """
        mcer = MonteCarloSimulator(
                self.players, self.q_values, self.size_of_board,
                self.num_rounds
        )
        mcer.run()
        self.game_episodes = mcer.recordings

    @staticmethod
    def updateValues(xDictionary, xKey, xValue,
                     xDictionaryNext=None, xKeyNext=None):
        """
        update dictionary with value to key
        xDictionary entry:
        {xKey: [xCount, xValue]}
        """
        xDictionary.setdefault(xKey, [1e-4, 0])
        if xKeyNext is None:
            xDictionary[xKey] = [
                xDictionary[xKey][0] + 1,
                xDictionary[xKey][1] + xValue
            ]
        else:
            count_next, value_next = xDictionaryNext.get(xKeyNext, [1e-4, 8e-5])
            xDictionary[xKey] = [
                xDictionary[xKey][0] + 1,
                xDictionary[xKey][1] + xValue + value_next/count_next
            ]

    def getValueFunctions(self, xMethod,
                          stateFlag=True,
                          stateActionFlag=True):
        """
        calculate the state value functions
        from game episodes

        xMethod = mc - monte carlo
        xMethod = td - temporal difference
        """
        state_values, state_action_values = {}, {}

        if xMethod.lower() == 'mc':
            for episode in self.game_episodes:
                # monte carlo method
                # starting from termination of episode
                value = 0
                for step in reversed(episode):
                    # considering one-player game now
                    # player id discarded
                    _, state, action, reward, state_next = step
                    value += reward

                    if stateFlag:
                        key = str(tuple(state))
                        self.updateValues(state_values, key, value)

                    if stateActionFlag:
                        key = (str(tuple(state)), action)
                        self.updateValues(state_action_values, key, value)

        if xMethod.lower() == 'td':
            # randomize all steps in all episodes
            steps = []
            for episode in self.game_episodes:
                steps += episode
            random.seed(87112)
            random.shuffle(steps)
            for i, step in enumerate(steps):
                _, state, action, reward, state_next = step
                key_next = str(tuple(state_next))

                if stateFlag:
                    key_current = str(tuple(state))
                    self.updateValues(state_values, key_current, reward,
                                      state_values, key_next)
                if stateActionFlag:
                    key_current = (str(tuple(state)), action)
                    self.updateValues(state_action_values, key_current, reward,
                                      state_values, key_next)

        return state_values, state_action_values

    def evaluate(self):
        self.simulate()
        self.state_values, self.state_action_values\
            = self.getValueFunctions('mc')


class Trainer:
    def __init__(self, xTag, xNumPlayers,
                 xSizeOfBoard, xNumGames,
                 xTotalEpoch, xStartEpoch=1,
                 xQC=False):
        self.tag = xTag
        self.num_players = xNumPlayers
        self.size_of_board = xSizeOfBoard
        self.num_games = xNumGames
        self.QC = xQC
        self.epoch = xStartEpoch
        self.epoch_total = xTotalEpoch
        self.memory_decay = 0.9

        self.game_recordings = None
        self.q_values, self.q_values_delta = None, None
        self.file_handler = FileHandler()
        self.game_recordings_file_name = None
        self.q_values_file_name = None

    def updateFileNames(self):
        file_prefix = 'misc/rl/{}_{}x{}_{}'.format(
                self.tag, self.size_of_board, self.size_of_board,
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
        self.updateFileNames()

        players = []
        for i in range(self.num_players):
            players.append(LearnedPlayer(xId=i)
                           )

        batch_player = MonteCarloSimulator(players, self.size_of_board,
                                   self.q_values,
                                   self.num_games)
        batch_player.run()
        self.game_recordings = batch_player.recordings
        self.file_handler.saveToPickle(self.game_recordings,
                                self.game_recordings_file_name)

        self.epoch += 1
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
            for step in reversed(recording):
                _, state, action, reward, state_next = step
                value += reward

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
                            count*self.memory_decay+count_delta,
                            value*self.memory_decay+value_delta
                            ]

        self.file_handler.saveToPickle(self.q_values,
                                       self.q_values_file_name)
        if self.QC:
            print("""
            saved {} state-action pairs to {}
            """.format(len(self.q_values),self.q_values_file_name))

    def execute(self):
        while self.epoch <= self.epoch_total:
            self.playGames()
            self.getCurrentQValues()
            self.updateQValues()

    def checkStats(self, xEpochs):
        print('epoch | episode length avg | std')
        print('-'*40)
        for epoch in xEpochs:
            self.epoch = epoch
            self.updateFileNames()
            self.game_recordings = self.file_handler.loadFromPickle(
                                self.game_recordings_file_name)
            lengths = np.array([
                len(recording) for recording in self.game_recordings
            ])

            print('{:6s} | {:.3f} | {:.3f} '.format(
                str(self.epoch), np.average(lengths), np.std(lengths)
            ))

    def checkState(self, xEpochs, xState=None):
        cnt = 0
        for epoch in xEpochs:
            self.epoch = epoch
            self.updateFileNames()

            self.q_values = self.file_handler.loadFromPickle(
                self.q_values_file_name
            )
            if self.QC:
                print('loaded state values from {}'.format(
                    self.q_values_file_name
                ))

            if xState is None:
                xState = random.sample(self.q_values.keys(),1)[0][0]
            if cnt == 0:
                print('target state')
                print(np.asarray(ast.literal_eval(xState)).reshape(self.size_of_board,-1))

            print('{:20s} | q-value |  # experiments'.format('action'))
            print('-'*60)
            q_values, actions  = [], []

            for state_action in self.q_values.keys():
                # print(state_action, self.q_values[state_action])
                if state_action[0] == xState:
                    count_sa, value_sa = self.q_values[state_action]
                    q_values.append(value_sa/count_sa)
                    actions.append(state_action[1])
                    print('{:20s} |  {:.3f}  | {:.2f} '.format(
                              str(state_action[1]), value_sa/count_sa, count_sa
                    ))
            print('\n')
            cnt += 1
