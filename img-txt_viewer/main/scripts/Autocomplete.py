#region Imports


# Standard Library
import os
import re
import sys
import csv
import pickle
import itertools
import tkinter as tk
from functools import partial
from collections import defaultdict
import yaml


# Type Hinting
from typing import TYPE_CHECKING, Dict, List, Tuple, Set, Optional, Pattern, Any, Union, DefaultDict, Callable, Iterator, Match
if TYPE_CHECKING:
    from app import ImgTxtViewer as Main


#endregion
#region Autocomplete


class Autocomplete:
    """
    Tag autocomplete engine using CSV data sources.

    Expected CSV format:
    - Column 1: Tag name (required) - used for matching
    - Column 2: Classifier ID (optional) - used for color-coding
    - Column 3: Tag ranking (optional) - used for sorting
    - Column 4: Similar names (comma-separated, optional) - used for suggestions
    """
    def __init__(self, data_file: str, include_my_tags: bool = True) -> None:
        # Data
        self.data_file: str = data_file
        # MyTags storage
        self.my_tags_yml: str = 'my_tags.yaml'

        # Settings
        self.max_suggestions: int = 4
        self.suggestion_threshold: int = 115000
        self.include_my_tags: bool = include_my_tags

        # Cache
        self.autocomplete_dict: Optional[Dict[str, Tuple[str, List[str]]]] = None
        self.similar_names_dict: Optional[DefaultDict[str, List[str]]] = None
        self.previous_text: Optional[str] = None
        self.previous_suggestions: Optional[List[Tuple[str, Tuple[str, List[str]]]]] = None
        self.previous_pattern: Optional[Pattern] = None
        self.previous_threshold_results: Dict[Tuple[str, int], Dict[str, Tuple[str, List[str]]]] = {}
        self.single_letter_cache: Dict[str, List[Tuple[str, Tuple[str, List[str]]]]] = {}

        # Load Data
        self._load_data()
        self._precache_single_letter_suggestions()

        # Misc
        self.tags_with_underscore: List[str] = ["0_0", "(o)_(o)", "o_o", ">_o", "u_u", "x_x", "|_|", "||_||", "._.", "^_^", ">_<", "@_@", ">_@", "+_+", "+_-", "=_=", "<o>_<o>", "<|>_<|>", "ಠ_ಠ", "3_3", "6_9"]


