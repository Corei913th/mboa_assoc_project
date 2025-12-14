/**
 * Gestionnaire OTP - Formulaire de vérification avec 6 inputs séparés
 * Fonctionnalités :
 * - Navigation automatique entre les champs
 * - Support du collage de code
 * - Timer de compte à rebours
 * - Validation en temps réel
 * - Désactivation du bouton tant que tous les champs ne sont pas remplis
 */

class OTPHandler {
  constructor() {
    this.otpInputs = document.querySelectorAll('.otp-input');
    this.submitBtn = document.getElementById('submitBtn');
    this.fullCodeInput = document.getElementById('fullCode');
    this.form = document.getElementById('otpForm');
    this.timerElement = document.getElementById('timer');
    this.timerText = document.getElementById('timerText');
    this.timeLeft = 600; // 10 minutes en secondes
    this.timerInterval = null;

    this.init();
  }

  init() {
    if (!this.otpInputs.length) return;

    this.setupInputHandlers();
    this.setupFormHandler();
    this.startTimer();
    
    // Focus automatique sur le premier input
    this.otpInputs[0].focus();
  }

  setupInputHandlers() {
    this.otpInputs.forEach((input, index) => {
      // Saisie de caractère
      input.addEventListener('input', (e) => this.handleInput(e, index));
      
      // Retour arrière
      input.addEventListener('keydown', (e) => this.handleKeydown(e, index));
      
      // Collage
      input.addEventListener('paste', (e) => this.handlePaste(e));
      
      // Sélection au focus
      input.addEventListener('focus', function() {
        this.select();
      });
    });
  }

  handleInput(e, index) {
    const value = e.target.value;
    
    // Accepter uniquement les chiffres
    if (!/^\d$/.test(value)) {
      e.target.value = '';
      return;
    }

    // Marquer comme rempli
    if (value.length === 1) {
      e.target.classList.add('filled');
      e.target.classList.remove('error');
      
      // Passer au champ suivant
      if (index < this.otpInputs.length - 1) {
        this.otpInputs[index + 1].focus();
      }
    }

    this.checkAllFilled();
  }

  handleKeydown(e, index) {
    if (e.key === 'Backspace') {
      if (e.target.value === '' && index > 0) {
        // Revenir au champ précédent
        this.otpInputs[index - 1].focus();
        this.otpInputs[index - 1].value = '';
        this.otpInputs[index - 1].classList.remove('filled');
      } else {
        e.target.value = '';
        e.target.classList.remove('filled');
      }
      this.checkAllFilled();
    }
  }

  handlePaste(e) {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text').trim();
    
    // Vérifier que c'est bien 6 chiffres
    if (/^\d{6}$/.test(pastedData)) {
      // Remplir tous les champs
      pastedData.split('').forEach((char, i) => {
        if (i < this.otpInputs.length) {
          this.otpInputs[i].value = char;
          this.otpInputs[i].classList.add('filled');
        }
      });
      
      // Focus sur le dernier champ
      this.otpInputs[this.otpInputs.length - 1].focus();
      this.checkAllFilled();
    }
  }

  checkAllFilled() {
    const allFilled = Array.from(this.otpInputs).every(input => input.value.length === 1);
    this.submitBtn.disabled = !allFilled;
    
    if (allFilled) {
      // Construire le code complet
      const code = Array.from(this.otpInputs).map(input => input.value).join('');
      this.fullCodeInput.value = code;
      
      // Ajouter la classe "filled" à tous les inputs
      this.otpInputs.forEach(input => input.classList.add('filled'));
    } else {
      this.fullCodeInput.value = '';
    }
  }

  setupFormHandler() {
    this.form.addEventListener('submit', (e) => {
      // Vérifier que tous les champs sont remplis
      if (!this.fullCodeInput.value || this.fullCodeInput.value.length !== 6) {
        e.preventDefault();
        
        // Marquer les champs vides en erreur
        this.otpInputs.forEach(input => {
          if (input.value === '') {
            input.classList.add('error');
          }
        });
        
        return false;
      }

      // Désactiver le bouton pour éviter les doubles soumissions
      this.submitBtn.disabled = true;
      this.submitBtn.innerHTML = `
        <svg class="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
        </svg>
        Vérification...
      `;
    });
  }

  startTimer() {
    this.updateTimer();
    this.timerInterval = setInterval(() => this.updateTimer(), 1000);
  }

  updateTimer() {
    const minutes = Math.floor(this.timeLeft / 60);
    const seconds = this.timeLeft % 60;
    this.timerText.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;

    // Changer la couleur selon le temps restant
    if (this.timeLeft <= 60) {
      this.timerElement.classList.add('expired');
      this.timerElement.classList.remove('warning');
    } else if (this.timeLeft <= 180) {
      this.timerElement.classList.add('warning');
      this.timerElement.classList.remove('expired');
    }

    if (this.timeLeft <= 0) {
      clearInterval(this.timerInterval);
      this.timerText.textContent = 'Expiré';
      
      // Désactiver les inputs
      this.otpInputs.forEach(input => {
        input.disabled = true;
        input.classList.add('error');
      });
      this.submitBtn.disabled = true;
      
      // Afficher un message
      this.showExpiredMessage();
    }

    this.timeLeft--;
  }

  showExpiredMessage() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'alert alert-error';
    messageDiv.innerHTML = `
      <p class="text-sm font-medium">Le code OTP a expiré.</p>
      <p class="text-sm">Veuillez demander un nouveau code.</p>
    `;
    
    const form = document.getElementById('otpForm');
    form.parentNode.insertBefore(messageDiv, form);
  }

  handleError() {
    // Marquer tous les inputs en erreur
    this.otpInputs.forEach(input => {
      input.classList.add('error');
      setTimeout(() => {
        input.classList.remove('error');
      }, 3000);
    });
    
    // Vider tous les champs
    this.otpInputs.forEach(input => {
      input.value = '';
      input.classList.remove('filled');
    });
    
    // Focus sur le premier champ
    this.otpInputs[0].focus();
  }
}

// Initialiser au chargement de la page
document.addEventListener('DOMContentLoaded', () => {
  new OTPHandler();
});
