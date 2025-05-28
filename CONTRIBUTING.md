# Contributing to Rstring

Thanks for your interest in contributing! Here's how to get started:

## Development Setup

1. **Clone and setup development environment**:
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

4. **Use development version**:
   ```bash
   # With dev environment activated
   rstring [options]  # Uses your development code
   ```

5. **Switch between versions**:
   ```bash
   # Use development version
   source venv/bin/activate
   rstring [options]

   # Use production version
   deactivate
   rstring [options]  # Uses globally installed version
   ```

## Guidelines

- Fork the repo and create your branch from `main`
- Add tests for new functionality
- Ensure all tests pass
- Keep the focused scope: efficient code stringification for AI assistants
- Follow existing code style

## Questions?

Open an issue for discussion before major changes.