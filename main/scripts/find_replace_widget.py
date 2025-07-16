"""
Description:
------------
A custom Tkinter widget for find and replace functionality in a text widget.

Features:
---------
- Find and replace text in a text widget
- Highlight all matches
- Highlight the current match
- Case sensitive search
- Match whole word search
- Regular expression search
- Navigate to next and previous matches
- Replace current match
- Replace all matches

Instructions:
-------------
0. Install the TkToolTip package
    git+https://github.com/Nenotriple/TkToolTip.git
1. Import
    from find_replace_widget import FindReplaceEntry
2. Create the widget, passing the parent frame and text widget as arguments
    find_replace_widget = FindReplaceEntry(parent_frame, text_widget)
3. Place the widget in the parent frame. You must use the grid geometry manager.
    find_replace_widget.grid(row=0, column=0, sticky="ew")
4. Bind the toggle function to a key event, e.g., Ctrl+F
    text_widget.bind("<Control-f>", lambda _: find_replace_widget.show_widget())

Methods:
--------
- show_widget(): Display widget and search for selected text
- hide_widget(): Hide widget and clear highlights
- get_selected_text(): Get currently selected text from the associated text widget
- toggle_replace_row(): Toggle the visibility of the replace row
- search_for_text(text): Search for specific text in the text widget
"""


#region Imports

import re
from typing import Tuple
import tkinter as tk
from tkinter import ttk

# Third party
from TkToolTip.TkToolTip import TkToolTip as Tip


#endregion
#region TextSearchManager


class TextSearchManager:
    """Manages text search operations with support for highlighting, navigation, and replacements."""

    def __init__(self, text_widget: tk.Text):
        """Initialize with a text widget to operate on."""
        self.text_widget = text_widget
        self.matches = []  # List of tuples containing start and end indices of matches
        self.current_match_index = -1  # Index of the currently selected match
        self.highlight_tag = "search_highlight"
        self.current_tag = "current_match"
        # Configure tag appearance
        self.text_widget.tag_configure(self.highlight_tag,  background="#FFFF99", selectbackground="#ffc800", selectforeground="black")
        self.text_widget.tag_configure(self.current_tag,    background="#FF9933", selectbackground="#ff6e00", selectforeground="black")


#endregion
#region Helper Functions


    def _get_search_pattern(self, search_term: str, match_whole_word: bool) -> str:
        """Convert search term to regex pattern if needed."""
        if match_whole_word:
            # Add word boundary markers
            return r'\b' + re.escape(search_term) + r'\b'
        return re.escape(search_term)


    def _index_to_line_char(self, text: str, index: int) -> Tuple[int, int]:
        """Convert a character index to line.char format for tkinter."""
        lines = text[:index].split('\n')
        line_num = len(lines)
        char_num = len(lines[-1])
        return line_num, char_num


    def _highlight_current_match(self):
        """Highlight the current match with a different color."""
        # Remove current highlight from all matches
        self.text_widget.tag_remove(self.current_tag, "1.0", "end")
        # Add current highlight to the selected match
        if 0 <= self.current_match_index < len(self.matches):
            start, end = self.matches[self.current_match_index]
            self.text_widget.tag_add(self.current_tag, start, end)
            self.text_widget.see(start)  # Ensure the match is visible


#endregion
#region Search Operations


    def find_all(self, search_term: str, case_sensitive: bool = False, match_whole_word: bool = False, use_regex: bool = False) -> int:
        """Find all occurrences of the search term in the text widget."""
        self.clear_highlights()
        self.matches = []
        if not search_term:
            return 0
        text_content = self.text_widget.get("1.0", "end-1c")
        # Prepare regex flags
        flags = 0 if case_sensitive else re.IGNORECASE
        try:
            if use_regex:
                # Use the regex pattern directly
                pattern = search_term
            else:
                # Escape the search term to treat it as a literal string
                pattern = self._get_search_pattern(search_term, match_whole_word)
            # Find all matches
            for match in re.finditer(pattern, text_content, flags):
                start_idx = match.start()
                end_idx = match.end()
                # Convert character indices to tkinter text indices
                start_line, start_char = self._index_to_line_char(text_content, start_idx)
                end_line, end_char = self._index_to_line_char(text_content, end_idx)
                start_tk_idx = f"{start_line}.{start_char}"
                end_tk_idx = f"{end_line}.{end_char}"
                self.matches.append((start_tk_idx, end_tk_idx))
                self.text_widget.tag_add(self.highlight_tag, start_tk_idx, end_tk_idx)
        except re.error:
            # Invalid regex pattern
            return 0
        # If matches were found, select the first one
        if self.matches:
            self.current_match_index = 0
            self._highlight_current_match()
        return len(self.matches)


