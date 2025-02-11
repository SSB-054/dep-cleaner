#!/usr/bin/python3
"""
Dependency Directory Cleaner

A utility tool to clean up development-related directories that consume disk space,
such as virtual environments (venv), node_modules, and other dependency directories.

Features:
- Configurable target directories to clean
- Dry run mode to preview deletions
- Size calculation before deletion
- Detailed progress reporting
- Interactive confirmation dialogs
- Comprehensive logging
- Skip list for protected directories
- Color-coded output with progress bars
"""

import os
import shutil
import argparse
from datetime import datetime
import logging
from typing import Set, List, Dict
import colorama
from colorama import Fore, Style
import time
from tqdm import tqdm

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
        self.stats = {
            'total_size': 0,
            'deleted_count': 0,
            'failed_count': 0,
            'skipped_count': 0,
            'start_time': time.time()
        }

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
            with tqdm(desc=f"{Fore.BLUE}Calculating size", unit="files", leave=False) as pbar:
                for dirpath, dirnames, filenames in os.walk(path):
                    pbar.update(len(filenames))
                    for filename in filenames:
                        file_path = os.path.join(dirpath, filename)
                        try:
                            total_size += os.path.getsize(file_path)
                        except OSError:
                            continue
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

            size = self.get_dir_size(path)
            size_str = self.format_size(size)

            if self.interactive:
                print(f"\n{Fore.CYAN}Directory: {path}")
                print(f"{Fore.CYAN}Size: {size_str}")
                print(f"{Fore.CYAN}Contents: {len(os.listdir(path))} items")

                response = input(
                    f"\n{Fore.YELLOW}Options:\n"
                    f"  [y] Yes - delete this directory\n"
                    f"  [n] No - skip this directory\n"
                    f"  [a] All - delete this and all remaining directories\n"
                    f"  [q] Quit - stop the cleanup process\n"
                    f"\nYour choice [y/n/a/q]: "
                ).lower()

                if response == 'q':
                    print(f"\n{Fore.YELLOW}Cleanup process stopped by user.")
                    raise KeyboardInterrupt
                elif response == 'a':
                    self.interactive = False
                elif response != 'y':
                    self.stats['skipped_count'] += 1
                    print(f"{Fore.BLUE}Skipping {path}")
                    return False

            print(f"{Fore.GREEN}Removing: {path} ({size_str})")
            with tqdm(total=1, desc="Deleting", unit="dir") as pbar:
                shutil.rmtree(path)
                pbar.update(1)

            logging.info(f"Successfully removed: {path} ({size_str})")
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
        print(f"\n{Fore.GREEN}=== Dependency Directory Cleaner ===")
        print(f"{Fore.CYAN}Starting cleanup from: {self.root_dir}")
        print(f"{Fore.CYAN}Target directories: {', '.join(sorted(self.target_dirs))}")

        if self.dry_run:
            print(f"{Fore.YELLOW}Running in DRY RUN mode - no files will be deleted")

        try:
            for dirpath, dirnames, _ in os.walk(self.root_dir, topdown=True):
                if self.is_protected_path(dirpath):
                    print(f"{Fore.YELLOW}Skipping protected path: {dirpath}")
                    dirnames.clear()
                    continue

                for dirname in dirnames[:]:
                    if dirname in self.target_dirs:
                        full_path = os.path.join(dirpath, dirname)
                        size = self.get_dir_size(full_path)

                        if self.remove_directory(full_path):
                            self.stats['deleted_count'] += 1
                            self.stats['total_size'] += size

        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Cleanup process interrupted by user")

        self.stats['end_time'] = time.time()
        return self.stats

def main():
    """Parse command line arguments and run the cleanup operation."""
    parser = argparse.ArgumentParser(
        description="Clean up development dependency directories to free up disk space.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--root', '-r',
        default=os.getcwd(),
        help='Root directory to start the search (default: current directory)'
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

    # Initial warning and confirmation
    if not args.dry_run:
        print(f"\n{Fore.YELLOW}WARNING: This will delete the following types of directories:")
        for target in sorted(args.target_dirs):
            print(f"  - {target}")
        print(f"\n{Fore.YELLOW}Starting directory: {args.root}")

        confirm = input(
            f"\n{Fore.YELLOW}Are you sure you want to proceed? [y/N]: "
        )
        if not confirm.lower().startswith('y'):
            print(f"{Fore.RED}Operation cancelled.")
            return

    try:
        # Initialize and run the cleaner
        cleaner = DependencyCleaner(
            root_dir=args.root,
            target_dirs=set(args.target_dirs),
            dry_run=args.dry_run,
            interactive=not args.no_interactive,
            log_file=args.log_file
        )

        stats = cleaner.clean()

        # Print detailed summary
        elapsed_time = stats['end_time'] - stats['start_time']
        print(f"\n{Fore.GREEN}=== Cleanup Summary ===")
        print(f"{Fore.CYAN}Time elapsed: {elapsed_time:.2f} seconds")
        print(f"Directories processed: {stats['deleted_count']}")
        print(f"Space freed: {cleaner.format_size(stats['total_size'])}")
        print(f"Skipped: {stats['skipped_count']}")
        print(f"Failed: {stats['failed_count']}")

        if stats['failed_count'] > 0:
            print(f"\n{Fore.YELLOW}Note: Some operations failed. Check the log file for details.")

    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Operation cancelled by user.")
    except Exception as e:
        print(f"\n{Fore.RED}An error occurred: {e}")
        logging.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
