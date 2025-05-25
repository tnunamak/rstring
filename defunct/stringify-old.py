#!/usr/bin/env python

import argparse
import fnmatch
import os

def main():
    parser = argparse.ArgumentParser(description='Gather code from a directory into a single string with file paths labeled.')
    parser.add_argument('directory', type=str, help='Root directory to gather code from')
    parser.add_argument('-o', '--output', type=str, help='Output file (default is stdout)', default=None)
    parser.add_argument('-i', '--include', action='append', help='Include patterns (glob format, repeatable)', default=["*"])
    parser.add_argument('-e', '--exclude', action='append', help='Exclude patterns (glob format, repeatable)', default=[])

    args = parser.parse_args()

    gather_code(args.directory, args.output, args.include, args.exclude)

def gather_code(directory, output_file, includes, excludes):
    result = ""
    for root, dirs, files in os.walk(directory, topdown=True):
        # Exclude specified directories
        dirs[:] = [d for d in dirs if not any(fnmatch.fnmatch(os.path.join(root, d), pat) for pat in excludes)]
        
        # Apply include patterns
        if includes:
            files = [f for f in files if any(fnmatch.fnmatch(os.path.join(root, f), pat) for pat in includes)]
        
        # Exclude specified files
        relative_root = os.path.relpath(root, start=directory)
        files = [f for f in files if not any(fnmatch.fnmatch(os.path.join(relative_root, f), pat) for pat in excludes)]
        
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as file_content:
                    file_data = file_content.read()
                    result += f'--- {os.path.relpath(file_path, start=directory)} ---\n{file_data}\n'
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result)
    else:
        print(result)

if __name__ == '__main__':
    main()

