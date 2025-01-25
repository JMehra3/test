############################################
# Datei: QawaleNNetWrapper.py (ähnlich wie NNet(2).py)
############################################
import os
import time
import numpy as np
from NeuralNet import NeuralNet   # Basisklasse, NICHT verändern!

import argparse
from .QawaleNNet import QawaleNNet

class QawaleNNetWrapper(NeuralNet):
    """
    Eine Wrapper-Klasse für das Qawale-Keras-Modell.
    Entspricht in etwa der Struktur von NNet(2).py.
    """

    def __init__(self, game):
        # Default-Argumente lassen sich hier anpassen
        self.args = {
            'lr': 0.001,
            'dropout': 0.3,
            'epochs': 10,
            'batch_size': 64,
            'cuda': False,
            'num_channels': 64,
        }
        # Konvertierung in ein brauchbares Objekt
        self.args = type('dotdict', (dict,), self.args)()

        self.nnet = QawaleNNet(game, self.args)
        self.board_x, self.board_y = game.getBoardSize()
        self.action_size = game.getActionSize()

    def train(self, examples):
        """
        :param examples: Liste von (board, pi, v)
                         board: np.array (4,4)
                         pi: np.array der Länge action_size
                         v: float in [-1, 1]
        """
        input_boards, target_pis, target_vs = list(zip(*examples))
        input_boards = np.asarray(input_boards)
        target_pis = np.asarray(target_pis)
        target_vs = np.asarray(target_vs)

        self.nnet.model.fit(
            x=input_boards,
            y=[target_pis, target_vs],
            batch_size=self.args.batch_size,
            epochs=self.args.epochs
        )

    def predict(self, board):
        """
        :param board: np.array (4,4)
        :return: pi, v (jeweils np.array)
        """
        # board vorbereiten
        board = board[np.newaxis, :, :]
        pi, v = self.nnet.model.predict(board, verbose=False)
        return pi[0], v[0]

    def save_checkpoint(self, folder='checkpoint', filename='checkpoint.pth.tar'):
        """
        Speichert die Modellgewichte im .h5-Format
        """
        # Dateiendung ändern
        filename = filename.split(".")[0] + ".h5"
        filepath = os.path.join(folder, filename)

        if not os.path.exists(folder):
            print("Checkpoint Directory does not exist! Making directory {}".format(folder))
            os.mkdir(folder)
        else:
            print("Checkpoint Directory exists!")

        self.nnet.model.save_weights(filepath)

    def load_checkpoint(self, folder='checkpoint', filename='checkpoint.pth.tar'):
        """
        Lädt die Modellgewichte aus einer .h5-Datei
        """
        # Dateiendung ändern
        filename = filename.split(".")[0] + ".h5"
        filepath = os.path.join(folder, filename)

        if not os.path.exists(filepath):
            raise FileNotFoundError("No model in path '{}'".format(filepath))

        self.nnet.model.load_weights(filepath)
