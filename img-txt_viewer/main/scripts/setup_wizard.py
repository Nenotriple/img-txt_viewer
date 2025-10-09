#region Imports


from tkinter import ttk, Toplevel, StringVar, BooleanVar, Frame, Label
from abc import ABC, abstractmethod

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .settings_manager import SettingsManager


#endregion
#region SetupPage


class SetupPage(ABC):
	def __init__(self, wizard: 'SetupWizard'):
		self.wizard = wizard


	@abstractmethod
	def render(self, container: Frame) -> None:
		pass


	@abstractmethod
	def on_enter(self) -> None:
		pass


	@abstractmethod
	def on_exit(self, direction: str) -> bool:
		pass


#endregion
#region DictionarySelectionPage


class DictionarySelectionPage(SetupPage):
	def __init__(self, wizard: 'SetupWizard'):
		super().__init__(wizard)
		self.dictionary_vars = {
			"English Dictionary": BooleanVar(value=True),
			"Danbooru": BooleanVar(),
			"Danbooru (Safe)": BooleanVar(),
			"e621": BooleanVar(),
			"Derpibooru": BooleanVar()
		}
		self.trace_ids = {"Danbooru": None, "Danbooru (Safe)": None}
		self.danbooru_checkbutton = None
		self.danbooru_safe_checkbutton = None


	def render(self, container: Frame) -> None:
		vars = self.dictionary_vars
		# Top
		top_frame = Frame(container)
		top_frame.pack(side="top", fill="x", pady=5)
		Label(top_frame, text="Please select your preferred autocomplete dictionaries").pack(pady=5)
		ttk.Separator(top_frame, orient="horizontal").pack(fill="x", pady=5)
        # Middle
		mid_frame = Frame(container)
		mid_frame.pack(side="top", fill="both", expand=True, pady=5)
		group_top = Frame(mid_frame)
		group_top.pack(pady=(10, 0), anchor="w")
		ttk.Checkbutton(group_top, text="English Dictionary", variable=vars["English Dictionary"]).pack(side="top", anchor="w", pady=2)
		Label(group_top, text="(~113k tags) General English words for natural language tags, including common typo corrections.", wraplength=400, justify="left", font=("Arial", 8, "italic"), fg="#555").pack(side="top", anchor="w", padx=(20, 0))
		self.danbooru_safe_checkbutton = ttk.Checkbutton(group_top, text="Danbooru (Safe)", variable=vars["Danbooru (Safe)"])
		self.danbooru_safe_checkbutton.pack(side="top", anchor="w", pady=2)
		Label(group_top, text="(~56k tags) Safe-for-work anime tags from Danbooru, including common typo corrections.", wraplength=400, justify="left", font=("Arial", 8, "italic"), fg="#555").pack(side="top", anchor="w", padx=(20, 0))
		ttk.Separator(mid_frame, orient="horizontal").pack(pady=10)
		group_bottom = Frame(mid_frame)
		group_bottom.pack(pady=(0, 10), anchor="w")
		self.danbooru_checkbutton = ttk.Checkbutton(group_bottom, text="Danbooru", variable=vars["Danbooru"])
		self.danbooru_checkbutton.pack(side="top", anchor="w", pady=2)
		Label(group_bottom, text="(~100k tags) Unfiltered tags from Danbooru, an anime image-board, including common typo corrections. (NSFW)", wraplength=400, justify="left", font=("Arial", 8, "italic"), fg="#555").pack(side="top", anchor="w", padx=(20, 0))
		ttk.Checkbutton(group_bottom, text="e621", variable=vars["e621"]).pack(side="top", anchor="w", pady=2)
		Label(group_bottom, text="(~100k tags) Unfiltered tags from e621, a furry image board, including common typo corrections. (NSFW)", wraplength=400, justify="left", font=("Arial", 8, "italic"), fg="#555").pack(side="top", anchor="w", padx=(20, 0))
		ttk.Checkbutton(group_bottom, text="Derpibooru", variable=vars["Derpibooru"]).pack(side="top", anchor="w", pady=2)
		Label(group_bottom, text="(~95k tags) Unfiltered tags from Derpibooru, a My Little Pony image board. (NSFW)", wraplength=400, justify="left", font=("Arial", 8, "italic"), fg="#555").pack(side="top", anchor="w", padx=(20, 0))
        # Logic
		self._attach_traces()
		self._toggle_danbooru()
		self._toggle_danbooru_safe()


	def on_enter(self) -> None:
		pass


	def on_exit(self, direction: str) -> bool:
		self._detach_traces()
		app = self.wizard.app
		vars = self.dictionary_vars
		app.csv_english_dictionary.set(vars["English Dictionary"].get())
		app.csv_danbooru.set(vars["Danbooru"].get())
		app.csv_danbooru_safe.set(vars["Danbooru (Safe)"].get())
		app.csv_e621.set(vars["e621"].get())
		app.csv_derpibooru.set(vars["Derpibooru"].get())
		if direction == "next":
			self.wizard.sm.save_settings()
		return True


	def _attach_traces(self) -> None:
		vars = self.dictionary_vars
		self._detach_traces()
		self.trace_ids["Danbooru (Safe)"] = vars["Danbooru (Safe)"].trace_add("write", self._toggle_danbooru)
		self.trace_ids["Danbooru"] = vars["Danbooru"].trace_add("write", self._toggle_danbooru_safe)


	def _detach_traces(self) -> None:
		vars = self.dictionary_vars
		for key, trace_id in self.trace_ids.items():
			if trace_id:
				vars[key].trace_remove("write", trace_id)
		self.trace_ids = {"Danbooru": None, "Danbooru (Safe)": None}


	def _toggle_danbooru_safe(self, *_args) -> None:
		if self.danbooru_safe_checkbutton and self.danbooru_safe_checkbutton.winfo_exists():
			state = "disabled" if self.dictionary_vars["Danbooru"].get() else "normal"
			self.danbooru_safe_checkbutton.config(state=state)


	def _toggle_danbooru(self, *_args) -> None:
		if self.danbooru_checkbutton and self.danbooru_checkbutton.winfo_exists():
			state = "disabled" if self.dictionary_vars["Danbooru (Safe)"].get() else "normal"
			self.danbooru_checkbutton.config(state=state)


