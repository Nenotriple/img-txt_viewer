"""
custom_simpledialog — simple, standalone dialogs using Tk/Ttk.

Purpose:
- Minimal, dependency-free replacements for common tkinter.simpledialog dialogs.
- Uses Toplevel and ttk widgets; returns Python values or None when cancelled.

Public API:
- askstring(title, prompt, initialvalue=None, parent=None, icon_image=None) -> Optional[str]
- askinteger(title, prompt, initialvalue=None, minvalue=None, maxvalue=None, parent=None, icon_image=None) -> Optional[int]
- askfloat(title, prompt, initialvalue=None, minvalue=None, maxvalue=None, parent=None, icon_image=None) -> Optional[float]
- askcombo(title, prompt, values, initialvalue=None, parent=None, icon_image=None) -> Optional[str]
- askradio(title, prompt, values, initialvalue=None, parent=None, icon_image=None) -> Optional[str]
- askyesno(title, prompt, detail=None, parent=None, icon_image=None) -> bool
- askyesnocancel(title, prompt, detail=None, parent=None, icon_image=None) -> Optional[bool]
- showinfo(title, prompt, detail=None, parent=None, icon_image=None) -> None

Notes:
- askradio accepts a sequence of choices. Each choice may be:
    - a string (used as both value and label)
    - a tuple (value, label)
    - a tuple (value, label, detail) — detail is displayed below the label
- All dialogs return the chosen or entered value, or None if cancelled.
- If no parent is provided, a temporary root window is created and destroyed after the dialog.
- Not designed for multi-threaded GUI usage.

Example:
    val = askstring("Name", "Enter your name:", initialvalue="Alice")
    num = askinteger("Count", "Enter a number:", initialvalue=5, minvalue=1, maxvalue=10)
"""

# region Imports


from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Sequence, Union


# endregion
# region Constants


__all__ = ["askstring", "askinteger", "askfloat", "askcombo", "askradio", "askyesno", "askyesnocancel", "showinfo"]
ChoiceValue = Union[str, tuple[str, str]]


# endregion
# region Utility

# region Root helpers


def _get_or_create_root(parent: Optional[tk.Misc]) -> tuple[tk.Misc, bool]:
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
            root.withdraw()
    return root, created


def _release_tk_variable(var: object) -> None:
    if isinstance(var, tk.Variable):
        try:
            var._tk = None  # type: ignore[attr-defined]
        except Exception:
            pass


def _run_dialog(dialog_class, *args, parent=None, icon_image=None, **kwargs):
    root, created = _get_or_create_root(parent)
    dialog = None
    try:
        dialog = dialog_class(parent=root, icon_image=icon_image, *args, **kwargs)
        dialog.wait_window()
        return dialog.result
    finally:
        if created and isinstance(root, tk.Tk):
            root.destroy()


# endregion
# region Dialog actions


def _on_ok(dialog: tk.Toplevel, var_attr: str = "_var"):
    var = getattr(dialog, var_attr, None)
    if isinstance(var, tk.Variable):
        dialog.result = var.get()
    else:
        dialog.result = getattr(dialog, var_attr, None)
    dialog.destroy()
    _release_tk_variable(var)
    setattr(dialog, var_attr, None)


def _on_cancel(dialog: tk.Toplevel, var_attr: str = "_var"):
    var = getattr(dialog, var_attr, None)
    dialog.result = None
    dialog.destroy()
    _release_tk_variable(var)
    setattr(dialog, var_attr, None)


# endregion
# region Layout helpers


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
    dialog.minsize(340, 120)


def _center_window_to_parent(window: tk.Toplevel, parent: Optional[tk.Misc]) -> None:
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


def _create_container(dialog: tk.Toplevel, prompt: str) -> ttk.Frame:
    container = ttk.Frame(dialog, padding=(18, 14, 18, 14))
    container.grid(row=0, column=0, sticky="nsew")
    dialog.columnconfigure(0, weight=1)
    dialog.rowconfigure(0, weight=1)
    container.columnconfigure(0, weight=1)
    lbl = ttk.Label(container, text=prompt, anchor="w", justify="left", wraplength=420)
    lbl.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 12), padx=(0, 0))
    return container


def _bind_widget_cursor_hand2(widget: tk.Widget) -> None:
    widget.bind("<Enter>", lambda e: widget.configure(cursor="hand2"))
    widget.bind("<Leave>", lambda e: widget.configure(cursor=""))


