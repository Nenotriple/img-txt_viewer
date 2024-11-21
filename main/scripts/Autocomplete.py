"""Autocomplete module for suggestions based on input text."""

################################################################################################################################################
#region - Imports


# Standard Library
import os
import re
import sys
import csv
import pickle
import itertools
from collections import defaultdict


#endregion
################################################################################################################################################
#region CLS: Autocomplete


class Autocomplete:
    def __init__(self, data_file, include_my_tags=True):
        # Data
        self.data_file = data_file
        self.my_tags_csv = 'my_tags.csv'

        # Settings
        self.max_suggestions = 4
        self.suggestion_threshold = 115000
        self.include_my_tags = include_my_tags

        # Cache
        self.autocomplete_dict, self.similar_names_dict = None, None
        self.previous_text = None
        self.previous_suggestions = None
        self.previous_pattern = None
        self.previous_threshold_results = {}
        self.single_letter_cache = {}

        # Load Data
        self._load_data()
        self._precache_single_letter_suggestions()

        # Misc
        self.tags_with_underscore = ["0_0", "(o)_(o)", "o_o", ">_o", "u_u", "x_x", "|_|", "||_||", "._.", "^_^", ">_<", "@_@", ">_@", "+_+", "+_-", "=_=", "<o>_<o>", "<|>_<|>", "ಠ_ಠ", "3_3", "6_9"]


# --------------------------------------
# Load/Read Data
# --------------------------------------
    def _load_data(self):
        """Load autocomplete data, only if not already cached."""
        if not self.autocomplete_dict:
            self.autocomplete_dict, self.similar_names_dict = self.load_autocomplete_data()


    def load_autocomplete_data(self):
        """Load the autocomplete data from CSV files."""
        app_path = self._get_app_path()
        data_file_path = os.path.join(app_path, "main\dict", self.data_file)
        additional_file_path = os.path.join(app_path, self.my_tags_csv)
        if not os.path.isfile(additional_file_path):
            self.include_my_tags = False
        autocomplete_data = {}
        similar_names_dict = defaultdict(list)
        self._read_csv(data_file_path, autocomplete_data, similar_names_dict)
        if self.include_my_tags:
            self._read_csv(additional_file_path, autocomplete_data, similar_names_dict, include_classifier_id=False)
        return autocomplete_data, similar_names_dict


    def _get_app_path(self):
        """Get the application path for the autocomplete data files."""
        if getattr(sys, 'frozen', False):
            return sys._MEIPASS
        path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return path


    def _read_csv(self, file_path, data, similar_names_dict, include_classifier_id=True):
        """Read the CSV file and populate the data dictionary."""
        if os.path.isfile(file_path):
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if row and not row[0].startswith('###'):
                        true_name = row[0]
                        classifier_id = row[1] if include_classifier_id and len(row) > 1 else ''
                        similar_names = row[3].split(',') if len(row) > 3 else []
                        if true_name in data and not include_classifier_id:
                            data[true_name][1].extend(similar_names)
                        else:
                            data[true_name] = (classifier_id, similar_names)
                        for sim_name in similar_names:
                            similar_names_dict[sim_name].append(true_name)


