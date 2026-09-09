import os
from itertools import chain

# chess game (pet project by Alexander Postavets)
class GameError(Exception):
    ...

class Logger():
    """
    Класс описывает простой логер
    с методом отображения в консоли группы
    записей для описания хода игры.
    """
  
    def __init__(self):
        self._log = list('' for line in range(4))

    # add new info record
    def info(self, *args):
        for arg in args:
            self._log.append(f" INFO {str(arg)}")

    # add new err record
    def err(self, *args):
        for arg in args:
            self._log.append(f" INFO {str(arg)}")

    # display the log
    def display(self):
        for line in self._log[-1:-5:-1]:
            print(line)


class ChessDesk:
    """
    Класс описывает шахматную доску.
    Изменяемая коллекция в виде матрицы.
    Доступ к элементам осуществляется через
    матричные координаты согласно правилам игры
    в шахматы. К регистру не чувствителен.
    Пример:
    desk = ChessDesk()
    obj = desk["A1"]
    desk["B3"] = obj
    del desk["h8"]
    """
    # символ пустой клетки
    fill_char = "\u25a2"

    # таблица соответствия координат
    horizontal = "ABCDEFGH"
    vertical = "87654321"

    @classmethod
    def chess_to_matrix(cls, coordinates: str) -> tuple[int, int]:
        """
        Метод для преобразования
        шахматных координат в списочные индексы
        для доступа к элементам матрицы.
        Input(str): "A1"
        Output(tuple[int, int]): (0, 7)
        """
        x, y = coordinates.upper()
        return cls.horizontal.index(x), cls.vertical.index(y)

    @classmethod
    def matrix_to_chess(cls, coordinates: tuple[int, int]) -> str:
        """
        Метод для преобразования
        кортежа из списочных индексов
        в строку шахматных координат.
        Input(tuple[int, int]): (0, 7)
        Output(str): "A1"
        """
        x, y = coordinates
        return cls.horizontal[x] + cls.vertical[y]

    def __init__(self):
        # матрица для хранения обьектов шахматных фигур
        self.matrix = [
            [self.fill_char for _ in range(8)]
            for _ in range(8)
        ]
        # список поверженных фигур
        self.defeated = []

    def __repr__(self):
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
        # фигура хранит свои текущие шахматные координаты
        obj.coordinates = coordinates

    def __delitem__(self, coordinates):
        x, y = self.chess_to_matrix(coordinates)
        obj = self.matrix[y][x]
        # съеденная фигура попадает в список self.defeated
        if isinstance(obj, Piece):
            self.defeated.add(obj)
        self.matrix[y][x] = self.fill_char

    def display(self):
        u_indent = 1
        d_indent = 1
        l_indent = os.get_terminal_size().columns // 2 - 16

        print("\n" * u_indent)

        for line_num, row in enumerate(self.matrix, start=1):
            print(f"{' ' * l_indent}{9 - line_num}   {'    '.join(row)}\n")

        print(" " * (l_indent - 1) + "    ".join(" ABCDEFGH"))

        print()

        print(' '.join(map(str, self.defeated)))

        print("\n" * d_indent)