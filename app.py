from flask import Flask, render_template, request, url_for
import os
import logging # For better logging

# Import functions from your existing script
from ascii_matic_5000 import image_to_ascii, text_to_image, ASCII_CHAR_SETS, TEMP_TEXT_IMAGE_PATH, DEFAULT_CHARSET_NAME

app = Flask(__name__)

# Configuration
# Place uploads inside the static folder temporarily if that simplifies serving/access,
# or keep in assets/uploads if preferred for separation.
# For simplicity in sandbox, assets/uploads is fine.
UPLOAD_FOLDER = 'assets/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16MB max upload size

# Ensure upload folder exists
# Correctly create assets and assets/uploads relative to the application root.
app_root_path = os.path.dirname(os.path.abspath(__file__))
assets_dir_abs = os.path.join(app_root_path, 'assets')
upload_dir_abs = os.path.join(app_root_path, UPLOAD_FOLDER)

if not os.path.exists(assets_dir_abs):
    os.makedirs(assets_dir_abs)
if not os.path.exists(upload_dir_abs):
    os.makedirs(upload_dir_abs)

# Setup basic logging
logging.basicConfig(level=logging.INFO)
# You might want to configure Flask's logger more specifically in a production scenario
# app.logger.setLevel(logging.INFO)


@app.route('/')
def index():
    # Pass charsets and default charset to the template
    return render_template('index.html', charsets=ASCII_CHAR_SETS.keys(), default_charset=DEFAULT_CHARSET_NAME, form_input={})

@app.route('/generate', methods=['POST'])
def generate_ascii():
    form_input = request.form.to_dict() # Store form data to pass back
    ascii_art = ""
    error_message = None
    processed_image_path = None # Path of the image that will be converted

    try:
        input_type = request.form.get('input_type')

        try:
            width = int(request.form.get('width', 100))
            if not (10 <= width <= 500):
                app.logger.warning(f"Invalid width {width} received, defaulting to 100.")
                width = 100
                form_input['width'] = '100' # Update for repopulation
        except ValueError:
            app.logger.warning(f"Non-integer width '{request.form.get('width')}' received, defaulting to 100.")
            width = 100
            form_input['width'] = '100'

        charset = request.form.get('charset', DEFAULT_CHARSET_NAME)
        if charset not in ASCII_CHAR_SETS:
            app.logger.warning(f"Invalid charset '{charset}' received, defaulting to {DEFAULT_CHARSET_NAME}.")
            charset = DEFAULT_CHARSET_NAME
            form_input['charset'] = charset # Update for repopulation

        if input_type == 'text':
            text_input = request.form.get('text_input', '').strip()
            if not text_input:
                error_message = "Text input cannot be empty."
            else:
                # text_to_image saves to TEMP_TEXT_IMAGE_PATH (relative to where ascii_matic_5000.py is)
                # Ensure TEMP_TEXT_IMAGE_PATH is correctly resolved if it's not absolute
                # For now, assume it's correctly handled by ascii_matic_5000.py
                processed_image_path = text_to_image(text_input)
                if not processed_image_path:
                    error_message = "Could not generate image from text. Font might be missing or an error occurred."

        elif input_type == 'image':
            if 'image_upload' not in request.files:
                error_message = "No image file part in the request."
            else:
                file = request.files['image_upload']
                if file.filename == '':
                    error_message = "No image file selected."
                elif file:
                    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
                    filename_parts = file.filename.rsplit('.', 1)
                    if len(filename_parts) > 1 and filename_parts[1].lower() in allowed_extensions:
                        from werkzeug.utils import secure_filename
                        s_filename = secure_filename(file.filename)
                        # Save to the absolute path of the upload directory
                        saved_image_path = os.path.join(upload_dir_abs, s_filename)
                        file.save(saved_image_path)
                        processed_image_path = saved_image_path
                    else:
                        error_message = "Invalid image file type. Allowed: png, jpg, jpeg, gif, bmp."
        else:
            error_message = "Invalid input type selected. Please choose 'Text' or 'Image'."

        if not error_message and processed_image_path:
            conversion_result = image_to_ascii(processed_image_path, width=width, char_set_name=charset)
            if "Error:" in conversion_result:
                error_message = conversion_result
            else:
                ascii_art = conversion_result
        elif not error_message and not processed_image_path and input_type in ['text', 'image']:
            error_message = "Input processed, but no image was available for ASCII conversion."
        elif not error_message and input_type not in ['text', 'image']: # Should be caught by "Invalid input type"
             error_message = "No valid input provided for generation."


    except Exception as e:
        app.logger.error(f"An unexpected error occurred in /generate: {e}", exc_info=True)
        error_message = f"An unexpected server-side error occurred: {str(e)}"

    finally:
        # Clean up temporary files
        if input_type == 'text' and processed_image_path == TEMP_TEXT_IMAGE_PATH:
            # TEMP_TEXT_IMAGE_PATH is relative to ascii_matic_5000.py. If app.py is in root, it's 'assets/temp_text_image.png'
            temp_text_img_abs_path = os.path.join(app_root_path, TEMP_TEXT_IMAGE_PATH)
            if os.path.exists(temp_text_img_abs_path):
                try:
                    os.remove(temp_text_img_abs_path)
                except Exception as e_remove:
                    app.logger.error(f"Warning: Could not remove temporary text image {temp_text_img_abs_path}: {e_remove}")
        elif input_type == 'image' and processed_image_path and processed_image_path.startswith(upload_dir_abs):
            if os.path.exists(processed_image_path):
                try:
                    os.remove(processed_image_path)
                except Exception as e_remove:
                    app.logger.error(f"Warning: Could not remove uploaded image {processed_image_path}: {e_remove}")

    return render_template('index.html', charsets=ASCII_CHAR_SETS.keys(), default_charset=DEFAULT_CHARSET_NAME,
                           ascii_art=ascii_art, error=error_message, form_input=form_input)

if __name__ == '__main__':
    # Make sure the app is accessible in typical sandbox/container environments
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 8080))
