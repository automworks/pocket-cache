const PocketMap = {
  init(elementId, { z, x, y }) {
    const n = Math.pow(2, z);
    const lon = (x + 0.5) / n * 360 - 180;
    const latRad = Math.atan(Math.sinh(Math.PI * (1 - 2 * (y + 0.5) / n)));
    const lat = latRad * 180 / Math.PI;

    const map = L.map(elementId, {
      center: [lat, lon],
      zoom: z,
      minZoom: 0,
      maxZoom: 4,
    });

    L.tileLayer("/tiles/{z}/{x}/{y}.png", {
      minZoom: 0,
      maxZoom: 4,
      tileSize: 256,
      attribution: "pocket-cache offline tiles",
    }).addTo(map);
  },
};

window.addEventListener("load", () => {
  PocketMap.init("map", { z: 2, x: 1, y: 1 });
});
