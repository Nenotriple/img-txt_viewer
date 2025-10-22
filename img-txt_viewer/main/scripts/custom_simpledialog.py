"""
custom_simpledialog — simple, standalone dialogs using Tk/Ttk.

Purpose:
- Minimal, dependency-free replacements for common tkinter.simpledialog dialogs.
- Uses Toplevel and ttk widgets; returns Python values or None when cancelled.

Public API:
- askstring(title, prompt, initialvalue=None, detail=None, parent=None, icon_image=None) -> Optional[str]
- askinteger(title, prompt, initialvalue=None, minvalue=None, maxvalue=None, detail=None, parent=None, icon_image=None) -> Optional[int]
- askfloat(title, prompt, initialvalue=None, minvalue=None, maxvalue=None, detail=None, parent=None, icon_image=None) -> Optional[float]
- askcombo(title, prompt, values, initialvalue=None, detail=None, parent=None, icon_image=None) -> Optional[str]
- askradio(title, prompt, values, initialvalue=None, parent=None, icon_image=None) -> Optional[str]
- askyesno(title, prompt, detail=None, parent=None, icon_image=None) -> bool
- askyesnocancel(title, prompt, detail=None, parent=None, icon_image=None) -> Optional[bool]
- showinfo(title, prompt, detail=None, parent=None, icon_image=None) -> None
- showprogress(title, prompt, task_function, args=(), kwargs=None, max_value=100, parent=None, icon_image=None, auto_close=True) -> Any
- confirmpath(title, prompt, path, detail=None, parent=None, icon_image=None) -> tuple[Optional[bool], Optional[str]]

Notes:
- askstring, askinteger, askfloat, and askcombo support a 'detail' argument for helper text below the prompt.
- askradio accepts a sequence of choices. Each choice may be:
    - a string (used as both value and label)
    - a tuple (value, label)
    - a tuple (value, label, detail) — detail is displayed below the label
- All dialogs return the chosen or entered value, or None if cancelled.
- If no parent is provided, a temporary root window is created and destroyed after the dialog.
- Not designed for multi-threaded GUI usage.

Example:
    val = askstring("Name", "Enter your name:", initialvalue="Alice", detail="Your name will be used for personalization.")
    num = askinteger("Count", "Enter a number:", initialvalue=5, minvalue=1, maxvalue=10, detail="Choose a number between 1 and 10.")
"""

# region Imports


from __future__ import annotations

import threading
import queue

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from typing import Optional, Sequence, Union, Callable, Any

# endregion
# region Constants