# --------------------------------------
# Load/Read Data
# --------------------------------------
    def _load_data(self) -> None:
        """Load autocomplete data if not cached."""
        if not self.autocomplete_dict:
            self.autocomplete_dict, self.similar_names_dict = self.load_autocomplete_data()


    def load_autocomplete_data(self) -> Tuple[Dict[str, Tuple[str, List[str]]], DefaultDict[str, List[str]]]:
        """Load and merge tag data from primary and custom CSV sources."""
        app_path: str = self._get_app_path()
        data_file_path: str = os.path.join(app_path, "main\dict", self.data_file)
        # Determine MyTags file to use: YAML > YML > CSV
        yaml_path: str = os.path.join(app_path, 'my_tags.yaml')
        yml_path: str = os.path.join(app_path, 'my_tags.yml')
        csv_path: str = os.path.join(app_path, 'my_tags.csv')
        additional_file_path: Optional[str] = None
        additional_format: Optional[str] = None
        if os.path.isfile(yaml_path):
            additional_file_path = yaml_path
            additional_format = 'yaml'
        elif os.path.isfile(yml_path):
            additional_file_path = yml_path
            additional_format = 'yaml'
        elif os.path.isfile(csv_path):
            additional_file_path = csv_path
            additional_format = 'csv'
        else:
            self.include_my_tags = False
        autocomplete_data: Dict[str, Tuple[str, List[str]]] = {}
        similar_names_dict: DefaultDict[str, List[str]] = defaultdict(list)
        self._read_csv(data_file_path, autocomplete_data, similar_names_dict)
        if self.include_my_tags and additional_file_path:
            if additional_format == 'yaml':
                self._read_yaml_mytags(additional_file_path, autocomplete_data, similar_names_dict)
            else:
                self._read_csv(additional_file_path, autocomplete_data, similar_names_dict, include_classifier_id=False)
        return autocomplete_data, similar_names_dict


    def _get_app_path(self) -> str:
        """Get absolute path to application root directory."""
        if getattr(sys, 'frozen', False):
            return sys._MEIPASS
        path: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return path


    def _read_csv(self, file_path: str, data: Dict[str, Tuple[str, List[str]]], similar_names_dict: DefaultDict[str, List[str]], include_classifier_id: bool = True) -> None:
        """Parse CSV file and populate tag data and similar names dictionaries."""
        if os.path.isfile(file_path):
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if row and not row[0].startswith('###'):
                        true_name: str = row[0]
                        classifier_id: str = row[1] if include_classifier_id and len(row) > 1 else ''
                        similar_names: List[str] = row[3].split(',') if len(row) > 3 else []
                        if true_name in data and not include_classifier_id:
                            data[true_name][1].extend(similar_names)
                        else:
                            data[true_name] = (classifier_id, similar_names)
                        for sim_name in similar_names:
                            similar_names_dict[sim_name].append(true_name)


    def _read_yaml_mytags(self, file_path: str, data: Dict[str, Tuple[str, List[str]]], similar_names_dict: DefaultDict[str, List[str]]) -> None:
        """Parse YAML MyTags file (list or {tags: [...]}) and populate data.
        Classifier IDs and similar names are not provided for MyTags.
        """
        if not os.path.isfile(file_path):
            return
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f) or []
            items: List[str] = []
            if isinstance(yaml_data, dict) and 'tags' in yaml_data and isinstance(yaml_data['tags'], list):
                items = [str(x).strip() for x in yaml_data['tags'] if str(x).strip()]
            elif isinstance(yaml_data, list):
                items = [str(x).strip() for x in yaml_data if str(x).strip()]
            for tag in items:
                if tag and tag not in data:
                    data[tag] = ('', [])
        except Exception:
            # Fail silently; YAML may be malformed
            pass


# --------------------------------------
# Pre-Cache Single-Letter Suggestions
# --------------------------------------
    def _precache_single_letter_suggestions(self) -> None:
        """Build and save cache of suggestions for single-letter inputs."""
        dictionary_file_path: str = os.path.join(self._get_app_path(), "main\dict", self.data_file)
        if not os.path.exists(dictionary_file_path):
            return
        dictionary_name: str = os.path.splitext(self.data_file)[0]
        cache_dir: str = os.path.join(self._get_app_path(), 'main\dict\cache')
        cache_file: str = os.path.join(cache_dir, f'{dictionary_name}_pre-cache')
        cache_timestamp_file: str = os.path.join(cache_dir, f'{dictionary_name}_pre-cache-timestamp')
        os.makedirs(cache_dir, exist_ok=True)
        cache_is_stale: bool = True
        if os.path.exists(cache_file) and os.path.exists(cache_timestamp_file):
            with open(cache_timestamp_file, 'r') as f:
                cache_timestamp_str: str = f.read().strip()
                if cache_timestamp_str:
                    cache_timestamp: float = float(cache_timestamp_str)
                    dictionary_timestamp: float = os.path.getmtime(dictionary_file_path)
                    if cache_timestamp >= dictionary_timestamp:
                        cache_is_stale = False
        if not cache_is_stale:
            if os.path.exists(cache_file):
                with open(cache_file, 'rb') as f:
                    self.single_letter_cache = pickle.load(f)
        else:
            for char in "abcdefghijklmnopqrstuvwxyz0123456789":
                pattern: Pattern = self._compile_pattern(char)
                suggestions: Dict[str, Tuple[str, List[str]]] = self._get_or_cache_threshold_results(pattern)
                self.single_letter_cache[char] = self._sort_suggestions(suggestions, char)
            with open(cache_file, 'wb') as f:
                pickle.dump(self.single_letter_cache, f)
            with open(cache_timestamp_file, 'w') as f:
                f.write(str(os.path.getmtime(dictionary_file_path)))


