"""
Nepali Roman to Devanagari Transliterator v3

A sophisticated rule-based transliteration engine with pattern learning.

Key insights from dataset analysis:
1. Single 'a' between consonants = inherent schwa (not written)
2. 'aa' = explicit long आ matra
3. Single 'a' before final consonant + vowel = often long ा
4. Final 'i' in content words = usually long ी
5. 'ai' at word end = ाई (long aa + independent ii)
6. 'n' before consonant after vowel = chandrabindu (nasalization)
7. Postpositions (ko, ma, lai, le) join to preceding word
8. Verb endings (chhu, chha) sometimes join to verb stems
"""

from typing import Tuple, Optional, List, Dict
import re

# =============================================================================
# UNICODE CONSTANTS
# =============================================================================

HALANT = '\u094D'       # ्
CHANDRABINDU = '\u0901' # ँ
ANUSVARA = '\u0902'     # ं
VISARGA = '\u0903'      # ः
NUKTA = '\u093C'        # ़

# =============================================================================
# PHONEME MAPPINGS
# =============================================================================

# Consonants: (roman_pattern, devanagari_base)
# Ordered by length (longest first) for greedy matching
# Consonants: (roman_pattern, devanagari_base)
# Ordered by length (longest first) for greedy matching
CONSONANTS = [
    # 4+ character combinations
    ('nchh', 'न्छ'),
    ('cchh', 'च्छ'),
    
    # 3 character - special conjuncts
    ('chh', 'छ'),
    ('ksh', 'क्ष'),
    ('gya', 'ज्ञ'),
    ('gny', 'ज्ञ'),
    ('jny', 'ज्ञ'),
    ('shr', 'श्र'),
    ('shw', 'श्व'),
    ('tra', 'त्र'),  # Special handling
    
    # 2 character - aspirated consonants
    ('kh', 'ख'),
    ('gh', 'घ'),
    ('ch', 'च'),  # specific check: if ch followed by 'a' and it is 'is', might be chha.
    ('jh', 'झ'),
    ('th', 'थ'),
    ('dh', 'ध'),
    ('ph', 'फ'),
    ('bh', 'भ'),
    ('sh', 'श'),
    ('ng', 'ङ'),
    ('ny', 'ञ'),
    ('xa', 'छ'),  # User rule: xa = छ
    
    # 2 character - double consonants (explicit conjuncts)
    ('kk', 'क्क'),
    ('gg', 'ग्ग'),
    ('cc', 'च्च'),
    ('jj', 'ज्ज'),
    ('tt', 'त्त'),
    ('dd', 'द्द'),
    ('nn', 'न्न'),
    ('pp', 'प्प'),
    ('bb', 'ब्ब'),
    ('mm', 'म्म'),
    ('yy', 'य्य'),
    ('rr', 'र्र'),
    ('ll', 'ल्ल'),
    ('ss', 'स्स'),
    
    # Single consonants
    ('k', 'क'),
    ('g', 'ग'),
    ('c', 'च'),
    ('j', 'ज'),
    ('t', 'त'),
    ('d', 'द'),
    ('n', 'न'),
    ('p', 'प'),
    ('b', 'ब'),
    ('m', 'म'),
    ('y', 'य'),
    ('r', 'र'),
    ('l', 'ल'),
    ('w', 'व'),
    ('v', 'व'),
    ('s', 'स'),
    ('h', 'ह'),
    ('q', 'क'),
    ('x', 'छ'),   # User rule: x = छ
    ('z', 'ज'),
    ('f', 'फ'),
]

