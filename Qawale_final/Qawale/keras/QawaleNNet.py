# Falls benötigt, erstelle zusätzlich eine leere __init__.py im gleichen Ordner,
# damit diese Klassen als Modul importiert werden können.

############################################
# Datei: QawaleNNet.py (ähnlich wie TicTacToeNNet.py)
############################################
import sys
sys.path.append('..')
from utils import *

import argparse
import numpy as np
from tensorflow.keras.models import Model
from tensorflow.keras.layers import (Input, Reshape, Conv2D, BatchNormalization, Activation, Flatten, Dense, Dropout)
from tensorflow.keras.optimizers import Adam


class QawaleNNet:
    """
    Diese Klasse erstellt ein Keras-Modell für Qawale.
    Ähnlich aufgebaut wie TicTacToeNNet, jedoch für das 4x4-Spielfeld von Qawale.
    """

    def __init__(self, game, args):
        """
        :param game: Instanz von QawaleGame
        :param args: Hyperparameter (lr, dropout, epochs, batch_size, cuda, num_channels)
        """
        self.board_x, self.board_y = game.getBoardSize()
        self.action_size = game.getActionSize()
        self.args = args

        # Eingabeschicht (4x4)
        self.input_boards = Input(shape=(self.board_x, self.board_y))

        # Reshape zu (4,4,1)
        x_image = Reshape((self.board_x, self.board_y, 1))(self.input_boards)

        # Convolution 1
        h_conv1 = Conv2D(self.args.num_channels, 3, padding='same')(x_image)
        h_conv1 = BatchNormalization(axis=3)(h_conv1)
        h_conv1 = Activation('relu')(h_conv1)

        # Convolution 2
        h_conv2 = Conv2D(self.args.num_channels, 3, padding='same')(h_conv1)
        h_conv2 = BatchNormalization(axis=3)(h_conv2)
        h_conv2 = Activation('relu')(h_conv2)

        # Flatten
        h_conv2_flat = Flatten()(h_conv2)

        # Vollverbundene Schicht 1
        s_fc1 = Dense(64)(h_conv2_flat)
        s_fc1 = BatchNormalization(axis=1)(s_fc1)
        s_fc1 = Activation('relu')(s_fc1)
        s_fc1 = Dropout(self.args.dropout)(s_fc1)

        # Vollverbundene Schicht 2
        s_fc2 = Dense(64)(s_fc1)
        s_fc2 = BatchNormalization(axis=1)(s_fc2)
        s_fc2 = Activation('relu')(s_fc2)
        s_fc2 = Dropout(self.args.dropout)(s_fc2)

        # Policy-Ausgabe (π)
        self.pi = Dense(self.action_size, activation='softmax', name='pi')(s_fc2)
        # Value-Ausgabe (v)
        self.v = Dense(1, activation='tanh', name='v')(s_fc2)

        self.model = Model(inputs=self.input_boards, outputs=[self.pi, self.v])
        self.model.compile(
            loss=['categorical_crossentropy', 'mean_squared_error'],
            optimizer=Adam(self.args.lr)
        )
