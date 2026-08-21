from collections import deque, Counter
from random import randint, choice ,shuffle
from constants import Textures, Constants, GameStates,AiModes,Directions

from testing import *

HEIGHT = 500
WIDTH = 900
TITLE = "Sea Buttle"
# одно поле равен ~38


class Cell:
    def __init__(self, is_player=False):
        self.is_player = is_player
        self.is_sea = True
        self.is_ship = False
        self.is_shooten = False
        self.is_destoed = False

    def shoot(self):
        self.is_shooten = True

    def un_or_place_ship(self):
        self.is_ship = not self.is_ship
        self.is_sea = not self.is_sea

    def place_ship(self):
        self.is_ship = True
        self.is_sea = False

    def un_place_ship(self):
        self.is_ship = False
        self.is_sea = True

    def texture_give(self, see_ship=False):
        if self.is_destoed:
            return Textures.DESTROED.value
        elif self.is_shooten and self.is_ship:
            return Textures.BURNING.value
        elif self.is_shooten and not self.is_ship:
            return Textures.SHOOTEN_SEA.value
        elif self.is_ship and (see_ship or self.is_player):
            return Textures.SHIP.value
        else:
            return Textures.SEA.value


class StatesOfGame:
    def __init__(self):
        self.state = GameStates.GAME


class Field_Seeble:
    def __init__(self):
        pass

    def generate_field_enemy(self):
        field = []
        for _ in range(Constants.SIZE_BOARD):
            in_field = []
            for _ in range(Constants.SIZE_BOARD):
                in_field.append(Cell(True))
            field.append(in_field)

        self.enemy_field_see = field

    def draw_enemy(self, screen, see_ships=False):
        x = Constants.SPASE_OF_SCREEN
        for i in range(Constants.SIZE_BOARD):
            y = Constants.SPASE_OF_SCREEN
            for j in range(Constants.SIZE_BOARD):
                screen.blit(self.enemy_field_see[i][j].texture_give(see_ships), (x, y))
                y += Constants.SIZE_PICTURE
            x += Constants.SIZE_PICTURE
        return x + Constants.SPASE_OF_SCREEN * 2

    def generate_field_my(self):

        def fill_test(field):
            test_data = [
                (1, 1),
                (1, 2),
                (1, 3),
                (1, 4),
                (4, 2),
                (4, 3),
                (4, 4),
                (7, 1),
                (7, 2),
                (7, 3),
                (1, 9),
                (2, 9),
                (1, 7),
                (2, 7),
                (9, 9),
                (9, 0),
                (5, 9),
                (7, 9),
                (6, 6),
                (5, 8),
            ]

            for x, y in test_data:
                field[x][y].place_ship()

        field = []
        for _ in range(Constants.SIZE_BOARD):
            in_field = []
            for _ in range(Constants.SIZE_BOARD):
                in_field.append(Cell(True))
            field.append(in_field)
        fill_test(field)
        self.my_field_see = field

    def draw_my(self, screen, x):
        for i in range(Constants.SIZE_BOARD):
            y = Constants.SPASE_OF_SCREEN
            for j in range(Constants.SIZE_BOARD):
                screen.blit(self.my_field_see[i][j].texture_give(), (x, y))
                y += Constants.SIZE_PICTURE
            x += Constants.SIZE_PICTURE


