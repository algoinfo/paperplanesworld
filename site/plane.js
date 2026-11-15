(() => {
  document.querySelectorAll(".step img").forEach((img) => {
    img.addEventListener("click", () => {
      const box = document.createElement("div");
      box.className = "lightbox";
      box.innerHTML = `<img src="${img.dataset.full || img.src}" alt="zoom" />`;
      box.addEventListener("click", () => box.remove());
      document.body.appendChild(box);
    });
  });

  function refreshDetailCopy() {
    if (!window.PPW) return;
    window.PPW.applyStatic();
    document.querySelectorAll(".chip[data-diff]").forEach((el) => {
      el.textContent = window.PPW.diffLabel(el.dataset.diff);
    });
    document.querySelectorAll(".chip[data-tag]").forEach((el) => {
      el.textContent = window.PPW.tagLabel(el.dataset.tag);
    });
    document.querySelectorAll(".chip[data-cut]").forEach((el) => {
      const need = el.dataset.cut === "1";
      el.textContent = window.PPW.t(need ? "needScissorsLong" : "noScissors");
      el.classList.toggle("cut", need);
    });
    document.querySelectorAll(".chip[data-steps]").forEach((el) => {
      el.textContent = window.PPW.t("stepsCount", { n: el.dataset.steps });
    });
    document.querySelectorAll(".step h3[data-step]").forEach((el) => {
      const n = el.dataset.step;
      el.innerHTML = `<span class="n">${n}</span>${window.PPW.t("stepLabel", { n })}`;
    });
  }

  window.addEventListener("ppw:lang", refreshDetailCopy);
  refreshDetailCopy();
})();
