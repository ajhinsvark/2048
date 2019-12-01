from grid import Tile

from collections import deque
from copy import deepcopy
import random
import time

times = {}

def reset_times():
    global times
    for k in times:
        times[k] = 0

def start_timer(name):
    global times
    times["START_" + name] = time.time()

def stop_timer(name):
    global times
    if name in times:
        times[name] += time.time() - times["START_" + name]
    else:
        times[name] = time.time() - times["START_" + name]

def print_times():
    global times
    for k in times:
        if not k.startswith("START_"):
            print(f"{k}: {times[k]}")


class State:
    def __init__(self, grid=[], merges=0, state=None):
        self.grid = grid
        self.merges = merges
        self.score = 0
        if state is not None:
            self.score = state.score
            self.grid = deepcopy(state.grid)
            self.merges = state.merges

        self.empty_positions = self._get_empty_positions()
        self.valid_moves = self._get_move_directions()

    def from_tiles(self, tiles):
        self.grid = []
        for row in tiles:
            num_row = []
            for tile in row:
                if tile is not None:
                    num_row.append(tile.value)
                else:
                    num_row.append(0)
            self.grid.append(num_row)
                
    def move_tile_in_place(self, new_grid, src_x, src_y, dest_x, dest_y):
        start_timer("move_in_place")
        val = new_grid[src_y][src_x]
        new_grid[dest_y][dest_x] += val
        new_grid[src_y][src_x] = 0
        self.empty_positions.discard((dest_y, dest_x))
        self.empty_positions.add((src_y, src_x))
        stop_timer("move_in_place")

    def move_tile(self, new_grid, src_x, src_y, dest_x, dest_y):
        val = new_grid[src_y][src_x]
        new_grid[dest_y][dest_x] += val
        new_grid[src_y][src_x] = 0

    def set_from(self, state):
        for r, row in enumerate(state.grid):
            for c, x in enumerate(row):
                self.grid[r][c] = x
        self.merges = state.merges
        self.empty_positions = state.empty_positions
        self.valid_moves = state.valid_moves
        self.score = state.score

    def add_random_tile(self):
        y, x = random.choice(list(self.empty_positions))
        if random.random() < 0.1:
            self.grid[y][x] = 4
            self.score += 4
        else:
            self.grid[y][x] = 2
            self.score += 2
        self.empty_positions.discard((y,x))
        self.valid_moves = self._get_move_directions()


    def _get_move_directions(self):
        directions = set()
        for x in range(len(self.grid)):
            for y in range(len(self.grid)):
                cur_val = self.grid[y][x]
                if cur_val > 0:
                    if x > 0:
                        adj = self.grid[y][x - 1]
                        if (adj == 0 or adj == cur_val):
                            directions.add("LEFT")
                    if x < len(self.grid) - 1:
                        adj = self.grid[y][x + 1]
                        if (adj == 0 or adj == cur_val):
                            directions.add("RIGHT")
                    if y > 0:
                        adj = self.grid[y - 1][x]
                        if (adj == 0 or adj == cur_val):
                            directions.add("DOWN")
                    if y < len(self.grid) - 1:
                        adj = self.grid[y + 1][x]
                        if (adj == 0 or adj == cur_val):
                            directions.add("UP")
        return directions
        

    def can_move(self, direction):
        return direction in self.valid_moves

    def _get_empty_positions(self):
        empty_pos = set()
        for r, row in enumerate(self.grid):
            for c, x in enumerate(row):
                if x == 0:
                    empty_pos.add((r,c))
        return empty_pos

    def transition_in_place(self, direction):
        # Update grid representation
        merges = 0
        if direction == 'LEFT':
            for y in range(len(self.grid)):
                prev_idx = 0
                for x in range(1, len(self.grid[y])):
                    cur_tile = self.grid[y][x]
                    if cur_tile:
                        # Check if empty
                        if self.grid[y][prev_idx] == 0:
                            self.move_tile_in_place(self.grid, x, y, prev_idx, y)
                        elif self.grid[y][prev_idx] == cur_tile and prev_idx != x:
                            # Check Merge
                            self.move_tile_in_place(self.grid, x, y, prev_idx, y)
                            merges += 1
                            prev_idx += 1
                        elif self.grid[y][prev_idx + 1] == 0:
                            # Move into adj
                            self.move_tile_in_place(self.grid, x, y, prev_idx + 1, y)
                            prev_idx += 1
                        else:
                            prev_idx = x
        elif direction == 'RIGHT':
            for y in range(len(self.grid)):
                prev_idx = len(self.grid) - 1
                for x in range(len(self.grid[y]) - 2, -1, -1):
                    cur_tile = self.grid[y][x]
                    if cur_tile:
                        # Check if empty
                        if self.grid[y][prev_idx] == 0:
                            self.move_tile_in_place(self.grid, x, y, prev_idx, y)
                        elif self.grid[y][prev_idx] == cur_tile and prev_idx != x:
                            # Check Merge
                            self.move_tile_in_place(self.grid, x, y, prev_idx, y)
                            merges += 1
                            prev_idx -= 1
                        elif self.grid[y][prev_idx - 1] == 0:
                            # Move into adj
                            self.move_tile_in_place(self.grid, x, y, prev_idx - 1, y)
                            prev_idx -= 1
                        else:
                            prev_idx = x
        elif direction == 'DOWN':
            for x in range(len(self.grid)):
                prev_idx = 0
                for y in range(1, len(self.grid)):
                    cur_tile = self.grid[y][x]
                    if cur_tile:
                        # Check if empty
                        if self.grid[prev_idx][x] == 0:
                            self.move_tile_in_place(self.grid, x, y, x, prev_idx)
                        elif self.grid[prev_idx][x] == cur_tile and prev_idx != y:
                            # Check Merge
                            self.move_tile_in_place(self.grid, x, y, x, prev_idx)
                            merges += 1
                            prev_idx += 1
                        elif self.grid[prev_idx + 1][x] == 0:
                            # Move into adj
                            self.move_tile_in_place(self.grid, x, y, x, prev_idx + 1)
                            prev_idx += 1
                        else:
                            prev_idx = y
        elif direction == 'UP':
            for x in range(len(self.grid)):
                prev_idx = len(self.grid) - 1
                for y in range(len(self.grid) - 2, -1, -1):
                    cur_tile = self.grid[y][x]
                    if cur_tile:
                        # Check if empty
                        if self.grid[prev_idx][x] == 0:
                            self.move_tile_in_place(self.grid, x, y, x, prev_idx)
                        elif self.grid[prev_idx][x] == cur_tile and prev_idx != y:
                            # Check Merge
                            self.move_tile_in_place(self.grid, x, y, x, prev_idx)
                            merges += 1
                            prev_idx -= 1
                        elif self.grid[prev_idx - 1][x] == 0:
                            # Move into adj
                            self.move_tile_in_place(self.grid, x, y, x, prev_idx - 1)
                            prev_idx -= 1
                        else:
                            prev_idx = y
        self.merges += merges
        #start_timer("get_moves")
        # self.valid_moves = self._get_move_directions()
        # stop_timer("get_moves")
        return self
        

    def transition(self, direction):
        # Update grid representation
        new_grid = [[x for x in row] for row in self.grid]
        merges = 0
        if direction == 'LEFT':
            for y in range(len(new_grid)):
                prev_idx = 0
                for x in range(1, len(new_grid[y])):
                    cur_tile = new_grid[y][x]
                    if cur_tile:
                        # Check if empty
                        if new_grid[y][prev_idx] == 0:
                            self.move_tile(new_grid, x, y, prev_idx, y)
                        elif new_grid[y][prev_idx] == cur_tile and prev_idx != x:
                            # Check Merge
                            self.move_tile(new_grid, x, y, prev_idx, y)
                            merges += 1
                            prev_idx += 1
                        elif new_grid[y][prev_idx + 1] == 0:
                            # Move into adj
                            self.move_tile(new_grid, x, y, prev_idx + 1, y)
                            prev_idx += 1
                        else:
                            prev_idx = x
        elif direction == 'RIGHT':
            for y in range(len(new_grid)):
                prev_idx = len(self.grid) - 1
                for x in range(len(new_grid[y]) - 2, -1, -1):
                    cur_tile = new_grid[y][x]
                    if cur_tile:
                        # Check if empty
                        if new_grid[y][prev_idx] == 0:
                            self.move_tile(new_grid, x, y, prev_idx, y)
                        elif new_grid[y][prev_idx] == cur_tile and prev_idx != x:
                            # Check Merge
                            self.move_tile(new_grid, x, y, prev_idx, y)
                            merges += 1
                            prev_idx -= 1
                        elif new_grid[y][prev_idx - 1] == 0:
                            # Move into adj
                            self.move_tile(new_grid, x, y, prev_idx - 1, y)
                            prev_idx -= 1
                        else:
                            prev_idx = x
        elif direction == 'DOWN':
            for x in range(len(new_grid)):
                prev_idx = 0
                for y in range(1, len(new_grid)):
                    cur_tile = new_grid[y][x]
                    if cur_tile:
                        # Check if empty
                        if new_grid[prev_idx][x] == 0:
                            self.move_tile(new_grid, x, y, x, prev_idx)
                        elif new_grid[prev_idx][x] == cur_tile and prev_idx != y:
                            # Check Merge
                            self.move_tile(new_grid, x, y, x, prev_idx)
                            merges += 1
                            prev_idx += 1
                        elif new_grid[prev_idx + 1][x] == 0:
                            # Move into adj
                            self.move_tile(new_grid, x, y, x, prev_idx + 1)
                            prev_idx += 1
                        else:
                            prev_idx = y
        elif direction == 'UP':
            for x in range(len(new_grid)):
                prev_idx = len(self.grid) - 1
                for y in range(len(new_grid) - 2, -1, -1):
                    cur_tile = new_grid[y][x]
                    if cur_tile:
                        # Check if empty
                        if new_grid[prev_idx][x] == 0:
                            self.move_tile(new_grid, x, y, x, prev_idx)
                        elif new_grid[prev_idx][x] == cur_tile and prev_idx != y:
                            # Check Merge
                            self.move_tile(new_grid, x, y, x, prev_idx)
                            merges += 1
                            prev_idx -= 1
                        elif new_grid[prev_idx - 1][x] == 0:
                            # Move into adj
                            self.move_tile(new_grid, x, y, x, prev_idx - 1)
                            prev_idx -= 1
                        else:
                            prev_idx = y
        return State(new_grid, merges=self.merges + merges)

    def is_dead(self):
        return len(self.empty_positions) == 0

    def is_able_to_move(self):
        for direction in ["UP", "DOWN", "LEFT", "RIGHT"]:
            if self.can_move(direction):
                return True
        return False

    def __str__(self):
        rows = []
        for row in self.grid[::-1]:
            rows.append(' '.join([str(x) for x in row]))
        return '\n'.join(rows)

    def full_stats(self):
        return f"{'-' * 20}\n{str(self)}\nmerges: {self.merges}\ndirs: {self.valid_moves}\nempty: {self.empty_positions}\n{'-' * 20}"
        
