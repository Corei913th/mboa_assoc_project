/**
 * Validation intelligente des formulaires en temps réel
 */

class FormValidator {
  constructor(formId) {
    this.form = document.getElementById(formId);
    if (!this.form) return;
    
    this.submitBtn = this.form.querySelector('button[type="submit"]');
    this.init();
  }

  init() {
    // Validation en temps réel sur tous les champs
    const inputs = this.form.querySelectorAll('input[required], input[type="password"]');
    inputs.forEach(input => {
      input.addEventListener('input', () => {
        this.validateField(input);
        this.updateSubmitButton();
      });
      input.addEventListener('blur', () => {
        this.validateField(input);
        this.updateSubmitButton();
      });
    });

    // Validation initiale du bouton
    this.updateSubmitButton();

    // Validation avant soumission
    this.form.addEventListener('submit', (e) => this.handleSubmit(e));
  }

  validateField(input) {
    const fieldName = input.name;
    let isValid = true;
    let message = '';

    // Validation selon le type de champ
    if (fieldName === 'telephone' || fieldName === 'username') {
      const result = this.validatePhone(input.value);
      isValid = result.valid;
      message = result.message;
    } else if (fieldName === 'password') {
      const result = this.validatePassword(input.value);
      isValid = result.valid;
      message = result.message;
    } else if (fieldName === 'password_confirm') {
      const passwordInput = this.form.querySelector('input[name="password"]');
      const result = this.validatePasswordMatch(passwordInput ? passwordInput.value : '', input.value);
      isValid = result.valid;
      message = result.message;
    } else if (input.hasAttribute('required')) {
      isValid = input.value.trim().length > 0;
      message = isValid ? '' : 'Ce champ est requis';
    }

    this.updateFieldUI(input, isValid, message);
    
    return isValid;
  }

  validatePhone(phone) {
    phone = phone.trim();
    
    if (phone.length === 0) {
      return { valid: false, message: 'Le numéro de téléphone est requis' };
    }

    // Formats acceptés selon Requirements 2.1, 4.1, 13.1:
    // +237XXXXXXXXX (avec +237 suivi de 9 chiffres commençant par 6)
    // 6XXXXXXXX (9 chiffres commençant par 6)
    const phoneRegex = /^(\+237[6][0-9]{8}|[6][0-9]{8})$/;
    
    if (!phoneRegex.test(phone)) {
      return { 
        valid: false, 
        message: 'Format valide: +237XXXXXXXXX ou 6XXXXXXXX' 
      };
    }

    return { valid: true, message: '✓ Numéro valide' };
  }

  validatePassword(password) {
    if (password.length === 0) {
      return { valid: false, message: 'Le mot de passe est requis' };
    }

    if (password.length < 6) {
      return { 
        valid: false, 
        message: `${password.length}/6 caractères minimum` 
      };
    }

    // Vérifier la force
    let strength = 0;
    if (password.length >= 8) strength++;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
    if (/[0-9]/.test(password)) strength++;
    if (/[^a-zA-Z0-9]/.test(password)) strength++;

    const strengthText = ['Faible', 'Moyen', 'Bon', 'Fort'][Math.min(strength, 3)];
    
    return { 
      valid: true, 
      message: `✓ ${strengthText} (${password.length} caractères)`,
      strength: strength
    };
  }

  validatePasswordMatch(password, confirmPassword) {
    if (confirmPassword.length === 0) {
      return { valid: false, message: 'Confirmez votre mot de passe' };
    }

    if (password !== confirmPassword) {
      return { 
        valid: false, 
        message: '✗ Les mots de passe ne correspondent pas' 
      };
    }

    return { valid: true, message: '✓ Les mots de passe correspondent' };
  }