class Ais_Turns:
    def __init__(self,board):
        self.board=board
        self.rotations = [(0, 1), (1, 0), (-1, 0), (0, -1)]
        self.target_cells=set()
        self.hit_cells=set()
        self.current_direction=None
        self.mode=AiModes.SEARCH
        self.visited_dontmovehere=set()
        
    def move(self):
        print(self.visited_dontmovehere)
        next_move = True
        #logic block
        if self.mode==AiModes.SEARCH:
            x = randint(0, 9)
            y = randint(0, 9)
            while self.board[x][y].is_shooten or (x,y) in self.visited_dontmovehere:
                x = randint(0, 9)
                y = randint(0, 9)
                
            self.board[x][y].shoot()
            if self.board[x][y].is_sea:
                next_move = True
            elif self.board[x][y].is_ship:
                if self.reset(x,y):
                    return False
                self.mode = AiModes.HUNTING
                for mx,my in self.rotations:
                    next_x=x+mx
                    next_y=y+my
                    self.target_cells.add((next_x,next_y))  
                return False
        elif self.mode==AiModes.HUNTING:
            if not self.target_cells:
                self.mode=AiModes.SEARCH
                return True
            while self.target_cells:
                x,y=choice(list(self.target_cells))
                self.target_cells.discard((x,y))
                if (x,y) in self.visited_dontmovehere:
                    continue
                if not (0 <= x < Constants.SIZE_BOARD and 0 <= y < Constants.SIZE_BOARD):
                    continue
                if self.board[x][y].is_shooten:
                    continue
                self.board[x][y].shoot()
                if not self.board[x][y].is_ship:
                    next_move = True
                    return next_move
                elif self.board[x][y].is_ship:
                    if self.reset(x,y):
                        return False
                    all_x = {x for x, y in self.hit_cells}
                    all_y = {y for x, y in self.hit_cells}
                    #aaa
                    if len(all_x)<2:
                        self.target_cells=set()
                        for tar_x,tar_y in self.hit_cells:
                            for rot_x,rot_y in ((0, -1) ,(0, 1)):
                                tx=tar_x+rot_x
                                ty=tar_y+rot_y
                                if not (0 <= tx < Constants.SIZE_BOARD and 0 <= ty < Constants.SIZE_BOARD):
                                    continue
                                if self.board[tx][ty].is_shooten:
                                    continue
                                self.target_cells.add((tx,ty))
                        self.current_direction=Directions.LEFT_RIGHT
                    elif len(all_y)<2:
                        self.target_cells=set()
                        for tar_x,tar_y in self.hit_cells:
                            for rot_x,rot_y in ((-1, 0), (1, 0)):
                                tx=tar_x+rot_x
                                ty=tar_y+rot_y
                                if not (0 <= tx < Constants.SIZE_BOARD and 0 <= ty < Constants.SIZE_BOARD):
                                    continue
                                if self.board[tx][ty].is_shooten:
                                    continue
                                self.target_cells.add((tx,ty))
                        self.current_direction=Directions.UP_DOUN
                    #aaa
                    next_move = False
                    return next_move
        return next_move
                    

    def reset(self, x, y):
        self.hit_cells.add((x, y))
        ship_cells = count_of_non_shooten(x, y, self.board)
        if self.hit_cells == ship_cells:
            self.visited_dontmovehere.update(do_step_on(ship_cells))
            self.hit_cells.clear()
            self.target_cells.clear()
            self.mode = AiModes.SEARCH
            self.current_direction = None
            return True
        return False

            
        #logic block
        
        
        
        



def get_ship_length(field, start_x, start_y):
    queue = deque([(start_x, start_y)])
    visited = {(start_x, start_y)}
    while queue:
        x, y = queue.popleft()
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if abs(dx) + abs(dy) != 1:
                    continue
                next_x = x + dx
                next_y = y + dy
                if not (0 <= next_x < len(field) and 0 <= next_y < len(field[next_x])):
                    continue
                if (next_x, next_y) in visited:
                    continue
                if field[next_x][next_y].is_ship:
                    queue.append((next_x, next_y))
                    visited.add((next_x, next_y))

    ship_nearby = False
    for x, y in visited:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if abs(dx) + abs(dy) != 2:
                    continue
                next_x = x + dx
                next_y = y + dy
                if not (0 <= next_x < len(field) and 0 <= next_y < len(field[next_x])):
                    continue
                if (next_x, next_y) not in visited and field[next_x][next_y].is_ship:
                    ship_nearby = True
    all_x = {x for x, y in visited}
    all_y = {y for x, y in visited}
    is_straight = len(all_x) == 1 or len(all_y) == 1
    return len(visited), is_straight, ship_nearby


