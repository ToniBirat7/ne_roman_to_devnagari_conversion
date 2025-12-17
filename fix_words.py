"""
Fix common word errors by analyzing the dataset and updating word_dict.
"""

import json
import os
import sys
import re
from collections import Counter

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, 'nepali_romanizer', 'src'))

from nepali_romanizer.transliterator import transliterate, WORD_DICT

# Load dataset
dataset_path = os.path.join(script_dir, 'Roman_to_Devnagari_Custom', 'csv_nepali_roman_devanagari.json')
with open(dataset_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

def clean(s):
    return re.sub(r'[।,?!;:\[\]()"\'…\u200b\u200c\u200d]', '', s).strip()

# Collect word-level errors
word_errors = Counter()
word_corrections = {}

for sample in data:
    expected = sample.get('devanagari', '').strip()
    roman = sample.get('roman', '').strip()
    
    if not roman or not expected:
        continue
    
    result = transliterate(roman)
    
    if result == expected:
        continue
    
    # Compare word by word for same-length sentences
    exp_words = expected.split()
    got_words = result.split()
    rom_words = roman.split()
    
    if len(exp_words) == len(got_words) == len(rom_words):
        for r, exp, got in zip(rom_words, exp_words, got_words):
            r_clean = clean(r).lower()
            exp_clean = clean(exp)
            got_clean = clean(got)
            
            if exp_clean != got_clean and r_clean and exp_clean:
                word_errors[(r_clean, exp_clean, got_clean)] += 1
                word_corrections[r_clean] = exp_clean

print("=== MOST COMMON WORD ERRORS ===\n")
for (r, exp, got), count in word_errors.most_common(50):
    print(f"{r:25} -> got '{got}' expected '{exp}' ({count}x)")

print(f"\n\nTotal unique word corrections needed: {len(word_corrections)}")

# Filter to high-confidence corrections (appear multiple times)
high_conf_corrections = {r: exp for (r, exp, got), count in word_errors.most_common() 
                         if count >= 2 for r2, exp2, got2 in [(r, exp, got)] if r2 == r}

print(f"High-confidence corrections (2+ occurrences): {len(high_conf_corrections)}")

# Generate the fix code
print("\n\n=== FIXES TO ADD TO word_dict.py ===\n")
print("# Add these to manual_fixes in extract script or directly to word_dict.py")
print("fixes = {")
for r, exp in sorted(high_conf_corrections.items())[:100]:
    if r not in WORD_DICT or WORD_DICT[r] != exp:
        print(f"    '{r}': '{exp}',")
print("}")
