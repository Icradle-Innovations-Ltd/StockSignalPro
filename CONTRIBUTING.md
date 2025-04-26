# Contributing to Stock Market Signal Processing Web App

Thank you for your interest in contributing to the Stock Market Signal Processing Web App! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation Guidelines](#documentation-guidelines)
- [Submitting Changes](#submitting-changes)
- [Review Process](#review-process)

## Code of Conduct

This project adheres to the Contributor Covenant code of conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

### Our Pledge

We pledge to make participation in our project and community a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

Examples of behavior that contributes to creating a positive environment include:

- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

Examples of unacceptable behavior include:

- The use of sexualized language or imagery and unwelcome sexual attention or advances
- Trolling, insulting/derogatory comments, and personal or political attacks
- Public or private harassment
- Publishing others' private information, such as a physical or electronic address, without explicit permission
- Other conduct which could reasonably be considered inappropriate in a professional setting

## Getting Started

### Prerequisites

Before you begin, ensure you have met the following requirements:
- You have installed Python 3.8 or higher
- You have installed PostgreSQL 13 or higher
- You are familiar with Git and GitHub
- You have read the [README.md](README.md) and [INSTALLATION.md](INSTALLATION.md) files

### Setting Up Your Development Environment

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/stock-market-signal-processing.git
   cd stock-market-signal-processing
   ```
3. Add the original repository as a remote:
   ```bash
   git remote add upstream https://github.com/original-owner/stock-market-signal-processing.git
   ```
4. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```
5. Set up your local database as described in the installation guide.

## How to Contribute

There are many ways to contribute to the project:

1. **Code Contributions**: Implementing new features or fixing bugs
2. **Documentation**: Improving or extending the documentation
3. **Bug Reports**: Submitting well-documented bug reports
4. **Feature Requests**: Suggesting new features or improvements
5. **Testing**: Writing tests or manually testing features
6. **Design**: Improving the UI/UX of the application
7. **Code Review**: Reviewing open pull requests

### Finding Issues to Work On

- Check the GitHub Issues page for tasks labeled as "good first issue" for newcomers
- Look for issues labeled as "help wanted" for tasks that need assistance
- Feel free to ask for clarification on any issue you're interested in

## Development Workflow

1. **Create a Branch**: Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-you-are-fixing
   ```

2. **Make Changes**: Implement your changes, following the coding standards

3. **Write Tests**: Add tests for your changes when applicable

4. **Update Documentation**: Update relevant documentation

5. **Run Tests Locally**: Ensure all tests pass before submitting:
   ```bash
   pytest
   ```

6. **Commit Your Changes**: Commit with a clear and descriptive message:
   ```bash
   git commit -m "Add feature: description of the feature"
   # or
   git commit -m "Fix: description of the fix (closes #issue-number)"
   ```

7. **Push to Your Fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Submit a Pull Request**: Open a pull request against the main branch of the original repository

## Coding Standards

This project follows the PEP 8 style guide for Python code with some additional guidelines:

### Python Style Guidelines

- Use 4 spaces for indentation (not tabs)
- Maximum line length of 100 characters
- Use docstrings for all modules, functions, classes, and methods
- Write clear, descriptive variable and function names
- Keep functions focused and short (generally under 50 lines)
- Use type hints for function parameters and return values

Example function with proper style:

```python
def calculate_moving_average(data: list[float], window_size: int) -> list[float]:
    """
    Calculate the moving average of a data series.
    
    Args:
        data: List of float values to average
        window_size: Size of the moving window in data points
        
    Returns:
        List of moving average values
        
    Raises:
        ValueError: If window_size is greater than the length of data
    """
    if window_size > len(data):
        raise ValueError("Window size cannot be greater than data length")
        
    result = []
    for i in range(len(data) - window_size + 1):
        window = data[i:i + window_size]
        average = sum(window) / window_size
        result.append(average)
        
    return result
```

### JavaScript Style Guidelines

- Use 2 spaces for indentation
- Use semicolons at the end of statements
- Use camelCase for variable and function names
- Prefer const over let where applicable

### HTML/CSS Style Guidelines

- Use 2 spaces for indentation
- Use semantic HTML5 elements
- Class names should be descriptive and use kebab-case
- Close all HTML tags properly

## Testing Guidelines

### Writing Tests

- Write unit tests for all new functions and methods
- Aim for high test coverage of critical functionality
- Use pytest as the testing framework
- Mock external dependencies when necessary
- Place tests in the `tests/` directory with a structure mirroring the main package

Example test:

```python
import pytest
from utils.data_processing import calculate_moving_average

def test_calculate_moving_average():
    data = [1.0, 2.0, 3.0, 4.0, 5.0]
    window_size = 3
    
    result = calculate_moving_average(data, window_size)
    
    assert len(result) == len(data) - window_size + 1
    assert result[0] == (1.0 + 2.0 + 3.0) / 3
    assert result[1] == (2.0 + 3.0 + 4.0) / 3
    assert result[2] == (3.0 + 4.0 + 5.0) / 3

def test_calculate_moving_average_raises_error():
    data = [1.0, 2.0, 3.0]
    window_size = 4
    
    with pytest.raises(ValueError):
        calculate_moving_average(data, window_size)
```

### Running Tests

Run all tests:
```bash
pytest
```

Run specific test file:
```bash
pytest tests/utils/test_data_processing.py
```

Generate coverage report:
```bash
pytest --cov=app tests/
```

## Documentation Guidelines

### Code Documentation

- All modules, functions, classes, and methods should have docstrings
- Use Google-style docstrings for clarity
- Include examples in docstrings where helpful
- Document complex algorithms with explanatory comments

### User Documentation

- Update README.md when adding significant features
- Update USER_GUIDE.md for user-facing changes
- Keep TECHNICAL_DOCUMENTATION.md up to date with architectural changes
- Update INSTALLATION.md when changing dependencies or setup requirements

## Submitting Changes

1. Ensure your branch is up to date with the main branch:
   ```bash
   git checkout main
   git pull upstream main
   git checkout your-branch-name
   git rebase main
   ```

2. Fix any conflicts during rebase and ensure tests still pass

3. Push your changes to your fork:
   ```bash
   git push -f origin your-branch-name  # If you rebased
   ```

4. Create a pull request from your branch to the main project:
   - Use a clear, descriptive title
   - Reference any related issues (e.g., "Fixes #123")
   - Provide a detailed description of your changes
   - Include screenshots if relevant (especially for UI changes)

## Review Process

After submitting a pull request:

1. Maintainers will review your code
2. CI tests will run automatically
3. You may receive feedback requesting changes
4. Make requested changes and push to your branch
5. Once approved, a maintainer will merge your pull request

### Responding to Feedback

- Be open to feedback and constructive criticism
- Respond to comments promptly
- Explain your reasoning for design decisions
- Make requested changes or discuss alternatives

## Thank You!

Your contributions are what make the open source community such an amazing place to learn, inspire, and create. Thank you for taking the time to improve this project!