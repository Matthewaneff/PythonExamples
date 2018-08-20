import os, sys, datetime, argparse
import pandas as pd

"""
========================================================================
Concatenate_Cadastral_Attributes.py
========================================================================
Author: Mitchell Fyock
========================================================================
Date			Modifier	Description of Change
11/01/2017		MF			Created
========================================================================

"""

parser = argparse.ArgumentParser()
parser.add_argument('file', type=str, help='Excel File to be reformatted')
args = parser.parse_args()

directory = os.path.dirname(args.file)
fName = os.path.basename(args.file)

try:
    df = pd.DataFrame(pd.read_excel(args.file, 'Sheet1'), columns=['ID', 'Township/Range', 'Section', 'Q', 'QQ', 'QQQ'])
except KeyError:
    print("Table does not contain one or all of the following columns: 'ID', 'Township/Range', 'Section', 'Q', 'QQ', 'QQQ'")
    sys.exit()

cols = ['Township/Range', 'Section', 'Q', 'QQ', 'QQQ']

df_ID = df['ID'].astype(str)
df_Att = df[cols].astype(str)

dict_list = []

for i in range(len(df)):

    dictionary = {'ID':df_ID[i],}

    strList = []

    for item in ['Township/Range', 'Section', 'Q', 'QQ', 'QQQ']:
        strList.append(df_Att.loc[i][item])

    dictionary['TRSQQQ'] = ' '.join(strList)

    dict_list.append(dictionary)

newDF = pd.DataFrame(dict_list, columns=['ID', 'TRSQQQ'])

newDF.to_excel(args.file, columns=['ID', 'TRSQ'], index=False)
