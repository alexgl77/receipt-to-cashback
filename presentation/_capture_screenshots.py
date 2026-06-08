"""Capture screenshots of the deployed app for the PPT.

Visits the live HF Space, drives the UI through each page, and saves
PNGs into presentation/screenshots/ ready to be embedded in the deck.
"""

from __future__ import annotations

import time
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

URL = "https://alexgl77-receipt-to-cashback.hf.space/"
OUT = Path(__file__).resolve().parent / "screenshots"
OUT.mkdir(exist_ok=True)


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            viewport={"width": 1600, "height": 1000},
            device_scale_factor=2,  # higher DPI screenshots
        )
        page = ctx.new_page()

        page.goto(URL, wait_until="networkidle", timeout=60_000)
        page.wait_for_timeout(4000)

        # --- 1. Upload page with sample #1 result ---
        comboboxes = page.get_by_role("combobox")
        sample_select = comboboxes.first
        expect(sample_select).to_be_visible(timeout=15_000)
        sample_select.click()
        page.wait_for_timeout(1500)
        page.get_by_text("CORD sample #1", exact=True).first.click()
        print("Selected sample #1, waiting for pipeline...")

        # Wait for the cashback number to appear
        deadline = time.time() + 120
        while time.time() < deadline:
            body = page.locator("body").inner_text()
            if "Cashback (strategy" in body and "Line-by-line breakdown" in body:
                break
            page.wait_for_timeout(2000)
        page.wait_for_timeout(3000)  # let charts settle

        page.screenshot(path=str(OUT / "01_upload_result.png"), full_page=True)
        print(f"saved {OUT / '01_upload_result.png'}")

        # --- 2. B2B Analytics ---
        page.get_by_text("B2B Analytics", exact=True).first.click()
        page.wait_for_timeout(7000)  # KMeans + chart render
        page.screenshot(path=str(OUT / "02_b2b_analytics.png"), full_page=True)
        print(f"saved {OUT / '02_b2b_analytics.png'}")

        # --- 3. Ethics ---
        page.get_by_text("Ethics", exact=True).first.click()
        page.wait_for_timeout(3000)
        page.screenshot(path=str(OUT / "03_ethics.png"), full_page=True)
        print(f"saved {OUT / '03_ethics.png'}")

        # --- 4. About ---
        page.get_by_text("About this project", exact=True).first.click()
        page.wait_for_timeout(3000)
        page.screenshot(path=str(OUT / "04_about.png"), full_page=True)
        print(f"saved {OUT / '04_about.png'}")

        browser.close()

    # Also crop tighter versions of the upload result (just the result panel)
    # for use as a slide hero image. PIL is already in the venv.
    from PIL import Image

    full = Image.open(OUT / "01_upload_result.png")
    w, h = full.size
    # Crop the right half (result panel + table)
    right = full.crop((w // 2, 0, w, min(h, 1600)))
    right.save(OUT / "01_upload_result_right.png")
    print(f"saved {OUT / '01_upload_result_right.png'}  size={right.size}")

    print("\nDone.")


if __name__ == "__main__":
    main()
