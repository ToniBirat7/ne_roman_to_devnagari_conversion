import sys
sys.path.append('nepali_romanizer/src')

from nepali_romanizer.transliterator import transliterate_phonetic, transliterate, VOWEL_SIGNS

print("VOWEL_SIGNS keys:", list(VOWEL_SIGNS.keys()))
print("'a' in VOWEL_SIGNS:", 'a' in VOWEL_SIGNS)

words = ["bajaar", "bajaarma", "purna", "tarkari", "airport"]
for w in words:
    print(f"Word: {w}")
    print(f"Phonetic: {transliterate_phonetic(w)}")
    print(f"Full: {transliterate(w)}")
    print("-" * 20)
