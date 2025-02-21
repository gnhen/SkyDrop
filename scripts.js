// Show Received Text
function showText() {
    fetch('/get_text')
        .then(response => response.text())
        .then(data => {
            const lines = data.split('\n').filter(line => line.trim() !== '');
            if (lines.length > 0) {
                let html = '<h2>Recently Received Text</h2>';
                lines.forEach(line => {
                    html += `<div class="line" onclick="copyText('${line.replace(/'/g, "\\'")}')">${line}</div>`;
                });
                document.getElementById('content').innerHTML = html;
            } else {
                document.getElementById('content').innerHTML = '<p>No text received yet.</p>';
            }
        });
}

// Copy Text to Clipboard
function copyText(text) {
    navigator.clipboard.writeText(text).then(() => {
        alert("Copied");
    });
}

// Show Received Files
function showFiles() {
    fetch('/get_files')
        .then(response => response.json())
        .then(files => {
            let html = '<h2>Recently Received Files</h2>';
            if (files.length > 0) {
                html += '<ul>';
                files.forEach(file => {
                    const filePath = `/received_files/${file.name}`;
                    const isImage = /\.(jpg|jpeg|png|gif|bmp|webp)$/i.test(file.name);

                    html += `<li>
                                <a href="${filePath}" download>${file.name}</a>
                                ${isImage ? `<button onclick="openImagePopup('${filePath}')">View</button>` : ''}
                                <button onclick="showRenamePrompt('${file.name}')">Rename</button>
                             </li>`;
                });
                html += '</ul>';
            } else {
                html += '<p>No files received yet.</p>';
            }
            document.getElementById('content').innerHTML = html;
        });
}

// Show Rename Prompt
function showRenamePrompt(oldName) {
    const newName = prompt("Enter new name for the file (including extension):", oldName);
    if (newName && newName !== oldName) {
        renameFile(oldName, newName);
    }
}

// Rename File
function renameFile(oldName, newName) {
    const formData = new FormData();
    formData.append("old_name", oldName);
    formData.append("new_name", newName);

    fetch('/rename_file', {
        method: 'POST',
        body: formData
    })
        .then(response => {
            if (response.ok) {
                alert("File renamed successfully");
                showFiles();
            } else {
                alert("Failed to rename file");
            }
        });
}

// Open Popup
function openImagePopup(imageSrc) {
    document.getElementById('popup-image').src = imageSrc;
    document.getElementById('download-btn').href = imageSrc;
    document.getElementById('popup').style.display = 'flex';
}

// Close Popup
function closePopup() {
    document.getElementById('popup').style.display = 'none';
}
