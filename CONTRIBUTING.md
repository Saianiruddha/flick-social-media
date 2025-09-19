# Contributing to FLICK ⚡

We love your input! We want to make contributing to FLICK as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

## Pull Requests

Pull requests are the best way to propose changes to the codebase. We actively welcome your pull requests:

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## Any contributions you make will be under the MIT Software License

In short, when you submit code changes, your submissions are understood to be under the same [MIT License](http://choosealicense.com/licenses/mit/) that covers the project. Feel free to contact the maintainers if that's a concern.

## Report bugs using GitHub's [issue tracker](https://github.com/yourusername/FLICK/issues)

We use GitHub issues to track public bugs. Report a bug by [opening a new issue](https://github.com/yourusername/FLICK/issues/new); it's that easy!

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

## Use a Consistent Coding Style

* Use 4 spaces for indentation in Python
* Use 2 spaces for indentation in CSS/JS
* Follow PEP 8 for Python code
* Use meaningful variable and function names
* Add comments for complex logic
* Keep functions small and focused

## FLICK Animation Guidelines

When contributing animations:

- Keep animations under 300ms for micro-interactions
- Use CSS custom properties for consistency
- Test on both desktop and mobile
- Respect `prefers-reduced-motion` setting
- Document any new animation classes

## Getting Started

1. Install Python 3.9+
2. Clone the repository
3. Create a virtual environment: `python -m venv .venv`
4. Activate virtual environment: `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (macOS/Linux)
5. Install dependencies: `pip install -r requirements.txt`
6. Run migrations: `python manage.py migrate`
7. Start development server: `python manage.py runserver`

## Questions?

Feel free to open an issue for any questions about contributing!

---

**Happy Contributing! 🎉**