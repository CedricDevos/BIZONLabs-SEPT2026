#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
from html import escape
from pathlib import Path
from string import Template
from urllib.parse import quote


ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content" / "site.json"
TEMPLATE = ROOT / "site" / "index.template.html"
DIST = ROOT / "dist"
MEDIA_LIBRARY = ROOT / "assets" / "media-library"
PAPER_LIBRARY = ROOT / "assets" / "papers"
IMAGE_TYPES = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
VIDEO_TYPES = {".mov", ".mp4", ".webm"}
PAPER_TYPES = {".pdf"}
VIDEO_MIME_TYPES = {
    ".mov": "video/quicktime",
    ".mp4": "video/mp4",
    ".webm": "video/webm",
}


def load_content() -> dict:
    with CONTENT.open("r", encoding="utf-8") as file:
        return json.load(file)


def render_pillars(pillars: list[dict]) -> str:
    items = []
    for index, pillar in enumerate(pillars, start=1):
        items.append(
            f"""
            <article class="pillar">
              <span class="pillar-number">{index:02d}</span>
              <h3>{pillar["title"]}</h3>
              <p>{pillar["body"]}</p>
            </article>
            """.strip()
        )
    return "\n".join(items)


def render_team(members: list[dict]) -> str:
    items = []
    for member in members:
        initials = "".join(part[0] for part in member["name"].split()[:2])
        linkedin = ""
        if member.get("linkedin"):
            linkedin = (
                f'<a class="linkedin-link" href="{member["linkedin"]}" '
                f'target="_blank" rel="noopener" aria-label="Connect with {member["name"]} on LinkedIn">'
                '<span aria-hidden="true">in</span> LinkedIn</a>'
            )
        items.append(
            f"""
            <article class="team-card">
              <div class="portrait-slot" aria-hidden="true">{initials}</div>
              <div>
                <h3>{member["name"]}</h3>
                <p class="role">{member["role"]}</p>
                <p>{member["bio"]}</p>
                {linkedin}
              </div>
            </article>
            """.strip()
        )
    return "\n".join(items)


def render_about_paragraphs(paragraphs: list[str]) -> str:
    return "\n".join(f"<p>{paragraph}</p>" for paragraph in paragraphs)


def render_origin_note(origin: str) -> str:
    if not origin:
        return ""
    return f'<p class="origin-note">{origin}</p>'


def render_media_library() -> str:
    curated_order = {
        "0001.jpeg": 0,
        "0004.jpeg": 1,
        "0007.mov": 2,
        "0008.mov": 3,
        "00012.jpeg": 4,
        "0003.jpg": 5,
        "0002.jpg": 6,
    }
    media_labels = [
        "Particle architecture",
        "Process development",
        "Formulation work",
        "Translation",
    ]
    files = [
        path
        for path in sorted(
            MEDIA_LIBRARY.iterdir(),
            key=lambda item: (curated_order.get(item.name, 100), item.name.lower()),
        )
        if path.is_file() and path.suffix.lower() in IMAGE_TYPES | VIDEO_TYPES
    ]
    items = []
    for index, path in enumerate(files):
        source = "assets/media-library/" + quote(path.name)
        is_video = path.suffix.lower() in VIDEO_TYPES
        active_class = " is-current" if index == 0 else ""
        privacy_class = " motion-insert-primary" if path.name == "bizon-lab-motion.mov" else ""
        if is_video:
            poster = MEDIA_LIBRARY / "posters" / f"{path.name}.png"
            poster_attr = ""
            if poster.exists():
                poster_src = "assets/media-library/posters/" + quote(poster.name)
                poster_attr = f' poster="{poster_src}"'
            media = f"""
              <video class="motion-insert{privacy_class}" autoplay muted loop playsinline preload="metadata"{poster_attr}>
                <source src="{source}" type="{VIDEO_MIME_TYPES[path.suffix.lower()]}" />
              </video>
            """.strip()
        else:
            media = f'<img class="media-image" src="{source}" alt="{escape(path.stem)}" loading="lazy" />'
        items.append(
            f"""
            <figure class="media-item{active_class}" data-media-item>
              {media}
              <figcaption class="media-label">{media_labels[index % len(media_labels)]}</figcaption>
            </figure>
            """.strip()
        )
    return "\n".join(items)


