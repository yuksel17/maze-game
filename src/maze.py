import random

class Maze:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[0 for _ in range(width)] for _ in range(height)]
        self.start_pos = (1, 1)
        self.exit_pos = (width - 2, height - 2)
        self.wrong_items = []
        self.items = {}
        self.generate_maze()

    def generate_maze(self):
        for x in range(self.width):
            self.grid[0][x] = self.grid[self.height-1][x] = 1
        for y in range(self.height):
            self.grid[y][0] = self.grid[y][self.width-1] = 1
        
        for _ in range((self.width * self.height) // 9):
            rx, ry = random.randint(1, self.width-2), random.randint(1, self.height-2)
            if (rx, ry) != self.start_pos and (rx, ry) != self.exit_pos:
                self.grid[ry][rx] = 1
