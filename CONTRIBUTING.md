# Contributing

Thanks for contributing to **News Intelligence Analyzer**.

## Development Setup

1. Create virtual environment
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
3. Run tests
   ```bash
   python -m unittest discover -s tests -p "test_*.py"
   ```
4. Run app
   ```bash
   streamlit run app.py
   ```

## Pull Request Guidelines

- Keep changes focused and documented.
- Add/adjust tests when modifying logic.
- Update README if setup/usage changes.
- Ensure code compiles and tests pass before submitting.
