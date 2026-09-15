from itertools import chain
import os
from collections import defaultdict
import random
from copy import copy



class GameError(Exception):
    """
    Исключение, возникающее
    при попытке нарушить
    правила игры.
    """
    ...


class Logger:
    """
    Логер.
    """
    len_log = 4
    
    def __init__(self):
        self.log = ["\n" for line in range(5)]
        self.records = 0
    
    def info(self, *args):
        for arg in args:
            self.records += 1
            self.log.append(f" {self.records} INFO: " + str(arg))
        
    def err(self, *args):
        for arg in args:
            self.records += 1
            self.log.append(f" {self.records} ERROR: " + str(arg))
            
    def display(self):
        for line in self.log[-1:-self.len_log - 1:-1]:
            print(line)
            
            
class ChessDesk:
    """
    Класс описывает шахматную доску.
    Является изменяемой коллекцией.
    Индекс не чуствителен к регистру.
    Пример работы с элементами:
    obj = desk["A4"] # получение элемента.
    desk["b7"] = obj # установка элемента.
    """
    
    # символ пустой клетки шахматной доски
    fill_char = [
        '\u25a2',
        ' '
        ][0]
    
    # таблица соответствия координат
    horizontal = "ABCDEFGH"
    vertical = "87654321"
    
    # линейки для легаси функции interval
    #verticals = '_12345678'
    #horizontals = '_abcdefgh'
    
    # преобразование шахматных координат в матричные
    @classmethod
    def chess_to_matrix(cls, coordinates: str) -> tuple[int, int]:
        """
        Функция для преобразования
        шахматных координат в матричные
        input(str): "A1"
        output(tuple(int, int)): (0, 7)
        """ 
        x, y = coordinates.upper()
        if not x in cls.horizontal or not y in cls.vertical:
            raise GameError(f"не верные координаты {x}{y}")
        return cls.horizontal.index(x), cls.vertical.index(y)
    
    @classmethod
    def matrix_to_chess(cls, coordinates: tuple[int, int]) -> str:
        """
        Функция для преобразования
        матричных координат в шахматные
        input(tuple(int, int)): (0, 7)
        output(str): "A1"
        """ 
        x, y = coordinates
        
        if not (0 <= x <= 7) or not (0 <= y <= 7):
            raise GameError("не верные индексы")
        return cls.horizontal[x] + cls.vertical[y]
    
    @classmethod
    def get_interval_coordinates(cls, source: str, destination: str, last=False) -> tuple[str]:
        """
        Функция возвращает кортеж из
        матричных координат между
        исходной клеткой и клеткой
        назначения не включительно,
        если last=False и включительно
        назначения, если last=True
        """      
        x1, y1 = cls.chess_to_matrix(source)
        x2, y2 = cls.chess_to_matrix(destination)
        
        """
        Используются как 3ий аргумент
        для срезов и инкрементируют/
        декрементируют 1ый аргумент
        для исключения source координат
        из срезов.
        """
        x_direction = {
            True: 1,
            False: -1
        }[x1<=x2]
        
        y_direction = {
            True: 1,
            False: -1
        }[y2>=y1]
        
        # срез строки из латинских букв + абсциса назначения или пустая строка + строка из 8 букв абсцисы или пустая строка
        horizontals = cls.horizontal[x1 + x_direction: x2: x_direction] + destination[:1 * last].upper() + source[:1].upper() * 8 * (x1 == x2)
        
        # срез строки из цифр + ордината назначения/пустая строка + строка из 8 цифр ординаты/пустая строка
        verticals = cls.vertical[y1 + y_direction: y2: y_direction] + destination[1:2 * last].upper() + source[1:2].upper() * 8 * (y1 == y2)

        return tuple(h+v for h,v in zip(horizontals, verticals))
    
    def __init__(self):
        
        # создание матрицы для внутренней реализации коллекции
        self.matrix = [[self.fill_char for j in range(8)] for i in range(8)]
        
        # хранилище сьеденных фигур
        self.defeated = list()
        

    def __str__(self):
        return "".join(
            " ".join(row) + "\n"
            for row in self.matrix )
        
    def __getitem__(self, position: str):
        x, y = self.chess_to_matrix(position)
        return self.matrix[y][x]
        
    def __setitem__(self, position: str, item):
        x, y = self.chess_to_matrix(position)
        self.matrix[y][x] = item
        
        if isinstance(item, Piece):
            item.coordinates = position
    
    def __delitem__(self, position: str):
        x, y = self.chess_to_matrix(position)
        self.matrix[y][x] = self.fill_char
    
    def get_interval_pieces(self, source, destination):
        return tuple(self[cors] for cors in self.get_interval_coordinates(source, destination) if isinstance(self[cors], Piece))
           
    def display(self):
        """
        Отображение шахматной доски
        в консоли.
        """
        u_indent = 0
        d_indent = 0
        
        # оцентровка отображения доски в консоли относительно длины ее строки
        l_indent = os.get_terminal_size().columns // 2 - 16 
        
        print("\n" * u_indent)
            
        for line_num, row in enumerate(self.matrix, start=1):
            
            print(f"{' ' * l_indent}{9 - line_num}   {'   '.join(map(str, row))}\n")
            
        # print(" " * (l_indent) + "   ".join(" ABCDEFGH"))
        print(" " * (l_indent + 4) + "A   B    C   D   E    F   G   H")
        
        print()
        
        print(
            " " * (l_indent) + " ".join(map(str, self.defeated[:16]))
            )
            
        print(
            " " * (l_indent) + " ".join(map(str, self.defeated[16:]))
        )
        
        print("\n" * d_indent)
        
                
