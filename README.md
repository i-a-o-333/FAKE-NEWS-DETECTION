# News Intelligence Analyzer

**Subtitle:** AI Narrative Investigation System

A professional Streamlit web application that investigates user-submitted news text or questions, extracts claims, finds references, evaluates reliability/manipulation risk, and generates an intelligence-style report.

> Core principle: this project follows an analysis workflow (triangulation + reasoning), not simple keyword counting.

## Features

- Claim extraction and per-claim verifiability analysis
- Reference triangulation across mainstream, academic, and alternative contexts
- Intent analysis and manipulation pattern detection
- Objectivity, factual reliability, and PR/propaganda scoring
- Final intelligence assessment with explicit reasoning
- Follow-up investigation questions
- Professional UI with saturated red→white design and animated 🌸 background

## Repository Structure
A Streamlit-based intelligence analysis web app that investigates user-submitted news text or questions, extracts claims, finds reference material, evaluates verifiability and manipulation risk, and produces a structured intelligence-style report.

> Core principle: this project is designed as an **analysis workflow**, not a simple keyword counter or binary classifier.

## Features

- Large centered input with one-click analysis
- Claim extraction and claim-type classification
- Claim-level verifiability assessment (specificity, evidence cues, independent verifiability)
- Reference discovery and triangulation:
  - Mainstream/reference context (Wikipedia)
  - Academic context (Crossref)
  - Alternative/non-mainstream/OSINT guidance entries
- Intent analysis:
  - Neutral information
  - Persuasion
  - Reputation improvement (PR)
  - Political influence
  - Emotional manipulation
- Manipulation pattern analysis:
  - Emotional pressure
  - One-sided framing
  - Hero/villain framing
  - Unsupported assertions
- Scoring:
  - Objectivity score (0-100)
  - Factual reliability score (0-100)
  - PR/propaganda probability (0-100)
- Final intelligence assessment with explicit reasoning
- AI-generated follow-up investigation questions
- Professional UI:
  - Red → white saturated gradient
  - Animated 🌸 flower rain background
  - Score bars + risk labels/panels

---

## Project Structure

```text
.
├── app.py
├── requirements.txt
├── pyproject.toml
├── README.md
├── CONTRIBUTING.md
├── LICENSE
├── docs/
│   └── sample-preview.html
├── src/
│   └── news_intel/
│       ├── analyzer.py
│       ├── models.py
│       ├── reference_finder.py
│       ├── text_processing.py
│       └── ui.py
└── tests/
    ├── test_analyzer.py
    └── test_text_processing.py
└── src/
    └── news_intel/
        ├── analyzer.py
        ├── models.py
        ├── reference_finder.py
        ├── text_processing.py
        └── ui.py
```

## Quick Start

```bash
git clone <your-repo-url>
cd FAKE-NEWS-DETECTION
python -m venv .venv
source .venv/bin/activate      # Linux/macOS
# .venv\Scripts\activate       # Windows (PowerShell)
pip install -U pip
pip install -r requirements.txt
streamlit run app.py
```

If `streamlit` command is unavailable:

```bash
python -m streamlit run app.py
```

## Tests and Checks

```bash
python -m py_compile app.py src/news_intel/*.py
python -m unittest discover -s tests -p "test_*.py"
```

## Sample HTML Preview Link

- Local static preview: [`docs/sample-preview.html`](docs/sample-preview.html)
- GitHub Pages URL pattern:
  - `https://<YOUR_GITHUB_USERNAME>.github.io/<YOUR_REPOSITORY_NAME>/docs/sample-preview.html`

Example format:
`https://acme-labs.github.io/FAKE-NEWS-DETECTION/docs/sample-preview.html`

## Production Notes

- Recommended Python: **3.10+**
- App continues to provide useful reference links when upstream APIs are unavailable
- Keep runtime isolated in a virtual environment for commercial deployments

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).

## Disclaimer

This tool provides decision-support analysis and hypothesis framing. It does **not** guarantee factual truth and should be used with independent verification and professional judgment.
### 1) Clone

```bash
git clone <your-repo-url>
cd FAKE-NEWS-DETECTION
```

### 2) Create virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows PowerShell
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

### 4) Run the web app

```bash
streamlit run app.py
```

Then open the local URL shown by Streamlit (typically `http://localhost:8501`).

---

## Usage

Paste either:
- a full news paragraph/article excerpt, or
- a short investigation prompt (e.g., `Do aliens exist?`).

Click **Analyze** to receive:
1. Summary
2. Extracted claims
3. Reference findings
4. Intent + manipulation analysis
5. Scores and risk cues
6. Final assessment and reasoning
7. Further investigation questions

---

## Notes for GitHub Publishing

- This repository includes:
  - `README.md` for project overview and setup
  - `requirements.txt` for dependencies
  - `.gitignore` for Python and Streamlit artifacts
- For best portability, keep Python at 3.10+.
- If external APIs are temporarily unavailable, the app still returns generated alternative reference entries and a full report structure.

---

## Disclaimer

This tool provides decision-support analysis and hypothesis framing. It does **not** guarantee factual truth and should be used with independent verification and source-critical judgment.
