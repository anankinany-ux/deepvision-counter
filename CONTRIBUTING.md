# Contributing to DeepVision Counter

Thank you for your interest in contributing to DeepVision Counter! 🎉

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:

- **Clear title** describing the bug
- **Steps to reproduce** the issue
- **Expected behavior** vs **actual behavior**
- **Screenshots** if applicable
- **System information** (OS, Python version, etc.)

### Suggesting Features

We welcome feature suggestions! Please:

- Check if the feature was already suggested
- Provide a clear description
- Explain the use case
- Consider implementation complexity

### Code Contributions

1. **Fork the repository**
2. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Test thoroughly**
5. **Commit with clear messages**:
   ```bash
   git commit -m "Add: Description of your change"
   ```
6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Open a Pull Request**

### Code Style

- Follow PEP 8 Python style guide
- Use meaningful variable names
- Add comments for complex logic
- Keep functions focused and small
- Write docstrings for functions/classes

### Testing

Before submitting:
- Test on your platform (Windows/macOS/Linux)
- Test with different camera configurations
- Ensure no errors in console
- Test edge cases

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/deepvision-counter.git
cd deepvision-counter

# Create virtual environment
python -m venv .venv

# Activate
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Make your changes
# Test your changes
python deepvision_counter.py
```

## Pull Request Process

1. Update README.md if needed
2. Update documentation if adding features
3. Ensure code follows style guidelines
4. Test on at least one platform
5. Wait for review and feedback

## Questions?

Open a discussion or issue if you have questions about contributing!

Thank you for making DeepVision Counter better! 🙏
