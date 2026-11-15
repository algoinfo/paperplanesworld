(() => {
  const filters = document.querySelector(".learn-filters");
  const status = document.querySelector(".learn-filter-status");
  const countLabel = document.getElementById("l3d-count");
  const cards = [...document.querySelectorAll(".l3d-card")];
  const families = [...document.querySelectorAll(".learn-family[data-family]")];
  const jumps = [...document.querySelectorAll(".family-jump a[data-family]")];
  const canvas = document.getElementById("l3d-canvas");
  const stage = document.getElementById("l3d-stage");
  if (!filters || !cards.length || !canvas || !stage) return;

  const ctx = canvas.getContext("2d");
  const state = {
    planes: [],
    selected: null,
    activeFilter: "all",
    yaw: -0.55,
    pitch: -0.24,
    dragging: false,
    lastInput: 0,
    size: { w: 0, h: 0 },
  };

  const GEO = {
    points: {
      nose: [0, 0.06, 1.55],
      tailL: [-0.82, 0.36, -1.05],
      tailR: [0.82, 0.36, -1.05],
      tailC: [0, 0.06, -1.05],
      keel: [0, -0.5, -0.72],
    },
    faces: [
      { pts: ["nose", "tailL", "tailC"], base: [255, 255, 255] },
      { pts: ["nose", "tailC", "tailR"], base: [252, 254, 255] },
      { pts: ["nose", "keel", "tailC"], base: [226, 236, 246] },
    ],
  };

  function match(card, key) {
    if (key === "all") return true;
    return (card.getAttribute("data-keys") || "").split(/\s+/).includes(key);
  }

  function applyFilter() {
    let visible = 0;
    const familyVisible = {};
    cards.forEach((card) => {
      const ok = match(card, state.activeFilter);
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
        state.activeFilter === "all"
          ? ""
          : window.PPW.t("learnFilterStatus", {
              n: visible,
              total: cards.length,
            });
    }
  }

  function perf(plane) {
    const d = plane.distanceScore || 0;
    const t = plane.timeScore || 0;
    return {
      distance: d
        ? `${Math.round(d * 0.06 * 0.85)}–${Math.round(d * 0.06 * 1.15)} m`
        : "—",
      time: t
        ? `${Math.round(t * 0.03 * 0.85)}–${Math.round(t * 0.03 * 1.15)} s`
        : "—",
    };
  }

  function select(slug) {
    const plane =
      state.planes.find((p) => p.slug === slug) ||
      state.planes[0] ||
      null;
    state.selected = plane;
    cards.forEach((card) => {
      const on = card.dataset.slug === plane?.slug;
      card.classList.toggle("is-active", on);
      const btn = card.querySelector(".l3d-select");
      if (btn) btn.setAttribute("aria-pressed", String(on));
    });
    if (!plane) return;
    document.getElementById("l3d-name").textContent = plane.name;
    const blurb = document.getElementById("l3d-blurb");
    blurb.textContent =
      window.PPW.lang === "zh"
        ? plane.description || plane.blurb || ""
        : plane.blurb || plane.description || "";
    const vals = perf(plane);
    document.getElementById("l3d-distance").textContent = vals.distance;
    document.getElementById("l3d-time").textContent = vals.time;
    document.getElementById("l3d-guide").href = `planes/${encodeURIComponent(plane.slug)}.html`;
    document.getElementById("l3d-lab").href = `fly.html?plane=${encodeURIComponent(plane.slug)}`;
  }

  function resize() {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const w = canvas.clientWidth;
    const h = canvas.clientHeight;
    canvas.width = Math.round(w * dpr);
    canvas.height = Math.round(h * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    state.size = { w, h };
  }

  function normalized(v) {
    const len = Math.hypot(v[0], v[1], v[2]) || 1;
    return [v[0] / len, v[1] / len, v[2] / len];
  }

  function drawModel() {
    const { w, h } = state.size;
    if (!w || !h) return;
    ctx.clearRect(0, 0, w, h);
    const cx = w / 2;
    const cy = h / 2 + 8;
    const scale = Math.min(w, h) * 0.33;
    const cyaw = Math.cos(state.yaw);
    const syaw = Math.sin(state.yaw);
    const cp = Math.cos(state.pitch);
    const sp = Math.sin(state.pitch);
    const light = normalized([-0.35, 0.72, -0.6]);

    const rotate = ([x, y, z]) => {
      const x1 = x * cyaw + z * syaw;
      const z1 = -x * syaw + z * cyaw;
      const y1 = y * cp - z1 * sp;
      const z2 = y * sp + z1 * cp;
      return [x1, y1, z2];
    };
    const project = ([x, y, z]) => {
      const zoom = 1 / (1 + z * 0.17);
      return { x: cx + x * scale * zoom, y: cy - y * scale * zoom, z };
    };

    ctx.fillStyle = "rgba(19,35,58,.10)";
    ctx.beginPath();
    ctx.ellipse(cx, cy + Math.min(h * 0.36, 110), scale * 0.95, scale * 0.14, 0, 0, Math.PI * 2);
    ctx.fill();

    const faces = GEO.faces.map((face) => {
      const pts3 = face.pts.map((key) => rotate(GEO.points[key]));
      const [a, b, c] = pts3;
      const u = [b[0] - a[0], b[1] - a[1], b[2] - a[2]];
      const v = [c[0] - a[0], c[1] - a[1], c[2] - a[2]];
      const n = normalized([
        u[1] * v[2] - u[2] * v[1],
        u[2] * v[0] - u[0] * v[2],
        u[0] * v[1] - u[1] * v[0],
      ]);
      const facing = n[2] >= 0 ? n : [-n[0], -n[1], -n[2]];
      const diffuse = Math.max(
        0,
        facing[0] * light[0] + facing[1] * light[1] + facing[2] * light[2]
      );
      const shade = 0.94 + 0.06 * diffuse;
      return {
        pts: pts3.map(project),
        depth: (a[2] + b[2] + c[2]) / 3,
        fill: `rgb(${face.base.map((ch) => Math.round(ch * shade)).join(",")})`,
      };
    });

    faces.sort((a, b) => b.depth - a.depth);
    faces.forEach((face) => {
      ctx.beginPath();
      face.pts.forEach((pt, i) => (i ? ctx.lineTo(pt.x, pt.y) : ctx.moveTo(pt.x, pt.y)));
      ctx.closePath();
      ctx.fillStyle = face.fill;
      ctx.fill();
      ctx.strokeStyle = "rgba(31,111,191,.25)";
      ctx.lineWidth = 1;
      ctx.stroke();
    });
  }

  function bindDrag() {
    let lastX = 0;
    let lastY = 0;
    stage.addEventListener("pointerdown", (e) => {
      state.dragging = true;
      lastX = e.clientX;
      lastY = e.clientY;
      stage.setPointerCapture(e.pointerId);
    });
    stage.addEventListener("pointermove", (e) => {
      if (!state.dragging) return;
      state.yaw += (e.clientX - lastX) * 0.01;
      state.pitch = Math.max(
        -0.9,
        Math.min(0.9, state.pitch + (e.clientY - lastY) * 0.008)
      );
      lastX = e.clientX;
      lastY = e.clientY;
      state.lastInput = performance.now();
    });
    const stop = (e) => {
      state.dragging = false;
      if (stage.hasPointerCapture?.(e.pointerId)) {
        stage.releasePointerCapture(e.pointerId);
      }
    };
    stage.addEventListener("pointerup", stop);
    stage.addEventListener("pointercancel", stop);
  }

  function tick(now) {
    if (!state.dragging && now - state.lastInput > 2200) state.yaw += 0.0045;
    drawModel();
    requestAnimationFrame(tick);
  }

  filters.addEventListener("click", (e) => {
    const btn = e.target.closest("button[data-filter]");
    if (!btn) return;
    state.activeFilter = btn.dataset.filter || "all";
    filters.querySelectorAll("button[data-filter]").forEach((b) => {
      b.setAttribute("aria-pressed", b === btn ? "true" : "false");
    });
    applyFilter();
  });

  document.querySelector(".l3d-body")?.addEventListener("click", (e) => {
    const btn = e.target.closest(".l3d-select");
    if (!btn) return;
    select(btn.dataset.slug);
  });

  window.addEventListener("ppw:lang", () => {
    document.querySelectorAll(".lc-meta [data-steps]").forEach((el) => {
      el.textContent = window.PPW.t("stepsCount", {
        n: el.getAttribute("data-steps"),
      });
    });
    if (state.selected) select(state.selected.slug);
    applyFilter();
  });

  document.querySelectorAll(".lc-meta [data-steps]").forEach((el) => {
    el.textContent = window.PPW.t("stepsCount", {
      n: el.getAttribute("data-steps"),
    });
  });

  applyFilter();
  bindDrag();
  window.addEventListener("resize", resize);
  resize();
  requestAnimationFrame(tick);

  function planesFromDom() {
    return cards.map((card) => ({
      slug: card.dataset.slug,
      name: card.querySelector(".lc-name")?.textContent?.trim() || card.dataset.slug,
      blurb: "",
      description: "",
      distanceScore: 0,
      timeScore: 0,
    }));
  }

  function boot(planes) {
    state.planes = planes;
    const firstVisible =
      cards.find((c) => !c.classList.contains("is-filtered-out"))?.dataset.slug ||
      planes[0]?.slug;
    select(firstVisible);
  }

  fetch("data/planes.json")
    .then((r) => {
      if (!r.ok) throw new Error("load failed");
      return r.json();
    })
    .then(boot)
    .catch(() => {
      boot(planesFromDom());
    });
})();
