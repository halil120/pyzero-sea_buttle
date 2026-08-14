from enum import IntEnum, Enum, auto
from collections import deque, Counter
from random import randint,choice
from time import sleep
HEIGHT = 500
WIDTH = 900
# одно поле равен ~38


class GameStates(Enum):
    MENU = auto()
    SHIPS_PLASE = auto()
    GAME = auto()
    VICTORY = auto()
    DEFEAT = auto()


class Constants(IntEnum):
    SPASE_OF_SCREEN = 25
    SIZE_PICTURE = 38


class Textures(Enum):
    SEA = images.piese_sea
    BURNING = images.ship_burning
    SHIP = images.ship
    MENU_BACKFONE = images.menu_phone
    LETS_GAME = images.game_button
    SHOOTEN_SEA=images.shooten





class FieldObg:
    def __init__(self,is_player=False):
        self.is_player=is_player
        self.is_sea = True
        self.is_ship = False
        self.is_shooten = False

    def shoot(self):
        self.is_shooten = True

    def un_or_plase_ship(self):
        self.is_ship = not self.is_ship
        self.is_sea = not self.is_sea

    def plase_ship(self):
        self.is_ship = True
        self.is_sea = False
        
    def un_plase_ship(self):
        self.is_ship = False
        self.is_sea = True

        
    def texture_give(self):
        if self.is_shooten and self.is_ship:
            return Textures.BURNING.value
        elif self.is_shooten and not self.is_ship:
            return Textures.SHOOTEN_SEA.value
        elif self.is_ship and self.is_player:
            return Textures.SHIP.value
        else:
            return Textures.SEA.value


class StatesOfGame:
    def __init__(self):
        self.state = GameStates.MENU

    # def get_game_state(self):
    #     if self.state==GameStates.GAME:


class Field_Seeble:
    def __init__(self):
        pass

    def generate_field_enemy(self):
        field = []
        for _ in range(10):
            in_field = []
            for _ in range(10):
                in_field.append(FieldObg())
            field.append(in_field)

        self.enemy_field_see = field

    def draw_enemy(self, screen):
        x = Constants.SPASE_OF_SCREEN
        for i in range(10):
            y = Constants.SPASE_OF_SCREEN
            for j in range(10):
                screen.blit(self.enemy_field_see[i][j].texture_give(), (x, y))
                y += round(Constants.SIZE_PICTURE, -1)
            x += round(Constants.SIZE_PICTURE, -1)
        return x + Constants.SPASE_OF_SCREEN * 2

    def generate_field_my(self):
        field = []
        for _ in range(10):
            in_field = []
            for _ in range(10):
                in_field.append(FieldObg(True))
            field.append(in_field)

        self.my_field_see = field

    def draw_my(self, screen, x):
        for i in range(10):
            y = Constants.SPASE_OF_SCREEN
            for j in range(10):
                screen.blit(self.my_field_see[i][j].texture_give(), (x, y))
                y += round(Constants.SIZE_PICTURE, -1)
            x += round(Constants.SIZE_PICTURE, -1)


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
    for i in range(10):
        for j in range(10):
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


def valid_ship(field):
    global ship_error
    ship_error = False
    for row in range(10):
        for col in range(10):
            if not field[row][col].is_ship:
                continue
            len_ship, is_straight, ship_nearby = get_ship_length(field, row, col)
            if len_ship > 4 or ship_nearby or not is_straight:
                ship_error = True


def pixel_to_cordinates(x, y, my=False):
    if my:
        x -= Constants.SPASE_OF_SCREEN * 3 + round(Constants.SIZE_PICTURE, -1) * 10
    else:
        x -= Constants.SPASE_OF_SCREEN
    y -= Constants.SPASE_OF_SCREEN
    x //= round(Constants.SIZE_PICTURE, -1)
    y //= round(Constants.SIZE_PICTURE, -1)
    if my:
        return x, y
    return x - 10, y


