#region Imports


# Standard Library
import random
from collections import deque


# Standard Library - GUI
from tkinter import ttk, Tk, Toplevel, messagebox, Frame, LabelFrame, Canvas, Label, TclError


#endregion
################################################################################################################################################
#region Globals


# Constants
GRID_WIDTH = 10
GRID_HEIGHT = 20
CELL_SIZE = 20
INITIAL_SPEED = 500
INITIAL_MOVE_DELAY = 100
MOVE_REPEAT_RATE = 50
PADX = 10
PADY = 10


# Tromino shapes
SHAPES = [
    # I
    [[1],
     [1],
     [1],
     [1]],
    # J
    [[0, 1],
     [0, 1],
     [1, 1]],
    # L
    [[1, 0],
     [1, 0],
     [1, 1]],
    # O
    [[1, 1],
     [1, 1]],
    # S
    [[0, 1, 1],
     [1, 1, 0]],
    # T
    [[0, 1, 0],
     [1, 1, 1]],
    # Z
    [[1, 1, 0],
     [0, 1, 1]]
]


# Tromino colors
COLORS = [
    # I
    "#00bde7",
    # J
    "#6d47e8",
    # L
    "#e26a00",
    # O
    "#e4b507",
    # S
    "#94e606",
    # T
    "#9a2daa",
    # Z
    "#ec0054"
]


#endregion
################################################################################################################################################
#region CLS: Tromino


class Tromino:
    def __init__(self, canvas, shape=None, color=None):
        self.canvas = canvas
        self.shape = shape if shape else random.choice(SHAPES)
        self.color = color if color else COLORS[SHAPES.index(self.shape)]
        self.x_pos = GRID_WIDTH // 2 - len(self.shape[0]) // 2
        self.y_pos = 0
        self.rotation = 0


    def rotate_clockwise(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]


#endregion
################################################################################################################################################
#region CLS: PyTrominosGame


class PyTrominosGame:
    def __init__(self, root: 'Tk', icon_path=None):
        self.root = Toplevel(root)
        self.root.title("PyTrominos")
        self.root.resizable(False, False)
        self.root.focus_set()
        self.icon_path = icon_path
        self.movement_keys = {}


#endregion
################################################################################################################################################
#region Interface and setup


    def run(self):
        self._set_icon()
        self.create_interface()
        self._center_window()
        self.setup_game_binds()
        self.start_game()
        #self.root.bind("<Configure>", lambda event: print(f"\rWindow size (W,H): {event.width},{event.height}    ", end='') if event.widget == self.root else None, add="+")


    def create_interface(self):
        mini_canvas_size = 6 * CELL_SIZE
        game_frame = Frame(self.root, relief="groove", borderwidth=5)
        game_frame.pack(side="left", anchor="nw", padx=PADX, pady=(PADY+6))
        self.game_canvas = Canvas(game_frame, width=GRID_WIDTH*CELL_SIZE + 1, height=GRID_HEIGHT*CELL_SIZE + 1, highlightthickness=0)
        self.game_canvas.pack(side="left", padx=PADX, pady=PADY)
        sidebar = Frame(self.root)
        sidebar.pack(side="left", fill="y")
        next_shape_frame = LabelFrame(sidebar, text="  Next  ", relief="groove", borderwidth=5)
        next_shape_frame.pack(padx=PADX, pady=PADY)
        self.next_shape_canvas = Canvas(next_shape_frame, width=mini_canvas_size, height=mini_canvas_size)
        self.next_shape_canvas.pack()
        hold_shape_frame = LabelFrame(sidebar, text="  Hold - C  ", relief="groove", borderwidth=5)
        hold_shape_frame.pack(padx=PADX, pady=PADY)
        self.hold_shape_canvas = Canvas(hold_shape_frame, width=mini_canvas_size, height=mini_canvas_size)
        self.hold_shape_canvas.pack()
        frame1 = Frame(sidebar)
        frame1.pack(padx=PADX, pady=(PADY,5), fill="x")
        self.level_label = Label(frame1, text=f"Level: 1")
        self.level_label.pack(side="left", anchor="w")
        help_button = ttk.Button(frame1, text="?", width=1, takefocus=False, command=self.show_help)
        help_button.pack(side="right", padx=1)
        frame2 = Frame(sidebar)
        frame2.pack(padx=PADX, pady=PADY, fill="x")
        self.score_label = Label(frame2, text=f"Score: 0")
        self.score_label.pack(side="left", anchor="w")
        button_frame = Frame(sidebar)
        button_frame.pack(padx=(0,PADX), pady=(5,PADY))
        pause_button = ttk.Button(button_frame, text="Pause", takefocus=False, command=self.toggle_pause)
        pause_button.pack(side="left", padx=1)
        restart_button = ttk.Button(button_frame, text="Restart", takefocus=False, command=self.restart_game)
        restart_button.pack(side="left", padx=1)
        self.board = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]


    def _center_window(self):
        self.root.update_idletasks()
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.root.geometry(f"+{x}+{y}")


    def _set_icon(self):
        if self.icon_path:
            try:
                self.root.iconbitmap(self.icon_path)
            except TclError:
                pass


    def setup_game_binds(self):
        self.root.bind("<KeyPress>", self.key_press)
        self.root.bind("<KeyRelease>", self.key_release)
        self.root.bind("<space>", self.instant_drop)
        self.root.bind("c", self.hold_shape)


    def start_game(self):
        self.current_shape = Tromino(self.game_canvas)
        self.shape_bag = []
        self.last_shapes = []
        self.next_shape = self.get_next_shape()
        self.spawn_new_shape()
        self.held_shape = None
        self.hold_used = False
        self.game_over = False
        self.paused = False
        self.after_id = None
        self.lock_timer = None
        self.down_key_pressed = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.speed = INITIAL_SPEED
        self.after_id = self.root.after(self.speed, self.drop_shape)
        self.draw_next_shape()
        self.draw_held_shape()
        self.gameloop()
        self.ghost_shape = None


