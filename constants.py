from enum import IntEnum, Enum, auto


class Textures(Enum):
    SEA = "piese_sea"
    BURNING = "ship_from_abdo_burn"
    SHIP = "ship_from_abdo"
    MENU_BACKFONE = "menu_phone"
    LETS_GAME = "game_button"
    SHOOTEN_SEA = "shooten"
    DESTROYED = "enemy_ship_shooten"


class GameStates(Enum):
    MENU = auto()
    SHIPS_place = auto()
    GAME = auto()
    VICTORY = auto()
    DEFEAT = auto()


class Constants(IntEnum):
    SPASE_OF_SCREEN = 25
    SIZE_PICTURE = 40
    SIZE_BOARD = 10


class AiModes(Enum):
    SEARCH = auto()
    HUNTING = auto()


class CellContent(Enum):
    WATER = auto()
    SHIP = auto()


class ShotState(Enum):
    NOT_SHOT = auto()
    MISS = auto()
    HIT = auto()
    DESTROYED = auto()
    
    
class Players(Enum):
    PLAYER=auto()
    COMPUTER=auto()
