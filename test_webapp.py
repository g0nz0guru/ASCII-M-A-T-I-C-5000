import unittest
import os
from app import app # Your Flask app instance

# Define the path for the test image, consistent with other test scripts if needed
TEST_IMAGE_PATH = "assets/test_image.png"

class WebAppTests(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False # Disable CSRF for testing forms if you were using Flask-WTF
        app.config['UPLOAD_FOLDER'] = 'assets/test_uploads' # Use a separate upload folder for tests
        self.client = app.test_client()

        # Ensure the test upload folder exists
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

        # Create a dummy test_image.png if it doesn't exist for the tests to run
        # This should ideally be part of a fixture or test setup utility
        if not os.path.exists(TEST_IMAGE_PATH):
            print(f"Creating dummy test image at {TEST_IMAGE_PATH} for web tests.")
            try:
                from PIL import Image, ImageDraw
                dummy_img = Image.new('L', (50, 30), color='gray') # Smaller for faster test processing
                draw = ImageDraw.Draw(dummy_img)
                draw.text((10,10), "Test", fill="white")
                if not os.path.exists("assets"):
                    os.makedirs("assets")
                dummy_img.save(TEST_IMAGE_PATH)
                print("Dummy image saved for web tests.")
            except Exception as e:
                print(f"Could not create dummy image for web tests: {e}.")


    def tearDown(self):
        # Clean up the test upload folder and any files within it
        if os.path.exists(app.config['UPLOAD_FOLDER']):
            for f in os.listdir(app.config['UPLOAD_FOLDER']):
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], f))
            os.rmdir(app.config['UPLOAD_FOLDER'])
        # Clean up the general test image if it was created by this test suite
        # Be cautious if other tests depend on it and manage it more globally
        # if os.path.exists(TEST_IMAGE_PATH) and "created_by_web_test" in TEST_IMAGE_PATH:
        #     os.remove(TEST_IMAGE_PATH)


    def test_01_index_page_loads(self):
        """Test that the index page loads correctly."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"ASCII-M-A-T-I-C-5000", response.data) # Check for title or key text
        self.assertIn(b"Input Type", response.data) # Check for form element

    def test_02_generate_from_text(self):
        """Test ASCII generation from text input."""
        response = self.client.post('/generate', data={
            'input_type': 'text',
            'text_input': 'Hello Web',
            'width': '80',
            'charset': 'default'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Generated ASCII Art", response.data) # Expecting the section title
        # A very basic check for any ASCII-like output, not validating content
        self.assertIn(b"<pre id=\"ascii_art_output\">", response.data)
        self.assertNotIn(b"Error:", response.data) # Should not have overt error messages

    def test_03_generate_from_image_upload(self):
        """Test ASCII generation from image upload."""
        if not os.path.exists(TEST_IMAGE_PATH):
            self.skipTest(f"Test image {TEST_IMAGE_PATH} not found, skipping image upload test.")

        with open(TEST_IMAGE_PATH, 'rb') as img_file:
            response = self.client.post('/generate', data={
                'input_type': 'image',
                'image_upload': (img_file, 'test_image.png'),
                'width': '70',
                'charset': 'simple'
            }, content_type='multipart/form-data')

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Generated ASCII Art", response.data)
        self.assertIn(b"<pre id=\"ascii_art_output\">", response.data)
        self.assertNotIn(b"Error:", response.data)

    def test_04_generate_missing_text_input(self):
        """Test error handling for missing text input when type is text."""
        response = self.client.post('/generate', data={
            'input_type': 'text',
            'text_input': '', # Empty text
            'width': '80',
            'charset': 'default'
        })
        self.assertEqual(response.status_code, 200) # Still 200 as it re-renders the page
        self.assertIn(b"<p><strong>Error:</strong> Text input cannot be empty.</p>", response.data)

    def test_05_generate_no_image_selected(self):
        """Test error handling for no image selected when type is image."""
        response = self.client.post('/generate', data={
            'input_type': 'image',
            # No 'image_upload' file part
            'width': '80',
            'charset': 'default'
        }, content_type='multipart/form-data') # Need multipart for file handling logic
        self.assertEqual(response.status_code, 200)
        # Check for the specific HTML structure of the error message
        self.assertTrue(b"<p><strong>Error:</strong> No image file part in the request.</p>" in response.data or \
                        b"<p><strong>Error:</strong> No image file selected.</p>" in response.data)


if __name__ == '__main__':
    unittest.main()
