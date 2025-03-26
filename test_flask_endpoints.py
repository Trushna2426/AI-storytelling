import unittest
import json
from app import app

class TestFlaskAPI(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_story_generation(self):
        """Ensure that a user can get valid story choices."""
        response = self.client.post("/", data={"user_prompt": "A detective finds a hidden letter."})
        self.assertEqual(response.status_code, 200)
        data = response.data.decode("utf-8")
        self.assertIn("Your Story So Far", data)  # Narrative should be displayed
        self.assertIn("choice", data.lower())  # Choices should be present

if __name__ == "__main__":
    unittest.main()
