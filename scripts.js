/**
 * Escapes HTML special characters to prevent XSS attacks
 * @param {string} unsafe - The unsafe string to escape
 * @returns {string} - The escaped string safe for HTML insertion
 */
function escapeHtml(unsafe) {
    const div = document.createElement('div');
    div.textContent = unsafe;
    return div.innerHTML;
}

/**
 * Get CSRF token from meta tag or cookie
 * @returns {string} - The CSRF token
 */
function getCsrfToken() {
    // Try to get from meta tag first
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    if (metaTag) {
        return metaTag.getAttribute('content');
    }
    
    // Fallback to cookie
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrf_token') {
            return decodeURIComponent(value);
        }
    }
    return '';
}

/**
 * Show Received Text with proper XSS protection
 */
function showText() {
    fetch('/get_text')
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch text');
            }
            return response.text();
        })
        .then(data => {
            const contentDiv = document.getElementById('content');
            const lines = data.split('\n').filter(line => line.trim() !== '');
            
            if (lines.length > 0) {
                // Create DOM elements instead of string concatenation
                const container = document.createElement('div');
                const heading = document.createElement('h2');
                heading.textContent = 'Recently Received Text';
                container.appendChild(heading);
                
                lines.forEach(line => {
                    const lineDiv = document.createElement('div');
                    lineDiv.className = 'line';
                    lineDiv.textContent = line; // Safe - uses textContent instead of innerHTML
                    lineDiv.addEventListener('click', () => copyText(line));
                    lineDiv.setAttribute('role', 'button');
                    lineDiv.setAttribute('tabindex', '0');
                    container.appendChild(lineDiv);
                });
                
                contentDiv.innerHTML = '';
                contentDiv.appendChild(container);
            } else {
                contentDiv.innerHTML = '<p>No text received yet.</p>';
            }
        })
        .catch(error => {
            console.error('Error loading text:', error);
            showNotification('Failed to load text', 'error');
        });
}

/**
 * Copy Text to Clipboard with better UX
 * @param {string} text - The text to copy
 */
function copyText(text) {
    navigator.clipboard.writeText(text)
        .then(() => {
            showNotification('Copied to clipboard!', 'success');
        })
        .catch(err => {
            console.error('Failed to copy:', err);
            showNotification('Failed to copy text', 'error');
        });
}

/**
 * Show notification instead of alert
 * @param {string} message - The message to display
 * @param {string} type - The notification type (success, error, info)
 */
function showNotification(message, type = 'info') {
    // Fallback to alert for now - will be replaced with toast in UI modernization
    alert(message);
}

/**
 * Show Received Files with XSS protection
 */
function showFiles() {
    fetch('/get_files')
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch files');
            }
            return response.json();
        })
        .then(files => {
            const contentDiv = document.getElementById('content');
            const container = document.createElement('div');
            
            const heading = document.createElement('h2');
            heading.textContent = 'Recently Received Files';
            container.appendChild(heading);
            
            if (files.length > 0) {
                const ul = document.createElement('ul');
                
                files.forEach(file => {
                    const li = document.createElement('li');
                    const fileName = escapeHtml(file.name);
                    const filePath = `/received_files/${encodeURIComponent(file.name)}`;
                    const isImage = /\.(jpg|jpeg|png|gif|bmp|webp)$/i.test(file.name);
                    
                    // Download link
                    const downloadLink = document.createElement('a');
                    downloadLink.href = filePath;
                    downloadLink.download = file.name;
                    downloadLink.textContent = file.name;
                    li.appendChild(downloadLink);
                    
                    // View button for images
                    if (isImage) {
                        const viewBtn = document.createElement('button');
                        viewBtn.textContent = 'View';
                        viewBtn.addEventListener('click', () => openImagePopup(filePath));
                        li.appendChild(viewBtn);
                    }
                    
                    // Rename button
                    const renameBtn = document.createElement('button');
                    renameBtn.textContent = 'Rename';
                    renameBtn.addEventListener('click', () => showRenamePrompt(file.name));
                    li.appendChild(renameBtn);
                    
                    ul.appendChild(li);
                });
                
                container.appendChild(ul);
            } else {
                const noFiles = document.createElement('p');
                noFiles.textContent = 'No files received yet.';
                container.appendChild(noFiles);
            }
            
            contentDiv.innerHTML = '';
            contentDiv.appendChild(container);
        })
        .catch(error => {
            console.error('Error loading files:', error);
            showNotification('Failed to load files', 'error');
        });
}