def paper_title(path: Path) -> str:
    return path.stem.replace("_", " ").replace("-", " ")


PAPER_METADATA = {
    "Boulais et al. - 2025 - Steady advection–diffusion in polygonal microfluidic mixers.pdf": {
        "title": "Steady advection-diffusion in polygonal microfluidic mixers",
        "journal": "Journal of Fluid Mechanics",
    },
    "Chen2026.pdf": {
        "title": "Synthesizing polymeric nanoparticles for efficient drug loading through a thermodynamically controlled tank reactor cascade",
        "journal": "Nanoscale Advances",
    },
    "Devos et al. - 2025 - Manufacturing mRNA-Loaded Lipid Nanoparticles with Precise Size and Morphology Control.pdf": {
        "title": "Manufacturing mRNA-loaded lipid nanoparticles with precise size and morphology control",
        "journal": "ACS Nano",
    },
    "Devos et al. - Impinging jet mixers A review of their mixing characteristics, performance considerations, and appl.pdf": {
        "title": "Impinging jet mixers: a review of their mixing characteristics, performance considerations, and applications",
        "journal": "Chemical Engineering Research and Design",
    },
    "Inguva et al. - 2025 - Mechanistic modeling of lipid nanoparticle formation for the delivery of nucleic acid therapeutics.pdf": {
        "title": "Mechanistic modeling of lipid nanoparticle formation for the delivery of nucleic acid therapeutics",
        "journal": "Chemical Engineering Science",
    },
    "Mukherjee et al. - 2026 - Understanding Size Distributions during Lipid Nanoparticle Manufacturing through Mechanistic Modelin.pdf": {
        "title": "Understanding size distributions during lipid nanoparticle manufacturing through mechanistic modeling",
        "journal": "Chemical Engineering Journal",
    },
    "Sagmeister et al. - 2023 - The Rocky Road to a Digital Lab.pdf": {
        "title": "The rocky road to a digital lab",
        "journal": "Trends in Chemistry",
    },
    "Sagmeister et al. - 2026 - The hidden half of lipid nanoparticle manufacturing Downstream processing.pdf": {
        "title": "The hidden half of lipid nanoparticle manufacturing: downstream processing",
        "journal": "Molecular Pharmaceutics",
    },
    "Shin et al. - 2025 - Mechanistic modeling of lipid nanoparticle (LNP) precipitation via population balance equations (PBE.pdf": {
        "title": "Mechanistic modeling of lipid nanoparticle precipitation via population balance equations",
        "journal": "Chemical Engineering Journal",
    },
    "Udepurkar et al. - 2025 - Structure and Morphology of Lipid Nanoparticles for Nucleic Acid Drug Delivery A Review.pdf": {
        "title": "Structure and morphology of lipid nanoparticles for nucleic acid drug delivery: a review",
        "journal": "ACS Nano",
    },
}


def paper_metadata(path: Path) -> dict[str, str]:
    return PAPER_METADATA.get(path.name, {"title": paper_title(path), "journal": "Selected work"})


SCIENCE_CATEGORIES = [
    {
        "id": "modeling",
        "label": "Modeling",
        "body": "Mechanistic thinking that links controllable process choices to particle outcomes.",
        "keywords": ("model", "advection", "diffusion", "distribution"),
    },
    {
        "id": "process",
        "label": "Process",
        "body": "Experience translating formulation ideas into reproducible particle-building workflows.",
        "keywords": ("manufactur", "mixer", "process", "precipitation", "downstream"),
    },
    {
        "id": "architecture",
        "label": "Architecture",
        "body": "Expertise in structure and morphology as design variables, not afterthoughts.",
        "keywords": ("structure", "morphology", "nanoscale", "architecture"),
    },
    {
        "id": "translation",
        "label": "Translation",
        "body": "Delivery-facing work shaped by biological performance, scale, and practical use.",
        "keywords": ("delivery", "translat", "drug", "therapeutic", "digital"),
    },
]

