"""TextWrapper extends ScrolledText to add text wrapping functionality for brackets and quotes."""

import tkinter as tk
from tkinter import scrolledtext

class CustomScrolledText(scrolledtext.ScrolledText):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.bind_wrapping_events()


    def bind_wrapping_events(self):
        """Bind necessary events to widget."""
        keys_to_bind = ["(", "[", "{", '"', "'"]
        for key in keys_to_bind:
            self.bind(f"<Key-{key}>", self.on_key_press)


    def on_key_press(self, event):
        """Handle key press events for bracket wrapping."""
        opening_brackets = {'(': ')', '[': ']', '{': '}', '"': '"', "'": "'"}
        if event.char in opening_brackets:
            self.wrap_selected_text(event.char, opening_brackets[event.char])
            return "break"


    def wrap_selected_text(self, opening_char, closing_char):
        """Wrap the selected text with the given opening and closing characters."""
        try:
            start, end, selected_text = self.get_selection()
            if selected_text:
                self.replace_selection_with_wrapped_text(start, end, selected_text, opening_char, closing_char)
                self.reselect_wrapped_text(start, opening_char, selected_text, closing_char)
            else:
                self.insert_empty_wrap(opening_char, closing_char)
        except tk.TclError:
            pass


    def get_selection(self):
        """Get the currently selected text."""
        try:
            start = self.index("sel.first")
            end = self.index("sel.last")
            selected_text = self.get(start, end)
        except tk.TclError:
            start = end = self.index(tk.INSERT)
            selected_text = ""
        return start, end, selected_text


    def replace_selection_with_wrapped_text(self, start, end, selected_text, opening_char, closing_char):
        """Replace the selected text with the wrapped text."""
        self.delete(start, end)
        self.insert(start, f"{opening_char}{selected_text}{closing_char}")


    def reselect_wrapped_text(self, start, opening_char, selected_text, closing_char):
        """Reselect the newly wrapped text."""
        self.tag_remove(tk.SEL, 1.0, tk.END)
        new_end = self.index(f"{start}+{len(opening_char + selected_text + closing_char)}c")
        self.tag_add(tk.SEL, start, new_end)
        self.mark_set(tk.INSERT, new_end)
        self.see(tk.INSERT)


    def insert_empty_wrap(self, opening_char, closing_char):
        """Insert an empty wrap at the current cursor position."""
        cursor_pos = self.index(tk.INSERT)
        self.insert(cursor_pos, f"{opening_char}{closing_char}")
        self.mark_set(tk.INSERT, f"{cursor_pos}+1c")
