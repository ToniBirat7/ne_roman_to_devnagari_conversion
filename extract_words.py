"""Extract all word mappings from dataset using smarter alignment."""
import json
from collections import defaultdict
import re

DATA_FILE = 'Roman_to_Devnagari_Custom/csv_nepali_roman_devanagari.json'
OUTPUT_FILE = 'learned_words.py'

with open(DATA_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

def clean_text(text):
    """Clean text by removing punctuation."""
    return re.sub(r'[,।\.\?!;:\[\]]', '', text)

# Extract word pairs from ALL sentences
# Use multiple strategies:
word_pairs = defaultdict(lambda: defaultdict(int))

for item in data:
    roman = item['roman']
    dev = item['devanagari']
    
    # Strategy 1: Direct word alignment (same word count)
    r_clean = clean_text(roman)
    d_clean = clean_text(dev)
    r_words = r_clean.lower().split()
    d_words = d_clean.split()
    
    if len(r_words) == len(d_words):
        for r, d in zip(r_words, d_words):
            if r and d:
                word_pairs[r][d] += 1
    
    # Strategy 2: Even for different word counts, extract obvious pairs
    # Look for isolated words that might match
    for r in r_words:
        # Check if there's exactly one devanagari word that could be the match
        possible_matches = []
        for d in d_words:
            # Simple heuristic: if roman and dev start with similar sounds
            # This is a rough filter
            if len(d) >= 2:
                possible_matches.append(d)
        
        # If we have context from other sentences, prefer the known match
        if r in word_pairs and len(word_pairs[r]) > 0:
            continue  # Already have data for this word

# Find the most common mapping for each word
final_mappings = {}
for r, dev_counts in word_pairs.items():
    if len(dev_counts) == 1:
        # Only one mapping - use it
        d = list(dev_counts.keys())[0]
        count = dev_counts[d]
        if count >= 1:  # Include even single occurrences
            final_mappings[r] = d
    else:
        # Multiple mappings - use the most common one if it's dominant
        sorted_devs = sorted(dev_counts.items(), key=lambda x: -x[1])
        top_dev, top_count = sorted_devs[0]
        second_count = sorted_devs[1][1] if len(sorted_devs) > 1 else 0
        # Use if top is significantly more common (at least 2x more)
        if top_count >= 2 and top_count >= second_count * 1.5:
            final_mappings[r] = top_dev

# Add some manual corrections for common English loanwords
loanwords = {
    'airport': 'एयरपोर्ट',
    'hotel': 'होटल',
    'dollar': 'डलर',
    'bus': 'बस',
    'station': 'स्टेशन',
    'book': 'बुक',
    'restaurant': 'रेस्टुरेन्ट',
    'ticket': 'टिकट',
    'hospital': 'अस्पताल',
    'doctor': 'डाक्टर',
    'phone': 'फोन',
    'mobile': 'मोबाइल',
    'computer': 'कम्प्युटर',
    'internet': 'इन्टरनेट',
    'email': 'इमेल',
    'name': 'नाम',
    'number': 'नम्बर',
}
final_mappings.update(loanwords)

# Additional common words that might be missing
common_fixes = {
    'nepal': 'नेपाल',
    'nepali': 'नेपाली',
    'kehi': 'केही',
    'tarkari': 'तरकारी',
    'phalaphul': 'फलफूल',
    'kinna': 'किन्न',
    'jaandai': 'जाँदै',
    'tapaai': 'तपाईं',
    'tapai': 'तपाईं',
    'tapaiin': 'तपाईं',
    'tapaain': 'तपाईं',
    'tapain': 'तपाईं',
    'tapaailaai': 'तपाईंलाई',
    'tapailaai': 'तपाईंलाई',
    'tapaainlaai': 'तपाईंलाई',
    'tapaainle': 'तपाईंले',
    'tapainle': 'तपाईंले',
    'chaahieema': 'चाहिएमा',
    'chahiema': 'चाहिएमा',
    'sodhna': 'सोध्न',
    'garna': 'गर्न',
    'basne': 'बस्ने',
    'jaanna': 'जान्न',
    'batauna': 'बताउन',
    'saatna': 'साट्न',
    'kathmandu': 'काठमाडौं',
    'khaana': 'खाना',
    'khana': 'खाना',
    'paani': 'पानी',
    'pani': 'पानी',
    'nyaano': 'न्यानो',
    'kotha': 'कोठा',
    'thau': 'ठाउँ',
    'hun': 'हुँ',
    'hunchha': 'हुन्छ',
    'chahanchhu': 'चाहन्छु',
    'saknuhunchha': 'सक्नुहुन्छ',
    'ameriki': 'अमेरिकी',
    'rupaiyaan': 'रुपैयाँ',
    'rupaiyan': 'रुपैयाँ',
    'sanskriti': 'संस्कृति',
    'parampara': 'परम्परा',
    'paramparagat': 'परम्परागत',
    'baarema': 'बारेमा',
    'barema': 'बारेमा',
    'pugne': 'पुग्ने',
    'aarakshan': 'आरक्षण',
    'arakshan': 'आरक्षण',
    'mahasus': 'महसुस',
    'bhairaaheko': 'भइरहेको',
    'bhairaheko': 'भइरहेको',
    'laagchha': 'लाग्छ',
    'lagchha': 'लाग्छ',
    'jwaro': 'ज्वरो',
    'aayeko': 'आएको',
    'ayeko': 'आएको',
    'ghumna': 'घुम्न',
    'sifaaris': 'सिफारिस',
    'sifaris': 'सिफारिस',
    'khojdai': 'खोज्दै',
    'paine': 'पाइने',
    'mausam': 'मौसम',
    'ghamaailo': 'घमाइलो',
    'ghamailo': 'घमाइलो',
    'hijo': 'हिजो',
    'aaipugeko': 'आइपुगेको',
    'aipugeko': 'आइपुगेको',
    'hapta': 'हप्ता',
    'yojana': 'योजना',
    'maddat': 'मद्दत',
    'najikkai': 'नजिकै',
    'najikko': 'नजिकको',
    # Compound words that should be together
    'kinabhane': 'किनभने',
}
final_mappings.update(common_fixes)

# Write to file
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(f'# Learned word mappings from dataset (auto-extracted + manual corrections)\n')
    f.write(f'# Total: {len(final_mappings)} words\n\n')
    f.write('LEARNED_WORDS = {\n')
    for r, d in sorted(final_mappings.items()):
        f.write(f"    '{r}': '{d}',\n")
    f.write('}\n')

print(f'Wrote {len(final_mappings)} word mappings to {OUTPUT_FILE}')
