# Rstring: Rsync-Powered Code Stringification

[![PyPI version](https://badge.fury.io/py/rstring.svg)](https://badge.fury.io/py/rstring)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Rstring is a developer tool that uses [Rsync](https://linux.die.net/man/1/rsync) to efficiently gather and stringify code from your projects. It's designed to streamline the process of preparing code context for AI programming assistants, making it easy to get intelligent insights about your codebase.

<div align="center">
  <img alt="Rstring demo" src="https://github.com/user-attachments/assets/c85106e3-2b02-42ff-b585-4234a58e8b9a" width="600">
  <p><i>Quickly prompt an LLM with your whole project!</i></p>
</div>

## Installation

Rstring requires Python 3.8+. We recommend using `pipx` for installation, as it installs Rstring in an isolated environment, preventing conflicts with other packages.

### Using pipx (recommended)

1. Install pipx if you haven't already. Follow the [official pipx installation guide](https://pipx.pypa.io/stable/installation/) for your operating system.

2. Install Rstring:
   ```bash
   pipx install rstring
   ```

### Using pip

If you prefer to use pip, you can install Rstring with:

```bash
pip install rstring
```

### Updating Rstring

To update Rstring to the latest version:

With pipx:
```bash
pipx upgrade rstring
```

With pip:
```bash
pip install --upgrade rstring
```

For more detailed information about pipx and its usage, refer to the [pipx documentation](https://pipx.pypa.io/stable/).

## Quick Start

Basic usage:
```bash
rstring  # All files (filtered by .gitignore)
```

Work with different directories:
```bash
rstring /path/to/project  # Analyze a specific directory
rstring -C /path/to/project  # Change directory before processing
```

Custom filtering:
```bash
rstring --include='*.py'  # Only Python files
rstring --include='*/' --include='*.js' --exclude='test*'  # Complex patterns
```

Get help:
```bash
rstring --help
```

Get a tree view of selected files:
```bash
rstring --summary
```

## Advanced Usage

### Custom Filtering

Rstring uses rsync's powerful include/exclude patterns:

```bash
# Include only Python files
rstring --include='*/' --include='*.py' --exclude='*'

# Include web development files, exclude tests
rstring --include='*/' --include='*.{js,css,html}' --exclude='test*' --exclude='*'

# Include documentation
rstring --include='*/' --include='*.md' --include='*.rst' --exclude='*'
```

### Creating Custom Shortcuts

For frequently used patterns, create shell aliases in your `.bashrc` or `.zshrc`:

```bash
# Python source files only
alias rstring-py="rstring --include='*/' --include='*.py' --exclude='test*'"

# Web development files
alias rstring-web="rstring --include='*/' --include='*.{js,ts,css,html}' --exclude='node_modules/'"

# Documentation files
alias rstring-docs="rstring --include='*/' --include='*.{md,rst,txt}' --exclude='*'"

# All source code (no tests, docs, or config)
alias rstring-src="rstring --include='src/' --include='lib/' --exclude='*'"
```

Usage:
```bash
rstring-py                    # Python files in current directory
rstring-web -C /path/to/app   # Web files in different directory
rstring-docs --summary        # Documentation with tree view
```

### File Preview

Limit output to first N lines of each file:
```bash
rstring --preview-length=10
```

### Gitignore Integration

By default, Rstring automatically excludes .gitignore patterns. To ignore .gitignore:
```bash
rstring --no-gitignore
```

### Interactive mode

Enter interactive mode to continuously preview and select matched files:
```bash
rstring -i
```

## Understanding Rstring

1. **Under the Hood**: Rstring efficiently selects files based on filters by running `rsync --archive --itemize-changes --dry-run --list-only <your filters>`. This means you can use Rsync's powerful include/exclude patterns to customize file selection.

2. **Default Behavior**: When run without specific patterns, rstring includes all files and directories, filtered by your project's `.gitignore` file.

3. **Output Format**:
   ```
   --- path/to/file1.py ---
   [File contents]

   --- path/to/file2.js ---
   [File contents]
   ```

4. **Binary Files**: Content of binary files is represented as a hexdump preview.

5. **Clipboard Integration**: Output is automatically copied to clipboard unless disabled with `--no-clipboard`.

6. **Git Integration**: By default, Rstring respects .gitignore patterns. Use `--no-gitignore` to ignore them.

## Pro Tips

1. **Start simple**: `rstring` with no arguments gives you everything in your project (filtered by .gitignore).

2. **Refer to Rsync documentation**: Rstring uses Rsync for file selection. Refer to the [Filter Rules](https://linux.die.net/man/1/rsync) section of the rsync man page to understand how include/exclude patterns work.

3. **Create project-specific aliases**: Set up shell aliases for your common file selection patterns.

4. **Use with AI tools**: Rstring is great for preparing code context for AI programming assistants.

5. **Large projects may produce substantial output**: Use `--preview-length` or specific patterns for better manageability.

## Common Patterns

Here are some useful rsync patterns for different scenarios:

```bash
# Python projects
rstring --include='*/' --include='*.py' --exclude='__pycache__/' --exclude='test*'

# JavaScript/Node.js projects
rstring --include='*/' --include='*.{js,ts,jsx,tsx}' --exclude='node_modules/' --exclude='test*'

# Web projects (frontend)
rstring --include='*/' --include='*.{js,ts,css,html,vue,svelte}' --exclude='dist/' --exclude='build/'

# Documentation only
rstring --include='*/' --include='*.{md,rst,txt}' --exclude='*'

# Configuration files
rstring --include='*/' --include='*.{json,yaml,yml,toml,ini}' --exclude='*'

# Source code only (exclude tests, docs, config)
rstring --include='src/' --include='lib/' --exclude='*'
```

## Support and Contributing

- **Issues and feature requests**: [GitHub Issues](https://github.com/tnunamak/rstring/issues)
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines
- **Pull requests welcome!**

## License

Rstring is released under the MIT License. See the [LICENSE](LICENSE) file for details.