class Piece: 
    allowed_moves = [] 
      
    def __init__(self, coordinates: str, color: str):
        self.coordinates = coordinates
        self.prevous_coordinates = None
        self.color = color
        
    def __repr__(self):
        return self.__str__()
         
    def can_move(self, coordinates):
        x1, y1 = ChessDesk.chess_to_matrix(self.coordinates)
        x2, y2 = ChessDesk.chess_to_matrix(coordinates)
        
        # из-за реверсии индексов ординат для обращения к матрице, для вычисления хода индексы ординат вычитаются наоборот.
      
        return (x2 - x1, y1 - y2) in self.allowed_moves
        
    def get_allowed_destinations(self) -> tuple[str]:
        destinations = []
        
        x1, y1 = game.desk.chess_to_matrix(self.coordinates)
        
        for x2, y2 in self.allowed_moves:
            
            condidate = x1 + x2, y1 - y2
            
            try:
                destination = game.desk.matrix_to_chess(condidate)
                
                destinations.append(
                    destination
                   )
                
            except GameError:
                continue
                            
        return destinations
    
    def get_allowed_dest_for_pawn_to_eat(self) -> tuple[str]:
        destinations = []
        
        x1, y1 = game.desk.chess_to_matrix(self.coordinates)
        
        for x2, y2 in self.allowed_moves_to_eat:
            
            condidate = x1 + x2, y1 - y2
            
            try:
                destination = game.desk.matrix_to_chess(condidate)
                
                destinations.append(
                    destination
                   )
                
            except GameError:
                continue
                            
        return destinations
      
    def can_eat(self, piece):
        """
        Метод проверяет может ли фигура
        сьесть переданную фигуру.
        """
        if isinstance(self, Pawn):
            
            if piece.coordinates.upper() in self.get_allowed_dest_for_pawn_to_eat():
                return True
            return False
        # если координаты проверяемой фигуры в разрешенных координатах назначения проверяющей фигуры
        if piece.coordinates.upper() in self.get_allowed_destinations():
   
            # список координат на пути к фигуре
            cors_list =  game.desk.get_interval_coordinates(self.coordinates, piece.coordinates)
            
            # если на пути к фигуре нет препятствующих ходу фигур
            if not [cors for cors in cors_list if isinstance(game.desk[cors], Piece)]:
                
                # можно есть
                return True      
        
        # есть нельзя
        return False
    
    def can_be_eaten_on(self, coordinates):     
        """
        Метод возвращает список фигур
        кем фигура
        может быть съедена на переданных
        коордитатах.
        """
        enemy_color = "w" if self.color == "b" else "b"
         
        piece_to_check = self.__class__(coordinates, self.color)
            
        obj = game.desk[coordinates]
            
        # список фигур, которые покушаются на текущую фигуру
        enemies = {piece for piece in game.pieces[enemy_color] if piece not in game.desk.defeated}           
            
        # если на клетке соперник
        if isinstance(obj, Piece) and obj.color != self.color:
                                
            # убираем его из сета, так как он будет сьеден
            enemies.discard(obj)
            
        who_can_eat_list = []
        
        old_obj = game.desk[coordinates]
            
        game.desk[coordinates] = piece_to_check
        
        for enemy in enemies:
            # если вражеская фигура может сьесть текущую, включаем ее в список  
            
            
            if enemy.can_eat(
                piece_to_check
                ):
                who_can_eat_list.append(
                    enemy
                   )
                   
        game.desk[coordinates] = old_obj
        
        return who_can_eat_list 
        
class Knight(Piece):
    def __init__(self, location, color):  
        super().__init__(location, color)
        self.name = 'Конь'
        self.priority = 3
        self.allowed_moves = [
            (1, 2),
            (1, -2),
            (2, 1),
            (2, -1),
            (-1, 2),
            (-1, -2),
            (-2, 1),
            (-2, -1)
           ]
        
    def __str__(self):
        return {
            "b": '\u265e',
            "w": '\u2658'
            }.get(self.color, 'k')
        
