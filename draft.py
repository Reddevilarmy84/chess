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
        
        # нельзя сделать ход на ту же клетку
        if player_input[:2].upper() == player_input[2:].upper():
            raise GameError(f"координаты совпадают '{player_input}'")                                            
    def run(self):
        """
        Запуск цикла игры.
        """
        
        # расставляем фигуры на доске      
        for piece in chain(
            self.pieces["w"],
            self.pieces["b"],
            ):
            self.desk[piece.coordinates] = piece
            
        while True:
            
            # имитация обновлентя экрана
            # os.system("clear")
            print("\n" * 10)
            
            print(f" Chess by Alexander Postavets(v0.1)©    {self.white_player} vs {self.black_player}")
            # отображенте доски
            self.desk.display()
            
            # отображение лога
            self.logger.display()
            
            if hasattr(self, "game_over"):
                break
            
            if self.debug:
                
                try:
                    inp = self.instructions.pop(0)
                    
                except:
                    self.debug = False
                    continue
                
            elif self.black_player == "ai" and self.whose_move == 'b':
                    inp = self.ai.suggest_a_move()
                    
            elif self.white_player == "ai" and self.whose_move == 'w':
                    inp = self.ai.suggest_a_move()
                    
            else:                   
                inp = input(f" ходят {self.whose_move}: ")
                    
            try:
                x = self.make_a_move(inp)
                if x: self.game_over = True
                
                
            except Exception as e:
                self.logger.err(
            f'{type(e).__name__}: {e}'
                   )
            finally:
                del inp
                
            print("\n" * 10)
            
    def make_a_move(self, player_input):
        """
        Функция выполняет шахматный ход,
        анализируя данные введенные
        игроком.
        """
        # если фигура сьедена, заполняем этот текст для отображения в логе
        check = ''
        mate = ''
        eat_txt = ''
        enemy_color = 'w' if self.whose_move == 'b' else 'b'
        enemy_king = self.kings[enemy_color]
              
        # функция проверяет ввод, ожидая корректные шахматные координаты
        self.check_player_input(
            player_input
           )
        
        # координаты исходной клетки
        source = player_input[:2].upper()
        
        # координаты клетки назначения
        destination = player_input[2:].upper()
        
        # обьект на исходной клетке
        source_obj = self.desk[source]
        
        # обьект на клетке назначения
        destination_obj = self.desk[destination]
        
        # нельзя сделать ход с пустой клетки
        if source_obj == self.desk.fill_char:
            raise GameError(f"исходная клетка пуста {source} --> {destination}")
        
        # нельзя ходить черными если мейсас ход белых и наоборот
        if source_obj.color != self.whose_move:
            raise GameError(f"ходят {self.whose_move} {source}({source_obj}) -> {destination}({destination_obj})")
            
        # нельзя ходить не по своей траектории
        if not source_obj.can_move(destination):
            raise GameError(f"{source_obj.name} так не ходит. {source}({source_obj}) --> {destination}({destination_obj})")
            
        # проверка: фигуры на пути(препятствия)        
        interval_pieces = self.desk.get_interval_pieces(source, destination)
        
        # нельзя ходить сквозь другие фигуры
        if interval_pieces:
            raise GameError(f"на траектории {source}({source_obj}) -> {destination}({destination_obj}) есть фигуры {"".join(map(str, interval_pieces))}")
            
        # проверка: есть ли на клетке назначения фигура
        if isinstance(destination_obj, Piece):
            # нельзя есть фигуру того же цвета
            if source_obj.color == destination_obj.color:
                raise GameError(f"клетка назначения занята {source}({source_obj}) --> {destination}({destination_obj})")
                
            # добавили в хранилище съеденную фигуру
            self.desk.defeated.append(
                destination_obj)
            
            # добавили в лог кого сьели
            eat_txt = f"Сьел {destination_obj}"
        # проверка Мат себе
        
        # перемещение фигуры с исходной клетки на клетку назначения
        del self.desk[source]        
        self.desk[destination] = source_obj
        
        # проверка на шах сопернику
        if source_obj.can_eat(
            self.kings[enemy_color]
            ):
            check = "ШАХ!"
            
            # король соперника проверяет себя на мат
        if  self.kings[enemy_color].mate():     
            mate = "МАТ!"  
                    
        # записываем в лог событие    
        self.logger.info(f"{source}({source_obj}) --> {destination}({destination_obj}) {eat_txt} {check} {mate}")
        
        
        
        if mate or (enemy_king in self.desk.defeated):
            game.logger.info(f"Игра окончена. Победили {'Белые' if self.whose_move == 'w' else 'Черные'}")
            return True
            
        if game.logger.records > 1000:
            game.logger.info("ничья, так и будем бегать")
            return True
            
        # передаем ход сопернику
        self.whose_move = "b" if self.whose_move == "w" else "w" 

           
