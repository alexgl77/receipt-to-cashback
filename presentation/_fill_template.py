"""Fill the bootcamp PPT template with our project content.

Design priorities (after user feedback "demasiado fome, todo bullets,
nada conecta"):

* One idea per slide. Headlines, not paragraphs.
* Real screenshots of the deployed app as the hero element on the
  slides that need to convince the jury the thing works.
* Bullets stay only where the brief explicitly demands them
  (Stack — ONLY BULLET POINTS per the template instructions).
* Keep the template's master design (Oswald font, layouts, colors)
  so the deck still looks like a DI capstone.
"""

from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.util import Emu, Inches, Pt

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "presentation" / "bootcamp_template.pptx"
OUTPUT = ROOT / "presentation" / "Receipt-to-Cashback.pptx"
SHOTS = ROOT / "presentation" / "screenshots"


# ---------------------------------------------------------------------------
# Content
# ---------------------------------------------------------------------------

PROJECT_NAME = "Receipt-to-Cashback"
YOUR_NAME = "Alex Goldbaum"

# Slide 2 — Project name
SLIDE_2_TITLE = "Scan a receipt. Get cashback. We sell the data."
SLIDE_2_BODY_LINES = [
    "A market-research data-acquisition app.",
    "",
    "Users scan a receipt → we pay flat cashback in exchange for the "
    "itemised consumption data → we anonymise it and sell it in "
    "aggregate to brands, retailers and research firms.",
    "",
    "Solves a real gap: no one today has a cross-merchant, item-level "
    "picture of what consumers actually buy. We get it by paying the "
    "consumer directly.",
]

# Slide 3 — Stack (brief demands ONLY BULLET POINTS here)
SLIDE_3_TITLE = "Stack"
SLIDE_3_BODY = [
    "OCR + extraction — Gemini 2.5 Flash Vision (image → structured JSON, one call)",
    "Schema validation — Pydantic (strict + retry on malformed output)",
    "Vector search — FAISS + multilingual sentence-transformer",
    "Clustering & A/B — scikit-learn KMeans + scipy Welch's t-test",
    "Data wrangling — pandas, matplotlib, seaborn",
    "Web app — Streamlit (4 pages: Upload · B2B · Ethics · About)  — SELF-TAUGHT",
    "Code style — Python OOP + dataclasses + type hints (bootcamp Weeks 1–9)",
]

# Slide 4 — Features list
SLIDE_4_TITLE = "Upload → 32,000 IDR in 8 seconds."
SLIDE_4_BODY_LINES = [
    "Upload page (live demo on the right):",
    "• photo of receipt → cashback number end-to-end in ~8 s",
    "• every item classified into food / beverage / bakery / …",
    "• raw Gemini JSON visible for debugging",
    "",
    "B2B Analytics page:",
    "• A/B-test simulation of two cashback rates",
    "• K-Means user clustering with PCA projection",
    "",
    "Ethics tab — surfaced in the app, not buried in a doc.",
]

# Slide 5 — Difficulties + Next steps headers
SLIDE_5_HEADER_DIFFICULTIES = "Difficulties"
SLIDE_5_HEADER_NEXT_STEPS = "Next steps"
SLIDE_5_DIFFICULTIES = [
    "Original 'partner-rebate' model rejected most receipts → pivoted "
    "to market-research data acquisition (all priced lines pay out).",
    "English-only embedding rejected Indonesian items → multilingual "
    "sentence-transformer fixed it (100 % classification).",
    "Two-step OCR → LLM pipeline misread the grand total → replaced "
    "with single Gemini Vision multimodal call.",
]
SLIDE_5_NEXT_STEPS = [
    "Real users (replace synthetic population)",
    "Postgres warehouse + image-level PII redaction",
    "K-anonymity floor before any data sale",
    "MCP 'spend search' agent",
]

# Slide 6 — Demo
SLIDE_6_HEADER = "See it work"
SLIDE_6_LINK_LINES = [
    "Live app   →  https://huggingface.co/spaces/alexgl77/receipt-to-cashback",
    "Demo video →  https://www.loom.com/share/b10268c4694f4a8f8cf5e7292aef7a21  (2:53)",
]

# Slide 7 — PSTB Links
SLIDE_7_LINKS = [
    "GitHub (public): https://github.com/alexgl77/receipt-to-cashback",
    "Live app: https://huggingface.co/spaces/alexgl77/receipt-to-cashback",
    "Loom video (2:53): https://www.loom.com/share/b10268c4694f4a8f8cf5e7292aef7a21",
    "Medium: not planned",
]