#endregion
#region MatchMethodPage


class MatchMethodPage(SetupPage):
	def __init__(self, wizard: 'SetupWizard'):
		super().__init__(wizard)
		self.last_word_match_var = StringVar(value="Match Last Word")
		self._match_modes = {"Match Whole String": False, "Match Last Word": True}


	def render(self, container: Frame) -> None:
		top_frame = Frame(container)
		top_frame.pack(side="top", fill="x", pady=5)
		Label(top_frame, text="Select autocomplete matching method").pack(pady=5)
		ttk.Separator(top_frame, orient="horizontal").pack(fill="x", pady=5)
		mid_frame = Frame(container)
		mid_frame.pack(side="top", fill="both", expand=True, pady=5)
		options = [
			("Match only the last word",
				"Only focus on the word currently being typed."
				"\nUse underscores between words for multi-word tags."
				"\n\nExample: Type 'white dress' — suggestions will focus on 'dress'",
				"Match Last Word"
			),
			("Match entire tag",
				"Focus on the whole tag under the cursor, helpful for multi-word tags."
				"\n\nExample: Type 'white dress' — suggestions will focus on 'white dress'",
				"Match Whole String"
			)
		]
		for header, description, value in options:
			rb = ttk.Radiobutton(mid_frame, text=header, variable=self.last_word_match_var, value=value)
			rb.pack(anchor="w")
			lbl = Label(mid_frame, text=description, wraplength=480, justify="left")
			lbl.pack(anchor="w")
			lbl.config(cursor="hand2")
			lbl.bind("<Button-1>", lambda _e, v=value: self.last_word_match_var.set(v))
			ttk.Separator(mid_frame, orient="horizontal").pack(pady=20)


	def on_enter(self) -> None:
		pass


	def on_exit(self, direction: str) -> bool:
		self.wizard.app.last_word_match_var.set(self._match_modes.get(self.last_word_match_var.get(), False))
		return True


#endregion
#region SetupWizard


