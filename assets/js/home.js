document$.subscribe(() => {
  VANTA.HALO({
    el: ".hero-container",
    mouseControls: true,
    touchControls: true,
    gyroControls: false,
    minHeight: 200.00,
    minWidth: 200.00,
    baseColor: 0x0,
    backgroundColor: 0x0,
    xOffset: 0.09,
    size: 0.90
  })
})