def valid_count_of_ship(field):
    global count_ship_error
    counter = Counter({1: 0, 2: 0, 3: 0, 4: 0})
    all_visited = set()
    visited = set()
    count_ship_error = False
    eczample = Counter({1: 4, 2: 3, 3: 2, 4: 1})
    for i in range(Constants.SIZE_BOARD):
        for j in range(Constants.SIZE_BOARD):
            if not field[i][j].is_ship:
                continue
            if (i, j) in visited or (i, j) in all_visited:
                continue
            queue = deque([(i, j)])
            visited = {(i, j)}
            while queue:
                x, y = queue.popleft()
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        if abs(dx) + abs(dy) != 1:
                            continue
                        next_x = x + dx
                        next_y = y + dy
                        if not (
                            0 <= next_x < len(field)
                            and 0 <= next_y < len(field[next_x])
                        ):
                            continue
                        if (next_x, next_y) in visited:
                            continue
                        if field[next_x][next_y].is_ship:
                            queue.append((next_x, next_y))
                            visited.add((next_x, next_y))
                            all_visited.add((next_x, next_y))
            counter[len(visited)] += 1
            if (
                counter[1] > eczample[1]
                or counter[2] > eczample[2]
                or counter[3] > eczample[3]
                or counter[4] > eczample[4]
            ):
                count_ship_error = True
                return counter
    return counter


def is_ship_died(x, y, field, is_for_player=False):
    deq = deque([(x, y)])
    viuved = set([(x, y)])
    count_of_sooten = 0
    if not field[x][y].is_ship:
        return False
    while deq:
        x, y = deq.popleft()
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if abs(dx) + abs(dy) != 1:
                    continue
                next_x = x + dx
                next_y = y + dy
                if not is_for_player and not (
                    0 <= next_x < Constants.SIZE_BOARD
                    and 0 <= next_y < Constants.SIZE_BOARD
                ):
                    continue
                if is_for_player and not (
                    (0 <= next_x < Constants.SIZE_BOARD)
                    and (0 <= next_y < Constants.SIZE_BOARD)
                ):
                    continue
                if (next_x, next_y) in viuved:
                    continue
                if field[next_x][next_y].is_shooten and field[next_x][next_y].is_ship:
                    count_of_sooten += 1
                if field[next_x][next_y].is_ship:
                    deq.append((next_x, next_y))
                    viuved.add((next_x, next_y))

    if len(viuved) == count_of_sooten + 1:
        for x, y in viuved:
            field[x][y].is_destoed = True
        return viuved
    return False


def valid_ship(field):
    global ship_error
    ship_error = False
    for row in range(Constants.SIZE_BOARD):
        for col in range(Constants.SIZE_BOARD):
            if not field[row][col].is_ship:
                continue
            len_ship, is_straight, ship_nearby = get_ship_length(field, row, col)
            if len_ship > 4 or ship_nearby or not is_straight:
                ship_error = True


def count_of_non_shooten(x,y,field):
    deq = deque([(x, y)])
    viuved = set([(x, y)])
    count_of_sooten = 0
    if not field[x][y].is_ship:
        return False
    while deq:
        x, y = deq.popleft()
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if abs(dx) + abs(dy) != 1:
                    continue
                next_x = x + dx
                next_y = y + dy
                if not (
                    0 <= next_x < Constants.SIZE_BOARD
                    and 0 <= next_y < Constants.SIZE_BOARD
                ):
                    continue
                if (next_x, next_y) in viuved:
                    continue
                if field[next_x][next_y].is_shooten and field[next_x][next_y].is_ship:
                    count_of_sooten += 1
                if field[next_x][next_y].is_ship:
                    deq.append((next_x, next_y))
                    viuved.add((next_x, next_y))
    return viuved


def pixel_to_cordinates(x, y, my=False):
    if my:
        x -= (
            Constants.SPASE_OF_SCREEN * 3
            + Constants.SIZE_PICTURE * Constants.SIZE_BOARD
        )
    else:
        x -= Constants.SPASE_OF_SCREEN
    y -= Constants.SPASE_OF_SCREEN
    x //= Constants.SIZE_PICTURE
    y //= Constants.SIZE_PICTURE
    if my:
        return x, y
    return x, y


