#region Imports


import tkinter as tk
from tkinter import ttk, TclError, Event

from typing import Literal



#endregion
#region EntrySelectionManager


class EntrySelectionManager:
    """Manager for selection operations in ttk.Entry widgets."""
    def __init__(self, entry: ttk.Entry):
        self.entry = entry
        self._bind_selection_events()


    def _bind_selection_events(self):
        self.entry.bind("<Double-1>", self.select_word_event)
        self.entry.bind("<Triple-1>", self.select_all_event)


    def select_word_event(self, event: Event) -> Literal["break"]:
        """Select the word under cursor when double-clicking an entry widget."""
        widget: ttk.Entry = event.widget
        click_index: int = widget.index(f"@{event.x}")
        entry_text: str = widget.get()
        if click_index < len(entry_text) and self._is_separator(entry_text[click_index]):
            widget.selection_clear()
            widget.selection_range(click_index, click_index + 1)
        else:
            word_start: int = click_index
            while word_start > 0 and not self._is_separator(entry_text[word_start - 1]):
                word_start -= 1
            word_end: int = click_index
            while word_end < len(entry_text) and not self._is_separator(entry_text[word_end]):
                word_end += 1
            widget.selection_clear()
            widget.selection_range(word_start, word_end)
        widget.icursor(click_index)
        return "break"


    def select_all_event(self, event: Event) -> Literal["break"]:
        """Select all text in the entry widget."""
        widget: ttk.Entry = event.widget
        widget.selection_range(0, 'end')
        return "break"


    @staticmethod
    def _is_separator(char: str) -> bool:
        """Check if a character is a separator."""
        return char in " ,.-|()[]<>\\/\"'{}:;!@#$%^&*+=~`?"


#endregion
#region EntryContextMenu


class EntryContextMenu:
    """Context menu manager for ttk.Entry widgets, allows adding custom commands."""
    def __init__(self, entry: ttk.Entry):
        self.entry = entry
        self.root = entry.winfo_toplevel()
        self.menu = tk.Menu(self.root, tearoff=0)
        self._custom_commands = []
        self._has_custom_separator = False
        self._add_default_commands()
        self._custom_start_index = self.menu.index("end") + 1 if self.menu.index("end") is not None else 0
        self.entry._entry_context_menu = self  # attach for event handler
        self.entry.bind("<Button-3>", self.show_entry_context_menu)


    def _add_default_commands(self):
        """Add default cut/copy/paste/delete/clear commands to the context menu."""
        try:
            has_selection = bool(self.entry.selection_present())
        except TclError:
            has_selection = False
        has_text = bool(self.entry.get())
        self.menu.add_command(label="Cut", command=lambda: self.entry.event_generate("<Control-x>"), state=self._tk_state(has_selection))
        self.menu.add_command(label="Copy", command=lambda: self.entry.event_generate("<Control-c>"), state=self._tk_state(has_selection))
        self.menu.add_command(label="Paste", command=lambda: self.entry.event_generate("<Control-v>"))
        self.menu.add_separator()
        self.menu.add_command(label="Delete", command=lambda: self.entry.delete("sel.first", "sel.last"), state=self._tk_state(has_selection))
        self.menu.add_command(label="Clear", command=lambda: self.entry.delete(0, "end"), state=self._tk_state(has_text))


    def show(self, event: Event):
        """Display the context menu at the event position."""
        self.menu.delete(0, "end")
        self._add_default_commands()
        if self._custom_commands:
            self.menu.add_separator()
            for kind, args, kwargs in self._custom_commands:
                if kind == "command":
                    self.menu.add_command(*args, **kwargs)
                elif kind == "checkbutton":
                    self.menu.add_checkbutton(*args, **kwargs)
                elif kind == "radiobutton":
                    self.menu.add_radiobutton(*args, **kwargs)
        self.menu.post(event.x_root, event.y_root)


    def add_command(self, *args, **kwargs):
        """Add a command to the context menu."""
        self._custom_commands.append(("command", args, kwargs))


    def add_checkbutton(self, *args, **kwargs):
        """Add a checkbutton to the context menu."""
        self._custom_commands.append(("checkbutton", args, kwargs))


    def add_radiobutton(self, *args, **kwargs):
        """Add a radiobutton to the context menu."""
        self._custom_commands.append(("radiobutton", args, kwargs))


    def entryconfig(self, label: str, **kwargs):
        """Set the configuration of a custom command by its label."""
        for i, (kind, args, current_kwargs) in enumerate(self._custom_commands):
            if 'label' in current_kwargs and current_kwargs['label'] == label:
                current_kwargs.update(kwargs)
                self._custom_commands[i] = (kind, args, current_kwargs)
                break


    @staticmethod
    def _tk_state(flag: bool) -> str:
        """Return a valid tkinter menu state string for a boolean flag."""
        return tk.NORMAL if flag else tk.DISABLED


    @staticmethod
    def show_entry_context_menu(event: Event):
        """Internal handler to show the context menu instance."""
        widget = event.widget
        if hasattr(widget, "_entry_context_menu") and isinstance(widget._entry_context_menu, EntryContextMenu):
            widget._entry_context_menu.show(event)


