"""
Robust Nepali Roman to Devanagari Transliterator.
"""

from typing import List, Tuple, Dict, Optional, Union

# =============================================================================
# DATASETS
# =============================================================================

LEARNED_WORDS = {
    'ma': 'म',
    'ta': 'त',
    'cha': 'छ',
    'chha': 'छ',
    'chhu': 'छु',
    'chhan': 'छन्',
    'chhau': 'छौ',
    'ho': 'हो',
    'haina': 'होइन',
    'thiyo': 'थियो',
    'thiye': 'थिए',
    'bhaeko': 'भएको',
    'bhayeko': 'भएको',
    'garna': 'गर्न',
    'garne': 'गर्ने',
    'garyo': 'गर्‍यो',
    'garda': 'गर्दा',
    'hunu': 'हुनु',
    'hunchha': 'हुन्छ',
    'hunuhunchha': 'हुनुहुन्छ',
    'sakchha': 'सक्छ',
    'saknu': 'सक्नु',
    'saknuhunchha': 'सक्नुहुन्छ',
    
    # Pronouns
    'tapaai': 'तपाईं',
    'tapaain': 'तपाईं',
    'tapai': 'तपाईं',
    'timi': 'तिमी',
    'timiharu': 'तिमीहरू',
    'hami': 'हामी',
    'hamro': 'हाम्रो',
    'mero': 'मेरो',
    'tero': 'तेरो',
    'usko': 'उसको',
    'uniko': 'उनको',
    'uniharu': 'उनीहरू',
    'yo': 'यो',
    'tyo': 'त्यो',
    'yi': 'यी',
    'tya': 'त्या',
    'tyahi': 'त्यही',
    'uha': 'उहाँ',
    'uhaan': 'उहाँ',
    
    # Particles/Question words
    'ke': 'के',
    'kun': 'कुन',
    'kina': 'किन',
    'kinabhane': 'किनभने',
    'kasari': 'कसरी',
    'kahile': 'कहिले',
    'kata': 'कता',
    'kaha': 'कहाँ',
    'kahaan': 'कहाँ',
    'ko': 'को',
    'le': 'ले',
    'lai': 'लाई',
    'ra': 'र',
    'tara': 'तर',
    'ani': 'अनि',
    'ki': 'कि',
    'yadi': 'यदि',
    'bhanda': 'भन्दा',
    'sanga': 'सँग',
    'baarema': 'बारेमा',
    'barema': 'बारेमा',
    
    # Common Nouns/Adverbs
    'aaja': 'आज',
    'hijo': 'हिजो',
    'bholi': 'भोलि',
    'sabai': 'सबै',
    'dherai': 'धेरै',
    'ali': 'अलि',
    'alikati': 'अलिकति',
    'ramro': 'राम्रो',
    'naramro': 'नराम्रो',
    'thik': 'ठीक',
    'dhanyabad': 'धन्यवाद',
    'namaste': 'नमस्ते',
    'nepal': 'नेपाल',
    'nepali': 'नेपाली',
    'angreji': 'अंग्रेजी',
    'english': 'अंग्रेजी',
    
    # English Loanwords common in dataset
    'london': 'लन्डन',
    'airport': 'एयरपोर्ट',
    'hotel': 'होटल',
    'bus': 'बस',
    'station': 'स्टेशन',
    'ticket': 'टिकट',
    'passport': 'राहदानी', 
    'video': 'भिडियो',
    'youtube': 'युट्युब', 
    'facebook': 'फेसबुक',
    'internet': 'इन्टरनेट',
    'online': 'अनलाइन',
    'phone': 'फोन',
    'mobile': 'मोबाइल',
    'number': 'नम्बर',
    'doctor': 'डाक्टर',
    'nurse': 'नर्स',
    'hospital': 'अस्पताल',
    'restaurant': 'रेष्टुरेन्ट',
    'dollar': 'डलर',
    
    # Specific corrections
    'tarkari': 'तरकारी',
    'bazar': 'बजार',
    'bajaar': 'बजार',
    'paine': 'पाइने',
    'khojdai': 'खोज्दै',
    'pathayeko': 'पठाएको',
    'aayeko': 'आएको',
    'gayeko': 'गएको',
    'bhayaeko': 'भएको',
}

# Postpositions to JOIN if found after a word (space separated)
JOINABLE_POSTPOSITIONS = {
    'ma', 'ko', 'le', 'lai', 'bata', 'sanga', 'dekhi', 'kai', 'bhanda', 'haru',
    'chha', 'chhu', 'chhan', 'chhau', 'hunchha', 'thiyo', 'thiye',
    'bhane', 
}

NO_JOIN_PREV = {
    'ra', 'tara', 'ani', 'ki', 'ke', 'ho', 'chha', 'chhan', 'thiyo', 'ma'
}

CHHA_GROUP = {'chha', 'chhu', 'chhan', 'chhau', 'hunchha', 'thiyo', 'thiye'}

