(function () {
  "use strict";

  const endpoints = {
    edupredict: "/api/edupredict/predict",
    unishield: "/api/unishield/analyze",
    tictactoe: "/api/tictactoe/play"
  };

  function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach((link) => {
      link.addEventListener("click", (event) => {
        const target = document.querySelector(link.getAttribute("href"));
        if (!target) return;
        event.preventDefault();
        target.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    });
  }

  function initCopyButtons() {
    document.querySelectorAll("[data-copy]").forEach((button) => {
      button.addEventListener("click", async () => {
        const value = `${window.location.origin}${button.dataset.copy}`;
        try {
          await navigator.clipboard.writeText(value);
          const original = button.textContent;
          button.textContent = "Route copiée";
          window.setTimeout(() => {
            button.textContent = original;
          }, 1400);
        } catch {
          button.textContent = "Copie indisponible";
        }
      });
    });
  }

  async function postJson(url, payload) {
    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      throw new Error(`Réponse ${response.status}`);
    }

    return response.json();
  }

  function initEduPredict() {
    const button = document.getElementById("btn-predict-edu");
    if (!button) return;

    button.addEventListener("click", async () => {
      const resultBox = document.getElementById("edu-result-box");
      const risk = document.getElementById("edu-risk");
      const explanation = document.getElementById("edu-xai");
      const note = Number.parseFloat(document.getElementById("edu-note").value);
      const absences = Number.parseInt(document.getElementById("edu-abs").value, 10);

      resultBox.style.display = "block";
      risk.textContent = "Analyse en cours...";
      explanation.textContent = "YasmineVerse contacte EduPredict ML.";

      try {
        const data = await postJson(endpoints.edupredict, {
          note_interro: note,
          absences_tp: absences,
          heures_connexion: 42
        });
        risk.textContent = `${data.prediction.niveau_risque} (${data.prediction.pourcentage_risque})`;
        explanation.textContent = data.prediction.explication_xai;
      } catch {
        risk.textContent = "Service indisponible";
        explanation.textContent = "Vérifiez que le service Render EduPredict est actif.";
      }
    });
  }

  function initUniShield() {
    const buttons = [
      document.getElementById("btn-simulate-ids"),
      document.getElementById("btn-simulate-ids-panel")
    ].filter(Boolean);
    if (!buttons.length) return;

    const scenarios = [
      { duree: 1.2, paquets: 14, octets: 6200 },
      { duree: 0.3, paquets: 1800, octets: 920000 },
      { duree: 0.02, paquets: 310, octets: 42000 }
    ];

    async function simulate() {
      const status = document.getElementById("ids-status-badge");
      const threat = document.getElementById("ids-threat");
      const confidence = document.getElementById("ids-conf");
      const log = document.getElementById("ids-log");
      const selected = scenarios[Math.floor(Math.random() * scenarios.length)];

      status.textContent = "Analyse...";
      threat.textContent = "-";
      confidence.textContent = "-";
      log.textContent = "YasmineVerse contacte UniShield ML.";

      try {
        const data = await postJson(endpoints.unishield, selected);
        status.textContent = data.status;
        threat.textContent = data.classification.type_menace;
        confidence.textContent = data.classification.score_confiance;
        log.textContent = data.classification.analyse_technique;
      } catch {
        status.textContent = "Indisponible";
        log.textContent = "Vérifiez que le service Render UniShield est actif.";
      }
    }

    buttons.forEach((button) => button.addEventListener("click", simulate));
  }

  function initTicTacToe() {
    const cells = Array.from(document.querySelectorAll(".cell"));
    const message = document.getElementById("game-message");
    const reset = document.getElementById("btn-reset-game");
    if (!cells.length || !message) return;

    let board = Array(9).fill("");
    let running = true;

    function paintBoard() {
      cells.forEach((cell, index) => {
        cell.textContent = board[index];
        cell.className = "cell";
        if (board[index] === "X") cell.classList.add("player-x");
        if (board[index] === "O") cell.classList.add("computer-o");
      });
    }

    function markWinners(symbol) {
      const combos = [
        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 8],
        [0, 3, 6],
        [1, 4, 7],
        [2, 5, 8],
        [0, 4, 8],
        [2, 4, 6]
      ];

      combos.forEach((combo) => {
        if (combo.every((index) => board[index] === symbol)) {
          combo.forEach((index) => cells[index].classList.add("winner-cell"));
        }
      });
    }

    cells.forEach((cell) => {
      cell.addEventListener("click", async () => {
        const index = Number.parseInt(cell.dataset.index, 10);
        if (!running || board[index]) return;

        board[index] = "X";
        paintBoard();
        message.textContent = "L'ordinateur réfléchit...";

        try {
          const data = await postJson(endpoints.tictactoe, { board });
          board = data.board;
          paintBoard();
          message.textContent = data.message;

          if (data.status === "gagne_humain" || data.status === "gagne_ordinateur") {
            running = false;
            markWinners(data.status === "gagne_humain" ? "X" : "O");
          }

          if (data.status === "egalite") {
            running = false;
          }
        } catch {
          message.textContent = "Service TicTacToe indisponible sur Render.";
        }
      });
    });

    reset?.addEventListener("click", () => {
      board = Array(9).fill("");
      running = true;
      message.textContent = "À votre tour !";
      paintBoard();
    });
  }

  function initDesignGallery() {
    const modal = document.getElementById("gallery-modal");
    const image = document.getElementById("gallery-image");
    const title = document.getElementById("gallery-title");
    const close = modal?.querySelector(".gallery-close");
    const previews = document.querySelectorAll("[data-gallery-src]");

    if (!modal || !image || !title || !close || !previews.length) return;

    function openGallery(button) {
      image.src = button.dataset.gallerySrc;
      image.alt = button.dataset.galleryTitle || "Aperçu Graphic Design";
      title.textContent = button.dataset.galleryTitle || "Aperçu";
      modal.classList.add("is-open");
      modal.setAttribute("aria-hidden", "false");
      document.body.style.overflow = "hidden";
    }

    function closeGallery() {
      modal.classList.remove("is-open");
      modal.setAttribute("aria-hidden", "true");
      document.body.style.overflow = "";
      image.src = "";
    }

    previews.forEach((button) => {
      button.addEventListener("click", () => openGallery(button));
    });

    close.addEventListener("click", closeGallery);
    modal.addEventListener("click", (event) => {
      if (event.target === modal) closeGallery();
    });

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && modal.classList.contains("is-open")) {
        closeGallery();
      }
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    initSmoothScroll();
    initCopyButtons();
    initEduPredict();
    initUniShield();
    initTicTacToe();
    initDesignGallery();
  });
})();