#endregion
################################################################################################################################################
#region Draw Game


    def draw_block_on_canvas(self, canvas, x, y, color):
        canvas.create_rectangle(x * CELL_SIZE, y * CELL_SIZE, (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE, fill=color, outline="black")


    def draw_block(self, x, y, color, ghost=False):
        if ghost:
            self.game_canvas.create_rectangle(
                x * CELL_SIZE, y * CELL_SIZE, (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE,
                fill=color, outline='', stipple='gray50')
        else:
            self.game_canvas.create_rectangle(
                x * CELL_SIZE, y * CELL_SIZE, (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE,
                fill=color, outline='black')


    def draw_board(self):
        self.game_canvas.delete("all")
        self.draw_grid_lines()
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                color = self.board[y][x]
                if color:
                    self.draw_block(x, y, color)
        self.calculate_ghost_position()
        # Ghost
        for i, row in enumerate(self.ghost_shape.shape):
            for j, val in enumerate(row):
                if val:
                    x = self.ghost_shape.x_pos + j
                    y = self.ghost_shape.y_pos + i
                    self.draw_block(x, y, self.ghost_shape.color, ghost=True)
        # Current
        for i, row in enumerate(self.current_shape.shape):
            for j, val in enumerate(row):
                if val:
                    self.draw_block(self.current_shape.x_pos + j, self.current_shape.y_pos + i, self.current_shape.color)


    def draw_grid_lines(self):
        for i in range(GRID_WIDTH + 1):
            x = i * CELL_SIZE
            self.game_canvas.create_line(x, 0, x, GRID_HEIGHT * CELL_SIZE, fill="lightgray")
        for i in range(GRID_HEIGHT + 1):
            y = i * CELL_SIZE
            self.game_canvas.create_line(0, y, GRID_WIDTH * CELL_SIZE, y, fill="lightgray")


    def draw_next_shape(self):
        self.next_shape_canvas.delete("all")
        shape = self.next_shape.shape
        color = self.next_shape.color
        shape_height = len(shape)
        shape_width = len(shape[0])
        x_off = (6 - shape_width) / 2
        y_off = (6 - shape_height) / 2
        for i, row in enumerate(shape):
            for j, val in enumerate(row):
                if val:
                    x = x_off + j
                    y = y_off + i
                    self.draw_block_on_canvas(self.next_shape_canvas, x, y, color)


    def draw_held_shape(self):
        self.hold_shape_canvas.delete("all")
        if self.held_shape:
            shape = self.held_shape.shape
            color = self.held_shape.color
            shape_height = len(shape)
            shape_width = len(shape[0])
            x_off = (6 - shape_width) / 2
            y_off = (6 - shape_height) / 2
            for i, row in enumerate(shape):
                for j, val in enumerate(row):
                    if val:
                        x = x_off + j
                        y = y_off + i
                        self.draw_block_on_canvas(self.hold_shape_canvas, x, y, color)


    def draw_text_on_canvas(self, text, x=None, y=None, event=None):
        font = ("Arial", 24)
        if x is None:
            x = GRID_WIDTH * CELL_SIZE / 2
        if y is None:
            y = GRID_HEIGHT * CELL_SIZE / 2
        for x_off, y_off in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            self.game_canvas.create_text(x + x_off, y + y_off, text=text, fill="black", font=font)
        self.game_canvas.create_text(x, y, text=text, fill="white", font=font)


#endregion
################################################################################################################################################
#region Update Game


    def gameloop(self):
        if not self.paused:
            self.draw_board()
            if not self.game_over:
                self.root.after(16, self.gameloop)
            else:
                self.draw_text_on_canvas(text="Game Over")


    def update_level(self):
        speed_step = 50
        min_speed = 20
        self.level = self.score // 100 + 1
        self.speed = max(min_speed, INITIAL_SPEED - (self.level - 1) * speed_step)
        self.level_label.config(text=f"Level: {self.level}")
        self.update_score()


    def update_score(self):
        self.score_label.config(text=f"Score: {self.score}")


#endregion
################################################################################################################################################
#region Move shape


    def move_shape(self, dx, dy):
        self.current_shape.x_pos += dx
        self.current_shape.y_pos += dy
        if self.check_collision():
            self.current_shape.x_pos -= dx
            self.current_shape.y_pos -= dy
            return False
        else:
            if self.lock_timer is not None:
                self.root.after_cancel(self.lock_timer)
                self.lock_timer = None
            self.calculate_ghost_position()
            return True


    def drop_shape(self):
        if self.game_over:
            return
        if not self.paused:
            if not self.move_shape(0, 1):
                if self.lock_timer is None:
                    self.lock_timer = self.root.after(500, self.lock_shape_and_spawn)
            else:
                if self.lock_timer is not None:
                    self.root.after_cancel(self.lock_timer)
                    self.lock_timer = None
            if not self.game_over:
                self.after_id = self.root.after(self.speed, self.drop_shape)


    def instant_drop(self, event=None):
        if not self.paused and not self.game_over:
            while self.move_shape(0, 1):
                self.draw_board()
                self.root.update_idletasks()
                self.root.after(5)
            self.lock_shape_and_spawn()
            if not self.game_over:
                if self.after_id:
                    self.root.after_cancel(self.after_id)
                self.after_id = self.root.after(self.speed, self.drop_shape)


    def rotate_shape(self):
        old_shape = self.current_shape.shape
        old_x = self.current_shape.x_pos
        old_y = self.current_shape.y_pos
        self.current_shape.rotate_clockwise()
        if self.check_collision():
            horizontal_kicks = [kick for kick in [(-1, 0), (1, 0)] if kick[1] == 0]
            shape_bottom = self.current_shape.y_pos + len(self.current_shape.shape)
            near_bottom = shape_bottom >= GRID_HEIGHT - 1
            kicks_to_try = horizontal_kicks.copy()
            if not near_bottom:
                kicks_to_try.append((0, -1))
            for dx, dy in kicks_to_try:
                self.current_shape.x_pos += dx
                self.current_shape.y_pos += dy
                if not self.check_collision():
                    return
                self.current_shape.x_pos = old_x
                self.current_shape.y_pos = old_y
            self.current_shape.shape = old_shape
        if not self.check_collision():
            if self.lock_timer is not None:
                self.root.after_cancel(self.lock_timer)
                self.lock_timer = None
        self.calculate_ghost_position()


    def collapse_floating_blocks(self):
        visited = [[False for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        queue = deque()
        for x in range(GRID_WIDTH):
            if self.board[GRID_HEIGHT-1][x]:
                queue.append((GRID_HEIGHT-1, x))
                visited[GRID_HEIGHT-1][x] = True
        while queue:
            y, x = queue.popleft()
            for dy, dx in [(-1,0), (1,0), (0,-1), (0,1)]:
                ny, nx = y + dy, x + dx
                if 0 <= ny < GRID_HEIGHT and 0 <= nx < GRID_WIDTH:
                    if self.board[ny][nx] and not visited[ny][nx]:
                        visited[ny][nx] = True
                        queue.append((ny, nx))
        floating = []
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.board[y][x] and not visited[y][x]:
                    floating.append((y, x))
        for y, x in sorted(floating, reverse=True):
            self.board[y][x] = None
            new_y = y
            while new_y + 1 < GRID_HEIGHT and not self.board[new_y + 1][x]:
                new_y += 1
            self.board[new_y][x] = COLORS.index(self.board[y][x]) if self.board[y][x] else None
        self.update_score()


#endregion
################################################################################################################################################
#region Lock / Spawn shape


    def lock_shape_and_spawn(self):
        self.lock_shape()
        self.clear_lines()
        self.spawn_new_shape()
        if self.check_collision():
            self.game_over = True
        self.lock_timer = None


    def spawn_new_shape(self):
        self.current_shape = self.next_shape
        self.current_shape.canvas = self.game_canvas
        self.next_shape = self.get_next_shape()
        self.hold_used = False
        self.draw_next_shape()


    def lock_shape(self):
        for i, row in enumerate(self.current_shape.shape):
            for j, val in enumerate(row):
                if val:
                    x = self.current_shape.x_pos + j
                    y = self.current_shape.y_pos + i
                    if y >= 0:
                        self.board[y][x] = self.current_shape.color


    def hold_shape(self, event=None):
        if not self.hold_used:
            if self.held_shape:
                self.current_shape, self.held_shape = self.held_shape, self.current_shape
                self.current_shape.x_pos = GRID_WIDTH // 2 - len(self.current_shape.shape[0]) // 2
                self.current_shape.y_pos = 0
            else:
                self.held_shape = self.current_shape
                self.spawn_new_shape()
            self.hold_used = True
            self.draw_held_shape()
            self.draw_board()


#endregion
################################################################################################################################################
#region Line Clearing


    def clear_lines(self):
        lines_to_clear = [y for y in range(GRID_HEIGHT) if all(self.board[y])]
        if lines_to_clear:
            self.flash_lines(lines_to_clear)
            self.root.after(200, self.remove_lines, lines_to_clear)
        else:
            self.collapse_floating_blocks()


    def flash_lines(self, lines):
        for _ in range(3):
            for y in lines:
                for x in range(GRID_WIDTH):
                    self.board[y][x] = None
            self.draw_board()
            self.root.update_idletasks()
            self.root.after(100)
            for y in lines:
                for x in range(GRID_WIDTH):
                    self.board[y][x] = "white"
            self.draw_board()
            self.root.update_idletasks()
            self.root.after(100)


    def remove_lines(self, lines):
        new_board = [row for y, row in enumerate(self.board) if y not in lines]
        lines_cleared = len(lines)
        self.lines_cleared += lines_cleared
        self.score += 10 * lines_cleared * (lines_cleared + 1) // 2 * min(self.level, 3)
        while len(new_board) < GRID_HEIGHT:
            new_board.insert(0, [None for _ in range(GRID_WIDTH)])
        self.board = new_board
        self.update_level()
        self.update_score()
        self.collapse_floating_blocks()


#endregion
################################################################################################################################################
#region Helper Functions


    def get_next_shape(self):
        if not self.shape_bag:
            self.shape_bag = list(range(len(SHAPES)))
            random.shuffle(self.shape_bag)
        next_shape_index = self.shape_bag.pop()
        if len(self.last_shapes) >= 2 and self.last_shapes[-1] == self.last_shapes[-2] == next_shape_index:
            for i, index in enumerate(self.shape_bag):
                if index != next_shape_index:
                    next_shape_index = self.shape_bag.pop(i)
                    break
        self.last_shapes.append(next_shape_index)
        if len(self.last_shapes) > 2:
            self.last_shapes.pop(0)
        shape = SHAPES[next_shape_index]
        color = COLORS[next_shape_index]
        return Tromino(self.game_canvas, shape=shape, color=color)


    def calculate_ghost_position(self):
        ghost_shape = Tromino(self.game_canvas, shape=[row[:] for row in self.current_shape.shape], color=self.current_shape.color)
        ghost_shape.x_pos = self.current_shape.x_pos
        ghost_shape.y_pos = self.current_shape.y_pos
        while not self.check_collision(shape=ghost_shape, dy=1):
            ghost_shape.y_pos += 1
        self.ghost_shape = ghost_shape


    def check_collision(self, shape=None, dx=0, dy=0):
        if shape is None:
            shape = self.current_shape
        for i, row in enumerate(shape.shape):
            for j, val in enumerate(row):
                if val:
                    x = shape.x_pos + j + dx
                    y = shape.y_pos + i + dy
                    if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT:
                        return True
                    if y >= 0 and self.board[y][x]:
                        return True
        return False


#endregion
################################################################################################################################################
#region Event Handlers


    def key_press(self, event):
        keysym = event.keysym
        if keysym in ("Left", "Right", "Down", "Up"):
            if keysym not in self.movement_keys:
                self.move_shape_key(keysym)  # Initial movement
                after_id = self.root.after(INITIAL_MOVE_DELAY, self.move_repeat, keysym)
                self.movement_keys[keysym] = after_id
        elif keysym == "space":
            self.instant_drop()
        elif keysym == "c":
            self.hold_shape()
        elif keysym == "p":
            self.toggle_pause()


    def key_release(self, event):
        keysym = event.keysym
        if keysym in self.movement_keys:
            self.root.after_cancel(self.movement_keys[keysym])
            del self.movement_keys[keysym]


    def move_repeat(self, keysym):
        self.move_shape_key(keysym)
        if keysym in self.movement_keys:
            repeat_rate = 10 if keysym == "Down" else MOVE_REPEAT_RATE
            after_id = self.root.after(repeat_rate, self.move_repeat, keysym)
            self.movement_keys[keysym] = after_id


    def move_shape_key(self, keysym):
        if keysym == "Left":
            self.move_shape(-1, 0)
        elif keysym == "Right":
            self.move_shape(1, 0)
        elif keysym == "Down":
            self.move_shape(0, 1)
        elif keysym == "Up":
            self.rotate_shape()


#endregion
################################################################################################################################################
#region Misc


    def toggle_pause(self, event=None):
        if self.paused:
            self.paused = False
            self.after_id = self.root.after(self.speed, self.drop_shape)
            self.gameloop()
        else:
            self.paused = True
            if self.after_id:
                self.root.after_cancel(self.after_id)
            if self.lock_timer:
                self.root.after_cancel(self.lock_timer)
                self.lock_timer = None
            self.draw_text_on_canvas(text="Paused")


    def show_help(self):
        self.toggle_pause()
        messagebox.showinfo("Help",
            "Move: Up, Down, Left, Right"
            "\n\nDrop: Space"
            "\n\nHold: C"
        )
        self.toggle_pause()
        self.root.focus_set()


    def restart_game(self, event=None):
        if self.after_id:
            self.root.after_cancel(self.after_id)
        self.board = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_shape = Tromino(self.game_canvas)
        self.shape_bag = []
        self.last_shapes = []
        self.next_shape = self.get_next_shape()
        self.spawn_new_shape()
        self.held_shape = None
        self.hold_used = False
        self.draw_next_shape()
        self.draw_held_shape()
        self.game_over = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.speed = INITIAL_SPEED
        self.down_key_pressed = False
        self.update_level()
        self.update_score()
        self.after_id = self.root.after(self.speed, self.drop_shape)
        self.gameloop()


#endregion
################################################################################################################################################
#region Debugging


# Run the game
#import tkinter as tk
#root = tk.Tk()
#root.withdraw()
#game = PyTrominosGame(root)
#game.run()
#root.mainloop()