# Vowels: (roman_pattern, independent_form, matra_form)
# Ordered by length for greedy matching
VOWELS = [
    # 3 character combinations
    ('aai', 'आइ', 'ाइ'),
    ('aau', 'आउ', 'ाउ'),
    ('aae', 'आए', 'ाए'),
    ('aao', 'आओ', 'ाओ'),
    
    # 2 character combinations  
    ('aa', 'आ', 'ा'),
    ('ai', 'ऐ', 'ै'),
    ('au', 'औ', 'ौ'),
    ('ou', 'औ', 'ौ'),
    ('ee', 'ई', 'ी'),
    ('ii', 'ई', 'ी'),
    ('oo', 'ऊ', 'ू'),
    ('uu', 'ऊ', 'ू'),
    ('ri', 'ऋ', 'ृ'),  # For Sanskrit loanwords
    
    # Single vowels
    ('a', 'अ', ''),   # Inherent vowel - no matra
    ('i', 'इ', 'ि'),  # Short i
    ('u', 'उ', 'ु'),  # Short u
    ('e', 'ए', 'े'),
    ('o', 'ओ', 'ो'),
]

# Punctuation mapping
PUNCTUATION = {
    '.': '।',
    ',': ',',
    '?': '?',
    '!': '!',
    ';': ';',
    ':': ':',
    '-': '-',
    '(': '(',
    ')': ')',
    '[': '[',
    ']': ']',
    '"': '"',
    "'": "'",
    '…': '...',
}

# =============================================================================
# WORD DICTIONARY (from dataset analysis)
# =============================================================================

try:
    from .word_dict import WORD_DICT
except ImportError:
    WORD_DICT = {}

# =============================================================================
# POSTPOSITIONS AND CONTEXT RULES
# =============================================================================

# Postpositions and context rules - these join to preceding word
JOINING_SUFFIXES = {
    'ko', 'ka',             # Possessive markers (NOT 'ki' - it's often question particle)
    'lai', 'le',            # To/by
    'bata', 'dekhi',        # From
    'sanga', 'sangai',      # With
    'haru', 'haruko', 'harulai', 'haruma', 'harule',  # Plural markers
    'bhanda',               # Than/comparing (sabai bhanda -> सबैभन्दा)
    'ma',                   # In/at (postposition - joins to nouns)
}

# Verb suffixes that join to verb stems
VERB_SUFFIXES = {
    'chhu', 'chha', 'chhan', 'chhau', 'chhin',  # Present tense
    'thiyo', 'thyo', 'thye', 'thin', 'thii',    # Past tense
}

# Words where 'ma' following them is the pronoun, not postposition
MA_AS_PRONOUN_AFTER = {
    'ra', 'tara', 'ani', 'athawa',  # Conjunctions
    'bhane', 'ki', 'ke',            # After these, 'ma' is pronoun
    'chha', 'chhan', 'chhu', 'ho',  # After verbs, 'ma' is pronoun
    'jab', 'yadi', 'agar',          # After conditionals, 'ma' is pronoun
}

# Words that typically precede verb suffixes (verb stems ending in -dai, -ne, etc.)
VERB_STEM_ENDINGS = ('dai', 'dae', 'ne', 'era', 'eko', 'eki', 'eka')

# Words that don't take joining suffixes (they stay separate)
NO_JOIN_WORDS = {
    'ra', 'tara', 'ani', 'athawa',  # Conjunctions
    'ki', 'ke',                      # Question particles
    'ho', 'chha', 'chhan',           # Verbs (standalone)
    'chhu',                          # Verb ending
}

# These pairs should always join (word1 + word2 -> combined)
COMPOUND_PAIRS = {
    ('kina', 'bhane'): True,
    ('sabai', 'bhanda'): True,
    ('kinaki', 'bhane'): True,
}

# Words after which 'ma' is the pronoun (I), not postposition (in)
MA_PRONOUN_CONTEXT = {'ra', 'jab', 'tara', 'ani', 'bhane', 'ki', 'kinaki', 'kinabhane', ','}

# Verb endings that join to stems
VERB_ENDINGS = {'chhu', 'chha', 'chhan', 'chhin', 'chhau', 'chhaina', 'chhainan'}

# =============================================================================
# PHONEME MATCHING
# =============================================================================

