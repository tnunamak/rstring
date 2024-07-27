# Rstring

Rstring is a developer-friendly tool that uses [Rsync](https://linux.die.net/man/1/rsync) to gather and stringify code and other text from specified files and directories. It offers features like preset management, interactive mode, and easy clipboard integration.

## Features

- Use Rsync to efficiently filter files and gather their contents
- Save and manage presets for quick access to common configurations
- Interactive mode for fine-tuning file selection
- Automatic clipboard copying (with option to disable)
- File preview options
- Summary view with file tree

## Developers

Create a venv and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
```

## Installation

```bash
pip install rstring
```

## Usage

Basic usage:

```bash
rstring [rsync_options]
```

For more options:

```bash
rstring --help
```

## Examples

1. Stringify all Python files in the current directory:
   ```bash
   rstring --include="*.py" --exclude="*" .
   ```
   
2. Stringify a Next.js project and save a preset:
   ```bash
   rstring  --save-as-preset="nextjs" --include="*.js" --include="*.jsx" --include="*.ts" --include="*.tsx" \
   --exclude="node_modules" --exclude=".next" --exclude=".vercel" \
   --exclude=".git" --exclude=".vscode" --exclude=".idea" --exclude=".DS_Store" \
   --exclude="*.log"
   ```

3. Use a saved preset:
   ```bash
   rstring -p my_preset
   ```

4. Enter interactive mode:
   ```bash
   rstring -i
   ```
