class HauntedProblem:
    def __init__(self, initial, goal, maze):
        self.initial = initial  # ((x, y), (toplanan_esyalar))
        self.goal = goal
        self.maze = maze

    def actions(self, state):
        (x, y), collected = state
        if len(collected) == 3 and (x, y) == self.goal:
            return []
        
        moves = []
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.maze.width and 0 <= ny < self.maze.height:
                if self.maze.grid[ny][nx] == 0 and (nx, ny) not in self.maze.traps:
                    moves.append((nx, ny))
        return moves

    def result(self, state, action):
        (x, y), collected = state
        new_coll = list(collected)
        if action in self.maze.items:
            item = self.maze.items[action]
            if item not in new_coll:
                new_coll.append(item)
        return (action, tuple(sorted(new_coll)))

    def goal_test(self, state):
        (pos, collected) = state
        return len(collected) == 3 and pos == self.goal

    def h(self, node):
        """Manhattan mesafesi ile en kısa rotayı garanti eder."""
        (x, y), collected = node.state
        uncollected = [p for p, name in self.maze.items.items() if name not in collected]
        
        if uncollected:
            # Tüm kalan iksirlerin mesafesini hesaba kat (Yolu uzatmasını engeller)
            return min(abs(x - p[0]) + abs(y - p[1]) for p in uncollected) + (3 - len(collected)) * 10
        else:
            # İksirler bittiyse doğrudan kapıya odaklan
            return abs(x - self.goal[0]) + abs(y - self.goal[1])