# --------------------------------------
# Get Suggestions
# --------------------------------------
    def get_suggestion(self, text: str) -> List[Tuple[str, Tuple[str, List[str]]]]:
        """Return ranked suggestions matching input text."""
        self._load_data()
        if not self.autocomplete_dict:
            return []
        if len(text) == 1 and text in self.single_letter_cache:
            return self.single_letter_cache[text][:self.max_suggestions]
        if text == self.previous_text:
            return self.previous_suggestions[:self.max_suggestions]
        text_with_underscores: str = text.replace(" ", "_")
        pattern: Pattern = self._compile_pattern(text_with_underscores)
        suggestions: Dict[str, Tuple[str, List[str]]] = self._get_or_cache_threshold_results(pattern)
        self._include_similar_name_suggestions(pattern, suggestions)
        sorted_suggestions: List[Tuple[str, Tuple[str, List[str]]]] = self._sort_suggestions(suggestions, text_with_underscores)
        self._cache_suggestions(text, sorted_suggestions, pattern)
        return sorted_suggestions[:self.max_suggestions]


    def _compile_pattern(self, text: str) -> Pattern:
        """Create regex pattern supporting wildcards from input text."""
        text_with_asterisks: str = re.escape(text).replace("\\*", ".*")
        return re.compile(text_with_asterisks)


    def _get_or_cache_threshold_results(self, pattern: Pattern) -> Dict[str, Tuple[str, List[str]]]:
        """Return cached or new matching results within threshold limit."""
        cache_key: Tuple[str, int] = (pattern.pattern, self.suggestion_threshold)
        if cache_key in self.previous_threshold_results:
            return self.previous_threshold_results[cache_key]
        results: Dict[str, Tuple[str, List[str]]] = self._find_matching_names(pattern, self.suggestion_threshold)
        self.previous_threshold_results[cache_key] = results
        return results


    def _find_matching_names(self, pattern: Pattern, threshold: int) -> Dict[str, Tuple[str, List[str]]]:
        """Find tags matching pattern within threshold limit."""
        return {
            true_name: (classifier_id, similar_names)
            for true_name, (classifier_id, similar_names)
            in itertools.islice(self.autocomplete_dict.items(), threshold)
            if pattern.match(true_name)
        }


    def _include_similar_name_suggestions(self, pattern: Pattern, suggestions: Dict[str, Tuple[str, List[str]]]) -> None:
        """Add matching similar names to suggestions."""
        for sim_name, true_names in self.similar_names_dict.items():
            if pattern.match(sim_name):
                for true_name in true_names:
                    suggestions[true_name] = self.autocomplete_dict[true_name]


    def _sort_suggestions(self, suggestions: Dict[str, Tuple[str, List[str]]], text: str) -> List[Tuple[str, Tuple[str, List[str]]]]:
        """Sort suggestions by relevance score."""
        return sorted(suggestions.items(), key=lambda x: self.get_score(x[0], text), reverse=True)


    def _cache_suggestions(self, text: str, sorted_suggestions: List[Tuple[str, Tuple[str, List[str]]]], pattern: Pattern) -> None:
        """Store current suggestions for reuse."""
        self.previous_text = text
        self.previous_suggestions = sorted_suggestions
        self.previous_pattern = pattern


# --------------------------------------
# Score Calculation
# --------------------------------------
    def get_score(self, suggestion: str, text: str, algorithm: str = "simple") -> float:
        """
        Calculate suggestion relevance score based on match quality."""
        # Use simple scoring algorithm (default)
        if algorithm == "simple":
            score: float = 0
            # Exact match gets highest priority
            if suggestion == text:
                return len(text) * 2
            # Starting match gets high priority
            for suggestion_char, input_char in zip(suggestion, text):
                if suggestion_char == input_char:
                    score += 1
                else:
                    break
            # Contains match gets lower score
            classifier_id, _ = self.autocomplete_dict.get(suggestion, ('', []))
            if not classifier_id and suggestion.startswith(text[:3]):
                score += 1
            return score
        # Use advanced scoring algorithm
        else:
            # Exact match gets highest priority
            if suggestion == text:
                return 1000
            # Starting match gets high priority
            if suggestion.startswith(text):
                base_score: float = 500 + len(text) * 2
                # Shorter suggestions ranked higher
                return base_score - (len(suggestion) - len(text)) * 0.5
            # Partial match at word boundaries
            words: List[str] = suggestion.split('_')
            for word in words:
                if word.startswith(text):
                    return 300 + len(text)
            # Contains match gets lower score
            if text in suggestion:
                return 200 + len(text)
            # Character-by-character match
            common_prefix_length: int = 0
            for s_char, t_char in zip(suggestion, text):
                if s_char == t_char:
                    common_prefix_length += 1
                else:
                    break
            return common_prefix_length * 10


