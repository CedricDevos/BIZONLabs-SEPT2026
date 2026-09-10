#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
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
PAPER_PREVIEWS = PAPER_LIBRARY / "previews"
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


def render_paper_library() -> str:
    files = [
        path
        for path in sorted(PAPER_LIBRARY.iterdir(), key=lambda item: item.name.lower())
        if path.is_file() and path.suffix.lower() in PAPER_TYPES
    ]
    if not files:
        return """
        <figure class="paper-card">
          <button class="paper-button" type="button" data-paper-button data-paper-src="assets/images/acs-nano-paper.png" data-paper-title="Selected publication preview">
            <img src="assets/images/acs-nano-paper.png" alt="ACS Nano publication preview" loading="lazy" />
          </button>
        </figure>
        """.strip()

    make_paper_previews(files)
    items = []
    for path in files:
        preview = PAPER_PREVIEWS / f"{path.name}.png"
        metadata = paper_metadata(path)
        title = metadata["title"]
        preview_src = "assets/images/acs-nano-paper.png"
        if preview.exists():
            preview_src = "assets/papers/previews/" + quote(preview.name)
        escaped_title = escape(title)
        escaped_journal = escape(metadata["journal"])
        items.append(
            f"""
            <figure class="paper-card">
              <button class="paper-button" type="button" data-paper-button data-paper-src="{preview_src}" data-paper-title="{escaped_title}" data-paper-journal="{escaped_journal}">
                <img src="{preview_src}" alt="{escaped_title} first page" loading="lazy" />
              </button>
            </figure>
            """.strip()
        )
    return "\n".join(items)


