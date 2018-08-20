from arcpy import *
import os, sys, datetime

env.OverwriteOutput = 'TRUE'

"""
========================================================================
Transect Spacing
========================================================================
Author: Mitchell Fyock
========================================================================
Date			Modifier	Description of Change
03/20/2017		MF			Created
06/29/2017		MF			Added boolean option enabling for clipping or non-clipping of final output
07/28/2017		MF			Modified Exports
========================================================================
This script is designed to create transect lines at specific user-defined
angles using a user-defined spacing interval.
"""

# Gather Inputs
inputFeature = GetParameterAsText(0)
bufer = GetParameterAsText(1)
outputFeature = GetParameterAsText(2)

# Write to Log
d = datetime.datetime.now()
sDate = d.strftime("%Y%m%d")
AddMessage(sDate)
AddMessage("===================================================================")
sVersionInfo = 'Point2SquareBuffer.py, v20170728'
AddMessage('Point to Square Buffer, {}'.format(sVersionInfo))
AddMessage("")
AddMessage("Support: mitchell.fyock@tetratech.com, 303-2173724")
AddMessage("")
AddMessage("Input Feature: {}".format(inFeature))
AddMessage("Personnel Number: {}".format(personnel))
AddMessage("Spacing Interval: {} {}".format(str(spacingInterval), spacingUnit))
AddMessage("Survey Angle: {}".format(surveyAngle))
AddMessage("Output Location: {}".format(outFeature))
AddMessage("===================================================================")
