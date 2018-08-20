import arcpy
from arcpy import *

# Set variables
feature = GetParameterAsText(0)
buffer = GetParameterAsText(1)
output = GetParameterAsText(2)

# Create Buffer
analysis.Buffer(feature, output, buffer, '', '', 'ALL')
