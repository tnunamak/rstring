# Rstring: Rsync-Powered Code Stringification

[![PyPI version](https://badge.fury.io/py/rstring.svg)](https://badge.fury.io/py/rstring)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Rstring is a developer tool that uses Rsync to efficiently gather and stringify code from your projects. It's designed to streamline the process of preparing code context for AI programming assistants, making it easy to get intelligent insights about your codebase.

<div align="center">
  <img alt="Rstring demo" src="https://github.com/user-attachments/assets/c85106e3-2b02-42ff-b585-4234a58e8b9a" width="600">
  <p><i>Quickly prompt an LLM with your whole project!</i></p>
</div>

## Installation

```bash
pip install rstring
```

## Quick Start

Basic usage:
```bash
rstring
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

Save a new preset:
```bash
rstring --save-preset "frontend" "--include=*.js --include=*.css --exclude=node_modules"
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

1. **Rsync Usage**: Rstring uses Rsync to efficiently select files based on include/exclude patterns.

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

## Pro Tips

1. **Explore the default preset**: Check `~/.rstring.yaml` to see how the 'common' preset works.

2. **Customize for your project**: Create a project-specific preset for quick context gathering.

3. **Use with AI tools**: Rstring is great for preparing code context for AI programming assistants.

4. **Large projects may produce substantial output**: Use `--preview-length` or specific patterns for better manageability.

## Support and Contributing

- Issues and feature requests: [GitHub Issues](https://github.com/tnunamak/rstring/issues)
- Contributions: Pull requests are welcome!

## License

Rstring is released under the MIT License. See the [LICENSE](LICENSE) file for details.