(() => {
  const TAG_LABEL = {
    distance: "远距",
    time_aloft: "滞空",
    acrobatic: "特技",
    decorative: "装饰",
  };

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
  };

  const escapeHtml = (s) =>
    String(s)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");

  const planeHref = (p) => `planes/${encodeURIComponent(p.slug)}.html`;

  const getChecked = (name) =>
    [...document.querySelectorAll(`input[name="${name}"]:checked`)].map(
      (el) => el.value
    );

  const getCut = () =>
    document.querySelector('input[name="cut"]:checked')?.value || "any";

  function applyFilters() {
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
      if (diffs.length && !diffs.includes(p.difficulty)) return false;
      if (cut === "yes" && !p.scissors) return false;
      if (cut === "no" && p.scissors) return false;
      if (tags.length) {
        const hit = (p.tags || []).some((t) => tags.includes(t));
        if (!hit) return false;
      }
      return true;
    });

    list = [...list].sort((a, b) => {
      if (sort === "name") return a.name.localeCompare(b.name);
      if (sort === "difficulty") return a.difficultyLevel - b.difficultyLevel;
      if (sort === "distance") return b.distanceScore - a.distanceScore;
      if (sort === "time") return b.timeScore - a.timeScore;
      return b.popularity - a.popularity;
    });

    state.filtered = list;
    els.count.textContent = `${list.length} / ${state.planes.length} 架`;
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
        const tags = (p.tags || [])
          .map((t) => `<span class="chip">${TAG_LABEL[t] || t}</span>`)
          .join("");
        const cut = p.scissors ? `<span class="chip cut">需剪刀</span>` : "";
        const badge = p.badge
          ? `<span class="badge">${escapeHtml(p.badge)}</span>`
          : "";
        const fallback = escapeHtml(p.thumb.replace(".webp", ".jpg"));
        return `
          <a class="plane-card" href="${planeHref(p)}" style="animation-delay:${Math.min(i, 12) * 0.03}s">
            ${badge}
            <img class="thumb" src="${escapeHtml(p.thumb)}" alt="${escapeHtml(p.name)} 纸飞机" loading="lazy" width="300" height="250" onerror="this.onerror=null;this.src='${fallback}'" />
            <div class="body">
              <h2>${escapeHtml(p.name)}</h2>
              <div class="meta-row">
                <span class="chip diff-${escapeHtml(p.difficulty)}">${escapeHtml(p.difficultyCn || p.difficulty)}</span>
                ${tags}${cut}
              </div>
            </div>
          </a>`;
      })
      .join("");
  }

  function bind() {
    ["input", "change"].forEach((evt) => {
      els.q.addEventListener(evt, applyFilters);
      els.sort.addEventListener(evt, applyFilters);
      document
        .querySelectorAll('input[name="tag"], input[name="diff"], input[name="cut"]')
        .forEach((el) => {
          el.addEventListener(evt, applyFilters);
        });
    });

    els.shuffle.addEventListener("click", () => {
      const pool = state.filtered.length ? state.filtered : state.planes;
      if (!pool.length) return;
      const pick = pool[Math.floor(Math.random() * pool.length)];
      location.href = planeHref(pick);
    });
  }

  async function init() {
    bind();
    const res = await fetch("data/planes.json");
    state.planes = await res.json();
    applyFilters();
  }

  init().catch((err) => {
    els.count.textContent = "加载失败";
    console.error(err);
  });
})();
