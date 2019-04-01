from entity import Entity
import tcod
from render_functions import RenderOrder

def shoot(shooter, target, game_map):
    #get equation of line
    #for each x value, get entry and exit y values
    slope = (target.y - shooter.y) / (target.x - shooter.x)
    cells = []
    start_x = min(shooter.x, target.x)
    end_x =  max(shooter.x, target.x)
    start_y = min(shooter.y, target.y)
    end_y =  max(shooter.y, target.y)
    for x in range(start_x, end_x+1):
        y_values = []
        entry = start_y + slope*(x - start_x)
        exit = start_y + slope*(x - start_x)
        print(str(x) + ": " + str(entry) + ", " + str(exit))
        for y in range(int(entry), int(exit)):
            cells.append([x, y])
    print(cells)

player1 = Entity(3, 4, '@', tcod.white, 'Player', blocks = True, render_order=RenderOrder.ACTOR)
player2 = Entity(1, 0, '@', tcod.white, 'Player', blocks = True, render_order=RenderOrder.ACTOR)
shoot(player1, player2, 4)
