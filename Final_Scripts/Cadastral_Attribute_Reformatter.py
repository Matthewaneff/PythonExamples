import os, sys, datetime
import pandas as pd
import argparse

"""
========================================================================
Cadastral_Attribute_Reformatter.py
========================================================================
Author: Mitchell Fyock
========================================================================
Date			Modifier	Description of Change
10/31/2017		MF			Created
========================================================================

"""

parser = argparse.ArgumentParser()
parser.add_argument('file', type=str, help='Excel File to be reformatted')
args = parser.parse_args()

directory = os.path.dirname(args.file)
fName = os.path.basename(args.file)
try:
    df = pd.DataFrame(pd.read_excel(args.file, sheetname='Sheet1'), columns=['ID', 'Township/Range', 'Section', 'Quarter'])
except KeyError:
    print("Table does not contain one or all of the following columns: 'ID', 'Township/Range', 'Section', 'Quarter'")
    sys.exit()

df['Q'] = df['Quarter'].str[2:]
df['QQ'] = df['Quarter'].str[0:2]
df.drop('Quarter', 1)

df.to_excel(os.path.join(directory, 'Revised_' + fName), columns=['ID', 'Township/Range', 'Section', 'Q', 'QQ', 'QQQ'], index=False)
