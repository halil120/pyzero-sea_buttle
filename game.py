
from enum import IntEnum, Enum, auto
from collections import deque,Counter

HEIGHT = 500
WIDTH = 900
# одно поле равен ~38

class GameStates(Enum):
    MENU=auto()
    SHIPS_PLASE=auto()
    GAME=auto()
    VICTORY=auto()
    DEFEAT=auto()
    
class Constants(IntEnum):
    SPASE_OF_SCREEN=25 
    SIZE_PICTURE=38 
    
class Textures(Enum):
    SEA=images.piese_sea
    BURNING=images.burning
    SHIP=images.ship

    
class FieldObg:
    def __init__(self):
        self.is_sea=True
        self.is_ship=False
        self.is_shooten=False
    def shoot(self):
        self.is_shooten=True
    def un_or_plase_ship(self):
        self.is_ship=not self.is_ship
        self.is_sea=not self.is_sea
    def texture_give(self):
        if self.is_shooten:
            return Textures.BURNING.value
        elif self.is_ship:
            return Textures.SHIP.value
        else:
            return Textures.SEA.value
        
        
class StatesOfGame:
    def __init__(self):
        self.state = GameStates.SHIPS_PLASE
    
    # def get_game_state(self):
    #     if self.state==GameStates.GAME:     
        
        
class Field_Seeble:
    def __init__(self):
        pass
   
    def generate_field_enemy(self):
        field=[]
        for _ in range(10):
            in_field=[]
            for _ in range(10):
                in_field.append(FieldObg())
            field.append(in_field)
            
        self.enemy_field_see=field
        

    def draw_enemy(self,screen):
        x=Constants.SPASE_OF_SCREEN
        for i in range(10):
            y=Constants.SPASE_OF_SCREEN
            for j in range(10):
                screen.blit(self.enemy_field_see[i][j].texture_give(),(x,y))
                y+=round(Constants.SIZE_PICTURE, -1)
            x+=round(Constants.SIZE_PICTURE, -1)
        return x+Constants.SPASE_OF_SCREEN*2

    
    def generate_field_my(self):
        field=[]
        for _ in range(10):
            in_field=[]
            for _ in range(10):
                in_field.append(FieldObg())
            field.append(in_field)
            
        self.my_field_see=field
            
    def draw_my(self,screen,x):
        for i in range(10):
            y=Constants.SPASE_OF_SCREEN
            for j in range(10):
                screen.blit(self.my_field_see[i][j].texture_give(),(x,y))
                y+=round(Constants.SIZE_PICTURE, -1)
            x+=round(Constants.SIZE_PICTURE, -1)
            

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
    
    ship_nearby=False
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
                    ship_nearby=True
    all_x = {x for x,y in visited}
    all_y = {y for x,y in visited}
    is_straight = len(all_x) == 1 or len(all_y) == 1
    return len(visited),is_straight,ship_nearby
            

def valid_count_of_ship(field):
    global count_ship_error
    counter=Counter({1:0,2:0,3:0,4:0})
    all_visited=set()
    visited=set()
    count_ship_error=False
    eczample=Counter({1:4,2:3,3:2,4:1})
    for i in range(10):
        for j in range(10):
            if not field[i][j].is_ship:
                continue
            if (i,j) in visited or (i,j) in all_visited:
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
                        if not (0 <= next_x < len(field) and 0 <= next_y < len(field[next_x])):
                            continue
                        if (next_x, next_y) in visited:
                            continue
                        if field[next_x][next_y].is_ship:
                            queue.append((next_x, next_y))
                            visited.add((next_x, next_y))
                            all_visited.add((next_x, next_y))
            counter[len(visited)]+=1
            if counter[1]>eczample[1] or counter[2]>eczample[2] or counter[3]>eczample[3] or counter[4]>eczample[4]:
                count_ship_error=True
                return counter
    return counter



def valid_ship(field):
    global ship_error
    ship_error=False
    for row in range(10):
        for col in range(10):
            if not field[row][col].is_ship:
                continue
            len_ship,is_straight,ship_nearby=get_ship_length(field,row,col)
            if len_ship>4 or ship_nearby or not is_straight:
                ship_error=True
                
                    
    
        
        
def pixel_to_cordinates(x,y,my=False):
    if my:
        x-=Constants.SPASE_OF_SCREEN*3+round(Constants.SIZE_PICTURE, -1)*10
    else:
        x-=Constants.SPASE_OF_SCREEN
    y-=Constants.SPASE_OF_SCREEN
    x//=round(Constants.SIZE_PICTURE, -1)
    y//=round(Constants.SIZE_PICTURE, -1)
    if my:
        return x,y
    return x-10,y
    



field=Field_Seeble()
game_state=StatesOfGame()
ship_error=False
count_ship_error=False
field.generate_field_enemy()
field.generate_field_my()


def draw():
    screen.clear()
    x=field.draw_enemy(screen)
    field.draw_my(screen,x)
    if ship_error:
        screen.draw.text('ship error',(550,200),fontsize=74,color='white')
    elif count_ship_error:
        screen.draw.text('count ship error',(450,150),fontsize=74,color='white')
    # screen.blit('sea',(0,0))

    
    
def on_mouse_up(pos,button):
    x,y=pos
    if game_state.state==GameStates.SHIPS_PLASE:
        # if 25<x<425 and 25<y<425:
        #     clk_x,clk_y=pixel_to_cordinates(x,y)
        #     field.enemy_field_see[clk_x][clk_y].un_or_plase_ship()
        if 475<x<875 and 25<y<425:
            clk_x,clk_y=pixel_to_cordinates(x,y,True)
            field.my_field_see[clk_x][clk_y].un_or_plase_ship()
            valid_ship(field.my_field_see)
            valid_count_of_ship(field.my_field_see)
        




