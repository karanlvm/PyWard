document.addEventListener("DOMContentLoaded", () => {
  gsap.to(".feature", {
    duration: 1.2,
    y: 0,
    opacity: 1,
    stagger: 0.3,
    ease: "power2.out"
  });
});
