import pyglet
import random
import math
from rect import Rect 


COLORS = {
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (234, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237,204,97),
    512: (237,200,80),
    1024: (237,197,63),
    2048: (237,197,1),
    4096: (94,218,146)
}


def dist(x1, y1, x2, y2):
    return abs(x1 - x2) + abs(y1 - y2)


class Tile:
    """A rectangle with a number"""
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        self.moving = False
        self.teleport = False
        self.to_x = self.x
        self.to_y = self.y

        if ( random.random() < 0.1):
            self.value = 4
        else:
            self.value = 2

        self.color = COLORS[self.value]
        self.child = None
        self.font_size = math.floor(72/96 * (self.width / len(str(self.value)) *.95))

        self.rect = Rect(self.x, self.y, self.width, self.height)
        self.label = pyglet.text.Label(str(self.value),
                                       font_name='Calibri',
                                       font_size=self.font_size,
                                       color=(0,0,0,255),
                                       x=self.x + self.width // 2,
                                       y=self.y + self.height // 2,
                                       anchor_x='center',
                                       anchor_y='center')

        print(self.label.width)

    def move_to(self, x, y, teleport=False):
        self.to_x = x
        self.to_y = y
        self.moving = True
        self.teleport = teleport

    def draw(self):
        if self.child is not None:
            self.child.draw()
        self.rect.fill(self.color)
        self.label.draw()

    def move(self, speed):
        if self.moving:
            if self.child is not None:
                self.child.move(speed)

            d = dist(self.x, self.y, self.to_x, self.to_y)
            if not self.teleport and d > speed:
                self.set(x=self.x + speed * (self.to_x - self.x) / d,
                         y=self.y + speed * (self.to_y - self.y) / d)
            else:
                self.set(x=self.to_x, y=self.to_y)
                self.teleport = False
                if self.child is not None:
                    if not self.child.moving:
                        self.set(value=self.value + self.child.value)
                        self.child = None
                        self.moving = False
                else:
                    self.moving = False
            
    def absorb(self, other):
        self.child = other
        self.moving = True

    def set(self, x=None, y=None, width=None, height=None, value=None, color=None):
        if x is not None:
            self.x = x
            self.rect.x = x
        if y is not None:
            self.y = y
            self.rect.y = y
        if width is not None:
            self.width = width
            self.rect.width = width
        if height is not None:
            self.height = height
            self.rect.height = height
        if value is not None:
            self.value = value
            self.label.text = str(self.value)
            self.color = COLORS[value]
            self.font_size = math.floor(72/96 * (self.width / len(str(self.value)) *.95))
        if color is not None:
            self.color = color
        
        self.label = pyglet.text.Label(str(self.value),
                                       font_name='Calibri',
                                       font_size=self.font_size,
                                       color=(0,0,0,255),
                                       x=self.x + self.width // 2,
                                       y=self.y + self.height // 2,
                                       anchor_x='center',
                                       anchor_y='center')


######################################################################################################

class Grid:
    """The background for the game
    """
    def __init__(self, width, height, row_size, buffer_size, background_color, empty_color):
        self.width = width
        self.height = height
        self.row_size = row_size
        self.buffer_size = buffer_size
        self.background_color = background_color
        self.empty_color = empty_color
        
        self.buffer_side_length = (self.width - self.buffer_size) // self.row_size
        self.side_length = self.buffer_side_length - self.buffer_size
        self.cells = []
        self.background = Rect(0, 0, self.width, self.height)
        for i in range(self.row_size):
            for j in range(self.row_size):
                self.cells.append(Rect(j * self.buffer_side_length + self.buffer_size,
                               i * self.buffer_side_length + self.buffer_size, 
                               self.side_length,
                               self.side_length,
                               ))

    def make_tile_at(self, x, y):
        return Tile(x * self.buffer_side_length + self.buffer_size,
                    y * self.buffer_side_length + self.buffer_size,
                    self.side_length,
                    self.side_length)

    def grid_pos_to_pixel_pos(self, x, y):
        return (x * self.buffer_side_length + self.buffer_size,
                y * self.buffer_side_length + self.buffer_size)

    def draw(self):
        self.background.fill(self.background_color)
        for cell in self.cells:
            cell.fill(self.empty_color)
