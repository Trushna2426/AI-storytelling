import unittest
from app import app  

class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        # Create a test client for the Flask application.
        self.app = app.test_client()
        self.app.testing = True

    def test_index_get(self):
        # Test that the index page loads correctly with a GET request.
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        print("GET / response:")
        print(response.data.decode('utf-8'))

    def test_index_post(self):
        # Test submitting a POST request to the index page with a user_id.
        response = self.app.post('/', data={'user_id': 'testuser'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        print("\nPOST / with user_id 'testuser' response:")
        print(response.data.decode('utf-8'))

    def test_story_get(self):
        # Set a user_id first so that session data is available, then test the /story endpoint.
        self.app.post('/', data={'user_id': 'testuser'}, follow_redirects=True)
        response = self.app.get('/story')
        self.assertEqual(response.status_code, 200)
        print("\nGET /story response:")
        print(response.data.decode('utf-8'))

if __name__ == '__main__':
    unittest.main()
