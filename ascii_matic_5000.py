# ASCII-M-A-T-I-C-5000
# Main script for the AI-Powered Retro ASCII Art Generator

import argparse
from PIL import Image, ImageDraw, ImageFont
import os

# Define available character sets (ramps)
ASCII_CHAR_SETS = {
    "default": "@%#*+=-:. ",  # Standard detailed ramp
    "simple": "#=-. ",       # Simpler, fewer characters
    "blocky": "█▓▒░ ",       # Uses block characters for a different feel
    "retro": "$#XO*o+-,. "   # Another thematic ramp
}
DEFAULT_CHARSET_NAME = "default"
TEMP_TEXT_IMAGE_PATH = "assets/temp_text_image.png"

def text_to_image(text, image_width=600, image_height=300, font_size=40):
    """
    Converts a string of text into a grayscale image.
    Saves the image to TEMP_TEXT_IMAGE_PATH.
    """
    img = Image.new('L', (image_width, image_height), color='white')
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("DejaVuSans.ttf", font_size)
    except IOError:
        print("Warning: DejaVuSans.ttf not found, using Pillow's default font. Text rendering may be basic.")
        try:
            font = ImageFont.load_default()
        except Exception as e:
            print(f"Critical: Could not load Pillow's default font: {e}. Text rendering will fail.")
            return None

    if hasattr(draw, 'textbbox'):
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    else:
        text_width, text_height = draw.textsize(text, font=font)

    x = (image_width - text_width) / 2
    y = (image_height - text_height) / 2
    draw.text((x, y), text, fill='black', font=font)

    try:
        img.save(TEMP_TEXT_IMAGE_PATH)
        return TEMP_TEXT_IMAGE_PATH
    except Exception as e:
        print(f"Error saving temporary text image: {e}")
        return None

def image_to_ascii(image_path, width=100, char_set_name="default"):
    """
    Converts an image file to ASCII art using a specified character set.
    """
    char_ramp = ASCII_CHAR_SETS.get(char_set_name, ASCII_CHAR_SETS[DEFAULT_CHARSET_NAME])
    num_chars = len(char_ramp)

    try:
        img = Image.open(image_path)
    except FileNotFoundError:
        return f"Error: Image not found at {image_path}"
    except Exception as e:
        return f"Error: Could not open image. {e}"

    img = img.convert("L") # Convert to grayscale

    original_width, original_height = img.size
    aspect_ratio = original_height / float(original_width)
    new_height = int(aspect_ratio * width * 0.55)
    img = img.resize((width, new_height))

    ascii_art_list = []
    pixels = img.getdata()
    for i, pixel_value in enumerate(pixels):
        char_index = int((pixel_value / 255) * (num_chars - 1))
        ascii_art_list.append(char_ramp[char_index])
        if (i + 1) % width == 0:
            ascii_art_list.append("\n")

    return "".join(ascii_art_list)

def main():
    parser = argparse.ArgumentParser(
        description="ASCII-M-A-T-I-C-5000: Convert images or text to ASCII art.",
        formatter_class=argparse.RawTextHelpFormatter # To allow newlines in help text
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--image", help="Path to the input image file.")
    group.add_argument("--text", help="Input text to convert to ASCII art.")

    parser.add_argument(
        "--width",
        type=int,
        default=100,
        help="Width of the output ASCII art (default: 100 characters)."
    )
    parser.add_argument(
        "--charset",
        choices=list(ASCII_CHAR_SETS.keys()),
        default=DEFAULT_CHARSET_NAME,
        help="Choose the ASCII character set (ramp) for rendering.\n"
             "Available sets:\n" +
             "\n".join([f"  {name}: '{''.join(chars).replace('%', '%%')}'" for name, chars in ASCII_CHAR_SETS.items()]) +
             f"\n(default: {DEFAULT_CHARSET_NAME})"
    )

    args = parser.parse_args()

    print("Welcome to the ASCII-M-A-T-I-C-5000!\n")

    image_path_to_convert = None
    input_source_message = ""

    if args.text:
        print(f"Generating image from text: \"{args.text}\"")
        image_path_to_convert = text_to_image(args.text)
        if image_path_to_convert:
            input_source_message = f"text input \"{args.text}\" (via {image_path_to_convert})"
        else:
            print("Failed to generate image from text.")
            return
    elif args.image:
        image_path_to_convert = args.image
        input_source_message = f"image file {image_path_to_convert}"

    if image_path_to_convert:
        print(f"Attempting to convert {input_source_message} to ASCII art (width: {args.width}, charset: {args.charset}).")
        ascii_output = image_to_ascii(image_path_to_convert, width=args.width, char_set_name=args.charset)

        print("-" * 30)
        print(ascii_output)
        print("-" * 30)
        print("Conversion complete.")

        if args.text and os.path.exists(TEMP_TEXT_IMAGE_PATH):
            try:
                os.remove(TEMP_TEXT_IMAGE_PATH)
            except Exception as e:
                print(f"Warning: Could not remove temporary image {TEMP_TEXT_IMAGE_PATH}: {e}")
    else:
        print("Error: No valid input (image or text) provided or text-to-image failed.")

if __name__ == "__main__":
    main()