class King(Piece):
    def __init__(self, location, color):       
        super().__init__(location, color)
        self.name = 'Король'
        self.priority = 1
        self.castling = True
        self.allowed_moves = [
            (1, 1),
            (0, 1),
            (1, 0),
            (-1, 1),
            (-1, 0),
            (-1, -1),
            (0, -1),
            (1, -1)
           ]
        
    def __str__(self):
        return  {
            "b": '\u265a',
            "w": '\u2654'
                }.get(self.color, "K")
    
    def check(self):
        """
        Метод проверяет, не поставлен
        ли королю шах, и возвращает
        список координат, куда можно
        убрать короля.
        """
        if self.can_be_eaten_on(self.coordinates):
            
            destinations = self.get_allowed_destinations()
            
            back_off_destinations = []
            
            for coordinates in destinations:
                if not self.can_be_eaten_on(coordinates):
                    obj = game.desk[coordinates]
                    if isinstance(obj, Piece) and obj.color != self.color:
                        back_off_destinations.append(coordinates)
                    elif obj == game.desk.fill_char:
                        back_off_destinations.append(coordinates)
            
            return back_off_destinations
            
        return []
                
    def mate(self):
        """
        Метод проверяет, поставлен ли
        королю мат.
        """
        
        # предикат вернет True, если на клетке фигура соперника или клетка пуста
        def checker(cors):
            if game.desk[cors] == game.desk.fill_char:
                return True
                
            if game.desk[cors].color != self.color:
                return True
        
        # ходы, куда королю можно идти в окружении фигур
        kings_destinations = [
            cors
            for cors in self.get_allowed_destinations()
            if checker(cors)
            ]
            
        kings_destinations.append(self.coordinates)
        
        
            
        for coordinates in kings_destinations:
            
            
            
            # game.logger.info(f"{self} на {coordinates} съедят {[i.__str__()+i.coordinates for i in self.can_be_eaten_on(piece, coordinates)]} {kings_destinations}")
            
            # если есть координаты на которых никто не сьест
            if not self.can_be_eaten_on(coordinates):
                return False
                
        # если по всем координатом могут съесть
        return True
                
class Rook(Piece):
    """
    Описывает туру.
    """
    def __init__(self, location, color):       
        super().__init__(location, color)
        self.name = 'Ладья'
        self.priority = 3
        self.castling = True
        self.allowed_moves = tuple(chain(
        ((0, i) for i in range(1, 8)),
        ((i, 0) for i in range(1, 8)),
        ((0, i) for i in range(-1, -8, -1)),
        ((i, 0) for i in range(-1, -8, -1))))
        
    def __str__(self):
        return {
            "b": '\u265c',
            "w": '\u2656'
            }.get(self.color, 'R')
               
class Queen(Piece):
    def __init__(self, location, color):       
        super().__init__(location, color)
        self.name = 'Ферзь'
        self.priority = 2
        self.allowed_moves = tuple(chain(
        ((0, i) for i in range(1, 8)),
        ((i, 0) for i in range(1, 8)),
        ((0, i) for i in range(-1, -8, -1)),
        ((i, 0) for i in range(-1, -8, -1)),
        ((i, j) for i, j in zip(range(1,8), range(1, 8))),
        ((i, j) for i, j in zip(range(-1,-8, -1), range(-1, -8, -1))),
        ((i, j) for i, j in zip(range(-1,-8, -1), range(1, 8))),
        ((i, j) for i, j in zip(range(1,8), range(-1, -8, -1)))))
                
    def __str__(self):
        return {
            "b": '\u265b',
            "w": '\u2655'
            }.get(self.color, 'Q')
        
class Bishop(Piece):
    def __init__(self, location, color):       
        super().__init__(location, color)
        self.name = 'Слон'
        self.priority = 3
        self.allowed_moves = tuple(chain(
        ((i, j) for i, j in zip(range(1,8), range(1, 8))),
        ((i, j) for i, j in zip(range(-1,-8, -1), range(-1, -8, -1))),
        ((i, j) for i, j in zip(range(-1,-8, -1), range(1, 8))),
        ((i, j) for i, j in zip(range(1,8), range(-1, -8, -1)))))
        
    def __str__(self):
        return {
            "b": '\u265d',
            "w": '\u2657'
            }.get(self.color, 'B')
        