__all__ = ["askstring", "askinteger", "askfloat", "askcombo", "askradio", "askyesno", "askyesnocancel", "showinfo", "showprogress", "confirmpath"]
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
    # Find the last used row in the container
    last_row = max([child.grid_info()["row"] for child in container.winfo_children()])
    btn_frame = ttk.Frame(container)
    btn_frame.grid(row=last_row + 1, column=0, columnspan=2, sticky="e", pady=(0, 0), padx=(0, 0))
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
    error_title: str,
    detail: Optional[str] = None
) -> Optional[Union[int, float]]:
    root, created = _get_or_create_root(parent)
    try:
        current = str(initialvalue) if initialvalue is not None else None
        while True:
            input_string = askstring(title, prompt, initialvalue=current, detail=detail, parent=root, icon_image=icon_image)
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
        detail: Optional detail text displayed below the prompt
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
        detail: Optional[str] = None,
        ok_text: str = "OK",
        cancel_text: str = "Cancel",
        icon_image: Optional["tk.PhotoImage"] = None
    ) -> None:
        super().__init__(parent)
        self.result: Optional[str] = None
        _setup_dialog_window(self, parent, title, icon_image)
        container = self._create_dialog_widgets(prompt, detail, initialvalue)
        _create_general_dialog_buttons(self, ok_text, cancel_text, container)
        self._show_dialog(parent, initialvalue)


    def _create_dialog_widgets(self, prompt: str, detail: Optional[str], initialvalue: Optional[str]) -> ttk.Frame:
        container = _create_container(self, prompt)
        row_index = 1
        if detail:
            detail_lbl = ttk.Label(container, text=detail, anchor="w", justify="left", wraplength=420, font=("TkDefaultFont", 9), foreground="gray50")
            detail_lbl.grid(row=row_index, column=0, columnspan=2, sticky="ew", pady=(0, 8))
            row_index += 1
        self._var = tk.StringVar(value="" if initialvalue is None else str(initialvalue))
        entry_width = max(28, min(60, len(self._var.get()) + 12))
        self.entry = ttk.Entry(container, textvariable=self._var, width=entry_width)
        self.entry.grid(row=row_index, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        # Move buttons to next row after entry
        container.rowconfigure(row_index + 1, weight=1)
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
        detail: Optional detail text displayed below the prompt
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
        detail: Optional[str] = None,
        ok_text: str = "OK",
        cancel_text: str = "Cancel",
        icon_image: Optional["tk.PhotoImage"] = None
    ) -> None:
        super().__init__(parent)
        self.result: Optional[str] = None
        _setup_dialog_window(self, parent, title, icon_image)
        container = self._create_dialog_widgets(prompt, detail, values)
        _create_general_dialog_buttons(self, ok_text, cancel_text, container)
        self._show_dialog(parent, initialvalue, values)


    def _create_dialog_widgets(self, prompt: str, detail: Optional[str], values: list[str]) -> ttk.Frame:
        container = _create_container(self, prompt)
        row_index = 1
        if detail:
            detail_lbl = ttk.Label(container, text=detail, anchor="w", justify="left", wraplength=420, font=("TkDefaultFont", 9), foreground="gray50")
            detail_lbl.grid(row=row_index, column=0, columnspan=2, sticky="ew", pady=(0, 8))
            row_index += 1
        self._var = tk.StringVar()
        combo_width = max(28, min(60, max(len(str(v)) for v in values) + 12))
        self.combo = ttk.Combobox(container, textvariable=self._var, values=values, width=combo_width, state="readonly")
        self.combo.grid(row=row_index, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        _bind_widget_cursor_hand2(self.combo)
        # Move buttons to next row after combobox
        container.rowconfigure(row_index + 1, weight=1)
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
# region _ProgressDialog


class _ProgressDialog(tk.Toplevel):
    """Dialog for displaying progress of long-running tasks with threading support.

    Parameters:
        parent: Parent window
        title: Dialog window title
        prompt: Text prompt displayed above the progress bar
        task_function: The function to execute in background thread
        args: Positional arguments for task_function
        kwargs: Keyword arguments for task_function
        max_value: Maximum progress value (default 100)
        icon_image: Optional window icon
        auto_close: Whether to automatically close on completion

    The task_function will receive a 'progress_callback' keyword argument that can be called with:
        progress_callback(value, message=None, detail=None)
    """
    def __init__(
        self,
        parent: tk.Misc,
        title: Optional[str],
        prompt: str,
        task_function: Callable,
        args: tuple = (),
        kwargs: Optional[dict] = None,
        max_value: int = 100,
        icon_image: Optional["tk.PhotoImage"] = None,
        auto_close: bool = True
    ) -> None:
        super().__init__(parent)
        self.result: Optional[Any] = None
        self._task_function = task_function
        self._task_args = args
        self._task_kwargs = kwargs or {}
        self._max_value = max_value
        self._auto_close = auto_close
        self._cancelled = threading.Event()
        self._queue: queue.Queue = queue.Queue()
        self._thread: Optional[threading.Thread] = None


        _setup_dialog_window(self, parent, title or "Processing", icon_image)
        self.protocol("WM_DELETE_WINDOW", self._on_close_attempt)
        container = self._create_dialog_widgets(prompt)
        self._show_dialog(parent)
        # Start background thread
        self._thread = threading.Thread(target=self._run_task, daemon=True)
        self._thread.start()
        # Begin polling queue
        self._check_queue()


    def _create_dialog_widgets(self, prompt: str) -> ttk.Frame:
        container = _create_container(self, prompt)
        # Progress bar
        self._progress_bar = ttk.Progressbar(container, maximum=self._max_value, length=400, mode="determinate")
        self._progress_bar.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        # Status label
        self._status_label = ttk.Label(container, text="Starting...", anchor="w", justify="left")
        self._status_label.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 4))
        # Detail label (smaller, gray text)
        self._detail_label = ttk.Label(container, text="", anchor="w", justify="left", font=("TkDefaultFont", 9), foreground="gray50", wraplength=400)
        self._detail_label.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        # Cancel button
        btn_frame = ttk.Frame(container)
        btn_frame.grid(row=4, column=0, columnspan=2, sticky="e")
        self._cancel_btn = ttk.Button(btn_frame, text="Cancel", command=self._on_cancel)
        self._cancel_btn.grid(row=0, column=0)
        _bind_widget_cursor_hand2(self._cancel_btn)
        return container


    def _show_dialog(self, parent: Optional[tk.Misc]) -> None:
        _center_window_to_parent(self, parent)
        self.deiconify()
        self.grab_set()
        self.focus_set()


    def _run_task(self) -> None:
        """Execute the task in the background thread."""
        try:
            # Inject progress callback into task
            def progress_callback(value: Union[int, float], message: Optional[str] = None, detail: Optional[str] = None) -> None:
                if self._cancelled.is_set():
                    raise InterruptedError("Task cancelled by user")
                self._queue.put(("progress", value, message, detail))
            # Add progress_callback to kwargs
            task_kwargs = self._task_kwargs.copy()
            task_kwargs["progress_callback"] = progress_callback
            # Execute task
            result = self._task_function(*self._task_args, **task_kwargs)
            # Send completion message
            self._queue.put(("done", result))
        except InterruptedError:
            self._queue.put(("cancelled", None))
        except Exception as e:
            self._queue.put(("error", str(e)))


    def _check_queue(self) -> None:
        """Process messages from the worker thread."""
        try:
            while True:
                msg = self._queue.get_nowait()
                self._handle_message(msg)
        except queue.Empty:
            pass
        # Continue polling if thread is alive
        if self._thread and self._thread.is_alive():
            self.after(100, self._check_queue)


    def _handle_message(self, msg: tuple) -> None:
        """Handle messages from the background thread."""
        msg_type = msg[0]
        if msg_type == "progress":
            _, value, message, detail = msg
            self._update_progress(value, message, detail)
        elif msg_type == "done":
            _, result = msg
            self.result = result
            self._progress_bar["value"] = self._max_value
            self._status_label.config(text="Completed!")
            self._detail_label.config(text="")
            self._cancel_btn.config(state="disabled")
            if self._auto_close:
                self.after(800, self.destroy)
            else:
                self._cancel_btn.config(text="Close", state="normal", command=self.destroy)
        elif msg_type == "cancelled":
            self._status_label.config(text="Cancelled by user")
            self._detail_label.config(text="")
            self._cancel_btn.config(state="disabled")
            if self._auto_close:
                self.after(800, self.destroy)
            else:
                self._cancel_btn.config(text="Close", state="normal", command=self.destroy)
        elif msg_type == "error":
            _, error_msg = msg
            self._status_label.config(text="Error occurred")
            self._detail_label.config(text=error_msg, foreground="red")
            self._cancel_btn.config(text="Close", state="normal", command=self.destroy)


    def _update_progress(self, value: Union[int, float], message: Optional[str], detail: Optional[str]) -> None:
        """Update progress bar and labels."""
        self._progress_bar["value"] = value
        if message is not None:
            self._status_label.config(text=message)
        if detail is not None:
            self._detail_label.config(text=detail)


    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        self._cancelled.set()
        self._status_label.config(text="Cancelling...")
        self._detail_label.config(text="")
        self._cancel_btn.config(state="disabled")


    def _on_close_attempt(self) -> None:
        """Handle window close attempt."""
        if self._thread and self._thread.is_alive() and not self._cancelled.is_set():
            self._status_label.config(text="Task still running...")
        else:
            self.destroy()


