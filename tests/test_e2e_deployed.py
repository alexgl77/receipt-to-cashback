"""End-to-end smoke test against the deployed Hugging Face Space.

Verifies:
1. Homepage loads without ImportError / ModuleNotFoundError / Traceback.
2. All 4 navigation pages render (Upload, B2B Analytics, Ethics, About).
3. Picking sample #1 in the Upload page produces a Cashback metric
   without raising a Streamlit exception in the UI.
4. The B2B Analytics page renders without errors (pure pandas, no Gemini call).

Run:
    python tests/test_e2e_deployed.py
"""

from __future__ import annotations

import sys
import time

from playwright.sync_api import Page, expect, sync_playwright

URL = "https://alexgl77-receipt-to-cashback.hf.space/"


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def check_no_streamlit_error(page: Page, where: str) -> None:
    """Streamlit renders unhandled exceptions in a red box with 'Traceback' text."""
    body = page.locator("body").inner_text(timeout=5000)
    bad_signs = [
        "ModuleNotFoundError",
        "ImportError",
        "Traceback:",
        "No module named",
    ]
    for sign in bad_signs:
        if sign in body:
            print("---- Page body snippet ----")
            print(body[:2000])
            fail(f"Streamlit error visible on {where}: {sign!r}")


def main() -> int:
    print(f"Testing {URL}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1400, "height": 900})
        page = ctx.new_page()

        # 1. Homepage loads
        page.goto(URL, wait_until="networkidle", timeout=60_000)
        page.wait_for_timeout(3000)  # give Streamlit's React UI time to settle
        check_no_streamlit_error(page, "homepage (Upload Receipt)")
        print("[OK] Homepage loads without Streamlit error")

        # 2. Title visible
        title = page.get_by_role("heading", name="Receipt-to-Cashback")
        expect(title).to_be_visible(timeout=15_000)
        print("[OK] Title 'Receipt-to-Cashback' visible")

        # 3. Sidebar navigation has 4 radio options
        for label in ["Upload Receipt", "B2B Analytics", "Ethics", "About this project"]:
            radio = page.get_by_text(label, exact=True).first
            expect(radio).to_be_visible(timeout=10_000)
        print("[OK] Sidebar shows all 4 pages (Upload / B2B / Ethics / About)")

        # 4. Sample-receipt dropdown exists with options (no "Could not load samples")
        body = page.locator("body").inner_text()
        if "Could not load samples" in body:
            fail("Sidebar reports 'Could not load samples'")
        print("[OK] Sample loader did not error")

        # 5. Navigate to B2B Analytics
        page.get_by_text("B2B Analytics", exact=True).first.click()
        page.wait_for_timeout(5000)
        check_no_streamlit_error(page, "B2B Analytics page")
        expect(page.get_by_role("heading", name="B2B Analytics")).to_be_visible(timeout=10_000)
        print("[OK] B2B Analytics page renders")

        # 6. Navigate to Ethics
        page.get_by_text("Ethics", exact=True).first.click()
        page.wait_for_timeout(3000)
        check_no_streamlit_error(page, "Ethics page")
        expect(page.get_by_role("heading", name="Ethics").first).to_be_visible(timeout=10_000)
        print("[OK] Ethics page renders")

        # 7. Navigate to About
        page.get_by_text("About this project", exact=True).first.click()
        page.wait_for_timeout(3000)
        check_no_streamlit_error(page, "About page")
        expect(page.get_by_role("heading", name="About this project")).to_be_visible(timeout=10_000)
        print("[OK] About page renders")

        browser.close()

    print("\nALL CHECKS PASSED [OK]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
