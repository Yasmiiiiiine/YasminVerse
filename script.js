/**
 * YasmineVerse — Interactivité du portfolio
 * Smooth scroll, modale ville interactive et connexions aux serveurs de calcul
 */

(function () {
  'use strict';

  const HEADER_OFFSET = 80;

  /* ── Données des bâtiments (ville interactive) ── */
  const BUILDING_DATA = {
    banque: {
      icon: '🏦',
      title: 'Banque',
      subtitle: 'Stage en informatique',
      description:
        "Explorez mon expérience professionnelle au sein du secteur bancaire. Ce bâtiment représente mon attestation de stage en informatique, où j'ai consolidé mes compétences en solutions informatiques appliquées à un environnement exigeant.",
      stats: [
        { value: '3 mois', label: 'Durée' },
        { value: '100%', label: 'Autonomie' },
        { value: 'A+', label: 'Évaluation' }
      ],
      tags: ['Stage', 'Informatique', 'Secteur bancaire', 'Solutions IT']
    },
    studio: {
      icon: '🎨',
      title: 'Studio',
      subtitle: 'Graphic Design',
      description:
        "Bienvenue dans mon studio créatif ! Découvrez mes réalisations Adobe Illustrator et Canva : identités visuelles, supports éditoriaux et modèles de cahiers. Chaque création reflète ma sensibilité esthétique et ma maîtrise des outils de design.",
      stats: [
        { value: '6+', label: 'Créations' },
        { value: 'AI', label: 'Illustrator' },
        { value: 'Canva', label: 'Outil' }
      ],
      tags: ['Illustrator', 'Canva', 'Identité Visuelle', 'Vector Art']
    },
    laboratoire: {
      icon: '🤖',
      title: 'Laboratoire',
      subtitle: 'Intelligence Artificielle',
      description:
        "Le cœur algorithmique de mon portfolio. Ici sont hébergés mes projets d'apprentissage automatique pur, dont EduPredict ML, qui analyse mathématiquement les métriques d'assiduité pour prévenir l'échec universitaire.",
      stats: [
        { value: '94%', label: 'Précision' },
        { value: 'Python', label: 'Core' },
        { value: 'FastAPI', label: 'Serveur' }
      ],
      tags: ['Machine Learning', 'Data Science', 'Random Forest', 'XAI']
    },
    securite: {
      icon: '🛡️',
      title: 'Centre de sécurité',
      subtitle: 'Cybersécurité',
      description:
        "Mon domaine de spécialisation. Ce pôle intègre CyberShield AI et mon IDS intelligent UniShield ML pour surveiller, classifier et bloquer en une fraction de seconde les requêtes anormales (DDoS, Bruteforce, Scans).",
      stats: [
        { value: 'Temps réel', label: 'Analyse' },
        { value: 'IDS', label: 'Système' },
        { value: 'XGBoost', label: 'Option ML' }
      ],
      tags: ['Cybersecurity', 'IDS', 'Network Traffic', 'Intrusion Detection']
    }
  };

  /* ── 1. Smooth Scroll ── */
  function initSmoothScroll() {
    const links = document.querySelectorAll('.nav-links a, .hero-actions a');
    links.forEach(function (link) {
      link.addEventListener('click', function (e) {
        const href = link.getAttribute('href');
        if (href.startsWith('#')) {
          e.preventDefault();
          const target = document.querySelector(href);
          if (target) {
            const elementPosition = target.getBoundingClientRect().top;
            const offsetPosition = elementPosition + window.pageYOffset - HEADER_OFFSET;
            window.scrollTo({
              top: offsetPosition,
              behavior: 'smooth'
            });
          }
        }
      });
    });
  }

  /* ── 2. Fenêtre Modale de la Ville ── */
  function initCityModal() {
    const overlay = document.getElementById('city-modal');
    if (!overlay) return;

    const closeBtn = overlay.querySelector('.modal-close');
    const titleEl = document.getElementById('modal-title');
    const subtitleEl = overlay.querySelector('.modal-subtitle');
    const descEl = overlay.querySelector('.modal-description');
    const statsContainer = overlay.querySelector('.modal-stats');
    const tagsContainer = overlay.querySelector('.modal-tags');
    const iconEl = overlay.querySelector('.modal-header .modal-icon');
    const buildings = document.querySelectorAll('.building');

    function openModal(buildingKey) {
      const data = BUILDING_DATA[buildingKey];
      if (!data) return;

      const activeBuilding = document.querySelector('.building[data-building="' + buildingKey + '"]');
      if (activeBuilding) activeBuilding.classList.add('is-active');

      iconEl.innerText = data.icon;
      titleEl.innerText = data.title;
      subtitleEl.innerText = data.subtitle;
      descEl.innerText = data.description;

      statsContainer.innerHTML = data.stats
        .map(function (s) {
          return '<div><span class="stat-val">' + s.value + '</span><span class="stat-lbl">' + s.label + '</span></div>';
        })
        .join('');

      tagsContainer.innerHTML = data.tags
        .map(function (tag) {
          return '<span>' + tag + '</span>';
        })
        .join('');

      overlay.classList.add('is-open');
      document.body.style.overflow = 'hidden';
    }

    function closeModal() {
      overlay.classList.remove('is-open');
      document.body.style.overflow = '';
      buildings.forEach(function (b) {
        b.classList.remove('is-active');
      });
    }

    buildings.forEach(function (building) {
      building.addEventListener('click', function () {
        openModal(building.dataset.building);
      });
    });

    closeBtn.addEventListener('click', closeModal);
    overlay.addEventListener('click', function (e) {
      if (e.target === overlay) closeModal();
    });
  }

  /* ── 3. Logique Interactive du Jeu Tic-Tac-Toe (X/O) ── */
  function initTicTacToe() {
    let currentBoard = ["", "", "", "", "", "", "", "", ""];
    let isGameRunning = true;
    const cells = document.querySelectorAll('.cell');
    const msgDisplay = document.getElementById('game-message');
    const resetBtn = document.getElementById('btn-reset-game');

    if (!cells.length) return;

    function cellClicked(e) {
      const idx = parseInt(e.target.dataset.index);
      if (currentBoard[idx] !== "" || !isGameRunning) return;

      // Joueur Humain (X en Bleu)
      currentBoard[idx] = "X";
      e.target.innerText = "X";
      e.target.classList.add('player-x');

      msgDisplay.innerText = "L'ordinateur réfléchit...";

      // Communication avec l'API Tic-Tac-Toe locale (Port 8002)
     fetch('https://yasmineverse-tictactoe.onrender.com/play', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ board: currentBoard })
      })
      .then(res => res.json())
      .then(data => {
        currentBoard = data.board;
        
        // Appliquer la réponse de l'ordinateur (O en Rouge)
        cells.forEach((cell, i) => {
          if (currentBoard[i] === "O") {
            cell.innerText = "O";
            cell.classList.add('computer-o');
          }
        });

        msgDisplay.innerText = data.message;

        if (data.status === "gagne_humain" || data.status === "gagne_ordinateur") {
          isGameRunning = false;
          highlightWinners(data.status === "gagne_humain" ? "X" : "O");
        } else if (data.status === "egalite") {
          isGameRunning = false;
        }
      })
      .catch(() => {
        msgDisplay.innerText = "❌ Lancez app_game.py (Port 8002)";
      });
    }

    function highlightWinners(sym) {
      const combos = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]];
      combos.forEach(c => {
        if (currentBoard[c[0]] === sym && currentBoard[c[1]] === sym && currentBoard[c[2]] === sym) {
          c.forEach(i => cells[i].classList.add('winner-cell')); // Passe en Vert
        }
      });
    }

    cells.forEach(c => c.addEventListener('click', cellClicked));
    if (resetBtn) {
      resetBtn.addEventListener('click', () => {
        currentBoard = ["", "", "", "", "", "", "", "", ""];
        isGameRunning = true;
        msgDisplay.innerText = "À votre tour !";
        cells.forEach(c => { c.innerText = ""; c.className = "cell"; });
      });
    }
  }

  /* ── 4. Connexion avec UniShield ML (IDS — Port 8001) ── */
  function initUniShieldIDS() {
    const btn = document.getElementById('btn-simulate-ids');
    if (!btn) return;

    btn.addEventListener('click', () => {
      const scenarios = [
        { duree: 1.2, paquets: 14, octets: 6200 },
        { duree: 0.3, paquets: 1800, octets: 920000 }, // DDoS
        { duree: 0.02, paquets: 310, octets: 42000 }   // PortScan
      ];
      const selected = scenarios[Math.floor(Math.random() * scenarios.length)];

      fetch('https://yasmineverse-unishield.onrender.com/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(selected)
      })
      .then(res => res.json())
      .then(data => {
        const badge = document.getElementById('ids-status-badge');
        badge.innerText = data.status;
        
        if (data.intrusion_detectee) {
          badge.className = "status-badge-alert";
        } else {
          badge.className = "";
          badge.style.background = "rgba(52, 211, 153, 0.1)";
          badge.style.color = "var(--success)";
          badge.style.border = "1px solid var(--success)";
        }
        
        document.getElementById('ids-threat').innerText = data.classification.type_menace;
        document.getElementById('ids-conf').innerText = data.classification.score_confiance;
        document.getElementById('ids-log').innerText = "> " + data.classification.analyse_technique;
      })
      .catch(() => {
        document.getElementById('ids-log').innerText = "❌ Moteur déconnecté. Lancez app_ids.py (Port 8001)";
      });
    });
  }

  /* ── 5. Connexion avec EduPredict ML (Échec Scolaire — Port 8000) ── */
  function initEduPredict() {
    const btn = document.getElementById('btn-predict-edu');
    if (!btn) return;

    btn.addEventListener('click', () => {
      const note = parseFloat(document.getElementById('edu-note').value);
      const abs = parseInt(document.getElementById('edu-abs').value);

      fetch('https://yasmineverse-edupredict.onrender.com/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ note_interro: note, absences_tp: abs, heures_connexion: 42.0 })
      })
      .then(res => res.json())
      .then(data => {
        document.getElementById('edu-result-box').style.display = "block";
        document.getElementById('edu-risk').innerText = data.prediction.niveau_risque + " (" + data.prediction.pourcentage_risque + ")";
        document.getElementById('edu-xai').innerText = data.prediction.explication_xai;
      })
      .catch(() => {
        alert("Activez d'abord le serveur Python app.py du projet EduPredict sur le port 8000 !");
      });
    });
  }

  /* ── Chargement Général ── */
  document.addEventListener('DOMContentLoaded', function () {
    initSmoothScroll();
    initCityModal();
    initTicTacToe();
    initUniShieldIDS();
    initEduPredict();
  });

})();
