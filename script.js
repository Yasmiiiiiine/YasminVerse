/**
 * YasmineVerse — Portfolio Logic
 * Gère la navigation, les interactions et la connexion aux APIs
 */

(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', () => {
    initSmoothScroll();
    initProjectLinks();
  });

  /* ── 1. Navigation fluide ── */
  function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
          window.scrollTo({
            top: target.offsetTop - 80,
            behavior: 'smooth'
          });
        }
      });
    });
  }

  /* ── 2. Gestion des liens projets (Connexion Render) ── */
  function initProjectLinks() {
    const projects = [
      { id: 'btn-cyber', url: 'https://ton-lien-render-1.onrender.com' },
      { id: 'btn-uni', url: 'https://ton-lien-render-2.onrender.com' }
    ];

    projects.forEach(p => {
      const btn = document.getElementById(p.id);
      if (btn) {
        btn.addEventListener('click', (e) => {
          console.log(`Ouverture du projet : ${p.url}`);
          // Ici, tu peux ajouter une animation de chargement si besoin
        });
      }
    });
  }

  /* ── 3. Notification Console pour le Développeur ── */
  console.log("%c YasmineVerse Hub est opérationnel ! 🛡️", "color: #1e3799; font-weight: bold;");

})();