# endregion
# region _ConfirmPathDialog


class _ConfirmPathDialog(tk.Toplevel):
    """Dialog for path confirmation with ability to change the path.

    Parameters:
        parent: Parent window
        title: Dialog window title
        prompt: Text prompt displayed above the path
        path: Initial path to confirm
        detail: Optional detail text
        icon_image: Optional window icon

    Returns:
        Tuple of (confirmation: Optional[bool], path: Optional[str])
        - (True, path) if OK clicked
        - (False, None) if Cancel clicked
        - (None, None) if window closed
    """
    def __init__(
        self,
        parent: tk.Misc,
        title: Optional[str],
        prompt: str,
        path: str,
        detail: Optional[str],
        icon_image: Optional["tk.PhotoImage"] = None
    ) -> None:
        super().__init__(parent)
        self.result: tuple[Optional[bool], Optional[str]] = (None, None)
        self._current_path = path
        self._initial_path = path

        _setup_dialog_window(self, parent, title, icon_image)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        container = _create_container(self, prompt)
        row_index = 1
        if detail:
            detail_lbl = ttk.Label(container, text=detail, anchor="w", justify="left", wraplength=420, font=("TkDefaultFont", 9), foreground="gray50")
            detail_lbl.grid(row=row_index, column=0, columnspan=2, sticky="ew", pady=(0, 8))
            row_index += 1
        # Path display
        path_frame = ttk.Frame(container)
        path_frame.grid(row=row_index, column=0, columnspan=2, sticky="ew", pady=(0, 16))
        path_frame.columnconfigure(0, weight=1)
        path_label = ttk.Label(path_frame, text="Path:", anchor="w", font=("TkDefaultFont", 9, "bold"))
        path_label.grid(row=0, column=0, sticky="w", pady=(0, 4))
        self._path_display = ttk.Label(path_frame, text=self._current_path, anchor="w", justify="left", relief="solid", borderwidth=2, padding=(6, 4), wraplength=400)
        self._path_display.grid(row=1, column=0, sticky="ew")
        self._path_display.bind("<Button-1>", self._copy_path_to_clipboard)
        _bind_widget_cursor_hand2(self._path_display)
        row_index += 1
        # Buttons
        self._create_buttons(container, row_index)
        self._show_dialog(parent)


    def _create_buttons(self, container: ttk.Frame, row_index: int) -> None:
        container.rowconfigure(row_index, weight=1)
        btn_frame = ttk.Frame(container)
        btn_frame.grid(row=row_index, column=0, columnspan=2, sticky="se")
        ok_btn = ttk.Button(btn_frame, text="OK", command=self._on_ok, default="active")
        ok_btn.grid(row=0, column=0, padx=(0, 10))
        _bind_widget_cursor_hand2(ok_btn)
        change_btn = ttk.Button(btn_frame, text="Change Path", command=self._on_change_path)
        change_btn.grid(row=0, column=1, padx=(0, 10))
        _bind_widget_cursor_hand2(change_btn)
        cancel_btn = ttk.Button(btn_frame, text="Cancel", command=self._on_cancel)
        cancel_btn.grid(row=0, column=2)
        _bind_widget_cursor_hand2(cancel_btn)
        self._ok_btn = ok_btn


    def _show_dialog(self, parent: Optional[tk.Misc]) -> None:
        _center_window_to_parent(self, parent)
        self.deiconify()
        self.grab_set()
        self._ok_btn.focus_set()


    def _on_ok(self) -> None:
        self.result = (True, self._current_path)
        self.destroy()


    def _on_cancel(self) -> None:
        self.result = (False, None)
        self.destroy()


    def _on_close(self) -> None:
        self.result = (None, None)
        self.destroy()


    def _on_change_path(self) -> None:
        new_path = filedialog.askdirectory(title="Select Directory", initialdir=self._current_path, parent=self)
        if new_path:
            self._current_path = new_path
            self._path_display.config(text=self._current_path)


    def _copy_path_to_clipboard(self, event=None):
        self.clipboard_clear()
        self.clipboard_append(self._current_path)
        original_text = self._current_path
        self._path_display.config(text="Copied!", relief="sunken", borderwidth=2, anchor="center")
        self.after(250, lambda: self._path_display.config(text=original_text, relief="solid", borderwidth=1, anchor="w"))