class Node:
    def __init__(self, state, parent, depth):
        self.state = state
        self.depth = depth
        self.parent = parent
        self.best_child = -1


def max_to_corner(state):
    total = 0
    numbered_tiles = 0
    max_pos = ()
    max_val = 1
    for r, row in enumerate(state.grid):
        for c, x in enumerate(row):
            if x != 0:
                total += x
                numbered_tiles += 1
                if x > max_val:
                    max_pos = (r,c)
                    max_val = x
    max_dist_to_corner = max_pos[0] + max_pos[1]
    tile_density = total / numbered_tiles

    value = tile_density
    # value = max_val
    if max_pos[0] == 0:
        value *= 5
        if max_pos[1] == 0:
            value *= 2

    second_max_val = 0
    second_max_pos = ()
    for r, row in enumerate(state.grid):
        for c, x in enumerate(row):
            if (r,c) != max_pos and x > second_max_val:
                second_max_pos = (r,c)
                second_max_val = x

    if second_max_pos[0] == 0:
        value *= 2

    third_max_val = -1
    third_max_pos = ()
    for r, row in enumerate(state.grid):
        for c, x in enumerate(row):
            if (r,c) != max_pos and (r,c) != second_max_pos and x > third_max_val:
                third_max_pos = (r,c)
                third_max_val = x

    if third_max_pos[0] == 0:
        value *= 1.5
    
    return value


