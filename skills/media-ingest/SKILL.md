---
name: media-ingest
description: Ingest media from a URL (YouTube + most sites) with `yt-dlp`/`ffmpeg` — transcript, audio, video, subtitles, formats. NOT for converting a local file to Markdown (use markdown-converter) or writing video scripts (use create).
when_to_use: "download a youtube video, download/rip audio from a video, mp3/opus from youtube, get the transcript of a video, youtube transcript, extract subtitles, list video formats, download a playlist, save a podcast episode, yt-dlp"
user-invocable: false
---

# Media Ingest

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
