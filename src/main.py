import pygame
import sys
import random
from maze import Maze
from haunted_problem import HauntedProblem
from search_utils import bfs, dfs, greedy_search, astar_search

# Renkler
COLOR_BG, COLOR_WALL = (245, 247, 250), (148, 163, 184)
COLOR_PANEL, COLOR_WITCH = (255, 255, 255), (147, 51, 234)
COLOR_EXIT, COLOR_TRAP = (251, 191, 36), (220, 38, 38)
COLOR_TEXT = (30, 41, 59)
POTION_COLORS = {"Snake Elixir": (59, 130, 246), "Emerald": (34, 197, 94), "Royal Elixir": (239, 68, 68)}

CELL_SIZE, COLS, ROWS, PANEL_H = 40, 15, 15, 110
WIDTH, HEIGHT = COLS * CELL_SIZE, ROWS * CELL_SIZE + PANEL_H

def init_game():
    m = Maze(COLS, ROWS)
    m.wrong_items = []
    for _ in range(5):
        rx, ry = random.randint(1, COLS-2), random.randint(1, ROWS-2)
        if m.grid[ry][rx] == 0 and (rx, ry) != m.start_pos:
            m.wrong_items.append((rx, ry))
    m.items = {}
    names = ["Snake Elixir", "Emerald", "Royal Elixir"]
    for n in names:
        while True:
            rx, ry = random.randint(1, COLS-2), random.randint(1, ROWS-2)
            if m.grid[ry][rx] == 0 and (rx, ry) not in m.items and (rx, ry) not in m.wrong_items:
                m.items[(rx, ry)] = n; break
    return m, list(m.start_pos), [], [], 0, "Manuel", False, 100

def draw_potion(screen, x, y, color):
    # Şişe Çizimi (Mock-up'taki gibi)
    pygame.draw.ellipse(screen, color, (x-10, y, 20, 18))
    pygame.draw.rect(screen, color, (x-4, y-6, 8, 8))
    pygame.draw.rect(screen, (120, 60, 30), (x-5, y-9, 10, 4))
    pygame.draw.circle(screen, (255, 255, 255), (x-4, y+4), 2)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Cadth Ajani: The Quest")
    font = pygame.font.SysFont("Arial", 14, bold=True)
    clock = pygame.time.Clock()
    maze, pos, coll, path, used, alg, over, limit = init_game()

    while True:
        screen.fill(COLOR_BG)
        pygame.draw.rect(screen, COLOR_PANEL, (0, 0, WIDTH, PANEL_H))
        screen.blit(font.render(f"Mod: {alg} | Hamle: {used}/{limit}", True, COLOR_TEXT), (20, 20))
        screen.blit(font.render(f"Iksirler: {len(coll)}/3", True, (34, 197, 94)), (20, 45))

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                # R TUŞU DÜZELTİLDİ: Artık her zaman çalışır
                if ev.key == pygame.K_r:
                    maze, pos, coll, path, used, alg, over, limit = init_game()
                
                if not over:
                    if ev.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                        p = HauntedProblem((tuple(pos), tuple(coll)), maze.exit_pos, maze)
                        node = None
                        if ev.key == pygame.K_1: alg, node = "BFS", bfs(p)
                        elif ev.key == pygame.K_2: alg, node = "DFS", dfs(p)
                        elif ev.key == pygame.K_3: alg, node = "A*", astar_search(p)
                        elif ev.key == pygame.K_4: alg, node = "Greedy", greedy_search(p)
                        if node: path = node.path()[1:]; p_idx = 0
                    
                    old_p, mv = list(pos), False
                    if ev.key == pygame.K_UP: pos[1]-=1; mv=True
                    elif ev.key == pygame.K_DOWN: pos[1]+=1; mv=True
                    elif ev.key == pygame.K_LEFT: pos[0]-=1; mv=True
                    elif ev.key == pygame.K_RIGHT: pos[0]+=1; mv=True
                    if mv:
                        if 0<=pos[0]<COLS and 0<=pos[1]<ROWS and maze.grid[pos[1]][pos[0]]==0:
                            used += 1; pt = tuple(pos)
                            if pt in maze.items and maze.items[pt] not in coll: coll.append(maze.items[pt])
                            if pt in maze.wrong_items: over = True
                            if pt == maze.exit_pos and len(coll) == 3: over = True
                        else: pos = old_p

        if path and not over:
            pos = list(path[p_idx].state[0]); coll = list(path[p_idx].state[1])
            p_idx += 1; used += 1; pygame.time.delay(100)
            if p_idx >= len(path): path = []
            if tuple(pos) == maze.exit_pos and len(coll) == 3: over = True

        for y in range(ROWS):
            for x in range(COLS):
                if maze.grid[y][x] == 1:
                    pygame.draw.rect(screen, COLOR_WALL, (x*CELL_SIZE, y*CELL_SIZE + PANEL_H, CELL_SIZE-1, CELL_SIZE-1), 0, 4)
        
        for pt, name in maze.items.items():
            if name not in coll:
                draw_potion(screen, pt[0]*CELL_SIZE+20, pt[1]*CELL_SIZE+20+PANEL_H, POTION_COLORS[name])

        for tp in maze.wrong_items: pygame.draw.circle(screen, COLOR_TRAP, (tp[0]*CELL_SIZE+20, tp[1]*CELL_SIZE+20+PANEL_H), 8, 2)
        pygame.draw.rect(screen, COLOR_EXIT, (maze.exit_pos[0]*CELL_SIZE+5, maze.exit_pos[1]*CELL_SIZE+5+PANEL_H, 30, 30), 0, 8)
        pygame.draw.circle(screen, COLOR_WITCH, (pos[0]*CELL_SIZE+20, pos[1]*CELL_SIZE+20+PANEL_H), 15)
        
        if over:
            msg = "ZAFER!" if len(coll)==3 and tuple(pos)==maze.exit_pos else "BASARISIZ!"
            screen.blit(font.render(msg, True, COLOR_TRAP), (WIDTH//2 - 40, 85))

        pygame.display.flip(); clock.tick(60)
if __name__ == "__main__": main()
