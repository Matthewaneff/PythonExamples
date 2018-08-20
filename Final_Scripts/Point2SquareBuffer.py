from arcpy import *
import os, sys, datetime

env.OverwriteOutput = 'TRUE'

"""
========================================================================
Point2SquareBuffer.py
========================================================================
Author: Mitchell Fyock
========================================================================
Date			Modifier	Description of Change
07/28/2017      MF          Created
========================================================================
Creates square buffers around points
"""

# Gather Inputs
inputFeature = GetParameterAsText(0)
desc = Describe(inputFeature)

bufferDist = GetParameterAsText(1)
(dist, metric) = bufferDist.split(' ')

outputFeature = GetParameterAsText(2)

# Write to Log
d = datetime.datetime.now()
sDate = d.strftime("%Y%m%d")
AddMessage(sDate)
AddMessage("===================================================================")
sVersionInfo = 'Point2SquareBuffer.py, v20170728'
AddMessage('Point to Square Buffer, {}'.format(sVersionInfo))
AddMessage("")
AddMessage("Support: mitchell.fyock@tetratech.com, 303-217-3724")
AddMessage("")
AddMessage("Input Feature: {}".format(inputFeature))
AddMessage("Buffer : {} {}".format(dist, metric))
AddMessage("Output Location: {}".format(outputFeature))
AddMessage("===================================================================")

'''Begin Here'''
temp = analysis.Buffer(inputFeature, "in_memory/temp", bufferDist)
management.FeatureEnvelopeToPolygon(temp, outputFeature)
management.Delete(temp)
