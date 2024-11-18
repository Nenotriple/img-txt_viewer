"""This script reads a CSV file and filters rows based on a blacklist of words."""


import csv
import re


# Function to check if any blacklisted word is in the specified columns
def is_blacklisted(row, blacklist):
    """Check if any blacklisted word is in the specified columns."""
    for word, partial_match in blacklist.items():
        if partial_match:
            pattern = re.escape(word)
        else:
            pattern = r'\b' + re.escape(word) + r'\b'
        if any(re.search(pattern, column) for column in (row[0], row[3])):
            return True
    return False


# Read the CSV file and filter rows
def filter_csv(input_file, output_file, blacklist):
    """Read the CSV file and filter rows based on the blacklist and column one entry value."""
    with open(input_file, mode='r', newline='', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        filtered_rows = [row for row in reader if not is_blacklisted(row, blacklist) and row[1] != "1"]
    # Write the filtered rows to a new CSV file
    with open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(filtered_rows)


# Define the blacklist; True for partial match, False for exact match
blacklist = {
    "breast": True,
    "boob": True,
    "nipple": True,
    "pussy": True,
    "vagina": True,
    "clit": True,
    "labia": True,
    "ass": False,
    "ass_": True,
    "ass-": True,
    "anus": True,
    "dildo": True,
    "panties": True,
    "panty": True,
    "thighhighs": True,
    "cleavage": False,
    "bikini": True,
    "lingerie": True,
    "swimsuit": True,
    "intercourse": True,
    "penetration": True,
    "masturbation": True,
    "handjob": True,
    "blowjob": True,
    "threesome": True,
    "foursome": True,
    "anal": True,
    "ejaculation": True,
    "creampie": True,
    "facial": True,
    "orgasm": True,
    "69_position": True,
    "fornication": True,
    "hardcore": True,
    "softcore": True,
    "cunnilingus": True,
    "fellatio": True,
    "gangbang": True,
    "voyeurism": True,
    "exhibitionism": True,
    "incest": True,
    "bestiality": True,
    "rape": True,
    "molestation": True,
    "assault": True,
    "roleplay": False,
    "hentai": True,
    "doujin": True,
    "tentacle": True,
    "futa": True,
    "furry": True,
    "bdsm": True,
    "loli": False,
    "oppai_loli": False,
    "_loli": False,
    "_loli_": False,
    "loli_": False,
    "shota": True,
    "yaoi": True,
    "yuri": True,
    "ecchi": True,
    "cum": True,
    "bondage": True,
    "seductive": True,
    "revealing": True,
    "barely_visible": True,
    "suggestive": True,
    "rape": True,
    "nude": True,
    "busty": True,
    "hyper": True,
    "fetish": True,
    "skin_tight": True,
    "see_through": True,
    "strip": True,
    "spread": True,
    "gape": True,
    "scantily_clad": False,
    "buxom": True,
    "naked": True,
    "crotch": True,
    "erotic": True,
    "sex": True,
    "provocative": True,
    "dominatrix": True,
    "vulgar": True,
    "intimate": True,
    "kinky": True,
    "undress": True,
    "sensual": True,
    "smell": True,
    "lick": True,
    "armpit": True,
    "penis": True,
    "erection": True,
    "testicle": True,
    "hetero": True,
    "censor": True,
    "guro": False,
    "flaccid": False,
    "legjob": False,
    "paizuri": True,
    "footjob": True,
    "buttjob": True,
    "hairjob": True,
    "glansjob": False,
    "nosejob": False,
    "facejob": False,
    "sleevejob": False,
    "sockjob": False,
    "hornjob": False,
}


# Filter the CSV file
filter_csv("danbooru.csv", "filtered_danbooru.csv", blacklist)
