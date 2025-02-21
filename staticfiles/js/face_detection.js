class FaceDetector {
    constructor() {
        this.video = document.createElement('video');
        this.canvas = document.createElement('canvas');
        this.photo = document.createElement('img');
    }

    async start() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            this.video.srcObject = stream;
            await this.video.play();
        } catch (err) {
            console.error("Error accessing camera:", err);
        }
    }

    capture() {
        const context = this.canvas.getContext('2d');
        this.canvas.width = this.video.videoWidth;
        this.canvas.height = this.video.videoHeight;
        context.drawImage(this.video, 0, 0);
        return this.canvas.toDataURL('image/jpeg');
    }

    stop() {
        const stream = this.video.srcObject;
        const tracks = stream.getTracks();
        tracks.forEach(track => track.stop());
    }
}