def _create_general_dialog_buttons(dialog: tk.Toplevel, ok_text: str, cancel_text: str, container: ttk.Frame) -> None:
    btn_frame = ttk.Frame(container)
    btn_frame.grid(row=2, column=0, columnspan=2, sticky="e", pady=(16, 0), padx=(0, 0))
    ok_btn = ttk.Button(btn_frame, text=ok_text, command=lambda: _on_ok(dialog), default="active")
    ok_btn.grid(row=0, column=0, padx=(0, 10))
    _bind_widget_cursor_hand2(ok_btn)
    cancel_btn = ttk.Button(btn_frame, text=cancel_text, command=lambda: _on_cancel(dialog))
    cancel_btn.grid(row=0, column=1)
    _bind_widget_cursor_hand2(cancel_btn)


# endregion
# region Input validation


def _validate_value(value_str: str, value_type: type, minvalue=None, maxvalue=None) -> tuple[bool, str]:
    try:
        val = value_type(value_str)
    except Exception:
        return False, f"Please enter a valid {value_type.__name__}."
    if minvalue is not None and val < minvalue:
        return False, f"Please enter a {value_type.__name__} >= {minvalue}."
    if maxvalue is not None and val > maxvalue:
        return False, f"Please enter a {value_type.__name__} <= {maxvalue}."
    return True, ""


def _ask_number(
    title: Optional[str],
    prompt: str,
    initialvalue: Optional[Union[int, float]],
    minvalue: Optional[Union[int, float]],
    maxvalue: Optional[Union[int, float]],
    parent: Optional[tk.Misc],
    icon_image: Optional["tk.PhotoImage"],
    value_type: type,
    error_title: str
) -> Optional[Union[int, float]]:
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
            root.destroy()


# endregion

# endregion
# region Dialog Classes
# region _AskStringDialog


