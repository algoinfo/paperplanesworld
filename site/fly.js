(function () {
  "use strict";

  const $ = (id) => document.getElementById(id);
  const state = {
    planes: [],
    selected: null,
    yaw: -0.55,
    pitch: -0.24,
    dragging: false,
    lastInput: 0,
    flight: null,
    lastResult: null,
  };

  /* ---------------- data ---------------- */

  function perf(plane) {
    const d = plane.distanceScore || 0;
    const t = plane.timeScore || 0;
    return {
      distance: d ? [Math.round(d * 0.06 * 0.85), Math.round(d * 0.06 * 1.15)] : null,
      time: t ? [Math.round(t * 0.03 * 0.85), Math.round(t * 0.03 * 1.15)] : null,
    };
  }

  function buildPicker() {
    const wrap = $("picker");
    wrap.innerHTML = "";
    state.planes.forEach((plane) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "pick-chip";
      btn.dataset.slug = plane.slug;
      btn.setAttribute("role", "option");
      btn.textContent = plane.name;
      btn.addEventListener("click", () => select(plane.slug));
      wrap.appendChild(btn);
    });
  }

  function select(slug) {
    state.selected = state.planes.find((p) => p.slug === slug) || state.planes[0];
    if (!state.selected) return;
    document.querySelectorAll(".pick-chip").forEach((chip) => {
      const on = chip.dataset.slug === state.selected.slug;
      chip.classList.toggle("is-active", on);
      chip.setAttribute("aria-selected", String(on));
    });
    const vals = perf(state.selected);
    $("stat-distance").textContent = vals.distance
      ? `${vals.distance[0]}–${vals.distance[1]} m`
      : "—";
    $("stat-time").textContent = vals.time ? `${vals.time[0]}–${vals.time[1]} s` : "—";
    $("stat-guide").href = `/planes/${encodeURIComponent(state.selected.slug)}`;
    cancelFlight();
  }

  /* ---------------- 3D model ---------------- */

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

  const modelCanvas = $("model-canvas");
  const modelCtx = modelCanvas.getContext("2d");
  const flightCanvas = $("flight-canvas");
  const flightCtx = flightCanvas.getContext("2d");
  const sizes = { model: { w: 0, h: 0 }, flight: { w: 0, h: 0 } };

  function resizeCanvas(canvas, ctx, key) {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const w = canvas.clientWidth;
    const h = canvas.clientHeight;
    canvas.width = Math.round(w * dpr);
    canvas.height = Math.round(h * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    sizes[key] = { w, h };
  }

  function normalized(v) {
    const len = Math.hypot(v[0], v[1], v[2]) || 1;
    return [v[0] / len, v[1] / len, v[2] / len];
  }

  function drawModel() {
    const { w, h } = sizes.model;
    if (!w || !h) return;
    modelCtx.clearRect(0, 0, w, h);

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

    // ground shadow
    modelCtx.fillStyle = "rgba(19,35,58,.10)";
    modelCtx.beginPath();
    modelCtx.ellipse(cx, cy + Math.min(h * 0.36, 130), scale * 0.95, scale * 0.14, 0, 0, Math.PI * 2);
    modelCtx.fill();

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
      const diffuse = Math.max(0, facing[0] * light[0] + facing[1] * light[1] + facing[2] * light[2]);
      const shade = 0.94 + 0.06 * diffuse;
      return {
        pts: pts3.map(project),
        depth: (a[2] + b[2] + c[2]) / 3,
        fill: `rgb(${face.base.map((ch) => Math.round(ch * shade)).join(",")})`,
      };
    });

    faces.sort((a, b) => b.depth - a.depth);
    faces.forEach((face) => {
      modelCtx.beginPath();
      face.pts.forEach((pt, i) => (i ? modelCtx.lineTo(pt.x, pt.y) : modelCtx.moveTo(pt.x, pt.y)));
      modelCtx.closePath();
      modelCtx.fillStyle = face.fill;
      modelCtx.fill();
      modelCtx.strokeStyle = "rgba(31,111,191,.25)";
      modelCtx.lineWidth = 1;
      modelCtx.stroke();
    });
  }

  function bindModelDrag() {
    const stage = $("model-stage");
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
      state.pitch = Math.max(-0.9, Math.min(0.9, state.pitch + (e.clientY - lastY) * 0.008));
      lastX = e.clientX;
      lastY = e.clientY;
      state.lastInput = performance.now();
    });
    const stop = (e) => {
      state.dragging = false;
      if (stage.hasPointerCapture?.(e.pointerId)) stage.releasePointerCapture(e.pointerId);
    };
    stage.addEventListener("pointerup", stop);
    stage.addEventListener("pointercancel", stop);
    stage.addEventListener("pointerleave", () => (state.dragging = false));
  }

  /* ---------------- test flight ---------------- */

  function flightMetrics() {
    const plane = state.selected;
    if (!plane) return null;
    const angle = Number($("angle").value);
    const baseD = plane.distanceScore ? plane.distanceScore * 0.06 : 4;
    const baseT = plane.timeScore ? plane.timeScore * 0.03 : 2.4;
    const penalty = 1 - 0.011 * Math.abs(angle - 8);
    return {
      distance: Math.max(2, baseD * penalty * (0.96 + Math.random() * 0.08)),
      duration: Math.max(1.4, baseT * (0.95 + Math.random() * 0.1)),
      angle,
    };
  }

  function launch() {
    if (state.flight || !state.selected) return;
    const m = flightMetrics();
    if (!m) return;
    state.flight = {
      ...m,
      started: performance.now(),
      animMs: Math.min(6000, 2400 + m.duration * 220),
      trail: [],
    };
    $("launch").disabled = true;
    $("flight-status").textContent = "";
  }

  function cancelFlight() {
    state.flight = null;
    state.lastResult = null;
    $("launch").disabled = false;
    $("out-distance").textContent = "0.0 m";
    $("out-time").textContent = "0.0 s";
    $("flight-status").textContent = "";
    drawFlight();
  }

  function resultText(distance, duration) {
    const label = window.PPW ? window.PPW.t("landed") : "Landed";
    return `${label} · ${distance.toFixed(1)} m · ${duration.toFixed(1)} s`;
  }

  function drawFlight() {
    const { w, h } = sizes.flight;
    if (!w || !h) return;
    const ctx = flightCtx;
    ctx.clearRect(0, 0, w, h);

    const groundY = h - 26;
    const startX = w * 0.07;
    const maxDistance = 30;

    // ground
    ctx.strokeStyle = "rgba(31,111,191,.28)";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(0, groundY);
    ctx.lineTo(w, groundY);
    ctx.stroke();

    // distance ticks
    ctx.fillStyle = "rgba(31,111,191,.45)";
    ctx.font = "10px system-ui, sans-serif";
    for (let m = 5; m <= maxDistance; m += 5) {
      const x = startX + (w * 0.88 * m) / maxDistance;
      ctx.beginPath();
      ctx.moveTo(x, groundY - 4);
      ctx.lineTo(x, groundY + 4);
      ctx.stroke();
      ctx.fillText(`${m} m`, x - 9, groundY + 16);
    }

    const f = state.flight;
    if (!f) {
      const d = state.lastResult ? state.lastResult.distance : 0;
      const restX = d ? startX + (w * 0.88 * Math.min(1, d / maxDistance)) : startX;
      drawGlider(ctx, restX, groundY - 16, d ? 0.02 : -0.15, 1);
      return;
    }

    const progress = Math.min(1, (performance.now() - f.started) / f.animMs);
    const travel = Math.min(1, f.distance / maxDistance);
    const endX = startX + w * 0.88 * travel;
    const x = startX + (endX - startX) * progress;
    const peak = 42 + Math.min(90, f.duration * 7) + f.angle * 1.4;
    const y = groundY - 12 - Math.sin(Math.PI * progress) * peak;
    const dy = -Math.cos(Math.PI * progress) * Math.PI * peak;
    const dx = endX - startX;
    const angle = Math.atan2(dy, dx || 1);

    f.trail.push({ x, y });
    if (f.trail.length > 90) f.trail.shift();

    ctx.strokeStyle = "rgba(31,111,191,.35)";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    f.trail.forEach((pt, i) => (i ? ctx.lineTo(pt.x, pt.y) : ctx.moveTo(pt.x, pt.y)));
    ctx.stroke();

    drawGlider(ctx, x, y, angle, 1);

    $("out-distance").textContent = `${(f.distance * progress).toFixed(1)} m`;
    $("out-time").textContent = `${(f.duration * progress).toFixed(1)} s`;

    if (progress >= 1) {
      state.lastResult = { distance: f.distance, duration: f.duration };
      $("flight-status").textContent = resultText(f.distance, f.duration);
      state.flight = null;
      $("launch").disabled = false;
    }
  }

  function drawGlider(ctx, x, y, angle, scale) {
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(angle);
    ctx.scale(scale, scale);
    ctx.beginPath();
    ctx.moveTo(14, 0);
    ctx.lineTo(-11, -7);
    ctx.lineTo(-6, 0);
    ctx.lineTo(-11, 7);
    ctx.closePath();
    ctx.fillStyle = "#ffffff";
    ctx.fill();
    ctx.strokeStyle = "rgba(19,35,58,.45)";
    ctx.lineWidth = 1.2;
    ctx.stroke();
    ctx.restore();
  }

  /* ---------------- loop ---------------- */

  function tick(now) {
    if (!state.dragging && now - state.lastInput > 2200) {
      state.yaw += 0.0045;
    }
    drawModel();
    drawFlight();
    requestAnimationFrame(tick);
  }

  function countText() {
    const zh = window.PPW && window.PPW.lang === "zh";
    return `${state.planes.length} ${zh ? "款机型" : "models"}`;
  }
  /* ---------------- boot ---------------- */

  function syncSizes() {
    resizeCanvas(modelCanvas, modelCtx, "model");
    resizeCanvas(flightCanvas, flightCtx, "flight");
  }

  async function init() {
    $("angle").addEventListener("input", (e) => {
      $("angle-out").textContent = `${e.target.value}°`;
    });
    $("launch").addEventListener("click", launch);

    window.addEventListener("resize", syncSizes);
    window.addEventListener("ppw:lang", () => {
      if (state.planes.length) $("fly-count").textContent = countText();
      if (state.lastResult) {
        $("flight-status").textContent = resultText(state.lastResult.distance, state.lastResult.duration);
      }
    });

    try {
      const res = await fetch("data/planes.json");
      if (!res.ok) throw new Error("load failed");
      state.planes = await res.json();
    } catch (err) {
      $("picker").textContent = window.PPW ? window.PPW.t("loadFail") : "Failed to load";
      return;
    }

    $("fly-count").textContent = countText();
    buildPicker();
    const params = new URLSearchParams(location.search);
    const fromQuery = params.get("plane");
    const preferred =
      (fromQuery && state.planes.find((p) => p.slug === fromQuery)) ||
      state.planes.find((p) => p.slug === "Stealth-Glider") ||
      state.planes[0];
    select(preferred.slug);
    bindModelDrag();
    syncSizes();
    cancelFlight();
    requestAnimationFrame(tick);
  }

  init();
})();