class SetupWizard:
	def __init__(self, settings_manager: 'SettingsManager'):
		self.sm = settings_manager
		self.app = settings_manager.app
		self.root = settings_manager.root
		self.pages: list[SetupPage] = []
		self.current_index = 0
		self.page_container: Frame | None = None
		self.nav_frame: Frame | None = None
		self.nav_buttons: dict[str, ttk.Button] = {}
		self._exit_handled = False


	def run(self):
		self.pages = [DictionarySelectionPage(self), MatchMethodPage(self)]
		self.setup_window = self.create_setup_window()
		self.page_container = Frame(self.setup_window)
		self.page_container.pack(side="top", fill="both", expand=True, padx=10, pady=5)
		self.nav_frame, self.nav_buttons = self._create_nav_buttons(self.setup_window, back_cmd=self.go_back, next_cmd=self.go_next, done_cmd=self.go_done)
		self.show_page(0)


	def create_setup_window(self):
		win = Toplevel(self.app.root)
		win.withdraw()
		win.title("Dictionary Setup")
		try:
			win.iconphoto(False, self.app.blank_image)
		except Exception:
			pass
		temp_container = Frame(win)
		temp_container.pack(side="top", fill="both", expand=True, padx=10, pady=5)
		self._create_nav_buttons(win)
		max_width = max_height = 0
		win.update_idletasks()
		max_width = max(max_width, win.winfo_reqwidth())
		max_height = max(max_height, win.winfo_reqheight())
		for page in self.pages:
			for widget in temp_container.winfo_children():
				widget.destroy()
			page.render(temp_container)
			win.update_idletasks()
			max_width = max(max_width, win.winfo_reqwidth())
			max_height = max(max_height, win.winfo_reqheight())
			detach = getattr(page, "_detach_traces", None)
			if callable(detach):
				detach()
		for widget in win.winfo_children():
			widget.destroy()
		if not max_width or not max_height:
			max_width, max_height = 500, 600
		position_right = self.root.winfo_screenwidth() // 2 - max_width // 2
		position_top = self.root.winfo_screenheight() // 2 - max_height // 2
		win.geometry(f"{max_width}x{max_height}+{position_right}+{position_top}")
		win.resizable(False, False)
		win.grab_set()
		win.deiconify()
		win.protocol("WM_DELETE_WINDOW", self.save_and_close)
		return win


	def _create_nav_buttons(self, parent, back_cmd=None, next_cmd=None, done_cmd=None):
		nav_frame = Frame(parent)
		nav_frame.pack(side="bottom", fill="x", padx=10, pady=10)
		ttk.Separator(nav_frame, orient="horizontal").pack(fill="x", pady=(0, 10))
		buttons = {}
		button_frame = Frame(nav_frame)
		button_frame.pack(fill="x")
		buttons["back"] = ttk.Button(button_frame, text="Back", width=10, command=back_cmd)
		buttons["back"].pack(side="left", padx=5)
		buttons["next"] = ttk.Button(button_frame, text="Next", width=10, command=next_cmd)
		buttons["done"] = ttk.Button(button_frame, text="Done", width=10, command=done_cmd)
		# Only pack "next" and "done" in update_nav_buttons
		return nav_frame, buttons


	def show_page(self, index: int) -> None:
		self.current_index = index
		if self.page_container:
			for widget in self.page_container.winfo_children():
				widget.destroy()
		page = self.pages[self.current_index]
		if self.page_container:
			page.render(self.page_container)
		page.on_enter()
		self.update_nav_buttons()
		self._exit_handled = False


	def update_nav_buttons(self) -> None:
		if self.nav_buttons["back"]:
			state = "disabled" if self.current_index == 0 else "normal"
			self.nav_buttons["back"].config(state=state)
		for key in ("next", "done"):
			if self.nav_buttons[key].winfo_manager():
				self.nav_buttons[key].pack_forget()
		if self.current_index == len(self.pages) - 1:
			self.nav_buttons["done"].pack(side="right", padx=5)
		else:
			self.nav_buttons["next"].pack(side="right", padx=5)


	def go_next(self) -> None:
		if self.current_index >= len(self.pages) - 1:
			return
		if self.pages[self.current_index].on_exit("next"):
			self.show_page(self.current_index + 1)


	def go_back(self) -> None:
		if self.current_index == 0:
			return
		if self.pages[self.current_index].on_exit("back"):
			self.show_page(self.current_index - 1)


	def go_done(self) -> None:
		if self.pages[self.current_index].on_exit("done"):
			self._exit_handled = True
			self.save_and_close()


	def save_and_close(self):
		if not self._exit_handled and self.pages:
			try:
				self.pages[self.current_index].on_exit("done")
			except Exception:
				pass
		self._exit_handled = False
		self.sm.save_settings()
		try:
			self.setup_window.destroy()
		except Exception:
			pass
		self.app.autocomplete.update_autocomplete_dictionary()


#endregion
