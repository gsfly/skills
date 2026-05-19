# Troubleshooting

## Live Preview Shows Empty / No Slides Found

**Symptom**: `http://localhost:5050` opens but shows no slides, or `/api/slides` returns `{"slides":[]}`.

**Root causes** and fixes:

1. **Port conflict — multiple servers on 5050 (most common on Windows)**

   On Windows, multiple Flask processes can bind to the same port via `SO_REUSEADDR`, but only the first one receives requests. Newer servers appear to start but silently fail to serve.

   **Fix**:
   ```powershell
   # Step 1: Check what's listening on 5050
   netstat -ano | Select-String ":5050.*LISTENING"

   # Step 2: Kill ALL processes found (both Flask servers and anything else)
   taskkill /PID <PID1> /F
   taskkill /PID <PID2> /F
   # ... kill every LISTENING PID

   # Step 3: Verify port is now free
   netstat -ano | Select-String ":5050.*LISTENING"
   # Expected: no output

   # Step 4: Restart the server
   python ${SKILL_DIR}/scripts/svg_editor/server.py <project_path> --live
   ```

2. **Server started without `--live` flag** — the server exits immediately when `svg_output/` is empty.

   **Fix**: Always use `--live` when starting for Step 6 auto-startup. Plain mode (no `--live`) is only for post-export annotation editing (live-preview.md Step 1).

3. **SVG files have encoding issues** — if the glob returns files but they fail to parse, run:
   ```powershell
   python -c "open(r'<project_path>\svg_output\*.svg','r',encoding='utf-8').read(); print('UTF-8 OK')"
   ```

4. **Wrong project path** — verify the server was started with the correct `<project_path>` (the one containing `svg_output/`).

## SVG Files Keep Getting Regenerated — How to Stop the Loop

**Symptom**: After running the quality checker, you keep regenerating all SVG files repeatedly.

**Root causes** (and fixes):

1. **Terminal encoding misread as file corruption** → See "Quality Checker Shows Garbled Characters" above. Verify files are intact before regenerating anything.

2. **Errors found on some pages but you regenerate everything** → Run the per-page quality check to identify exactly which page has the error. Fix only that page.

3. **Image path mismatch** → See "Image File Not Found Error" above. Fix the `href` in the SVG, do not regenerate.

4. **No state tracking** → Before generating, note which pages are already done (`[OK]`). Only regenerate pages that are missing or have errors.

**Correct pattern**:
```
1. Write page 1 → per-page check → [OK] → next
2. Write page 2 → per-page check → [ERROR: bad color] → fix page 2 → per-page check → [OK] → next
3. ... all pages done
4. Full deck check → [OK] → done
```

**Wrong pattern**:
```
1. Write all pages
2. Run full-deck check → find errors
3. Delete ALL SVGs and regenerate everything ← this is the loop
```

## Image File Not Found Error

**Cause**: The `<image href="...">` in the SVG does not match the actual filename on disk.

**Steps to diagnose**:
1. List actual files in `images/` directory:
```bash
ls <project_path>/images/
```
2. Check `images/image_manifest.json` for the authoritative filename (created by `import-sources`):
```bash
cat <project_path>/images/image_manifest.json
```
3. Compare the `href` value in the SVG with the actual filename.

**Common filename patterns**:
| Source | Typical filename |
|---|---|
| DOCX extracted images | `word_media__image_001.png` (double underscore) |
| PDF extracted | `image_001.png` |
| User renamed | `image1.png`, `video_001.png`, etc. |
| AI-generated | Whatever was saved by `image_gen.py` |

**Fix**: update the `href` in the SVG to match the exact filename from the `images/` directory. Do NOT rename files to match the SVG — update the SVG.

## Quality Checker Shows Garbled Characters on Windows

This is a **terminal encoding display issue**, not a file corruption issue. The SVG files themselves are written in UTF-8 and are intact.

**How to distinguish file corruption from terminal issue:**

| Symptom | Cause | Action |
|---|---|---|
| Quality checker output is garbled but checker returns `[OK]` | Terminal encoding only | No action needed — SVG is fine |
| Checker returns `[ERROR]` | Real file issue | Fix the reported error |
| Checker crashes with encoding error | Real file issue | Fix the file |

**Quick verification** — run this to confirm the SVG is intact:

```bash
python -c "open('<project_path>/svg_output/<file>.svg','r',encoding='utf-8').read()" && echo "File is valid UTF-8"
```

**Fix terminal output** (optional — for readability only):

```powershell
# Recommended: redirect output to file with explicit encoding
python ${SKILL_DIR}/scripts/svg_quality_checker.py <project_path> 2>&1 | Out-File -Encoding utf8 report.txt
# Then read report.txt in the editor
```

Do NOT regenerate SVG files because the terminal shows garbled output — this wastes time and produces no quality improvement.

## Validation Failed

1. Run:

```bash
python scripts/project_manager.py validate <project_path>
```

2. Fix missing files or invalid directories reported by the validator.
3. Re-run validation before post-processing or export.

## SVG Preview Looks Wrong

1. Check the file path and filename.
2. Confirm naming conventions are consistent.
3. Preview via a local server if browser file loading is inconsistent:

```bash
python -m http.server --directory <svg_output_path> 8000
```

## Speaker Notes Do Not Split

Check `total.md`:
- headings must start with `# `
- heading text must match SVG filenames
- sections must be separated by `---`

Then rerun:

```bash
python scripts/total_md_split.py <project_path>
```

## PPT Export Quality Issues

Preferred sequence:

```bash
python scripts/total_md_split.py <project_path>
python scripts/finalize_svg.py <project_path>
python scripts/svg_to_pptx.py <project_path>
```

Do not export directly from `svg_output/` when `svg_final/` exists.

## Recorded Narration Missing

1. Generate audio after `total_md_split.py`, so filenames in `audio/` can match split `notes/*.md` files.
2. Export with the project-relative audio directory:

```bash
python scripts/notes_to_audio.py <project_path> --voice zh-CN-XiaoxiaoNeural
python scripts/svg_to_pptx.py <project_path> --recorded-narration audio
```

`--recorded-narration` prepares PowerPoint recorded timings and narrations. If it fails, check:
- every slide has a matching `m4a`, `mp3`, or `wav` file in `audio/`
- `ffprobe` is installed and can read each audio duration
- the deck is not using `--animation-trigger on-click`

Use `--narration-audio-dir audio` only when you intentionally want lower-level, partial audio embedding instead of PowerPoint recorded timings.

## Dependency Checklist

Most tools use the standard library. Install extra dependencies only when needed:

```bash
pip install -r requirements.txt
```

Important optional packages:
- `python-pptx` for PPTX export
- `edge-tts` for `notes_to_audio.py` recorded narration audio
- `Pillow` for image utilities
- `numpy` for watermark removal
- `PyMuPDF` for PDF conversion
- `google-genai` / `openai` for image generation backends