#endregion
#region Navigation Operations


    def next_match(self):
        """Navigate to the next match."""
        if not self.matches:
            return
        self.current_match_index = (self.current_match_index + 1) % len(self.matches)
        self._highlight_current_match()


    def prev_match(self):
        """Navigate to the previous match."""
        if not self.matches:
            return
        self.current_match_index = (self.current_match_index - 1) % len(self.matches)
        self._highlight_current_match()


    def clear_highlights(self):
        """Clear all search highlights."""
        self.text_widget.tag_remove(self.highlight_tag, "1.0", "end")
        self.text_widget.tag_remove(self.current_tag, "1.0", "end")
        self.matches = []
        self.current_match_index = -1


#endregion
#region Replacement Operations


    def replace_current(self, replacement: str) -> bool:
        """Replace the currently selected match."""
        if not self.matches or self.current_match_index < 0:
            return False
        start, end = self.matches[self.current_match_index]
        self.text_widget.delete(start, end)
        self.text_widget.insert(start, replacement)
        # Re-run the search to update match positions
        search_term = self.text_widget.get(start, f"{start}+{len(replacement)}c")
        self.find_all(search_term)
        return True


    def replace_all(self, search_term: str, replacement: str, case_sensitive: bool = False, match_whole_word: bool = False, use_regex: bool = False) -> int:
        """Replace all occurrences of the search term with the replacement text."""
        if not search_term:
            return 0
        # Get the entire text content
        text_content = self.text_widget.get("1.0", "end-1c")
        # Prepare regex flags
        flags = 0 if case_sensitive else re.IGNORECASE
        try:
            if use_regex:
                # Use the regex pattern directly
                pattern = search_term
            else:
                # Escape the search term to treat it as a literal string
                pattern = self._get_search_pattern(search_term, match_whole_word)
            # Perform all replacements in one operation on the string
            new_content, count = re.subn(pattern, replacement, text_content, flags=flags)
            if count > 0:
                # Replace the entire text widget content
                self.text_widget.edit_separator()
                self.text_widget.delete("1.0", "end")
                self.text_widget.insert("1.0", new_content)
                self.text_widget.edit_separator()
            # Clear highlights and reset
            self.clear_highlights()
            return count
        except re.error:
            # Invalid regex pattern
            return 0


#endregion
#region FindReplaceEntry


class FindReplaceEntry(ttk.Frame):
    def __init__(self, parent: tk.Frame, text_widget: tk.Text, *args, **kwargs):
        # Initialize the ttk.Frame with parent and any extra options
        super().__init__(parent, *args, **kwargs)
        self.parent: tk.Frame = parent
        # Track the replace row visibility state
        self.replace_row_visible = False
        # Store text widget reference and create search manager if provided
        self.text_widget = text_widget
        self.search_manager = TextSearchManager(text_widget) if text_widget else None
        # Store references to widgets
        self.toggle_btn = None
        self.find_entry = None
        self.replace_entry = None
        self.replace_row_widgets = []
        self.results_label = None
        self.case_sensitive = tk.BooleanVar(value=False)
        self.match_whole_word = tk.BooleanVar(value=False)
        self.use_regex = tk.BooleanVar(value=False)
        # Create the widgets
        self.create_widgets()