class _AskStringDialog(tk.Toplevel):
    """Dialog for single string input.

    Parameters:
        parent: Parent window
        title: Dialog window title
        prompt: Text prompt displayed above the entry field
        initialvalue: Initial string value
        ok_text: OK button text
        cancel_text: Cancel button text
        icon_image: Optional window icon

    Returns:
        Entered string value or None if canceled
    """
    def __init__(self,
        parent: tk.Misc,
        title: Optional[str],
        prompt: str,
        initialvalue: Optional[str] = None,
        ok_text: str = "OK",
        cancel_text: str = "Cancel",
        icon_image: Optional["tk.PhotoImage"] = None
    ) -> None:
        super().__init__(parent)
        self.result: Optional[str] = None
        _setup_dialog_window(self, parent, title, icon_image)
        container = self._create_dialog_widgets(prompt, initialvalue)
        _create_general_dialog_buttons(self, ok_text, cancel_text, container)
        self._show_dialog(parent, initialvalue)


    def _create_dialog_widgets(self, prompt: str, initialvalue: Optional[str]) -> ttk.Frame:
        container = _create_container(self, prompt)
        self._var = tk.StringVar(value="" if initialvalue is None else str(initialvalue))
        entry_width = max(28, min(60, len(self._var.get()) + 12))
        self.entry = ttk.Entry(container, textvariable=self._var, width=entry_width)
        self.entry.grid(row=1, column=0, columnspan=2, sticky="ew")
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
    """Dialog for selecting from a dropdown list.

    Parameters:
        parent: Parent window
        title: Dialog window title
        prompt: Text prompt displayed above the combobox
        values: List of strings to populate the combobox
        initialvalue: Initial selection
        ok_text: OK button text
        cancel_text: Cancel button text
        icon_image: Optional window icon

    Returns:
        Selected string value or None if canceled
    """
    def __init__(self,
        parent: tk.Misc,
        title: Optional[str],
        prompt: str,
        values: list[str],
        initialvalue: Optional[str] = None,
        ok_text: str = "OK",
        cancel_text: str = "Cancel",
        icon_image: Optional["tk.PhotoImage"] = None
    ) -> None:
        super().__init__(parent)
        self.result: Optional[str] = None
        _setup_dialog_window(self, parent, title, icon_image)
        container = self._create_dialog_widgets(prompt, values)
        _create_general_dialog_buttons(self, ok_text, cancel_text, container)
        self._show_dialog(parent, initialvalue, values)


    def _create_dialog_widgets(self, prompt: str, values: list[str]) -> ttk.Frame:
        container = _create_container(self, prompt)
        self._var = tk.StringVar()
        combo_width = max(28, min(60, max(len(str(v)) for v in values) + 12))
        self.combo = ttk.Combobox(container, textvariable=self._var, values=values, width=combo_width, state="readonly")
        self.combo.grid(row=1, column=0, columnspan=2, sticky="ew")
        _bind_widget_cursor_hand2(self.combo)
        return container


    def _show_dialog(self, parent: Optional[tk.Misc], initialvalue: Optional[str], values: list[str]) -> None:
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
    """Dialog presenting radio button choices, with optional details.

    Parameters:
        parent: Parent window
        title: Dialog window title
        prompt: Text prompt displayed above the radio buttons
        values: Sequence of choices (string or tuple)
        initialvalue: Initial selection
        ok_text: OK button text
        cancel_text: Cancel button text
        icon_image: Optional window icon

    Returns:
        Selected value (string) or None if canceled
    """
    def __init__(
        self,
        parent: tk.Misc,
        title: Optional[str],
        prompt: str,
        values: Sequence[ChoiceValue],
        initialvalue: Optional[str] = None,
        ok_text: str = "OK",
        cancel_text: str = "Cancel",
        icon_image: Optional["tk.PhotoImage"] = None
    ) -> None:
        super().__init__(parent)
        self.result: Optional[str] = None
        _setup_dialog_window(self, parent, title, icon_image)
        container, first_radiobutton = self._create_dialog_widgets(prompt, values)
        _create_general_dialog_buttons(self, ok_text, cancel_text, container)
        self._show_dialog(parent, initialvalue, first_radiobutton)


    def _create_dialog_widgets(self, prompt: str, values: Sequence[ChoiceValue]) -> tuple[ttk.Frame, Optional[ttk.Radiobutton]]:
        container = _create_container(self, prompt)
        self._var = tk.StringVar()
        self._choices: list[str] = []
        radio_frame = ttk.Frame(container)
        radio_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        first_radiobutton: Optional[ttk.Radiobutton] = None
        for idx, choice in enumerate(values):
            if isinstance(choice, tuple):
                value = str(choice[0])
                label = str(choice[1]) if len(choice) > 1 else value
                detail = str(choice[2]) if len(choice) > 2 else None
            else:
                value = label = str(choice)
                detail = None
            self._choices.append(value)
            opt_frame = ttk.Frame(radio_frame)
            opt_frame.grid(row=idx, column=0, sticky="ew", pady=(0 if idx == 0 else 10, 0))
            opt_frame.columnconfigure(0, weight=1)
            btn = ttk.Radiobutton(opt_frame, text=label, value=value, variable=self._var)
            btn.grid(row=0, column=0, sticky="w", padx=(0, 0))
            _bind_widget_cursor_hand2(btn)
            if first_radiobutton is None:
                first_radiobutton = btn
            if detail:
                detail_lbl = ttk.Label(opt_frame, text=detail, anchor="w", justify="left", font=("TkDefaultFont", 9), foreground="gray", wraplength=400)
                detail_lbl.grid(row=1, column=0, sticky="w", padx=(28, 0))
                detail_lbl.bind("<Button-1>", lambda e, v=value: self._var.set(v))
                _bind_widget_cursor_hand2(detail_lbl)
        return container, first_radiobutton


    def _show_dialog(self, parent: Optional[tk.Misc], initialvalue: Optional[str], first_radiobutton: Optional[ttk.Radiobutton]) -> None:
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
# region _ConfirmDialog


