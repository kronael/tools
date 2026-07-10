---
name: markdown-converter
description: Convert existing files (PDF, Office, HTML, data, images, audio, EPub, ZIP, YouTube) to Markdown via `uvx markitdown`. NOT for authoring new prose (use writing) or syncing project docs (use readme).
when_to_use: "convert to markdown, pdf to markdown, docx/pptx/xlsx to markdown, office to markdown, html to markdown, extract text from a pdf, read a pdf/docx/spreadsheet, OCR an image, transcribe audio, epub to markdown, markitdown"
user-invocable: false
---

# Markdown Converter

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
