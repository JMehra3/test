import Arena
from MCTS import MCTS
from Qawale.QawaleGame import QawaleGame
from Qawale.keras.QawaleNNet import QawaleNNet as nn
import numpy as np
from utils import dotdict
import random


# ----------------------------------------------------
# Beispiel: Zufallsspieler für Qawale
# ----------------------------------------------------
class RandomQawalePlayer:
    def __init__(self, game):
        self.game = game

    def play(self, board):
        """
        Wählt unter allen gültigen Zügen zufällig einen aus.
        Die Spielklasse QawaleGame liefert getValidMoves() als Liste von (r,c).
        Daraus bauen wir ein 1D-Array und wählen zufällig eine gültige Aktion.
        """
        valid_moves_positions = self.game.getValidMoves(board, 1)  # Liste (r, c)
        valids = [0] * self.game.getActionSize()  # Länge 16 bei 4x4
        for (r, c) in valid_moves_positions:
            valids[r * 4 + c] = 1

        # Aus den gültigen Indizes zufällig wählen
        valid_indices = [i for i, valid in enumerate(valids) if valid == 1]
        return random.choice(valid_indices) if valid_indices else 0


# ----------------------------------------------------
# Beispiel: Menschlicher Spieler für Qawale (Konsolenmodus)
# ----------------------------------------------------
class HumanQawalePlayer:
    def __init__(self, game):
        self.game = game

    def play(self, board):
        """
        Lässt den Menschen interaktiv einen Zug auswählen.
        Da QawaleGame.getValidMoves() (r,c)-Paare liefert,
        fragen wir den Benutzer nach Zeile und Spalte.
        Wir bauen daraus die Aktion row*4 + col.
        """
        valid_moves_positions = self.game.getValidMoves(board, 1)
        valids = [0] * self.game.getActionSize()
        for (r, c) in valid_moves_positions:
            valids[r * 4 + c] = 1

        # Optional: Board in Textform anzeigen
        self.display_textboard(board)

        while True:
            try:
                inp = input("Gib deinen Zug ein (Zeile und Spalte mit Leerzeichen, z.B. '1 2'): ")
                row_str, col_str = inp.strip().split()
                row, col = int(row_str), int(col_str)
                if (0 <= row < 4) and (0 <= col < 4):
                    action = row * 4 + col
                    if valids[action] == 1:
                        return action
                print("Ungültiger Zug. Bitte erneut versuchen.")
            except Exception:
                print("Eingabe ungültig. Bitte z.B. '1 2' eingeben.")

    def display_textboard(self, board):
        """
        Zeigt die untersten Steine (Index 0 im Stapel) in Textform an.
        """
        print("\nAktuelles Board (unterste Steine):")
        for r in range(4):
            row_repr = []
            for c in range(4):
                stack = board[r][c]
                row_repr.append(stack[0] if len(stack) > 0 else ".")
            print(" ".join(row_repr))
        print()


# ----------------------------------------------------
# Haupt-Teil, entspricht dem bisherigen pit.py-Aufbau
# ----------------------------------------------------

# 1. Initialisiere ein Qawale-Spiel
g = QawaleGame()

# 2. Lege die Spieler fest
rp = RandomQawalePlayer(g).play
hp = HumanQawalePlayer(g).play

# 3. Initialisiere das Keras-Neural-Net und lade ein vorhandenes Modell
n1 = nn(g)
# Pfad ggf. anpassen, falls ein trainiertes Modell existiert
# n1.load_checkpoint('./checkpoint/', 'best_qawale.pth.tar')

# 4. Erzeuge die MCTS-Instanz
args1 = dotdict({'numMCTSSims': 50, 'cpuct': 1.0})
mcts1 = MCTS(g, n1, args1)

# Aus der MCTS-Policy wählen wir die Aktion mit höchster Wahrscheinlichkeit
n1p = lambda x: np.argmax(mcts1.getActionProb(x, temp=0))

# 5. Wähle Gegner (hier Mensch oder Zufall)
human_vs_cpu = True
player2 = hp if human_vs_cpu else rp

# 6. Erzeuge Arena und spiele eine Reihe von Partien
arena = Arena.Arena(n1p, player2, g, g.draw)  # display=None oder g.draw, wenn pygame genutzt werden soll
print(arena.playGames(2, verbose=True))  # spielt 2 Spiele und gibt Ergebnisse aus