# =============================================================================
# MAPPINGS
# =============================================================================

CONSONANT_MAP = {
    'k': 'क', 'kh': 'ख', 'g': 'ग', 'gh': 'घ', 'ng': 'ङ',
    'ch': 'च', 'chh': 'छ', 'j': 'ज', 'jh': 'झ', 'yn': 'ञ',
    't': 'त', 'th': 'थ', 'd': 'द', 'dh': 'ध', 'n': 'न',
    'p': 'प', 'ph': 'फ', 'b': 'ब', 'bh': 'भ', 'm': 'म',
    'y': 'य', 'r': 'र', 'l': 'ल', 'w': 'व', 'v': 'व',
    's': 'स', 'sh': 'श', 'shh': 'ष', 'h': 'ह',
    'gy': 'ज्ञ', 'tra': 'त्र', 'ksha': 'क्ष', 'kshya': 'क्ष्य',
    'f': 'फ', 'z': 'ज', 'c': 'क', 'q': 'क', 'x': 'क्स'
}

VOWEL_INDEPENDENT = {
    'a': 'अ', 'aa': 'आ',
    'i': 'इ', 'ee': 'ई',
    'u': 'उ', 'oo': 'ऊ',
    'e': 'ए', 'ai': 'ऐ',
    'o': 'ओ', 'au': 'ौ',
    'ri': 'ऋ',
}

VOWEL_SIGNS = {
    'aa': 'ा',
    'a': '',
    'i': 'ि', 'ee': 'ी',
    'u': 'ु', 'oo': 'ू',
    'e': 'े', 'ai': 'ै',
    'o': 'ो', 'au': 'ौ',
    'ri': 'ृ',
}

INDEP_TO_MATRA = {
    'अ': '',   'आ': 'ा',
    'इ': 'ि',   'ई': 'ी',
    'उ': 'ु',   'ऊ': 'ू',
    'ए': 'े',   'ऐ': 'ै',
    'ओ': 'ो',   'औ': 'ौ',
    'ऋ': 'ृ'
}

# Suffix Mappings: suffix -> (devanagari, mode)
SUFFIXES = {
    'ma': ('मा', False),
    'ko': ('को', False),
    'ka': ('का', False),
    'ki': ('की', False),
    'le': ('ले', False),
    'lai': ('लाई', False),
    'bata': ('बाट', False),
    'sanga': ('सँग', False),
    'dekhi': ('देखि', False),
    'bhanda': ('भन्दा', False),
    'haru': ('हरू', False),
    
    # Verb Endings
    'chha': ('छ', True),
    'chhu': ('छु', True),
    'chhan': ('छन्', True),
    'chhau': ('छौ', True),
    'dai': ('दै', True),
    'nu': ('नु', True),
    'ne': ('ने', True),
    'na': ('न', True),
    
    # Vowel Starting Verbs
    'eko': ('एको', 'VOWEL'),
    'iera': ('िएर', 'VOWEL'),
    'era': ('एर', 'VOWEL'),
}

NUMERALS = {
    '0': '०', '1': '१', '2': '२', '3': '३', '4': '४',
    '5': '५', '6': '६', '7': '७', '8': '८', '9': '९'
}

PUNCTUATION = {
    '.': '।', 
    ',': ',', '?': '?', '!': '!', ';': ';',
    ':': ':', '(': '(', ')': ')', '-': '-',
    '"': '"', "'": "'"
}

SORTED_CONSONANTS = sorted(CONSONANT_MAP.keys(), key=len, reverse=True)
SORTED_SUFFIXES = sorted(SUFFIXES.keys(), key=len, reverse=True)


# =============================================================================
# LOGIC
# =============================================================================

DEVANAGARI_CONSONANTS = set("कखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषहळक्षज्ञ")

class Tokenizer:
    @staticmethod
    def tokenize(text: str) -> List[Tuple[str, str]]:
        tokens = []
        current = []
        
        for char in text:
            if char.isalnum() or char in ["'"]:
                current.append(char)
            else:
                if current:
                    tokens.append(('word', ''.join(current)))
                    current = []
                tokens.append(('sep', char))
        
        if current:
            tokens.append(('word', ''.join(current)))
        return tokens

