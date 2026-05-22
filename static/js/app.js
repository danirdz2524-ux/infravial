console.log("Sistema InfraVial iniciado - Versión Mejorada");

// Auto-cerrar alertas después de 3 segundos
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(function() {
        let alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            let bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 3000);
});

// Drag & drop para fotografía
const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('fileInput');
const previewContainer = document.getElementById('previewContainer');
const previewImage = document.getElementById('previewImage');
const removeBtn = document.getElementById('removeImage');

if (dropzone) {
    dropzone.addEventListener('click', () => fileInput.click());
    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.style.borderColor = '#2c7da0';
    });
    dropzone.addEventListener('dragleave', () => {
        dropzone.style.borderColor = '#e0e4e8';
    });
    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.style.borderColor = '#e0e4e8';
        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith('image/')) {
            fileInput.files = e.dataTransfer.files;
            showPreview(file);
        }
    });
}

fileInput.addEventListener('change', (e) => {
    if (fileInput.files.length > 0) {
        showPreview(fileInput.files[0]);
    }
});

function showPreview(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImage.src = e.target.result;
        previewContainer.style.display = 'block';
        dropzone.style.display = 'none';
    };
    reader.readAsDataURL(file);
}

if (removeBtn) {
    removeBtn.addEventListener('click', () => {
        fileInput.value = '';
        previewContainer.style.display = 'none';
        dropzone.style.display = 'block';
    });
}

// Agregar al final de tu app.js o en el HTML
console.log("✅ Manual de usuario integrado - Botón de ayuda flotante");

// Mostrar número de ficha si es edición (se puede pasar desde Jinja)
// Si estamos en nueva ficha, badge "Nueva". Si es edición, muestra el número.
// En tu template de edición (editar_ficha.html) puedes usar {{ ficha.ficha_numero }}
// Para este formulario (nuevo) se queda como "Nueva"