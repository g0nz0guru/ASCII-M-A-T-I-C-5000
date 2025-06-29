function toggleInputFields() {
    const inputType = document.querySelector('input[name="input_type"]:checked').value;
    const textInputGroup = document.getElementById('text_input_group');
    const imageUploadGroup = document.getElementById('image_upload_group');
    const textArea = document.getElementById('text_input_area');
    const imageInput = document.getElementById('image_upload_input');

    if (inputType === 'text') {
        textInputGroup.style.display = 'block';
        imageUploadGroup.style.display = 'none';
        if (textArea) textArea.required = true;
        if (imageInput) imageInput.required = false;
    } else { // 'image'
        textInputGroup.style.display = 'none';
        imageUploadGroup.style.display = 'block';
        if (textArea) textArea.required = false;
        if (imageInput) imageInput.required = true;
    }
}

function saveScrollPositionAndShowLoading() {
    const asciiArtDiv = document.getElementById('ascii_art_output');
    if (asciiArtDiv && asciiArtDiv.innerHTML.trim() !== '') {
        localStorage.setItem('asciiArtScrollY', window.scrollY);
    }

    const submitButton = document.querySelector('form button[type="submit"]');
    if (submitButton) {
        submitButton.disabled = true;
        submitButton.textContent = 'Generating...';
    }

    let loadingMessageDiv = document.getElementById('loading_message_container');
    if (loadingMessageDiv) {
        loadingMessageDiv.style.display = 'block';
        loadingMessageDiv.textContent = 'Generating your ASCII art, please wait...';
    }
    return true; // Allow form submission to proceed
}

window.onload = function() {
    // Restore input type selection from data attribute set by Flask/Jinja
    const currentInputType = document.body.getAttribute('data-current-input-type') || 'text';
    if (currentInputType === 'image') {
        const imageRadio = document.getElementById('input_type_image');
        if (imageRadio) imageRadio.checked = true;
    } else {
        const textRadio = document.getElementById('input_type_text');
        if (textRadio) textRadio.checked = true;
    }
    toggleInputFields(); // Apply visibility based on restored state

    // Restore scroll position for ASCII art if it exists
    const asciiArtDiv = document.getElementById('ascii_art_output');
    if (asciiArtDiv && asciiArtDiv.innerHTML.trim() !== '') {
        const scrollY = localStorage.getItem('asciiArtScrollY');
        if (scrollY) {
            window.scrollTo(0, parseInt(scrollY, 10));
            localStorage.removeItem('asciiArtScrollY');
        }
    }

    // Add change listeners to radio buttons
    document.querySelectorAll('input[name="input_type"]').forEach(radio => {
        radio.addEventListener('change', toggleInputFields);
    });

    // Attach the submit handler to the form
    const mainForm = document.getElementById('ascii_form');
    if (mainForm) {
        mainForm.addEventListener('submit', saveScrollPositionAndShowLoading);
    }
};
