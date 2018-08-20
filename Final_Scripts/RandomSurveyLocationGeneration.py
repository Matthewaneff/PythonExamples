from arcpy import *
import sys, os
import numpy as np


''' Define Inputs '''

# Define Project Area
inputFeature = GetParameterAsText(0)
try:
	count = management.GetCount(inputFeature)
	count == 1
except ValueError:
	AddError('Feature class contains more than one row')
	sys.exit()

# Define Acreage
inputAcreage = GetParameterAsText(1)

(value, metric) = inputAcreage.split(" ")

if metric.lower() == 'acres':
	area = float(value) * 4046.86
elif metric.lower() == 'ares':
	area = float(value) * 100
elif metric.lower() == 'squaremeters':
	area = float(value)
elif metric.lower() == 'squaremiles':
	area = float(value) * 2589.99 
elif metric.lower() == 'squarekilometers':
	area = float(value) * 1000
else:
	AddError('Areal Unit Not Valid')

# Define Sample Size
sampleSize = GetParameterAsText(2)
sampleSize = int(sampleSize)

# Define Output Feature Class
outputFeature = GetParameterAsText(3)

# Calculate length and width, and then find the radius
sqAcre = np.sqrt(area)
radius = sqAcre / 2

desc = Describe(inputFeature)
spaRef = desc.spatialReference
extent = desc.extent

xMin = extent.XMin
xMax = extent.XMax
yMin = extent.YMin
yMax = extent.YMax

boundaryArray = Array()

with da.SearchCursor(inputFeature, "SHAPE@") as cursor:
	for row in cursor:
		boundary = row[0]
		a = Array()
		for vertice in boundary.getPart(0):
			point = Point(vertice.X, vertice.Y)
			a.append(point)
		boundaryArray.add(a)

boundary = Polygon(boundaryArray)

# Create the new empty feature classs
(path, name) = os.path.split(outputFeature)
newFeature = management.CreateFeatureclass(path, name, "Polygon", '', '', '', spaRef)

arrayList = []

while sampleSize > 0:
	
	# Create Random coordinates
	x = np.random.uniform(xMin, xMax)
	y = np.random.uniform(yMin, yMax)
	point = Point(x,y)	
	
	# If the point is within the Input Feature, buffer it by the radius
	if point.within(boundary):
		centroid = PointGeometry(point)
		pointBuff = centroid.buffer(radius)
		
		# Create extent boundaries around buffer
		buffExtent = pointBuff.extent
		
		array = Array()
		array.append(Point(buffExtent.XMin, buffExtent.YMin))
		array.append(Point(buffExtent.XMax, buffExtent.YMin))
		array.append(Point(buffExtent.XMax, buffExtent.YMax))
		array.append(Point(buffExtent.XMin, buffExtent.YMax))
		
		# Create a polygon geometry object from the array
		poly = Polygon(array)
		arrayList.append(poly)
		sampleSize = sampleSize - 1
		
		#~ if poly.within(boundary):
			#~ arrayList.append(poly)
			#~ sampleSize = sampleSize - 1

for item in arrayList:
	with da.InsertCursor(newFeature, "SHAPE@") as cursor:
		cursor.insertRow([item])
