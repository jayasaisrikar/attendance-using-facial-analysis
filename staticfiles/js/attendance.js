document.addEventListener('DOMContentLoaded', function() {
    const photoInput = document.getElementById('class_photo');
    const preview = document.getElementById('preview');
    const form = document.getElementById('attendanceForm');

    photoInput.addEventListener('change', function() {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                preview.src = e.target.result;
                preview.classList.remove('d-none');
            }
            reader.readAsDataURL(file);
        }
    });

    form.addEventListener('submit', function(e) {
        const loadingButton = document.querySelector('button[type="submit"]');
        loadingButton.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Processing...';
        loadingButton.disabled = true;
    });
});