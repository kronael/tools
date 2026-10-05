---
name: ingest
description: Ingest a local file or a URL — PDF, Office, HTML, EPub, images, audio, ZIP to Markdown via `uvx markitdown`; YouTube and most sites to transcript, audio, video or subtitles via `yt-dlp`/`ffmpeg`. NOT for authoring new prose (use writing), syncing project docs (use readme) or writing video scripts (use create).
when_to_use: "convert to markdown, pdf to markdown, docx/pptx/xlsx to markdown, office to markdown, html to markdown, extract text from a pdf, read a pdf/docx/spreadsheet, OCR an image, transcribe audio, epub to markdown, markitdown, download a youtube video, download/rip audio from a video, mp3/opus from youtube, get the transcript of a video, youtube transcript, extract subtitles, list video formats, download a playlist, save a podcast episode, yt-dlp"
user-invocable: false
---

# Ingest

Two local tools, one per source: `uvx markitdown <file>` for a file on disk,
`yt-dlp` (+ `ffmpeg`) for a URL. Both sections are adapted from
steipete/agent-scripts (credited in `../README.md`).

## File → Markdown (`markitdown`)

Turn a binary/opaque file into Markdown so it can be read or quoted. One tool:
`uvx markitdown <file>` — zero-install (PEP 723; first run caches deps, no `pip install`).

Handles: PDF, Word/PowerPoint/Excel, HTML, CSV/JSON/XML, images (EXIF + OCR),
audio (EXIF + transcription), EPub, ZIP (walks contents), YouTube URLs. Output keeps
structure — headings, tables, lists, links.

- ALWAYS reach for this instead of hand-parsing a PDF/office doc or writing a one-off
  extractor — it is already installed and structure-aware.
- From stdin the type is unknown — ALWAYS pass a hint: `-x .pdf` (extension), `-m <mime>`,
  or `-c <charset>`. A bare pipe with no hint misdetects.
- LOCAL-ONLY by default. NEVER assume the two network paths work offline: `-d`/`-e`
  (Azure Document Intelligence, for salvaging bad scans) is a PAID cloud service, and a
  YouTube URL fetches over the network. Everything else runs on the box.

## URL → transcript, audio, video (`yt-dlp`)

Pull media from a URL — YouTube and nearly every site `yt-dlp` supports. Tools: `yt-dlp`
(+ `ffmpeg` for merge/extract), both local CLIs; the fetch itself needs network.

- **Transcript** — `yt-dlp --write-auto-subs --sub-lang en --skip-download --sub-format vtt`.
  ALWAYS flatten the `.vtt` yourself: auto-caption VTT is ROLLING — each cue repeats the
  tail of the previous one, so a naive concatenation duplicates most lines. Drop the
  cue-timestamp lines and `[Music]`/`[Applause]` bracket cues, collapse consecutive
  repeats, join to a paragraph. Emit timestamps ONLY when asked.
- Human-authored subs are cleaner than auto — ALWAYS try `--write-subs` first, fall back
  to `--write-auto-subs` only when none exist.
- **Audio** — `yt-dlp -x --audio-format opus` (or mp3). **Video** — `-F` to list formats,
  then `-f <id>` and `--remux-video mp4` to repackage WITHOUT re-encoding.
- NEVER reach for a scraping library or the raw YouTube Data API — `yt-dlp` is the
  maintained path and already handles formats, playlists, and sign-in walls.