def make_paper_previews(files: list[Path]) -> None:
    generator = shutil.which("qlmanage")
    if generator is None:
        return
    PAPER_PREVIEWS.mkdir(parents=True, exist_ok=True)
    for path in files:
        preview = PAPER_PREVIEWS / f"{path.name}.png"
        if preview.exists() and preview.stat().st_mtime >= path.stat().st_mtime:
            continue
        subprocess.run(
            [generator, "-t", "-s", "1100", "-o", str(PAPER_PREVIEWS), str(path)],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


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
        "body": "Mechanistic models that connect process inputs to particle outcomes.",
        "keywords": ("model", "advection", "diffusion", "distribution"),
    },
    {
        "id": "process",
        "label": "Process",
        "body": "Manufacturing and mixing work that turns formulation ideas into controlled particles.",
        "keywords": ("manufactur", "mixer", "process", "precipitation", "downstream"),
    },
    {
        "id": "architecture",
        "label": "Architecture",
        "body": "Structure and morphology studies that define what the particle becomes.",
        "keywords": ("structure", "morphology", "nanoscale", "architecture"),
    },
    {
        "id": "translation",
        "label": "Translation",
        "body": "Delivery-facing work that keeps biological performance and scale in view.",
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


def paper_preview_source(path: Path) -> str:
    preview = PAPER_PREVIEWS / f"{path.name}.png"
    if preview.exists():
        return "assets/papers/previews/" + quote(preview.name)
    return "assets/images/acs-nano-paper.png"


def render_science_network() -> str:
    files = paper_files()
    if files:
        make_paper_previews(files)

    nodes = []
    papers = []
    for index, category in enumerate(SCIENCE_CATEGORIES, start=1):
        active = " is-active" if index == 1 else ""
        selected = "true" if index == 1 else "false"
        nodes.append(
            f"""
            <button class="science-orbit-node science-orbit-{category["id"]}{active}" type="button" aria-pressed="{selected}" data-science-category="{category["id"]}">
              <span>{index:02d}</span>
              <strong>{escape(category["label"])}</strong>
            </button>
            """.strip()
        )

    if files:
        for path in files:
            metadata = paper_metadata(path)
            title = metadata["title"]
            category_id = science_category_for(title)
            visible = " is-visible" if category_id == SCIENCE_CATEGORIES[0]["id"] else ""
            escaped_title = escape(title)
            escaped_journal = escape(metadata["journal"])
            papers.append(
                f"""
                <button class="science-paper{visible}" type="button" data-science-paper data-category="{category_id}" data-paper-src="{paper_preview_source(path)}" data-paper-title="{escaped_title}" data-paper-journal="{escaped_journal}">
                  <span>{escaped_journal}</span>
                  <strong>{escaped_title}</strong>
                </button>
                """.strip()
            )
    else:
        papers.append(
            """
            <button class="science-paper is-visible" type="button" data-science-paper data-category="modeling" data-paper-src="assets/images/acs-nano-paper.png" data-paper-title="Selected publication preview">
              <span>Modeling</span>
              <strong>Selected publication preview</strong>
            </button>
            """.strip()
        )

    return f"""
    <div class="science-network" data-science-network>
      <div class="science-web" data-science-web data-active-category="{SCIENCE_CATEGORIES[0]["id"]}">
        <svg class="science-web-lines" viewBox="0 0 900 560" aria-hidden="true" focusable="false">
          <path class="web-ring" d="M450 92 C615 92 748 196 748 280 C748 364 615 468 450 468 C285 468 152 364 152 280 C152 196 285 92 450 92Z" />
          <path class="web-ring web-ring-inner" d="M450 158 C562 158 653 213 653 280 C653 347 562 402 450 402 C338 402 247 347 247 280 C247 213 338 158 450 158Z" />
          <path class="web-path web-path-modeling" data-web-line="modeling" d="M450 280 C378 220 298 158 212 118" />
          <path class="web-path web-path-process" data-web-line="process" d="M450 280 C560 215 664 168 782 140" />
          <path class="web-path web-path-architecture" data-web-line="architecture" d="M450 280 C594 310 700 352 804 420" />
          <path class="web-path web-path-translation" data-web-line="translation" d="M450 280 C330 345 245 388 122 428" />
          <path class="web-branch web-branch-modeling" data-web-line="modeling" d="M212 118 C265 91 338 84 404 100" />
          <path class="web-branch web-branch-process" data-web-line="process" d="M782 140 C728 103 646 93 580 108" />
          <path class="web-branch web-branch-architecture" data-web-line="architecture" d="M804 420 C744 462 650 474 572 450" />
          <path class="web-branch web-branch-translation" data-web-line="translation" d="M122 428 C188 464 286 474 372 448" />
        </svg>
        <div class="science-hub">
          <span>Design loop</span>
          <strong>Process -> architecture -> biology</strong>
        </div>
        {"".join(nodes)}
        <div class="science-category-note" data-science-category-note>
          <span>{escape(SCIENCE_CATEGORIES[0]["label"])}</span>
          <p>{escape(SCIENCE_CATEGORIES[0]["body"])}</p>
        </div>
        <div class="science-paper-cluster" aria-live="polite">
          <p class="science-paper-panel-label">Selected papers</p>
          {"".join(papers)}
        </div>
      </div>
    </div>
    """.strip()


def render_science_areas(areas: list[str]) -> str:
    return "\n".join(
        f"""
        <div class="science-node">
          <span>{index:02d}</span>
          <p>{escape(area)}</p>
        </div>
        """.strip()
        for index, area in enumerate(areas, start=1)
    )


def render_publications(publications: list[str]) -> str:
    items = []
    for index, publication in enumerate(publications, start=1):
        if isinstance(publication, str):
            title = publication
            url = ""
        else:
            title = publication["title"]
            url = publication.get("url", "")
        text = escape(title)
        if url:
            text = f'<a href="{escape(url)}" target="_blank" rel="noreferrer">{text}</a>'
        items.append(
            f"""
            <article class="publication-item">
              <span>{index:02d}</span>
              <p>{text}</p>
            </article>
            """.strip()
        )
    return "\n".join(items)


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


def render_profile_links(profiles: list[dict]) -> str:
    return "\n".join(
        f'<a href="{escape(profile["url"])}" target="_blank" rel="noreferrer">{escape(profile["label"])}</a>'
        for profile in profiles
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
        paper_previews=render_paper_library(),
        science_areas=render_science_areas(sections["science"]["areas"]),
        science_network=render_science_network(),
        publications=render_publications(sections["science"]["publications"]),
        profile_links=render_profile_links(sections["science"].get("profiles", [])),
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
