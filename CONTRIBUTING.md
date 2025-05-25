# Contributing to Rstring

Thanks for your interest in contributing! Here's how to get started:

## Development Setup

1. **Clone and setup**:
   ```bash
   git clone https://github.com/tnunamak/rstring.git
   cd rstring
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Install for development**:
   ```bash
   pip install -e .
   pip install -r requirements-dev.txt
   ```

3. **Run tests**:
   ```bash
   pytest
   ```

4. **Use locally**:
   ```bash
   # After pip install -e ., you can use rstring from anywhere:
   rstring [options]

   # Or if that doesn't work, use the module form:
   python -m rstring [options]
   ```

## Guidelines

- Fork the repo and create your branch from `main`
- Add tests for new functionality
- Ensure all tests pass
- Keep the focused scope: efficient code stringification for AI assistants
- Follow existing code style

## Questions?

Open an issue for discussion before major changes.