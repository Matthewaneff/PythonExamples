# -*- coding: utf-8 -*-
"""
Created on Thu Jun 15 12:25:20 2017

@author: MITCHELL.FYOCK
"""

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import numpy as np
import pandas as pd

fig = plt.figure()
ax = fig.gca(projection='3d')

# Get Data
f = pd.read_excel('C:/Users/Mitchell.Fyock/Desktop/Projects/ND_Wilton_IV_GPS/Deliverables/20161130_Site_Attributes/Site_Attributes_Datum.xlsx')
df = pd.DataFrame(f)

x = np.array([row for row in df['Easting_m']])
y = np.array([row for row in df['Northing_m']])
z = np.array([row for row in df['Elevation']])

ax.scatter(x,y,z)

ax.set_xlabel('Easting')
ax.set_ylabel('Northing')
ax.set_zlabel('Elevation (m)')
plt.show()