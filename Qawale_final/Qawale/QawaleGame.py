import pygame
import sys
import numpy as np

from Game import Game
from QawaleLogic import QawaleLogic

class QawaleGame(Game):
    """
    Diese Klasse erbt von der Game-Basisklasse[2] und behält die
    Funktionalitäten des Qawale-Spiels bei. Die Methoden get_valid_moves_setstone
    und get_valid_moves_distribute wurden zu einer getValidMoves()-Methode zusammengefasst.
    """

    def __init__(self, width=600, height=600):
        super().__init__()
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Qawale")
        self.clock = pygame.time.Clock()
        self.running = True

        self.logic = QawaleLogic()

        self.bg_color = (220, 220, 220)
        self.grid_color = (0, 0, 0)
        self.highlight_color = (0, 255, 0)
        self.blue = (0, 0, 255)
        self.red = (255, 0, 0)
        self.yellow = (255, 255, 0)

        self.cell_size = 100
        self.margin_left = 100
        self.margin_top = 100

        self.distributing = False
        self.distribution_path = []
        self.selected_stack = None
        self.placed_stone_cell = None

    ##################################################
    # Methoden entsprechend der Struktur von Game[2] #
    ##################################################

    def getInitBoard(self):
        """Gibt das initiale Board aus der QawaleLogic zurück."""
        return self.logic.board

    def getBoardSize(self):
        """Gibt die Dimensionen des Boards zurück (Zeilen, Spalten)."""
        return (self.logic.rows, self.logic.cols)

    def getActionSize(self):
        """
        Gibt die Anzahl möglicher Aktionen zurück.
        Für Qawale wird dies hier vereinfacht gehandhabt.
        """
        return self.logic.rows * self.logic.cols

    def getNextState(self, board, player, action):
        """
        Übergang in den nächsten Zustand.
        In dieser vereinfachten Version wird die Logik über
        Mausinteraktionen gesteuert und nicht über 'action'.
        """
        return (board, -player)

    def getValidMoves(self, board=None, player=None):
        """
        Fasst get_valid_moves_setstone und get_valid_moves_distribute zu einer Methode zusammen.
        Wenn distributing == False, dann mögliche Felder zum Steinelegen,
        sonst mögliche Felder zum Verteilen.
        """
        if not self.distributing:
            moves = []
            for r in range(self.logic.rows):
                for c in range(self.logic.cols):
                    if len(self.logic.board[r][c]) > 0:
                        moves.append((r, c))
            return moves
        else:
            moves = []
            current_spot = self.distribution_path[-1]
            forbidden = self.distribution_path[-2] if len(self.distribution_path) >= 2 else None
            (sr, sc) = current_spot
            for (dr, dc) in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                rr, cc = sr + dr, sc + dc
                if 0 <= rr < self.logic.rows and 0 <= cc < self.logic.cols:
                    if (rr, cc) != forbidden:
                        moves.append((rr, cc))
            return moves

    def getGameEnded(self, board, player):
        """
        Prüft, ob das Spiel beendet ist.
        0 wenn weitergespielt wird, 1 wenn aktueller Spieler gewonnen hat,
        -1 wenn aktueller Spieler verloren hat, kleiner Wert für Unentschieden.
        """
        if self.logic.game_over:
            if self.logic.winner == "B" and player == 1:
                return 1
            if self.logic.winner == "R" and player == -1:
                return 1
            if self.logic.winner == "Unentschieden":
                return 1e-4
            return -1
        return 0

    def getCanonicalForm(self, board, player):
        """
        Gibt die kanonische Form des Boards zurück, hier unverändert.
        """
        return board

    def getSymmetries(self, board, pi):
        """
        Liefert symmetrische Versionen des Boards zurück.
        Für Qawale in dieser simplen Variante nicht genutzt.
        """
        return [(board, pi)]

    def stringRepresentation(self, board):
        """
        Gibt eine String-Repräsentation des Boards zurück
        (z.B. wichtig für MCTS-Hashing).
        """
        return str(board)

    ##################################################
    # Pygame-spezifische Methoden für Qawale          #
    ##################################################

    def run(self):
        while self.running:
            self.clock.tick(30)
            self.handle_events()
            self.update()
            self.draw()
        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not self.logic.game_over:
                self.handle_mouse_click(pygame.mouse.get_pos())

    def handle_mouse_click(self, pos):
        grid_pos = self.get_grid_pos_from_mouse(pos)
        if not grid_pos:
            return

        moves = self.getValidMoves()  # Neu aufgerufene, kombinierte Methode
        if not self.distributing:
            # Stein legen
            if grid_pos in moves:
                self.logic.place_stone_on_stack(*grid_pos)
                self.placed_stone_cell = grid_pos
                self.selected_stack = grid_pos
                self.distributing = True
                self.distribution_path = [grid_pos]
        else:
            # Stapel verlegen
            if grid_pos in moves:
                self.distribution_path.append(grid_pos)
                start_stack_size = len(self.logic.board[self.selected_stack[0]][self.selected_stack[1]])
                if len(self.distribution_path) - 1 == start_stack_size:
                    self.logic.distribute_stack(self.distribution_path)
                    self.distributing = False
                    self.distribution_path = []
                    self.placed_stone_cell = None
                    self.logic.check_winner()
                    if not self.logic.game_over:
                        self.logic.switch_player()

    def update(self):
        pass

    def draw(self):
        self.screen.fill(self.bg_color)

        # 4×4 Gitter
        for r in range(self.logic.rows + 1):
            y = self.margin_top + r * self.cell_size
            pygame.draw.line(self.screen, self.grid_color,
                             (self.margin_left, y),
                             (self.margin_left + self.logic.cols * self.cell_size, y), 2)
        for c in range(self.logic.cols + 1):
            x = self.margin_left + c * self.cell_size
            pygame.draw.line(self.screen, self.grid_color,
                             (x, self.margin_top),
                             (x, self.margin_top + self.logic.rows * self.cell_size), 2)

        # Stapel zeichnen
        for r in range(self.logic.rows):
            for c in range(self.logic.cols):
                stack = self.logic.board[r][c]
                x_center = self.margin_left + c * self.cell_size + self.cell_size // 2
                y_center = self.margin_top + r * self.cell_size + self.cell_size // 2
                offset = 0
                for stone in reversed(stack):
                    color = self.get_color_for_stone(stone)
                    pygame.draw.circle(self.screen, (0, 0, 0),
                                       (x_center, y_center - offset), 20, 2)
                    pygame.draw.circle(self.screen, color,
                                       (x_center, y_center - offset), 18)
                    offset += 10

        # Feld mit neuem Stein blau umranden
        if self.placed_stone_cell is not None:
            r, c = self.placed_stone_cell
            rx = self.margin_left + c * self.cell_size
            ry = self.margin_top + r * self.cell_size
            pygame.draw.rect(self.screen, self.blue,
                             (rx + 2, ry + 2, self.cell_size - 4, self.cell_size - 4), 3)

        font = pygame.font.SysFont(None, 28)
        if not self.logic.game_over:
            turn_text = "Aktueller Spieler: "
            turn_text += "Blau" if self.logic.current_player == "B" else "Rot"
            self.screen.blit(font.render(turn_text, True, (0, 0, 0)), (40, 30))

            # Gültige Felder markieren
            vs = self.getValidMoves()
            self.highlight_moves(vs)
        else:
            msg = "Spielende! "
            if self.logic.winner == "B":
                msg += "Blau hat gewonnen!"
            elif self.logic.winner == "R":
                msg += "Rot hat gewonnen!"
            elif self.logic.winner == "Unentschieden":
                msg += "Unentschieden!"
            else:
                msg += "Kein Sieger."
            self.screen.blit(font.render(msg, True, (0, 0, 0)), (40, 30))

        pygame.display.flip()

    def get_color_for_stone(self, stone):
        if stone == "B":
            return self.blue
        elif stone == "R":
            return self.red
        else:
            return self.yellow

    def highlight_moves(self, moves):
        for (r, c) in moves:
            rx = self.margin_left + c * self.cell_size
            ry = self.margin_top + r * self.cell_size
            pygame.draw.rect(self.screen, self.highlight_color,
                             (rx + 2, ry + 2, self.cell_size - 4, self.cell_size - 4), 3)

    def get_grid_pos_from_mouse(self, pos):
        mx, my = pos
        if (self.margin_left <= mx < self.margin_left + self.logic.cols * self.cell_size and
                self.margin_top <= my < self.margin_top + self.logic.rows * self.cell_size):
            col = (mx - self.margin_left) // self.cell_size
            row = (my - self.margin_top) // self.cell_size
            return (row, col)
        return None
