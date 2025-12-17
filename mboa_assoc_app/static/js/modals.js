/**
 * Modal Management System
 * Gestion des modals avec Tailwind CSS
 */

/**
 * Ouvre un modal
 * @param {string} modalId - ID du modal à ouvrir
 */
function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove('hidden');
    setTimeout(() => modal.classList.add('show'), 10);
    document.body.style.overflow = 'hidden';
    
    // Focus sur le premier input
    const firstInput = modal.querySelector('input, textarea, select');
    if (firstInput) {
      setTimeout(() => firstInput.focus(), 100);
    }
  }
}

/**
 * Ferme un modal
 * @param {string} modalId - ID du modal à fermer
 */
function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove('show');
    setTimeout(() => {
      modal.classList.add('hidden');
      document.body.style.overflow = '';
      
      // Reset form if exists
      const form = modal.querySelector('form');
      if (form) {
        form.reset();
      }
    }, 300);
  }
}

/**
 * Ferme tous les modals ouverts
 */
function closeAllModals() {
  document.querySelectorAll('.modal-overlay.show').forEach(modal => {
    closeModal(modal.id);
  });
}

// Initialize modal system when DOM is ready
document.addEventListener('DOMContentLoaded', function () {
  // Close on overlay click
  document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', function (e) {
      if (e.target === this) {
        closeModal(this.id);
      }
    });
  });

  // Close on Escape key
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      closeAllModals();
    }
  });

  // Handle form submissions with loading states
  document.querySelectorAll('.modal-content form').forEach(form => {
    form.addEventListener('submit', function (e) {
      const submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn && !submitBtn.disabled) {
        submitBtn.disabled = true;
        const originalHTML = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Envoi...';
        
        // Re-enable after 5 seconds as fallback
        setTimeout(() => {
          submitBtn.disabled = false;
          submitBtn.innerHTML = originalHTML;
        }, 5000);
      }
    });
  });
});
