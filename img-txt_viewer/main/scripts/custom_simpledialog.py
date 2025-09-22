"""
A minimal, standalone simpledialog-like module using Tkinter Toplevel and ttk.

API:
- askstring(title, prompt, initialvalue=None, parent=None, show=None, icon_image=None) -> Optional[str]
"""


from __future__ import annotations


import tkinter as tk
from tkinter import ttk
from typing import Optional


__all__ = ["askstring"]


class _AskStringDialog(tk.Toplevel):
	"""A modal dialog asking for a single string input."""

	def __init__(
		self,
		parent: tk.Misc,
		title: Optional[str],
		prompt: str,
		initialvalue: Optional[str] = None,
		show: Optional[str] = None,
		ok_text: str = "OK",
		cancel_text: str = "Cancel",
		icon_image: Optional["tk.PhotoImage"] = None,
	) -> None:

		super().__init__(parent)
		self.withdraw()
		self.result: Optional[str] = None

		# Window setup
		self.title(title or "")
		self.resizable(False, False)
		if icon_image is not None:
			try:
				self.iconphoto(False, icon_image)
			except Exception:
				pass
		if parent:
			try:
				self.transient(parent)
			except Exception:
				pass
		self.protocol("WM_DELETE_WINDOW", self._on_cancel)

		# Layout
		container = ttk.Frame(self, padding=(12, 10))
		container.grid(row=0, column=0, sticky="nsew")
		self.columnconfigure(0, weight=1)
		self.rowconfigure(0, weight=1)
		container.columnconfigure(0, weight=1)

		lbl = ttk.Label(container, text=prompt, anchor="w", justify="left")
		lbl.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))

		self._var = tk.StringVar(value="" if initialvalue is None else str(initialvalue))
		entry_width = max(24, min(60, len(self._var.get()) + 10))
		self.entry = ttk.Entry(container, textvariable=self._var, width=entry_width)
		if show:
			self.entry.configure(show=show)
		self.entry.grid(row=1, column=0, columnspan=2, sticky="ew")

		btns = ttk.Frame(container)
		btns.grid(row=2, column=0, columnspan=2, sticky="e", pady=(10, 0))
		ok_btn = ttk.Button(btns, text=ok_text, command=self._on_ok, default="active")
		cancel_btn = ttk.Button(btns, text=cancel_text, command=self._on_cancel)
		ok_btn.grid(row=0, column=0, padx=(0, 6))
		cancel_btn.grid(row=0, column=1)

		# Key bindings
		self.bind("<Return>", lambda e: self._on_ok())
		self.bind("<KP_Enter>", lambda e: self._on_ok())
		self.bind("<Escape>", lambda e: self._on_cancel())

		# Show
		self._center_to_parent(parent)
		self.deiconify()
		self.grab_set()
		self.entry.focus_set()
		if initialvalue:
			self.entry.selection_range(0, tk.END)
			self.entry.icursor(tk.END)


	def _center_to_parent(self, parent: Optional[tk.Misc]) -> None:
		self.update_idletasks()
		w = self.winfo_reqwidth()
		h = self.winfo_reqheight()
		try:
			if parent and parent.winfo_ismapped():
				px, py = parent.winfo_rootx(), parent.winfo_rooty()
				pw, ph = parent.winfo_width(), parent.winfo_height()
				x = px + max(0, (pw - w) // 2)
				y = py + max(0, (ph - h) // 2)
			else:
				sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
				x = max(0, (sw - w) // 2)
				y = max(0, (sh - h) // 3)
		except Exception:
			sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
			x = max(0, (sw - w) // 2)
			y = max(0, (sh - h) // 3)
		self.geometry(f"+{x}+{y}")


	def _on_ok(self) -> None:
		self.result = self._var.get()
		self.destroy()


	def _on_cancel(self) -> None:
		self.result = None
		self.destroy()


def askstring(
	title: Optional[str],
	prompt: str,
	initialvalue: Optional[str] = None,
	parent: Optional[tk.Misc] = None,
	show: Optional[str] = None,
	icon_image: Optional["tk.PhotoImage"] = None,
) -> Optional[str]:
	"""
	Show a modal prompt dialog and return the entered string, or None if canceled.

	Parameters mirror tkinter.simpledialog.askstring for easier drop-in use.

	icon_image: Optional[tk.PhotoImage]
		If provided, sets the Toplevel window icon.
	"""
	created_root = False
	root: Optional[tk.Misc] = parent
	if root is None:
		# Try to reuse default root if available; otherwise create a temporary one.
		root = tk._get_default_root()  # type: ignore[attr-defined]
		if root is None:
			root = tk.Tk()
			created_root = True
			try:
				root.withdraw()
			except Exception:
				pass
	dlg = _AskStringDialog(
		parent=root,
		title=title,
		prompt=prompt,
		initialvalue=initialvalue,
		show=show,
		icon_image=icon_image,
	)
	dlg.wait_window()
	res = dlg.result
	if created_root and root:
		try:
			root.destroy()
		except Exception:
			pass
	return res


if __name__ == "__main__":
	# Minimal manual test when running this file directly.
	# Example usage with icon (requires PIL.ImageTk and a valid image):
	# from PIL import Image, ImageTk
	# img = Image.open("icon.png")
	# icon = ImageTk.PhotoImage(img)
	# val = askstring("Input required", "Enter a value:", initialvalue="Hello", icon_image=icon)
	val = askstring("Input required", "Enter a value:", initialvalue="Hello")
	print("Result:", repr(val))