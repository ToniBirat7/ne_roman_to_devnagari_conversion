"""
Basic tests for Nepali transliteration.
"""

import pytest
from nepali_romanizer import transliterate, NepaliTransliterator


class TestBasicTransliteration:
    """Test basic transliteration functionality."""
    
    def test_simple_consonants(self):
        """Test basic consonant transliteration."""
        assert 'क' in transliterate("ka")
        assert 'ख' in transliterate("kha")
        assert 'ग' in transliterate("ga")
        assert 'घ' in transliterate("gha")
    
    def test_vowels_independent(self):
        """Test independent vowels at word start."""
        assert transliterate("a") == "अ"
        assert transliterate("aa") == "आ"
        assert transliterate("i") == "इ"
        assert transliterate("u") == "उ"
        assert transliterate("e") == "ए"
        assert transliterate("o") == "ओ"
    
    def test_vowels_with_consonants(self):
        """Test vowel signs after consonants."""
        result = transliterate("ka")
        assert 'क' in result
        
        result = transliterate("ki")
        assert 'क' in result and 'ि' in result
        
        result = transliterate("ku")
        assert 'क' in result and 'ु' in result
    
    def test_empty_string(self):
        """Test empty string handling."""
        assert transliterate("") == ""
    
    def test_spaces_preserved(self):
        """Test that spaces are preserved."""
        result = transliterate("ka ga")
        assert " " in result
    
    def test_numbers(self):
        """Test numeral conversion."""
        result = transliterate("123")
        assert "१२३" == result


class TestTransliteratorClass:
    """Test the NepaliTransliterator class."""
    
    def test_instance_creation(self):
        """Test creating a transliterator instance."""
        t = NepaliTransliterator()
        assert t is not None
    
    def test_batch_transliteration(self):
        """Test batch transliteration."""
        t = NepaliTransliterator()
        texts = ["ka", "kha", "ga"]
        results = t.transliterate_batch(texts)
        assert len(results) == 3


class TestCommonNepaliWords:
    """Test common Nepali words."""
    
    def test_namaste(self):
        """Test transliteration of 'namaste'."""
        result = transliterate("namaste")
        # Should contain न, म, स, त, े
        assert 'न' in result
        assert 'म' in result
    
    def test_nepal(self):
        """Test transliteration of 'nepal'."""
        result = transliterate("nepal")
        assert 'न' in result
        assert 'प' in result
        assert 'ल' in result
    
    def test_dhanyabad(self):
        """Test transliteration of 'dhanyabad'."""
        result = transliterate("dhanyabad")
        assert 'ध' in result
        assert 'न' in result
