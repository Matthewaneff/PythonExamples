import sys, os
from arcpy import *

class Unit(object):
    def __init__(self, in_unit, out_unit):
        '''
        in_unit -> linear unit data type
        out_unit -> arcpy.Describe class
        '''

        self.in_value = float(in_unit.split(' ')[0])
        self.in_unit = in_unit.split(' ')[1]
        self.out_unit = out_unit.spatialReference.linearUnitName

    def Metric_Conversion(self, uFrom, uTo, distance):
        if uFrom == 'Centimeters' and uTo == 'Meter':
            dist = distance * .01
        elif uFrom == 'Kilometers' and uTo == 'Meter':
            dist = distance * 1000
        elif uFrom == 'Millimeters' and uTo == 'Meter':
            dist = distance * .001
        elif uFrom == 'Feet' and uTo == 'Meter':
            dist = distance * 0.3048
        elif uFrom == 'Inches' and uTo == 'Meter':
            dist = distance * 0.0254
        elif uFrom == 'Miles' and uTo == 'Meter':
            dist = distance * 1609.34
        elif uFrom == 'Yards' and uTo == 'Meter':
            dist = distance * 0.9144
        else:
            AddError('Unit Not Recognized')
            sys.exit()

        return dist

    def Imperial_Conversion(self, uFrom, uTo, distance):
        if uFrom == 'Inches' and uTo == 'Foot':
            dist = distance * (1/2)
        elif uFrom == 'Yards' and uTo == 'Foot':
            dist = distance * 3
        elif uFrom == 'Miles' and uTo == 'Foot':
            dist = distance * 5280
        elif uFrom == 'Meters' and uTo == 'Foot':
            dist = distance * 3.28084
        elif uFrom == 'Kilometers' and uTo == 'Foot':
            dist = distance * 3280.84
        elif uFrom == 'Centimeters' and uTo == 'Foot':
            dist = distance * 0.0328084
        elif uFrom == 'Millimeters' and uTo == 'Foot':
            dist = distance * 0.00328084
        else:
            AddError('Unit Not Recognized')
            sys.exit()

        return dist
