import tkinter as tk
from tkinter import ttk, TclError, Event

from typing import Literal


SEPARATORS: str = " ,.-|()[]<>\\/\"'{}:;!@#$%^&*+=~`?"


# region Utility


def _is_separator(char: str) -> bool:
    """Check if a character is a separator."""
    return char in SEPARATORS


def _tk_state(flag: bool) -> str:
    """Return a valid tkinter menu state string for a boolean flag."""
    return tk.NORMAL if flag else tk.DISABLED


# endregion
# region Selection


def custom_select_word_for_entry(event: Event) -> Literal["break"]:
    """Select the word under cursor when double-clicking an entry widget."""
    widget: ttk.Entry = event.widget
    click_index: int = widget.index(f"@{event.x}")
    entry_text: str = widget.get()
    if click_index < len(entry_text) and _is_separator(entry_text[click_index]):
        widget.selection_clear()
        widget.selection_range(click_index, click_index + 1)
    else:
        word_start: int = click_index
        while word_start > 0 and not _is_separator(entry_text[word_start - 1]):
            word_start -= 1
        word_end: int = click_index
        while word_end < len(entry_text) and not _is_separator(entry_text[word_end]):
            word_end += 1
        widget.selection_clear()
        widget.selection_range(word_start, word_end)
    widget.icursor(click_index)
    return "break"


def select_all_in_entry(event: Event) -> Literal["break"]:
    """Select all text in the entry widget."""
    widget: ttk.Entry = event.widget
    widget.selection_range(0, 'end')
    return "break"


# endregion
# region Context Menu


def show_entry_context_menu(event: Event) -> None:
    """Show a context menu for the entry widget."""
    widget: ttk.Entry = event.widget
    if isinstance(widget, ttk.Entry):
        root: tk.Tk = widget.winfo_toplevel()
        context_menu: tk.Menu = tk.Menu(root, tearoff=0)
        try:
            has_selection: bool = bool(widget.selection_present())
        except TclError:
            has_selection = False
        has_text: bool = bool(widget.get())
        context_menu.add_command(label="Cut", command=lambda: widget.event_generate("<Control-x>"), state=_tk_state(has_selection))
        context_menu.add_command(label="Copy", command=lambda: widget.event_generate("<Control-c>"), state=_tk_state(has_selection))
        context_menu.add_command(label="Paste", command=lambda: widget.event_generate("<Control-v>"))
        context_menu.add_separator()
        context_menu.add_command(label="Delete", command=lambda: widget.delete("sel.first", "sel.last"), state=_tk_state(has_selection))
        context_menu.add_command(label="Clear", command=lambda: widget.delete(0, "end"), state=_tk_state(has_text))
        context_menu.post(event.x_root, event.y_root)


# endregion
# region Undo/Redo Stack


class EntryHistory:
    """Undo/redo stack for ttk.Entry widgets."""
    def __init__(self, entry: ttk.Entry, max_depth: int = 10000):
        self.entry = entry
        self.max_depth = max_depth
        self.undo_stack: list[str] = []
        self.redo_stack: list[str] = []
        self._prev_value = entry.get()
        self.entry.bind("<KeyRelease>", self._record_change)
        self.entry.bind("<Control-z>", self._on_undo)
        self.entry.bind("<Control-y>", self._on_redo)


    def _record_change(self, event: Event) -> None:
        """Record text changes into the undo stack."""
        current_value = self.entry.get()
        if current_value != self._prev_value:
            if len(self.undo_stack) >= self.max_depth:
                self.undo_stack.pop(0)
            self.undo_stack.append(self._prev_value)
            self._prev_value = current_value
            self.redo_stack.clear()


    def _on_undo(self, event: Event) -> Literal["break"]:
        """Undo the last change."""
        if not self.undo_stack:
            return "break"
        current_value = self.entry.get()
        self.redo_stack.append(current_value)
        prev_value = self.undo_stack.pop()
        self._set_text(prev_value)
        return "break"


    def _on_redo(self, event: Event) -> Literal["break"]:
        """Redo the last undone change."""
        if not self.redo_stack:
            return "break"
        current_value = self.entry.get()
        self.undo_stack.append(current_value)
        next_value = self.redo_stack.pop()
        self._set_text(next_value)
        return "break"


    def _set_text(self, value: str) -> None:
        """Replace the entry content with value."""
        self.entry.delete(0, "end")
        self.entry.insert(0, value)
        self._prev_value = value


# endregion
# region Main


def bind_helpers(entry_widget: ttk.Entry) -> None:
    """Set up standard bindings for ttk.Entry widgets."""
    entry_widget.bind("<Double-1>", custom_select_word_for_entry)
    entry_widget.bind("<Triple-1>", select_all_in_entry)
    entry_widget.bind("<Button-3>", show_entry_context_menu)
    EntryHistory(entry_widget)


# endregion