def match_consonant(text: str, pos: int) -> Tuple[Optional[str], Optional[str], int]:
    """Match consonant pattern at position. Returns (pattern, devanagari, length)."""
    remaining = text[pos:].lower()
    for pattern, dev in CONSONANTS:
        if remaining.startswith(pattern):
            return pattern, dev, len(pattern)
    return None, None, 0

def match_vowel(text: str, pos: int) -> Tuple[Optional[str], str, str, int]:
    """Match vowel pattern at position. Returns (pattern, independent, matra, length)."""
    remaining = text[pos:].lower()
    for pattern, indep, matra in VOWELS:
        if remaining.startswith(pattern):
            return pattern, indep, matra, len(pattern)
    return None, '', '', 0

def is_vowel_char(c: str) -> bool:
    """Check if character is a vowel."""
    return c.lower() in 'aeiou'

def is_consonant_char(c: str) -> bool:
    """Check if character is a consonant."""
    return c.lower() in 'bcdfghjklmnpqrstvwxyz'

# =============================================================================
# SYLLABLE ANALYSIS
# =============================================================================

def analyze_syllables(word: str) -> List[dict]:
    """
    Analyze word into syllables for better transliteration.
    
    Nepali syllable structure: (C)(C)V(C)
    - Onset: 0-2 consonants
    - Nucleus: 1 vowel (required)
    - Coda: 0-1 consonant
    """
    syllables = []
    word_lower = word.lower()
    pos = 0
    
    while pos < len(word_lower):
        syllable = {'onset': '', 'nucleus': '', 'coda': '', 'start': pos}
        
        # Match onset (consonants)
        while pos < len(word_lower):
            cons_pat, cons_dev, cons_len = match_consonant(word_lower, pos)
            if cons_pat:
                syllable['onset'] += cons_pat
                pos += cons_len
            else:
                break
        
        # Match nucleus (vowel)
        if pos < len(word_lower):
            vow_pat, vow_indep, vow_matra, vow_len = match_vowel(word_lower, pos)
            if vow_pat:
                syllable['nucleus'] = vow_pat
                pos += vow_len
        
        # Match coda (consonant at end of syllable)
        # Only if followed by another consonant+vowel (new syllable)
        if pos < len(word_lower) and is_consonant_char(word_lower[pos]):
            # Look ahead: if next is consonant+vowel, current consonant is coda
            next_pos = pos + 1
            if next_pos < len(word_lower) and is_vowel_char(word_lower[next_pos]):
                # Next char is vowel - current consonant starts new syllable
                pass
            elif next_pos < len(word_lower) and is_consonant_char(word_lower[next_pos]):
                # Consonant cluster - handle specially
                pass
        
        syllable['end'] = pos
        if syllable['onset'] or syllable['nucleus']:
            syllables.append(syllable)
        else:
            # Unmatched character
            pos += 1
    
    return syllables

# =============================================================================
# CONTEXT-AWARE TRANSLITERATION
# =============================================================================

def should_nasalize(word: str, pos: int) -> bool:
    """
    Check if 'n' at position should become chandrabindu.
    Pattern: vowel + n + consonant (not ng, ny, nn)
    """
    word_lower = word.lower()
    if pos >= len(word_lower) or word_lower[pos] != 'n':
        return False
    
    # Must be after vowel
    if pos == 0 or word_lower[pos - 1] not in 'aeiou':
        return False
    
    # Must be before consonant (not ng, ny, nn, nk, etc that form conjuncts)
    if pos + 1 >= len(word_lower):
        return False
    
    next_char = word_lower[pos + 1]
    # n before these forms conjunct, not nasalization
    if next_char in 'ngykh':
        return False
    
    # n before other consonants = nasalization
    return is_consonant_char(next_char)

