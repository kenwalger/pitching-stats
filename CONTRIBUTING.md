# Contributing

Thanks for your interest in improving this project. Contributions are welcome as pull requests or well-scoped issues.

## Getting started

1. **Fork and clone** the repository, then create a branch for your work (`fix/…`, `feature/…`, or similar).

2. **Python**: The repo targets **Python 3.13** (see `.python-version`). Use a matching interpreter when possible.

3. **Virtual environment and dependencies**

   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Run the app locally**

   ```bash
   python app.py
   ```

   Open `http://127.0.0.1:5000` and exercise the flows you changed.

5. **CLI** (optional sanity check)

   ```bash
   python main.py --start_date YYYY-MM-DD --end_date YYYY-MM-DD --n 3
   ```

   Statcast fetches need network access and can be slow; use a short date range for quick tests.

## Pull requests

- **Keep changes focused** on one concern (bugfix, feature, or docs). Avoid mixing unrelated refactors with functional changes.
- **Describe what and why** in the PR description so reviewers can follow the intent.
- **Match existing style**: naming, structure, and template/JS patterns already in the repo.
- **Update docs** when behavior or setup changes (`README.md`, `CHANGELOG.md` as appropriate).

## Issues

Use issues for bugs, small feature ideas, or questions. Include steps to reproduce for bugs, and note your OS and Python version when it might matter.

## License

By contributing, you agree your contributions will be licensed under the same terms as the project (see [LICENSE](LICENSE)).