# Slide 8 — PSTB Job
SLIDE_8_JOB = [
    "CV: [REPLACE WITH YOUR CV URL]",
    "LinkedIn: https://www.linkedin.com/in/alex-goldbaum/",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _first_run_font(text_frame):
    for paragraph in text_frame.paragraphs:
        for run in paragraph.runs:
            if run.text.strip():
                return run.font
    for paragraph in text_frame.paragraphs:
        for run in paragraph.runs:
            return run.font
    return None


def _copy_font(src_font, dst_run, size_override: int | None = None):
    if src_font is None:
        return
    f = dst_run.font
    if src_font.name:
        f.name = src_font.name
    if size_override is not None:
        f.size = Pt(size_override)
    elif src_font.size:
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
    tf = text_frame
    p0 = tf.paragraphs[0]
    for run in list(p0.runs):
        run._r.getparent().remove(run._r)
    for p in list(tf.paragraphs[1:]):
        p._p.getparent().remove(p._p)


def fill_text_frame(text_frame, lines, size_override: int | None = None):
    """Replace contents preserving font; one paragraph per line."""
    if not lines:
        return
    src_font = _first_run_font(text_frame)
    _clear_paragraphs(text_frame)
    p0 = text_frame.paragraphs[0]
    run0 = p0.add_run()
    run0.text = lines[0]
    _copy_font(src_font, run0, size_override)
    for line in lines[1:]:
        p = text_frame.add_paragraph()
        run = p.add_run()
        run.text = line
        _copy_font(src_font, run, size_override)


def set_title(slide, shape_index, title):
    tf = slide.shapes[shape_index].text_frame
    src_font = _first_run_font(tf)
    _clear_paragraphs(tf)
    run = tf.paragraphs[0].add_run()
    run.text = title
    _copy_font(src_font, run)


def replace_run_text(run, new_text):
    run.text = new_text


def remove_shape(shape):
    sp = shape._element
    sp.getparent().remove(sp)


def add_picture_right_half(slide, img_path: Path, *, top_in=1.6, height_in=4.2):
    """Insert an image on the right half of a 10x5.625" slide,
    vertically centred-ish under the title."""
    if not img_path.exists():
        return
    pic = slide.shapes.add_picture(
        str(img_path),
        Inches(5.2), Inches(top_in),
        height=Inches(height_in),
    )
    return pic


def add_picture_full_right(slide, img_path: Path):
    """Insert a tall image on the right two-thirds of the slide."""
    if not img_path.exists():
        return
    pic = slide.shapes.add_picture(
        str(img_path),
        Inches(4.8), Inches(1.3),
        height=Inches(4.0),
    )
    return pic


# ---------------------------------------------------------------------------
# Edit
# ---------------------------------------------------------------------------

prs = Presentation(TEMPLATE)
slides = list(prs.slides)
assert len(slides) >= 8

# Slide 1 — title textbox replacements
title_textbox = slides[0].shapes[4]
tf = title_textbox.text_frame
for paragraph in tf.paragraphs:
    for run in paragraph.runs:
        if "MY PROJECT NAME" in run.text:
            replace_run_text(run, PROJECT_NAME)
        elif "YOUR NAME" in run.text:
            replace_run_text(run, YOUR_NAME)


# Slide 2 — Project overview: short text on the left, screenshot on the right
set_title(slides[1], 0, SLIDE_2_TITLE)
# Resize the body placeholder so it doesn't fight the picture
body_shape = slides[1].shapes[1]
body_shape.left = Inches(0.3)
body_shape.width = Inches(4.8)
fill_text_frame(body_shape.text_frame, SLIDE_2_BODY_LINES, size_override=14)
remove_shape(slides[1].shapes[2])  # "Time of presentation"
add_picture_full_right(slides[1], SHOTS / "04_about.png")


# Slide 3 — Stack: tight bullets only (brief demands ONLY BULLET POINTS here)
set_title(slides[2], 0, SLIDE_3_TITLE)
fill_text_frame(slides[2].shapes[1].text_frame, SLIDE_3_BODY, size_override=13)
remove_shape(slides[2].shapes[2])


# Slide 4 — Features: text on the left, big screenshot of the upload result on the right
set_title(slides[3], 0, SLIDE_4_TITLE)
body4 = slides[3].shapes[1]
body4.left = Inches(0.3)
body4.width = Inches(4.5)
fill_text_frame(body4.text_frame, SLIDE_4_BODY_LINES, size_override=13)
remove_shape(slides[3].shapes[2])
add_picture_full_right(slides[3], SHOTS / "01_upload_result_right.png")


# Slide 5 — Difficulties + Next steps (two halves)
set_title(slides[4], 0, SLIDE_5_HEADER_DIFFICULTIES)
fill_text_frame(slides[4].shapes[4].text_frame, SLIDE_5_DIFFICULTIES, size_override=12)
set_title(slides[4], 3, SLIDE_5_HEADER_NEXT_STEPS)
fill_text_frame(slides[4].shapes[1].text_frame, SLIDE_5_NEXT_STEPS, size_override=12)
remove_shape(slides[4].shapes[5])
remove_shape(slides[4].shapes[2])


# Slide 6 — Demo (URLs big, B2B screenshot for context)
set_title(slides[5], 0, SLIDE_6_HEADER)
body6 = slides[5].shapes[1]
body6.left = Inches(0.3)
body6.width = Inches(4.8)
fill_text_frame(body6.text_frame, SLIDE_6_LINK_LINES, size_override=12)
remove_shape(slides[5].shapes[3])  # IMPORTANT-time placeholder
remove_shape(slides[5].shapes[2])  # Time of presentation
add_picture_full_right(slides[5], SHOTS / "02_b2b_analytics.png")


# Slide 7 — Links (PSTB Team Only)
set_title(slides[6], 0, "Links (For PSTB Team Only – Not for Presentation)")
fill_text_frame(slides[6].shapes[1].text_frame, SLIDE_7_LINKS, size_override=14)


# Slide 8 — Job (PSTB Team Only)
set_title(slides[7], 0, "Job (For PSTB Team Only – Not for Presentation)")
fill_text_frame(slides[7].shapes[1].text_frame, SLIDE_8_JOB, size_override=14)


prs.save(OUTPUT)
print(f"Wrote {OUTPUT}")
print(f"Slides: {len(prs.slides)}")
