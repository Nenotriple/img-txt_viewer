"""
A minimal, standalone simpledialog-like module using Tkinter Toplevel and ttk.

API:
- askstring(title, prompt, initialvalue=None, parent=None, show=None, icon_image=None) -> Optional[str]
- askinteger(title, prompt, initialvalue=None, minvalue=None, maxvalue=None, parent=None, icon_image=None) -> Optional[int]
- askfloat(title, prompt, initialvalue=None, minvalue=None, maxvalue=None, parent=None, icon_image=None) -> Optional[float]
- askcombo(title, prompt, values, initialvalue=None, parent=None, icon_image=None) -> Optional[str]
- askradio(title, prompt, values, initialvalue=None, parent=None, icon_image=None) -> Optional[str]
"""


# region Imports and Typing


from __future__ import annotations


# Standard GUI
import tkinter as tk
from tkinter import ttk, messagebox


# Type hints
from typing import Optional, Sequence, Union


# endregion
# region API and Constants


__all__ = ["askstring", "askinteger", "askfloat", "askcombo", "askradio"]


ChoiceValue = Union[str, tuple[str, str]]


# endregion
# region Utility


def _get_or_create_root(parent: Optional[tk.Misc]) -> tuple[tk.Misc, bool]:
    """Return (root, created_root_flag)."""
    root: Optional[tk.Misc] = parent
    created = False
    if root is None:
        try:
            root = tk._get_default_root()  # type: ignore[attr-defined]
        except Exception:
            root = None
        if root is None:
            root = tk.Tk()
            created = True
            try:
                root.withdraw()
            except Exception:
                pass
    return root, created


def _setup_dialog_window(dialog: tk.Toplevel, parent: Optional[tk.Misc], title: str, icon_image: Optional["tk.PhotoImage"]) -> None:
    dialog.withdraw()
    dialog.title(title or "")
    dialog.resizable(False, False)
    dialog.protocol("WM_DELETE_WINDOW", lambda: _on_cancel(dialog))
    dialog.bind("<Return>", lambda e: _on_ok(dialog))
    dialog.bind("<Escape>", lambda e: _on_cancel(dialog))
    if icon_image is not None:
        try:
            dialog.iconphoto(False, icon_image)
        except Exception:
            pass
    if parent:
        try:
            dialog.transient(parent)
        except Exception:
            pass


def _create_container(dialog: tk.Toplevel, prompt: str) -> ttk.Frame:
    container = ttk.Frame(dialog, padding=(12, 10))
    container.grid(row=0, column=0, sticky="nsew")
    dialog.columnconfigure(0, weight=1)
    dialog.rowconfigure(0, weight=1)
    container.columnconfigure(0, weight=1)
    lbl = ttk.Label(container, text=prompt, anchor="w", justify="left")
    lbl.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
    return container


def create_general_dialog_buttons(dialog: tk.Toplevel, ok_text: str, cancel_text: str, container: ttk.Frame) -> None:
    btn_frame = ttk.Frame(container)
    btn_frame.grid(row=2, column=0, columnspan=2, sticky="e", pady=(10, 0))
    ok_btn = ttk.Button(btn_frame, text=ok_text, command=lambda: _on_ok(dialog), default="active")
    ok_btn.grid(row=0, column=0, padx=(0, 6))
    ok_btn.bind("<Enter>", lambda e: ok_btn.configure(cursor="hand2"))
    ok_btn.bind("<Leave>", lambda e: ok_btn.configure(cursor=""))
    cancel_btn = ttk.Button(btn_frame, text=cancel_text, command=lambda: _on_cancel(dialog))
    cancel_btn.grid(row=0, column=1)
    cancel_btn.bind("<Enter>", lambda e: cancel_btn.configure(cursor="hand2"))
    cancel_btn.bind("<Leave>", lambda e: cancel_btn.configure(cursor=""))