#endregion
#region SuggestionHandler


class SuggestionHandler:
    """Manages suggestion display and interaction in the UI."""
    def __init__(self, parent: 'Main') -> None:
        self.parent: 'Main' = parent
        self.autocomplete: Autocomplete = None  # Will be initialized later
        self.suggestions: List[Tuple[str, Tuple[str, List[str]]]] = []
        self.selected_suggestion_index: int = 0
        self.suggestion_colors: Dict[int, str] = {}
        self.selected_csv_files: List[str] = []


    def _handle_suggestion_event(self, event: tk.Event) -> bool:
        """Process keyboard events for suggestion navigation."""
        keysym: str = event.keysym
        if keysym == "Tab":
            if self.selected_suggestion_index < len(self.suggestions):
                selected_suggestion = self.suggestions[self.selected_suggestion_index]
                if isinstance(selected_suggestion, tuple):
                    selected_suggestion = selected_suggestion[0]
                self._insert_selected_suggestion(selected_suggestion.strip())
            self.clear_suggestions()
        elif keysym in ("Alt_L", "Alt_R"):
            if self.suggestions:
                if keysym == "Alt_R":
                    self.selected_suggestion_index = (self.selected_suggestion_index - 1) % len(self.suggestions)
                else:
                    self.selected_suggestion_index = (self.selected_suggestion_index + 1) % len(self.suggestions)
                self._highlight_suggestions()
            return False  # Do not clear suggestions
        elif keysym in ("Up", "Down", "Left", "Right") or event.char == ",":
            return True
        else:
            return False


    def update_suggestions(self, event: Optional[tk.Event] = None) -> None:
        """Refresh suggestions based on current input state."""
        # Initialize empty event if none provided
        event = type('', (), {'keysym': '', 'char': ''})() if event is None else event
        cursor_position: str = self.parent.text_box.index("insert")
        # Early returns for special cases
        if self._cursor_inside_tag(cursor_position):
            self.clear_suggestions()
            return
        if self._handle_suggestion_event(event):
            self.clear_suggestions()
            return
        text: str = self.parent.text_box.get("1.0", "insert")
        # Get current word based on mode
        if self.parent.last_word_match_var.get():
            current_word: str = (text.split() or [''])[-1]
        else:
            separator: str = '\n' if self.parent.list_mode_var.get() else ','
            current_word = (text.split(separator) or [''])[-1].strip()
        # Check if suggestions should be shown
        if not current_word or (len(self.selected_csv_files) < 1 and not self.parent.use_mytags_var.get()):
            self.clear_suggestions()
            return
        # Get and process suggestions
        suggestions: List[Tuple[str, Tuple[str, List[str]]]] = self.autocomplete.get_suggestion(current_word)
        if not suggestions:
            self.clear_suggestions()
            return
        # Transform suggestions for display
        self.suggestions = [(suggestion[0] if suggestion[0] in self.autocomplete.tags_with_underscore else suggestion[0].replace("_", " "), suggestion[1]) for suggestion in sorted(suggestions, key=lambda x: self.autocomplete.get_score(x[0], current_word), reverse=True)]
        # Show or clear suggestions
        if self.suggestions:
            self._highlight_suggestions()
        else:
            self.clear_suggestions()


    def _highlight_suggestions(self) -> None:
        """Update suggestion display with highlighting and interactivity."""
        def on_mouse_hover(tag_name: str, highlight: bool, event=None) -> None:
            if highlight:
                widget.tag_config(tag_name, relief='raised', borderwidth=1)
                widget.config(cursor="hand2")
            else:
                widget.tag_config(tag_name, relief='flat', borderwidth=0)
                widget.config(cursor="")
        widget = self.parent.suggestion_textbox
        widget.config(state='normal')
        widget.delete('1.0', 'end')
        configured_colors: Set[str] = set()
        num_suggestions: int = len(self.suggestions)
        for index, (suggestion_text, classifier_id) in enumerate(self.suggestions):
            classifier_id = classifier_id[0]
            color_index: int = int(classifier_id) % len(self.suggestion_colors) if classifier_id and classifier_id.isdigit() else 0
            suggestion_color: str = self.suggestion_colors[color_index]
            bullet_symbol: str = "⚫" if index == self.selected_suggestion_index else "⚪"
            suggestion: str = f"suggestion_tag_{index}"
            widget.insert('end', bullet_symbol)
            widget.insert('end', f" {suggestion_text} ", (suggestion, suggestion_color))
            if suggestion_color not in configured_colors:
                widget.tag_config(suggestion_color, foreground=suggestion_color, font=('Segoe UI', '9'))
                configured_colors.add(suggestion_color)
            widget.tag_bind(suggestion, '<Button-1>', partial(self._on_suggestion_click, index))
            widget.tag_bind(suggestion, '<Enter>', partial(on_mouse_hover, suggestion, True))
            widget.tag_bind(suggestion, '<Leave>', partial(on_mouse_hover, suggestion, False))
            if index < num_suggestions - 1:
                widget.insert('end', ', ')
        widget.config(state='disabled')


    def _cursor_inside_tag(self, cursor_position: str) -> bool:
        """Check if cursor is within an existing tag."""
        line, column = map(int, cursor_position.split('.'))
        line_text: str = self.parent.text_box.get(f"{line}.0", f"{line}.end")
        if self.parent.list_mode_var.get():
            inside_tag: bool = column not in (0, len(line_text))
        else:
            inside_tag = not (column == 0 or line_text[column-1:column] in (',', ' ') or line_text[column:column+1] in (',', ' ') or column == len(line_text))
        return inside_tag


    def clear_suggestions(self) -> None:
        """Reset suggestion display to default state."""
        self.suggestions = []
        self.selected_suggestion_index = 0
        self.parent.suggestion_textbox.config(state='normal')
        self.parent.suggestion_textbox.delete('1.0', 'end')
        self.parent.suggestion_textbox.insert('1.0', "...")
        self.parent.suggestion_textbox.config(state='disabled')


