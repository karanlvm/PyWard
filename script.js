// Import GSAP and ScrollTrigger
import gsap from "gsap"
import { ScrollTrigger } from "gsap/ScrollTrigger"

// Register ScrollTrigger plugin
gsap.registerPlugin(ScrollTrigger)

// Navbar scroll effect
window.addEventListener("scroll", () => {
  const navbar = document.querySelector(".navbar")
  if (window.scrollY > 50) {
    navbar.style.background = "rgba(255, 255, 255, 0.98)"
    navbar.style.boxShadow = "0 4px 6px -1px rgb(0 0 0 / 0.1)"
  } else {
    navbar.style.background = "rgba(255, 255, 255, 0.95)"
    navbar.style.boxShadow = "none"
  }
})

// Typewriter effect
function typeWriter(element, text, speed = 100) {
  let i = 0
  element.textContent = ""

  function type() {
    if (i < text.length) {
      element.textContent += text.charAt(i)
      i++
      setTimeout(type, speed)
    }
  }

  type()
}

// Initialize typewriter when page loads
document.addEventListener("DOMContentLoaded", () => {
  const typewriterElement = document.querySelector(".typewriter")
  const text = typewriterElement.getAttribute("data-text") || "pip install pyward-cli"

  // Start typewriter effect after a short delay
  setTimeout(() => {
    typeWriter(typewriterElement, text, 80)
  }, 1000)
})

// Copy to clipboard functionality
document.addEventListener("click", (e) => {
  if (e.target.classList.contains("copy-btn")) {
    const textToCopy = e.target.getAttribute("data-copy")

    navigator.clipboard
      .writeText(textToCopy)
      .then(() => {
        const originalText = e.target.textContent
        e.target.textContent = "Copied!"
        e.target.style.background = "#10b981"
        e.target.style.borderColor = "#10b981"
        e.target.style.color = "white"

        setTimeout(() => {
          e.target.textContent = originalText
          e.target.style.background = "transparent"
          e.target.style.borderColor = "#334155"
          e.target.style.color = "#64748b"
        }, 2000)
      })
      .catch(() => {
        e.target.textContent = "Failed"
        setTimeout(() => {
          e.target.textContent = "Copy"
        }, 2000)
      })
  }
})

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener("click", function (e) {
    e.preventDefault()
    const target = document.querySelector(this.getAttribute("href"))
    if (target) {
      const offsetTop = target.offsetTop - 80 // Account for fixed navbar
      window.scrollTo({
        top: offsetTop,
        behavior: "smooth",
      })
    }
  })
})

// GSAP Animations
gsap.set(".fade-in", { opacity: 0, y: 30 })
gsap.set(".slide-in-left", { opacity: 0, x: -50 })
gsap.set(".slide-in-right", { opacity: 0, x: 50 })
gsap.set(".scale-in", { opacity: 0, scale: 0.9 })

// Hero animations
gsap
  .timeline()
  .from(".hero-badge", { opacity: 0, y: 20, duration: 0.8, delay: 0.2 })
  .from(".hero-title", { opacity: 0, y: 30, duration: 0.8 }, "-=0.6")
  .from(".hero-subtitle", { opacity: 0, y: 20, duration: 0.8 }, "-=0.6")
  .from(".typewriter-container", { opacity: 0, y: 20, duration: 0.8 }, "-=0.4")
  .from(".hero-buttons", { opacity: 0, y: 20, duration: 0.8 }, "-=0.4")
  .from(".code-window", { opacity: 0, scale: 0.9, duration: 1, ease: "back.out(1.7)" }, "-=0.6")

// Scroll-triggered animations
ScrollTrigger.batch(".feature-card", {
  onEnter: (elements) => {
    gsap.from(elements, {
      opacity: 0,
      y: 50,
      stagger: 0.2,
      duration: 0.8,
      ease: "power2.out",
    })
  },
  start: "top 80%",
})

ScrollTrigger.batch(".step", {
  onEnter: (elements) => {
    gsap.from(elements, {
      opacity: 0,
      x: -50,
      stagger: 0.3,
      duration: 0.8,
      ease: "power2.out",
    })
  },
  start: "top 80%",
})

ScrollTrigger.batch(".usage-card", {
  onEnter: (elements) => {
    gsap.from(elements, {
      opacity: 0,
      y: 30,
      stagger: 0.15,
      duration: 0.6,
      ease: "power2.out",
    })
  },
  start: "top 85%",
})

// Parallax effect for hero background
gsap.to(".hero::before", {
  yPercent: -50,
  ease: "none",
  scrollTrigger: {
    trigger: ".hero",
    start: "top bottom",
    end: "bottom top",
    scrub: true,
  },
})

// Code window 3D effect on scroll
ScrollTrigger.create({
  trigger: ".code-window",
  start: "top 80%",
  end: "bottom 20%",
  scrub: 1,
  onUpdate: (self) => {
    const rotation = self.progress * 10 - 5
    gsap.set(".code-window", {
      rotationY: rotation,
      rotationX: rotation * 0.5,
    })
  },
})

// Contribute section animation
ScrollTrigger.create({
  trigger: ".contribute-section",
  start: "top 80%",
  onEnter: () => {
    gsap
      .timeline()
      .from(".contribute-text h2", { opacity: 0, y: 30, duration: 0.8 })
      .from(".contribute-text p", { opacity: 0, y: 20, duration: 0.8 }, "-=0.6")
      .from(".contribute-stats .stat", { opacity: 0, y: 20, stagger: 0.1, duration: 0.6 }, "-=0.4")
      .from(".contribute-actions .button", { opacity: 0, x: 30, stagger: 0.1, duration: 0.6 }, "-=0.4")
  },
})

// Add hover effects to buttons
document.querySelectorAll(".button").forEach((button) => {
  button.addEventListener("mouseenter", () => {
    gsap.to(button, { scale: 1.05, duration: 0.3, ease: "power2.out" })
  })

  button.addEventListener("mouseleave", () => {
    gsap.to(button, { scale: 1, duration: 0.3, ease: "power2.out" })
  })
})

// Add floating animation to feature icons
gsap.to(".feature-icon", {
  y: -10,
  duration: 2,
  ease: "power2.inOut",
  yoyo: true,
  repeat: -1,
  stagger: 0.3,
})

// Performance optimization: Reduce animations on mobile
const isMobile = window.innerWidth < 768
if (isMobile) {
  // Disable some heavy animations on mobile
  ScrollTrigger.getAll().forEach((trigger) => {
    if (trigger.vars.scrub) {
      trigger.kill()
    }
  })
}

// Refresh ScrollTrigger on window resize
window.addEventListener("resize", () => {
  ScrollTrigger.refresh()
})

console.log("🛡️ PyWard website loaded successfully!")