def _center_window_to_parent(window: tk.Toplevel, parent: Optional[tk.Misc]) -> None:
    """Center a Toplevel window to its parent or screen."""
    window.update_idletasks()
    w = window.winfo_reqwidth()
    h = window.winfo_reqheight()
    try:
        if parent and parent.winfo_ismapped():
            px, py = parent.winfo_rootx(), parent.winfo_rooty()
            pw, ph = parent.winfo_width(), parent.winfo_height()
            x = px + max(0, (pw - w) // 2)
            y = py + max(0, (ph - h) // 2)
        else:
            sw, sh = window.winfo_screenwidth(), window.winfo_screenheight()
            x = max(0, (sw - w) // 2)
            y = max(0, (sh - h) // 3)
    except Exception:
        sw, sh = window.winfo_screenwidth(), window.winfo_screenheight()
        x = max(0, (sw - w) // 2)
        y = max(0, (sh - h) // 3)
    window.geometry(f"+{x}+{y}")


def _on_ok(dialog: tk.Toplevel, var_attr: str = "_var"):
    setattr(dialog, "result", getattr(dialog, var_attr).get())
    dialog.destroy()


def _on_cancel(dialog: tk.Toplevel):
    dialog.result = None
    dialog.destroy()


def _validate_value(value_str: str, value_type: type, minvalue=None, maxvalue=None) -> tuple[bool, str]:
    """Universal value validator for int/float dialogs. Returns (is_valid, error_message)."""
    try:
        val = value_type(value_str)
    except Exception:
        return False, f"Please enter a valid {value_type.__name__}."
    if minvalue is not None and val < minvalue:
        return False, f"Please enter a {value_type.__name__} >= {minvalue}."
    if maxvalue is not None and val > maxvalue:
        return False, f"Please enter a {value_type.__name__} <= {maxvalue}."
    return True, ""


def _ask_number(title: Optional[str], prompt: str, initialvalue: Optional[Union[int, float]], minvalue: Optional[Union[int, float]], maxvalue: Optional[Union[int, float]], parent: Optional[tk.Misc], icon_image: Optional["tk.PhotoImage"], value_type: type, error_title: str) -> Optional[Union[int, float]]:
    root, created = _get_or_create_root(parent)
    try:
        current = str(initialvalue) if initialvalue is not None else None
        while True:
            input_string = askstring(title, prompt, initialvalue=current, parent=root, icon_image=icon_image)
            if input_string is None:
                return None
            valid, msg = _validate_value(input_string, value_type, minvalue, maxvalue)
            if not valid:
                messagebox.showerror(title or error_title, msg, parent=root)
                current = input_string
                continue
            return value_type(input_string)
    finally:
        if created and isinstance(root, tk.Tk):
            try:
                root.destroy()
            except Exception:
                pass


# endregion
# region Dialog Classes
# region _AskStringDialog


class _AskStringDialog(tk.Toplevel):
    """A modal dialog asking for a single string input."""
    def __init__(self, parent: tk.Misc, title: Optional[str], prompt: str, initialvalue: Optional[str] = None, ok_text: str = "OK", cancel_text: str = "Cancel", icon_image: Optional["tk.PhotoImage"] = None) -> None:
        super().__init__(parent)
        self.result: Optional[str] = None
        _setup_dialog_window(self, parent, title, icon_image)
        container = self._create_dialog_widgets(prompt, initialvalue)
        create_general_dialog_buttons(self, ok_text, cancel_text, container)
        self._show_dialog(parent, initialvalue)


    def _create_dialog_widgets(self, prompt: str, initialvalue: Optional[str]) -> ttk.Frame:
        container = _create_container(self, prompt)
        self._var = tk.StringVar(value="" if initialvalue is None else str(initialvalue))
        entry_width = max(24, min(60, len(self._var.get()) + 10))
        self.entry = ttk.Entry(container, textvariable=self._var, width=entry_width)
        self.entry.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.entry.bind("<Enter>", lambda e: self.entry.configure(cursor="hand2"))
        self.entry.bind("<Leave>", lambda e: self.entry.configure(cursor=""))
        return container


    def _show_dialog(self, parent: Optional[tk.Misc], initialvalue: Optional[str]) -> None:
        _center_window_to_parent(self, parent)
        self.deiconify()
        self.grab_set()
        self.entry.focus_set()
        if initialvalue:
            self.entry.selection_range(0, tk.END)
            self.entry.icursor(tk.END)



# endregion
# region _AskComboDialog


class _AskComboDialog(tk.Toplevel):
    """A modal dialog asking for a selection from a dropdown list."""
    def __init__(self, parent: tk.Misc, title: Optional[str], prompt: str, values: list[str], initialvalue: Optional[str] = None, ok_text: str = "OK", cancel_text: str = "Cancel", icon_image: Optional["tk.PhotoImage"] = None) -> None:
        super().__init__(parent)
        self.result: Optional[str] = None
        _setup_dialog_window(self, parent, title, icon_image)
        container = self._create_dialog_widgets(prompt, values)
        create_general_dialog_buttons(self, ok_text, cancel_text, container)
        self.show_dialog(parent, initialvalue, values)


    def _create_dialog_widgets(self, prompt: str, values: list[str], initialvalue: Optional[str] = None) -> ttk.Frame:
        container = _create_container(self, prompt)
        self._var = tk.StringVar()
        combo_width = max(24, min(60, max(len(str(v)) for v in values) + 10))
        self.combo = ttk.Combobox(container, textvariable=self._var, values=values, width=combo_width, state="readonly")
        self.combo.bind("<Enter>", lambda e: self.combo.configure(cursor="hand2"))
        self.combo.bind("<Leave>", lambda e: self.combo.configure(cursor=""))
        self.combo.grid(row=1, column=0, columnspan=2, sticky="ew")
        return container


    def show_dialog(self, parent: Optional[tk.Misc], initialvalue: Optional[str], values: list[str]) -> None:
        _center_window_to_parent(self, parent)
        self.deiconify()
        self.grab_set()
        self.combo.focus_set()
        if initialvalue is not None and initialvalue in values:
            self._var.set(initialvalue)
        elif values:
            self._var.set(values[0])


# endregion
# region _AskRadioDialog


class _AskRadioDialog(tk.Toplevel):
    """A modal dialog presenting a list of radio button choices, with optional descriptions."""
    def __init__(self, parent: tk.Misc, title: Optional[str], prompt: str, values: Sequence[ChoiceValue], initialvalue: Optional[str] = None, ok_text: str = "OK", cancel_text: str = "Cancel", icon_image: Optional["tk.PhotoImage"] = None) -> None:
        super().__init__(parent)
        self.result: Optional[str] = None
        _setup_dialog_window(self, parent, title, icon_image)
        container, first_radiobutton = self.create_dialog_widgets(prompt, values)
        create_general_dialog_buttons(self, ok_text, cancel_text, container)
        self.show_dialog(parent, initialvalue, first_radiobutton)


    def create_dialog_widgets(self, prompt, values):
        container = _create_container(self, prompt)
        self._var = tk.StringVar()
        self._choices: list[str] = []
        radio_frame = ttk.Frame(container)
        radio_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        first_radiobutton: Optional[ttk.Radiobutton] = None
        for idx, choice in enumerate(values):
            # Support (value, label), (value, label, description), or just value
            if isinstance(choice, tuple):
                if len(choice) == 3:
                    value, label, description = choice
                elif len(choice) == 2:
                    value, label = choice
                    description = None
                else:
                    value = str(choice[0])
                    label = value
                    description = None
            else:
                value = str(choice)
                label = value
                description = None
            self._choices.append(value)
            opt_frame = ttk.Frame(radio_frame)
            opt_frame.grid(row=idx, column=0, sticky="ew", pady=(0 if idx == 0 else 8, 0))
            opt_frame.columnconfigure(0, weight=1)
            btn = ttk.Radiobutton(opt_frame, text=label, value=value, variable=self._var)
            btn.grid(row=0, column=0, sticky="w")
            btn.bind("<Enter>", lambda e, b=btn: b.configure(cursor="hand2"))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(cursor=""))
            if first_radiobutton is None:
                first_radiobutton = btn
            if description:
                desc_lbl = ttk.Label(opt_frame, text=description, anchor="w", justify="left", font=("TkDefaultFont", 9), foreground="gray", wraplength=400)
                desc_lbl.grid(row=1, column=0, sticky="w", padx=(24, 0))
                desc_lbl.bind("<Button-1>", lambda e, v=value: self._var.set(v))
                desc_lbl.bind("<Enter>", lambda e, l=desc_lbl: l.configure(cursor="hand2"))
                desc_lbl.bind("<Leave>", lambda e, l=desc_lbl: l.configure(cursor=""))
        return container, first_radiobutton


    def show_dialog(self, parent: Optional[tk.Misc], initialvalue: Optional[str], first_radiobutton: Optional[ttk.Radiobutton]) -> None:
        _center_window_to_parent(self, parent)
        self.deiconify()
        self.grab_set()
        if initialvalue is not None and initialvalue in self._choices:
            self._var.set(initialvalue)
        elif self._choices:
            self._var.set(self._choices[0])
        if first_radiobutton is not None:
            first_radiobutton.focus_set()


# endregion
# endregion
# region Public API


def askstring(title: Optional[str], prompt: str, initialvalue: Optional[str] = None, parent: Optional[tk.Misc] = None, icon_image: Optional["tk.PhotoImage"] = None) -> Optional[str]:
    """Show a modal prompt dialog and return the entered string, or None if canceled.

    Parameters:
        title: Dialog window title
        prompt: Text prompt displayed above the entry field
        initialvalue: Initial value for the entry field
        parent: Parent window
        icon_image: Optional window icon

    Returns:
        Entered string value or None if canceled
    """
    root, created = _get_or_create_root(parent)
    try:
        dialog = _AskStringDialog(parent=root, title=title, prompt=prompt, initialvalue=initialvalue, icon_image=icon_image)
        dialog.wait_window()
        result = dialog.result
        return result
    finally:
        if created and isinstance(root, tk.Tk):
            try:
                root.destroy()
            except Exception:
                pass


def askinteger(title: Optional[str], prompt: str, initialvalue: Optional[int] = None, minvalue: Optional[int] = None, maxvalue: Optional[int] = None, parent: Optional[tk.Misc] = None, icon_image: Optional["tk.PhotoImage"] = None) -> Optional[int]:
    """Show a modal prompt dialog for integer input. Returns None if canceled.

    Parameters:
        title: Dialog window title
        prompt: Text prompt displayed above the entry field
        initialvalue: Initial integer value
        minvalue: Minimum allowed integer value
        maxvalue: Maximum allowed integer value
        parent: Parent window
        icon_image: Optional window icon

    Returns:
        Entered integer value or None if canceled
    """
    return _ask_number(title, prompt, initialvalue, minvalue, maxvalue, parent, icon_image, int, "Invalid integer")


def askfloat(title: Optional[str], prompt: str, initialvalue: Optional[float] = None, minvalue: Optional[float] = None, maxvalue: Optional[float] = None, parent: Optional[tk.Misc] = None, icon_image: Optional["tk.PhotoImage"] = None) -> Optional[float]:
    """Show a modal prompt dialog for float input. Returns None if canceled.

    Parameters:
        title: Dialog window title
        prompt: Text prompt displayed above the entry field
        initialvalue: Initial float value
        minvalue: Minimum allowed float value
        maxvalue: Maximum allowed float value
        parent: Parent window
        icon_image: Optional window icon

    Returns:
        Entered float value or None if canceled
    """
    return _ask_number(title, prompt, initialvalue, minvalue, maxvalue, parent, icon_image, float, "Invalid number")


def askcombo(title: Optional[str], prompt: str, values: list[str], initialvalue: Optional[str] = None, parent: Optional[tk.Misc] = None, icon_image: Optional["tk.PhotoImage"] = None) -> Optional[str]:
    """Show a modal dialog with a combobox for selecting from predefined values.

    Parameters:
        title: Dialog window title
        prompt: Text prompt displayed above the combobox
        values: List of strings to populate the combobox
        initialvalue: Initial selection (must be in values list)
        parent: Parent window
        icon_image: Optional window icon

    Returns:
        Selected string value or None if canceled
    """
    if not values:
        raise ValueError("values list cannot be empty")
    root, created = _get_or_create_root(parent)
    try:
        dialog = _AskComboDialog(parent=root, title=title, prompt=prompt, values=values, initialvalue=initialvalue, icon_image=icon_image)
        dialog.wait_window()
        return dialog.result
    finally:
        if created and isinstance(root, tk.Tk):
            try:
                root.destroy()
            except Exception:
                pass


def askradio(title: Optional[str], prompt: str, values: Sequence[ChoiceValue], initialvalue: Optional[str] = None, parent: Optional[tk.Misc] = None, icon_image: Optional["tk.PhotoImage"] = None) -> Optional[str]:
    """Show a modal dialog with radio buttons for selecting a single option.

    Parameters:
        title: Dialog window title
        prompt: Text prompt displayed above the radio buttons
        values: Sequence of choices, each can be:
            - a string (used as both value and label)
            - a tuple (value, label)
            - a tuple (value, label, description)
        initialvalue: Value to be selected initially (must match one of the values)
        parent: Parent window
        icon_image: Optional window icon

    Returns:
        Selected value (string) or None if canceled
    """
    if not values:
        raise ValueError("values list cannot be empty")
    root, created = _get_or_create_root(parent)
    try:
        dialog = _AskRadioDialog(parent=root, title=title, prompt=prompt, values=values, initialvalue=initialvalue, icon_image=icon_image)
        dialog.wait_window()
        return dialog.result
    finally:
        if created and isinstance(root, tk.Tk):
            try:
                root.destroy()
            except Exception:
                pass


# endregion
# region Main Test Block


if __name__ == "__main__":
    # Test askstring
    #val = askstring("Input required", "Enter a value:", initialvalue="Hello")
    #print("String result:", repr(val))


    # Test askcombo
    #colors = ["Red", "Green", "Blue", "Yellow", "Purple", "Orange"]
    #selected_color = askcombo("Color Selection", "Choose your favorite color:", colors, initialvalue="Blue")
    #print("Selected color:", repr(selected_color))


    # Test askinteger
    #val = askinteger("Input required", "Enter a value (10-100):", initialvalue=42, minvalue=10, maxvalue=100)
    #print("Integer result:", repr(val))


    # Test askfloat
    #val = askfloat("Input required", "Enter a float value (0.0 - 1.0):", initialvalue=0.5, minvalue=0.0, maxvalue=1.0)
    #print("Float result:", repr(val))


    # Test askradio
    radio_options = [
        ("return_val1", "display_label1"),
        ("return_val2", "display_label2", ("description2. " * 4)),
        ("return_val3", "display_label3", ("description3. " * 8)),
        ("return_val4", "display_label4", ("description4. " * 12)),
    ]
    selected_radio = askradio("Radio Selection", "Choose an option:", radio_options, initialvalue="return_val1")
    print("Selected radio option:", repr(selected_radio))


# endregion
