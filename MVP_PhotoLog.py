import os, sys, datetime
from arcpy import *

photoFC = r'C:\Users\Mitchell.Fyock\Desktop\Projects\VA_MVP\GIS\Data\TetraTech\MVP_TWS.gdb\Photo_Point_Log'
inputFeature = GetParameterAsText(0)
PhotoID = GetParameterAsText(1)

photoLog = []
delLog = []

with da.SearchCursor(photoFC, PhotoID) as cursor:
	for row in cursor:
		photoLog.append(row[0])
		
inscurs = da.InsertCursor(photoFC, "Photo_ID")

with da.SearchCursor(inputFeature, "Photo_ID") as cursor:
	for row in cursor:
		if row[0] in photoLog:
			delLog.append(str(row[0]))
		else:
			inscurs.insertRow([row[0]])

del inscurs

if len(delLog) != 0:
	
	lyr = management.MakeFeatureLayer(inputFeature, "inputFeature")
	
	management.SelectLayerByAttribute(lyr, "NEW_SELECTION", "{} IN {}".format(PhotoID, tuple(delLog)))
	
	management.DeleteRows(lyr)