#endregion
#region UI Construction


    def create_widgets(self):
        """Create and configure the child widgets."""
        self.columnconfigure(2, weight=1)  # Expand the entry widgets
        # Create the find and replace rows
        self.create_find_row()
        self.create_replace_row()


    def create_find_row(self):
        self.toggle_btn = ttk.Button(self, text="˃", width=3, command=self.toggle_replace_row)
        self.toggle_btn.grid(row=0, column=0, rowspan=2, sticky="ns")
        Tip.create(self.toggle_btn, "Toggle replace row", delay=250, origin="widget", pady=-22)
        # Label
        ttk.Label(self, text="Find:").grid(row=0, column=1, sticky="w")
        # Entry
        self.find_entry = ttk.Entry(self)
        self.find_entry.grid(row=0, column=2, sticky="ew")
        self.find_entry.bind("<Return>", lambda e: self.next_match())
        self.find_entry.bind("<Shift-Return>", lambda e: self.previous_match())
        self.find_entry.bind("<KeyRelease>", self.perform_search)
        self.find_entry.bind("<Escape>", lambda e: self.hide_widget())
        # Options menubutton
        self.options_menubutton = ttk.Menubutton(self, text="☰")
        self.options_menubutton.grid(row=0, column=3)
        self.options_menu = tk.Menu(self.options_menubutton, tearoff=0)
        self.options_menubutton.config(menu=self.options_menu)
        # Menu items
        self.options_menu.add_checkbutton(label="Match case (Aa)", variable=self.case_sensitive, command=self.perform_search)
        self.options_menu.add_checkbutton(label="Match whole word (≃)", variable=self.match_whole_word, command=self.perform_search)
        self.options_menu.add_checkbutton(label="Use regular expressions (.*)", variable=self.use_regex, command=self.perform_search)
        Tip.create(self.options_menubutton, "Search options", delay=250, origin="widget", pady=-22)
        # Results label
        self.results_label = tk.Label(self, text="No results", highlightbackground="#dcdcdc", highlightthickness=1, anchor="w")
        self.results_label.grid(row=0, column=4, columnspan=2, sticky="w")
        # Prev
        prev_btn = ttk.Button(self, text="˄", width=3, command=self.previous_match)
        prev_btn.grid(row=0, column=6, sticky="e")
        Tip.create(prev_btn, "Previous match (Shift+Enter)", delay=250, origin="widget", pady=-22)
        # Next
        next_btn = ttk.Button(self, text="˅", width=3, command=self.next_match)
        next_btn.grid(row=0, column=7, sticky="e")
        Tip.create(next_btn, "Next match (Enter)", delay=250, origin="widget", pady=-22)
        # Close
        close_btn = ttk.Button(self, text="X", width=3, command=self.hide_widget)
        close_btn.grid(row=0, column=8, sticky="e")
        Tip.create(close_btn, "Close (Esc)", delay=250, origin="widget", pady=-22)


    def create_replace_row(self):
        # Label
        replace_label = ttk.Label(self, text="Replace:")
        replace_label.grid(row=1, column=1, sticky="w")
        replace_label.grid_remove()
        # Entry
        self.replace_entry = ttk.Entry(self)
        self.replace_entry.grid(row=1, column=2, sticky="ew")
        self.replace_entry.grid_remove()
        self.replace_entry.bind("<Control-f>", lambda e: self.hide_widget())
        # Replace button
        replace_btn = ttk.Button(self, text="Replace", command=self.replace_current)
        replace_btn.grid(row=1, column=3, columnspan=2, sticky="ew")
        replace_btn.grid_remove()
        Tip.create(replace_btn, "Replace current match", delay=250, origin="widget", pady=-22)
        # Replace All button
        replace_all_btn = ttk.Button(self, text="Replace All", command=self.replace_all)
        replace_all_btn.grid(row=1, column=5, columnspan=4, sticky="ew")
        replace_all_btn.grid_remove()
        Tip.create(replace_all_btn, "Replace all matches", delay=250, origin="widget", pady=-22)
        # Store references to widgets
        self.replace_row_widgets = [replace_label, self.replace_entry, replace_btn, replace_all_btn]