#endregion
#region EntryHistory


class EntryHistory:
    """Undo/redo stack for ttk.Entry widgets."""
    def __init__(self, entry: ttk.Entry, max_depth: int = 10000):
        self.entry = entry
        self.max_depth = max_depth
        self.undo_stack: list[tuple[str, int]] = []
        self.redo_stack: list[tuple[str, int]] = []
        # Initialize previous value and cursor from the widget's current content
        self._prev_value = entry.get()
        self._prev_cursor = entry.index("insert")
        # Record changes
        self.entry.bind("<KeyRelease>", self._record_change)
        self.entry.bind("<Button-1>", self._sync_prev_value)
        self.entry.bind("<FocusIn>", self._sync_prev_value)
        # Undo / redo bindings
        self.entry.bind("<Control-z>", self._on_undo)
        self.entry.bind("<Control-y>", self._on_redo)


    def _sync_prev_value(self, event: Event) -> None:
        """Synchronize the internal previous value with the widget content."""
        self._prev_value = self.entry.get()
        self._prev_cursor = self.entry.index("insert")


    def _record_change(self, event: Event) -> None:
        """Record text changes into the undo stack."""
        current_value = self.entry.get()
        current_cursor = self.entry.index("insert")
        if current_value != self._prev_value:
            if len(self.undo_stack) >= self.max_depth:
                self.undo_stack.pop(0)
            self.undo_stack.append((self._prev_value, self._prev_cursor))
            self._prev_value = current_value
            self._prev_cursor = current_cursor
            self.redo_stack.clear()
        else:
            self._prev_cursor = current_cursor  # Always update cursor


    def _on_undo(self, event: Event) -> Literal["break"]:
        """Undo the last change."""
        if not self.undo_stack:
            return "break"
        current_value = self.entry.get()
        current_cursor = self.entry.index("insert")
        self.redo_stack.append((current_value, current_cursor))
        prev_value, prev_cursor = self.undo_stack.pop()
        self._set_text(prev_value, prev_cursor)
        return "break"


    def _on_redo(self, event: Event) -> Literal["break"]:
        """Redo the last undone change."""
        if not self.redo_stack:
            return "break"
        current_value = self.entry.get()
        current_cursor = self.entry.index("insert")
        self.undo_stack.append((current_value, current_cursor))
        next_value, next_cursor = self.redo_stack.pop()
        self._set_text(next_value, next_cursor)
        return "break"


    def _set_text(self, value: str, cursor: int) -> None:
        """Replace the entry content with value and restore cursor position."""
        self.entry.delete(0, "end")
        self.entry.insert(0, value)
        self.entry.icursor(cursor)
        self._prev_value = value
        self._prev_cursor = cursor


#endregion
#region Main API


# All
def bind_helpers(entry_widget: ttk.Entry) -> tuple[EntrySelectionManager, EntryContextMenu, EntryHistory]:
    """Set up standard bindings for ttk.Entry widgets and return selection manager, context menu manager, and history."""
    selection_manager = EntrySelectionManager(entry_widget)
    context_menu = EntryContextMenu(entry_widget)
    history = EntryHistory(entry_widget)
    return selection_manager, context_menu, history


# Selection
def bind_selection_manager(entry_widget: ttk.Entry) -> EntrySelectionManager:
    """Bind only the selection logic to a ttk.Entry widget and return the selection manager."""
    return EntrySelectionManager(entry_widget)


# Context Menu
def bind_context_menu(entry_widget: ttk.Entry) -> EntryContextMenu:
    """Bind only the context menu logic to a ttk.Entry widget and return the context menu manager."""
    return EntryContextMenu(entry_widget)


# Undo Stack
def bind_undo_stack(entry_widget: ttk.Entry, max_depth: int = 10000) -> EntryHistory:
    """Attach an undo/redo stack to a ttk.Entry widget."""
    return EntryHistory(entry_widget, max_depth)


#endregion
#endregion