/**
 * Show Rename Prompt with validation
 * @param {string} oldName - The current filename
 */
function showRenamePrompt(oldName) {
    const newName = prompt("Enter new name for the file (including extension):", oldName);
    if (newName && newName !== oldName) {
        // Basic validation
        if (newName.includes('/') || newName.includes('\\')) {
            showNotification('Filename cannot contain / or \\', 'error');
            return;
        }
        if (newName.trim() === '') {
            showNotification('Filename cannot be empty', 'error');
            return;
        }
        renameFile(oldName, newName);
    }
}

/**
 * Rename File with error handling
 * @param {string} oldName - The current filename
 * @param {string} newName - The new filename
 */
function renameFile(oldName, newName) {
    const formData = new FormData();
    formData.append("old_name", oldName);
    formData.append("new_name", newName);
    
    // Add CSRF token
    const csrfToken = getCsrfToken();
    if (csrfToken) {
        formData.append("csrf_token", csrfToken);
    }

    fetch('/rename_file', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': csrfToken
        }
    })
        .then(response => {
            if (response.ok) {
                showNotification("File renamed successfully", 'success');
                showFiles();
            } else {
                return response.text().then(text => {
                    throw new Error(text || 'Failed to rename file');
                });
            }
        })
        .catch(error => {
            console.error('Rename error:', error);
            showNotification(error.message || 'Failed to rename file', 'error');
        });
}

/**
 * Open Popup for image preview
 * @param {string} imageSrc - The image source URL
 */
function openImagePopup(imageSrc) {
    const popupImage = document.getElementById('popup-image');
    const downloadBtn = document.getElementById('download-btn');
    const popup = document.getElementById('popup');
    
    popupImage.src = imageSrc;
    downloadBtn.href = imageSrc;
    popup.style.display = 'flex';
    
    // Add keyboard accessibility
    popup.focus();
}

/**
 * Close Popup
 */
function closePopup() {
    document.getElementById('popup').style.display = 'none';
}

// Event listener for logo click to upload files
document.getElementById('skydrop-logo').addEventListener('click', function () {
    document.getElementById('file-input').click();
});

// Event listener for file input change
document.getElementById('file-input').addEventListener('change', function () {
    uploadFile();
});

// Close popup on Escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closePopup();
    }
});

/**
 * Upload File with progress feedback
 */
function uploadFile() {
    const fileInput = document.getElementById('file-input');
    
    if (!fileInput.files || fileInput.files.length === 0) {
        showNotification('No file selected', 'error');
        return;
    }
    
    const file = fileInput.files[0];
    
    // Validate file size (16MB limit)
    if (file.size > 16 * 1024 * 1024) {
        showNotification('File size exceeds 16MB limit', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    // Add CSRF token
    const csrfToken = getCsrfToken();
    if (csrfToken) {
        formData.append('csrf_token', csrfToken);
    }

    fetch('/upload_file', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': csrfToken
        }
    })
        .then(response => {
            if (response.ok) {
                showNotification("File uploaded successfully", 'success');
                fileInput.value = ''; // Clear the input
                showFiles();
            } else {
                return response.text().then(text => {
                    throw new Error(text || 'Failed to upload file');
                });
            }
        })
        .catch(error => {
            console.error('Upload error:', error);
            showNotification(error.message || 'Failed to upload file', 'error');
        });
}
