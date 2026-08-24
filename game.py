from collections import deque, Counter
from random import randint, choice
from constants import (
    Textures,
    Constants,
    GameStates,
    AiModes,
    Directions,
    ShotState,
    CellContent,
    Players,
)

HEIGHT = 500
WIDTH = 900
TITLE = "Sea Buttle"


class Cell:
    def __init__(self):
        self.content = CellContent.WATER
        self.shot_state = ShotState.NOT_SHOT

    def shoot(self):
        match self.content:
            case CellContent.WATER:
                self.shot_state = ShotState.MISS
            case CellContent.SHIP:
                if not self.shot_state == ShotState.DESTROYED:
                    self.shot_state = ShotState.HIT

    def un_or_place_ship(self):
        match self.content:
            case CellContent.WATER:
                self.content = CellContent.SHIP
            case CellContent.SHIP:
                self.content = CellContent.WATER

    def place_ship(self):
        self.content = CellContent.SHIP

    def un_place_ship(self):
        self.content = CellContent.WATER


class Board:
    def __init__(self, owner):
        self.board_owner = owner
        self.board = []

    def generate(self):
        field = []
        for _ in range(Constants.SIZE_BOARD):
            in_field = []
            for _ in range(Constants.SIZE_BOARD):
                in_field.append(Cell())
            field.append(in_field)

        self.board = field

    def draw_field(self, screen, x, see_ships=False):
        for i in range(Constants.SIZE_BOARD):
            y = Constants.SPASE_OF_SCREEN
            for j in range(Constants.SIZE_BOARD):
                screen.blit(self.texture_give(self.board[i][j], see_ships), (x, y))
                y += Constants.SIZE_PICTURE
            x += Constants.SIZE_PICTURE

    def fill_test(self):
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
            self.board[x][y].place_ship()

    def texture_give(self, cell, see_ship):
        match cell.content:
            case CellContent.WATER:
                match cell.shot_state:
                    case ShotState.NOT_SHOT:
                        return Textures.SEA.value
                    case ShotState.MISS:
                        return Textures.SHOOTEN_SEA.value
            case CellContent.SHIP:
                match cell.shot_state:
                    case ShotState.NOT_SHOT:
                        if self.board_owner == Players.PLAYER or see_ship:
                            return Textures.SHIP.value
                        return Textures.SEA.value
                    case ShotState.HIT:
                        return Textures.BURNING.value
                    case ShotState.DESTROYED:
                        return Textures.DESTROYED.value


class ComputerPlayer:
    def __init__(self, board):
        self.board = board
        self.rotations = [(0, 1), (1, 0), (-1, 0), (0, -1)]
        self.target_cells = set()
        self.hit_cells = set()
        self.mode = AiModes.SEARCH
        self.visited_dontmovehere = set()

    def move(self):
        next_move = True
        # logic block
        if self.mode == AiModes.SEARCH:
            x = randint(0, Constants.SIZE_BOARD - 1)
            y = randint(0, Constants.SIZE_BOARD - 1)
            while (
                not self.board[x][y].shot_state == ShotState.NOT_SHOT
                or (x, y) in self.visited_dontmovehere
            ):
                x = randint(0, Constants.SIZE_BOARD - 1)
                y = randint(0, Constants.SIZE_BOARD - 1)

            self.board[x][y].shoot()
            if self.board[x][y].content == CellContent.WATER:
                next_move = True
            elif self.board[x][y].content == CellContent.SHIP:
                if self.reset(x, y):
                    return False
                self.mode = AiModes.HUNTING
                for mx, my in self.rotations:
                    next_x = x + mx
                    next_y = y + my
                    self.target_cells.add((next_x, next_y))
                return False
        elif self.mode == AiModes.HUNTING:
            if not self.target_cells:
                self.mode = AiModes.SEARCH
                self.hit_cells.clear()
                return True
            while self.target_cells:
                x, y = choice(list(self.target_cells))
                self.target_cells.discard((x, y))
                if (x, y) in self.visited_dontmovehere:
                    continue
                if not (
                    0 <= x < Constants.SIZE_BOARD and 0 <= y < Constants.SIZE_BOARD
                ):
                    continue
                if not self.board[x][y].shot_state == ShotState.NOT_SHOT:
                    continue
                self.board[x][y].shoot()
                if not self.board[x][y].content == CellContent.SHIP:
                    next_move = True
                    return next_move
                elif self.board[x][y].content == CellContent.SHIP:
                    if self.reset(x, y):
                        return False
                    all_x = {x for x, y in self.hit_cells}
                    all_y = {y for x, y in self.hit_cells}

                    if len(all_x) < 2:
                        self.target_cells = set()
                        for tar_x, tar_y in self.hit_cells:
                            for rot_x, rot_y in ((0, -1), (0, 1)):
                                tx = tar_x + rot_x
                                ty = tar_y + rot_y
                                if not (
                                    0 <= tx < Constants.SIZE_BOARD
                                    and 0 <= ty < Constants.SIZE_BOARD
                                ):
                                    continue
                                if (
                                    not self.board[tx][ty].shot_state
                                    == ShotState.NOT_SHOT
                                ):
                                    continue
                                self.target_cells.add((tx, ty))
                    elif len(all_y) < 2:
                        self.target_cells = set()
                        for tar_x, tar_y in self.hit_cells:
                            for rot_x, rot_y in ((-1, 0), (1, 0)):
                                tx = tar_x + rot_x
                                ty = tar_y + rot_y
                                if not (
                                    0 <= tx < Constants.SIZE_BOARD
                                    and 0 <= ty < Constants.SIZE_BOARD
                                ):
                                    continue
                                if (
                                    not self.board[tx][ty].shot_state
                                    == ShotState.NOT_SHOT
                                ):
                                    continue
                                self.target_cells.add((tx, ty))
                    next_move = False
                    return next_move
        return next_move

    def reset(self, x, y):
        self.hit_cells.add((x, y))
        ship_cells = count_of_non_shooten(x, y, self.board)
        if self.hit_cells == ship_cells:
            for x, y in self.hit_cells:
                self.board[x][y].shot_state = ShotState.DESTROYED
            self.visited_dontmovehere.update(do_step_on(ship_cells))
            self.hit_cells.clear()
            self.target_cells.clear()
            self.mode = AiModes.SEARCH
            self.current_direction = None
            return True
        return False


