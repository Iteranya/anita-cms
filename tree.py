#!/usr/bin/env python3
import os
import argparse
from pathlib import Path

# --- Installation Check ---
try:
    import pathspec
except ImportError:
    print("Error: 'pathspec' library not found.")
    print("Please install it by running: pip install pathspec")
    exit(1)
# --------------------------

# Configuration for tree drawing
TEE = "├──"
ELBOW = "└──"
PIPE = "│  "
SPACE = "   "

def get_gitignore_spec(path):
    """
    Finds the .gitignore file in the given path or its parents
    and returns a PathSpec object.
    """
    gitignore_file = None
    current_path = Path(path).resolve()
    
    # Look for .gitignore in current and parent directories
    while current_path != current_path.parent:
        potential_gitignore = current_path / ".gitignore"
        if potential_gitignore.is_file():
            gitignore_file = potential_gitignore
            break
        current_path = current_path.parent
    
    lines = []
    if gitignore_file:
        with open(gitignore_file, 'r') as f:
            lines = f.readlines()
            
    # Add common patterns to ignore by default
    default_ignore = ['.git', '__pycache__', '.vscode', '.idea']
    spec_lines = [line.strip() for line in lines if line.strip() and not line.startswith('#')]
    spec_lines.extend(default_ignore)
    
    return pathspec.PathSpec.from_lines('gitwildmatch', spec_lines)

def generate_tree(start_path: Path, spec: pathspec.PathSpec):
    """
    Generates the tree structure recursively.
    """
    # Use os.walk to get all directories and files
    for root, dirs, files in os.walk(start_path, topdown=True):
        # Get the path relative to the starting point
        relative_root = Path(root).relative_to(start_path)

        # Filter directories and files using the gitignore spec
        # Note: pathspec expects paths with forward slashes
        paths_to_check = [
            (str(relative_root / d) + '/').replace('\\', '/') for d in dirs
        ] + [
            str(relative_root / f).replace('\\', '/') for f in files
        ]

        ignored_paths = set(spec.match_files(paths_to_check))

        # Filter dirs and files in-place so os.walk skips them
        dirs[:] = [d for d in dirs if (str(relative_root / d) + '/').replace('\\', '/') not in ignored_paths]
        files[:] = [f for f in files if str(relative_root / f).replace('\\', '/') not in ignored_paths]
        
        dirs.sort()
        files.sort()

        level = str(relative_root).count(os.sep)
        indent = PIPE * (level - 1) + TEE if level > 0 else ""
        
        # Don't print the root folder name again, just its contents
        if relative_root != Path('.'):
            # Determine the prefix for the current directory
            parent_path = Path(root).parent
            parent_dirs = sorted([d for d in os.listdir(parent_path) if os.path.isdir(os.path.join(parent_path, d))])
            
            # Check if this directory is the last in its parent list to use the elbow
            is_last = Path(root).name == parent_dirs[-1] if parent_dirs else True # A rough check
            
            # A more refined way to determine prefix might be needed for perfect trees,
            # but os.walk makes that complex. This is a good approximation.
            # We will correct this with a simpler recursive approach.

    # Let's switch to a simpler recursive approach for better prefix handling.
    # The os.walk approach is tricky for drawing lines correctly.
    _generate_tree_recursive(start_path, "", spec, start_path)


def _generate_tree_recursive(directory: Path, prefix: str, spec: pathspec.PathSpec, root_dir: Path):
    """
    A recursive helper function to generate the tree with correct prefixes.
    """
    # Get all items in the directory
    try:
        items = list(directory.iterdir())
    except PermissionError:
        return # Skip directories we can't read

    # Create a list of relative paths for pathspec
    relative_items = [item.relative_to(root_dir) for item in items]
    
    # pathspec works best with string paths using forward slashes
    str_paths = []
    for p in relative_items:
        path_str = str(p).replace('\\', '/')
        if p.is_dir():
            path_str += '/'
        str_paths.append(path_str)

    # Find which paths are ignored
    ignored_paths_set = set(spec.match_files(str_paths))
    
    # Filter out the ignored items
    visible_items = [
        item for item, str_path in zip(items, str_paths) if str_path not in ignored_paths_set
    ]
    
    # Separate and sort directories and files
    visible_dirs = sorted([p for p in visible_items if p.is_dir()])
    visible_files = sorted([p for p in visible_items if p.is_file()])
    
    # Combine them, directories first
    entries = visible_dirs + visible_files
    
    for i, entry in enumerate(entries):
        is_last = i == (len(entries) - 1)
        connector = ELBOW if is_last else TEE
        
        print(f"{prefix}{connector} {entry.name}")
        
        if entry.is_dir():
            extension = SPACE if is_last else PIPE
            _generate_tree_recursive(entry, prefix + extension, spec, root_dir)

def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(
        description="Prints a project tree, respecting .gitignore.",
        epilog="Example: python tree.py ./my_project"
    )
    parser.add_argument(
        "start_path",
        type=str,
        nargs="?",
        default=".",
        help="The path to the directory to scan (default: current directory)."
    )
    args = parser.parse_args()
    
    start_path = Path(args.start_path)
    
    if not start_path.is_dir():
        print(f"Error: Path '{start_path}' is not a valid directory.")
        return

    # Get the gitignore spec
    spec = get_gitignore_spec(start_path)

    # Print the root and start the tree generation
    print(f"{start_path.resolve().name}/")
    _generate_tree_recursive(start_path, "", spec, start_path)

if __name__ == "__main__":
    main()