class Pawn(Piece):
    """
    Класс описывает пешку.
    """
    def __init__(self, location, color):       
        super().__init__(location, color)
        self.name = 'Пешка'
        self.priority = 4
        
        # устанавливаем разрешенные ходы для пешки по ее цвету(расположению соответственно) + первый ход на 2 клетки
        self.allowed_moves = {
            "w": {(0, 1),(0, 2)},
            "b": {(0, -1),(0, -2)}
        }.get(self.color, ())
        
        # разрешенные ходы для сьедания фигуры соперника
        self.allowed_moves_to_eat = {
            "w": {(1, 1),(-1, 1)},
            "b": {(1, -1),(-1, -1)}
        }.get(self.color, ())
         
    def __str__(self):
        return {
            "b": '\u265f',
            "w": '\u2659'
        }.get(self.color, 'P')
        
    def can_move(self, coordinates):
        """
        Метод переопределен для
        добавления логики поведения
        пешки.
        """
        # получаем результат стандартной реализации метода
        super_return = super().can_move(coordinates)
        
        # после первого хода пешка не ходит на 2 клетки вперед. убираем соответствующие move
        if (0, 2) in self.allowed_moves:
            self.allowed_moves.discard((0, 2))
            
        if (0, -2) in self.allowed_moves:
            self.allowed_moves.discard((0, -2))
            
        # source матричные координаты
        x1, y1 = game.desk.chess_to_matrix(self.coordinates)
        
        # destination матричные координаты
        x2, y2 = game.desk.chess_to_matrix(coordinates)
        
        # создаем кортеж текущего move для проверки разрещенных ходов
        move = x2 - x1, y1 - y2
        
        # пешка не может сделать ход, если перед ней фигура
        if isinstance(
            game.desk[coordinates],
            Piece
            ) and super_return:
            return False
        
        # пешка может сьесть фигуру соперника по диагонали. moves зависят от цвета фигуры   
        if isinstance(
            game.desk[coordinates],
            Piece
            ) and move in self.allowed_moves_to_eat:
            return True
        
        # возвращаем стандартное поведение метода
        return super_return
        
         
class Game:
    """
    Класс описывает процесс игры.
    Запускает игровой цикл.
    Следит за соблюдением правил игры.
    """
       
    pieces_to_place = {
        Knight('B1', 'w'),
        Knight('G1', 'w'),
        Knight('B8', 'b'),
        Knight('G8', 'b'),
        Rook('A1', 'w'),
        Rook('H1', 'w'),
        Rook('A8', 'b'),
        Rook('H8', 'b'),
        Queen('D1', 'w'),
        Queen('D8', 'b'),
        Bishop('C1', 'w'),
        Bishop('F1', 'w'),
        Bishop('C8', 'b'),
        Bishop('F8', 'b'),
        Pawn('A2', 'w'),
        Pawn('B2', 'w'),
        Pawn('C2', 'w'),
        Pawn('D2', 'w'),
        Pawn('E2', 'w'),
        Pawn('F2', 'w'),
        Pawn('G2', 'w'),
        Pawn('H2', 'w'),
        Pawn('A7', 'b'),
        Pawn('B7', 'b'),
        Pawn('C7', 'b'),
        Pawn('D7', 'b'),
        Pawn('E7', 'b'),
        Pawn('F7', 'b'),
        Pawn('G7', 'b'),
        Pawn('H7', 'b'),       
    }
        
    def __init__(self):
        self.desk = ChessDesk()
        self.logger = Logger()
        self.ai = Ai()
        self.white_player = 'player'
        self.black_player = 'player'
        self.debug = False
        self.whose_move = "w"
        self.instructions = [None]   
        self.kings = {
            "w": King("e1", "w"),
            "b": King("e8", "b")
        }      
        self.pieces = {
            "b": [piece for piece in self.pieces_to_place if piece.color == 'b'],        
            "w": [piece for piece in self.pieces_to_place if piece.color == 'w']
            }
        self.pieces["b"].append(self.kings["b"])
        self.pieces["w"].append(self.kings["w"])
           
    def check_player_input(self, player_input):
        """
        Функция проверяет соответствие
        ввода игрока ожидаемой команде.
        Ожидается строка из координат:
        например 'A1B7', где 'A1' -
        клетка фигуры, совершающей ход,
        'B7' - желаемая клетка назначения
        для хода этой фигуры.
        """
        
        # проверка длины строки ввода
        if len(player_input) != 4:
            raise GameError(f"не верные координаты '{player_input}'")
        
        # выравниваем регистр    
        x1, y1, x2, y2 = player_input.upper()
        
        # проверка соответствия координат правилам игры 
        if not all( [
            x1 in self.desk.horizontal,
            y1 in self.desk.vertical,
            x2 in self.desk.horizontal,
            y2 in self.desk.vertical
           ] ):
           raise GameError(f"не верные координаты '{player_input}'")
        
       