def adj_tiles(state):
    count = 0
    values = []
    for r in range(len(state.grid)):
        for c in range(len(state.grid[r])):
            cur = state.grid[r][c]
            if r > 0:
               above = state.grid[r-1][c] 
               if above == cur:
                   count += 1
                   values.append(cur)
            if c > 0:
                left = state.grid[r][c-1]
                if left == cur:
                    values.append(cur)
    return count


def tile_density(state):
    total = 0
    numbered_tiles = 0
    for r, row in enumerate(state.grid):
        for c, x in enumerate(row):
            if x != 0:
                total += x
                numbered_tiles += 1
    tile_density = total / numbered_tiles

    return tile_density


class Agent:
    def __init__(self, max_depth=3):
        self.directions = ["LEFT", "DOWN", "RIGHT", "UP"]
        self.max_depth = max_depth
        self.states_considered = 0

    def value_state(self, state):
        self.states_considered += 1
        value = state.merges
        # value = sum([sum(row) for row in state.grid]) + 2**adj_tiles(state)
        # value = max_to_corner(state)
        # value = tile_density(state)
        return value

    def get_random_successors(self, state):
        for y, x in list(state.empty_positions):
            for val in [2, 4]:
                rand_state = State(state=state)
                rand_state.grid[y][x] = val
                yield rand_state

    def find_best(self, state, MAX_DEPTH=3):
        value = self.value_state(state)
        if MAX_DEPTH == 0 or not state.is_able_to_move():
            return value, None
        max_v = value
        best_dir = "LEFT"
        for direction in self.directions:
            if state.can_move(direction):
                next_state = state.transition(direction)
                for y, x in list(state.empty_positions):
                    for val, chance  in [(2, .9), (4, .1)]:
                        succ = State(state=next_state)
                        succ.grid[y][x] = val
                        v, _ = self.find_best(succ, MAX_DEPTH - 1) 
                        v *= chance
                        if v > max_v:
                            max_v = v
                            best_dir = direction
        return max_v, best_dir

    def get_move(self, state):
        start_time = time.time()
        self.states_considered = 0
        val, direction = self.find_best(state, MAX_DEPTH=self.max_depth)
        print(f"Moving {direction} with expected value {val}")
        print(f"Considered {agent.states_considered} states in {time.time() - start_time} seconds")
        return direction


