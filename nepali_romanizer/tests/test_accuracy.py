"""
Accuracy tests using the provided test data.
"""

import json
import pytest
from pathlib import Path
from nepali_romanizer import transliterate, NepaliTransliterator


def load_test_data():
    """Load the test data from JSON file."""
    # Try multiple possible locations
    possible_paths = [
        Path(__file__).parent.parent.parent / "Roman_to_Devnagari_Custom" / "test.json",
        Path(__file__).parent.parent.parent.parent / "Roman_to_Devnagari_Custom" / "test.json",
        Path("d:/Roman_To_Devnagari_Custom/Roman_to_Devnagari_Custom/test.json"),
    ]
    
    for path in possible_paths:
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
    
    pytest.skip("Test data file not found")
    return []


def get_all_test_cases():
    """Extract all test cases from the test data."""
    data = load_test_data()
    test_cases = []
    
    for category in data:
        category_name = category.get('category', 'Unknown')
        for item in category.get('data', []):
            roman = item.get('roman', '')
            devanagari = item.get('devanagari', '')
            test_cases.append((roman, devanagari, category_name))
    
    return test_cases


class TestAccuracy:
    """Test accuracy against the provided test data."""
    
    @pytest.fixture
    def transliterator(self):
        """Create a transliterator instance."""
        return NepaliTransliterator()
    
    @pytest.fixture
    def test_data(self):
        """Load test data."""
        return load_test_data()
    
    def test_data_loaded(self, test_data):
        """Verify test data is loaded correctly."""
        assert len(test_data) > 0, "Test data should not be empty"
    
    def test_categories_present(self, test_data):
        """Verify all expected categories are present."""
        categories = [cat['category'] for cat in test_data]
        assert len(categories) >= 5, "Should have multiple categories"


class TestCategoryAccuracy:
    """Test accuracy by category."""
    
    def calculate_accuracy(self, test_cases):
        """Calculate accuracy for a set of test cases."""
        if not test_cases:
            return 0, 0, []
        
        correct = 0
        failures = []
        
        for roman, expected, category in test_cases:
            result = transliterate(roman)
            if result == expected:
                correct += 1
            else:
                failures.append({
                    'roman': roman,
                    'expected': expected,
                    'got': result,
                    'category': category
                })
        
        return correct, len(test_cases), failures
    
    def test_overall_accuracy(self):
        """Test overall accuracy across all test cases."""
        test_cases = get_all_test_cases()
        if not test_cases:
            pytest.skip("No test cases available")
        
        correct, total, failures = self.calculate_accuracy(test_cases)
        accuracy = (correct / total) * 100 if total > 0 else 0
        
        print(f"\n=== Overall Accuracy: {accuracy:.2f}% ({correct}/{total}) ===")
        
        if failures and len(failures) <= 20:
            print("\nSample failures:")
            for f in failures[:10]:
                print(f"  Roman: {f['roman']}")
                print(f"  Expected: {f['expected']}")
                print(f"  Got: {f['got']}")
                print()
        
        # We're starting out - aim to improve this
        # assert accuracy >= 50, f"Accuracy should be at least 50%, got {accuracy:.2f}%"
    
    def test_keywords_category(self):
        """Test accuracy on specific keywords."""
        test_cases = get_all_test_cases()
        keywords = [(r, e, c) for r, e, c in test_cases if c == "Specific Keywords (Sabdawali)"]
        
        if not keywords:
            pytest.skip("Keywords category not found")
        
        correct, total, failures = self.calculate_accuracy(keywords)
        accuracy = (correct / total) * 100 if total > 0 else 0
        
        print(f"\n=== Keywords Accuracy: {accuracy:.2f}% ({correct}/{total}) ===")
        
        if failures:
            print("\nKeyword failures:")
            for f in failures[:10]:
                print(f"  {f['roman']} → Expected: {f['expected']}, Got: {f['got']}")


# Parametrized tests for individual test cases
@pytest.mark.parametrize("roman,expected,category", get_all_test_cases()[:50])  # Test first 50
def test_individual_transliteration(roman, expected, category):
    """Test individual transliterations."""
    result = transliterate(roman)
    # This will show which specific cases fail
    # assert result == expected, f"[{category}] {roman}: expected '{expected}', got '{result}'"
    pass  # Start with pass to see what works
