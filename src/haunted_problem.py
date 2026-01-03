class HauntedProblem:
    def __init__(self, initial, goal, maze):
        self.initial = initial # ((x, y), (envanter))
        self.goal = goal
        self.maze = maze

    def actions(self, state):
        (x, y), coll = state
        if (x, y) == self.goal and len(coll) == 3: return []
        
        res = []
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.maze.width and 0 <= ny < self.maze.height:
                # 1. Duvar değilse ve 2. Zehirli eşya değilse geçebilir (Akıllı Kaçınma)
                if self.maze.grid[ny][nx] == 0 and (nx, ny) not in self.maze.wrong_items:
                    res.append((nx, ny))
        return res

    def result(self, state, action):
        (x, y), coll = state
        new_coll = list(coll)
        if action in self.maze.items:
            it = self.maze.items[action]
            if it not in new_coll: new_coll.append(it)
        return (action, tuple(sorted(new_coll)))

    def goal_test(self, state):
        return state[0] == self.goal and len(state[1]) == 3

    def h(self, node):
        (x, y), coll = node.state
        dist = abs(x - self.goal[0]) + abs(abs(y - self.goal[1]))
        return dist + (3 - len(coll)) * 10
