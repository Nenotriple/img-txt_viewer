#region - Imports


import re
import os


#endregion
################################################################################################################################################
#region - Tag Editor


def analyze_tags(text_files):
    """
    This method processes text files to extract tags and their
    positions, storing them in a dictionary. Keys are tags, and
    values are lists of tuples with the file index and tag position.
    Returns:
        dict: Dictionary with tags (str) as keys and lists of tuples as values.
            Each tuple contains the file index (int) and tag position (int).
    """
    text_files = _validate_files(text_files)
    tags = {}
    for file_index, file_path in enumerate(text_files):
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            extracted_tags = _extract_tags(content)
            for tag, position in extracted_tags:
                if tag not in tags:
                    tags[tag] = []
                tags[tag].append((file_index, position))
    return tags


def edit_tags(text_files, tags, delete=False, edit=None):
    """
    This method processes text files to delete or edit specified tags.
    If the delete flag is True, tags are removed. If an edit string is
    provided, tags are replaced with it.
    Args:
        tags (list): List of tags (str)
        delete (bool): Flag to delete tags (default: False)
        edit (str): String to replace tags (if None, delete tags)
    """
    text_files = _validate_files(text_files)
    for file_index, file_path in enumerate(text_files):
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        for tag in tags:
            if delete:
                content = content.replace(tag, '')
            elif edit is not None:
                content = content.replace(tag, edit)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)


def _extract_tags(text):
    """
    This method standardizes delimiters by replacing periods with
    commas, then uses a regular expression to find tags and their
    starting positions. It returns a list of tuples with each tag
    and its starting position.
    """
    text = text.replace('.', ',')
    raw_tags = re.finditer(r'[^,]+', text)
    tags = [(tag, match.start()) for match in raw_tags if (tag := match.group().strip())]
    return tags


def _validate_files(text_files):
    """
    This method checks if the text files provided in the constructor
    exist. If a file does not exist, it is removed from the list of
    text files to process.
    """
    text_files = [file for file in text_files if os.path.exists(file)]
    return text_files
