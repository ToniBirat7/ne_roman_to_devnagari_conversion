# Nepali Romanizer 🇳🇵

A robust Python package for transliterating Nepali Roman (Romanized Nepali) text to Devnagari script using a dynamic, rule-based, phoneme-driven approach. No hardcoded word exceptions are used. The system is designed to handle ambiguous cases using dynamic rules and a disambiguation layer.

## Features

- ✅ **Phoneme-based mapping** - Handles complex Nepali phonetics and ambiguous cases
- ✅ **Conjunct support** - Proper handling of consonant clusters (संयुक्त व्यञ्जन)
- ✅ **Context-aware** - Intelligent vowel and consonant handling, schwa deletion, and matra placement
- ✅ **Zero dependencies** - Pure Python implementation
- ✅ **Fast** - Optimized for performance
- ✅ **Well-tested** - Comprehensive test suite

## Installation

```bash
pip install nepali-romanizer
```

## Quick Start

```python
# Usage instructions will be updated after new implementation
```

## Usage Examples

### Basic Usage

```python
from nepali_romanizer import transliterate

# Simple words
print(transliterate("nepal"))      # नेपाल
print(transliterate("kanoon"))     # कानून
print(transliterate("namaste"))    # नमस्ते

# Sentences
print(transliterate("jagga namasari garna k k chaincha"))
# जग्गा नामसारी गर्न के के चाहिन्छ
```

### Advanced Usage

```python
from nepali_romanizer import NepaliTransliterator

# Create a transliterator instance
transliterator = NepaliTransliterator()

# Transliterate text
result = transliterator.transliterate("mero ghar nepal ma cha")
print(result)  # मेरो घर नेपालमा छ

# Batch processing
texts = ["namaste", "dhanyabad", "subha prabhat"]
results = transliterator.transliterate_batch(texts)
print(results)  # ['नमस्ते', 'धन्यवाद', 'शुभ प्रभात']
```

## Supported Mappings

### Vowels (स्वर)
| Roman | Devnagari |
| ----- | --------- |
| a     | अ         |
| aa/ā  | आ         |
| i     | इ         |
| ee/ī  | ई         |
| u     | उ         |
| oo/ū  | ऊ         |
| e     | ए         |
| ai    | ऐ         |
| o     | ओ         |
| au    | औ         |

### Consonants (व्यञ्जन)
See the full mapping in [MAPPINGS.md](./MAPPINGS.md)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Testing

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=nepali_romanizer --cov-report=html
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by the need for accurate Nepali transliteration
- Thanks to all contributors and testers

## Support

If you find this package useful, please consider giving it a ⭐ on GitHub!

---

Made with ❤️ for the Nepali language community
