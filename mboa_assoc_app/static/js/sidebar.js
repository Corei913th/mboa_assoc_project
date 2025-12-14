/**
 * Sidebar Navigation - Mobile & Desktop
 * Gestion de l'ouverture/fermeture de la sidebar sur mobile
 */

document.addEventListener('DOMContentLoaded', function () {
  const sidebar = document.getElementById('sidebar');
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebarOverlay = document.getElementById('sidebarOverlay');

  if (!sidebar || !sidebarToggle || !sidebarOverlay) {
    return; // Pas de sidebar sur cette page
  }

  /**
   * Toggle la sidebar (ouvrir/fermer)
   */
  function toggleSidebar() {
    sidebar.classList.toggle('open');
    sidebarOverlay.classList.toggle('visible');
    
    // Accessibilité : gérer l'attribut aria-expanded
    const isOpen = sidebar.classList.contains('open');
    sidebarToggle.setAttribute('aria-expanded', isOpen);
    
    // Empêcher le scroll du body quand la sidebar est ouverte sur mobile
    if (window.innerWidth < 1024) {
      document.body.style.overflow = isOpen ? 'hidden' : '';
    }
  }

  /**
   * Fermer la sidebar
   */
  function closeSidebar() {
    sidebar.classList.remove('open');
    sidebarOverlay.classList.remove('visible');
    sidebarToggle.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
  }

  // Event listeners
  sidebarToggle.addEventListener('click', toggleSidebar);
  sidebarOverlay.addEventListener('click', closeSidebar);

  // Fermer la sidebar avec la touche ESC
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && sidebar.classList.contains('open')) {
      closeSidebar();
    }
  });

  // Fermer la sidebar automatiquement sur mobile après un clic sur un lien
  const sidebarLinks = sidebar.querySelectorAll('.sidebar-nav-item');
  sidebarLinks.forEach(link => {
    link.addEventListener('click', function () {
      if (window.innerWidth < 1024) {
        setTimeout(closeSidebar, 200); // Petit délai pour la transition
      }
    });
  });

  // Gérer le resize de la fenêtre
  let resizeTimer;
  window.addEventListener('resize', function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function () {
      // Sur desktop, toujours fermer l'overlay et réactiver le scroll
      if (window.innerWidth >= 1024) {
        sidebarOverlay.classList.remove('visible');
        document.body.style.overflow = '';
      }
    }, 250);
  });
});
