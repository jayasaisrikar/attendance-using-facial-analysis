class CameraCapture {
    constructor() {
        this.videoElement = document.getElementById('video-preview');
        this.captureButton = document.getElementById('capture-btn');
        this.previewContainer = document.getElementById('preview-container');
        this.capturedImages = [];
        this.stream = null;
    }

    async init() {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({ video: true });
            this.videoElement.srcObject = this.stream;
            document.getElementById('start-camera').style.display = 'none';
            document.querySelector('.camera-container').style.display = 'block';
        } catch (err) {
            console.error('Error accessing camera:', err);
            alert('Error accessing camera. Please ensure camera permissions are granted.');
        }
    }

    capture() {
        const canvas = document.createElement('canvas');
        canvas.width = this.videoElement.videoWidth;
        canvas.height = this.videoElement.videoHeight;
        const context = canvas.getContext('2d');
        context.drawImage(this.videoElement, 0, 0);

        // Create preview
        const img = document.createElement('img');
        img.src = canvas.toDataURL('image/jpeg');
        img.className = 'captured-image';
        this.previewContainer.appendChild(img);

        // Convert to blob and store
        canvas.toBlob((blob) => {
            const file = new File([blob], `face_${this.capturedImages.length}.jpg`, { type: 'image/jpeg' });
            this.capturedImages.push(file);
            this.updateFormData();
        }, 'image/jpeg', 0.9);
    }

    updateFormData() {
        const form = document.getElementById('signup-form');
        
        // Remove existing face_images inputs
        form.querySelectorAll('input[name="face_images[]"]').forEach(el => el.remove());
        
        // Add new file inputs for each captured image
        this.capturedImages.forEach((file) => {
            const input = document.createElement('input');
            input.type = 'file';
            input.name = 'face_images[]';
            input.style.display = 'none';
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            input.files = dataTransfer.files;
            
            form.appendChild(input);
        });
    }

    stopCamera() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
        }
    }
} 