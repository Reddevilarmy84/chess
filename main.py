import time
import os
from itertools import chain

# chess game (pet project by Alexander Postavets)

class Logger():
    """
    The class describes the
    event logging in the game.
    """
  
    def __init__(self):
        self._log = list('' for line in range(4))

    # add new info record
    def info(self, *args):
        for arg in args:
            self._log.append(f" INFO {str(arg)}")
        self._log = self._log[-4:]

    # add new err record
    def err(self, *args):
        for arg in args:
            self._log.append(f" INFO {str(arg)}")
        self._log = self._log[-4:]

    # display the log
    def display(self):
        for line in reversed(self._log):
            print(line)
        print()


class ChessDesk:

    # символ пустой клетки
    fill_char = "\u25a2"

    # таблица соответствия координат
    horizontal = "ABCDEFGH"
    vertical = "87654321"

    @classmethod
    def chess_to_matrix(cls, coordinates: str) -> tuple(int, int):
        x, y = coordinates.upper()
        return cls.horizontal.index(x), cls.vertical.index(y)

    @classmethod
    def matrix_to_chess(cls, coordinates: tuple(int, int)) -> str:
        x, y = coordinates
        return cls.horizontal[x] + cls.vertical[y]

    def __init__(self):
        self.matrix = [
            [self.fill_char for _ in range(8)]
            for _ in range(8)
        ]

        self.defeated = []

    def __str__(self):
        return ''.join(
            f"{' '.join(row)}\n"
            for row in self.matrix
        )

    def __getitem__(self, coordinates: str):
        x, y = self.chess_to_matrix(coordinates)
        return self.matrix[y][x]

    def __setitem__(self, coordinates, obj):
        x, y = self.chess_to_matrix(coordinates)
        self.matrix[y][x] = obj

    def __delitem__(self, coordinates):
        x, y = self.chess_to_matrix(coordinates)
        self.matrix[y][x] = self.fill_char

    def display(self):
        u_indent = 2
        d_indent = 2
        l_indent = os.get_terminal_size().columns // 2 - 16

        print("\n" * u_indent)

        for line_num, row in enumerate(self.matrix, start=1):
            print(f"{' ' * l_indent}{9 - line_num}   {'    '.join(row)}\n")

        print(" " * (l_indent - 1) + "    ".join(" ABCDEFGH"))

        print("\n" * d_indent)