class Game:
    def __init__(self):
        self.player_field = Board(Players.PLAYER)
        self.computer_field = Board(Players.COMPUTER)
        self.state = GameStates.MENU
        self.ai = ComputerPlayer(self.player_field.board)
        self.ship_error = False
        self.count_ship_error = False
        self.ready_to_game = False
        self.is_player_turn = True

    def xy_but_set(self, x, y, button):
        self.x = x
        self.y = y
        self.button = button

    def state_MENU(self):
        self.near_ship_ai = set()
        self.is_player_turn = True
        if 300 <= self.x < 600 and 150 <= self.y < 302:
            self.player_field.generate()
            self.computer_field.generate()
            wrong = place_ships_enemy(self.computer_field.board)
            self.ai = ComputerPlayer(self.player_field.board)
            while not wrong:
                self.computer_field.generate()
                wrong = place_ships_enemy(self.computer_field.board)
            self.state = GameStates.SHIPS_place

    def state_SHIPS_place(self):
        if 475 < self.x < 875 and 25 < self.y < 425:
            clk_x, clk_y = pixel_to_cordinates(self.x, self.y, True)
            self.player_field.board[clk_x][clk_y].un_or_place_ship()
            valid_ship(self.player_field.board)
            ships = valid_count_of_ship(self.player_field.board)
            if check_ready_to_game(ships) == 20:
                self.ready_to_game = True
            else:
                self.ready_to_game = False

        if (
            not self.ship_error
            and self.ready_to_game
            and 100 <= self.x < 400
            and 150 <= self.y < 302
        ):
            self.ready_to_game = False
            self.state = GameStates.GAME

    def state_GAME(self):
        if 25 < self.x < 425 and 25 < self.y < 425:
            clk_x, clk_y = pixel_to_cordinates(self.x, self.y)
            self.is_player_turn = players_ones_turn(
                self.is_player_turn, self.computer_field.board, clk_x, clk_y
            )
            if check_los_or_vin(self.computer_field.board):
                self.state = GameStates.VICTORY

        if 5 <= self.x < 63 and 475 <= self.y < 500:
            self.state = GameStates.MENU

    def state_VIN_LOS(self):
        if self.button:
            self.state = GameStates.MENU


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
                if field[next_x][next_y].content == CellContent.SHIP:
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
                if (next_x, next_y) not in visited and field[next_x][
                    next_y
                ].content == CellContent.SHIP:
                    ship_nearby = True
    all_x = {x for x, y in visited}
    all_y = {y for x, y in visited}
    is_straight = len(all_x) == 1 or len(all_y) == 1
    return len(visited), is_straight, ship_nearby


def valid_count_of_ship(field):
    counter = Counter({1: 0, 2: 0, 3: 0, 4: 0})
    all_visited = set()
    visited = set()
    game.count_ship_error = False
    eczample = Counter({1: 4, 2: 3, 3: 2, 4: 1})
    for i in range(Constants.SIZE_BOARD):
        for j in range(Constants.SIZE_BOARD):
            if not field[i][j].content == CellContent.SHIP:
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
                        if field[next_x][next_y].content == CellContent.SHIP:
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
                game.count_ship_error = True
                return counter
    return counter


