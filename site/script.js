const header = document.querySelector("[data-header]");
const canvas = document.querySelector("[data-particle-canvas]");
const progress = document.querySelector("[data-page-progress]");
const hero = document.querySelector(".hero");
const heroVideo = document.querySelector("[data-hero-video]");
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

if ("scrollRestoration" in window.history) {
  window.history.scrollRestoration = "manual";
}

const updateHeader = () => {
  header?.classList.toggle("is-scrolled", window.scrollY > 24);
};

const updateProgress = () => {
  if (!progress) return;
  const scrollable = document.documentElement.scrollHeight - window.innerHeight;
  const amount = scrollable > 0 ? window.scrollY / scrollable : 0;
  progress.style.transform = `scaleX(${Math.min(1, Math.max(0, amount))})`;
};

updateHeader();
updateProgress();
window.addEventListener("scroll", updateHeader, { passive: true });
window.addEventListener("scroll", updateProgress, { passive: true });

if (hero && heroVideo && !reduceMotion.matches) {
  heroVideo.addEventListener("ended", () => {
    hero.classList.add("is-complete");
    heroVideo.pause();
    heroVideo.currentTime = 0;
  });
}

document.querySelectorAll("nav a[href^='#']").forEach((link) => {
  const target = document.querySelector(link.getAttribute("href"));
  if (!target) return;
  const observer = new IntersectionObserver(
    ([entry]) => {
      link.classList.toggle("is-active", entry.isIntersecting);
    },
    { rootMargin: "-35% 0px -55% 0px" }
  );
  observer.observe(target);
});

document.querySelectorAll("[data-reveal], .pillar, .team-card, .science-metric, .news-item").forEach((element) => {
  element.setAttribute("data-reveal", "");
});

const revealObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        revealObserver.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.12, rootMargin: "0px 0px -6% 0px" }
);

document.querySelectorAll("[data-reveal]").forEach((element) => {
  revealObserver.observe(element);
});

if (canvas) {
  const context = canvas.getContext("2d");
  let width = 0;
  let height = 0;
  let particles = [];
  let frame = null;

  const resize = () => {
    const ratio = Math.min(window.devicePixelRatio || 1, 2);
    width = canvas.clientWidth;
    height = canvas.clientHeight;
    canvas.width = width * ratio;
    canvas.height = height * ratio;
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    const count = Math.max(30, Math.round((width * height) / 38000));
    particles = Array.from({ length: count }, (_, index) => ({
      x: Math.random() * width,
      y: Math.random() * height,
      r: index % 8 === 0 ? 1.8 : 0.9,
      vx: (Math.random() - 0.5) * 0.055,
      vy: (Math.random() - 0.5) * 0.055,
      tone: Math.random() > 0.72 ? "124, 112, 235" : "255, 255, 255",
    }));
  };

  const draw = () => {
    context.clearRect(0, 0, width, height);
    particles.forEach((particle, index) => {
      particle.x += particle.vx;
      particle.y += particle.vy;
      if (particle.x < -10) particle.x = width + 10;
      if (particle.x > width + 10) particle.x = -10;
      if (particle.y < -10) particle.y = height + 10;
      if (particle.y > height + 10) particle.y = -10;

      context.beginPath();
      context.arc(particle.x, particle.y, particle.r, 0, Math.PI * 2);
      context.fillStyle = `rgba(${particle.tone}, 0.24)`;
      context.fill();

      for (let other = index + 1; other < particles.length; other += 1) {
        const neighbor = particles[other];
        const dx = particle.x - neighbor.x;
        const dy = particle.y - neighbor.y;
        const distance = Math.hypot(dx, dy);
        if (distance < 104) {
          context.beginPath();
          context.moveTo(particle.x, particle.y);
          context.lineTo(neighbor.x, neighbor.y);
          context.strokeStyle = `rgba(124, 112, 235, ${0.04 * (1 - distance / 104)})`;
          context.lineWidth = 1;
          context.stroke();
        }
      }
    });
    frame = requestAnimationFrame(draw);
  };

  resize();
  if (!reduceMotion.matches) {
    draw();
  }
  window.addEventListener("resize", resize, { passive: true });
}
