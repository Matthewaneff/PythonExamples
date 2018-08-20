from arcpy import *
import pandas as pd
import sys, os, datetime

"""
========================================================================
Mass_Site_Name_Update.py
========================================================================
Author: Mitchell Fyock
========================================================================
Date			Modifier	Description of Change
10/02/2017		MF			Created
========================================================================
Cycles through a user-specified feature dataset renaming site name attributes
stored in feature classes using a .csv that contains the old and new names
"""

if __name__ == '__main__':

	inputWorkspace = GetParameterAsText(0)
	gdb, ds = os.path.split(inputWorkspace)

	table = GetParameterAsText(1)

	tempName = GetParameterAsText(2)
	updateName = GetParameterAsText(3)

	df = pd.DataFrame(pd.read_csv(table))

	tempIDs = [i for i in df['{}'.format(tempName)]]
	newIDs = [i for i in df['{}'.format(updateName)]]

	if len(tempIDs) != len(newIDs):
		AddError('Please Check Table Entries...')
		sys.exit()

	env.workspace = gdb

	for fc in ListFeatureClasses('', '', ds):
		fields = [i.name for i in ListFields(fc)]
		
		if tempName in fields and updateName in fields:
			
			rowCount = int(management.GetCount(fc).getOutput(0))
			
			if rowCount > 0:
				
				count = 0
				
				for i in range(len(tempIDs)):
					
					tempID = tempIDs[i]
					newID = newIDs[i]
					
					with da.UpdateCursor(fc, [tempName, updateName]) as cursor:
						for row in cursor:
							if row[0] == tempID:
								row[1] = newID
								count += 1
								
							cursor.updateRow(row)
				
				if count > 0:
					AddMessage('Updating {} Featureclass'.format(fc))			
					AddMessage('{} rows updated'.format(str(count)))
