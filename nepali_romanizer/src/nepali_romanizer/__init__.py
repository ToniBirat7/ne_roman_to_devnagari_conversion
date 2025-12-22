"""
Nepali Romanizer - A robust Python package for Nepali Roman to Devnagari transliteration.

This package provides accurate transliteration of Romanized Nepali text to Devnagari script.
Uses a phoneme-based, rule-driven approach with no hardcoded exceptions.
"""

from .transliterator import transliterate

__version__ = "0.1.0"
__author__ = "Your Name"
__all__ = ["transliterate"]
