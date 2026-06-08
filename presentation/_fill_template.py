"""Fill the bootcamp PPT template with our project content.

Keeps the template's visual design intact (master, layouts, fonts, colors,
images) and only replaces the text inside each placeholder / text-box.

Strategy:
  * Slide 1 (title): edit the existing runs in the title textbox so
    Oswald font and sizes are preserved.
  * Slides 2-8: each placeholder has a single style (taken from its
    first paragraph/run). Clear paragraphs, then rebuild with our bullet
    points using the same font/size/color so the look stays consistent.

Input:  presentation/bootcamp_template.pptx (downloaded from the
        bootcamp's Google Slides via Drive MCP)
Output: presentation/Receipt-to-Cashback.pptx
"""

from __future__ import annotations

import copy
from pathlib import Path

from pptx import Presentation
from pptx.util import Emu

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "presentation" / "bootcamp_template.pptx"
OUTPUT = ROOT / "presentation" / "Receipt-to-Cashback.pptx"


# ---------------------------------------------------------------------------
# Content per slide (matches the template's structure, in English).
# Bullets are designed to be brief — the template's slides 3/5/6 specify
# "ONLY BULLET POINTS".
# ---------------------------------------------------------------------------

PROJECT_NAME = "Receipt-to-Cashback"
YOUR_NAME = "Alex Goldbaum"

SLIDE_2_TITLE = "Receipt-to-Cashback"
SLIDE_2_BODY = [
    "A market-research data-acquisition app: users scan a receipt; we pay a "
    "flat cashback in exchange for the itemised consumption data, which we "
    "anonymise and sell in aggregate to brands and research firms.",
    "Problem solved: market research today buys slow self-reported surveys; "
    "loyalty programs see one retailer at a time. Nobody has the "
    "cross-merchant, item-level picture of what consumers actually buy. "
    "We do.",
    "Target users: consumers who want any-merchant cashback (B2C) and "
    "brands, retailers and market-research firms as data buyers (B2B).",
]

SLIDE_3_TITLE = "Stack"
SLIDE_3_BODY = [
    "Python · OOP · Pydantic — bootcamp Week 1–2",
    "pandas · matplotlib · seaborn — bootcamp Week 3–4",
    "scikit-learn KMeans · scipy Welch's t-test — bootcamp Week 4–5",
    "EasyOCR (CRAFT + CRNN) — bootcamp Week 7",
    "FAISS + multilingual sentence-transformer — bootcamp Week 8",
    "Gemini 2.5 Flash Lite + few-shot + strict Pydantic schema — bootcamp Week 9",
    "Streamlit web app (4 pages) — SELF-TAUGHT",
]

SLIDE_4_TITLE = "Features list"
SLIDE_4_BODY = [
    "Upload page: receipt photo → cashback number in ~8 seconds end-to-end",
    "OCR + LLM extractor with strict Pydantic schema and few-shot prompts",
    "Multilingual semantic matching against a 110-SKU F&B catalog (FAISS)",
    "Two-tier drift guard: scales at 10% drift, refuses cashback at 50%",
    "B2B Analytics page: K-Means user clustering + A/B-test simulation (Welch's t-test)",
    "Ethics tab inside the app + full ethics doc in the repo",
    "13 unit tests on the CashbackEngine — all passing",
    "Branch-per-feature git workflow with --no-ff merges",
]

SLIDE_5_DIFFICULTIES = [
    "Original partner-rebate business model gated cashback on most receipts → "
    "pivoted to market-research model: every priced line pays out",
    "English-only embedding rejected Indonesian item 'PKT AYAM' → switched to "
    "paraphrase-multilingual-MiniLM-L12-v2 → 100% classification",
    "End-to-end latency was 40+ seconds on first run → moved to Gemini Flash "
    "Lite + image-hash cache → ~8 seconds",
    "OCR and LLM aren't perfect — they sometimes double-count items or "
    "misread the total. Sanity check: if the sum of items disagrees with the "
    "printed total by 10%, we trust the printed total; if by 50%, we refuse "
    "the cashback and ask the user for another photo.",
]

SLIDE_5_NEXT_STEPS = [
    "Real users instead of a synthetic population",
    "Postgres warehouse for receipt records",
    "Image-level redaction of cardholder data and identifiers",
    "K-anonymity floor before any aggregated data is sold",
    "MCP 'spend search' agent (e.g. 'how much did I spend on coffee in May?')",
    "Multilingual OCR (Hebrew, Arabic) for global users",
]

