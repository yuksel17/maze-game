import pygame
from demo import setup_scenario
from algorithms import bfs_items, dfs_items, astar_items, greedy_items

CELL = 40
MARGIN = 2
TOP = 80
WHITE = (255,255,255)
BLACK = (0,0,0)
GREEN = (0,200,0)
RED = (200,0,0)
BLUE = (0,0,200)

def run_alg(name, grid, start, goal, move_limit):
    if name == "BFS":
        return bfs_items(grid, start, goal, move_limit)
    if name == "DFS":
        return dfs_items(grid, start, goal, move_limit)
    if name == "A*":
        return astar_items(grid, start, goal, move_limit)
    if name == "Greedy":
        return greedy_items(grid, start, goal, move_limit)

def draw(screen, grid, start, goal, path):
    screen.fill(WHITE)
    for y,row in enumerate(grid):
        for x,val in enumerate(row):
            color = BLACK if val==1 else WHITE
            pygame.draw.rect(
                screen, color,
                (x*CELL, y*CELL+TOP, CELL-MARGIN, CELL-MARGIN)
            )
    for (x,y) in path:
        pygame.draw.rect(
            screen, BLUE,
            (x*CELL, y*CELL+TOP, CELL-MARGIN, CELL-MARGIN)
        )
    pygame.draw.rect(screen, GREEN, (start[0]*CELL, start[1]*CELL+TOP, CELL, CELL))
    pygame.draw.rect(screen, RED, (goal[0]*CELL, goal[1]*CELL+TOP, CELL, CELL))

def main():
    pygame.init()
    grid, start, goal, _, _, move_limit = setup_scenario()
    alg = "A*"

    found, steps, expanded, path = run_alg(
        alg, grid, start, goal, move_limit
    )

    h, w = len(grid), len(grid[0])
    screen = pygame.display.set_mode((w*CELL, h*CELL+TOP))
    pygame.display.set_caption("Haunted Maze - Search Algorithms")

    font = pygame.font.SysFont(None, 28)

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

        draw(screen, grid, start, goal, path)
        txt = font.render(
            f"{alg} | found={found} steps={steps} expanded={expanded}",
            True, (0,0,0)
        )
        screen.blit(txt, (10,20))
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
