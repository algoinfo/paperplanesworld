(() => {
  const list = document.getElementById("vg-list");
  const empty = document.getElementById("vg-empty");
  const matchN = document.getElementById("vg-match-n");
  const countLabel = document.getElementById("vg-count");
  const q = document.getElementById("vg-q");
  const cards = [...document.querySelectorAll(".vg-card")];

  if (!list || !cards.length) return;

  const checked = (name) =>
    [...document.querySelectorAll(`input[name="${name}"]:checked`)].map(
      (el) => el.value
    );

  function apply() {
    const query = (q?.value || "").trim().toLowerCase();
    const diffs = checked("vg-diff");
    const types = checked("vg-type");
    const papers = checked("vg-paper");
    let visible = 0;

    cards.forEach((card) => {
      const keys = (card.getAttribute("data-keys") || "").split(/\s+/);
      const name = card.getAttribute("data-name") || "";
      const hitDiff = diffs.some((d) => keys.includes(d));
      const hitType = types.some((t) => keys.includes(t));
      const hitPaper = papers.some((p) => keys.includes(p));
      const hitQ = !query || name.includes(query);
      const ok = hitDiff && hitType && hitPaper && hitQ;
      card.classList.toggle("is-filtered-out", !ok);
      if (ok) visible += 1;
    });

    if (empty) empty.classList.toggle("hidden", visible > 0);
    if (matchN) matchN.textContent = String(visible);
    if (countLabel) {
      countLabel.textContent = window.PPW.t("vgCount", {
        n: visible,
        total: cards.length,
      });
    }

    // localize stat labels after filter/lang
    document.querySelectorAll("[data-i18n-stat]").forEach((el) => {
      const key = el.getAttribute("data-i18n-stat");
      const map = {
        speed: "vgStatSpeed",
        glide: "vgStatGlide",
        accuracy: "vgStatAccuracy",
      };
      if (map[key]) el.textContent = window.PPW.t(map[key]);
    });

    document.querySelectorAll(".vg-diff").forEach((el) => {
      const raw = [...el.classList]
        .find((c) => c.startsWith("diff-"))
        ?.replace("diff-", "");
      if (raw) el.textContent = window.PPW.diffLabel(raw);
    });
  }

  ["input", "change"].forEach((evt) => {
    q?.addEventListener(evt, apply);
    document
      .querySelectorAll('input[name="vg-diff"], input[name="vg-type"], input[name="vg-paper"]')
      .forEach((el) => el.addEventListener(evt, apply));
  });

  window.addEventListener("ppw:lang", () => {
    window.PPW.applyStatic();
    apply();
  });

  apply();
})();
