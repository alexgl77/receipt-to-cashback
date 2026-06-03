"""HF Spaces entry point.

Hugging Face Spaces expects `app.py` at the repo root. The real
application code lives in `app/streamlit_app.py` so the project keeps
its module layout. This file just defers to that.
"""

from app.streamlit_app import main

if __name__ == "__main__":
    main()
