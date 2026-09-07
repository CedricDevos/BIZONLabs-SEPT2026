const header = document.querySelector("[data-header]");
const canvas = document.querySelector("[data-particle-canvas]");
const progress = document.querySelector("[data-page-progress]");
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

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

document.querySelectorAll("[data-reveal], .pillar, .team-card").forEach((element) => {
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
  { threshold: 0.16, rootMargin: "0px 0px -8% 0px" }
);

document.querySelectorAll("[data-reveal]").forEach((element) => {
  revealObserver.observe(element);
});

const mediaItems = Array.from(document.querySelectorAll("[data-media-item]"));
const mediaGallery = document.querySelector("[data-media-gallery]");
const mediaNext = document.querySelector("[data-media-next]");
const mediaPrev = document.querySelector("[data-media-prev]");
const paperGallery = document.querySelector("[data-paper-gallery]");
let activeMedia = 0;
let mediaTimer = null;
let paperTimer = null;

const scrollMediaToActive = (behavior = "smooth") => {
  if (!mediaItems[activeMedia]) return;
  mediaItems[activeMedia].scrollIntoView({
    behavior,
    block: "nearest",
    inline: "start",
  });
};

const syncMedia = (behavior = "smooth") => {
  mediaItems.forEach((item, index) => {
    const offset = (index - activeMedia + mediaItems.length) % mediaItems.length;
    const isCurrent = offset === 0;
    const isNext = offset === 1;
    const isThird = offset === 2;
    item.classList.toggle("is-current", isCurrent);
    item.classList.toggle("is-next", isNext);
    item.classList.toggle("is-third", isThird);
    item.querySelectorAll("video").forEach((video) => {
      if ((isCurrent || isNext || isThird) && !reduceMotion.matches) {
        video.play().catch(() => {});
      } else {
        video.pause();
      }
    });
  });
  scrollMediaToActive(behavior);
};

mediaItems.forEach((item) => {
  item.querySelectorAll("video").forEach((video) => {
    video.addEventListener("error", () => {
      item.classList.add("has-video-error");
    });
  });
});

if (mediaItems.length > 0) {
  syncMedia("auto");
}

const restartMediaTimer = () => {
  if (mediaTimer) {
    window.clearInterval(mediaTimer);
  }
  if (mediaItems.length <= 1 || reduceMotion.matches) return;
  mediaTimer = window.setInterval(() => {
    activeMedia = (activeMedia + 1) % mediaItems.length;
    syncMedia();
  }, 6200);
};

if (mediaItems.length > 1 && mediaNext) {
  mediaNext.addEventListener("click", () => {
    activeMedia = (activeMedia + 1) % mediaItems.length;
    syncMedia();
    restartMediaTimer();
  });
}

if (mediaItems.length > 1 && mediaPrev) {
  mediaPrev.addEventListener("click", () => {
    activeMedia = (activeMedia - 1 + mediaItems.length) % mediaItems.length;
    syncMedia();
    restartMediaTimer();
  });
}

restartMediaTimer();

if (mediaGallery) {
  mediaGallery.addEventListener("pointerenter", () => {
    if (mediaTimer) {
      window.clearInterval(mediaTimer);
    }
  });
  mediaGallery.addEventListener("pointerleave", restartMediaTimer);
}

if (paperGallery && !reduceMotion.matches) {
  const paperCards = Array.from(paperGallery.querySelectorAll(".paper-card"));
  let activePaper = 0;
  const startPaperTimer = () => {
    if (paperTimer) {
      window.clearInterval(paperTimer);
    }
    paperTimer = window.setInterval(() => {
      activePaper = (activePaper + 1) % paperCards.length;
      paperCards[activePaper].scrollIntoView({
        behavior: "smooth",
        block: "nearest",
        inline: "start",
      });
    }, 6800);
  };
  if (paperCards.length > 1) {
    startPaperTimer();
    paperGallery.addEventListener("pointerenter", () => window.clearInterval(paperTimer));
    paperGallery.addEventListener("pointerleave", startPaperTimer);
  }
}

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
