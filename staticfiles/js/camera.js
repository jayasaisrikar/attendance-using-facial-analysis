class CameraCapture {
    constructor() {
        this.stream = null;
        this.capturedImages = [];
    }

    async init() {
        try {
            const startBtn = document.getElementById('start-camera');
            startBtn.addEventListener('click', () => this.startCamera());
        } catch (error) {
            console.error('Error initializing camera:', error);
        }
    }

    async startCamera() {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({ video: true });
            const videoPreview = document.getElementById('video-preview');
            videoPreview.srcObject = this.stream;
            document.querySelector('.camera-container').style.display = 'block';
        } catch (error) {
            console.error('Error accessing camera:', error);
        }
    }

    capture() {
        const video = document.getElementById('video-preview');
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext('2d').drawImage(video, 0, 0);
        
        canvas.toBlob((blob) => {
            const file = new File([blob], `face_${Date.now()}.jpg`, { type: 'image/jpeg' });
            this.capturedImages.push(file);
            this.displayPreview(URL.createObjectURL(blob));
            this.updateFormData();
        }, 'image/jpeg');
    }

    displayPreview(url) {
        const previewContainer = document.getElementById('preview-container');
        const div = document.createElement('div');
        div.className = 'preview-image';
        const img = document.createElement('img');
        img.src = url;
        div.appendChild(img);
        previewContainer.appendChild(div);
    }

    updateFormData() {
        const form = document.getElementById('signup-form');
        // Remove any existing face_images inputs
        form.querySelectorAll('input[name="face_images"]').forEach(el => el.remove());
        
        // Add new file inputs for each captured image
        this.capturedImages.forEach((file, index) => {
            const input = document.createElement('input');
            input.type = 'file';
            input.name = 'face_images';
            input.style.display = 'none';
            
            // Create a DataTransfer object and add the file
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            input.files = dataTransfer.files;
            
            form.appendChild(input);
        });
    }
} 