  updateFieldUI(input, isValid, message) {
    const container = input.closest('div');
    let feedbackDiv = container.querySelector('.field-feedback');
    
    // Créer le div de feedback s'il n'existe pas
    if (!feedbackDiv) {
      feedbackDiv = document.createElement('div');
      feedbackDiv.className = 'field-feedback mt-1 text-sm transition-all duration-200';
      input.parentNode.insertBefore(feedbackDiv, input.nextSibling);
    }

    // Mettre à jour les styles du champ
    input.classList.remove('border-red-500', 'border-green-500', 'border-gray-300');
    
    if (input.value.trim().length > 0) {
      if (isValid) {
        input.classList.add('border-green-500');
        feedbackDiv.className = 'field-feedback mt-1 text-sm text-green-600 transition-all duration-200';
      } else {
        input.classList.add('border-red-500');
        feedbackDiv.className = 'field-feedback mt-1 text-sm text-red-600 transition-all duration-200';
      }
      feedbackDiv.textContent = message;
    } else {
      input.classList.add('border-gray-300');
      feedbackDiv.textContent = '';
    }

    // Ajouter une barre de force pour le mot de passe
    /*if (input.name === 'password' && input.value.length > 0 && isValid) {
      const result = this.validatePassword(input.value);
      this.updatePasswordStrengthBar(container, result.strength || 0);
    }*/
  }

  updatePasswordStrengthBar(container, strength) {
    let strengthBar = container.querySelector('.password-strength-bar');
    
    if (!strengthBar) {
      strengthBar = document.createElement('div');
      strengthBar.className = 'password-strength-bar mt-2 h-1 bg-gray-200 rounded-full overflow-hidden';
      strengthBar.innerHTML = '<div class="strength-fill h-full transition-all duration-300"></div>';
      container.appendChild(strengthBar);
    }

    const fill = strengthBar.querySelector('.strength-fill');
    const colors = ['bg-red-500', 'bg-orange-500', 'bg-yellow-500', 'bg-green-500'];
    const widths = ['w-1/4', 'w-2/4', 'w-3/4', 'w-full'];
    
    // Retirer toutes les classes
    colors.forEach(c => fill.classList.remove(c));
    widths.forEach(w => fill.classList.remove(w));
    
    // Ajouter les nouvelles classes
    if (strength > 0) {
      fill.classList.add(colors[Math.min(strength, 3)]);
      fill.classList.add(widths[Math.min(strength, 3)]);
    }
  }

  updateSubmitButton() {
    if (!this.submitBtn) return;

    // Valider tous les champs requis
    const requiredInputs = this.form.querySelectorAll('input[required], input[type="password"]');
    let allValid = true;
    
    requiredInputs.forEach(input => {
      const fieldName = input.name;
      let fieldValid = true;
      
      // Vérifier selon le type de champ
      if (fieldName === 'telephone' || fieldName === 'username') {
        fieldValid = this.validatePhone(input.value).valid;
      } else if (fieldName === 'password') {
        fieldValid = this.validatePassword(input.value).valid;
      } else if (fieldName === 'password_confirm') {
        const passwordInput = this.form.querySelector('input[name="password"]');
        fieldValid = this.validatePasswordMatch(
          passwordInput ? passwordInput.value : '', 
          input.value
        ).valid;
      } else if (input.hasAttribute('required')) {
        fieldValid = input.value.trim().length > 0;
      }
      
      if (!fieldValid) {
        allValid = false;
      }
    });

    // Activer/désactiver le bouton
    this.submitBtn.disabled = !allValid;

    // Mise à jour visuelle du bouton
    if (this.submitBtn.disabled) {
      this.submitBtn.classList.add('opacity-50', 'cursor-not-allowed');
      this.submitBtn.classList.remove('hover:scale-105');
    } else {
      this.submitBtn.classList.remove('opacity-50', 'cursor-not-allowed');
      this.submitBtn.classList.add('hover:scale-105');
    }
  }

  handleSubmit(e) {
    const inputs = this.form.querySelectorAll('input[required], input[type="password"]');
    let allValid = true;

    inputs.forEach(input => {
      if (!this.validateField(input)) {
        allValid = false;
      }
    });

    if (!allValid) {
      e.preventDefault();
      
      // Scroll vers le premier champ invalide
      const firstInvalid = this.form.querySelector('.border-red-500');
      if (firstInvalid) {
        firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
        firstInvalid.focus();
      }
    }
  }
}

// Auto-initialisation
document.addEventListener('DOMContentLoaded', function() {
  // Initialiser pour le formulaire d'inscription
  if (document.getElementById('registerForm')) {
    new FormValidator('registerForm');
  }

  // Initialiser pour le formulaire de connexion
  if (document.getElementById('loginForm')) {
    new FormValidator('loginForm');
  }

  // Initialiser pour le formulaire de profil
  if (document.getElementById('profileForm')) {
    new FormValidator('profileForm');
  }
});
