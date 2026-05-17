// Tiny offline tile viewer compatibility shim for pocket-cache demo.
// This is not Leaflet. It provides just enough behavior for the demo map page.
window.PocketMap = {
  init: function(containerId, options) {
    const el = document.getElementById(containerId);
    const state = { z: options.z || 2, x: options.x || 1, y: options.y || 1 };
    const tileSize = 256;

    function render() {
      el.innerHTML = "";
      const wrap = document.createElement("div");
      wrap.style.position = "relative";
      wrap.style.width = "100%";
      wrap.style.height = "100%";
      wrap.style.overflow = "hidden";
      wrap.style.touchAction = "manipulation";

      const cols = Math.ceil(el.clientWidth / tileSize) + 2;
      const rows = Math.ceil(el.clientHeight / tileSize) + 2;
      const startX = Math.max(0, state.x - Math.floor(cols / 2));
      const startY = Math.max(0, state.y - Math.floor(rows / 2));
      const max = Math.pow(2, state.z);

      for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
          const tx = (startX + c) % max;
          const ty = (startY + r) % max;
          const img = document.createElement("img");
          img.src = `/tiles/${state.z}/${tx}/${ty}.png`;
          img.style.position = "absolute";
          img.style.left = `${c * tileSize - 96}px`;
          img.style.top = `${r * tileSize - 96}px`;
          img.style.width = `${tileSize}px`;
          img.style.height = `${tileSize}px`;
          img.draggable = false;
          wrap.appendChild(img);
        }
      }

      const controls = document.createElement("div");
      controls.style.position = "absolute";
      controls.style.right = "12px";
      controls.style.top = "12px";
      controls.style.display = "grid";
      controls.style.gap = "8px";

      [["+", 1], ["−", -1]].forEach(([label, delta]) => {
        const btn = document.createElement("button");
        btn.textContent = label;
        btn.style.width = "44px";
        btn.style.height = "44px";
        btn.style.borderRadius = "12px";
        btn.style.border = "1px solid rgba(255,255,255,.2)";
        btn.style.background = "rgba(8,10,12,.85)";
        btn.style.color = "white";
        btn.style.font = "700 24px monospace";
        btn.onclick = () => {
          state.z = Math.max(0, Math.min(4, state.z + delta));
          state.x = Math.min(Math.pow(2, state.z) - 1, state.x);
          state.y = Math.min(Math.pow(2, state.z) - 1, state.y);
          render();
        };
        controls.appendChild(btn);
      });

      wrap.appendChild(controls);

      let start = null;
      wrap.addEventListener("pointerdown", e => { start = { x: e.clientX, y: e.clientY }; });
      wrap.addEventListener("pointerup", e => {
        if (!start) return;
        const dx = e.clientX - start.x;
        const dy = e.clientY - start.y;
        const max = Math.pow(2, state.z);
        if (Math.abs(dx) > 40) state.x = (state.x + (dx < 0 ? 1 : -1) + max) % max;
        if (Math.abs(dy) > 40) state.y = Math.max(0, Math.min(max - 1, state.y + (dy < 0 ? 1 : -1)));
        start = null;
        render();
      });

      el.appendChild(wrap);
    }

    render();
    window.addEventListener("resize", render);
  }
};
