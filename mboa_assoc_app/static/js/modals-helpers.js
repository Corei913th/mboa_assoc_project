/**
 * Helpers pour les modals génériques
 * DRY: Une seule source de vérité pour les modals
 */

function showConfirmModal(options) {
  const {
    title = 'Confirmation',
    message,
    action,
    method = 'POST',
    buttonText = 'Confirmer',
    buttonClass = 'btn-error',
    icon = 'fa-exclamation-triangle',
    iconClass = 'text-warning'
  } = options;

  document.getElementById('confirmTitle').textContent = title;
  document.getElementById('confirmMessage').textContent = message;
  document.getElementById('confirmIcon').className = `fa-solid ${icon} ${iconClass}`;
  
  const form = document.getElementById('confirmForm');
  form.action = action;
  form.method = method;
  
  const button = document.getElementById('confirmButton');
  button.textContent = buttonText;
  button.className = `btn ${buttonClass}`;
  
  openModal('confirmModal');
}

function showSuccessModal(message, callback) {
  Toast.success(message);
  if (callback) setTimeout(callback, 1500);
}

function showErrorModal(message) {
  Toast.error(message);
}

function confirmDelete(itemName, deleteUrl) {
  showConfirmModal({
    title: 'Supprimer',
    message: `Êtes-vous sûr de vouloir supprimer "${itemName}" ? Cette action est irréversible.`,
    action: deleteUrl,
    buttonText: 'Supprimer',
    buttonClass: 'btn-error',
    icon: 'fa-trash',
    iconClass: 'text-error'
  });
}

function confirmExclude(memberName, excludeUrl) {
  showConfirmModal({
    title: 'Exclure un membre',
    message: `Êtes-vous sûr de vouloir exclure "${memberName}" ? Cette action est irréversible.`,
    action: excludeUrl,
    buttonText: 'Exclure',
    buttonClass: 'btn-error',
    icon: 'fa-user-xmark',
    iconClass: 'text-error'
  });
}

function confirmArchive(itemName, archiveUrl) {
  showConfirmModal({
    title: 'Archiver',
    message: `Êtes-vous sûr de vouloir archiver "${itemName}" ?`,
    action: archiveUrl,
    buttonText: 'Archiver',
    buttonClass: 'btn-warning',
    icon: 'fa-archive',
    iconClass: 'text-warning'
  });
}

// Helper pour les formulaires avec feedback
function submitFormWithFeedback(form, successMessage, errorMessage) {
  const formData = new FormData(form);
  const loadingToast = Toast.loading('Envoi en cours...');
  
  fetch(form.action, {
    method: form.method || 'POST',
    body: formData,
    headers: {'X-Requested-With': 'XMLHttpRequest'}
  })
  .then(response => response.json())
  .then(data => {
    Toast.remove(loadingToast);
    if (data.success) {
      Toast.success(successMessage || data.message);
      if (data.redirect) setTimeout(() => window.location.href = data.redirect, 1500);
    } else {
      Toast.error(errorMessage || data.error);
    }
  })
  .catch(() => {
    Toast.remove(loadingToast);
    Toast.error('Une erreur est survenue');
  });
}
