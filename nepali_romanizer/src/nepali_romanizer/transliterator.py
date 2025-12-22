"""
Robust Nepali Roman to Devanagari Transliterator.
"""

from typing import List, Tuple, Dict, Optional

# =============================================================================
# DATASETS
# =============================================================================

# Common words that violate strict phonetic rules or have standard spellings
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
    'tya': 'त्या', # maybe typo
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
    'ma': 'म', # Default to Pronoun 'ma'. Suffix 'ma' handled separately.
    'ra': 'र',
    'tara': 'तर',
    'ani': 'अनि',
    'ki': 'कि', # conjunction
    'yadi': 'यदि',
    'bhanda': 'भन्दा',
    'sanga': 'सँग',
    'baarema': 'बारेमा', # about
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
    'passport': 'राहदानी', # Or passport?
    'video': 'भिडियो',
    'youtube': 'युट्युब', # standardized
    'facebook': 'फेसबुक',
    'internet': 'इन्टरनेट',
    'online': 'अनलाइन',
    'phone': 'फोन',
    'mobile': 'मोबाइल',
    'number': 'नम्बर',
    'doctor': 'डाक्टर',
    'nurse': 'नर्स',
    'hospital': 'अस्पताल',
    'restaurant': 'रेष्टुरेन्ट', # or रेस्टुरेन्ट
    'dollar': 'डलर',
}

# Postpositions to JOIN if found after a word (space separated)
JOINABLE_POSTPOSITIONS = {
    'ma', 'ko', 'le', 'lai', 'bata', 'sanga', 'dekhi', 'kai', 'bhanda', 'haru',
    'chha', 'chhu', 'chhan', 'chhau', 'hunchha', 'thiyo', 'thiye', # Verb endings sometimes separated?
    'bhane', # kina bhane -> kinabhane
}

# Words that should NOT join with following postpositions (usually)
NO_JOIN_PREV = {
    'ra', 'tara', 'ani', 'ki', 'ke', 'ho', 'chha', 'chhan', 'thiyo', 'ma'
}

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
    'gy': 'ज्ञ', 'tra': 'त्र', 'ksha': 'क्ष', 'kshya': 'क्ष्य'
}

VOWEL_INDEPENDENT = {
    'a': 'अ', 'aa': 'आ',
    'i': 'इ', 'ee': 'ई',
    'u': 'उ', 'oo': 'ऊ',
    'e': 'ए', 'ai': 'ऐ',
    'o': 'ओ', 'au': 'औ',
    'ri': 'ऋ',
}

VOWEL_SIGNS = {
    'aa': 'ा',
    'a': '', # Inherent vowel - valid matra (empty)
    'i': 'ि', 'ee': 'ी',
    'u': 'ु', 'oo': 'ू',
    'e': 'े', 'ai': 'ै',
    'o': 'ो', 'au': 'ौ',
    'ri': 'ृ',
}

