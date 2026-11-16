(() => {
  const state = {
    planes: [],
    filtered: [],
  };

  const els = {
    grid: document.getElementById("plane-grid"),
    empty: document.getElementById("empty"),
    count: document.getElementById("count-label"),
    q: document.getElementById("q"),
    sort: document.getElementById("sort"),
    shuffle: document.getElementById("btn-shuffle"),
    focusSearch: document.getElementById("btn-focus-search"),
  };

  const escapeHtml = (s) =>
    String(s)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");

  const planeHref = (p) => `/planes/${encodeURIComponent(p.slug)}`;

  const getChecked = (name) =>
    [...document.querySelectorAll(`input[name="${name}"]:checked`)].map(
      (el) => el.value
    );

  const getCut = () =>
    document.querySelector('input[name="cut"]:checked')?.value || "any";

  /** Prefer a single clearest goal for cards / chips. */
  const primaryGoal = (p) => {
    const tags = p.tags || [];
    if (tags.includes("distance") && tags.includes("time_aloft")) {
      return "time_aloft";
    }
    for (const key of ["distance", "time_aloft", "acrobatic", "decorative"]) {
      if (tags.includes(key)) return key;
    }
    return "distance";
  };

  function setChecks(name, values) {
    const wanted = new Set(values.filter(Boolean));
    document.querySelectorAll(`input[name="${name}"]`).forEach((el) => {
      el.checked = wanted.has(el.value);
    });
  }

  /** Apply ?tag=&diff=&cut=&q=&sort= from the URL into the hangar filters. */
  function applyQueryFilters() {
    const params = new URLSearchParams(window.location.search);
    // Also accept hash query forms like #hangar-body?tag=distance (defensive).
    const hash = window.location.hash || "";
    const hashQuery = hash.includes("?") ? hash.slice(hash.indexOf("?") + 1) : "";
    if (hashQuery) {
      new URLSearchParams(hashQuery).forEach((value, key) => {
        params.append(key, value);
      });
    }
    if (![...params.keys()].length) return false;

    const tags = params.getAll("tag");
    const diffs = params.getAll("diff");
    const cut = params.get("cut");
    const q = params.get("q");
    const sort = params.get("sort");

    if (tags.length) setChecks("tag", tags);
    if (diffs.length) setChecks("diff", diffs);
    if (cut) {
      const cutEl = document.querySelector(`input[name="cut"][value="${CSS.escape(cut)}"]`);
      if (cutEl) cutEl.checked = true;
    }
    if (q && els.q) els.q.value = q;
    if (sort && els.sort) {
      const opt = [...els.sort.options].find((o) => o.value === sort);
      if (opt) els.sort.value = sort;
    }
    return true;
  }

  function applyFilters() {
    if (!state.planes.length) return;
    const q = els.q.value.trim().toLowerCase();
    const tags = getChecked("tag");
    const diffs = getChecked("diff");
    const cut = getCut();
    const sort = els.sort.value;

    let list = state.planes.filter((p) => {
      if (
        q &&
        !p.name.toLowerCase().includes(q) &&
        !p.blurb.toLowerCase().includes(q)
      ) {
        return false;
      }
      // Empty skill/goal selection = no restriction (not "match all checked").
      if (diffs.length && !diffs.includes(p.difficulty)) return false;
      if (cut === "yes" && !p.scissors) return false;
      if (cut === "no" && p.scissors) return false;
      if (tags.length) {
        const hit = (p.tags || []).some((t) => tags.includes(t));
        if (!hit) return false;
      }
      return true;
    });

    // "featured" keeps the shuffled hangar order from planes.json (not foldnfly order).
    if (sort !== "featured") {
      list = [...list].sort((a, b) => {
        if (sort === "name") return a.name.localeCompare(b.name);
        if (sort === "difficulty") return a.difficultyLevel - b.difficultyLevel;
        if (sort === "distance") return b.distanceScore - a.distanceScore;
        if (sort === "time") return b.timeScore - a.timeScore;
        return b.popularity - a.popularity;
      });
    }

    state.filtered = list;
    els.count.textContent = window.PPW.t("count", {
      n: list.length,
      total: state.planes.length,
    });
    paintGrid();
  }

  function paintGrid() {
    if (!state.filtered.length) {
      els.grid.innerHTML = "";
      els.empty.classList.remove("hidden");
      return;
    }
    els.empty.classList.add("hidden");
    els.grid.innerHTML = state.filtered
      .map((p, i) => {
        const goal = primaryGoal(p);
        const cut = p.scissors
          ? `<span class="chip cut">${escapeHtml(window.PPW.t("needScissors"))}</span>`
          : "";
        const badge = p.badge
          ? `<span class="badge">${escapeHtml(p.badge)}</span>`
          : "";
        const fallback = escapeHtml(p.thumb.replace(".webp", ".jpg"));
        const alt = escapeHtml(
          window.PPW.t("planeAlt", { name: p.name })
        );
        return `
          <a class="plane-card" href="${planeHref(p)}" style="animation-delay:${Math.min(i, 12) * 0.03}s">
            ${badge}
            <img class="thumb" src="${escapeHtml(p.thumb)}" alt="${alt}" loading="lazy" width="300" height="300" onerror="this.onerror=null;this.src='${fallback}'" />
            <div class="body">
              <h3>${escapeHtml(p.name)}</h3>
              <div class="meta-row">
                <span class="chip goal goal-${escapeHtml(goal)}">${escapeHtml(window.PPW.tagLabel(goal))}</span>
                <span class="chip diff-${escapeHtml(p.difficulty)}">${escapeHtml(window.PPW.diffLabel(p.difficulty))}</span>
                ${cut}
              </div>
              <span class="card-cta">${escapeHtml(window.PPW.t("viewTutorial"))}</span>
            </div>
          </a>`;
      })
      .join("");
  }

  function bind() {
    ["input", "change"].forEach((evt) => {
      els.q?.addEventListener(evt, applyFilters);
      els.sort?.addEventListener(evt, applyFilters);
      document
        .querySelectorAll('input[name="tag"], input[name="diff"], input[name="cut"]')
        .forEach((el) => {
          el.addEventListener(evt, applyFilters);
        });
    });

    if (els.shuffle) {
      els.shuffle.addEventListener("click", () => {
        const pool = state.filtered.length ? state.filtered : state.planes;
        if (!pool.length) return;
        const pick = pool[Math.floor(Math.random() * pool.length)];
        location.href = planeHref(pick);
      });
    }

    if (els.focusSearch) {
      els.focusSearch.addEventListener("click", () => {
        const hangar = document.getElementById("hangar-body");
        if (hangar) hangar.scrollIntoView({ behavior: "smooth", block: "start" });
        if (els.q) {
          els.q.focus();
          els.q.select?.();
        }
      });
    }

    // Wire static lang-select if present (i18n also injects one when missing).
    document.querySelectorAll(".lang-select").forEach((select) => {
      select.addEventListener("change", (e) => {
        window.PPW.setLang(e.target.value);
      });
    });

    window.addEventListener("ppw:lang", () => {
      window.PPW.applyStatic();
      applyFilters();
    });
  }

  async function init() {
    bind();
    applyQueryFilters();
    if (els.count) els.count.textContent = window.PPW.t("loading");
    const res = await fetch("data/planes.json");
    state.planes = await res.json();
    // Re-apply after data load in case an earlier paint raced the form.
    applyQueryFilters();
    applyFilters();
  }

  init().catch((err) => {
    if (els.count) els.count.textContent = window.PPW.t("loadFail");
    console.error(err);
  });
})();