def backfill(screen):
    if game_state.state == GameStates.MENU:
        screen.blit(Textures.MENU_BACKFONE.value, (0, 0))
        screen.blit(Textures.LETS_GAME.value, (300, 150))
    elif (
        game_state.state == GameStates.SHIPS_place
        or game_state.state == GameStates.GAME
    ):
        screen.blit("sea", (-200, -200))
        x = field.draw_enemy(screen)
        field.draw_my(screen, x)
        screen.draw.text("my field", (630, 440), fontsize=50)
        screen.draw.text("enemy field", (130, 440), fontsize=50)
        if ready_to_game and not ship_error:
            screen.blit(Textures.LETS_GAME.value, (100, 150))
        if game_state.state == GameStates.GAME:
            screen.blit("insta_loose", (5, 475))
    elif (
        game_state.state == GameStates.VICTORY or game_state.state == GameStates.DEFEAT
    ):
        screen.blit("sea", (-200, -200))
        x = field.draw_enemy(screen, True)
        field.draw_my(screen, x)
        # screen.fill((51, 204, 242))
        if game_state.state == GameStates.VICTORY:
            screen.draw.text("!VICTORY!", (350, 200), fontsize=75, color="white")
        elif game_state.state == GameStates.DEFEAT:
            screen.draw.text("DEFEAT", (350, 200), fontsize=75, color="red")


def error(screen):
    if game_state.state == GameStates.SHIPS_place:
        if ship_error:
            screen.draw.text("ship error", (550, 200), fontsize=74, color="white")
        elif count_ship_error:
            screen.draw.text("count ship error", (450, 150), fontsize=74, color="white")


def check_ready_to_game(ships):
    count_of_ship_blocks = 0
    for key, val in ships.items():
        if abs(key + (-5)) >= val:
            count_of_ship_blocks += key * val
    return count_of_ship_blocks


def place_ships_enemy(field):
    rotations = [(0, 1), (1, 0)]
    ships = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
    for lenght in ships:
        placed = False
        for _ in range(100):
            rx = randint(0, 9)
            ry = randint(0, 9)
            dx, dy = choice(rotations)
            ship_cells = []
            for step in range(lenght):
                x = rx + dx * step
                y = ry + dy * step
                ship_cells.append((x, y))
            if not all(
                map(
                    lambda i: (
                        True
                        if 0 <= i[0] < Constants.SIZE_BOARD
                        and 0 <= i[1] < Constants.SIZE_BOARD
                        else False
                    ),
                    ship_cells,
                )
            ):
                continue
            can_place = True
            for x, y in ship_cells:
                for kor_x in (1, 0, -1):
                    for kor_y in (1, 0, -1):
                        next_x = x + kor_x
                        next_y = y + kor_y
                        if not (
                            0 <= next_x < Constants.SIZE_BOARD
                            and 0 <= next_y < Constants.SIZE_BOARD
                        ):
                            continue
                        if field.enemy_field_see[next_x][next_y].is_ship:
                            can_place = False
            if not can_place:
                continue
            for x, y in ship_cells:
                field.enemy_field_see[x][y].place_ship()
            placed = True
            break
    if placed:
        return True
    return False


def players_ones_turn(turn, board, x_clict, y_clict):
    if turn:
        if not board[x_clict][y_clict].is_shooten:
            board[x_clict][y_clict].shoot()
            is_ship_died(x_clict, y_clict, field.enemy_field_see, True)
            # ultimate_ship_chec_func(x_clict, y_clict, field.enemy_field_see, SelectMode.IS_SHIP_DIED, is_players_board=True)
            if board[x_clict][y_clict].is_ship:
                return turn
            return not turn
        return turn


