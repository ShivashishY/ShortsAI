# Contributing to YouTube to Shorts AI Generator

First off, thank you for considering contributing to this project! 🎉

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Style Guidelines](#style-guidelines)
- [Commit Messages](#commit-messages)

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code:

- Be respectful and inclusive
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates.

**When reporting a bug, include:**
- A clear, descriptive title
- Steps to reproduce the issue
- Expected behavior vs actual behavior
- Screenshots or logs if applicable
- Your environment (OS, Python version, Node version)

### Suggesting Features

Feature suggestions are welcome! Please:
- Check if the feature has already been requested
- Provide a clear use case
- Explain why this feature would be useful

### Code Contributions

1. Look for issues labeled `good first issue` or `help wanted`
2. Comment on the issue to let others know you're working on it
3. Fork and clone the repository
4. Create a feature branch
5. Make your changes
6. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- FFmpeg
- Ollama (optional, for AI features)

### Quick Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/youtube-to-shorts-ai.git
cd youtube-to-shorts-ai

# Run automated setup
./setup.sh  # macOS/Linux
# or
.\setup.ps1  # Windows
```

### Manual Setup

```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
pip install -r requirements-dev.txt  # development dependencies

# Frontend
cd ../frontend
npm install
```

### Running Tests

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm test
```

### Running Linters

```bash
# Python
cd backend
flake8 .
black --check .

# JavaScript/React
cd frontend
npm run lint
```

## Pull Request Process

1. **Branch naming**: Use descriptive names
   - `feature/add-instagram-support`
   - `fix/video-download-error`
   - `docs/update-api-documentation`

2. **Before submitting**:
   - Update documentation if needed
   - Add tests for new features
   - Ensure all tests pass
   - Run linters and fix any issues

3. **PR description should include**:
   - What changes were made
   - Why the changes were made
   - How to test the changes
   - Related issue numbers (e.g., "Fixes #123")

4. **Review process**:
   - PRs require at least one approval
   - Address reviewer feedback promptly
   - Keep PRs focused and small when possible

## Style Guidelines

### Python (Backend)

- Follow [PEP 8](https://pep8.org/)
- Use [Black](https://black.readthedocs.io/) for formatting
- Use type hints where possible
- Write docstrings for functions and classes

```python
def process_video(url: str, duration: int = 60) -> list[dict]:
    """
    Process a video and extract clips.
    
    Args:
        url: YouTube video URL
        duration: Clip duration in seconds
        
    Returns:
        List of clip metadata dictionaries
    """
    pass
```

### JavaScript/React (Frontend)

- Use ESLint with the project configuration
- Use Prettier for formatting
- Prefer functional components with hooks
- Use meaningful component and variable names

```jsx
// Good
const VideoPreview = ({ clip, onDownload }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  // ...
};

// Avoid
const VP = ({ c, od }) => {
  const [x, setX] = useState(false);
  // ...
};
```

### CSS/Tailwind

- Use Tailwind utility classes
- Extract repeated patterns to components
- Use semantic color names from the theme

## Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```
feat(backend): add TikTok URL support

fix(frontend): resolve video preview loading state

docs: update API documentation for new endpoints

refactor(ai): improve motion detection algorithm
```

## Questions?

Feel free to open an issue with the `question` label or reach out to the maintainers.

Thank you for contributing! 🚀
