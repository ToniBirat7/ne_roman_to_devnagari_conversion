"""
Test accuracy of the new transliterator against the dataset.
"""

import json
import os
import sys

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Add src to python path
sys.path.insert(0, os.path.join(script_dir, 'nepali_romanizer', 'src'))

from nepali_romanizer.transliterator import transliterate

# Load dataset
dataset_path = os.path.join(script_dir, 'Roman_to_Devnagari_Custom', 'csv_nepali_roman_devanagari.json')
with open(dataset_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

correct = 0
total = 0
errors = []

for i, sample in enumerate(data):
    expected = sample.get('devanagari', '').strip()
    roman = sample.get('roman', '').strip()
    
    if not roman or not expected:
        continue
    
    result = transliterate(roman)
    
    # Normalize both for comparison
    # Remove zero-width chars, normalize quotes
    def normalize(s):
        s = s.replace('\u200b', '').replace('\u200c', '').replace('\u200d', '')
        s = s.replace(''', "'").replace(''', "'").replace('"', '"').replace('"', '"')
        return s
    
    expected_norm = normalize(expected)
    result_norm = normalize(result)
    
    total += 1
    
    if result_norm == expected_norm:
        correct += 1
    # Also count as correct if only spacing differs
    elif ''.join(result_norm.split()) == ''.join(expected_norm.split()):
        correct += 1
    else:
        errors.append({
            'idx': i,
            'roman': roman,
            'expected': expected,
            'got': result
        })

print(f"Accuracy: {correct}/{total} = {100*correct/total:.2f}%")

with open('errors.txt', 'w', encoding='utf-8') as f:
    f.write(f"Accuracy: {correct}/{total} = {100*correct/total:.2f}%\n\n")
    for e in errors:
        f.write(f"[{e['idx']}] Roman: {e['roman']}\n")
        f.write(f"  Expected: {e['expected']}\n")
        f.write(f"  Got:      {e['got']}\n")
        f.write("-" * 40 + "\n")

print("Errors written to errors.txt")

# Analyze error patterns
print("\n" + "="*50)
print("ERROR PATTERN ANALYSIS")
print("="*50)

# Check how many are word-for-word matches (ignoring joining)
word_by_word_correct = 0
for e in errors:
    expected_words = e['expected'].split()
    got_words = e['got'].split()
    # Simple normalization to check if content represents same characters
    if "".join(expected_words) == "".join(got_words):
         word_by_word_correct += 1

print(f"\nCharacter-exact matches (ignoring spaces): {word_by_word_correct}")

# Count joining errors (expected has fewer words than got)
joining_errors = sum(1 for e in errors if len(e['expected'].split()) < len(e['got'].split()))
print(f"Joining errors (expected has fewer words): {joining_errors}")
