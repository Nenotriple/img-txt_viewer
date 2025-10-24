"""TextWrapper extends ScrolledText to add text wrapping functionality for brackets and quotes."""

#region Imports


# tkinter
import tkinter as tk
from tkinter import scrolledtext

# Typing
from typing import Tuple


#endregion
#region CustomScrolledText


class CustomScrolledText(scrolledtext.ScrolledText):
    def __init__(self, master: tk.Widget = None, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.bind_wrapping_events()
        self.bind("<Double-1>", self.custom_select_word_for_text, add="+")
        self.bind("<Triple-1>", self.custom_select_line_for_text, add="+")


    def bind_wrapping_events(self) -> None:
        """Bind necessary events to widget."""
        keys_to_bind = ["(", "[", "{", '"', "'"]
        for key in keys_to_bind:
            self.bind(f"<Key-{key}>", self.on_key_press, add="+")


    def on_key_press(self, event: tk.Event) -> str:
        """Handle key press events for bracket wrapping."""
        opening_brackets = {'(': ')', '[': ']', '{': '}', '"': '"', "'": "'"}
        if event.char in opening_brackets:
            self.wrap_selected_text(event.char, opening_brackets[event.char])
            return "break"


    def wrap_selected_text(self, opening_char: str, closing_char: str) -> None:
        """Wrap the selected text with the given opening and closing characters."""
        try:
            start, end, selected_text = self.get_selection()
            if selected_text:
                self.replace_selection_with_wrapped_text(start, end, selected_text, opening_char, closing_char)
                self.reselect_wrapped_text(start, opening_char, selected_text, closing_char)
            else:
                cursor_pos = self.index(tk.INSERT)
                self.insert(cursor_pos, opening_char)
        except tk.TclError:
            pass


    def get_selection(self) -> Tuple[str, str, str]:
        """Get the currently selected text."""
        try:
            start = self.index(tk.SEL_FIRST)
            end = self.index(tk.SEL_LAST)
            selected_text = self.get(start, end)
        except tk.TclError:
            start = end = self.index(tk.INSERT)
            selected_text = ""
        return start, end, selected_text


    def replace_selection_with_wrapped_text(self, start: str, end: str, selected_text: str, opening_char: str, closing_char: str) -> None:
        """Replace the selected text with the wrapped text."""
        self.delete(start, end)
        self.insert(start, f"{opening_char}{selected_text}{closing_char}")


    def reselect_wrapped_text(self, start: str, opening_char: str, selected_text: str, closing_char: str) -> None:
        """Reselect the newly wrapped text."""
        self.tag_remove(tk.SEL, "1.0", tk.END)
        char_count = len(opening_char + selected_text + closing_char)
        new_end = self.index(f"{start}+{char_count}c")
        self.tag_add(tk.SEL, start, new_end)
        self.mark_set(tk.INSERT, new_end)
        self.see(tk.INSERT)


    def insert_empty_wrap(self, opening_char: str, closing_char: str) -> None:
        """Insert an empty wrap at the current cursor position."""
        cursor_pos = self.index(tk.INSERT)
        self.insert(cursor_pos, f"{opening_char}{closing_char}")
        new_pos = self.index(f"{cursor_pos}+1c")
        self.mark_set(tk.INSERT, new_pos)


    def custom_select_word_for_text(self, event: tk.Event) -> str:
        """Select a whole word at or next to the click position (double-click behavior)."""
        separators = " ,.-|()[]<>\\/\"'{}:;!@#$%^&*+=~`?"
        click_index = self.index(f"@{event.x},{event.y}")
        line, char_index = map(int, click_index.split("."))
        line_text = self.get(f"{line}.0", f"{line}.end")
        if char_index >= len(line_text):
            return "break"
        if line_text[char_index] in separators:
            self.tag_remove(tk.SEL, "1.0", tk.END)
            self.tag_add(tk.SEL, f"{line}.{char_index}", f"{line}.{char_index + 1}")
            self.mark_set(tk.INSERT, f"{line}.{char_index + 1}")
        else:
            word_start = char_index
            while word_start > 0 and line_text[word_start - 1] not in separators:
                word_start -= 1
            word_end = char_index
            while word_end < len(line_text) and line_text[word_end] not in separators:
                word_end += 1
            self.tag_remove(tk.SEL, "1.0", tk.END)
            self.tag_add(tk.SEL, f"{line}.{word_start}", f"{line}.{word_end}")
            self.mark_set(tk.INSERT, f"{line}.{word_end}")
        return "break"


    def custom_select_line_for_text(self, event: tk.Event) -> str:
        """Select the whole line for a triple-click."""
        click_index = self.index(f"@{event.x},{event.y}")
        line, _ = map(int, click_index.split("."))
        self.tag_remove(tk.SEL, "1.0", tk.END)
        self.tag_add(tk.SEL, f"{line}.0", f"{line}.end")
        self.mark_set(tk.INSERT, f"{line}.0")
        return "break"