SLIDE_6_VIDEO_LINK = "Live demo: https://huggingface.co/spaces/alexgl77/receipt-to-cashback"
SLIDE_6_VIDEO_LINK_2 = "Loom video (2:53): https://www.loom.com/share/b10268c4694f4a8f8cf5e7292aef7a21"

SLIDE_7_LINKS = [
    "GitHub (public repo): https://github.com/alexgl77/receipt-to-cashback",
    "Live app: https://huggingface.co/spaces/alexgl77/receipt-to-cashback",
    "Demo video (Loom, 2:53): https://www.loom.com/share/b10268c4694f4a8f8cf5e7292aef7a21",
    "Medium article: not planned",
]

SLIDE_8_JOB = [
    "CV: [REPLACE WITH YOUR CV URL]",
    "LinkedIn: https://www.linkedin.com/in/alex-goldbaum/",
]

# Replacement headers for the two free text boxes on slide 5 (the
# template ships them as "Difficulties you managed to overcome" and
# "My next step ..." — keeping them looks like the template wasn't
# customised, so we shorten them to clean section headers).
SLIDE_5_HEADER_DIFFICULTIES = "Difficulties"
SLIDE_5_HEADER_NEXT_STEPS = "Next steps (optional)"

# Slide 6's header in the template is "SHOW THE 3minutes videos + SHOW
# some part of the code" — that's a directive to the presenter, not a
# slide title. Replace with a real section title.
SLIDE_6_HEADER = "Demo · video + code"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _first_run_font(text_frame):
    """Return the font of the first non-empty run in the text frame, or None."""
    for paragraph in text_frame.paragraphs:
        for run in paragraph.runs:
            if run.text.strip():
                return run.font
    # Fall back to the first run we can find
    for paragraph in text_frame.paragraphs:
        for run in paragraph.runs:
            return run.font
    return None


def _copy_font(src_font, dst_run):
    if src_font is None:
        return
    f = dst_run.font
    if src_font.name:
        f.name = src_font.name
    if src_font.size:
        f.size = src_font.size
    if src_font.bold is not None:
        f.bold = src_font.bold
    if src_font.italic is not None:
        f.italic = src_font.italic
    try:
        if src_font.color and src_font.color.type:
            f.color.rgb = src_font.color.rgb
    except Exception:
        pass


def _clear_paragraphs(text_frame):
    """Remove all paragraphs except the first (which we'll reuse)."""
    tf = text_frame
    p0 = tf.paragraphs[0]
    # Clear runs in the first paragraph
    for run in list(p0.runs):
        run._r.getparent().remove(run._r)
    # Remove all other paragraphs
    for p in list(tf.paragraphs[1:]):
        p._p.getparent().remove(p._p)


def fill_text_frame(text_frame, lines, *, bullet=False):
    """Replace the contents of a text_frame with `lines`, preserving the
    original font/size/color of the first run.

    Each item in `lines` becomes its own paragraph. Pass `bullet=True` to
    keep paragraph defaults (the template's bullets come from layout
    formatting, so we just reuse the layout).
    """
    if not lines:
        return
    src_font = _first_run_font(text_frame)
    _clear_paragraphs(text_frame)

    p0 = text_frame.paragraphs[0]
    run0 = p0.add_run()
    run0.text = lines[0]
    _copy_font(src_font, run0)

    for line in lines[1:]:
        p = text_frame.add_paragraph()
        run = p.add_run()
        run.text = line
        _copy_font(src_font, run)


def set_title(slide, shape_index, title):
    """Slide titles are usually a single paragraph, single run."""
    tf = slide.shapes[shape_index].text_frame
    src_font = _first_run_font(tf)
    _clear_paragraphs(tf)
    run = tf.paragraphs[0].add_run()
    run.text = title
    _copy_font(src_font, run)


def replace_run_text(run, new_text):
    """Replace a run's text while keeping its formatting intact."""
    run.text = new_text


def clear_text_frame(text_frame):
    """Empty a text frame so it visually disappears, without removing the
    shape itself (removing the shape would break the template's layout).
    Used to wipe the template's 'Time of presentation : X min max'
    placeholders and the 'IMPORTANT : ...' instructions, which are
    directives to the presenter rather than slide content.
    """
    _clear_paragraphs(text_frame)
    # leave one empty paragraph with no runs


def remove_shape(shape):
    """Remove a shape from its slide entirely.

    Needed for the template's 'Time of presentation' placeholders:
    just clearing the text isn't enough — Google Slides shows them
    as 'Click to add a title' once they're empty placeholders, which
    looks like the deck wasn't finished.
    """
    sp = shape._element
    sp.getparent().remove(sp)


