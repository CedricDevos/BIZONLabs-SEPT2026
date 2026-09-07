# BIZON Labs Website Workflow

- The user's real website folder is the source of truth for public media:
  `/Users/cedricdevos/Documents/PostDoc_MIT_Private/Bizonwebsite/Bizonlabs-Website-Sept2026/assets/media-library`.
- Do not restore, recreate, or copy old images/videos into `assets/media-library` after the user deletes them.
- Before rebuilding or syncing, mirror the current real `assets/media-library` into the working copy exactly. Do not let stale working-copy media override the user's current media choices.
- If a HEIC file was previously converted to JPG, remember that the JPG copy is what appears on the website. If the user removes the image, remove the matching JPG copy too.
- Paper PDFs live separately in `assets/papers`; do not mix papers into the media library.
