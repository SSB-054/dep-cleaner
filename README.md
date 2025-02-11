# Dependency Directory Cleaner 🧹

A powerful Python utility to clean up development dependency directories and free up valuable disk space.
This tool helps you manage and remove common development directories like `node_modules`, `venv`, `.env`, and other cache directories that can consume significant storage space over time.


## 🌟 Features

- 🎯 Configurable target directories (`node_modules`, `venv`, `.env`, etc.)
- 🔍 Dry run mode to preview deletions
- 📊 Size calculation and reporting
- 🛡️ Protected system paths
- 📝 Detailed logging
- 🎨 Color-coded output
- 🤝 Interactive and non-interactive modes
- 💪 Robust error handling

## 🚀 Installation

1. Clone the repository:
```bash
git clone git@github.com:SSB-054/dep-cleaner.git
cd dep-cleaner
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## 💡 Usage

### Basic Usage

```bash
# Basic cleanup (will prompt for confirmation)
python remove_dep.py

# Start cleanup from a specific directory
python remove_dep.py --root /path/to/projects

# Preview what would be deleted (dry run)
python remove_dep.py --dry-run
```

### Advanced Options

```bash
# Clean specific directory types
python remove_dep.py --target-dirs node_modules venv .pytest_cache

# Non-interactive mode with logging
python remove_dep.py --no-interactive --log-file cleanup.log

# Combine multiple options
python remove_dep.py --root /home/user/projects --dry-run --target-dirs node_modules venv
```

### Command Line Arguments

| Argument | Short | Description |
|----------|-------|-------------|
| `--root` | `-r` | Root directory to start the search (default: /) |
| `--dry-run` | `-d` | Show what would be deleted without actually deleting |
| `--no-interactive` | `-n` | Delete without asking for confirmation |
| `--log-file` | `-l` | Path to log file |
| `--target-dirs` | `-t` | Space-separated list of directory names to target |

## ⚙️ Customization

### Adding Custom Target Directories

You can modify the `DEFAULT_TARGET_DIRS` set in the script to include additional directory types:

```python
DEFAULT_TARGET_DIRS = {
    'venv',
    'node_modules',
    '.env',
    '__pycache__',
    '.pytest_cache',
    '.mypy_cache',
    'your_custom_dir'  # Add your custom directory here
}
```

### Modifying Protected Paths

Add or remove protected paths by modifying the `DEFAULT_PROTECTED_PATHS` set:

```python
DEFAULT_PROTECTED_PATHS = {
    '/usr',
    '/bin',
    '/sbin',
    '/var',
    '/etc',
    '/lib',
    '/lib64',
    '/boot',
    '/sys',
    '/root',
    '/your/protected/path'  # Add your protected path here
}
```

### Customizing Output Colors

The script uses the `colorama` library for colored output. You can modify the colors by changing the `Fore` color values:

```python
print(f"{Fore.GREEN}Success message")  # Green text
print(f"{Fore.YELLOW}Warning message")  # Yellow text
print(f"{Fore.RED}Error message")      # Red text
```

## 📊 Example Output

```
Starting cleanup from: /home/user/projects
Delete /home/user/projects/project1/node_modules (156.42 MB)? [y/N]: y
Delete /home/user/projects/project2/venv (89.75 MB)? [y/N]: y

Cleanup Summary:
Directories processed: 2
Total space freed: 246.17 MB
Failed operations: 0
```

## ⚠️ Safety Features

1. **Protected Paths**: System-critical directories are protected from deletion
2. **Size Confirmation**: Shows directory size before deletion
3. **Dry Run Mode**: Preview what would be deleted
4. **Logging**: Detailed logging of all operations
5. **Interactive Confirmation**: Prompts for confirmation before each deletion

## 🤝 Contributing

Contributions are always welcome! Here's how you can help:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/improvement`)
3. Make your changes
4. Commit your changes (`git commit -am 'Add some feature'`)
5. Push to the branch (`git push origin feature/improvement`)
6. Create a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Suraj Singh Bisht**
- Email: surajsinghbisht054@gmail.com
- GitHub: [@surajsinghbisht054](https://github.com/surajsinghbisht054)


## 📖 Changelog

### v1.0.0 (Initial Release)
- Basic functionality for cleaning dependency directories
- Support for multiple target directories
- Interactive and non-interactive modes
- Dry run capability
- Size reporting
- Protected paths
- Logging system

---

⭐️ If you find this tool useful, please consider giving it a star on GitHub!