def transliterate_phonetic(word: str) -> str:
    """Core phonetic engine."""
    if not word: return ""
    
    if word.isupper() and len(word) > 1:
        if word == "UK": return "UK"
    
    res = []
    i = 0
    length = len(word)
    word_lower = word.lower()
    
    while i < length:
        # 1. Consonants
        match = None
        match_val = None
        for pat in SORTED_CONSONANTS:
            if word_lower.startswith(pat, i):
                match = pat
                match_val = CONSONANT_MAP[pat]
                break
        
        if match:
            res.append(match_val)
            i += len(match)
            
            # Check for following vowel
            vmatch = None
            vmatch_matra = None
            
            for v in ['aa', 'ai', 'au', 'ee', 'oo', 'ri']:
                 if word_lower.startswith(v, i):
                     vmatch = v
                     vmatch_matra = VOWEL_SIGNS[v]
                     break
            
            if not vmatch:
                 c = word_lower[i] if i < length else ''
                 if c in VOWEL_SIGNS: 
                      if c == 'a':
                          vmatch = 'a'
                          vmatch_matra = '' # Inherent
                      else:
                          vmatch = c
                          vmatch_matra = VOWEL_SIGNS[c]

            if vmatch:
                res.append(vmatch_matra)
                i += len(vmatch)
                
                # Check Nasal 'n'
                if i < length and word_lower[i] == 'n':
                   is_end = (i + 1 == length)
                   next_char_is_vowel = (i + 1 < length) and (word_lower[i+1] in 'aeiou')
                   
                   if not next_char_is_vowel:
                        if vmatch == 'aa' and is_end:
                            res.append('ँ') 
                            i += 1
                        pass
                
            else:
                # No vowel follows (Schwa)
                # Middle of word -> Halant
                if i < length:
                    res.append('\u094D')
            continue

        # 2. Independent Vowels
        vmatch = None
        vmatch_val = None
        for v in ['aa', 'ai', 'au', 'ee', 'oo', 'ri']:
            if word_lower.startswith(v, i):
                 vmatch = v
                 vmatch_val = VOWEL_INDEPENDENT[v]
                 break
        if not vmatch:
             c = word_lower[i]
             if c in VOWEL_INDEPENDENT:
                 vmatch = c
                 vmatch_val = VOWEL_INDEPENDENT[c]
        
        if vmatch:
            res.append(vmatch_val)
            i += len(vmatch)
            continue
            
        # 3. Numerals
        if word[i] in NUMERALS:
            res.append(NUMERALS[word[i]])
            i += 1
            continue
            
        # 4. Fallback
        res.append(word[i])
        i += 1
        
    return "".join(res)


def transliterate_word_smart(word: str) -> str:
    word_lower = word.lower()
    
    if word_lower in LEARNED_WORDS:
        return LEARNED_WORDS[word_lower]
        
    best_suffix = None
    for suffix in SORTED_SUFFIXES:
        if word_lower.endswith(suffix):
            stem = word[:-len(suffix)]
            if len(stem) >= 2:
                best_suffix = suffix
                break
    
    if best_suffix:
        suffix_info = SUFFIXES[best_suffix]
        suffix_dev = suffix_info[0]
        mode = suffix_info[1]
        
        stem = word[:-len(best_suffix)]
        stem_lower = stem.lower()
        
        if stem_lower in LEARNED_WORDS:
             stem_val = LEARNED_WORDS[stem_lower]
        else:
             stem_val = transliterate_phonetic(stem)
             
        # Joining Logic
        if mode == 'VOWEL':
             if stem_val:
                 last_char = stem_val[-1]
                 if last_char in DEVANAGARI_CONSONANTS:
                     indep_v = suffix_dev[0]
                     if indep_v in INDEP_TO_MATRA:
                         matra = INDEP_TO_MATRA[indep_v]
                         suffix_use = matra + suffix_dev[1:]
                         return stem_val + suffix_use
             
             return stem_val + suffix_dev
             
        elif mode == True: # Force Halant
            if stem_val:
                 last_char = stem_val[-1]
                 if last_char in DEVANAGARI_CONSONANTS:
                      stem_val += '\u094D'
        
        return stem_val + suffix_dev

    # Post-Processing
    res = transliterate_phonetic(word)
    if word_lower.endswith('i') and not word_lower.endswith('ai'): 
        if res.endswith('ि'):
            res = res[:-1] + 'ी'
    return res

def transliterate(text: str) -> str:
    if not text: return ""
    tokens = Tokenizer.tokenize(text)
    result = []
    i = 0
    length = len(tokens)
    
    while i < length:
        type_a, val_a = tokens[i]
        
        if type_a == 'word':
            # Lookahead for Join
            if i + 2 < length:
                type_b, val_b = tokens[i+1]
                type_c, val_c = tokens[i+2]
                
                if val_b == ' ' and type_c == 'word':
                     c_lower = val_c.lower()
                     if c_lower in JOINABLE_POSTPOSITIONS:
                         should_join = True
                         a_lower = val_a.lower()
                         
                         if a_lower in NO_JOIN_PREV:
                             should_join = False
                         
                         if c_lower in CHHA_GROUP:
                             if a_lower.endswith(('a', 'e', 'i', 'o', 'u')) and not a_lower.endswith('dai'):
                                  should_join = False
                         
                         if should_join:
                             combined_raw = val_a + val_c
                             combined_res = transliterate_word_smart(combined_raw)
                             result.append(combined_res)
                             i += 3 
                             continue
            
            result.append(transliterate_word_smart(val_a))
            i += 1
        else:
            if val_a in PUNCTUATION:
                result.append(PUNCTUATION[val_a])
            else:
                result.append(val_a)
            i += 1
            
    return "".join(result)
