#region - Imports


import tkinter as tk
from tkinter import scrolledtext


#endregion
#region - HelpWindow


class HelpWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master=master)
        self.title("Help")
        self.minsize(200, 200)
        self.geometry("400x700")
        self.bind("<Escape>", self.close_window)
        self.protocol("WM_DELETE_WINDOW", self.close_window)
        self._setup_widgets()
        self.withdraw()


#endregion
#region - Window Methods


    def open_window(self, title=None, geometry=None, help_text=None, text_format="rich"):
        """
        Opens and displays the help window with specified settings.

        This method configures and shows the help window, updating its title,
        geometry, and content as specified. The window is centered relative
        to its master window and brought to the front.

        Args:
            title (str, optional): Window title. If None, no change.
            geometry (str, optional): Window geometry in format "WxH" or "WxH+X+Y".
                If None, no change.
            help_text (Union[str, Dict[str, str], List[str]], optional): Content to display.
                Can be a dictionary ("rich"), plain text, or a list. ("simple")
            text_format (str, optional): Format for displaying text. Options are:
                - "rich": Uses styled formatting for headers (default)
                - "simple": Displays plain text without formatting
        """
        self._update_window(title, geometry)
        self._update_help_text(help_text, text_format)
        self.deiconify()
        self._center_window()
        self.lift()


    def close_window(self, event=None):
        """Closes the help window and hides it from view."""
        self.withdraw()


    def _update_window(self, title=None, geometry=None):
        if title is not None:
            self.title(title)
        if geometry is not None:
            self.geometry(geometry)


    def _center_window(self):
        if not self.master:
            return
        self.update_idletasks()
        # Get master's geometry
        master_x = self.master.winfo_x()
        master_y = self.master.winfo_y()
        master_width = self.master.winfo_width()
        master_height = self.master.winfo_height()
        # Get current help window size
        help_width = self.winfo_width()
        help_height = self.winfo_height()
        # Ensure the help window does not exceed the master's dimensions
        target_width = min(help_width, master_width)
        target_height = min(help_height, master_height)
        # Calculate centered position within master
        x = master_x + (master_width - target_width) // 2
        y = master_y + (master_height - target_height) // 2
        # Update geometry with the new dimensions and position
        self.geometry(f"{target_width}x{target_height}+{x}+{y}")


#endregion
#region - Create Interface


    def _setup_widgets(self):
        self._create_textbox()
        self._create_footer_label()


    def _create_textbox(self):
        self.textbox = scrolledtext.ScrolledText(self, wrap="word", height=1)
        self.textbox.pack(expand=True, fill='both')
        self.textbox.tag_config("#header",   font=("", 18, "bold"), justify='center')
        self.textbox.tag_config("##header",  font=("", 12, "bold"))
        self.textbox.tag_config("###header", font=("", 10, "bold"))
        self.textbox.tag_config("content",   font=("", 10))


    def _create_footer_label(self):
        self.author_label = tk.Label(self, text=f"Created by: github.com/Nenotriple", font=("", 10))
        self.author_label.pack(side="bottom", fill="x")


#endregion
#region - Update Text


    def _update_help_text(self, help_text=None, text_format="rich"):
        """
        Display help text in the textbox using either simple or rich formatting.

        :param help_text: The text or dictionary to display.
        :param text_format: Determines how the text is formatted ("rich" or "simple").
        """
        self.textbox.config(state='normal')
        self.textbox.delete("1.0", "end")
        if help_text is None:
            self.textbox.insert("end", "No help text available")
            self.textbox.config(state='disabled')
            return
        if text_format == "rich" and isinstance(help_text, dict):
            self._insert_rich_text(help_text)
        else: # "simple" or not a dict
            self._insert_simple_text(help_text)
        self.textbox.config(state='disabled')


    def _insert_simple_text(self, help_text):
        """
        Insert the provided help text as plain text into the textbox.

        :param help_text: Can be a dict, list, or string. Each element or line is inserted as-is.
        """
        try:
            text = ""
            if isinstance(help_text, dict):
                for header, content in help_text.items():
                    text += f"{header}\n{content}\n\n"
            elif isinstance(help_text, list):
                for item in help_text:
                    text += f"{str(item)}\n"
            else:
                text = str(help_text)
            self.textbox.insert("end", text)
        except Exception as e:
            self.textbox.insert("end", f"Error: {str(e)}")


    def _insert_rich_text(self, help_text):
        """
        Insert the provided help text using styled headers.

        :param help_text: Expects a dict of header-content pairs for rich formatting.
        """
        try:
            for idx, (header, content) in enumerate(help_text.items()):
                tag = "#header" if idx == 0 else "##header"
                self.textbox.insert("end", header + "\n", tag)
                for line in content.splitlines():
                    if not line.strip():
                        continue
                    line_tag = "###header" if line.strip().endswith(':') else "content"
                    self.textbox.insert("end", line + "\n", line_tag)
                self.textbox.insert("end", "\n")
        except AttributeError:
            self._insert_simple_text(help_text)
