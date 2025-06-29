# ASCII-M-A-T-I-C-5000

Welcome to the ASCII-M-A-T-I-C-5000! This project is an artistic experiment and a nostalgic retro experience, designed to showcase AI capabilities in generating ASCII art.

## Features

*   **Command-Line Interface (CLI):**
    *   Convert images to ASCII art.
    *   Convert text directly to ASCII art (via basic text-to-image rendering).
    *   Adjustable output width.
    *   Multiple character sets for different retro styles.
*   **Web Interface:**
    *   All CLI features accessible through a user-friendly web page.
    *   Retro aesthetic design.
    *   Upload images or input text directly.
    *   Select output width and character set.
    *   View generated ASCII art in the browser.

## Setup

1.  **Clone the repository (if you haven't already).**
2.  **Ensure you have Python 3 installed.**
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Command-Line Interface (CLI)

The main script for CLI operations is `ascii_matic_5000.py`.

**Examples:**

*   Convert an image:
    ```bash
    python ascii_matic_5000.py --image assets/test_image.png --width 80 --charset blocky
    ```
*   Convert text:
    ```bash
    python ascii_matic_5000.py --text "Hello Retro AI" --width 60 --charset simple
    ```
*   See all options:
    ```bash
    python ascii_matic_5000.py --help
    ```

### Web Application

The web application provides a graphical interface for all ASCII generation features.

1.  **Start the Flask development server:**
    ```bash
    python app.py
    ```
2.  **Open your web browser and navigate to:**
    `http://127.0.0.1:8080` (or `http://localhost:8080`)

    The application will typically print the exact URL it's running on in the console. You can then use the form to upload images or enter text, select options, and generate ASCII art.

## Development

*   **CLI Tests:** Run `python test_ascii_matic.py`
*   **Web App Tests:** Run `python test_webapp.py`

Stay tuned for more updates!