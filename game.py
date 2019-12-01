import pyglet
from pyglet.window import key
import random
import time

from grid import Grid, Tile
from rect import Rect
from agent import MonteCarloAgent, State


class Player:

    def __init__(self, width, height, size, teleport=False):
        self.background = Grid(
            width,
            height,
            row_size=size,
            buffer_size=80 / size,
            background_color=(189,173,158),
            empty_color=(218,204,192)
        )
        self.grid = [[None for _ in range(size)] for _ in range(size)]
        self.size = size
        self.direction = None
        self.moving = False
        self.speed = 2000.0
        self.teleport = teleport

    def reset_grid(self):
        for r in range(len(self.grid)):
            for c in range(len(self.grid)):
                self.grid[r][c] = None 

    def add_random_tile(self):
        # Find open positions
        open_positions = []
        for y in range(self.size):
            for x in range(self.size):
                if not self.grid[y][x]:
                    open_positions.append((x,y))
        pos = random.choice(open_positions)

        # Create a new tile
        tile = self.background.make_tile_at(pos[0],pos[1])

        self.grid[pos[1]][pos[0]] = tile
        self.print_grid()

    def print_grid(self):
        elems = []
        for row in self.grid[::-1]:
            for x in row:
                elems.append(str(x.value) if x else '0')
            elems.append('\n')
        print(' '.join(elems))


    def can_move(self, direction):
        for x in range(self.size):
            for y in range(self.size):
                cur_tile = self.grid[y][x]
                if cur_tile:
                    if direction == "LEFT" and x > 0:
                        adj = self.grid[y][x - 1]
                        if (not adj or adj.value == cur_tile.value):
                            return True
                    if direction == "RIGHT" and x < self.size - 1:
                        adj = self.grid[y][x + 1]
                        if (not adj or adj.value == cur_tile.value):
                            return True
                    if direction == "DOWN" and y > 0:
                        adj = self.grid[y - 1][x]
                        if (not adj or adj.value == cur_tile.value):
                            return True
                    if direction == "UP" and y < self.size - 1:
                        adj = self.grid[y + 1][x]
                        if (not adj or adj.value == cur_tile.value):
                            return True
        return False

    def move_tile(self, x, y, to_x, to_y):
        tile = self.grid[y][x]
        self.grid[y][x] = None
        dest_tile = self.grid[to_y][to_x]
        if dest_tile is not None:
            dest_tile.absorb(tile)
        else:
            self.grid[to_y][to_x] = tile
        px, py = self.background.grid_pos_to_pixel_pos(to_x, to_y)
        tile.move_to(px, py, teleport=self.teleport)


    def transition(self, direction):
        if self.moving or not self.can_move(direction):
            return

        # Update grid representation
        if direction == 'LEFT':
            for y in range(self.size):
                prev_idx = 0
                for x in range(1, self.size):
                    cur_tile = self.grid[y][x]
                    if cur_tile:
                        # Check if empty
                        if self.grid[y][prev_idx] is None:
                            self.move_tile(x, y, prev_idx, y)
                        elif self.grid[y][prev_idx].value == cur_tile.value and prev_idx != x:
                            # Check Merge
                            self.move_tile(x, y, prev_idx, y)
                            prev_idx += 1
                        elif self.grid[y][prev_idx + 1] is None:
                            # Move into adj
                            self.move_tile(x, y, prev_idx + 1, y)
                            prev_idx += 1
                        else:
                            prev_idx = x
        elif direction == 'RIGHT':
            for y in range(self.size):
                prev_idx = self.size - 1
                for x in range(self.size - 2, -1, -1):
                    cur_tile = self.grid[y][x]
                    if cur_tile:
                        # Check if empty
                        if self.grid[y][prev_idx] is None:
                            self.move_tile(x, y, prev_idx, y)
                        elif self.grid[y][prev_idx].value == cur_tile.value and prev_idx != x:
                            # Check Merge
                            self.move_tile(x, y, prev_idx, y)
                            prev_idx -= 1
                        elif self.grid[y][prev_idx - 1] is None:
                            # Move into adj
                            self.move_tile(x, y, prev_idx - 1, y)
                            prev_idx -= 1
                        else:
                            prev_idx = x
        elif direction == 'DOWN':
            for x in range(self.size):
                prev_idx = 0
                for y in range(1, self.size):
                    cur_tile = self.grid[y][x]
                    if cur_tile:
                        # Check if empty
                        if self.grid[prev_idx][x] is None:
                            self.move_tile(x, y, x, prev_idx)
                        elif self.grid[prev_idx][x].value == cur_tile.value and prev_idx != y:
                            # Check Merge
                            self.move_tile(x, y, x, prev_idx)
                            prev_idx += 1
                        elif self.grid[prev_idx + 1][x] is None:
                            # Move into adj
                            self.move_tile(x, y, x, prev_idx + 1)
                            prev_idx += 1
                        else:
                            prev_idx = y
        elif direction == 'UP':
            for x in range(self.size):
                prev_idx = self.size - 1
                for y in range(self.size - 2, -1, -1):
                    cur_tile = self.grid[y][x]
                    if cur_tile:
                        # Check if empty
                        if self.grid[prev_idx][x] is None:
                            self.move_tile(x, y, x, prev_idx)
                        elif self.grid[prev_idx][x].value == cur_tile.value and prev_idx != y:
                            # Check Merge
                            self.move_tile(x, y, x, prev_idx)
                            prev_idx -= 1
                        elif self.grid[prev_idx - 1][x] is None:
                            # Move into adj
                            self.move_tile(x, y, x, prev_idx - 1)
                            prev_idx -= 1
                        else:
                            prev_idx = y

        self.print_grid()
        
        # Start moving tiles
        self.direction = direction
        self.moving = True
            

    def move(self, dt):
        if not self.moving:
            return
    
        for tile in self.iter_tiles():
            tile.move(self.speed * dt)

        self.moving = self.tiles_moving()
        if not self.moving:
            self.direction = None
            self.add_random_tile()
        
    def iter_tiles(self):
        for row in self.grid:
            for tile in row:
                if tile is not None:
                    yield tile

    def tiles_moving(self):
        for tile in self.iter_tiles():
            if tile.moving:
                return True
        return False

    def draw(self):
        self.background.draw()

        for tile in self.iter_tiles():
            tile.draw()



def start_game():
    width = 800
    height = 800
    fps = 60.0
    window = pyglet.window.Window(width, height)

    player = Player(width, height, 4)
    player.reset_grid()
    player.add_random_tile()
    player.add_random_tile()
    agent = MonteCarloAgent(max_depth=4, repetitions=30)
    player.was_moving = False

    def update(dt):
        if not player.moving:
            state = State()
            state.from_tiles(player.grid)
            direction = agent.get_move(state)
            state.transition(direction)
            if state.is_dead():
                print("GAME OVER")
                exit()
            player.transition(direction)
            player.was_moving = False
        else:
            if not player.was_moving:
                player.was_moving = True
            else:
                player.move(dt)



    @window.event
    def on_draw():
        window.clear()
        player.draw()

    @window.event
    def on_key_press(symbol, modifiers):
        if symbol == key.SPACE:
            player.reset_grid()
            player.add_random_tile()
            player.add_random_tile()

        if symbol == key.LEFT:
            player.transition('LEFT')
        if symbol == key.RIGHT:
            player.transition('RIGHT')
        if symbol == key.UP:
            player.transition('UP')
        if symbol == key.DOWN:
            player.transition('DOWN')

    pyglet.clock.schedule_interval(update, 1/fps)
    pyglet.app.run()


if __name__ == '__main__':
    start_game()