def backfill(screen):
    if game_state.state == GameStates.MENU:
        screen.blit(Textures.MENU_BACKFONE.value, (0, 0))
        screen.blit(Textures.LETS_GAME.value, (300, 150))
    elif (
        game_state.state == GameStates.SHIPS_PLASE
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
    elif game_state.state == GameStates.VICTORY or game_state.state == GameStates.DEFEAT:
        screen.fill((51, 204, 242))
        if game_state.state == GameStates.VICTORY:
            screen.draw.text('!VICTORY!',(350,200),fontsize=75,color='white')
        elif game_state.state == GameStates.DEFEAT:
            screen.draw.text('DEFEAT',(350,200),fontsize=75,color='red')


def error(screen):
    if game_state.state == GameStates.SHIPS_PLASE:
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


def plase_ships_enemy(field):
    rotations=[(0,1),(1,0)]
    ships=[4,3,3,2,2,2,1,1,1,1]
    for lenght in ships:
        plased=False
        for _ in range(100):
            rx=randint(0,9)
            ry=randint(0,9)
            dx, dy = choice(rotations)
            ship_cells = []
            for step in range(lenght):
                x = rx + dx * step
                y = ry + dy * step
                ship_cells.append((x, y))
            if not all(map(lambda i:True if 0<=i[0]<10 and 0<=i[1]<10 else False,ship_cells)):
                continue
            can_plase=True
            for x,y in ship_cells:
                for kor_x in (1,0,-1):
                    for kor_y in (1,0,-1):
                        next_x=x+kor_x
                        next_y=y+kor_y
                        if not (0<=next_x<10 and 0<=next_y<10):
                            continue
                        if field.enemy_field_see[next_x][next_y].is_ship:
                            can_plase=False
            if not can_plase:
                continue
            for x,y in ship_cells:
                field.enemy_field_see[x][y].plase_ship()
            plased=True
            break
    if plased:
        return True
    return False


def some_ones_turn(turn,field,x_clict,y_clict):
    if turn:
        if not field[x_clict][y_clict].is_shooten:
            field[x_clict][y_clict].shoot()
            if field[x_clict][y_clict].is_ship:
                return turn
            return not turn
        return turn

def ais_turn(field,gratest_next_move=False):
    rx=randint(0,9)
    ry=randint(0,9)
    rotations=[(0,1),(1,0),(-1,0),(0,-1)]
    while field[rx][ry].is_shooten:
        rx=randint(0,9)
        ry=randint(0,9)
    next_move=True
    if gratest_next_move:
        x,y=gratest_next_move
        field[x][y].shoot()
        if field[x][y].is_ship:
            next_move=False
        for rot_x,rot_y in rotations:
            next_x=x+rot_x
            next_y=y+rot_y
            if not (0<=next_x<10 and 0<=next_y<10):
                continue
            if field[next_x][next_y].is_ship and not field[next_x][next_y].is_shooten:
                return (next_x,next_y),next_move
        return False ,next_move
    else:
        field[rx][ry].shoot()
        if field[rx][ry].is_ship:
            next_move=False
            return (rx,ry),next_move
        return False,next_move
        
def check_los_or_vin(field):
    for row in field:
        for cord in row:
            if cord.is_ship and not cord.is_shooten:
                return False
    return True
        



field = Field_Seeble()
game_state = StatesOfGame()
ship_error = False
count_ship_error = False
field.generate_field_enemy()
field.generate_field_my()
wrong=plase_ships_enemy(field)
while not wrong:
    field.generate_field_enemy()
    wrong=plase_ships_enemy(field)
ready_to_game = False
is_player_turn=True
gratest_move=False

def draw():
    screen.clear()
    backfill(screen)
    error(screen)


def update():
    global is_player_turn,gratest_move
    if game_state.state == GameStates.GAME:
        if not is_player_turn:
            gratest_move,next_move=ais_turn(field.my_field_see,gratest_move)
            if check_los_or_vin(field.my_field_see):
                game_state.state = GameStates.DEFEAT
            is_player_turn= next_move



def on_mouse_up(pos, button):
    global ready_to_game, is_player_turn, gratest_move
    x, y = pos
    if game_state.state == GameStates.MENU:
        if 300 <= x < 600 and 150 <= y < 302:
            field.generate_field_enemy()
            field.generate_field_my()
            wrong=plase_ships_enemy(field)
            while not wrong:
                field.generate_field_enemy()
                wrong=plase_ships_enemy(field)
            game_state.state = GameStates.SHIPS_PLASE
            
    elif game_state.state == GameStates.SHIPS_PLASE:
        if 475 < x < 875 and 25 < y < 425:
            clk_x, clk_y = pixel_to_cordinates(x, y, True)
            field.my_field_see[clk_x][clk_y].un_or_plase_ship()
            valid_ship(field.my_field_see)
            ships = valid_count_of_ship(field.my_field_see)
            if check_ready_to_game(ships) == 20:
                ready_to_game = True

        if not ship_error and ready_to_game and 100 <= x < 400 and 150 <= y < 302:
            ready_to_game = False
            game_state.state = GameStates.GAME

    elif game_state.state == GameStates.GAME:
        
        if 25<x<425 and 25<y<425:
            clk_x,clk_y=pixel_to_cordinates(x,y)
            is_player_turn=some_ones_turn(is_player_turn,field.enemy_field_see,clk_x,clk_y)
            if check_los_or_vin(field.enemy_field_see):
                game_state.state = GameStates.VICTORY
        
        if 5 <= x < 63 and 475 <= y < 500:
            game_state.state = GameStates.MENU
    
    elif game_state.state == GameStates.VICTORY or game_state.state == GameStates.DEFEAT:
       if button:
        game_state.state = GameStates.MENU