def should_use_long_i(word: str, pos: int, vow_len: int) -> bool:
    """
    Determine if final 'i' should be long (ी) or short (ि).
    
    Pattern from data analysis:
    - Content words (nouns, adjectives) usually get long ी
    - Grammatical particles (ki, ni) usually get short ि
    """
    word_lower = word.lower()
    
    # Check if this is final position
    is_final = pos + vow_len >= len(word_lower)
    if not is_final:
        return False  # Not final, use normal rules
    
    # Short words that are particles
    short_i_words = {'ki', 'ni', 'ji', 'si', 'ti'}
    if word_lower in short_i_words:
        return False
    
    # Words ending in -agi, -chi usually have short i
    if word_lower.endswith('agi') or word_lower.endswith('chi'):
        return False
    
    # Default: use long for final i in content words
    return True

def should_use_long_a(word: str, pos: int, next_pos: int) -> bool:
    """
    Determine if single 'a' should be long (ा) or inherent (no matra).
    
    Key insight from data:
    - 'a' between consonants = usually inherent
    - 'a' before consonant + long vowel = often long
    - 'a' in -ali, -ari endings = long
    """
    word_lower = word.lower()
    
    # At word end - usually inherent
    if next_pos >= len(word_lower):
        return False
    
    # Look ahead pattern
    remaining = word_lower[next_pos:]
    
    # Pattern: a + consonant + ii/ee at end (like nepali, tarkari)
    # These get long a
    if len(remaining) >= 2:
        # Check if followed by consonant + long vowel
        cons_pat, _, cons_len = match_consonant(word_lower, next_pos)
        if cons_pat and next_pos + cons_len < len(word_lower):
            after_cons = word_lower[next_pos + cons_len:]
            if after_cons.startswith(('i', 'ii', 'ee')) and next_pos + cons_len + 1 >= len(word_lower) - 1:
                return True
    
    # Pattern: -ari, -ali endings
    if word_lower[pos:].startswith(('ari', 'ali')):
        return True
    
    return False

def transliterate_word_rules(word: str) -> str:
    """
    Rule-based transliteration for words not in dictionary.
    
    Key rules from Nepali phonology:
    1. 'aa' = explicit long आ matra (ा)
    2. Single 'a' at end = short (inherent) - no matra usually
    3. Single 'a' between consonants = inherent (no matra)
    4. 'r' before consonant = र् conjunct, NOT हलन्त र
    5. Final single 'i' = usually long ी in content words
    6. 'n' before consonant (after vowel) = chandrabindu ँ or anusvara ं
    """
    if not word:
        return ''
    
    result = []
    pos = 0
    word_len = len(word)
    word_lower = word.lower()
    
    while pos < word_len:
        char = word[pos]
        
        # Pass through non-ASCII, digits, and special chars
        if char.isdigit() or ord(char) > 127 or char in '[]{}()':
            result.append(char)
            pos += 1
            continue
        
        # Try consonant match first
        cons_pat, cons_dev, cons_len = match_consonant(word, pos)
        
        if cons_pat:
            # Check for nasalization 'n' - ONLY if matched as single 'n'
            # (to avoid breaking 'nn', 'ny', 'ng' etc.)
            if cons_pat == 'n' and should_nasalize(word, pos):
                result.append(CHANDRABINDU)
                pos += 1
                continue

            next_pos = pos + cons_len
            
            # Check what follows the consonant
            if next_pos >= word_len:
                # Word-final consonant - typically no halant in Nepali
                result.append(cons_dev)
                # result.append(HALANT) # Disabled
                pos = next_pos
                continue
            
            # Check for following vowel
            vow_pat, vow_indep, vow_matra, vow_len = match_vowel(word, next_pos)
            
            if vow_pat:
                result.append(cons_dev)
                
                # Apply vowel - with context-sensitive handling
                if vow_pat == 'a':
                    # Single 'a' - usually inherent (no matra)
                    # But at word end before postposition (ma, ko, etc), use long ा
                    after_a_pos = next_pos + vow_len
                    remaining = word_lower[after_a_pos:] if after_a_pos < word_len else ''
                    
                    # Check if followed by postposition suffix
                    if remaining in ('ma', 'ko', 'ka', 'ki', 'lai', 'le'):
                        result.append('ा')  # Long a before postposition
                    # Check for word-final a (like 'katha' -> कथा)
                    elif after_a_pos >= word_len:
                        # Word-final single a - check word pattern
                        # Words like 'katha' get long ा, but 'sama' doesn't
                        # This is tricky - use short by default
                        pass  # Inherent (no matra)
                    # Otherwise inherent (no matra)
                    
                elif vow_pat == 'i' and next_pos + vow_len >= word_len:
                    # Final single 'i' - usually long ी in content words
                    # Exceptions: short i words like ki, ni
                    if word_len <= 2:
                        result.append('ि')  # Short for 2-letter words
                    else:
                        result.append('ी')  # Long for content words
                elif vow_pat == 'ai':
                    # 'ai' - check context
                    # Word-final 'ai' after consonant = ै
                    result.append(vow_matra)
                elif vow_matra:
                    result.append(vow_matra)
                # else: inherent 'a' - no matra needed
                
                pos = next_pos + vow_len
                
            else:
                # Consonant followed by another consonant - form conjunct
                next_cons_pat, next_cons_dev, next_cons_len = match_consonant(word, next_pos)
                
                if next_cons_pat:
                    # Check for special consonant cluster patterns
                    # 'r' before consonant creates रेफ (r above next consonant)
                    # This is complex in Unicode - use halant for now
                    result.append(cons_dev)
                    result.append(HALANT)
                else:
                    # Just add the consonant
                    result.append(cons_dev)
                
                pos = next_pos
        else:
            # Try vowel match (word-initial vowel)
            vow_pat, vow_indep, vow_matra, vow_len = match_vowel(word, pos)
            
            if vow_pat:
                result.append(vow_indep)
                pos += vow_len
            elif should_nasalize(word, pos):
                # 'n' that should be chandrabindu
                result.append(CHANDRABINDU)
                pos += 1
            else:
                # Unknown character - pass through
                result.append(char)
                pos += 1
    
    return ''.join(result)

