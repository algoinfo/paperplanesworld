(() => {
  document.querySelectorAll(".step img").forEach((img) => {
    img.addEventListener("click", () => {
      const box = document.createElement("div");
      box.className = "lightbox";
      box.innerHTML = `<img src="${img.dataset.full || img.src}" alt="放大图" />`;
      box.addEventListener("click", () => box.remove());
      document.body.appendChild(box);
    });
  });
})();