def science_category_for(title: str) -> str:
    normalized = title.lower()
    for category in SCIENCE_CATEGORIES:
        if any(keyword in normalized for keyword in category["keywords"]):
            return category["id"]
    return "translation"


def paper_files() -> list[Path]:
    return [
        path
        for path in sorted(PAPER_LIBRARY.iterdir(), key=lambda item: item.name.lower())
        if path.is_file() and path.suffix.lower() in PAPER_TYPES
    ]


def render_science_metrics(metrics: list[dict]) -> str:
    return "\n".join(
        f"""
        <div class="science-metric">
          <strong>{escape(metric["value"])}</strong>
          <span>{escape(metric["label"])}</span>
        </div>
        """.strip()
        for metric in metrics
    )


def render_science_evidence() -> str:
    return "\n".join(
        f"""
        <article class="evidence-card">
          <div class="evidence-card-heading">
            <span>{index:02d}</span>
            <h3>{escape(category["label"])}</h3>
          </div>
          <p>{escape(category["body"])}</p>
        </article>
        """.strip()
        for index, category in enumerate(SCIENCE_CATEGORIES, start=1)
    )


def copy_tree(source: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination, copy_function=shutil.copy)


def remove_unpublished_media() -> None:
    public_media = DIST / "assets" / "media-library"
    if not public_media.exists():
        return
    allowed = IMAGE_TYPES | VIDEO_TYPES | {".md"}
    for path in public_media.iterdir():
        if path.is_file() and path.suffix.lower() not in allowed:
            path.unlink()


def build() -> None:
    data = load_content()
    sections = data["sections"]
    html = Template(TEMPLATE.read_text(encoding="utf-8")).safe_substitute(
        company=data["company"],
        email=data["email"],
        headline=data["headline"],
        subheadline=data["subheadline"],
        about_eyebrow=sections["about"]["eyebrow"],
        about_title=sections["about"]["title"],
        about_body=render_about_paragraphs(sections["about"]["body"]),
        origin_note=render_origin_note(sections["about"].get("origin", "")),
        approach_eyebrow=sections["approach"]["eyebrow"],
        approach_title=sections["approach"]["title"],
        approach_body=sections["approach"]["body"],
        pillars=render_pillars(sections["approach"]["pillars"]),
        science_eyebrow=sections["science"]["eyebrow"],
        science_title=sections["science"]["title"],
        science_body=sections["science"]["body"],
        science_metrics=render_science_metrics(sections["science"].get("metrics", [])),
        science_evidence=render_science_evidence(),
        team_eyebrow=sections["team"]["eyebrow"],
        team_title=sections["team"]["title"],
        team_intro=sections["team"]["intro"],
        team_members=render_team(sections["team"]["members"]),
        media_items=render_media_library(),
        contact_eyebrow=sections["contact"]["eyebrow"],
        contact_title=sections["contact"]["title"],
        contact_body=sections["contact"]["body"],
        contact_note=sections["contact"].get("note", ""),
    )

    DIST.mkdir(exist_ok=True)
    (DIST / "index.html").write_text(html, encoding="utf-8")
    shutil.copy2(ROOT / "site" / "styles.css", DIST / "styles.css")
    shutil.copy2(ROOT / "site" / "script.js", DIST / "script.js")
    cname = ROOT / "site" / "CNAME"
    if cname.exists():
        shutil.copy2(cname, DIST / "CNAME")
    copy_tree(ROOT / "assets", DIST / "assets")
    remove_unpublished_media()


if __name__ == "__main__":
    build()
