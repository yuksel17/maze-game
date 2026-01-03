import random

class HauntedEnv:
    def __init__(self, maze):
        self.maze = maze
        self.rows = len(maze)
        self.cols = len(maze[0])
        self.items = {"S": None, "E": None, "R": None} # Snake, Emerald, Royal
        self.wrong_items = [] # Yanlış eşyalar (X)
        self.exit_pos = (self.rows - 2, self.cols - 2) # Çıkış genellikle sağ alt köşedir
        self.place_items()

    def is_free(self, r, c):
        return self.maze[r][c] == "."

    def place_items(self):
        # Boş yolları bul
        empty_cells = [(r, c) for r in range(self.rows) for c in range(self.cols) if self.is_free(r, c)]
        
        # Rastgele 3 doğru eşya yerleştir
        chosen = random.sample(empty_cells, 8) # 3 doğru + 5 yanlış için 8 yer seç
        
        self.items["S"] = chosen[0]
        self.items["E"] = chosen[1]
        self.items["R"] = chosen[2]
        
        # Kalan 5 tanesi yanlış eşya (X)
        self.wrong_items = chosen[3:]

    def get_item_at(self, r, c):
        for key, pos in self.items.items():
            if pos == (r, c):
                return key
        return None
