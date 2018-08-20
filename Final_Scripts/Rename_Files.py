import os, sys, argparse

def main():
    os.chdir(args.folder)

    for item in os.listdir(args.folder):
        os.rename(item, '{}'.format(item.replace(args.string, '')))

    return

"""
========================================================================
Rename_Files.py
========================================================================
Author: Mitchell Fyock
========================================================================
Date			Modifier	Description of Change
09/15/2017      MF          Created
========================================================================
Rename bulk files using command line interface
"""

# Initialize Arguments
parser = argparse.ArgumentParser()
parser.add_argument('folder', type=str, help='Folder location of files to be renamed...')
parser.add_argument('string', type=str, help='String be replaced...')
args = parser.parse_args()

if __name__ == '__main__':
    main()
