#!/usr/bin/env python3
"""
convert_requirements_to_pyproject.py

A script to convert a requirements.txt file (including nested requirements with -r)
into a pyproject.toml file compatible with Poetry.

Usage:
    python convert_requirements_to_pyproject.py -i requirements.txt -o pyproject.toml

Dependencies:
    - None (uses only standard libraries)
"""

import argparse
import os
import re
from collections import OrderedDict

def parse_requirements(file_path, parsed_files=None):
    """
    Parses a requirements.txt file, handling nested -r includes.

    Args:
        file_path (str): Path to the requirements.txt file.
        parsed_files (set): Set of already parsed file paths to avoid circular includes.

    Returns:
        list of str: List of requirement lines.
    """
    if parsed_files is None:
        parsed_files = set()

    requirements = []

    absolute_path = os.path.abspath(file_path)
    if absolute_path in parsed_files:
        print(f"Already parsed {absolute_path}, skipping to avoid circular includes.")
        return requirements

    if not os.path.exists(absolute_path):
        print(f"Warning: {absolute_path} does not exist. Skipping.")
        return requirements

    parsed_files.add(absolute_path)

    with open(absolute_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue  # Skip empty lines and comments
            if line.startswith('-r') or line.startswith('--requirement'):
                # Handle nested requirement files
                parts = line.split()
                if len(parts) == 2:
                    nested_req = parts[1]
                    nested_path = os.path.join(os.path.dirname(absolute_path), nested_req)
                    requirements.extend(parse_requirements(nested_path, parsed_files))
                else:
                    print(f"Unrecognized requirement line: {line}")
            else:
                requirements.append(line)

    return requirements

def parse_requirement_line(line):
    """
    Parses a single requirement line into package and version specifier.

    Args:
        line (str): A requirement line.

    Returns:
        tuple: (package, version_specifier)
    """
    # Regex to match package and version
    # Example matches:
    # package==1.2.3
    # package>=1.0,<2.0
    # package
    # package[extra]==1.2.3

    # Handle extras
    match = re.match(r'^([A-Za-z0-9_\-\.]+(?:\[[A-Za-z0-9_,\-\.]+\])?)\s*(.*)$', line)
    if not match:
        print(f"Warning: Could not parse requirement line: {line}")
        return (line, None)

    package, version = match.groups()
    version = version.strip() if version else None

    return (package, version)

def generate_pyproject_toml(dependencies):
    """
    Generates the content for pyproject.toml with given dependencies.

    Args:
        dependencies (dict): Dictionary of package to version specifier.

    Returns:
        str: Content of pyproject.toml
    """
    toml_content = '''[tool.poetry]
name = "your-project-name"
version = "0.1.0"
description = "A short description of your project."
authors = ["Your Name <you@example.com>"]

[tool.poetry.dependencies]
python = "^3.8"
'''

    for pkg, ver in dependencies.items():
        if ver:
            toml_content += f'{pkg} = "{ver}"\n'
        else:
            toml_content += f'{pkg} = "*"\n'

    toml_content += '''

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
'''
    return toml_content

def main():
    parser = argparse.ArgumentParser(description="Convert requirements.txt (with nested -r) to pyproject.toml for Poetry.")
    parser.add_argument('-i', '--input', default='requirements.txt', help='Path to the requirements.txt file.')
    parser.add_argument('-o', '--output', default='pyproject.toml', help='Path to the output pyproject.toml file.')
    args = parser.parse_args()

    reqs = parse_requirements(args.input)

    dependencies = OrderedDict()
    for req in reqs:
        pkg, ver = parse_requirement_line(req)
        dependencies[pkg] = ver

    toml = generate_pyproject_toml(dependencies)

    with open(args.output, 'w') as f:
        f.write(toml)

    print(f"Successfully generated {args.output}")

if __name__ == "__main__":
    main()
