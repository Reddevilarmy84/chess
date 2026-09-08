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

class Defeated:
    """
    the class discribes a box
    with defeated pieces.
    """

    def __init__(self):
        self.white = []
        self.black = []

    # display lines with defeated pieces
    def view(self):
        print(f"{' '.join(map(str, self.white))}")
        print(f"{' '.join(map(str, self.white))}")

    # add a piece in corresponding list, depending on the color
    def add(self, obj):
        if obj is not None:
            self.__dict__[obj.color].append(obj)

class ChessDesk:
    fill_char = "*"
    cor_table = {
        k:v for v,k in chain(enumerate("abcdefgh"), enumerate("12345678"))
    }

    @classmethod
    def convert(cls, coordinates: str) -> tuple:
        return tuple(
            cls.cor_table.get(char.lower()) for char in coordinates
        )

    def __init__(self):
        self.matrix = [
            [self.fill_char for _ in range(8)]
            for _ in range(8)
        ]

    def __str__(self):
        return ''.join(
            f"{' '.join(row)}\n"
            for row in self.matrix
        )

    def __getitem__(self, coordinates: str):
        col, row = self.convert(coordinates)
        return self.matrix[7 - row][col]

    def __setitem__(self, coordinates, obj):
        col, row = self.convert(coordinates)
        self.matrix[7 - row][col] = obj

    def __delitem__(self, coordinates):
        col, row = self.convert(coordinates)
        self.matrix[7 - row][col] = self.fill_char

    def display(self):
        u_indent = 2
        d_indent = 2
        l_indent = os.get_terminal_size().columns // 2 - 16

        print("\n" * u_indent)

        for line_num, row in enumerate(self.matrix, start=1):
            print(f"{' ' * l_indent}{9 - line_num}   {'    '.join(row)}\n")

        print(" " * (l_indent - 1) + "    ".join(" ABCDEFGH"))

        print("\n" * d_indent)