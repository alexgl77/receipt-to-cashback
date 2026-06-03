# Deploy guide — Hugging Face Spaces

This project is too heavy for Streamlit Community Cloud (1 GB RAM
ceiling) because the runtime needs torch + easyocr + sentence-
transformers loaded simultaneously. Hugging Face Spaces free CPU
basic plan ships 16 GB RAM, which is plenty.

## Why HF Spaces over the alternatives

| Option | Verdict |
|---|---|
| Streamlit Community Cloud | **No** — 1 GB RAM ceiling, our stack peaks at ~2.5 GB |
| **Hugging Face Spaces (CPU basic, free)** | **Yes** — 16 GB RAM, 50 GB disk, native Streamlit support, build from `requirements.txt`, env vars as Repository secrets |
| Railway / Render | Works but charges past a free trial; HF Spaces is genuinely free for public Spaces |
| Self-hosted VPS | Overkill for a 10-day capstone |

## One-time setup (the user does this, not Claude)

These steps require the user's Hugging Face account; Claude cannot
sign in to HF on the user's behalf without the user pasting a token.

1. Create the Space at https://huggingface.co/new-space
   - **Owner:** your HF username
   - **Space name:** `receipt-to-cashback`
   - **License:** MIT
   - **SDK:** **Docker** (HF Spaces removed the Streamlit SDK in
     2025; Streamlit apps now ship inside a Docker container — our
     repo has a `Dockerfile` at root that the platform builds)
   - **Docker template:** Blank (we ship our own Dockerfile)
   - **Hardware:** CPU basic (free)
   - **Visibility:** Public
2. Add the Gemini API key as a **Repository secret** (Settings →
   *Variables and secrets* → New secret):
   - Name: `GEMINI_API_KEY`
   - Value: the key from https://aistudio.google.com/app/apikey
   - Type: secret (not variable — secrets are not echoed in logs)
3. Add the Space as a git remote and push:
   ```bash
   git remote add hf https://huggingface.co/spaces/<your-username>/receipt-to-cashback
   git push hf main
   ```
   (Or use a `huggingface_hub` PAT instead of password.)

## What HF Spaces reads from the repo

| Path | Purpose |
|---|---|
| `README.md` (frontmatter block) | Sets title, SDK, app entry point, colours, license |
| `app.py` | Entry point (Streamlit imports this) — already wraps `app/streamlit_app.py` |
| `requirements.txt` | Installed inside the Space's Docker build |
| `.gitignore` | Excludes `.env`, `data/receipts/`, model weights from the build |

## First build will take 5–15 minutes

HF compiles `torch`, downloads `easyocr` weights (~300 MB) and the
multilingual sentence-transformer (~470 MB) on first cold start. On
subsequent visits the wheels are cached, so warm boots take ~30 s.

## Things to check after the first successful deploy

- [ ] Upload page loads and shows the empty-state hint
- [ ] Sidebar "CORD sample #1" loads and the spine returns a result
  (will be slower than local — expect 15–25 s)
- [ ] B2B Analytics page renders charts (no Gemini call needed —
  pure pandas/sklearn)
- [ ] Ethics page renders the markdown
- [ ] No `KeyError: GEMINI_API_KEY` in the logs (means the secret is
  configured)

## Adding the URL back to this repo

Once the Space is live, paste the URL into:

- [`README.md`](../README.md) — under **Live demo**
- The Slack DM to Yossi (so he can poke around before demo day)
- The PPT (slide 1: live URL + QR code is nice to have)