# endregion
# endregion
# region Public API


def askstring(
    title: Optional[str],
    prompt: str,
    initialvalue: Optional[str] = None,
    detail: Optional[str] = None,
    parent: Optional[tk.Misc] = None,
    icon_image: Optional["tk.PhotoImage"] = None
) -> Optional[str]:
    """Show a prompt dialog and return the entered string.

    Parameters:
        title: Dialog window title
        prompt: Text prompt displayed above the entry field
        initialvalue: Initial string value
        detail: Optional detail text displayed below the prompt
        parent: Parent window
        icon_image: Optional window icon

    Returns:
        Entered string value or None if canceled
    """
    return _run_dialog(_AskStringDialog, title=title, prompt=prompt, initialvalue=initialvalue, detail=detail, parent=parent, icon_image=icon_image)


def askinteger(
    title: Optional[str],
    prompt: str,
    initialvalue: Optional[int] = None,
    minvalue: Optional[int] = None,
    maxvalue: Optional[int] = None,
    detail: Optional[str] = None,
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
        detail: Optional detail text displayed below the prompt
        parent: Parent window
        icon_image: Optional window icon

    Returns:
        Entered integer value or None if canceled
    """
    return _ask_number(title, prompt, initialvalue, minvalue, maxvalue, parent, icon_image, int, "Invalid integer", detail)


def askfloat(
    title: Optional[str],
    prompt: str,
    initialvalue: Optional[float] = None,
    minvalue: Optional[float] = None,
    maxvalue: Optional[float] = None,
    detail: Optional[str] = None,
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
        detail: Optional detail text displayed below the prompt
        parent: Parent window
        icon_image: Optional window icon

    Returns:
        Entered float value or None if canceled
    """
    return _ask_number(title, prompt, initialvalue, minvalue, maxvalue, parent, icon_image, float, "Invalid number", detail)


def askcombo(
    title: Optional[str],
    prompt: str,
    values: list[str],
    initialvalue: Optional[str] = None,
    detail: Optional[str] = None,
    parent: Optional[tk.Misc] = None,
    icon_image: Optional["tk.PhotoImage"] = None
) -> Optional[str]:
    """Show a dialog with a combobox for selecting from predefined values.

    Parameters:
        title: Dialog window title
        prompt: Text prompt displayed above the combobox
        values: List of strings to populate the combobox
        initialvalue: Initial selection (must be in values list)
        detail: Optional detail text displayed below the prompt
        parent: Parent window
        icon_image: Optional window icon

    Returns:
        Selected string value or None if canceled
    """
    if not values:
        raise ValueError("values list cannot be empty")
    return _run_dialog(_AskComboDialog, title=title, prompt=prompt, values=values, initialvalue=initialvalue, detail=detail, parent=parent, icon_image=icon_image)


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


def showprogress(
    title: Optional[str],
    prompt: str,
    task_function: Callable,
    args: tuple = (),
    kwargs: Optional[dict] = None,
    max_value: int = 100,
    parent: Optional[tk.Misc] = None,
    icon_image: Optional["tk.PhotoImage"] = None,
    auto_close: bool = True
) -> Any:
    """Show a progress dialog and execute a task in a background thread.

    The task_function will be called with a 'progress_callback' keyword argument that
    can be used to update the progress display:
        progress_callback(value, message=None, detail=None)

    The task can check for cancellation by catching InterruptedError, which will be
    raised when the user clicks Cancel.

    Parameters:
        title: Dialog window title
        prompt: Text prompt displayed above the progress bar
        task_function: Callable to execute in background thread
        args: Positional arguments for task_function
        kwargs: Keyword arguments for task_function (progress_callback will be added)
        max_value: Maximum progress value (default 100)
        parent: Parent window
        icon_image: Optional window icon
        auto_close: If True, dialog closes automatically on completion (default True)

    Returns:
        The return value of task_function, or None if cancelled or error occurred

    Example:
    ```
        def my_task(items, progress_callback):
            for i, item in enumerate(items):
                process(item)
                progress_callback(i + 1, f"Processing {item}", f"Item {i+1} of {len(items)}")
            return "Done"

        result = showprogress("Processing", "Please wait...", my_task, args=([1,2,3,4,5],), max_value=5)
    ```
    """
    return _run_dialog(
        _ProgressDialog,
        title=title,
        prompt=prompt,
        task_function=task_function,
        args=args,
        kwargs=kwargs,
        max_value=max_value,
        parent=parent,
        icon_image=icon_image,
        auto_close=auto_close
    )


def confirmpath(
    title: Optional[str],
    prompt: str,
    path: str,
    detail: Optional[str] = None,
    parent: Optional[tk.Misc] = None,
    icon_image: Optional["tk.PhotoImage"] = None
) -> tuple[Optional[bool], Optional[str]]:
    """Show a path confirmation dialog with option to change the path.

    Parameters:
        title: Dialog window title
        prompt: Text prompt displayed above the path
        path: Initial path to confirm
        detail: Optional detail text
        parent: Parent window
        icon_image: Optional window icon

    Returns:
        Tuple of (confirmation, path):
        - (True, path) if OK clicked
        - (False, None) if Cancel clicked
        - (None, None) if window closed

    Example:
    ```
        confirmed, output_path = confirmpath("Confirm Output Location",
            "Save files to:",
            "C:\\docs\\output",
            detail="Confirm or change now."
        )
        if confirmed:
            print(f"Saving to: {output_path}")
    ```
    """
    result = _run_dialog(
        _ConfirmPathDialog,
        title=title or "Confirm Path",
        prompt=prompt,
        path=path,
        detail=detail,
        parent=parent,
        icon_image=icon_image
    )
    return result if result is not None else (None, None)


# endregion
# region Test Block


if __name__ == "__main__":
    def test_askstring():
        val = askstring("askstring", "Value:", initialvalue="Hi", detail="detail")
        print("String:", repr(val))

    def test_askinteger():
        val = askinteger("askinteger", "Num (1-9):", initialvalue=4, minvalue=1, maxvalue=9, detail="detail")
        print("Integer:", repr(val))

    def test_askfloat():
        val = askfloat("askfloat", "Float (0-1):", initialvalue=0.5, minvalue=0.0, maxvalue=1.0, detail="detail")
        print("Float:", repr(val))

    def test_askcombo():
        opts = ["Red", "Green", "Blue"]
        val = askcombo("askcombo", "Pick:", opts, initialvalue="Blue", detail="detail")
        print("Combo:", repr(val))

    def test_askradio():
        opts = [("v1", "A"), ("v2", "B", "d2"), ("v3", "C", "d3")]
        val = askradio("askradio", "Choose:", opts, initialvalue="v1")
        print("Radio:", repr(val))

    def test_askyesno():
        print("YesNo:", askyesno("askyesno", "Proceed?", "detail"))

    def test_askyesnocancel():
        print("Y/N/C:", askyesnocancel("askyesnocancel", "Save?", "detail"))

    def test_showinfo():
        showinfo("showinfo", "Info", "detail")

    def test_showprogress():
        import time

        def task(duration, count, progress_callback):
            for i in range(1, count + 1):
                time.sleep(duration / count)
                progress_callback(i, f"{i}/{count}", f"{i*100/count:.0f}%")
            return "ok"

        print("Progress:", showprogress("showprogress", "Wait...", task, args=(1, 5), max_value=5, auto_close=True))

    def test_confirmpath():
        import os
        p = os.path.expanduser("~\\Documents")
        confirmed, sel = confirmpath("confirmpath", "Confirm path", path=p, detail="detail")
        print("Confirm:", confirmed, repr(sel))

    #test_askstring()
    #test_askinteger()
    #test_askfloat()
    #test_askcombo()
    #test_askradio()
    #test_askyesno()
    #test_askyesnocancel()
    #test_showinfo()
    #test_showprogress()
    test_confirmpath()


# endregion
