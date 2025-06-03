# Contributing to PyWard

We welcome contributions to PyWard! Your help can make this linter even better at catching optimization issues and security vulnerabilities. Whether you're fixing a bug, adding a new feature, or improving documentation, your efforts are appreciated.

---

## How to Contribute

To contribute to PyWard, please follow these steps:

1.  **Fork the Repository**: Start by forking the [PyWard repository](https://github.com/karanlvm/PyWard) on GitHub.

2.  **Clone Your Fork**: Clone your forked repository to your local machine:
    ```bash
    git clone [https://github.com/your-username/PyWard.git](https://github.com/your-username/PyWardi.git)
    cd pyward-cli
    ```

3.  **Create a New Branch**: Create a new branch for your changes. Please use a descriptive name for your branch, as outlined in the [Branch Naming Conventions](#branch-naming-conventions) section below.
    ```bash
    git checkout -b feature/your-feature-name
    ```

4.  **Implement Your Changes**: Make your desired changes to the codebase. This could involve:
    * Adding new optimization checks.
    * Implementing new security vulnerability detections.
    * Improving existing rules.
    * Fixing bugs.
    * Enhancing documentation.

5.  **Add Tests (If Applicable)**: If you're adding new features or fixing bugs, please include corresponding tests to ensure your changes work as expected and prevent regressions.

6.  **Run Tests**: Before submitting your pull request, make sure all existing tests pass, and your new tests are also passing.

7.  **Commit Your Changes**: Write clear and meaningful commit messages. Good commit messages help others understand the purpose of your changes.

8.  **Push to Your Fork**: Push your new branch to your forked repository on GitHub:
    ```bash
    git push origin feature/your-feature-name
    ```

---

## Opening a Pull Request (PR)

Once you've pushed your changes to your fork, you can open a Pull Request (PR) to the main PyWard repository.

1.  **Navigate to your fork on GitHub.**
2.  You should see a banner indicating "This branch is X commits ahead of PyWard:main." or similar, with a "Compare & pull request" button. Click this button.
3.  **Ensure the base branch is `main` (or `master` if applicable) and the compare branch is your feature branch.**
4.  **Provide a clear and concise description for your PR.**
    * **Title:** Follow the [PR Naming Conventions](#pr-naming-conventions) below.
    * **Description:**
        * Explain what your PR does.
        * Why is this change necessary or beneficial?
        * If it fixes an issue, reference the issue number (e.g., `Fixes #123`).
        * Include any relevant screenshots or examples if it's a visual change or a new feature.
        * Mention any breaking changes or significant impacts if applicable.
5.  Click "Create pull request."

We will review your PR as soon as possible and may provide feedback or request further changes.

---

## Creating Issues

If you find a bug, have a feature request, or want to suggest an improvement, please open an issue on our [GitHub Issues page](https://github.com/your-username/pyward-cli/issues).

When creating an issue, please:

* **Check existing issues** to avoid duplicates.
* **Use a clear and descriptive title.**
* **For bug reports:**
    * Provide steps to reproduce the bug.
    * Describe the expected behavior.
    * Describe the actual behavior.
    * Include your Python version and PyWard version.
    * Attach any relevant code snippets or error messages.
* **For feature requests or improvements:**
    * Clearly describe the desired feature or improvement.
    * Explain why you believe it would be valuable to PyWard.
    * Provide any examples or use cases.

---

## Naming Conventions

To maintain consistency and clarity, please follow these naming conventions:

### Branch Naming Conventions

Use a prefix to indicate the type of change, followed by a concise description.

* `feature/` for new features: `feature/add-yaml-linter`
* `bugfix/` for bug fixes: `bugfix/fix-unreachable-code-detection`
* `refactor/` for code refactoring (no new features or bug fixes): `refactor/improve-cli-parsing`
* `docs/` for documentation updates: `docs/update-installation-guide`
* `chore/` for maintenance tasks, build process, etc.: `chore/update-dependencies`

Example: `git checkout -b feature/new-security-rule`

### PR Naming Conventions

Follow a similar convention to branch names, often in the format `Type: Description`.

* **`feat:`** for new features (e.g., `feat: Add detection for unsafe pickle usage`)
* **`fix:`** for bug fixes (e.g., `fix: Correct unreachable code detection in loops`)
* **`refactor:`** for code refactoring (e.g., `refactor: Optimize AST traversal logic`)
* **`docs:`** for documentation changes (e.g., `docs: Clarify contributing guidelines`)
* **`chore:`** for maintenance, build-related changes (e.g., `chore: Update development dependencies`)
* **`security:`** for security vulnerability fixes or new security checks (e.g., `security: Flag CVE-2025-XXXXX pattern`)

Example PR Title: `feat: Add new CVE pattern detection`

---

## Coding Style

Please adhere to the existing coding style of the PyWard project. We generally follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code. Using a linter like `flake8` or a formatter like `black` can help ensure your code is consistent.

---

## Code of Conduct

We aim to foster a welcoming and inclusive environment for all contributors. Please refer to our `CODE_OF_CONDUCT.md` (if you have one) for expected behavior.

---

Thank you for contributing to PyWard!
