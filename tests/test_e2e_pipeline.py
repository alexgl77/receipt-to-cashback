"""Deep end-to-end test: run a real receipt through the deployed pipeline.

Picks sample #1 from the sidebar, waits up to 90 seconds for the
Gemini Vision call + FAISS + CashbackEngine, and asserts that:
1. No Streamlit traceback was rendered
2. A 'Cashback' metric appeared on screen
3. A line-by-line breakdown table appeared
"""

from __future__ import annotations

import sys
import time

from playwright.sync_api import Page, expect, sync_playwright

URL = "https://alexgl77-receipt-to-cashback.hf.space/"


def fail(msg: str, page: Page | None = None) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    if page is not None:
        try:
            snippet = page.locator("body").inner_text(timeout=2000)[:2000]
            print("---- body snippet ----", file=sys.stderr)
            print(snippet, file=sys.stderr)
        except Exception:
            pass
    sys.exit(1)


def main() -> int:
    print(f"Testing pipeline on {URL}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1600, "height": 1000})
        page = ctx.new_page()

        page.goto(URL, wait_until="networkidle", timeout=60_000)
        page.wait_for_timeout(4000)

        # Sidebar should already be on Upload Receipt
        body = page.locator("body").inner_text()
        if "ModuleNotFoundError" in body or "Traceback:" in body:
            fail("Streamlit traceback on homepage", page)
        print("[OK] Homepage clean")

        # Open the Sample index dropdown. Streamlit renders selectboxes as
        # role="combobox". The Upload page has 1 combobox (Sample index)
        # — pick that one.
        comboboxes = page.get_by_role("combobox")
        # The first combobox in the page is the Sample index selector.
        sample_select = comboboxes.first
        expect(sample_select).to_be_visible(timeout=15_000)
        sample_select.click()
        page.wait_for_timeout(1500)

        option = page.get_by_text("CORD sample #1", exact=True).first
        expect(option).to_be_visible(timeout=10_000)
        option.click()
        print("[OK] Selected CORD sample #1")

        # Now wait for the pipeline to complete. Cold start can take 30-90s
        # because the model + sentence-transformer + FAISS index load, then
        # Gemini Vision is called.
        print("[..] Waiting for pipeline (up to 120s)...")
        deadline = time.time() + 120
        cashback_found = False
        while time.time() < deadline:
            body = page.locator("body").inner_text()
            if "ModuleNotFoundError" in body or "Traceback:" in body or "ImportError" in body:
                fail("Streamlit traceback during pipeline", page)
            if "Cashback (strategy" in body:
                cashback_found = True
                break
            page.wait_for_timeout(3000)

        if not cashback_found:
            fail("No 'Cashback (strategy ...)' metric appeared within 120s", page)
        print("[OK] Cashback metric rendered")

        # Verify line-by-line table appears
        body = page.locator("body").inner_text()
        if "Line-by-line breakdown" not in body:
            fail("Line-by-line breakdown table missing", page)
        print("[OK] Line-by-line breakdown table present")

        # Verify Total spend is shown (anything > 0)
        if "Total spend:" not in body:
            fail("'Total spend:' caption missing", page)
        print("[OK] Total spend caption present")

        # Print the headline numbers for the human reading the test output
        for line in body.split("\n"):
            line = line.strip()
            if any(k in line for k in ("Cashback (", "Total spend:", "effective rate", "Categorised", "Merchant:")):
                print(f"    >> {line}")

        browser.close()

    print("\nDEEP PIPELINE E2E PASSED [OK]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
