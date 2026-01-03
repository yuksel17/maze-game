import random

def gen_maze_random(width=15, height=11, wall_prob=0.25, seed=None):
    if seed is not None:
        random.seed(seed)
    return [[0 if random.random() > wall_prob else 1
             for _ in range(width)] for _ in range(height)]

def random_free_cell(grid, forbidden=set()):
    h, w = len(grid), len(grid[0])
    while True:
        x, y = random.randrange(w), random.randrange(h)
        if grid[y][x] == 0 and (x, y) not in forbidden:
            return (x, y)

def convert_grid_to_maze(grid, exit_pos):
    maze = []
    for r in range(len(grid)):
        row = []
        for c in range(len(grid[0])):
            if (c, r) == exit_pos:
                row.append("E")
            elif grid[r][c] == 1:
                row.append("#")
            else:
                row.append(".")
        maze.append(row)
    return maze

def setup_scenario(seed=None):
    grid = gen_maze_random(seed=seed)

    start_xy = random_free_cell(grid)
    exit_xy = random_free_cell(grid, {start_xy})

    maze = convert_grid_to_maze(grid, exit_xy)

    # (row, col) formatına çeviriyoruz
    start = (start_xy[1], start_xy[0])
    exit_pos = (exit_xy[1], exit_xy[0])

    return maze, start, exit_pos

def print_maze_with_path(maze, path, start, exit_pos):
    maze_copy = [row[:] for row in maze]

    for r, c in path:
        if (r, c) != start and (r, c) != exit_pos:
            maze_copy[r][c] = "*"

    sr, sc = start
    er, ec = exit_pos
    maze_copy[sr][sc] = "S"
    maze_copy[er][ec] = "E"

    for row in maze_copy:
        print(" ".join(row))
