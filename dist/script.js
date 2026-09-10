const header = document.querySelector("[data-header]");
const canvas = document.querySelector("[data-particle-canvas]");
const progress = document.querySelector("[data-page-progress]");
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

document.querySelectorAll("[data-reveal], .pillar, .team-card, .science-metric").forEach((element) => {
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

const mediaItems = Array.from(document.querySelectorAll("[data-media-item]"));
const mediaGallery = document.querySelector("[data-media-gallery]");
const mediaNext = document.querySelector("[data-media-next]");
const mediaPrev = document.querySelector("[data-media-prev]");
let activeMedia = 0;

const scrollItemInTrack = (track, item, behavior = "smooth") => {
  if (!track || !item) return;
  const left = item.offsetLeft - track.offsetLeft;
  track.scrollTo({ left, behavior });
};

const scrollMediaToActive = (behavior = "smooth") => {
  if (!mediaItems[activeMedia]) return;
  scrollItemInTrack(mediaGallery, mediaItems[activeMedia], behavior);
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
      if (!reduceMotion.matches) {
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

if (mediaItems.length > 1 && mediaNext) {
  mediaNext.addEventListener("click", () => {
    activeMedia = (activeMedia + 1) % mediaItems.length;
    syncMedia();
  });
}

if (mediaItems.length > 1 && mediaPrev) {
  mediaPrev.addEventListener("click", () => {
    activeMedia = (activeMedia - 1 + mediaItems.length) % mediaItems.length;
    syncMedia();
  });
}

const paperGallery = document.querySelector("[data-paper-gallery]");
const paperItems = Array.from(document.querySelectorAll(".paper-card"));
const paperModal = document.querySelector("[data-paper-modal]");
const paperModalImage = document.querySelector("[data-paper-modal-image]");
const paperModalTitle = document.querySelector("[data-paper-modal-title]");
const paperModalCloseButtons = document.querySelectorAll("[data-paper-close]");
const scienceOpen = document.querySelector("[data-science-open]");
const scienceModal = document.querySelector("[data-science-modal]");
const scienceModalCloseButtons = document.querySelectorAll("[data-science-close]");
const scienceCategoryButtons = Array.from(document.querySelectorAll("[data-science-category]"));
const sciencePapers = Array.from(document.querySelectorAll("[data-science-paper]"));
const scienceWeb = document.querySelector("[data-science-web]");
const scienceCategoryNote = document.querySelector("[data-science-category-note]");
let activePaper = 0;
let paperScrollTimer = null;

const scienceNotes = {
  modeling: {
    label: "Modeling",
    body: "Mechanistic models that connect process inputs to particle outcomes.",
  },
  process: {
    label: "Process",
    body: "Manufacturing and mixing work that turns formulation ideas into controlled particles.",
  },
  architecture: {
    label: "Architecture",
    body: "Structure and morphology studies that define what the particle becomes.",
  },
  translation: {
    label: "Translation",
    body: "Delivery-facing work that keeps biological performance and scale in view.",
  },
};

const syncPapers = () => {
  paperItems.forEach((item, index) => {
    const offset = Math.abs(index - activePaper);
    item.classList.toggle("is-current", index === activePaper);
    item.classList.toggle("is-adjacent", offset === 1);
  });
};

const updateActivePaperFromScroll = () => {
  if (!paperGallery || paperItems.length === 0) return;
  const galleryCenter = paperGallery.scrollLeft + paperGallery.clientWidth / 2;
  activePaper = paperItems.reduce((closestIndex, item, index) => {
    const itemCenter = item.offsetLeft - paperGallery.offsetLeft + item.offsetWidth / 2;
    const closest = paperItems[closestIndex];
    const closestCenter = closest.offsetLeft - paperGallery.offsetLeft + closest.offsetWidth / 2;
    return Math.abs(itemCenter - galleryCenter) < Math.abs(closestCenter - galleryCenter)
      ? index
      : closestIndex;
  }, activePaper);
  syncPapers();
};

const openPaperPreview = (source, title = "Selected publication") => {
  if (!source || !paperModal || !paperModalImage || !paperModalTitle) return;
  if (!source) return;
  paperModalImage.src = source;
  paperModalImage.alt = `${title} first page`;
  paperModalTitle.textContent = title;
  paperModal.hidden = false;
  document.body.classList.add("has-open-modal");
};

const openPaperModal = (item) => {
  const button = item.querySelector("[data-paper-button]");
  if (!button) return;
  openPaperPreview(button.dataset.paperSrc, button.dataset.paperTitle || "Selected publication");
};

const closePaperModal = () => {
  if (!paperModal || !paperModalImage) return;
  paperModal.hidden = true;
  paperModalImage.removeAttribute("src");
  if (!scienceModal || scienceModal.hidden) {
    document.body.classList.remove("has-open-modal");
  }
};

const setScienceCategory = (category) => {
  if (!category) return;
  scienceWeb?.setAttribute("data-active-category", category);
  scienceCategoryButtons.forEach((button) => {
    const isActive = button.dataset.scienceCategory === category;
    button.classList.toggle("is-active", isActive);
    button.setAttribute("aria-selected", isActive ? "true" : "false");
  });
  sciencePapers.forEach((paper) => {
    paper.classList.toggle("is-visible", paper.dataset.category === category);
  });
  const note = scienceNotes[category];
  if (scienceCategoryNote && note) {
    scienceCategoryNote.querySelector("span").textContent = note.label;
    scienceCategoryNote.querySelector("p").textContent = note.body;
  }
};

const openScienceModal = () => {
  if (!scienceModal) return;
  scienceModal.hidden = false;
  document.body.classList.add("has-open-modal");
  setScienceCategory(scienceCategoryButtons.find((button) => button.classList.contains("is-active"))?.dataset.scienceCategory || "modeling");
};

const closeScienceModal = () => {
  if (!scienceModal) return;
  scienceModal.hidden = true;
  document.body.classList.remove("has-open-modal");
};

paperItems.forEach((item, index) => {
  item.addEventListener("click", () => {
    activePaper = index;
    syncPapers();
    scrollItemInTrack(paperGallery, item);
    openPaperModal(item);
  });
});

if (paperItems.length > 0) {
  syncPapers();
}

paperGallery?.addEventListener(
  "scroll",
  () => {
    window.clearTimeout(paperScrollTimer);
    paperScrollTimer = window.setTimeout(updateActivePaperFromScroll, 110);
  },
  { passive: true }
);

paperModalCloseButtons.forEach((button) => {
  button.addEventListener("click", closePaperModal);
});

scienceOpen?.addEventListener("click", openScienceModal);

scienceCategoryButtons.forEach((button) => {
  button.addEventListener("click", () => setScienceCategory(button.dataset.scienceCategory));
});

sciencePapers.forEach((button) => {
  button.addEventListener("click", () => {
    openPaperPreview(button.dataset.paperSrc, button.dataset.paperTitle || "Selected publication");
  });
});

scienceModalCloseButtons.forEach((button) => {
  button.addEventListener("click", closeScienceModal);
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && paperModal && !paperModal.hidden) {
    closePaperModal();
  }
  if (event.key === "Escape" && scienceModal && !scienceModal.hidden) {
    closeScienceModal();
  }
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
