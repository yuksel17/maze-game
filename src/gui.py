import tkinter as tk

class HauntedGUI:
    def __init__(self, root, maze, cell_size=30):
        self.root = root
        self.maze = maze
        self.cell_size = cell_size
        self.rows = len(maze)
        self.cols = len(maze[0])
        
        self.canvas = tk.Canvas(root, width=self.cols*self.cell_size, height=self.rows*self.cell_size, bg="white")
        self.canvas.pack()
        self.draw_maze()

    def draw_maze(self):
        for r in range(self.rows):
            for c in range(self.cols):
                color = "#2c3e50" if self.maze[r][c] == "#" else "#ecf0f1"
                self.canvas.create_rectangle(
                    c*self.cell_size, r*self.cell_size,
                    (c+1)*self.cell_size, (r+1)*self.cell_size,
                    fill=color, outline="#bdc3c7"
                )

    def draw_agent(self, r, c):
        padding = self.cell_size // 5
        self.canvas.delete("agent")
        return self.canvas.create_oval(
            c*self.cell_size + padding, r*self.cell_size + padding,
            (c+1)*self.cell_size - padding, (r+1)*self.cell_size - padding,
            fill="#3498db", tags="agent"
        )

    def draw_items(self, env):
        # Doğru eşyaları (S, E, R) çiz
        for item_type, pos in env.items.items():
            r, c = pos
            self.canvas.create_text(
                c*self.cell_size + self.cell_size//2, 
                r*self.cell_size + self.cell_size//2, 
                text=item_type, fill="#f1c40f", font=("Arial", 14, "bold")
            )
        
        # Yanlış eşyaları (X) çiz
        for pos in env.wrong_items:
            r, c = pos
            self.canvas.create_text(
                c*self.cell_size + self.cell_size//2, 
                r*self.cell_size + self.cell_size//2, 
                text="X", fill="#e74c3c", font=("Arial", 14, "bold")
            )
            
        # Çıkış kapısını çiz
        er, ec = env.exit_pos
        self.canvas.create_rectangle(
            ec*self.cell_size + 2, er*self.cell_size + 2,
            (ec+1)*self.cell_size - 2, (er+1)*self.cell_size - 2,
            fill="#9b59b6", outline="white"
        )