# Suffix Mappings for `transliterate_word_smart`
SUFFIXES = {
    'ma': 'मा',
    'ko': 'को',
    'ka': 'का',
    'ki': 'की',
    'le': 'ले',
    'lai': 'लाई',
    'bata': 'बाट',
    'sanga': 'सँग',
    'dekhi': 'देखि',
    'bhanda': 'भन्दा',
    'haru': 'हरू',
    'chha': 'छ',
    'chhu': 'छु',
    'chhan': 'छन्',
    'dai': 'दै',
    'eko': 'एको',
    'iera': 'िएर',
    'era': 'एर',
    'nu': 'नु',
    'ne': 'ने',
    'na': 'न',
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
    
    # Capitalized Acronyms (Simple check)
    if word.isupper() and len(word) > 1:
        if word == "UK": return "UK" # Exceptions...
        # return word # Retain Roman for Acronyms? or Transliterate?
        # Dataset mix. Let's try to map if simple.
    
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
            # Consonant Logic
            res.append(match_val)
            i += len(match)
            
            # Check for following vowel
            vmatch = None
            vmatch_matra = None
            
            # Lookahead for matra
            # Check multi-char vowels first (aa, ai...)
            for v in ['aa', 'ai', 'au', 'ee', 'oo', 'ri']:
                 if word_lower.startswith(v, i):
                     vmatch = v
                     vmatch_matra = VOWEL_SIGNS[v]
                     break
            
            if not vmatch:
                 # Check single char vowels
                 c = word_lower[i] if i < length else ''
                 if c in VOWEL_SIGNS: # a, i, u, e, o
                      # 'a' handling: no matra (inherent schwa), unless it's explicitly 'a'
                      # BUT 'a' key logic:
                      # If vowel is 'a', it adds NOTHING (Inherent).
                      # IF vowel is NOT 'a', adds matra.
                      if c == 'a':
                          vmatch = 'a'
                          vmatch_matra = '' # Inherent
                      else:
                          vmatch = c
                          vmatch_matra = VOWEL_SIGNS[c]

            if vmatch:
                res.append(vmatch_matra)
                i += len(vmatch)
                
                # Check Nasal 'n' or 'm' after vowel
                # e.g. 'aa' + 'n' -> Chandrabindu?
                # Heuristics:
                # 'aan' at end of word -> 'ाँ' (usually).
                # 'in' at end of word -> 'िँ' (usually).
                # 'aun' -> 'ौँ'.
                if i < length and word_lower[i] == 'n':
                   # Check if 'n' is followed by vowel -> then it is 'na' syllable, not nasal.
                   # Check if 'n' is followed by consonant -> could be Anusvara or Half-N.
                   # Check if 'n' is End of Word -> Chandrabindu common for 'aan', 'in'.
                   
                   is_end = (i + 1 == length)
                   next_char_is_vowel = (i + 1 < length) and (word_lower[i+1] in 'aeiou')
                   
                   if not next_char_is_vowel:
                        # Candidate for nasal
                        # If 'aa' + 'n' (End): 'kahaan' -> 'कहाँ'.
                        if vmatch == 'aa' and is_end:
                            # Replace last char (matra 'ा') with 'ाँ'?
                            # No, append Chandrabindu.
                            # 'ा' + 'ँ' = 'ाँ'.
                            res.append('ँ') 
                            i += 1
                        # If 'au' + 'n' (End): 'aau' -> 'आउ' + 'n'. 'chhaun' -> 'छौं'.
                        elif vmatch == 'au' and is_end:
                             # 'au' matra is 'ौ'. Add anusvara 'ं' or chandrabindu?
                             # chhaun -> छौं (dot). 'aun' -> ौँ.
                             # Standard Nepali: plural often 'an' -> 'न्'.
                             # suffix 'chhau' (you are). 'chhaun' (they/we?).
                             pass # Leave as 'n' (half) for now to be safe: 'न्'
                        
                        # General 'n' -> 'न्' (Half Na).
                        # Let the next loop handle 'n' as consonant if we don't consume it here.
                        pass
                
            else:
                # No vowel follows (Schwa or Halant)
                # If end of word -> Keep Full (Implicit Schwa).
                # If middle of word -> Add Halant (Conjunct).
                if i < length:
                    res.append('\u094D') # Halant
            continue

        # 2. Independent Vowels
        # Only if NOT preceded by consonant (already handled above).
        # So this runs if we are at start of word, or after another vowel.
        vmatch = None
        vmatch_val = None
        for v in ['aa', 'ai', 'au', 'ee', 'oo', 'ri']:
            if word_lower.startswith(v, i):
                 vmatch = v
                 vmatch_val = VOWEL_INDEPENDENT[v]
                 break
        if not vmatch:
             # Single char
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
    
    # 1. Learned/Common Dictionary
    if word_lower in LEARNED_WORDS:
        return LEARNED_WORDS[word_lower]
        
    # 2. Suffix Handling
    best_suffix = None
    for suffix in SORTED_SUFFIXES:
        if word_lower.endswith(suffix):
            stem = word[:-len(suffix)]
            if len(stem) >= 2: # Min stem length
                best_suffix = suffix
                break
    
    if best_suffix:
        suffix_dev = SUFFIXES[best_suffix]
        stem = word[:-len(best_suffix)]
        
        # Check if stem is learned
        stem_lower = stem.lower()
        if stem_lower in LEARNED_WORDS:
             # Special join rules?
             # 'uniharu' -> 'uni' (learned?) + 'haru'.
             # dictionary has 'uniharu'.
             # if stem is 'ghar' -> 'घर'.
             # suffix 'ma' -> 'मा'.
             # 'gharma' -> 'घरमा'.
             return LEARNED_WORDS[stem_lower] + suffix_dev
        
        # Else Phonetic Stem
        return transliterate_phonetic(stem) + suffix_dev

    # 3. Post-Processing Rules (word-final i/u)
    # Apply to purely phonetic result
    res = transliterate_phonetic(word)
    
    # Heuristic: Word ending in 'i' usually 'ी', 'u' usually 'ू'.
    if word_lower.endswith('i') and not word_lower.endswith('ai'): 
        # e.g. 'pani' -> 'पनि' (also) - EXCEPT 'pani' (water) is 'पानी'.
        # ambiguous. 'pni' -> 'पनि'.
        # dataset: 'kehi' -> 'केही'.
        # 'nepali' -> 'नेपाली'. (ee)
        # Convert final 'ि' to 'ी'?
        if res.endswith('ि'):
            res = res[:-1] + 'ी'
            
    if word_lower.endswith('u') and not word_lower.endswith('au'):
        # 'aafu' -> 'आफू'.
        # 'siknu' -> 'सिक्नु' (verb - short u).
        # Verbs usually short u. Nouns long?
        # Safe to leave short u for verbs, which are common.
        pass

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
            # Allow joining multiple times? 'ghar' + 'ma' + 'le' (ungrammatical but possible structure)
            
            # Check Next Token (should be space/sep) and NextNext (word)
            has_joined = False
            
            if i + 2 < length:
                type_b, val_b = tokens[i+1] # Separator
                type_c, val_c = tokens[i+2] # Next Word
                
                # Check if we should join val_c to val_a
                # Criteria: val_b is space
                # val_c is in JOINABLE_POSTPOSITIONS
                # val_a is NOT in NO_JOIN_PREV
                
                if val_b == ' ' and type_c == 'word':
                     if val_c.lower() in JOINABLE_POSTPOSITIONS:
                         if val_a.lower() not in NO_JOIN_PREV:
                             # DO JOIN
                             # Construct combined word
                             # But we might want to lookup `val_a` individually?
                             # Better: Combine string "val_a val_c" -> "val_aval_c" and process?
                             # Or process val_a, process val_c (as suffix), and concat?
                             # "ghar" "ma" -> "ghar" + "ma" -> "घर" + "मा" -> "घरमा".
                             # "kina" "bhane" -> "kinabhane" -> dictionary "किनभने".
                             
                             # Try combined lookup first
                             combined_raw = val_a + val_c
                             combined_res = transliterate_word_smart(combined_raw)
                             
                             # If combined result looks like just phonetic concat, maybe better to do safe join?
                             # Actually `transliterate_word_smart` handles suffixes.
                             
                             result.append(combined_res)
                             i += 3 # Skip a, b, c
                             continue
            
            # Normal Word
            result.append(transliterate_word_smart(val_a))
            i += 1
            
        else:
            # Separator
            if val_a in PUNCTUATION:
                result.append(PUNCTUATION[val_a])
            else:
                result.append(val_a)
            i += 1
            
    return "".join(result)
