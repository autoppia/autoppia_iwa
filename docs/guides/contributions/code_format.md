# Contributing Guidelines

Thank you for considering contributing to this project! To maintain code quality and consistency, we use `pre-commit`
hooks. Please follow these steps before submitting a pull request.

## Setting Up Pre-Commit

1. **Install (if not already installed)**

   ```sh
   pip install pre-commit
   ```

2. **Navigate to the repository and install hooks**

   ```sh
   pre-commit install
   ```

   This ensures that `pre-commit` runs automatically before every commit.

3. **Run on all files (optional but recommended)**

   ```sh
   pre-commit run --all-files
   ```

   This helps identify and fix any issues before committing.

## Pre-Commit Hooks Used

We use the following pre-commit hooks (configured in `.pre-commit-config.yaml`):

- **Trailing whitespace removal**
- **End-of-file fixer**
- **YAML format checker**
- **Code formatter (Black for Python, etc.)**

## Submitting a Pull Request

1. **Ensure your branch is up to date**

   ```sh
   git pull origin main
   ```

2. **Create a new feature branch**

   ```sh
   git checkout -b feature-branch-name
   ```

3. **Make changes and commit**

   ```sh
   git add .
   git commit -m "Your descriptive commit message"
   ```

   - `pre-commit` will run automatically before the commit.
   - Fix any issues before committing again if necessary.

4. **Push your branch and create a pull request**

   ```sh
   git push origin feature-branch-name
   ```

Thank you for your contribution! 🚀
