import pyglet


class Rect:
    """Get rect'd
    """
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def fill(self, color):
        color = color if len(color) == 4 else color + (255,)
        pyglet.graphics.draw(
                4, pyglet.gl.GL_QUADS,
                ('v2f',
                    (self.x, self.y,
                     self.x + self.width, self.y,
                     self.x + self.width, self.y + self.height,
                     self.x, self.y + self.height)
                ),
                ('c4B', color*4)
            )

    def overlaps(self, rect2):
        if ((self.x < rect2.x + rect2.width) and 
           (self.x + self.width > rect2.x) and
           (self.y < rect2.y + rect2.height) and
           (self.y + self.height > rect2.y)):
               return True
        return False