# --------------------------------------
# Pre-Cache Single-Letter Suggestions
# --------------------------------------
    def _precache_single_letter_suggestions(self):
        """Pre-cache suggestions for all single-letter inputs (a-z, 0-9)."""
        dictionary_file_path = os.path.join(self._get_app_path(), "main\dict", self.data_file)
        if not os.path.exists(dictionary_file_path):
            return
        dictionary_name = os.path.splitext(self.data_file)[0]
        cache_dir = os.path.join(self._get_app_path(), 'main\dict\cache')
        cache_file = os.path.join(cache_dir, f'{dictionary_name}_pre-cache')
        cache_timestamp_file = os.path.join(cache_dir, f'{dictionary_name}_pre-cache-timestamp')
        os.makedirs(cache_dir, exist_ok=True)
        cache_is_stale = True
        if os.path.exists(cache_file) and os.path.exists(cache_timestamp_file):
            with open(cache_timestamp_file, 'r') as f:
                cache_timestamp_str = f.read().strip()
                if cache_timestamp_str:
                    cache_timestamp = float(cache_timestamp_str)
                    dictionary_timestamp = os.path.getmtime(dictionary_file_path)
                    if cache_timestamp >= dictionary_timestamp:
                        cache_is_stale = False
        if not cache_is_stale:
            if os.path.exists(cache_file):
                with open(cache_file, 'rb') as f:
                    self.single_letter_cache = pickle.load(f)
        else:
            for char in "abcdefghijklmnopqrstuvwxyz0123456789":
                pattern = self._compile_pattern(char)
                suggestions = self._get_or_cache_threshold_results(pattern)
                self.single_letter_cache[char] = self._sort_suggestions(suggestions, char)
            with open(cache_file, 'wb') as f:
                pickle.dump(self.single_letter_cache, f)
            with open(cache_timestamp_file, 'w') as f:
                f.write(str(os.path.getmtime(dictionary_file_path)))


# --------------------------------------
# Get Suggestions
# --------------------------------------
    def get_suggestion(self, text):
        """Main entry point to get suggestions based on input text."""
        self._load_data()
        if not self.autocomplete_dict:
            return None
        if len(text) == 1 and text in self.single_letter_cache:
            return self.single_letter_cache[text][:self.max_suggestions]
        if text == self.previous_text:
            return self.previous_suggestions[:self.max_suggestions]
        text_with_underscores = text.replace(" ", "_")
        pattern = self._compile_pattern(text_with_underscores)
        suggestions = self._get_or_cache_threshold_results(pattern)
        self._include_similar_name_suggestions(pattern, suggestions)
        sorted_suggestions = self._sort_suggestions(suggestions, text_with_underscores)
        self._cache_suggestions(text, sorted_suggestions, pattern)
        return sorted_suggestions[:self.max_suggestions]


    def _compile_pattern(self, text):
        """Compile the regex pattern with support for wildcard matching."""
        text_with_asterisks = re.escape(text).replace("\\*", ".*")
        return re.compile(text_with_asterisks)


    def _get_or_cache_threshold_results(self, pattern):
        """Cache and retrieve results for threshold-based searches."""
        cache_key = (pattern.pattern, self.suggestion_threshold)
        if cache_key in self.previous_threshold_results:
            return self.previous_threshold_results[cache_key]
        results = self._find_matching_names(pattern, self.suggestion_threshold)
        self.previous_threshold_results[cache_key] = results
        return results


    def _find_matching_names(self, pattern, threshold):
        """Find matching names in the main data based on the regex pattern."""
        return {
            true_name: (classifier_id, similar_names)
            for true_name, (classifier_id, similar_names)
            in itertools.islice(self.autocomplete_dict.items(), threshold)
            if pattern.match(true_name)
        }


    def _include_similar_name_suggestions(self, pattern, suggestions):
        """Include suggestions based on similar names matching the pattern."""
        for sim_name, true_names in self.similar_names_dict.items():
            if pattern.match(sim_name):
                for true_name in true_names:
                    suggestions[true_name] = self.autocomplete_dict[true_name]


    def _sort_suggestions(self, suggestions, text):
        """Sort suggestions based on their matching score."""
        return sorted(suggestions.items(), key=lambda x: self.get_score(x[0], text), reverse=True)


    def _cache_suggestions(self, text, sorted_suggestions, pattern):
        """Cache the current suggestions for potential reuse."""
        self.previous_text = text
        self.previous_suggestions = sorted_suggestions
        self.previous_pattern = pattern


# --------------------------------------
# Score Calculation
# --------------------------------------
    def get_score(self, suggestion, text):
        """Calculate a score for the suggestion based on its similarity to the input text."""
        score = 0
        if suggestion == text:
            return len(text) * 2
        for suggestion_char, input_char in zip(suggestion, text):
            if suggestion_char == input_char:
                score += 1
            else:
                break
        classifier_id, _ = self.autocomplete_dict.get(suggestion, ('', []))
        if not classifier_id and suggestion.startswith(text[:3]):
            score += 1
        return score
