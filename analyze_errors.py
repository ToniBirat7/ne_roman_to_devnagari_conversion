"""Analyze the most common word-level errors."""
import json
from collections import Counter

with open('errors.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# Parse errors
errors = []
current = {}
for line in content.split('\n'):
    if line.startswith('['):
        if current:
            errors.append(current)
        current = {}
    elif line.startswith('  Expected:'):
        current['expected'] = line.replace('  Expected: ', '')
    elif line.startswith('  Got:'):
        current['got'] = line.replace('  Got:      ', '')

if current:
    errors.append(current)

# Find word-level mismatches
word_errors = Counter()
for e in errors:
    if 'expected' not in e or 'got' not in e:
        continue
    exp_words = e['expected'].split()
    got_words = e['got'].split()
    # Simple comparison: find words that differ at same position
    for i, (ew, gw) in enumerate(zip(exp_words, got_words)):
        if ew != gw:
            word_errors[(gw, ew)] += 1

print("Most common word-level errors (got -> expected):")
for (got, exp), count in word_errors.most_common(50):
    print(f"  {got} -> {exp}: {count}")
