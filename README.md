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
rstring  # Use the default preset
```

```bash
rstring --include=*/ --include=*.py --exclude=* # traverse all dirs, include .py files, exclude everything else
```

Get help:
```bash
rstring --help
```

Use a specific preset:
```bash
rstring --preset my_preset
```

Get a tree view of selected files:
```bash
rstring --summary
```

## Advanced Usage

### Custom Presets

Create a new preset:
```bash
rstring --save-preset python --include=*/ --include=*.py --exclude=*  # save it
rstring --preset python  # use it
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

### Interactive mode:

Enter interactive mode to continuously preview and select matched files:
```bash
rstring -i
```

## Understanding Rstring

1. **Under the Hood**: Rstring efficiently selects files based on filters by running `rsync --archive --itemize-changes --dry-run --list-only <your filters>`. This means you can use Rsync's powerful include/exclude patterns to customize file selection.

2. **Preset System**: The default configuration file is at `~/.rstring.yaml`. The 'common' preset is used by default and includes sensible exclusions for most projects.

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

1. **Explore the default preset**: Check `~/.rstring.yaml` to see how the 'common' preset works.

2. **Refer to Rsync documentation**: Rstring uses Rsync for file selection. Refer to the [Filter Rules](https://linux.die.net/man/1/rsync) section of the rsync man page to understand how include/exclude patterns work.

3. **Customize for your project**: Create a project-specific preset for quick context gathering.

4. **Use with AI tools**: Rstring is great for preparing code context for AI programming assistants.

5. **Large projects may produce substantial output**: Use `--preview-length` or specific patterns for better manageability.

## Development

If you'd like to contribute to Rstring or set it up for local development, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/tnunamak/rstring.git
   cd rstring
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

4. Install the package in editable mode:
   ```bash
   pip install -e .
   ```

5. Run the tests:
   ```bash
   pytest
   ```

### Running Rstring Locally

To run Rstring locally during development:

1. Make sure you're in the project root directory and your virtual environment is activated.

2. Run Rstring using the Python interpreter:
   ```bash
   python -m rstring [options]
   ```

   For example:
   ```bash
   python -m rstring --include=*/ --include=*.py --exclude=*
   ```

3. If you want to use the `rstring` command directly, you can create an alias or a batch file:

   On Unix-like systems (add to your shell configuration file, e.g., `.bashrc` or `.zshrc`):
   ```bash
   alias rstring="python /path/to/rstring/directory/rstring/__main__.py"
   ```

   On Windows (create a batch file named `rstring.bat` in a directory in your PATH):
   ```batch
   @echo off
   python C:\path\to\rstring\directory\rstring\__main__.py %*
   ```

   After setting up the alias or batch file, you can use `rstring` as if it were installed:
   ```bash
   rstring --help
   ```

### Contributing

We welcome contributions to Rstring! Here are some guidelines:

1. Fork the repository and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. Ensure the test suite passes.
4. Make sure your code lints.
5. Issue a pull request!

For more details on contributing, please see our [CONTRIBUTING.md](CONTRIBUTING.md) file.

## Support and Contributing

- Issues and feature requests: [GitHub Issues](https://github.com/tnunamak/rstring/issues)
- Contributions: Pull requests are welcome!

## License

Rstring is released under the MIT License. See the [LICENSE](LICENSE) file for details.