# =============================================================================
# MAIN TRANSLITERATION
# =============================================================================

def transliterate_word(word: str, context: dict = None) -> str:
    """
    Transliterate a single word.
    
    Args:
        word: Roman word to transliterate
        context: Optional context info (is_sentence_start, prev_word, etc.)
    
    Returns:
        Devanagari transliteration
    """
    if not word:
        return ''
    
    word_lower = word.lower()
    context = context or {}
    
    # Special handling for 'ma' based on context
    if word_lower == 'ma':
        prev_word = context.get('prev_word', '').lower()
        is_sentence_start = context.get('is_sentence_start', False)
        
        # 'ma' as pronoun (I)
        # Check punctuation on prev_word
        prev_clean = prev_word.rstrip('.,?!;:')
        
        # If prev_word was punctuation itself (e.g. sent in as ','), handle it
        if prev_word in (',', ';', '-', '...'):
            return 'म'
            
        if is_sentence_start or prev_clean in MA_PRONOUN_CONTEXT or prev_word.endswith(','):
            return 'म'
        # else: 'ma' as postposition - will be handled by dictionary or rules
    
    # Suffix splitting logic for joined inputs (e.g. "Nepalma")
    # Don't split if word is short or in dictionary
    if len(word) > 3 and word_lower not in WORD_DICT:
        # Sort suffixes by length desc
        sorted_suffixes = sorted(list(JOINING_SUFFIXES), key=len, reverse=True)
        for suffix in sorted_suffixes:
            if word_lower.endswith(suffix):
                stem = word[:-len(suffix)]
                # Heuristic: stem must be reasonably long (2+)
                if len(stem) >= 2:
                    # Just split and join
                    stem_trans = transliterate_word(stem, context)
                    suffix_trans = transliterate_word(suffix, context)
                    return stem_trans + suffix_trans
    
    
    # Special context handling for 'hun'
    if word_lower == 'hun':
        prev_word = context.get('prev_word', '').lower()
        if context.get('is_sentence_start', False) or prev_word == 'ma' or prev_word in MA_PRONOUN_CONTEXT:
            return 'हुँ'  # I am
        # else: return 'हुन्' (They are) - handled by common_particles below
        
    # COMMON PARTICLES/WORDS OVERRIDE
    common_particles = {
        'ma': 'मा',
        'ko': 'को',
        'le': 'ले',
        'lai': 'लाई',
        'bata': 'बाट',
        'dekhi': 'देखि',
        'sanga': 'सँग',
        'chha': 'छ',
        'chhu': 'छु',
        'chhan': 'छन्',
        'ho': 'हो',
        'hun': 'हुन्',
        'ta': 'त',
        'nai': 'नै',
        'ni': 'नि',
        'po': 'पो',
        'ra': 'र',
        'ki': 'कि',
        'ke': 'के',
        'yo': 'यो',
        'tyo': 'त्यो',
        'u': 'ऊ',
        'nepal': 'नेपाल',
        'nepali': 'नेपाली',
        'sabai': 'सबै',
        'dherai': 'धेरै',
    }
    
    if word_lower in common_particles:
        return common_particles[word_lower]

    # Check dictionary first
    if word_lower in WORD_DICT:
        return WORD_DICT[word_lower]
    
    # Fall back to rules
    return transliterate_word_rules(word)

