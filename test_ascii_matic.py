import subprocess
import os
import unittest

# Define the path to the main script
MAIN_SCRIPT = "ascii_matic_5000.py"
TEST_IMAGE_PATH = "assets/test_image.png"
NON_EXISTENT_IMAGE_PATH = "assets/this_image_does_not_exist.png"

# Ensure the main script is executable
if not os.access(MAIN_SCRIPT, os.X_OK):
    os.chmod(MAIN_SCRIPT, 0o755)

class TestAsciiMatic(unittest.TestCase):

    def run_script(self, args):
        """Helper function to run the main script with arguments and return output/error."""
        cmd = ["python", MAIN_SCRIPT] + args
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        return stdout, stderr, process.returncode

    def test_01_image_conversion_default(self):
        """Test basic image conversion with default settings."""
        stdout, stderr, returncode = self.run_script(["--image", TEST_IMAGE_PATH])
        self.assertEqual(returncode, 0, f"Script failed with stderr: {stderr}")
        self.assertTrue(len(stdout) > 100, "Output seems too short or empty.")
        self.assertNotIn("Error:", stdout)
        self.assertNotIn("Traceback", stderr)

    def test_02_text_conversion_default(self):
        """Test basic text-to-image conversion."""
        stdout, stderr, returncode = self.run_script(["--text", "Test Text"])
        self.assertEqual(returncode, 0, f"Script failed with stderr: {stderr}")
        self.assertTrue(len(stdout) > 100, "Output seems too short or empty.")
        self.assertNotIn("Error:", stdout) # Excludes "Error saving temporary text image" etc.
        self.assertNotIn("Traceback", stderr)
        # Check if temp file was cleaned up
        self.assertFalse(os.path.exists("assets/temp_text_image.png"), "Temporary text image was not cleaned up.")

    def test_03_charset_selection(self):
        """Test image conversion with a specific charset."""
        stdout, stderr, returncode = self.run_script(["--image", TEST_IMAGE_PATH, "--charset", "simple"])
        self.assertEqual(returncode, 0, f"Script failed with stderr: {stderr}")
        self.assertTrue(len(stdout) > 100, "Output seems too short or empty.")
        self.assertNotIn("Error:", stdout)
        self.assertNotIn("Traceback", stderr)

    def test_04_width_selection(self):
        """Test image conversion with a specific width."""
        stdout, stderr, returncode = self.run_script(["--image", TEST_IMAGE_PATH, "--width", "50"])
        self.assertEqual(returncode, 0, f"Script failed with stderr: {stderr}")
        self.assertTrue(len(stdout) > 50, "Output seems too short or empty.")
        # Verify the width of one of the lines
        lines = stdout.splitlines()
        ascii_art_lines = [line for line in lines if len(line.strip()) > 0 and not line.startswith("Welcome") and not line.startswith("Attempting") and not line.startswith("-----") and not line.startswith("Conversion")]
        if ascii_art_lines:
             # Taking a sample line from the middle of the art, if available
            sample_line_index = len(ascii_art_lines) // 2
            self.assertEqual(len(ascii_art_lines[sample_line_index]), 50, f"ASCII art line width is not 50. Line: '{ascii_art_lines[sample_line_index]}'")
        self.assertNotIn("Error:", stdout)
        self.assertNotIn("Traceback", stderr)

    def test_05_mutually_exclusive_image_text(self):
        """Test providing both --image and --text fails."""
        stdout, stderr, returncode = self.run_script(["--image", TEST_IMAGE_PATH, "--text", "Hello"])
        self.assertNotEqual(returncode, 0, "Script should fail when both --image and --text are provided.")
        self.assertIn("not allowed with argument", stderr.lower()) # Argparse error message

    def test_06_missing_image_or_text(self):
        """Test providing neither --image nor --text fails."""
        stdout, stderr, returncode = self.run_script([])
        self.assertNotEqual(returncode, 0, "Script should fail when neither --image nor --text is provided.")
        self.assertIn("one of the arguments --image --text is required", stderr.lower())

    def test_07_invalid_charset(self):
        """Test providing an invalid --charset value fails."""
        stdout, stderr, returncode = self.run_script(["--image", TEST_IMAGE_PATH, "--charset", "nonexistent"])
        self.assertNotEqual(returncode, 0, "Script should fail with an invalid charset.")
        self.assertIn("invalid choice", stderr.lower()) # Argparse error message for choices

    def test_08_non_existent_image(self):
        """Test conversion of a non-existent image file."""
        stdout, stderr, returncode = self.run_script(["--image", NON_EXISTENT_IMAGE_PATH])
        self.assertEqual(returncode, 0, f"Script should handle non-existent image gracefully. Stderr: {stderr}")
        self.assertIn(f"Error: Image not found at {NON_EXISTENT_IMAGE_PATH}", stdout)
        self.assertNotIn("Traceback", stderr)

if __name__ == "__main__":
    # Create a dummy test_image.png if it doesn't exist for the tests to run
    # This is primarily for CI environments or fresh checkouts.
    if not os.path.exists(TEST_IMAGE_PATH):
        print(f"Creating dummy test image at {TEST_IMAGE_PATH} for tests.")
        try:
            from PIL import Image, ImageDraw
            dummy_img = Image.new('L', (200, 100), color='gray')
            draw = ImageDraw.Draw(dummy_img)
            draw.ellipse((20, 20, 80, 80), fill='white')
            draw.rectangle((100, 30, 180, 70), fill='black')
            if not os.path.exists("assets"):
                os.makedirs("assets")
            dummy_img.save(TEST_IMAGE_PATH)
            print("Dummy image saved.")
        except Exception as e:
            print(f"Could not create dummy image for tests: {e}. Some tests might fail.")
            # Depending on policy, one might exit here if the test image is critical

    unittest.main()