def is_ship_died(x, y, field, is_for_player=False):
    deq = deque([(x, y)])
    viuved = set([(x, y)])
    count_of_sooten = 0
    if not field[x][y].content == CellContent.SHIP:
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
                if (
                    field[next_x][next_y].shot_state == ShotState.HIT
                    and field[next_x][next_y].content == CellContent.SHIP
                ):
                    count_of_sooten += 1
                if field[next_x][next_y].content == CellContent.SHIP:
                    deq.append((next_x, next_y))
                    viuved.add((next_x, next_y))

    if len(viuved) == count_of_sooten + 1:
        for x, y in viuved:
            field[x][y].shot_state = ShotState.DESTROYED
        return viuved
    return False


def valid_ship(field):
    game.ship_error = False
    for row in range(Constants.SIZE_BOARD):
        for col in range(Constants.SIZE_BOARD):
            if not field[row][col].content == CellContent.SHIP:
                continue
            len_ship, is_straight, ship_nearby = get_ship_length(field, row, col)
            if len_ship > 4 or ship_nearby or not is_straight:
                game.ship_error = True


def count_of_non_shooten(x, y, field):
    deq = deque([(x, y)])
    viuved = set([(x, y)])
    count_of_sooten = 0
    if field[x][y].content == CellContent.WATER:
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
                if (
                    field[next_x][next_y].shot_state == ShotState.HIT
                    and field[next_x][next_y].content == CellContent.SHIP
                ):
                    count_of_sooten += 1
                if field[next_x][next_y].content == CellContent.SHIP:
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
    if game.state == GameStates.MENU:
        screen.blit(Textures.MENU_BACKFONE.value, (0, 0))
        screen.blit(Textures.LETS_GAME.value, (300, 150))
    elif game.state == GameStates.SHIPS_place or game.state == GameStates.GAME:
        screen.blit("sea", (-200, -200))
        game.computer_field.draw_field(screen, 25)
        game.player_field.draw_field(screen, 475)
        screen.draw.text("my field", (630, 440), fontsize=50)
        screen.draw.text("enemy field", (130, 440), fontsize=50)
        if game.ready_to_game and not game.ship_error:
            screen.blit(Textures.LETS_GAME.value, (100, 150))
        if game.state == GameStates.GAME:
            screen.blit("insta_loose", (5, 475))
    elif game.state == GameStates.VICTORY or game.state == GameStates.DEFEAT:
        screen.blit("sea", (-200, -200))
        game.computer_field.draw_field(screen, 25, True)
        game.player_field.draw_field(screen, 475)
        if game.state == GameStates.VICTORY:
            screen.draw.text("!VICTORY!", (350, 200), fontsize=75, color="white")
        elif game.state == GameStates.DEFEAT:
            screen.draw.text("DEFEAT", (350, 200), fontsize=75, color="red")


def error(screen):
    if game.state == GameStates.SHIPS_place:
        if game.ship_error:
            screen.draw.text("ship error", (550, 200), fontsize=74, color="white")
        elif game.count_ship_error:
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
                        if field[next_x][next_y].content == CellContent.SHIP:
                            can_place = False
            if not can_place:
                continue
            for x, y in ship_cells:
                field[x][y].place_ship()
            placed = True
            break
    # for developers
    # game.player_field.fill_test()
    # for developers
    if placed:
        return True
    return False


def players_ones_turn(turn, board, x_clict, y_clict):
    if turn:
        if board[x_clict][y_clict].shot_state == ShotState.NOT_SHOT:
            board[x_clict][y_clict].shoot()
            is_ship_died(x_clict, y_clict, game.computer_field.board, True)
            if board[x_clict][y_clict].content == CellContent.SHIP:
                return turn
            return not turn
        return turn


def check_los_or_vin(field):
    for row in field:
        for cord in row:
            if (
                cord.content == CellContent.SHIP
                and not cord.shot_state == ShotState.DESTROYED
            ):
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
                    0 <= next_x < len(game.player_field.board)
                    and 0 <= next_y < len(game.player_field.board[next_x])
                ):
                    continue
                if (next_x, next_y) in ship:
                    continue
                not_choose_this.add((next_x, next_y))
    return not_choose_this


game = Game()


def draw():
    screen.clear()
    backfill(screen)
    error(screen)


def update():
    if game.state == GameStates.GAME:
        if not game.is_player_turn:
            next_move = game.ai.move()
            if check_los_or_vin(game.player_field.board):
                game.state = GameStates.DEFEAT
            game.is_player_turn = next_move


def on_mouse_up(pos, button):
    x, y = pos
    game.xy_but_set(x, y, button)
    match game.state:
        case GameStates.MENU:
            game.state_MENU()

        case GameStates.SHIPS_place:
            game.state_SHIPS_place()

        case GameStates.GAME:
            game.state_GAME()

        case GameStates.VICTORY | GameStates.DEFEAT:
            game.state_VIN_LOS()