def ais_turn(board, gratest_next_move=False):
    rx = randint(0, 9)
    ry = randint(0, 9)
    rotations = [(0, 1), (1, 0), (-1, 0), (0, -1)]
    gratest_move = False
    while board[rx][ry].is_shooten:
        rx = randint(0, 9)
        ry = randint(0, 9)
    next_move = True
    if gratest_next_move:
        rx, ry = gratest_next_move
        board[rx][ry].shoot()
        if board[rx][ry].is_ship:
            next_move = False
        for rot_x, rot_y in rotations:
            next_x = rx + rot_x
            next_y = ry + rot_y
            if not (
                0 <= next_x < Constants.SIZE_BOARD
                and 0 <= next_y < Constants.SIZE_BOARD
            ):
                continue
            if board[next_x][next_y].is_ship and not board[next_x][next_y].is_shooten:
                gratest_move = (next_x, next_y)
            # else:
            #     gratest_move=False
    else:
        while (rx, ry) in near_ship_ai or board[rx][ry].is_shooten:
            rx = randint(0, 9)
            ry = randint(0, 9)

        board[rx][ry].shoot()
        if board[rx][ry].is_ship:
            next_move = False
            gratest_move = (rx, ry)
        else:
            gratest_move = False

    check = is_ship_died(rx, ry, field.my_field_see)
    if check:
        near_ship_ai.update(do_step_on(check))
    return gratest_move, next_move


def check_los_or_vin(field):
    for row in field:
        for cord in row:
            if cord.is_ship and not cord.is_shooten:
                return False
    return True


def do_step_on(ship):
    not_choose_this = set()
    for x, y in ship:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                next_x = x + dx
                next_y = y + dy
                if not (
                    0 <= next_x < len(field.my_field_see)
                    and 0 <= next_y < len(field.my_field_see[next_x])
                ):
                    continue
                if (next_x, next_y) in ship:
                    continue
                not_choose_this.add((next_x, next_y))
    return not_choose_this


field = Field_Seeble()
game_state = StatesOfGame()
ship_error = False
count_ship_error = False
field.generate_field_enemy()
field.generate_field_my()
wrong = place_ships_enemy(field)
while not wrong:
    field.generate_field_enemy()
    wrong = place_ships_enemy(field)
ready_to_game = False
is_player_turn = True
gratest_move = False
ai = Ais_Turns(field.my_field_see)


def draw():
    screen.clear()
    backfill(screen)
    error(screen)


def update():
    global is_player_turn
    if game_state.state == GameStates.GAME:
        if not is_player_turn:
            next_move = ai.move()
            if check_los_or_vin(field.my_field_see):
                game_state.state = GameStates.DEFEAT
            is_player_turn = next_move


def on_mouse_up(pos, button):
    global ready_to_game, is_player_turn, near_ship_ai, is_player_turn,ai
    x, y = pos
    if game_state.state == GameStates.MENU:
        near_ship_ai = set()
        is_player_turn = True
        if 300 <= x < 600 and 150 <= y < 302:
            field.generate_field_enemy()
            field.generate_field_my()
            wrong = place_ships_enemy(field)
            ai = Ais_Turns(field.my_field_see)
            while not wrong:
                field.generate_field_enemy()
                wrong = place_ships_enemy(field)
            game_state.state = GameStates.SHIPS_place

    elif game_state.state == GameStates.SHIPS_place:
        if 475 < x < 875 and 25 < y < 425:
            clk_x, clk_y = pixel_to_cordinates(x, y, True)
            field.my_field_see[clk_x][clk_y].un_or_place_ship()
            valid_ship(field.my_field_see)
            ships = valid_count_of_ship(field.my_field_see)
            if check_ready_to_game(ships) == 20:
                ready_to_game = True
            else:
                ready_to_game = False

        if not ship_error and ready_to_game and 100 <= x < 400 and 150 <= y < 302:
            ready_to_game = False
            game_state.state = GameStates.GAME

    elif game_state.state == GameStates.GAME:

        if 25 < x < 425 and 25 < y < 425:
            clk_x, clk_y = pixel_to_cordinates(x, y)
            is_player_turn = players_ones_turn(
                is_player_turn, field.enemy_field_see, clk_x, clk_y
            )
            if check_los_or_vin(field.enemy_field_see):
                game_state.state = GameStates.VICTORY

        if 5 <= x < 63 and 475 <= y < 500:
            game_state.state = GameStates.MENU

    elif (
        game_state.state == GameStates.VICTORY or game_state.state == GameStates.DEFEAT
    ):
        if button:
            game_state.state = GameStates.MENU
