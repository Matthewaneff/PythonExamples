from arcpy import *
import numpy as np

#~ angle_A = GetParameter(0)
#~ segLength = GetParameter(1)

angle_A = 45
segLength = 20

angle_B = (180 - angle_A) / 2
angle_C = 180 - 90 - angle_B

seg_BC = np.tan(np.deg2rad(angle_A)) * segLength

seg_DC = np.sin(np.deg2rad(angle_C)) * seg_BC

seg_DB = np.tan(np.deg2rad(angle_C)) * seg_DC

seg_AD = segLength - seg_DB