#region UI State Management


    def toggle_replace_row(self):
        """Toggle the visibility of the replace row"""
        self.replace_row_visible = not self.replace_row_visible
        # Update toggle button appearance
        self.toggle_btn.config(text="˅" if self.replace_row_visible else "˃")
        # Show or hide replace row widgets
        if self.replace_row_visible:
            for widget in self.replace_row_widgets:
                widget.grid()
        else:
            for widget in self.replace_row_widgets:
                widget.grid_remove()


    def update_results_count(self, count=None):
        """Update the results label with the current match count"""
        if count is None or count == 0:
            self.results_label.config(text="No results")
        elif count == 1:
            self.results_label.config(text="1 match")
        else:
            current_idx = self.search_manager.current_match_index + 1 if self.search_manager.current_match_index >= 0 else 0
            self.results_label.config(text=f"{current_idx} of {count}")


    def show_widget(self):
        """Toggle the visibility of the find/replace widget and search for selected text."""
        if self.winfo_viewable():
            self.focus_find_entry()
            self.search_for_text(self.get_selected_text())
        else:
            self.grid()
            self.focus_find_entry()
            self.search_for_text(self.get_selected_text())


    def hide_widget(self):
        """Handle the close button click"""
        if self.search_manager:
            self.search_manager.clear_highlights()
        self.grid_remove()
        self.text_widget.focus_set()


    def focus_find_entry(self):
        """Set focus to the find entry field and select all text."""
        if self.find_entry:
            self.find_entry.focus_set()
            self.find_entry.select_range(0, 'end')
            self.find_entry.icursor('end')


#endregion
#region Search Operations


    def perform_search(self, event=None):
        """Perform search based on the current find entry"""
        # Ignore Return and Shift+Return key events
        if event and event.keysym in ("Return", "KP_Enter"):
            return
        if not self.search_manager or not self.text_widget:
            self.search_manager.clear_highlights()
            self.update_results_count(None)
            return
        search_term = self.find_entry.get()
        if not search_term:
            self.search_manager.clear_highlights()
            self.update_results_count(None)
            return
        case_sensitive = self.case_sensitive.get()
        match_whole_word = self.match_whole_word.get()
        use_regex = self.use_regex.get()
        match_count = self.search_manager.find_all(search_term, case_sensitive=case_sensitive, match_whole_word=match_whole_word, use_regex=use_regex)
        self.update_results_count(match_count)


    def next_match(self):
        """Navigate to the next match"""
        if self.search_manager:
            self.search_manager.next_match()
            if self.search_manager.matches:
                self.update_results_count(len(self.search_manager.matches))


    def previous_match(self):
        """Navigate to the previous match"""
        if self.search_manager:
            self.search_manager.prev_match()
            if self.search_manager.matches:
                self.update_results_count(len(self.search_manager.matches))


    def search_for_text(self, text: str):
        """
        Set the find entry text to the provided string and perform a search.

        Args:
            text (str): The text to search for
        """
        if not self.text_widget or not self.search_manager:
            return
        # Set the find entry text
        if len(text) > 1:
            self.find_entry.delete(0, 'end')
            self.find_entry.insert(0, text)
        # Perform the search
        self.perform_search()
        # Focus the find entry
        self.focus_find_entry()


#endregion
#region Replace Operations


    def replace_current(self):
        """Replace the current match with replacement text"""
        if not self.search_manager:
            return
        replacement = self.replace_entry.get()
        success = self.search_manager.replace_current(replacement)
        # Update the match count
        if success:
            self.update_results_count(len(self.search_manager.matches))
            self.perform_search()


    def replace_all(self):
        """Replace all matches with replacement text"""
        if not self.search_manager:
            return
        search_term = self.find_entry.get()
        replacement = self.replace_entry.get()
        case_sensitive = self.case_sensitive.get()
        match_whole_word = self.match_whole_word.get()
        use_regex = self.use_regex.get()
        if not search_term:
            return
        replacements = self.search_manager.replace_all(search_term, replacement, case_sensitive=case_sensitive, match_whole_word=match_whole_word, use_regex=use_regex)
        self.update_results_count(None)


#endregion
#region Highlights


    def clear_highlights(self):
        self.search_manager.clear_highlights()


#endregion
#region Helper Methods


    def get_selected_text(self):
        """Get selected text from the associated text widget."""
        if not self.text_widget:
            return ""
        if self.text_widget.tag_ranges("sel"):
            return self.text_widget.get("sel.first", "sel.last")
        return ""


#endregion
