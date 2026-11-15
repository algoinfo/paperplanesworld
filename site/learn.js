(() => {
  const filters = document.querySelector(".learn-filters");
  const status = document.querySelector(".learn-filter-status");
  const countLabel = document.getElementById("learn-count");
  const cards = [...document.querySelectorAll(".learn-card")];
  const families = [...document.querySelectorAll(".learn-family[data-family]")];
  const jumps = [...document.querySelectorAll(".family-jump a[data-family]")];

  if (!filters || !cards.length) return;

  let active = "all";

  function match(card, key) {
    if (key === "all") return true;
    const keys = (card.getAttribute("data-keys") || "").split(/\s+/);
    return keys.includes(key);
  }

  function apply() {
    let visible = 0;
    const familyVisible = {};

    cards.forEach((card) => {
      const ok = match(card, active);
      card.classList.toggle("is-filtered-out", !ok);
      if (ok) {
        visible += 1;
        const fam = card.closest(".learn-family")?.dataset.family;
        if (fam) familyVisible[fam] = (familyVisible[fam] || 0) + 1;
      }
    });

    families.forEach((section) => {
      const id = section.dataset.family;
      const n = familyVisible[id] || 0;
      section.classList.toggle("is-empty", n === 0);
      const jump = jumps.find((a) => a.dataset.family === id);
      if (jump) {
        const countEl = jump.querySelector(".jump-count");
        if (countEl) countEl.textContent = String(n);
        jump.classList.toggle("is-empty", n === 0);
      }
    });

    if (countLabel) {
      countLabel.textContent = window.PPW.t("learnCount", {
        n: visible,
        total: cards.length,
      });
    }

    if (status) {
      status.textContent =
        active === "all"
          ? ""
          : window.PPW.t("learnFilterStatus", { n: visible, total: cards.length });
    }
  }

  filters.addEventListener("click", (e) => {
    const btn = e.target.closest("button[data-filter]");
    if (!btn) return;
    active = btn.dataset.filter || "all";
    filters.querySelectorAll("button[data-filter]").forEach((b) => {
      b.setAttribute("aria-pressed", b === btn ? "true" : "false");
    });
    apply();
  });

  window.addEventListener("ppw:lang", () => {
    // Refresh step labels + status copy after language switch.
    document.querySelectorAll(".lc-meta [data-steps]").forEach((el) => {
      const n = el.getAttribute("data-steps");
      el.textContent = window.PPW.t("stepsCount", { n });
    });
    apply();
  });

  document.querySelectorAll(".lc-meta [data-steps]").forEach((el) => {
    const n = el.getAttribute("data-steps");
    el.textContent = window.PPW.t("stepsCount", { n });
  });

  apply();
})();