# --------------------------------------
# Insert Suggestion
# --------------------------------------
    def _insert_selected_suggestion(self, selected_suggestion: str) -> None:
        """Insert chosen suggestion at cursor position."""
        selected_suggestion = selected_suggestion.strip()
        text: str = self.parent.text_box.get("1.0", "insert").rstrip()
        if self.parent.last_word_match_var.get():
            words: List[str] = text.split()
            current_word: str = words[-1] if words else ''
        else:
            elements: List[str] = [element.strip() for element in text.split('\n' if self.parent.list_mode_var.get() else ',')]
            current_word = elements[-1]
        remaining_text: str = self.parent.text_box.get("insert", "end").rstrip('\n')
        start_of_current_word: str = "1.0 + {} chars".format(len(text) - len(current_word))
        self.parent.text_box.delete(start_of_current_word, "insert")
        if self.parent.list_mode_var.get() and not remaining_text.startswith('\n') and not self.parent.last_word_match_var.get():
            self.parent.text_box.insert(start_of_current_word, selected_suggestion + '\n')
        else:
            self.parent.text_box.insert(start_of_current_word, selected_suggestion)

        if self.parent.list_mode_var.get() and remaining_text:
            self.insert_newline_listmode(called_from_insert=True)
            self.parent.text_box.mark_set("insert", "insert + 1 lines")
        self.parent.append_comma_to_text()


    def insert_newline_listmode(self, event: Optional[tk.Event] = None, called_from_insert: bool = False) -> str:
        """Handle newline insertion in list mode."""
        if self.parent.list_mode_var.get():
            self.parent.text_box.insert("insert", '\n')
            if called_from_insert and self.parent.text_box.index("insert") != self.parent.text_box.index("end-1c"):
                self.parent.text_box.mark_set("insert", "insert-1l")
            return 'break'
        return ''


    def _on_suggestion_click(self, suggestion_index: int, event=None) -> None:
        """Handle suggestion selection via mouse click."""
        selected_suggestion, _ = self.suggestions[suggestion_index]
        self._insert_selected_suggestion(selected_suggestion.strip())
        self.clear_suggestions()