# ---------------------------------------------------------------------------
# Edit
# ---------------------------------------------------------------------------


prs = Presentation(TEMPLATE)
slides = list(prs.slides)
assert len(slides) >= 8, f"expected >=8 slides in template, got {len(slides)}"


# Slide 1 (title) — textbox with </MY PROJECT NAME> and </YOUR NAME>
# Note: the placeholders in the template are literally "</MY PROJECT NAME>"
# (with a forward slash) and "</YOUR NAME>" — match accordingly.
title_textbox = slides[0].shapes[4]
tf = title_textbox.text_frame
for paragraph in tf.paragraphs:
    for run in paragraph.runs:
        if "MY PROJECT NAME" in run.text:
            replace_run_text(run, PROJECT_NAME)
        elif "YOUR NAME" in run.text:
            replace_run_text(run, YOUR_NAME)


# NOTE on slide-2/3/4: shape[2] is the "Time of presentation" placeholder.
# Removing it (not just clearing) so Google Slides doesn't render
# "Click to add a title" in its slot.

# Slide 2 — Project name (title + body)
set_title(slides[1], 0, SLIDE_2_TITLE)
fill_text_frame(slides[1].shapes[1].text_frame, SLIDE_2_BODY)
remove_shape(slides[1].shapes[2])

# Slide 3 — Stack
set_title(slides[2], 0, SLIDE_3_TITLE)
fill_text_frame(slides[2].shapes[1].text_frame, SLIDE_3_BODY, bullet=True)
remove_shape(slides[2].shapes[2])

# Slide 4 — Features list
set_title(slides[3], 0, SLIDE_4_TITLE)
fill_text_frame(slides[3].shapes[1].text_frame, SLIDE_4_BODY, bullet=True)
remove_shape(slides[3].shapes[2])

# Slide 5 — Difficulties (top half) + Next steps (bottom half)
# Verified positions (inches) in the template:
#   shape[0] textbox "Difficulties..." header — top=0.20 (TOP HEADER)
#   shape[4] placeholder bullets             — top=0.82 (TOP BODY)
#   shape[2] placeholder "Time of pres."     — top=0.27 (junk, remove)
#   shape[3] textbox "My next step..."       — top=2.91 (BOTTOM HEADER)
#   shape[1] placeholder bullets             — top=3.64 (BOTTOM BODY)
#   shape[5] placeholder "Time of pres."     — top=3.40 (junk, remove)
# IMPORTANT: shapes are not in visual order; remove junk first, then
# fill, otherwise indices shift while we work.
set_title(slides[4], 0, SLIDE_5_HEADER_DIFFICULTIES)
fill_text_frame(slides[4].shapes[4].text_frame, SLIDE_5_DIFFICULTIES, bullet=True)
set_title(slides[4], 3, SLIDE_5_HEADER_NEXT_STEPS)
fill_text_frame(slides[4].shapes[1].text_frame, SLIDE_5_NEXT_STEPS, bullet=True)
# Remove junk placeholders AFTER filling (descending index so shifts don't bite)
remove_shape(slides[4].shapes[5])
remove_shape(slides[4].shapes[2])

# Slide 6 — Show video + code
# shape[0] = template directive title → replace
# shape[1] = video link placeholder → fill
# shape[2] = "Time of presentation" → remove
# shape[3] = "IMPORTANT : your PPT + the video..." directive → remove
set_title(slides[5], 0, SLIDE_6_HEADER)
fill_text_frame(
    slides[5].shapes[1].text_frame,
    [SLIDE_6_VIDEO_LINK, SLIDE_6_VIDEO_LINK_2],
)
# Remove in descending index
remove_shape(slides[5].shapes[3])
remove_shape(slides[5].shapes[2])

# Slide 7 — Links (PSTB Team Only)
set_title(slides[6], 0, "Links (For PSTB Team Only – Not for Presentation)")
fill_text_frame(slides[6].shapes[1].text_frame, SLIDE_7_LINKS, bullet=True)

# Slide 8 — Job (PSTB Team Only)
set_title(slides[7], 0, "Job (For PSTB Team Only – Not for Presentation)")
fill_text_frame(slides[7].shapes[1].text_frame, SLIDE_8_JOB, bullet=True)


prs.save(OUTPUT)
print(f"Wrote {OUTPUT}")
print(f"Slides: {len(prs.slides)}")