set_time = 0
class MonteCarloAgent(Agent):

    def __init__(self, max_depth=3, repetitions=10):
        super().__init__()
        self.mc_count = repetitions
        self.max_depth = max_depth

    def _monte_carlo_iterative(self, state, depth=3):
        root = Node(None,None,-1)
        stack = deque([Node(state, parent=root, depth=0)])
        while len(stack) > 0:
            cur_node = stack.pop()
            parent = cur_node.parent
            if cur_node.depth == depth:
                parent.best_child = max(parent.best_child, self.value_state(cur_node.state))
            else:
                for direction in self.directions:
                    if cur_node.state.can_move(direction):
                        next_state = cur_node.state.transition(direction)
                        if not next_state.is_dead():
                            next_state.add_random_tile()
                            stack.append(Node(next_state, cur_node, cur_node.depth + 1))
                        else:
                            v = self.value_state(next_state)
                            cur_node.best_child = max(cur_node.best_child, v)
                if cur_node.best_child > parent.best_child:
                    parent.best_child = cur_node.best_child
        return root.best_child 

    def _monte_carlo_helper(self, state, depth=5):
        if state.is_dead() or depth == 0:
            return self.value_state(state)
        max_v = -1
        for direction in self.directions:
            if state.can_move(direction):
                next_state = state.transition(direction)
                next_state.add_random_tile()
                v = self._monte_carlo_helper(next_state, depth - 1)
                if v > max_v:
                    max_v = v
        return max_v

    def monte_carlo(self, orig_state):
        global set_time
        total = 0
        state = State(state=orig_state)
        for i in range(self.mc_count):
            v = self._monte_carlo_helper(state, self.max_depth)
            # print("value;", v)
            # print(state)
            total += v
            st_set = time.time()
            state.set_from(orig_state)
            set_time += time.time() - st_set
        return total/self.mc_count

    def find_best(self, state):
        self.states_considered = 0
        value = self.value_state(state)
        if value == -float("inf"):
            return value, None
        max_v = -1
        best_dir = "LEFT"
        dir_vals = {}
        for direction in self.directions:
            if state.can_move(direction):
                next_state = state.transition(direction)
                v = self.monte_carlo(next_state)
                dir_vals[direction] = v
                if v > max_v:
                    max_v = v
                    best_dir = direction
        print(dir_vals)
        return max_v, best_dir

    def get_move(self, state):
        start_time = time.time()
        val, direction = self.find_best(state)
        print(f"Considered {self.states_considered} states in {time.time() - start_time} seconds")
        return direction

