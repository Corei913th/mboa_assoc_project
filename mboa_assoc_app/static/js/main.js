

/**
 * Afficher un message toast
 */
function showToast(message, type = 'info') {
  const toast = document.createElement('div');
  toast.className = `alert alert-${type} fixed top-4 right-4 z-50 shadow-lg animate-slide-in`;
  toast.style.minWidth = '300px';
  toast.innerHTML = `<p class="text-sm">${message}</p>`;
  
  document.body.appendChild(toast);
  
  setTimeout(() => {
    toast.classList.add('animate-slide-out');
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

/**
 * Formater un numéro de téléphone camerounais
 */
function formatPhoneNumber(phone) {
  // Supprimer tous les caractères non numériques sauf le +
  let cleaned = phone.replace(/[^\d+]/g, '');
  
  // Ajouter +237 si nécessaire
  if (!cleaned.startsWith('+237')) {
    if (cleaned.startsWith('237')) {
      cleaned = '+' + cleaned;
    } else if (cleaned.startsWith('6') || cleaned.startsWith('2')) {
      cleaned = '+237' + cleaned;
    }
  }
  
  return cleaned;
}

/**
 * Valider un numéro de téléphone camerounais
 */
function isValidCameroonPhone(phone) {
  const pattern = /^\+237[0-9]{9}$/;
  return pattern.test(phone);
}

/**
 * Débounce - Limiter la fréquence d'exécution d'une fonction
 */
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// ============================================
// GESTION DES FORMULAIRES
// ============================================

/**
 * Validation en temps réel des champs de formulaire
 */
function setupFormValidation() {
  const forms = document.querySelectorAll('form[data-validate]');
  
  forms.forEach(form => {
    const inputs = form.querySelectorAll('input[required], textarea[required]');
    
    inputs.forEach(input => {
      input.addEventListener('blur', function() {
        validateField(this);
      });
      
      input.addEventListener('input', debounce(function() {
        if (this.classList.contains('error')) {
          validateField(this);
        }
      }, 500));
    });
  });
}

function validateField(field) {
  const value = field.value.trim();
  const type = field.type;
  let isValid = true;
  let errorMessage = '';
  
  // Vérifier si le champ est requis et vide
  if (field.hasAttribute('required') && !value) {
    isValid = false;
    errorMessage = 'Ce champ est obligatoire';
  }
  
  // Validation spécifique par type
  if (value && type === 'email') {
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailPattern.test(value)) {
      isValid = false;
      errorMessage = 'Adresse email invalide';
    }
  }
  
  if (value && type === 'tel') {
    if (!isValidCameroonPhone(value)) {
      isValid = false;
      errorMessage = 'Numéro de téléphone invalide (format: +237XXXXXXXXX)';
    }
  }
  
  // Afficher ou masquer l'erreur
  if (isValid) {
    field.classList.remove('error');
    removeFieldError(field);
  } else {
    field.classList.add('error');
    showFieldError(field, errorMessage);
  }
  
  return isValid;
}

function showFieldError(field, message) {
  removeFieldError(field);
  
  const errorDiv = document.createElement('div');
  errorDiv.className = 'field-error text-error text-sm mt-1';
  errorDiv.textContent = message;
  
  field.parentNode.appendChild(errorDiv);
}

function removeFieldError(field) {
  const existingError = field.parentNode.querySelector('.field-error');
  if (existingError) {
    existingError.remove();
  }
}

// ============================================
// GESTION DES MESSAGES
// ============================================

/**
 * Auto-masquer les messages Django après quelques secondes
 */
function setupMessageAutoHide() {
  const messages = document.querySelectorAll('.alert');
  
  messages.forEach(message => {
    setTimeout(() => {
      message.style.opacity = '0';
      message.style.transform = 'translateY(-20px)';
      message.style.transition = 'all 0.3s ease';
      
      setTimeout(() => message.remove(), 300);
    }, 5000);
  });
}

// ============================================
// INITIALISATION
// ============================================

document.addEventListener('DOMContentLoaded', function() {
  // Initialiser la validation des formulaires
  setupFormValidation();
  
  // Auto-masquer les messages
  setupMessageAutoHide();
  
  // Formater automatiquement les champs téléphone
  const phoneInputs = document.querySelectorAll('input[type="tel"]');
  phoneInputs.forEach(input => {
    input.addEventListener('blur', function() {
      this.value = formatPhoneNumber(this.value);
    });
  });
});

// ============================================
// EXPORT POUR UTILISATION GLOBALE
// ============================================

window.MboaUtils = {
  showToast,
  formatPhoneNumber,
  isValidCameroonPhone,
  debounce,
  validateField
};
