import unittest
from story_database import get_choices_by_theme

class TestStoryDataset(unittest.TestCase):
    def test_get_choices_by_theme(self):
        """Ensure that predefined choices are retrieved correctly."""
        choices = get_choices_by_theme("magic")
        self.assertIsInstance(choices, list)
        self.assertGreater(len(choices), 0)
        self.assertTrue(any("wizard" in choice.lower() for choice in choices))

if __name__ == "__main__":
    unittest.main()
