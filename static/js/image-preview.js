document.getElementById('face-images').addEventListener('change', function(event) {
    const container = document.getElementById('preview-container');
    container.innerHTML = '';
    
    const files = event.target.files;
    
    if (files.length !== 10) {
        alert('Please select exactly 10 images');
        event.target.value = '';
        return;
    }
    
    for (let file of files) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const div = document.createElement('div');
            div.style.width = '100px';
            div.style.height = '100px';
            div.style.overflow = 'hidden';
            
            const img = document.createElement('img');
            img.src = e.target.result;
            img.style.width = '100%';
            img.style.height = '100%';
            img.style.objectFit = 'cover';
            
            div.appendChild(img);
            container.appendChild(div);
        }
        reader.readAsDataURL(file);
    }
}); 