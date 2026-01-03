import sys
import os

# AIMA dosyalarına erişebilmek için bir üst dizine yol açıyoruz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from search import Problem

class HauntedProblem(Problem):
    def __init__(self, initial, goal, maze, items_pos, wrong_items):
        super().__init__(initial, goal)
        self.maze = maze
        self.items_pos = items_pos # {'S': (r,c), 'E': (r,c), 'R': (r,c)}
        self.wrong_items = wrong_items # [(r,c), ...]

    def actions(self, state):
        # state: ((r, c), tuple_of_collected_items)
        (r, c), collected = state
        moves = []
        # Yukarı, Aşağı, Sol, Sağ
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            # Duvar değilse ve Yanlış eşya (X) değilse oraya gidebilir
            if self.maze[nr][nc] == "." and (nr, nc) not in self.wrong_items:
                moves.append((nr, nc))
        return moves

    def result(self, state, action):
        (r, c), collected = state
        next_pos = action
        new_collected = list(collected)
        
        # Eğer gittiği yerde bir eşya varsa ve henüz toplanmadıysa çantaya at
        for item, pos in self.items_pos.items():
            if next_pos == pos and item not in new_collected:
                new_collected.append(item)
        
        return (next_pos, tuple(sorted(new_collected)))

    def goal_test(self, state):
        (r, c), collected = state
        # Hedef: 3 eşya da toplandı mı VE çıkış kapısında mıyız?
        return len(collected) == 3 and (r, c) == self.goal

    def h(self, node):
        # A* için Sezgisel Fonksiyon (Heuristic)
        # Manhattan mesafesi: Mevcut konumdan hedefe olan uzaklık
        (r, c), collected = node.state
        gr, gc = self.goal
        return abs(r - gr) + abs(c - gc)
