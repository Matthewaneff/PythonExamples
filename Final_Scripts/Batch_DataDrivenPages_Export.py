import sys, os, datetime
from arcpy import *
import numpy as np

def writeLog(*argv):
	AddMessage(' ')
	AddMessage("===================================================================")
	sVersionInfo = 'Batch_DataDrivenPages_Export.py, v20180109'
	AddMessage('Batch Data Driven Pages Export, {}'.format(sVersionInfo))
	AddMessage("")
	AddMessage("Support: mitchell.fyock@tetratech.com, 303-217-3724")
	AddMessage("")
	AddMessage("ArcGIS Map Docutment: {}".format(argv[0]))
	AddMessage("Output Location: {}".format(argv[1]))
	AddMessage("===================================================================")
	AddMessage(" ")

if __name__ == '__main__':

	env.overwriteOutput = True

	inputMXD = GetParameterAsText(0)
	outputFolder = GetParameterAsText(1)
	
	# Write to Log
	writeLog(inputMXD, outputFolder)

	mxd = mapping.MapDocument(inputMXD)

	pageCount = mxd.dataDrivenPages.pageCount

	pageIterator = np.floor(pageCount / 5)

	startPage = 0
	pageName = 1

	while startPage <= pageIterator:
		start = (startPage * 5) + 1
		end = (startPage * 5) + 5
		
		mxd.dataDrivenPages.exportToPDF(os.path.join(outputFolder, "Map_Book_Set_{}.pdf".format(str(pageName))), "RANGE", "{}-{}".format(start, end), "PDF_SINGLE_FILE")
		
		AddMessage('Page {} Export Complete'.format(str(pageName)))
		
		startPage += 1
		pageName += 1
