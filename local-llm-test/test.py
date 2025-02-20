import tkinter as tk
from random import randint

class Game:
    def __init__(self, window):
        self.window = window
        self.window.title('Snake Game')
        
        # Screen dimensions and setup
        self.canvas_width = 600
        self.canvas_height = 400
        self.scale = 20
        
        # Create canvas for the game
        self.canvas = tk.Canvas(window, width=self.canvas_width,
                                  height=self.canvas_height)
        self.canvas.pack()
        
        # Key bindings
        window.bind('<Left>', lambda e: self.change_direction('left'))
        window.bind('<Right>', lambda e: self.change_direction('right'))
        window.bind('<Up>', lambda e: self.change_direction('up'))
        window.bind('<Down>', lambda e: self.change_direction('down'))

        # Game variables
        self.snake = [(10, 5), (9, 5), (8, 5)]
        self.direction = 'right'
        
    def create_snake(self):
        for segment in self.snake:
            x1 = segment[0] * self.scale
            y1 = segment[1] * self.scale
            x2 = x1 + self.scale
            y2 = y1 + self.scale
            
            # Draw each snake body part as a rectangle on the canvas
            rect = tk.Rectangle(self.canvas, x1, y1, x2, y2,
                               fill='green', outline='black')
            
    def create_food(self):
        while True:
            food_pos = (randint(0, self.canvas_width // self.scale - 1),
                       randint(0, self.canvas_height // self.scale - 1))
            if food_pos not in [segment[0] for segment in self.snake]:
                break
        
        # Draw the food as a rectangle
        x1 = food_pos[0] * self.scale
        y1 = food_pos[1] * self.scale
        x2 = x1 + self.scale
        y2 = y1 + self.scale

        rect = tk.Rectangle(self.canvas, x1, y1, x2, y2,
                           fill='red', outline='black')
        
    def update_snake(self):
        head_x = (self.snake[0][0] + 1 if self.direction == 'right' else
                  self.snake[0][0] - 1 if self.direction == 'left' else 
                  self.snake[0][0])
        head_y = (self.snake[0][1] + 1 if self.direction == 'down' else
                  self.snake[0][1] - 1 if self.direction == 'up' else 
                  self.snake[0][1])

        new_head = (head_x, head_y)
        
        # Insert new segment at the front of snake
        new_snake = [new_head]
        for body in self.snake:
            if body == new_head and len(self.snake) > 2: 
                break
            new_snake.append(body)
        
        # Clear old canvas and redraw everything
        self.canvas.delete(tk.ALL)
        create_snake(new_snake)

    def change_direction(self, direction):
        directions = {'left': (-1, 0), 'right': (1, 0),
                      'up': (0, -1), 'down': (0, 1)}
        
        # Allow turning around if not heading the opposite way
        if self.direction != ('right' and direction == 'left') or \
           self.direction != ('left' and direction == 'right') or \
           self.direction != ('up' and direction == 'down') or \
           self.direction != ('down' and direction == 'up'):
            self.direction = directions[direction]

def game_over():
    tk.messagebox.showinfo("Game Over", "You lost!")
    root.quit()

root = tk.Tk()
game = Game(root)
root.mainloop()