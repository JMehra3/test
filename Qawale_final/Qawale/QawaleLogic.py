import random


class QawaleLogic:
    def __init__(self):
        # 4×4-Spielfeld, in jeder Zelle ein Stapel (Liste)
        self.rows = 4
        self.cols = 4
        self.board = [[[] for _ in range(self.cols)] for _ in range(self.rows)]

        # Insgesamt 8 Steine Blau (B), 8 Steine Rot (R), 8 Gelb (G) zum Aufbau
        self.stones_blue = 8
        self.stones_red = 8

        # In jede der 4 Ecken 2 gelbe Steine
        for (r, c) in [(0, 0), (0, 3), (3, 0), (3, 3)]:
            self.board[r][c] = ["G", "G"]

        # Zufälliger Startspieler
        self.current_player = random.choice(["B", "R"])

        self.winner = None
        self.game_over = False

    def place_stone_on_stack(self, row, col):
        """
        Einen neuen Stein unten in den Stapel legen (Index 0).
        """
        if self.current_player == "B" and self.stones_blue > 0:
            self.board[row][col].insert(0, "B")
            self.stones_blue -= 1
        elif self.current_player == "R" and self.stones_red > 0:
            self.board[row][col].insert(0, "R")
            self.stones_red -= 1

    def distribute_stack(self, path_positions):
        """
        Verteile die Steine von oben nach unten (oberster Stein = Ende der Liste).
        Jeder verteilte Stein kommt unten (Index 0) auf den Zielstapel.
        """
        if len(path_positions) < 2:
            return

        start = path_positions[0]
        stack = self.board[start[0]][start[1]]
        self.board[start[0]][start[1]] = []

        # Stapel reversed durchgehen — oberster Stein ist am Listenende
        reversed_stack = list(reversed(stack))
        for i, stone in enumerate(reversed_stack):
            if i + 1 < len(path_positions):
                nxt = path_positions[i + 1]
                self.board[nxt[0]][nxt[1]].insert(0, stone)

    def check_winner(self):
        """
        Gewonnen hat, wer eine Viererreihe (waagerecht, senkrecht, diagonal)
        aus den untersten Steinen bildet (Index 0 im Stapel), also 'von unten betrachtet'.
        """
        # Unterster Stein im Stapel = board[r][c][ -1? ] => nein, hier index 0
        # Falls Stapel leer, None
        lowest = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        for r in range(self.rows):
            for c in range(self.cols):
                if len(self.board[r][c]) > 0:
                    lowest[r][c] = self.board[r][c][0]  # unterster Stein

        def is_four_in_a_row(lst):
            return lst.count(lst[0]) == 4 and lst[0] in ("B", "R")

        # Horizontal
        for r in range(self.rows):
            row_check = [lowest[r][c] for c in range(self.cols)]
            if row_check[0] and is_four_in_a_row(row_check):
                self.game_over = True
                self.winner = row_check[0]
                return

        # Vertikal
        for c in range(self.cols):
            col_check = [lowest[r][c] for r in range(self.rows)]
            if col_check[0] and is_four_in_a_row(col_check):
                self.game_over = True
                self.winner = col_check[0]
                return

        # Diagonal ↘
        diag1 = [lowest[i][i] for i in range(self.rows)]
        if diag1[0] and is_four_in_a_row(diag1):
            self.game_over = True
            self.winner = diag1[0]
            return

        # Diagonal ↙
        diag2 = [lowest[i][self.cols - 1 - i] for i in range(self.rows)]
        if diag2[0] and is_four_in_a_row(diag2):
            self.game_over = True
            self.winner = diag2[0]
            return

        # Unentschieden, wenn alle Steine weg und keiner hat eine Reihe
        if self.stones_blue == 0 and self.stones_red == 0 and not self.winner:
            self.game_over = True
            self.winner = "Unentschieden"

    def switch_player(self):
        self.current_player = "R" if self.current_player == "B" else "B"