def should_join(word1: str, word2: str, context: dict = None) -> Tuple[bool, str]:
    """
    Determine if word2 should join to word1.
    Returns (should_join, combined_form).
    """
    w1_lower = word1.lower().rstrip('.,?!;:')
    w2_lower = word2.lower().rstrip('.,?!;:')
    context = context or {}
    
    # Check for known compound pairs first
    if (w1_lower, w2_lower) in COMPOUND_PAIRS:
        return True, COMPOUND_PAIRS[(w1_lower, w2_lower)]
    
    # Check if combined form exists in dictionary
    combined = w1_lower + w2_lower
    if combined in WORD_DICT:
        return True, WORD_DICT[combined]
    
    # Special handling for 'ma' - don't join if it's the pronoun
    if w2_lower == 'ma':
        # After sentence enders or certain words, 'ma' is pronoun
        if w1_lower.endswith(('.', ',', '?', '!')) or w1_lower in MA_PRONOUN_CONTEXT:
            return False, ''
    
    # Don't join 'ko', 'ki', etc after certain words
    if w2_lower in ('ko', 'ki', 'ka'):
        # After verbs ending in chha, these usually don't join
        if w1_lower.endswith(('chha', 'chhu', 'chhan')):
            return False, ''
    
    # Check if w2 is a joining suffix
    if w2_lower in JOINING_SUFFIXES:
        # Return True but no combined form - caller will handle
        return True, ''
    
    return False, ''

# =============================================================================
# TRANSLITERATOR CLASS
# =============================================================================