# --------------------------------------
# Suggestion Settings
# --------------------------------------
    def update_autocomplete_dictionary(self) -> None:
        """Update tag database based on selected CSV sources."""
        csv_vars = {
            'danbooru.csv': self.parent.csv_danbooru,
            'danbooru_safe.csv': self.parent.csv_danbooru_safe,
            'e621.csv': self.parent.csv_e621,
            'dictionary.csv': self.parent.csv_english_dictionary,
            'derpibooru.csv': self.parent.csv_derpibooru
            }
        self.selected_csv_files = [csv_file for csv_file, var in csv_vars.items() if var.get()]
        if not self.selected_csv_files:
            self.autocomplete = Autocomplete("None", include_my_tags=self.parent.use_mytags_var.get())
        else:
            self.autocomplete = Autocomplete(self.selected_csv_files[0], include_my_tags=self.parent.use_mytags_var.get())
            for csv_file in self.selected_csv_files[1:]:
                self.autocomplete.autocomplete_dict.update(Autocomplete(csv_file).autocomplete_dict, include_my_tags=self.parent.use_mytags_var.get())
        self.clear_suggestions()
        self._set_suggestion_color(self.selected_csv_files[0] if self.selected_csv_files else "None")
        self.set_suggestion_threshold()


    def _set_suggestion_color(self, csv_file: str) -> None:
        """Configure suggestion color scheme based on data source."""
        color_mappings: Dict[str, Dict[int, str]] = {
            'None': {0: "black"},
            'dictionary.csv': {0: "black", 1: "black", 2: "black", 3: "black", 4: "black", 5: "black", 6: "black", 7: "black", 8: "black"},
            'danbooru.csv': {0: "black", 1: "#c00004", 2: "black", 3: "#a800aa", 4: "#00ab2c", 5: "#fd9200"},
            'danbooru_safe.csv': {0: "black", 1: "#c00004", 2: "black", 3: "#a800aa", 4: "#00ab2c", 5: "#fd9200"},
            'e621.csv': {-1: "black", 0: "black", 1: "#f2ac08", 3: "#dd00dd", 4: "#00aa00", 5: "#ed5d1f", 6: "#ff3d3d", 7: "#ff3d3d", 8: "#228822"},
            'derpibooru.csv': {0: "black", 1: "#e5b021", 3: "#fd9961", 4: "#cf5bbe", 5: "#3c8ad9", 6: "#a6a6a6", 7: "#47abc1", 8: "#7871d0", 9: "#df3647", 10: "#c98f2b", 11: "#e87ebe"}
        }
        black_mappings: Dict[int, str] = {key: "black" for key in color_mappings[csv_file].keys()}
        self.suggestion_colors = color_mappings[csv_file] if self.parent.colored_suggestion_var.get() else black_mappings


    def set_suggestion_quantity(self, suggestion_quantity: int) -> None:
        """Set maximum number of displayed suggestions."""
        self.autocomplete.max_suggestions = suggestion_quantity
        self.update_suggestions(event=None)


    def set_suggestion_threshold(self) -> None:
        """Set performance/completeness tradeoff threshold."""
        thresholds: Dict[str, int] = {
            "Slow"  : 275000,
            "Normal": 130000,
            "Fast"  : 75000,
            "Faster": 40000
        }
        self.autocomplete.suggestion_threshold = thresholds.get(self.parent.suggestion_threshold_var.get())


    def clear_dictionary_csv_selection(self) -> None:
        """Reset CSV source selection to none."""
        for attr in ['csv_danbooru', 'danbooru_safe.csv', 'csv_derpibooru', 'csv_e621', 'csv_english_dictionary']:
            getattr(self, attr).set(False)
        self.update_autocomplete_dictionary()