dead_time = 0
move_time = 0
trans_time = 0
rand_time = 0
choice_time = 0
class MonteCarloLight(MonteCarloAgent):
    
    def _monte_carlo_helper(self, state, depth=5):
        global dead_time, move_time, trans_time, rand_time, choice_time
        st_dead = time.time()
        dead = state.is_dead()
        dead_time += time.time() - st_dead
        while state.is_able_to_move():
            st_move = time.time()
            valid_directions = list(state.valid_moves)
            move_time += time.time() - st_move

            st_choice = time.time()
            direction = random.choice(valid_directions)
            choice_time += time.time() - st_choice

            st_trans = time.time()
            state.transition_in_place(direction)
            trans_time += time.time() - st_trans
            
            if state.is_dead():
                break

            st_rand = time.time()
            state.add_random_tile()
            rand_time += time.time() - st_rand

            # st_dead = time.time()
            # dead = state.is_dead()
            # dead_time += time.time() - st_dead

        return state.score


class RandomAgent(Agent):

    def get_move(self, state):
        valid_directions = [d for d in self.directions if state.can_move(d)]
        if len(valid_directions) > 0:
            return random.choice(valid_directions)
        else:
            return None


if __name__ == "__main__":
    size = 4
    grid = [[0 for _ in range(size)] for _ in range(size)]

    state = State(grid)
    state.add_random_tile()
    state.add_random_tile()
    # agent = MonteCarloAgent(max_depth=5, repetitions=10)
    agent = MonteCarloLight(repetitions=100)
    # agent = Agent(max_depth=5)
    # agent = RandomAgent()
    while True:
        print(state)
       #  direction = input("\nMove> ").strip().upper()
       #  if direction == "AUTO" or direction == "A":
        dead_time = 0
        move_time = 0
        trans_time = 0
        rand_time = 0
        set_time = 0
        choice_time = 0
        reset_times()
        direction = agent.get_move(state)
        state = state.transition(direction)
        print(f"is_dead(): {dead_time}\ncan_move(): {move_time}\ntransition(): {trans_time}\nadd_random_tile(): {rand_time}\nset_from(): {set_time}\nRandom choice: {choice_time}")
        print_times()
        print(f"Actual merges: {state.merges}")
        if state.is_dead():
            print("\n-----GAME OVER-----\n")
            break
        state.add_random_tile()
        
