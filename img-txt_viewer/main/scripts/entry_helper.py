from typing import Literal
from tkinter import TclError, Event, Menu, Tk
from tkinter import ttk


def bind_helpers(entry_widget: ttk.Entry) -> None:
    """Set up standard bindings for ttk.Entry widgets.

    Args:
        entry_widget: A ttk.Entry widget to apply bindings to
    """
    entry_widget.bind("<Double-1>", custom_select_word_for_entry)
    entry_widget.bind("<Triple-1>", select_all_in_entry)
    entry_widget.bind("<Button-3>", show_entry_context_menu)


def custom_select_word_for_entry(event: Event) -> Literal["break"]:
    """Select the word under cursor when double-clicking an entry widget.

    Args:
        event: The event triggered by double-clicking

    Returns:
        str: 'break' to prevent default event handling
    """
    widget: ttk.Entry = event.widget
    separators: str = " ,.-|()[]<>\\/\"'{}:;!@#$%^&*+=~`?"
    click_index: int = widget.index(f"@{event.x}")
    entry_text: str = widget.get()

    if click_index < len(entry_text) and entry_text[click_index] in separators:
        widget.selection_clear()
        widget.selection_range(click_index, click_index + 1)
    else:
        word_start: int = click_index
        while word_start > 0 and entry_text[word_start - 1] not in separators:
            word_start -= 1
        word_end: int = click_index
        while word_end < len(entry_text) and entry_text[word_end] not in separators:
            word_end += 1
        widget.selection_clear()
        widget.selection_range(word_start, word_end)
    widget.icursor(click_index)
    return "break"


def select_all_in_entry(event: Event) -> Literal["break"]:
    """Select all text in the entry widget.

    Args:
        event: The event triggered by triple-clicking

    Returns:
        str: 'break' to prevent default event handling
    """
    widget: ttk.Entry = event.widget
    widget.selection_range(0, 'end')
    return "break"


def show_entry_context_menu(event: Event) -> None:
    """Show a context menu for the entry widget.

    Args:
        event: The event triggered by right-clicking
    """
    widget: ttk.Entry = event.widget
    if isinstance(widget, ttk.Entry):
        # Get the root window to attach the menu to
        root: Tk = widget.winfo_toplevel()
        context_menu: Menu = Menu(root, tearoff=0)
        # Check if there is a selection and/or text in the widget
        try:
            widget.selection_get()
            has_selection: bool = True
        except TclError:
            has_selection: bool = False
        has_text: bool = bool(widget.get())
        # Add commands to the context menu
        context_menu.add_command(
            label="Cut",
            command=lambda: widget.event_generate("<Control-x>"),
            state="normal" if has_selection else "disabled"
        )
        context_menu.add_command(
            label="Copy",
            command=lambda: widget.event_generate("<Control-c>"),
            state="normal" if has_selection else "disabled"
        )
        context_menu.add_command(
            label="Paste",
            command=lambda: widget.event_generate("<Control-v>")
        )
        context_menu.add_separator()
        context_menu.add_command(
            label="Delete",
            command=lambda: widget.delete("sel.first", "sel.last"),
            state="normal" if has_selection else "disabled"
        )
        context_menu.add_command(
            label="Clear",
            command=lambda: widget.delete(0, "end"),
            state="normal" if has_text else "disabled"
        )
        context_menu.post(event.x_root, event.y_root)
