document$.subscribe(() => {
  const hero = document.querySelector(".hero-container");
  if (!hero || !window.VANTA?.WAVES || hero.dataset.vantaInitialized === "true") {
    return;
  }

  hero.dataset.vantaInitialized = "true";
  window.VANTA.WAVES({
    el: hero,
    mouseControls: true,
    touchControls: true,
    gyroControls: false,
    minHeight: 200.0,
    minWidth: 200.0,
    scale: 1.0,
    scaleMobile: 1.0,
    color: 0x0,
    shininess: 60.0,
    waveHeight: 39.5,
    waveSpeed: 0.95,
    zoom: 0.65,
  });
});
