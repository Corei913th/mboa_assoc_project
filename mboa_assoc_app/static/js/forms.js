/**
 * Script de gestion des formulaires pour les associations
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialiser tous les gestionnaires
    initializeFormValidation();
    initializeFileUpload();
    initializeConfirmations();
    initializeSearchUsers();
});

/**
 * Validation des formulaires en temps réel
 */
function initializeFormValidation() {
    const forms = document.querySelectorAll('form[data-validate="true"]');
    
    forms.forEach(form => {
        // Validation lors de la soumission
        form.addEventListener('submit', function(e) {
            if (!validateForm(form)) {
                e.preventDefault();
            }
        });
        
        // Validation en temps réel des champs
        const inputs = form.querySelectorAll('.form-input, .form-textarea, .form-select');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(input);
            });
            
            input.addEventListener('input', function() {
                clearFieldError(input);
            });
        });
    });
}

/**
 * Valide un formulaire complet
 */
function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!validateField(field)) {
            isValid = false;
        }
    });
    
    return isValid;
}

/**
 * Valide un champ individuel
 */
function validateField(field) {
    const value = field.value.trim();
    const fieldName = field.name;
    let errorMessage = '';
    
    // Champ requis
    if (field.hasAttribute('required') && !value) {
        errorMessage = 'Ce champ est requis';
    }
    
    // Validation spécifique par type de champ
    if (value) {
        switch(fieldName) {
            case 'name':
                if (value.length < 3) {
                    errorMessage = 'Le nom doit contenir au moins 3 caractères';
                }
                break;
            
            case 'email':
                if (!isValidEmail(value)) {
                    errorMessage = 'Adresse email invalide';
                }
                break;
        }
    }
    
    // Afficher ou masquer l'erreur
    if (errorMessage) {
        showFieldError(field, errorMessage);
        return false;
    } else {
        clearFieldError(field);
        return true;
    }
}

/**
 * Affiche une erreur sur un champ
 */
function showFieldError(field, message) {
    field.classList.add('error');
    
    // Supprimer l'ancien message d'erreur s'il existe
    let errorElement = field.parentElement.querySelector('.form-error');
    if (!errorElement) {
        errorElement = document.createElement('span');
        errorElement.className = 'form-error';
        field.parentElement.appendChild(errorElement);
    }
    
    errorElement.textContent = message;
}

/**
 * Efface l'erreur d'un champ
 */
function clearFieldError(field) {
    field.classList.remove('error');
    
    const errorElement = field.parentElement.querySelector('.form-error');
    if (errorElement) {
        errorElement.remove();
    }
}

/**
 * Valide un email
 */
function isValidEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

/**
 * Gestion de l'upload de fichiers
 */
function initializeFileUpload() {
    const fileInputs = document.querySelectorAll('.form-file');
    
    fileInputs.forEach(input => {
        const wrapper = createFileUploadWrapper(input);
        
        input.addEventListener('change', function(e) {
            handleFileSelect(e, wrapper);
        });
    });
}

/**
 * Crée le wrapper pour l'upload de fichier
 */
function createFileUploadWrapper(input) {
    const wrapper = document.createElement('div');
    wrapper.className = 'file-upload-wrapper';
    
    const label = document.createElement('label');
    label.className = 'file-upload-label';
    label.htmlFor = input.id;
    label.innerHTML = `
        <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12"/>
        </svg>
        <span>Cliquez pour choisir un fichier ou glissez-déposez</span>
    `;
    
    const preview = document.createElement('div');
    preview.className = 'file-preview';
    preview.style.display = 'none';
    
    input.parentNode.insertBefore(wrapper, input);
    wrapper.appendChild(input);
    wrapper.appendChild(label);
    wrapper.appendChild(preview);
    
    return wrapper;
}

/**
 * Gère la sélection d'un fichier
 */
function handleFileSelect(e, wrapper) {
    const file = e.target.files[0];
    const preview = wrapper.querySelector('.file-preview');
    const label = wrapper.querySelector('.file-upload-label');
    
    if (file) {
        // Vérifier la taille (max 5MB)
        if (file.size > 5 * 1024 * 1024) {
            alert('Le fichier est trop volumineux (max 5MB)');
            e.target.value = '';
            return;
        }
        
        // Afficher l'aperçu pour les images
        if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = function(event) {
                preview.innerHTML = `
                    <img src="${event.target.result}" alt="Aperçu" style="max-width: 200px; border-radius: 8px;">
                    <p>${file.name} (${formatFileSize(file.size)})</p>
                `;
                preview.style.display = 'block';
                label.style.display = 'none';
            };
            reader.readAsDataURL(file);
        } else {
            preview.innerHTML = `<p>${file.name} (${formatFileSize(file.size)})</p>`;
            preview.style.display = 'block';
            label.style.display = 'none';
        }
    }
}

/**
 * Formate la taille d'un fichier
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Dialogues de confirmation
 */
function initializeConfirmations() {
    const confirmButtons = document.querySelectorAll('[data-confirm]');
    
    confirmButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm');
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
}

/**
 * Recherche d'utilisateurs en temps réel
 */
function initializeSearchUsers() {
    const searchInput = document.querySelector('#user-search');
    if (!searchInput) return;
    
    let searchTimeout;
    
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        
        const query = this.value.trim();
        
        if (query.length < 2) {
            hideSearchResults();
            return;
        }
        
        // Attendre 500ms après la dernière frappe
        searchTimeout = setTimeout(() => {
            searchUsers(query);
        }, 500);
    });
}

/**
 * Recherche les utilisateurs via AJAX
 */
function searchUsers(query) {
    const resultsContainer = document.querySelector('#search-results');
    if (!resultsContainer) return;
    
    // Afficher un loader
    resultsContainer.innerHTML = '<p class="text-muted">Recherche en cours...</p>';
    resultsContainer.style.display = 'block';
    
    // Effectuer la recherche (adapter l'URL selon votre configuration)
    const url = `?search=${encodeURIComponent(query)}`;
    
    fetch(url, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.text())
    .then(html => {
        // Extraire les résultats (à adapter selon votre structure HTML)
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const results = doc.querySelector('#search-results');
        
        if (results) {
            resultsContainer.innerHTML = results.innerHTML;
        }
    })
    .catch(error => {
        console.error('Erreur de recherche:', error);
        resultsContainer.innerHTML = '<p class="text-danger">Erreur lors de la recherche</p>';
    });
}

/**
 * Masque les résultats de recherche
 */
function hideSearchResults() {
    const resultsContainer = document.querySelector('#search-results');
    if (resultsContainer) {
        resultsContainer.style.display = 'none';
    }
}

/**
 * Auto-dismiss des messages après 5 secondes
 */
document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => {
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 300);
    }, 5000);
});