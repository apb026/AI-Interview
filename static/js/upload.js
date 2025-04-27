// upload.js - Handles the document upload functionality

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const resumeUpload = document.getElementById('resume-upload');
    const jdUpload = document.getElementById('jd-upload');
    const resumeDropzone = document.querySelector('.upload-box.resume-upload');
    const jdDropzone = document.querySelector('.upload-box.jd-upload');
    const resumePreview = document.getElementById('resume-preview');
    const jdPreview = document.getElementById('jd-preview');
    const resumeProgress = document.querySelector('.resume-upload .upload-progress');
    const jdProgress = document.querySelector('.jd-upload .upload-progress');
    const uploadForm = document.getElementById('upload-form');
    const nextButton = document.getElementById('next-button');
    
    // File validation
    const allowedFileTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    const maxFileSize = 5 * 1024 * 1024; // 5MB
    
    // Initialize dropzones
    function initDropzone(dropzone, fileInput, previewElement, progressElement) {
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        // Highlight dropzone when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            dropzone.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, unhighlight, false);
        });
        
        function highlight() {
            dropzone.classList.add('highlight');
        }
        
        function unhighlight() {
            dropzone.classList.remove('highlight');
        }
        
        // Handle dropped files
        dropzone.addEventListener('drop', handleDrop, false);
        
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            if (files.length > 0) {
                handleFiles(files[0]);
            }
        }
        
        // Handle file selection via input
        fileInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                handleFiles(this.files[0]);
            }
        });
        
        // Click to select files
        dropzone.addEventListener('click', function() {
            fileInput.click();
        });
        
        // Process the selected file
        function handleFiles(file) {
            // Validate file type
            if (!allowedFileTypes.includes(file.type)) {
                showError(dropzone, 'Invalid file type. Please upload a PDF or Word document.');
                return;
            }
            
            // Validate file size
            if (file.size > maxFileSize) {
                showError(dropzone, 'File is too large. Maximum size is 5MB.');
                return;
            }
            
            // Clear any previous errors
            clearError(dropzone);
            
            // Update the UI
            updatePreview(file, previewElement);
            
            // Simulate upload
            uploadFile(file, progressElement);
        }
        
        // Show file preview
        function updatePreview(file, previewElement) {
            // Clear previous preview
            previewElement.innerHTML = '';
            
            // Create preview element
            const previewItem = document.createElement('div');
            previewItem.classList.add('preview-item');
            
            // Determine icon based on file type
            let iconClass = 'file-icon';
            if (file.type === 'application/pdf') {
                iconClass += ' pdf-icon';
            } else {
                iconClass += ' doc-icon';
            }
            
            // Format file size
            const fileSize = formatFileSize(file.size);
            
            previewItem.innerHTML = `
                <div class="${iconClass}"></div>
                <div class="file-details">
                    <div class="file-name">${file.name}</div>
                    <div class="file-size">${fileSize}</div>
                </div>
                <button type="button" class="remove-file">×</button>
            `;
            
            previewElement.appendChild(previewItem);
            
            // Add remove button functionality
            previewItem.querySelector('.remove-file').addEventListener('click', function() {
                removeFile(fileInput, previewElement, progressElement);
            });
            
            // Show preview container
            previewElement.parentElement.classList.remove('hidden');
            
            // Hide the dropzone
            dropzone.classList.add('hidden');
        }
        
        // Remove file
        function removeFile(fileInput, previewElement, progressElement) {
            // Reset file input
            fileInput.value = '';
            
            // Clear preview
            previewElement.innerHTML = '';
            previewElement.parentElement.classList.add('hidden');
            
            // Reset progress
            progressElement.style.width = '0%';
            progressElement.textContent = '';
            
            // Show dropzone
            dropzone.classList.remove('hidden');
            
            // Check if we should enable/disable next button
            updateNextButtonState();
        }
        
        // Simulate file upload with progress
        function uploadFile(file, progressElement) {
            let progress = 0;
            const progressInterval = setInterval(() => {
                progress += 5;
                progressElement.style.width = `${progress}%`;
                progressElement.textContent = `${progress}%`;
                
                if (progress >= 100) {
                    clearInterval(progressInterval);
                    progressElement.textContent = 'Complete';
                    
                    // Check if we should enable next button
                    updateNextButtonState();
                }
            }, 100);
        }
    }
    
    // Error handling
    function showError(dropzone, message) {
        // Clear any existing error
        clearError(dropzone);
        
        // Create error message
        const errorElement = document.createElement('div');
        errorElement.classList.add('error-message');
        errorElement.textContent = message;
        
        // Add error message to dropzone
        dropzone.appendChild(errorElement);
        dropzone.classList.add('error');
    }
    
    function clearError(dropzone) {
        // Remove error class
        dropzone.classList.remove('error');
        
        // Remove error message if exists
        const errorElement = dropzone.querySelector('.error-message');
        if (errorElement) {
            errorElement.remove();
        }
    }
    
    // Helper function to format file size
    function formatFileSize(bytes) {
        if (bytes < 1024) {
            return bytes + ' bytes';
        } else if (bytes < 1024 * 1024) {
            return (bytes / 1024).toFixed(1) + ' KB';
        } else {
            return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
        }
    }
    
    // Check if we should enable next button
    function updateNextButtonState() {
        const resumeUploaded = !resumePreview.parentElement.classList.contains('hidden');
        
        if (resumeUploaded) {
            nextButton.removeAttribute('disabled');
            nextButton.classList.remove('disabled');
        } else {
            nextButton.setAttribute('disabled', 'disabled');
            nextButton.classList.add('disabled');
        }
    }
    
    // Initialize form submission
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Validate resume upload
            if (resumePreview.innerHTML === '') {
                showError(resumeDropzone, 'Please upload your resume.');
                return;
            }
            
            // Show loading state
            nextButton.textContent = 'Processing...';
            nextButton.setAttribute('disabled', 'disabled');
            
            // Simulate processing
            setTimeout(() => {
                // In a real app, you would send the files to the server
                // and then redirect to the next page
                window.location.href = '/dashboard';
            }, 2000);
        });
    }
    
    // Job description URL handling
    const jdUrlInput = document.getElementById('jd-url');
    const jdUrlSubmit = document.getElementById('jd-url-submit');
    
    if (jdUrlInput && jdUrlSubmit) {
        jdUrlSubmit.addEventListener('click', function() {
            const url = jdUrlInput.value.trim();
            
            if (!url) {
                jdUrlInput.classList.add('error');
                return;
            }
            
            jdUrlInput.classList.remove('error');
            jdUrlSubmit.textContent = 'Scraping...';
            jdUrlSubmit.setAttribute('disabled', 'disabled');
            
            // Simulate scraping
            setTimeout(() => {
                jdUrlSubmit.textContent = 'Submit';
                jdUrlSubmit.removeAttribute('disabled');
                
                // Show success message
                const successMsg = document.createElement('div');
                successMsg.classList.add('success-message');
                successMsg.textContent = 'Job description scraped successfully!';
                jdUrlInput.parentNode.appendChild(successMsg);
                
                setTimeout(() => {
                    successMsg.remove();
                }, 3000);
                
                // Update JD preview
                const fakeJdFile = {
                    name: 'Scraped Job Description.pdf',
                    size: 245 * 1024,
                    type: 'application/pdf'
                };
                
                updatePreview(fakeJdFile, jdPreview);
                
                // Hide JD dropzone
                jdDropzone.classList.add('hidden');
                
                // Update progress
                const jdProgressElement = document.querySelector('.jd-upload .upload-progress');
                jdProgressElement.style.width = '100%';
                jdProgressElement.textContent = 'Complete';
                
                // Check if we should enable next button
                updateNextButtonState();
            }, 2000);
        });
    }
    
    // Initialize dropzones if they exist on the page
    if (resumeDropzone && resumeUpload) {
        initDropzone(resumeDropzone, resumeUpload, resumePreview, resumeProgress);
    }
    
    if (jdDropzone && jdUpload) {
        initDropzone(jdDropzone, jdUpload, jdPreview, jdProgress);
    }
});