"""
Prune learned_words.py to keep only true exceptions: English acronyms, loanwords, quoted/parenthesized/number/foreign terms.
"""
import re

infile = 'nepali_romanizer/src/nepali_romanizer/learned_words.py'
outfile = infile

# Patterns to keep: acronyms, quoted, parenthesized, numbers, non-Nepali
keep_patterns = [
    re.compile(r"^[A-Za-z]{2,}$"),  # acronyms/loanwords
    re.compile(r"^[\(\"\']"),   # quoted or parenthesized
    re.compile(r"^[0-9\-\+\*%]+$"),  # numbers/symbols
    re.compile(r"[A-Z]"),  # any uppercase (likely foreign)
]

key_re = re.compile(r"\s*'([^']+)': ")

with open(infile, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    m = key_re.match(line)
    if m:
        key = m.group(1)
        if not any(p.match(key) for p in keep_patterns):
            continue  # skip common Nepali words
    new_lines.append(line)

with open(outfile, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"Pruned {outfile} to keep only true exceptions.")