class _ConfirmDialog(tk.Toplevel):
    """Dialog for confirmation-style prompts with configurable buttons.

    Parameters:
        parent: Parent window
        title: Dialog window title
        prompt: Text prompt displayed above the buttons
        detail: Optional detail text
        buttons: Sequence of (text, value, is_default) tuples
        cancel_value: Value to return if canceled
        icon_image: Optional window icon

    Returns:
        Selected value or cancel_value if canceled
    """
    def __init__(
        self,
        parent: tk.Misc,
        title: Optional[str],
        prompt: str,
        detail: Optional[str],
        buttons: Sequence[tuple[str, object, bool]],
        cancel_value: object,
        icon_image: Optional["tk.PhotoImage"] = None
    ) -> None:
        super().__init__(parent)
        self.result: object = cancel_value
        self._cancel_value = cancel_value
        self._default_value: object = cancel_value
        _setup_dialog_window(self, parent, title, icon_image)
        container = _create_container(self, prompt)
        row_index = 1
        if detail:
            detail_lbl = ttk.Label(container, text=detail, anchor="w", justify="left", wraplength=420, font=("TkDefaultFont", 9), foreground="gray50")
            detail_lbl.grid(row=row_index, column=0, columnspan=2, sticky="ew")
            row_index += 1
        button_defs = list(buttons)
        if not button_defs:
            raise ValueError("buttons sequence cannot be empty")
        default_widget = self._create_dialog_widgets(container, button_defs, row_index)
        self._show_dialog(parent, default_widget)


    def _create_dialog_widgets(
        self,
        container: ttk.Frame,
        buttons: list[tuple[str, object, bool]],
        row_index: int
    ) -> Optional[ttk.Button]:
        container.rowconfigure(row_index, weight=1)
        btn_frame = ttk.Frame(container)
        btn_frame.grid(row=row_index, column=0, columnspan=2, sticky="se")
        btn_frame.columnconfigure(0, weight=1)
        default_widget: Optional[ttk.Button] = None
        first_button: Optional[ttk.Button] = None
        for idx, (text, value, is_default) in enumerate(buttons):
            btn = ttk.Button(btn_frame, text=text, command=lambda v=value: self._finish(v))
            btn.grid(row=0, column=idx, padx=(0 if idx == 0 else 10, 0))
            _bind_widget_cursor_hand2(btn)
            if idx == 0:
                first_button = btn
            if is_default and default_widget is None:
                btn.configure(default="active")
                default_widget = btn
                self._default_value = value
        if default_widget is None and first_button is not None:
            first_button.configure(default="active")
            default_widget = first_button
            self._default_value = buttons[0][1]
        return default_widget


    def _show_dialog(self, parent: Optional[tk.Misc], default_widget: Optional[ttk.Button]) -> None:
        _center_window_to_parent(self, parent)
        self.deiconify()
        self.grab_set()
        if default_widget is not None:
            default_widget.focus_set()
        else:
            self.focus_set()


    def _finish(self, value: object) -> None:
        self.result = value
        self.destroy()


# endregion
# endregion
# region Public API


def askstring(
    title: Optional[str],
    prompt: str,
    initialvalue: Optional[str] = None,
    parent: Optional[tk.Misc] = None,
    icon_image: Optional["tk.PhotoImage"] = None
) -> Optional[str]:
    """Show a prompt dialog and return the entered string.

    Parameters:
        title: Dialog window title
        prompt: Text prompt displayed above the entry field
        initialvalue: Initial string value
        parent: Parent window
        icon_image: Optional window icon

    Returns:
        Entered string value or None if canceled
    """
    return _run_dialog(_AskStringDialog, title=title, prompt=prompt, initialvalue=initialvalue, parent=parent, icon_image=icon_image)


def askinteger(
    title: Optional[str],
    prompt: str,
    initialvalue: Optional[int] = None,
    minvalue: Optional[int] = None,
    maxvalue: Optional[int] = None,
    parent: Optional[tk.Misc] = None,
    icon_image: Optional["tk.PhotoImage"] = None
) -> Optional[int]:
    """Show a prompt dialog for integer input.

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


def askfloat(
    title: Optional[str],
    prompt: str,
    initialvalue: Optional[float] = None,
    minvalue: Optional[float] = None,
    maxvalue: Optional[float] = None,
    parent: Optional[tk.Misc] = None,
    icon_image: Optional["tk.PhotoImage"] = None
) -> Optional[float]:
    """Show a prompt dialog for float input.

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