class Ai:
    """
    Имитирует поведение игрока.
    """
    def who_can_be_eaten(self) -> defaultdict:
        """
        Метод проверяет, какие фигуры
        можно сьесть.
        """
        self_color = game.whose_move
        enemy_color = "b" if game.whose_move == "w" else "w"
        
        who_can_be_eaten = defaultdict(list)
        
        for self_piece in game.pieces[self_color]:
            
            if self_piece in game.desk.defeated:
                continue
            
            enemy_pieces = copy(game.pieces[enemy_color])
            
            # сортировка вражеских фигур по атрибуту приоритета
            enemy_pieces.sort(key=lambda x:x.priority)
            
            for enemy in enemy_pieces:
                
                if enemy in game.desk.defeated:
                    continue
                
                if self_piece.can_eat(enemy):
                    who_can_be_eaten[self_piece].append(enemy)
                    
        # сортировка словаря по атрибуту приоритета первой фигуры в значениях
        who_can_be_eaten = {
            k:v
            for k,v in sorted(who_can_be_eaten.items(), key=lambda x:x[1][0].priority)
        }
                            
        return who_can_be_eaten
        
    def where_can_go(self):
        
        self_color = game.whose_move
        
        where_can_go = defaultdict(list)
        
        # собираем живые дружественные фигуры в список
        pieces = [piece for piece in game.pieces[self_color] if piece not in game.desk.defeated]
        
        for piece in pieces:
                
            destinations = piece.get_allowed_destinations()
            
                                                 
            free_squares = []
            
            for coordinates in destinations:
                interval = game.desk.get_interval_coordinates(
                    piece.coordinates,
                    coordinates
                   )
                
                pieces_on_interval = [
                    coordinates
                    for coordinates in interval
                    if isinstance(
                        game.desk[coordinates],
                        Piece
                       )
                       ]
                
                if game.desk[coordinates] == game.desk.fill_char and not pieces_on_interval and not piece.can_be_eaten_on(coordinates):
                                   
                    free_squares.append(
                        coordinates
                       )
                
            if free_squares:
                where_can_go[piece].extend(
                    free_squares
                   )
        
        return where_can_go
               
    def suggest_a_move(self):
        """
        Метод возвращает координаты
        предложенные AI.
        """        
        self_color = game.whose_move
        
        # анализ: не под швхом ли король        
        check = game.kings[self_color].check()
        
        if check:
            print("AI: королю поставлен шах:")
            self_king = game.kings[self_color]
                                    
            enemies_in_check = [game.desk[i] for i in check if isinstance(game.desk[i], Piece) and game.desk[i].color != self_color]
            
            empty_squares = [i for i in check if game.desk[i] == game.desk.fill_char and not self_king.can_be_eaten_on(i)]
            
            for i in empty_squares:
                print(i, self_king.can_be_eaten_on(i))
                
            if empty_squares:
                print(f"Могу убрать короля на: {" ".join(empty_squares)}")
            
            if enemies_in_check:
                print(f"Могу съесть налетчика: {" ".join(map(str, enemies_in_check))}")
            
            self_king = game.kings[self_color]
            
            destination = random.choice(list(i.coordinates for i in enemies_in_check) if enemies_in_check else check)
        
            print(f"хожу так: {self_king.coordinates}({self_king}) -> {destination}({game.desk[destination]})")
            
            # input("делаю ход? ")
        
            return self_king.coordinates + destination
        
        # анализ, кого кем можно сьесть
        who_can_be_eaten = self.who_can_be_eaten()
        
        wcbe_keys = list(who_can_be_eaten.keys())
        
        if wcbe_keys:
            # future feature: проверить не подвергаешь ли опасности короля, шаху или мату.
            
            whom = wcbe_keys[0]
            
            who = who_can_be_eaten[whom][0]
  
  
            print(f"AI: ходят {'белые' if self_color == 'w' else 'черные'}")
            
            print("кем кого можно сьесть:")
                     
            for self_piece, enemies in who_can_be_eaten.items():
                
                print(f"     {self_piece}{self_piece.coordinates} ->", end=' ')
                
                for enemy in enemies:
                    
                    print(f"{enemy}{enemy.coordinates}", end=", ")
                    
                print("")
                
            print(f"буду ходить так: {whom}{whom.coordinates} -> {who}{who.coordinates}")
                        
            # input("делаю ход?")
            
            return whom.coordinates + who.coordinates
                
        # анализ, кем куда пойти, чтобы следующим ходом можно было сьесть
        
        # здесь могла быть рекурсия анализов, но пока нет
        
        # рандомный ход
        where_can_go = self.where_can_go()
        
        
                    
        print("AI: могу пойти сюда:\n")
        for k, v in where_can_go.items():
            print(f"{k}{k.coordinates} -> {" ".join(v)}")
                      
        selected_piece = random.choice(list(where_can_go))
        
        # список безопасных клеток где нас не сьедят
       
        safe_destinations = [i for i in where_can_go[selected_piece] if not selected_piece.can_be_eaten_on(i)]
        
        print(f"здесь не съедят{" ".join(safe_destinations)}")
                   
        destination = random.choice(safe_destinations if safe_destinations else where_can_go[selected_piece])
        
        print(f"\nмой выбор: {selected_piece}{selected_piece.coordinates} на {destination}")
        
        # input("делаю ход?")
               
        return selected_piece.coordinates + destination       
        
        # если ни к чему не удалось прийти
        coordinates = input(f" ходят {game.whose_move}. AI: я пока плохо играю. Поможешь с ходом? ")
        
        return coordinates

                    
if __name__ == "__main__":
    
    instructions = {
        
        # мат в 4 хода
        1: [
        "e2e4",
        "e7e5",
        "f1c4",
        "f8c5",
        "d1h5",
        "a7a5",
        "h5f7"
        ],
        
        # мат 4 хода(3 хода, без мата)
        2: [
        "e2e4",
        "e7e5",
        "f1c4",
        "f8c5",
        "d1h5",
        "a7a5",
        ],
        3: [
        ]
    }
    
    game = Game()
    
    game.white_player = 'ai'
    game.black_player = 'ai'
    
    game.debug = True
    
    # если есть список инструкций, ходы в нем выполняются автоматически при game.debug=True
    game.instructions = instructions[3]
    
    # запуск цикла игры   
    game.run()
    