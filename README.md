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
