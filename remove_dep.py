#!/usr/bin/python3
"""
Dependency Directory Cleaner

A utility tool to clean up development-related directories that consume disk space,
such as virtual environments (venv), node_modules, and other dependency directories.

Features:
- Configurable target directories to clean
- Dry run mode to preview deletions
- Size calculation before deletion
- Logging of operations
- Skip list for protected directories
- Color-coded output
"""

import os
import shutil
import argparse
from datetime import datetime
import logging
from typing import Set, List, Dict
import colorama
from colorama import Fore, Style

# Initialize colorama for cross-platform colored output
colorama.init(autoreset=True)

# Default directories to target for cleanup
DEFAULT_TARGET_DIRS = {
    'venv',
    'node_modules',
    '.env',
    '.pytest_cache',
    '.mypy_cache'
}

# Default directories to protect from deletion
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
    '/root'
}

class DependencyCleaner:
    """Main class for handling dependency directory cleanup operations."""

    def __init__(self,
                 root_dir: str,
                 target_dirs: Set[str] = DEFAULT_TARGET_DIRS,
                 protected_paths: Set[str] = DEFAULT_PROTECTED_PATHS,
                 dry_run: bool = False,
                 interactive: bool = True,
                 log_file: str = None):
        """
        Initialize the DependencyCleaner.

        Args:
            root_dir: Starting directory for the search
            target_dirs: Set of directory names to target for deletion
            protected_paths: Set of paths to protect from deletion
            dry_run: If True, only simulate deletions
            interactive: If True, ask for confirmation before each deletion
            log_file: Path to log file (if None, logging will be disabled)
        """
        self.root_dir = os.path.abspath(root_dir)
        self.target_dirs = target_dirs
        self.protected_paths = protected_paths
        self.dry_run = dry_run
        self.interactive = interactive
        self.stats = {'total_size': 0, 'deleted_count': 0, 'failed_count': 0}

        # Setup logging
        if log_file:
            logging.basicConfig(
                filename=log_file,
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s'
            )

    def get_dir_size(self, path: str) -> int:
        """Calculate total size of a directory in bytes."""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    total_size += os.path.getsize(file_path)
        except Exception as e:
            logging.warning(f"Failed to calculate size for {path}: {e}")
        return total_size

    def format_size(self, size: int) -> str:
        """Convert size in bytes to human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"

    def is_protected_path(self, path: str) -> bool:
        """Check if the path is in the protected paths list."""
        return any(path.startswith(protected) for protected in self.protected_paths)

    def remove_directory(self, path: str) -> bool:
        """Remove a directory and return True if successful."""
        try:
            if self.dry_run:
                print(f"{Fore.YELLOW}[DRY RUN] Would delete: {path}")
                return True

            if self.interactive:
                size = self.get_dir_size(path)
                response = input(
                    f"{Fore.YELLOW}Delete {path} ({self.format_size(size)})? [y/N]: "
                ).lower()
                if response != 'y':
                    print(f"{Fore.BLUE}Skipping {path}")
                    return False

            shutil.rmtree(path)
            logging.info(f"Successfully removed: {path}")
            return True

        except Exception as e:
            self.stats['failed_count'] += 1
            logging.error(f"Failed to remove {path}: {e}")
            print(f"{Fore.RED}Error removing {path}: {e}")
            return False

    def clean(self) -> Dict:
        """
        Main cleanup method that walks through directories and removes targets.
        Returns statistics about the cleanup operation.
        """
        print(f"{Fore.GREEN}Starting cleanup from: {self.root_dir}")
        if self.dry_run:
            print(f"{Fore.YELLOW}Running in DRY RUN mode - no files will be deleted")

        for dirpath, dirnames, _ in os.walk(self.root_dir, topdown=True):
            if self.is_protected_path(dirpath):
                dirnames.clear()  # Skip protected directories
                continue

            for dirname in dirnames[:]:  # Copy list as we'll modify it
                if dirname in self.target_dirs:
                    full_path = os.path.join(dirpath, dirname)
                    size = self.get_dir_size(full_path)

                    if self.remove_directory(full_path):
                        self.stats['deleted_count'] += 1
                        self.stats['total_size'] += size

        return self.stats

def main():
    """Parse command line arguments and run the cleanup operation."""
    parser = argparse.ArgumentParser(
        description="Clean up development dependency directories to free up disk space."
    )
    parser.add_argument(
        '--root', '-r',
        default='/',
        help='Root directory to start the search (default: /)'
    )
    parser.add_argument(
        '--dry-run', '-d',
        action='store_true',
        help='Show what would be deleted without actually deleting'
    )
    parser.add_argument(
        '--no-interactive', '-n',
        action='store_true',
        help='Delete without asking for confirmation'
    )
    parser.add_argument(
        '--log-file', '-l',
        help='Path to log file'
    )
    parser.add_argument(
        '--target-dirs', '-t',
        nargs='+',
        default=list(DEFAULT_TARGET_DIRS),
        help='Space-separated list of directory names to target'
    )

    args = parser.parse_args()

    # Confirm before proceeding with non-dry-run
    if not args.dry_run:
        confirm = input(
            f"This script will scan for these patterns {DEFAULT_TARGET_DIRS}\n"
            f"Root Directory [{args.root}] (Enter y to continue) : "
        )
        if not confirm.lower().startswith('y'):
            print("Operation cancelled.")
            return

    # Initialize and run the cleaner
    cleaner = DependencyCleaner(
        root_dir=args.root,
        target_dirs=set(args.target_dirs),
        dry_run=args.dry_run,
        interactive=not args.no_interactive,
        log_file=args.log_file
    )

    stats = cleaner.clean()

    # Print summary
    print(f"\n{Fore.GREEN}Cleanup Summary:")
    print(f"Directories processed: {stats['deleted_count']}")
    print(f"Total space freed: {cleaner.format_size(stats['total_size'])}")
    print(f"Failed operations: {stats['failed_count']}")

if __name__ == "__main__":
    main()