def askcombo(
    title: Optional[str],
    prompt: str,
    values: list[str],
    initialvalue: Optional[str] = None,
    parent: Optional[tk.Misc] = None,
    icon_image: Optional["tk.PhotoImage"] = None
) -> Optional[str]:
    """Show a dialog with a combobox for selecting from predefined values.

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
    return _run_dialog(_AskComboDialog, title=title, prompt=prompt, values=values, initialvalue=initialvalue, parent=parent, icon_image=icon_image)


def askradio(
    title: Optional[str],
    prompt: str,
    values: Sequence[ChoiceValue],
    initialvalue: Optional[str] = None,
    parent: Optional[tk.Misc] = None,
    icon_image: Optional["tk.PhotoImage"] = None
) -> Optional[str]:
    """Show a dialog with radio buttons for selecting a single option.

    Parameters:
        title: Dialog window title
        prompt: Text prompt displayed above the radio buttons
        values: Sequence of choices, each can be:
            - a string (used as both value and label)
            - a tuple (value, label)
            - a tuple (value, label, detail)
        initialvalue: Value to be selected initially (must match one of the values)
        parent: Parent window
        icon_image: Optional window icon

    Returns:
        Selected value (string) or None if canceled
    """
    if not values:
        raise ValueError("values list cannot be empty")
    return _run_dialog(_AskRadioDialog, title=title, prompt=prompt, values=values, initialvalue=initialvalue, parent=parent, icon_image=icon_image)


def askyesno(
    title: Optional[str],
    prompt: str,
    detail: Optional[str] = None,
    parent: Optional[tk.Misc] = None,
    icon_image: Optional["tk.PhotoImage"] = None
) -> bool:
    """Show a yes/no dialog.

    Parameters:
        title: Dialog window title
        prompt: Text prompt displayed above the buttons
        detail: Optional detail text
        parent: Parent window
        icon_image: Optional window icon

    Returns:
        True for Yes, False for No or Cancel
    """
    result = _run_dialog(
        _ConfirmDialog,
        title=title,
        prompt=prompt,
        detail=detail,
        buttons=[("Yes", True, True), ("No", False, False)],
        cancel_value=False,
        parent=parent,
        icon_image=icon_image
    )
    return bool(result)


def askyesnocancel(
    title: Optional[str],
    prompt: str,
    detail: Optional[str] = None,
    parent: Optional[tk.Misc] = None,
    icon_image: Optional["tk.PhotoImage"] = None
) -> Optional[bool]:
    """Show a yes/no/cancel dialog.

    Parameters:
        title: Dialog window title
        prompt: Text prompt displayed above the buttons
        detail: Optional detail text
        parent: Parent window
        icon_image: Optional window icon

    Returns:
        True for Yes, False for No, None for Cancel
    """
    result = _run_dialog(
        _ConfirmDialog,
        title=title,
        prompt=prompt,
        detail=detail,
        buttons=[("Yes", True, True), ("No", False, False), ("Cancel", None, False)],
        cancel_value=None,
        parent=parent,
        icon_image=icon_image
    )
    return result if isinstance(result, bool) or result is None else None


def showinfo(
    title: Optional[str],
    prompt: str,
    detail: Optional[str] = None,
    parent: Optional[tk.Misc] = None,
    icon_image: Optional["tk.PhotoImage"] = None
) -> None:
    """Show an info dialog with an acknowledgment button.

    Parameters:
        title: Dialog window title
        prompt: Text prompt displayed above the button
        detail: Optional detail text
        parent: Parent window
        icon_image: Optional window icon

    Returns:
        None
    """
    _run_dialog(
        _ConfirmDialog,
        title=title or "Info",
        prompt=prompt,
        detail=detail,
        buttons=[("OK", None, True)],
        cancel_value=None,
        parent=parent,
        icon_image=icon_image
    )


# endregion
# region Test Block


if __name__ == "__main__":
    def test_askstring():
        val = askstring("askstring", "Enter a value:", initialvalue="Hello")
        print("String result:", repr(val))


    def test_askinteger():
        val = askinteger("askinteger", "Enter a value (10-100):", initialvalue=42, minvalue=10, maxvalue=100)
        print("Integer result:", repr(val))


    def test_askfloat():
        val = askfloat("askfloat", "Enter a float value (0.0 - 1.0):", initialvalue=0.5, minvalue=0.0, maxvalue=1.0)
        print("Float result:", repr(val))


    def test_askcombo():
        colors = ["Red", "Green", "Blue", "Yellow", "Purple", "Orange"]
        selected_color = askcombo("askcombo", "Choose your favorite color:", colors, initialvalue="Blue")
        print("Selected color:", repr(selected_color))


    def test_askradio():
        radio_options = [
            ("return_val1", "display_label1"),
            ("return_val2", "display_label2", ("detail2. " * 5)),
            ("return_val3", "display_label3", ("detail3. " * 10)),
            ("return_val4", "display_label4", ("detail4. " * 20)),
        ]
        selected_radio = askradio("askradio", "Choose an option:", radio_options, initialvalue="return_val1")
        print("Selected radio option:", repr(selected_radio))


    def test_askyesno():
        result = askyesno("askyesno", "Do you want to proceed?", "This action cannot be undone.")
        print("Yes/No result:", result)


    def test_askyesnocancel():
        result = askyesnocancel("askyesnocancel", "Do you want to save changes?", "Your changes will be lost if you don't save.")
        print("Yes/No/Cancel result:", result)


    def test_showinfo():
        showinfo("showinfo", "This is an info message.", "Additional details can go here.")


    test_askstring()
    test_askinteger()
    test_askfloat()
    test_askcombo()
    test_askradio()
    test_askyesno()
    test_askyesnocancel()
    test_showinfo()


# endregion
