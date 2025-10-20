import tkinter as tk
from tkinter import ttk


class ButtonMenu(ttk.Button):
    """
    A ttk.Button widget with an attached Menu that displays on click.

    This widget combines a button and menu, handling all binding automatically.
    The menu is accessible via the `menu` attribute for adding options.

    Args:
        parent: The parent widget
        side: Menu position relative to button: "up", "down", "left", "right" (default: "down")
        **kwargs: Any valid ttk.Button arguments (text, width, etc.)

    Attributes:
        menu: The tk.Menu instance for adding menu items

    Example:
        buttonmenu = ButtonMenu(parent, text="☰", width=2, side="down")
        buttonmenu.pack(side="right", padx=2)

        buttonmenu.menu.add_command(label="Option 1", command=callback)
        buttonmenu.menu.add_separator()
        buttonmenu.menu.add_checkbutton(label="Toggle", command=toggle_callback)
    """


    def __init__(self, parent, side="down", **kwargs):
        """Initialize the ButtonMenu widget."""
        super().__init__(parent, **kwargs)
        self.side = side
        self.menu = tk.Menu(self, tearoff=0)
        self.configure(command=self.show_menu)


    def show_menu(self):
        """Display the menu at the button's location."""
        try:
            btn_x = self.winfo_rootx()
            btn_y = self.winfo_rooty()
            btn_width = self.winfo_width()
            btn_height = self.winfo_height()
            menu_width = self.menu.winfo_reqwidth()
            menu_height = self.menu.winfo_reqheight()
            if self.side == "down":
                x = btn_x
                y = btn_y + btn_height
            elif self.side == "up":
                x = btn_x
                y = btn_y - menu_height - 5
            elif self.side == "left":
                x = btn_x - menu_width - 20
                y = btn_y
            elif self.side == "right":
                x = btn_x + btn_width
                y = btn_y
            else:
                x = btn_x
                y = btn_y + btn_height
            self.menu.post(x, y)
        except tk.TclError:
            pass


    def hide_menu(self):
        """Hide the menu if it's currently displayed."""
        try:
            self.menu.unpost()
        except tk.TclError:
            pass


# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    # up
    menu_up = ButtonMenu(root, text="Up ▲", side="up")
    menu_up.pack(side="left", padx=5, pady=5)
    menu_up.menu.add_command(label="Command", command=lambda: print("Up selected"))
    # down
    menu_down = ButtonMenu(root, text="Down ▼", side="down")
    menu_down.pack(side="left", padx=5, pady=5)
    menu_down.menu.add_command(label="Command", command=lambda: print("Down selected"))
    # left
    menu_left = ButtonMenu(root, text="◀ Left", side="left")
    menu_left.pack(side="left", padx=5, pady=5)
    menu_left.menu.add_command(label="Command", command=lambda: print("Left selected"))
    # right
    menu_right = ButtonMenu(root, text="Right ▶", side="right")
    menu_right.pack(side="left", padx=5, pady=5)
    menu_right.menu.add_command(label="Command", command=lambda: print("Right selected"))

    root.mainloop()