class NepaliTransliterator:
    """Main transliterator with intelligent word joining."""
    
    def __init__(self):
        self.cache = {}
    
    def transliterate(self, text: str) -> str:
        """Transliterate full text with word joining for postpositions."""
        if not text:
            return ''
        
        # Tokenize
        tokens = self._tokenize(text)
        
        # Process tokens with lookahead for joining
        result = []
        i = 0
        is_sentence_start = True
        prev_word = ''
        
        while i < len(tokens):
            ttype, tval = tokens[i]
            
            if ttype == 'word':
                context = {
                    'is_sentence_start': is_sentence_start,
                    'prev_word': prev_word,
                }
                
                # Look ahead for words that should join
                words_to_join = [tval]
                j = i + 1
                
                while j < len(tokens):
                    # Need space then word
                    if j < len(tokens) and tokens[j][0] == 'space':
                        if j + 1 < len(tokens) and tokens[j + 1][0] == 'word':
                            next_word = tokens[j + 1][1]
                            next_lower = next_word.lower()
                            prev_lower = words_to_join[-1].lower()
                            
                            # Check if this is a compound pair
                            if (prev_lower, next_lower) in COMPOUND_PAIRS:
                                words_to_join.append(next_word)
                                j += 2
                                continue
                            
                            # Verb Joining Logic REMOVED (Dataset prefers separate usually)
                            # if next_lower in {'chhu', 'chha', 'chhan'}: ...
                            
                            # Check if next word is a joining suffix
                            if next_lower in JOINING_SUFFIXES:
                                is_joining_suffix = True
                                
                                # Special handling for 'ma'
                                if next_lower == 'ma':
                                    # 'ma' is pronoun if:
                                    # Check prev_word for 'ends with' checking
                                    # If prev word is 'kinabhane' (kina + bhane), it ends with 'bhane'
                                    if context.get('prev_word', '').endswith(','): 
                                         is_joining_suffix = False
                                    elif any(prev_lower.endswith(w) for w in MA_AS_PRONOUN_AFTER):
                                         is_joining_suffix = False
                                    elif prev_lower.endswith(','):
                                         is_joining_suffix = False
                                
                                # Special handling for 'ki'
                                elif next_lower == 'ki':
                                    # Default to NOT joining 'ki' for now unless we add smart rule.
                                    pass

                                if is_joining_suffix:
                                    # Don't join if previous word implies separate
                                    if prev_lower not in NO_JOIN_WORDS:
                                        # Don't join if previous word already ends with a postposition?
                                        # But allow multi-joining like 'haru' + 'lai'
                                        words_to_join.append(next_word)
                                        j += 2
                                        continue
                    break
                
                # Transliterate and optionally join
                if len(words_to_join) == 1:
                    result.append(self._get_cached(tval, context))
                else:
                    # Try combined form first
                    combined_lower = ''.join(w.lower() for w in words_to_join)
                    if combined_lower in WORD_DICT:
                        result.append(WORD_DICT[combined_lower])
                    else:
                        # Transliterate parts and join without space
                        parts = []
                        for k, w in enumerate(words_to_join):
                            ctx = context if k == 0 else {'prev_word': words_to_join[k-1]}
                            parts.append(self._get_cached(w, ctx))
                        result.append(''.join(parts))
                
                prev_word = words_to_join[-1]
                is_sentence_start = False
                i = j
                
            elif ttype == 'space':
                result.append(tval)
                i += 1
                
            elif ttype == 'punct':
                result.append(PUNCTUATION.get(tval, tval))
                if tval in '.?!|':
                    is_sentence_start = True
                
                # Update prev_word to be the punctuation char so next word sees it
                prev_word = tval
                i += 1
            else:
                i += 1
        
        return ''.join(result)
    
    def _tokenize(self, text: str) -> List[Tuple[str, str]]:
        """Tokenize text into (type, value) pairs."""
        tokens = []
        current = []
        
        for char in text:
            if char.isspace():
                if current:
                    tokens.append(('word', ''.join(current)))
                    current = []
                tokens.append(('space', char))
            elif char in PUNCTUATION:
                if current:
                    tokens.append(('word', ''.join(current)))
                    current = []
                tokens.append(('punct', char))
            else:
                current.append(char)
        
        if current:
            tokens.append(('word', ''.join(current)))
        
        return tokens
    
    def _get_cached(self, word: str, context: dict) -> str:
        """Get transliteration with caching."""
        word_lower = word.lower()
        
        # Context-sensitive words shouldn't be cached
        if word_lower in ('ma',):
            return transliterate_word(word, context)
        
        if word_lower not in self.cache:
            self.cache[word_lower] = transliterate_word(word, context)
        return self.cache[word_lower]

# =============================================================================
# MODULE API
# =============================================================================

_instance = None

def get_transliterator() -> NepaliTransliterator:
    global _instance
    if _instance is None:
        _instance = NepaliTransliterator()
    return _instance

def transliterate(text: str) -> str:
    """Transliterate Roman Nepali text to Devanagari."""
    return get_transliterator().transliterate(text)
