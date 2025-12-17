/**
 * Système de notifications Toast
 * DRY: Une seule source pour tous les feedbacks utilisateur
 */

const Toast = {
  container: null,
  
  init() {
    this.container = document.getElementById('toastContainer');
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.id = 'toastContainer';
      this.container.className = 'fixed top-4 right-4 z-50 space-y-2';
      document.body.appendChild(this.container);
    }
  },
  
  show(options) {
    this.init();
    
    const {
      type = 'info',
      title,
      message,
      duration = 5000,
      closable = true
    } = options;
    
    const icons = {
      success: 'fa-check-circle',
      error: 'fa-exclamation-circle',
      warning: 'fa-exclamation-triangle',
      info: 'fa-info-circle'
    };
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
      <i class="fa-solid ${icons[type]} toast-icon icon-${type}"></i>
      <div class="toast-content">
        ${title ? `<div class="toast-title">${title}</div>` : ''}
        <div class="toast-message">${message}</div>
      </div>
      ${closable ? '<i class="fa-solid fa-times toast-close"></i>' : ''}
    `;
    
    if (closable) {
      toast.querySelector('.toast-close').addEventListener('click', () => this.remove(toast));
    }
    
    this.container.appendChild(toast);
    
    if (duration > 0) {
      setTimeout(() => this.remove(toast), duration);
    }
    
    return toast;
  },
  
  remove(toast) {
    toast.classList.add('toast-exit');
    setTimeout(() => toast.remove(), 300);
  },
  
  success(message, title = 'Succès') {
    return this.show({ type: 'success', title, message });
  },
  
  error(message, title = 'Erreur') {
    return this.show({ type: 'error', title, message, duration: 7000 });
  },
  
  warning(message, title = 'Attention') {
    return this.show({ type: 'warning', title, message });
  },
  
  info(message, title = 'Information') {
    return this.show({ type: 'info', title, message });
  },
  
  // Helpers pour les actions courantes
  created(itemName) {
    return this.success(`${itemName} créé avec succès`);
  },
  
  updated(itemName) {
    return this.success(`${itemName} modifié avec succès`);
  },
  
  deleted(itemName) {
    return this.success(`${itemName} supprimé avec succès`);
  },
  
  saved() {
    return this.success('Modifications enregistrées');
  },
  
  loading(message = 'Chargement en cours...') {
    return this.show({ type: 'info', message, duration: 0, closable: false });
  }
};

// Intégration avec Django messages
document.addEventListener('DOMContentLoaded', () => {
  const djangoMessages = document.querySelectorAll('.django-message');
  djangoMessages.forEach(msg => {
    const type = msg.dataset.type || 'info';
    const message = msg.textContent.trim();
    Toast.show({ type, message });
    msg.remove();
  });
});

// Export global
window.Toast = Toast;
